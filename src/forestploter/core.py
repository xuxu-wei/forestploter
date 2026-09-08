"""Core renderer for table-style forest plots.

The renderer consumes a validated long table. Each source record represents
one series in one CI column, and ``_plot_row`` determines the final vertical
coordinate. This module does not calculate statistical estimates.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from math import ceil
from pathlib import Path
from typing import Any, cast

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.colors import is_color_like
from matplotlib.figure import Figure
from matplotlib.font_manager import FontProperties
from matplotlib.lines import Line2D
from matplotlib.markers import MarkerStyle
from matplotlib.patches import Polygon, Rectangle
from matplotlib.textpath import TextPath

from .data import ForestData
from .layout import (
    ColumnGeometry,
    ForestColumn,
    ForestLayoutDiagnostics,
    ForestLegendSpec,
    ForestReferenceLegendSpec,
    ForestSeriesStyle,
    ForestTableLayoutSpec,
    compute_column_geometry,
)
from .theme import ForestTheme
from .validation import _NormalizedForestTable, normalize_forest_data


@dataclass(frozen=True)
class ForestPlotResult:
    """Store rendered objects and auditable layout information.

    Parameters
    ----------
    figure : matplotlib.figure.Figure
        Complete Matplotlib Figure.
    axes : matplotlib.axes.Axes
        Axes shared by the table and confidence intervals.
    geometry : tuple of ColumnGeometry
        Normalized horizontal boundaries for every output column.
    row_centers : tuple of float
        Visual-row centers in unique ``_plot_row`` order.
    clipped_intervals : int
        Number of intervals with at least one endpoint outside ``xlim``; each
        interval is counted at most once.
    layout_diagnostics : ForestLayoutDiagnostics
        Diagnostics for rows, observation positions, merged spans, legends,
        and headers.
    """

    figure: Figure
    axes: Axes
    geometry: tuple[ColumnGeometry, ...]
    row_centers: tuple[float, ...]
    clipped_intervals: int
    layout_diagnostics: ForestLayoutDiagnostics

    def save(self, path: str | Path, *, dpi: int = 300) -> Path:
        """Save PNG, SVG, or another Matplotlib-supported format.

        Parameters
        ----------
        path : str or pathlib.Path
            Output path. The suffix determines the format, and missing parent
            directories are created automatically.
        dpi : int, default 300
            Raster-output resolution.

        Returns
        -------
        pathlib.Path
            Absolute path of the saved file.

        Raises
        ------
        OSError
            Raised when the directory cannot be created or the file cannot be
            written.
        ValueError
            Raised when Matplotlib does not support the requested format.
        """

        destination = Path(path).resolve()
        destination.parent.mkdir(parents=True, exist_ok=True)
        self.figure.savefig(destination, dpi=dpi, facecolor="white", bbox_inches="tight")
        return destination


def _value_to_canvas(value: float, left: float, right: float, xlim: tuple[float, float]) -> float:
    return left + (value - xlim[0]) / (xlim[1] - xlim[0]) * (right - left)


def _add_arrow(
    ax: Axes, *, side: str, left: float, right: float, y: float, color: str, gid: str
) -> None:
    arrow_width = (right - left) * 0.022
    if side == "left":
        vertices = [[left, y], [left + arrow_width, y + 0.10], [left + arrow_width, y - 0.10]]
    else:
        vertices = [[right, y], [right - arrow_width, y + 0.10], [right - arrow_width, y - 0.10]]
    patch = Polygon(vertices, closed=True, facecolor=color, edgecolor=color, zorder=5)
    patch.set_gid(gid)
    ax.add_patch(patch)


def _draw_clipped_interval(
    ax: Axes,
    *,
    estimate: float,
    lower: float,
    upper: float,
    y: float,
    left: float,
    right: float,
    xlim: tuple[float, float],
    color: str,
    summary: bool,
    marker: str,
    summary_marker: str,
    record_index: int,
) -> int:
    """绘制单个区间，并让箭头取代越界侧端帽。

    完全位于范围外的区间只显示最近的向外箭头；不会绘制边界线、端帽或
    伪造的点估计。返回值按受影响区间计数，只能是零或一。
    """

    clipped_left = lower < xlim[0]
    clipped_right = upper > xlim[1]
    affected = int(clipped_left or clipped_right)
    prefix = f"ci:{record_index}"

    if upper < xlim[0]:
        _add_arrow(
            ax,
            side="left",
            left=left,
            right=right,
            y=y,
            color=color,
            gid=f"{prefix}:arrow:left:offscale",
        )
        return 1
    if lower > xlim[1]:
        _add_arrow(
            ax,
            side="right",
            left=left,
            right=right,
            y=y,
            color=color,
            gid=f"{prefix}:arrow:right:offscale",
        )
        return 1

    visible_low = max(lower, xlim[0])
    visible_high = min(upper, xlim[1])
    x_low = _value_to_canvas(visible_low, left, right, xlim)
    x_high = _value_to_canvas(visible_high, left, right, xlim)
    line = ax.plot(
        [x_low, x_high],
        [y, y],
        color=color,
        linewidth=1.25,
        zorder=4,
        solid_capstyle="round",
    )[0]
    line.set_gid(f"{prefix}:line")
    cap_half_height = 0.10
    if not clipped_left:
        cap = ax.plot(
            [x_low, x_low],
            [y - cap_half_height, y + cap_half_height],
            color=color,
            linewidth=1.0,
            zorder=4,
        )[0]
        cap.set_gid(f"{prefix}:cap:left")
    else:
        _add_arrow(
            ax,
            side="left",
            left=left,
            right=right,
            y=y,
            color=color,
            gid=f"{prefix}:arrow:left",
        )
    if not clipped_right:
        cap = ax.plot(
            [x_high, x_high],
            [y - cap_half_height, y + cap_half_height],
            color=color,
            linewidth=1.0,
            zorder=4,
        )[0]
        cap.set_gid(f"{prefix}:cap:right")
    else:
        _add_arrow(
            ax,
            side="right",
            left=left,
            right=right,
            y=y,
            color=color,
            gid=f"{prefix}:arrow:right",
        )

    if xlim[0] <= estimate <= xlim[1]:
        x_estimate = _value_to_canvas(estimate, left, right, xlim)
        if summary and summary_marker == "diamond":
            half_width = max((right - left) * 0.012, 0.004)
            summary_point = Polygon(
                [
                    [x_estimate - half_width, y],
                    [x_estimate, y + 0.18],
                    [x_estimate + half_width, y],
                    [x_estimate, y - 0.18],
                ],
                closed=True,
                facecolor=color,
                edgecolor=color,
                zorder=6,
            )
            summary_point.set_gid(f"{prefix}:marker:summary")
            ax.add_patch(summary_point)
        else:
            marker_point = ax.scatter(
                [x_estimate],
                [y],
                marker=marker,
                s=22,
                facecolor=color,
                edgecolor=color,
                zorder=6,
            )
            marker_point.set_gid(f"{prefix}:marker")
    return affected


def _measure_text_width_pt(text: str, *, size: float, weight: str = "normal") -> float:
    if not text:
        return 0.0
    prop = FontProperties(size=size, weight=weight)
    widths: list[float] = []
    for line in str(text).splitlines() or [str(text)]:
        if not line:
            widths.append(0.0)
        else:
            widths.append(
                float(TextPath((0, 0), line, prop=prop, usetex=False).get_extents().width)
            )
    return max(widths, default=0.0)


def _wrap_header_text(text: str, *, target_width_pt: float, size: float, max_lines: int) -> str:
    if not text or max_lines < 1:
        return text
    wrapped: list[str] = []
    for source in str(text).splitlines() or [str(text)]:
        words = source.split()
        if not words:
            wrapped.append("")
            continue
        current = words[0]
        for word in words[1:]:
            candidate = f"{current} {word}"
            if _measure_text_width_pt(candidate, size=size, weight="bold") <= target_width_pt:
                current = candidate
            else:
                wrapped.append(current)
                current = word
        wrapped.append(current)
    if len(wrapped) <= max_lines:
        return "\n".join(wrapped)
    return "\n".join(wrapped[: max_lines - 1] + [" ".join(wrapped[max_lines - 1 :])])


def _resolve_table_layout(
    table: _NormalizedForestTable,
    columns: Sequence[ForestColumn],
    *,
    style: ForestTheme,
    figure_width: float,
    spec: ForestTableLayoutSpec,
) -> tuple[tuple[ForestColumn, ...], float]:
    if not isinstance(spec.auto_width, (bool, np.bool_)) or not isinstance(
        spec.auto_wrap_headers, (bool, np.bool_)
    ):
        raise ValueError("Forest table auto_width and auto_wrap_headers must be boolean.")
    if spec.column_padding_pt <= 0 or spec.edge_padding_pt < 0:
        raise ValueError("Forest table padding values must be positive.")
    if spec.max_header_lines < 1:
        raise ValueError("max_header_lines must be at least one.")
    if spec.max_figure_width < figure_width:
        raise ValueError("max_figure_width cannot be smaller than figure_width.")
    if not spec.auto_width:
        return tuple(columns), float(figure_width)
    weights = np.asarray([column.width for column in columns], dtype=float)
    usable_initial = figure_width * 72.0 - 2.0 * spec.edge_padding_pt
    preferred = usable_initial * weights / weights.sum()
    resolved_columns: list[ForestColumn] = []
    required_widths: list[float] = []
    for column, preferred_width in zip(columns, preferred, strict=True):
        header = column.header
        if spec.auto_wrap_headers and header:
            header = _wrap_header_text(
                header,
                target_width_pt=max(18.0, preferred_width - 2.0 * spec.column_padding_pt),
                size=style.base_font_size,
                max_lines=spec.max_header_lines,
            )
        resolved_columns.append(replace(column, header=header))
        header_width = _measure_text_width_pt(header, size=style.base_font_size, weight="bold")
        cell_width = 0.0
        if column.role != "ci":
            for row in table.plot_rows:
                value = row.value(column.key)
                if value is not None and not pd.isna(value):
                    cell_width = max(
                        cell_width,
                        _measure_text_width_pt(str(value), size=style.base_font_size),
                    )
            if column.alignment == "left":
                cell_width += max((row.indent for row in table.plot_rows), default=0.0) * 9.0
        required_widths.append(max(18.0, header_width, cell_width) + 2.0 * spec.column_padding_pt)
    required = np.asarray(required_widths, dtype=float)
    minimum_width = (required.sum() + 2.0 * spec.edge_padding_pt) / 72.0
    final_width = max(float(figure_width), float(minimum_width))
    if final_width > spec.max_figure_width + 1e-12:
        raise ValueError(
            f"Forest table requires {final_width:.2f} inches, exceeding "
            f"max_figure_width={spec.max_figure_width:.2f}."
        )
    usable_final = final_width * 72.0 - 2.0 * spec.edge_padding_pt
    remainder = max(0.0, usable_final - required.sum())
    allocated = required + remainder * weights / weights.sum()
    return (
        tuple(
            replace(column, width=float(width))
            for column, width in zip(resolved_columns, allocated, strict=True)
        ),
        final_width,
    )


def _compute_row_geometry(
    count: int,
) -> tuple[tuple[float, ...], tuple[tuple[float, float], ...], tuple[float, ...]]:
    centers = tuple(float(count - index - 0.5) for index in range(count))
    bounds = tuple((float(count - index - 1), float(count - index)) for index in range(count))
    return centers, bounds, tuple(1.0 for _ in range(count))


def _validate_legend_position(
    spec: ForestLegendSpec | ForestReferenceLegendSpec,
    *,
    keys: set[str],
) -> None:
    if spec.location not in {"header", "bottom"}:
        raise ValueError("Legend location must be 'header' or 'bottom'.")
    if isinstance(spec.ncol, bool) or not isinstance(spec.ncol, int) or spec.ncol < 1:
        raise ValueError("Legend ncol must be a positive integer.")
    if spec.location == "header" and not spec.column_key:
        raise ValueError("A header legend requires column_key.")
    if spec.column_key is not None and spec.column_key not in keys:
        raise ValueError(f"Legend column_key does not name a forest column: {spec.column_key!r}")


def _legend_height(item_count: int, ncol: int) -> float:
    return 0.52 + max(0, ceil(item_count / ncol) - 1) * 0.34


def _series_styles(
    table: _NormalizedForestTable,
    supplied: Mapping[str, ForestSeriesStyle] | None,
    theme: ForestTheme,
) -> dict[str, ForestSeriesStyle]:
    observed = table.series_order
    if supplied is None:
        if observed and not theme.ci_colors:
            raise ValueError("ForestTheme.ci_colors must contain at least one color.")
        return {
            name: ForestSeriesStyle(
                label=name,
                color=theme.ci_colors[index % len(theme.ci_colors)],
            )
            for index, name in enumerate(observed)
        }
    if not isinstance(supplied, Mapping):
        raise TypeError("series_styles must be a mapping keyed by series name.")
    supplied_keys = set(supplied)
    if supplied_keys != set(observed):
        missing = sorted(set(observed) - supplied_keys)
        unexpected = sorted(supplied_keys - set(observed))
        raise ValueError(
            f"series_styles keys must exactly match observed series; missing={missing}, "
            f"unexpected={unexpected}."
        )
    resolved: dict[str, ForestSeriesStyle] = {}
    for name in observed:
        item = supplied[name]
        if not isinstance(item, ForestSeriesStyle):
            raise TypeError(f"series_styles[{name!r}] must be a ForestSeriesStyle.")
        if item.summary_marker not in {"diamond", "same"}:
            raise ValueError("ForestSeriesStyle.summary_marker must be 'diamond' or 'same'.")
        if not isinstance(item.label, str) or not item.label:
            raise ValueError("ForestSeriesStyle.label must be a non-empty string.")
        if not is_color_like(item.color):
            raise ValueError(f"Invalid series color for {name!r}: {item.color!r}")
        if not isinstance(item.marker, str) or not item.marker:
            raise ValueError(
                "ForestSeriesStyle.marker must be a non-empty Matplotlib marker string."
            )
        try:
            MarkerStyle(item.marker)
        except (TypeError, ValueError) as error:
            raise ValueError(
                f"Invalid Matplotlib marker for series {name!r}: {item.marker!r}"
            ) from error
        resolved[name] = item
    return resolved


def _validate_theme(theme: ForestTheme) -> None:
    if not np.isfinite(theme.base_font_size) or theme.base_font_size <= 0:
        raise ValueError("ForestTheme.base_font_size must be a positive finite number.")
    if not isinstance(theme.show_table_border, (bool, np.bool_)):
        raise ValueError("ForestTheme.show_table_border must be boolean.")
    if not isinstance(theme.show_vertical_grid, (bool, np.bool_)):
        raise ValueError("ForestTheme.show_vertical_grid must be boolean.")
    color_fields = {
        "header_fill": theme.header_fill,
        "alternate_fill": theme.alternate_fill,
        "group_fill": theme.group_fill,
        "text_color": theme.text_color,
        "muted_color": theme.muted_color,
        "summary_fill": theme.summary_fill,
        "grid_color": theme.grid_color,
        "reference_color": theme.reference_color,
        "ideal_color": theme.ideal_color,
    }
    invalid_colors = [name for name, value in color_fields.items() if not is_color_like(value)]
    if invalid_colors:
        raise ValueError(f"ForestTheme contains invalid colors: {invalid_colors}")
    try:
        ci_colors = tuple(theme.ci_colors)
    except TypeError as error:
        raise ValueError("ForestTheme.ci_colors must be a sequence of colors.") from error
    if isinstance(theme.ci_colors, str) or any(not is_color_like(value) for value in ci_colors):
        raise ValueError("ForestTheme.ci_colors must contain valid Matplotlib colors.")
    for name, value in {
        "reference_line_style": theme.reference_line_style,
        "ideal_line_style": theme.ideal_line_style,
    }.items():
        if not isinstance(value, str) or not value:
            raise ValueError(f"ForestTheme.{name} must be a non-empty Matplotlib line style.")


def _row_fill(row_type: str, index: int, theme: ForestTheme) -> str:
    if row_type == "header":
        return theme.group_fill
    if row_type != "spacer" and index % 2 == 1:
        return theme.alternate_fill
    return "white"


def _legend_x_span(
    *,
    column_key: str | None,
    by_key: dict[str, ColumnGeometry],
    ci_columns: Sequence[str],
) -> tuple[float, float]:
    if column_key is not None:
        cell = by_key[column_key]
        return cell.left, cell.right
    if not ci_columns:
        raise ValueError(
            "A bottom legend without column_key requires at least one active CI column."
        )
    cells = [by_key[key] for key in ci_columns]
    return min(cell.left for cell in cells), max(cell.right for cell in cells)


def forest(
    data: ForestData | pd.DataFrame,
    *,
    columns: Sequence[ForestColumn],
    ref_line: float = 0.0,
    ideal_line: float | None = None,
    ideal_line_columns: Sequence[str] | None = None,
    xlim: tuple[float, float] | None = None,
    ticks_at: Sequence[float] | None = None,
    arrow_lab: tuple[str, str] | None = None,
    theme: ForestTheme | None = None,
    title: str | None = None,
    figure_width: float = 12.0,
    row_height: float = 0.36,
    series_styles: Mapping[str, ForestSeriesStyle] | None = None,
    legend: ForestLegendSpec | None = None,
    table_layout: ForestTableLayoutSpec | None = None,
    reference_legend: ForestReferenceLegendSpec | None = None,
) -> ForestPlotResult:
    """Render a table-style forest plot from an explicit long table.

    Parameters
    ----------
    data : ForestData or pandas.DataFrame
        Result of :func:`read_forest_data`, or a long-form DataFrame using the
        default reserved field names. One source record may describe only one
        series in one CI column with one ``estimate/lower/upper`` triple.
    columns : sequence of ForestColumn
        Display and CI columns in final left-to-right plot order. This sequence
        is the sole authority for visual order: text may appear before or after
        any CI column regardless of XLSX/CSV header order. Display keys must be
        source fields; CI keys are targeted by ``_ci_column`` records.
    ref_line : float, default 0
        Reference line shared by all CI columns.
    ideal_line : float, optional
        Optional additional ideal or target line shared by the selected CI
        columns.
    ideal_line_columns : sequence of str, optional
        Active CI-column keys in which to draw ``ideal_line``. ``None``
        preserves the default behavior of drawing it in every active CI
        column; an empty sequence suppresses the additional line and cannot
        be paired with an ideal-line legend label. Requires ``ideal_line``.
    xlim : tuple of float, optional
        Shared linear range ``(minimum, maximum)``. When omitted, it is derived
        from all nonblank intervals.
    ticks_at : sequence of float, optional
        Shared tick values. Five ticks are generated within ``xlim`` when
        omitted.
    arrow_lab : tuple of str, optional
        Left and right direction labels below the first active CI column.
    theme : ForestTheme, optional
        Colors, font size, optional table borders, grid, and guide-line styles.
    title : str, optional
        In-figure title.
    figure_width : float, default 12
        Minimum Figure width in inches.
    row_height : float, default 0.36
        Physical height of each unique ``_plot_row`` in inches.
    series_styles : mapping of str to ForestSeriesStyle, optional
        Mapping keyed by ``_series`` values. Supplied keys must exactly match
        observed series. Defaults follow first-appearance order.
    legend : ForestLegendSpec, optional
        Series legend placed in one column header or in the bottom region.
    table_layout : ForestTableLayoutSpec, optional
        Automatic column width, header wrapping, and edge-padding rules.
    reference_legend : ForestReferenceLegendSpec, optional
        Reference/ideal-line legend. It uses the same placement semantics as
        the series legend. When both exist, they stack with the series legend
        first.

    Returns
    -------
    ForestPlotResult
        Figure, Axes, column boundaries, visual-row centers, clipping count,
        and layout diagnostics.

    Raises
    ------
    TypeError
        Raised for invalid ``data`` or series-style types.
    ValueError
        Raised when the long table, intervals, styles, coordinates, legends,
        columns, or layout settings are invalid.

    Notes
    -----
    Prefer :func:`read_forest_data` for XLSX. For three series under one
    outcome, the recommended hierarchy uses one ``header`` row for the shared
    outcome-level values and three child ``_plot_row`` values with
    ``_indent=1``. Put the series label and its CI text on each child row. This
    conventional layout needs no merged cells. Supported vertical XLSX merges
    remain available for specialized display needs. On the header record,
    leave ``_series``, ``_ci_column``, and ``estimate/lower/upper`` blank; use
    ``_row_type="header"``, ``_indent=0``, and ``_is_summary=False``.

    To show one series in several CI columns, duplicate the record, retain the
    same ``_plot_row``, and change only ``_ci_column``. CSV uses the same
    logical fields but has no merge metadata; blanks are never inferred or
    forward-filled.

    A readable file-header order is recommended but does not control output.
    Place display fields before the first CI, then ``estimate/lower/upper`` as
    the first CI's physical representation, then trailing display fields, and
    finally the six controls ``_plot_row``, ``_series``, ``_ci_column``,
    ``_row_type``, ``_indent``, and ``_is_summary``. The ``columns`` sequence
    remains authoritative for the actual rendered order.

    ``_row_type`` controls row semantics. ``_is_summary`` must be boolean and
    controls marker shape only. A fully blank triple skips an interval; a
    partially blank triple is invalid. At an axis overflow, an arrow replaces
    the cap on that side. A fully off-scale interval shows only the nearest
    outward arrow.

    This function uses one global linear axis configuration. It performs no
    logarithmic transformation and computes no effect size, confidence
    interval, or meta-analysis statistic. ``ideal_line_columns`` controls only
    the additional line's visibility; all CI columns still share the same
    reference value, limits, and ticks.

    Examples
    --------
    >>> import pandas as pd
    >>> from forestploter import ForestColumn, forest
    >>> df = pd.DataFrame({
    ...     "Outcome": ["Overall survival"],
    ...     "estimate": [0.72], "lower": [0.58], "upper": [0.90],
    ...     "Effect": ["0.72 [0.58, 0.90]"],
    ...     "_plot_row": ["os-a"],
    ...     "_series": ["Treatment A"],
    ...     "_ci_column": ["ci"],
    ...     "_row_type": ["estimate"], "_indent": [0],
    ...     "_is_summary": [False],
    ... })
    >>> result = forest(df, columns=[
    ...     ForestColumn("Outcome", "Outcome", "text", 2),
    ...     ForestColumn("ci", "Treatment effect", "ci", 3, "center"),
    ...     ForestColumn("Effect", "Effect [95% CI]", "numeric", 2, "right"),
    ... ], xlim=(0.4, 1.4), ref_line=1.0)
    >>> result.row_centers
    (0.5,)
    """

    style = theme or ForestTheme()
    if not isinstance(style, ForestTheme):
        raise TypeError("theme must be a ForestTheme instance.")
    _validate_theme(style)
    if not np.isfinite(figure_width) or figure_width <= 0:
        raise ValueError("figure_width must be a positive finite number.")
    if not np.isfinite(row_height) or row_height <= 0:
        raise ValueError("row_height must be a positive finite number.")
    if arrow_lab is not None:
        try:
            arrow_labels = tuple(arrow_lab)
        except TypeError as error:
            raise ValueError("arrow_lab must contain exactly two strings.") from error
        if (
            isinstance(arrow_lab, str)
            or len(arrow_labels) != 2
            or any(not isinstance(value, str) for value in arrow_labels)
        ):
            raise ValueError("arrow_lab must contain exactly two strings.")
        arrow_lab = (arrow_labels[0], arrow_labels[1])
    if title is not None and not isinstance(title, str):
        raise ValueError("title must be a string when provided.")
    compute_column_geometry(columns)
    table = normalize_forest_data(data, columns=columns)
    if table_layout is not None and not isinstance(table_layout, ForestTableLayoutSpec):
        raise TypeError("table_layout must be a ForestTableLayoutSpec instance.")
    if legend is not None and not isinstance(legend, ForestLegendSpec):
        raise TypeError("legend must be a ForestLegendSpec instance.")
    if reference_legend is not None and not isinstance(reference_legend, ForestReferenceLegendSpec):
        raise TypeError("reference_legend must be a ForestReferenceLegendSpec instance.")
    table_spec = table_layout or ForestTableLayoutSpec()
    resolved_columns, final_figure_width = _resolve_table_layout(
        table,
        columns,
        style=style,
        figure_width=figure_width,
        spec=table_spec,
    )
    geometry = compute_column_geometry(resolved_columns)
    by_key = {item.key: item for item in geometry}
    all_keys = set(by_key)
    active_ci = table.ci_columns or tuple(
        column.key for column in resolved_columns if column.role == "ci"
    )
    if ideal_line_columns is None:
        ideal_line_targets = frozenset(active_ci)
    else:
        if ideal_line is None:
            raise ValueError("ideal_line_columns requires ideal_line to be set.")
        if isinstance(ideal_line_columns, str):
            raise ValueError(
                "ideal_line_columns must be a sequence of CI-column keys, not a string."
            )
        try:
            requested_ideal_columns = tuple(ideal_line_columns)
        except TypeError as error:
            raise ValueError("ideal_line_columns must be a sequence of CI-column keys.") from error
        if any(not isinstance(key, str) or not key for key in requested_ideal_columns):
            raise ValueError("ideal_line_columns must contain non-empty strings only.")
        if len(requested_ideal_columns) != len(set(requested_ideal_columns)):
            raise ValueError("ideal_line_columns must not contain duplicate keys.")
        invalid_ideal_columns = sorted(set(requested_ideal_columns) - set(active_ci))
        if invalid_ideal_columns:
            raise ValueError(
                "ideal_line_columns must name active columns with role='ci'; "
                f"invalid={invalid_ideal_columns}."
            )
        ideal_line_targets = frozenset(requested_ideal_columns)

    if legend is not None:
        _validate_legend_position(legend, keys=all_keys)
    if reference_legend is not None:
        _validate_legend_position(reference_legend, keys=all_keys)
        if reference_legend.reference_label is not None and not isinstance(
            reference_legend.reference_label, str
        ):
            raise ValueError("reference_label must be a string or None.")
        if reference_legend.ideal_label is not None and not isinstance(
            reference_legend.ideal_label, str
        ):
            raise ValueError("ideal_label must be a string or None.")
        if reference_legend.ideal_label and ideal_line is None:
            raise ValueError("An ideal_label requires ideal_line to be set.")
        if reference_legend.ideal_label and not ideal_line_targets:
            raise ValueError("An ideal_label requires at least one active ideal-line target.")
        if not reference_legend.reference_label and not reference_legend.ideal_label:
            raise ValueError("reference_legend must define at least one label.")

    styles = _series_styles(table, series_styles, style)
    if legend is not None and not styles:
        raise ValueError("A series legend requires at least one observed series.")
    if xlim is None:
        if not table.observations:
            raise ValueError("xlim is required when the data contain no confidence intervals.")
        lower_min = min(float(item.lower) for item in table.observations if item.lower is not None)
        upper_max = max(float(item.upper) for item in table.observations if item.upper is not None)
        spread = upper_max - lower_min
        padding = max(spread * 0.08, 0.1)
        xlim = (lower_min - padding, upper_max + padding)
    if len(xlim) != 2 or not np.isfinite(xlim).all() or xlim[0] >= xlim[1]:
        raise ValueError("xlim must contain two increasing finite values.")
    ticks = np.asarray(ticks_at if ticks_at is not None else np.linspace(*xlim, 5), dtype=float)
    if not np.isfinite(ticks).all():
        raise ValueError("Forest ticks must be finite.")
    if not np.isfinite(ref_line):
        raise ValueError("ref_line must be finite.")
    if ideal_line is not None and not np.isfinite(ideal_line):
        raise ValueError("ideal_line must be finite when provided.")

    row_centers, row_bounds, row_scales = _compute_row_geometry(len(table.plot_rows))
    total_rows = float(len(table.plot_rows))
    max_header_lines = max(
        (len(column.header.splitlines()) for column in resolved_columns), default=1
    )
    base_header_height = max(0.86, 0.46 + 0.20 * max_header_lines)
    header_specs: list[tuple[str, int, int]] = []
    bottom_specs: list[tuple[str, int, int]] = []
    if legend is not None:
        target = header_specs if legend.location == "header" else bottom_specs
        target.append(("series", len(styles), legend.ncol))
    reference_count = 0
    if reference_legend is not None:
        reference_count = int(bool(reference_legend.reference_label)) + int(
            bool(reference_legend.ideal_label)
        )
        target = header_specs if reference_legend.location == "header" else bottom_specs
        target.append(("reference", reference_count, reference_legend.ncol))
    header_legend_heights = [_legend_height(count, ncol) for _, count, ncol in header_specs]
    header_height = base_header_height + sum(header_legend_heights) + 0.06 * len(header_specs)
    footer_cursor = -1.08 if arrow_lab else -0.34
    bottom_centers: dict[str, float] = {}
    for kind, count, ncol in bottom_specs:
        height = _legend_height(count, ncol)
        bottom_centers[kind] = footer_cursor - height / 2.0
        footer_cursor -= height + 0.08
    footer_height = max(1.20 if arrow_lab else 0.42, -footer_cursor + 0.12)
    title_height = 0.40 if title else 0.0
    figure_height = max(2.4, header_height + footer_height + row_height * total_rows + title_height)

    fig, ax = plt.subplots(figsize=(final_figure_width, figure_height))
    horizontal_edge = table_spec.edge_padding_pt / (final_figure_width * 72.0)
    vertical_edge = min(0.025, table_spec.edge_padding_pt / (figure_height * 72.0))
    fig.subplots_adjust(
        left=horizontal_edge,
        right=1.0 - horizontal_edge,
        bottom=vertical_edge,
        top=1.0 - vertical_edge,
    )
    ax.set_xlim(0, 1)
    ax.set_ylim(-footer_height, total_rows + header_height + title_height)
    ax.axis("off")
    usable_width_pt = final_figure_width * 72.0 - 2.0 * table_spec.edge_padding_pt
    cell_padding = table_spec.column_padding_pt / usable_width_pt

    ax.add_patch(
        Rectangle(
            (0, total_rows),
            1,
            header_height,
            facecolor=style.header_fill,
            edgecolor="none",
            zorder=0,
        )
    )
    for index, row in enumerate(table.plot_rows):
        bottom, top = row_bounds[index]
        ax.add_patch(
            Rectangle(
                (0, bottom),
                1,
                top - bottom,
                facecolor=_row_fill(row.row_type, index, style),
                edgecolor="none",
                zorder=0,
            )
        )
    for span in table.spans:
        cell = by_key[span.column_key]
        bottom = row_bounds[span.end_row][0]
        top = row_bounds[span.start_row][1]
        ax.add_patch(
            Rectangle(
                (cell.left, bottom),
                cell.right - cell.left,
                top - bottom,
                facecolor=_row_fill(
                    table.plot_rows[span.start_row].row_type, span.start_row, style
                ),
                edgecolor="none",
                zorder=0.5,
                gid=f"merged-cell:{span.column_key}:{span.start_record}:{span.end_record}",
            )
        )

    if style.show_table_border:
        # Horizontal separators stop at supported merged display cells.
        for row_index, (bottom, _) in enumerate(row_bounds):
            blocked = sorted(
                (
                    by_key[span.column_key].left,
                    by_key[span.column_key].right,
                )
                for span in table.spans
                if span.start_row <= row_index < span.end_row
            )
            cursor = 0.0
            segment_index = 0
            for left, right in blocked:
                if left > cursor:
                    artist = ax.plot(
                        [cursor, left],
                        [bottom, bottom],
                        color=style.grid_color,
                        linewidth=0.35,
                        zorder=1,
                    )[0]
                    artist.set_gid(f"table-border:row:{row_index}:segment:{segment_index}")
                    segment_index += 1
                cursor = max(cursor, right)
            if cursor < 1.0:
                artist = ax.plot(
                    [cursor, 1.0],
                    [bottom, bottom],
                    color=style.grid_color,
                    linewidth=0.35,
                    zorder=1,
                )[0]
                artist.set_gid(f"table-border:row:{row_index}:segment:{segment_index}")

        for name, y, linewidth in (
            ("header-separator", total_rows, 0.9),
            ("top", total_rows + header_height, 0.8),
        ):
            artist = ax.plot(
                [0, 1],
                [y, y],
                color=style.grid_color,
                linewidth=linewidth,
                zorder=2,
            )[0]
            artist.set_gid(f"table-border:{name}")

        if not style.show_vertical_grid:
            for name, x in (("left", 0.0), ("right", 1.0)):
                artist = ax.plot(
                    [x, x],
                    [0, total_rows + header_height],
                    color=style.grid_color,
                    linewidth=0.8,
                    zorder=1,
                )[0]
                artist.set_gid(f"table-border:{name}")

    if style.show_vertical_grid:
        for item in geometry:
            artist = ax.plot(
                [item.left, item.left],
                [0, total_rows + header_height],
                color=style.grid_color,
                linewidth=0.45,
                zorder=1,
            )[0]
            artist.set_gid(f"table-grid:column:{item.key}")
        artist = ax.plot(
            [1, 1],
            [0, total_rows + header_height],
            color=style.grid_color,
            linewidth=0.45,
            zorder=1,
        )[0]
        artist.set_gid("table-grid:right")

    header_text_y = total_rows + header_height - base_header_height / 2.0
    header_artists: list[tuple[str, Any, ColumnGeometry]] = []
    for column, cell in zip(resolved_columns, geometry, strict=True):
        x = (cell.left + cell.right) / 2.0
        if column.alignment == "left":
            x = cell.left + cell_padding
        elif column.alignment == "right":
            x = cell.right - cell_padding
        header_artist = ax.text(
            x,
            header_text_y,
            column.header,
            ha=column.alignment,
            va="center",
            fontsize=style.base_font_size,
            fontweight="bold",
            color=style.text_color,
            linespacing=1.15,
        )
        header_artists.append((column.key, header_artist, cell))

    for ci_key in active_ci:
        cell = by_key[ci_key]
        plot_left = cell.left + (cell.right - cell.left) * 0.08
        plot_right = cell.right - (cell.right - cell.left) * 0.08
        if xlim[0] <= ref_line <= xlim[1]:
            x_ref = _value_to_canvas(ref_line, plot_left, plot_right, xlim)
            reference_line_artist = ax.plot(
                [x_ref, x_ref],
                [0, total_rows],
                color=style.reference_color,
                linewidth=0.9,
                linestyle=style.reference_line_style,
                zorder=2,
            )[0]
            reference_line_artist.set_gid(f"reference-line:{ci_key}")
        if (
            ideal_line is not None
            and ci_key in ideal_line_targets
            and xlim[0] <= ideal_line <= xlim[1]
        ):
            x_ideal = _value_to_canvas(ideal_line, plot_left, plot_right, xlim)
            ideal_line_artist = ax.plot(
                [x_ideal, x_ideal],
                [0, total_rows],
                color=style.ideal_color,
                linewidth=1.0,
                linestyle=style.ideal_line_style,
                zorder=2,
            )[0]
            ideal_line_artist.set_gid(f"ideal-line:{ci_key}")
        for tick in ticks:
            if xlim[0] <= tick <= xlim[1]:
                x_tick = _value_to_canvas(float(tick), plot_left, plot_right, xlim)
                ax.plot([x_tick, x_tick], [-0.08, 0], color=style.muted_color, linewidth=0.6)
                ax.text(
                    x_tick,
                    -0.13,
                    f"{tick:g}",
                    ha="center",
                    va="top",
                    fontsize=style.base_font_size - 0.5,
                    color=style.muted_color,
                )

    plot_row_index = {row.plot_row: index for index, row in enumerate(table.plot_rows)}
    clipped = 0
    observation_positions: list[tuple[Any, str, str, float]] = []
    for observation in table.observations:
        cell = by_key[observation.ci_column]
        plot_left = cell.left + (cell.right - cell.left) * 0.08
        plot_right = cell.right - (cell.right - cell.left) * 0.08
        y = row_centers[plot_row_index[observation.plot_row]]
        series_style = styles[observation.series]
        assert observation.estimate is not None
        assert observation.lower is not None
        assert observation.upper is not None
        clipped += _draw_clipped_interval(
            ax,
            estimate=float(observation.estimate),
            lower=float(observation.lower),
            upper=float(observation.upper),
            y=y,
            left=plot_left,
            right=plot_right,
            xlim=xlim,
            color=series_style.color,
            summary=observation.is_summary,
            marker=series_style.marker,
            summary_marker=series_style.summary_marker,
            record_index=observation.record_index,
        )
        observation_positions.append(
            (observation.plot_row, observation.series, observation.ci_column, y)
        )

    span_by_column: dict[str, list[Any]] = {}
    for span in table.spans:
        span_by_column.setdefault(span.column_key, []).append(span)
    for column in resolved_columns:
        if column.role == "ci":
            continue
        cell = by_key[column.key]
        covered_rows: set[int] = set()
        for span in span_by_column.get(column.key, []):
            covered_rows.update(range(span.start_row, span.end_row + 1))
            bottom = row_bounds[span.end_row][0]
            top = row_bounds[span.start_row][1]
            y = (bottom + top) / 2.0
            row = table.plot_rows[span.start_row]
            x = (cell.left + cell.right) / 2.0
            if column.alignment == "left":
                x = cell.left + cell_padding + row.indent * 0.014
            elif column.alignment == "right":
                x = cell.right - cell_padding
            ax.text(
                x,
                y,
                str(span.value),
                ha=column.alignment,
                va="center",
                fontsize=style.base_font_size,
                fontweight="bold" if row.row_type in {"header", "summary"} else "normal",
                color=style.text_color,
                clip_on=True,
                gid=f"merged-text:{column.key}:{span.start_record}:{span.end_record}",
            )
        for row_index, row in enumerate(table.plot_rows):
            if row_index in covered_rows or row.row_type == "spacer":
                continue
            value = row.value(column.key)
            if value is None or pd.isna(value) or str(value) == "":
                continue
            x = (cell.left + cell.right) / 2.0
            if column.alignment == "left":
                x = cell.left + cell_padding + row.indent * 0.014
            elif column.alignment == "right":
                x = cell.right - cell_padding
            ax.text(
                x,
                row_centers[row_index],
                str(value),
                ha=column.alignment,
                va="center",
                fontsize=style.base_font_size,
                fontweight="bold" if row.row_type in {"header", "summary"} else "normal",
                color=style.text_color,
                clip_on=True,
                gid=f"cell-text:{column.key}:{row.plot_row}",
            )

    if arrow_lab:
        ci_cell = by_key[active_ci[0]]
        center = (ci_cell.left + ci_cell.right) / 2.0
        ax.text(
            ci_cell.left + 0.01,
            -0.94,
            arrow_lab[0],
            ha="left",
            va="bottom",
            fontsize=style.base_font_size - 0.5,
            color=style.muted_color,
        )
        ax.text(
            ci_cell.right - 0.01,
            -0.94,
            arrow_lab[1],
            ha="right",
            va="bottom",
            fontsize=style.base_font_size - 0.5,
            color=style.muted_color,
        )
        ax.annotate(
            "",
            xy=(ci_cell.left + 0.03, -0.55),
            xytext=(center, -0.55),
            arrowprops={"arrowstyle": "-|>", "color": style.muted_color, "lw": 0.7},
        )
        ax.annotate(
            "",
            xy=(ci_cell.right - 0.03, -0.55),
            xytext=(center, -0.55),
            arrowprops={"arrowstyle": "-|>", "color": style.muted_color, "lw": 0.7},
        )

    legend_artists: list[tuple[str, Any, float, float]] = []
    header_cursor = total_rows + header_height - base_header_height
    if legend is not None:
        handles = [
            Line2D(
                [0],
                [0],
                color=styles[name].color,
                marker=styles[name].marker,
                linewidth=1.2,
                markersize=4.5,
                label=styles[name].label,
            )
            for name in table.series_order
        ]
        if legend.location == "header":
            height = _legend_height(len(handles), legend.ncol)
            y = header_cursor - height / 2.0
            header_cursor -= height + 0.06
        else:
            y = bottom_centers["series"]
        left, right = _legend_x_span(
            column_key=legend.column_key,
            by_key=by_key,
            ci_columns=active_ci,
        )
        series_legend_artist = ax.legend(
            handles=handles,
            loc="center",
            bbox_to_anchor=((left + right) / 2.0, y),
            bbox_transform=ax.transData,
            ncol=legend.ncol,
            frameon=False,
            fontsize=style.base_font_size - 0.5,
            handlelength=1.5,
            columnspacing=0.8,
        )
        series_legend_artist.set_gid("forest-legend:series")
        ax.add_artist(series_legend_artist)
        legend_artists.append(("series", series_legend_artist, left, right))
    if reference_legend is not None:
        reference_handles: list[Line2D] = []
        if reference_legend.reference_label:
            reference_handles.append(
                Line2D(
                    [0],
                    [0],
                    color=style.reference_color,
                    linestyle=cast(Any, style.reference_line_style),
                    linewidth=1.1,
                    label=reference_legend.reference_label,
                )
            )
        if reference_legend.ideal_label:
            reference_handles.append(
                Line2D(
                    [0],
                    [0],
                    color=style.ideal_color,
                    linestyle=cast(Any, style.ideal_line_style),
                    linewidth=1.2,
                    label=reference_legend.ideal_label,
                )
            )
        if reference_legend.location == "header":
            height = _legend_height(len(reference_handles), reference_legend.ncol)
            y = header_cursor - height / 2.0
            header_cursor -= height + 0.06
        else:
            y = bottom_centers["reference"]
        left, right = _legend_x_span(
            column_key=reference_legend.column_key,
            by_key=by_key,
            ci_columns=active_ci,
        )
        reference_legend_artist = ax.legend(
            handles=reference_handles,
            loc="center",
            bbox_to_anchor=((left + right) / 2.0, y),
            bbox_transform=ax.transData,
            ncol=reference_legend.ncol,
            frameon=False,
            fontsize=style.base_font_size - 0.5,
            handlelength=2.0,
            columnspacing=1.0,
        )
        reference_legend_artist.set_gid("forest-legend:reference")
        ax.add_artist(reference_legend_artist)
        legend_artists.append(("reference", reference_legend_artist, left, right))

    if title:
        ax.text(
            0,
            total_rows + header_height + 0.12,
            title,
            ha="left",
            va="bottom",
            fontsize=style.base_font_size + 2.0,
            fontweight="bold",
            color=style.text_color,
        )

    fig.canvas.draw()
    renderer = cast(Any, fig.canvas).get_renderer()
    figure_bbox = fig.bbox
    overflow_columns: list[str] = []
    for key, artist, cell in header_artists:
        if not artist.get_text():
            continue
        bbox = artist.get_window_extent(renderer=renderer)
        left_px = ax.transData.transform((cell.left, 0))[0]
        right_px = ax.transData.transform((cell.right, 0))[0]
        if (
            bbox.x0 < left_px - 0.5
            or bbox.x1 > right_px + 0.5
            or bbox.x0 < figure_bbox.x0
            or bbox.x1 > figure_bbox.x1
        ):
            overflow_columns.append(key)
    if overflow_columns:
        plt.close(fig)
        raise ValueError(f"Forest header layout overflow in columns: {', '.join(overflow_columns)}")

    legend_bounds: list[tuple[str, float, float, float, float]] = []
    for kind, artist, target_left, target_right in legend_artists:
        bbox = artist.get_window_extent(renderer=renderer)
        (left, bottom), (right, top) = ax.transData.inverted().transform(
            [[bbox.x0, bbox.y0], [bbox.x1, bbox.y1]]
        )
        spec = legend if kind == "series" else reference_legend
        assert spec is not None
        if left < target_left - 0.015 or right > target_right + 0.015:
            plt.close(fig)
            raise ValueError(
                f"Forest {kind} legend does not fit within its target column/CI region."
            )
        if spec.location == "header" and (bottom < total_rows or top > total_rows + header_height):
            plt.close(fig)
            raise ValueError(f"Forest {kind} legend overflows the header region.")
        if spec.location == "bottom" and (bottom < -footer_height or top > 0):
            plt.close(fig)
            raise ValueError(f"Forest {kind} legend overflows the bottom region.")
        legend_bounds.append((kind, float(left), float(bottom), float(right), float(top)))

    resolved_spans = tuple(
        (
            span.column_key,
            table.plot_rows[span.start_row].plot_row,
            table.plot_rows[span.end_row].plot_row,
            float(row_bounds[span.end_row][0]),
            float(row_bounds[span.start_row][1]),
        )
        for span in table.spans
    )
    diagnostics = ForestLayoutDiagnostics(
        series_gap_used=0.0,
        row_bounds=row_bounds,
        row_scales=row_scales,
        wrapped_headers=tuple((column.key, column.header) for column in resolved_columns),
        final_figure_width=float(final_figure_width),
        header_overflow_count=0,
        plot_row_ids=tuple(row.plot_row for row in table.plot_rows),
        observation_positions=tuple(observation_positions),
        resolved_spans=resolved_spans,
        legend_bounds=tuple(legend_bounds),
    )
    return ForestPlotResult(fig, ax, geometry, row_centers, clipped, diagnostics)


__all__ = ["ForestPlotResult", "forest"]

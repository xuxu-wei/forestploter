"""Column, legend, layout, and geometry definitions for forest plots.

Vertical dimensions use one standard visual row as their unit. Horizontal
column boundaries are normalized to ``[0, 1]``. ``ForestDataMapping.plot_row``
controls how source records form visual rows; series are never offset
implicitly by this module.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Literal

import numpy as np


@dataclass(frozen=True)
class ForestColumn:
    """Define a display column or a confidence-interval plotting area.

    Parameters
    ----------
    key : str
        Unique column identifier. For ``role="text"`` or ``"numeric"``, it
        must name a display field in the long table. For ``role="ci"``, it
        must match values in the record-level ``_ci_column`` field.
    header : str
        Header text. Newline characters are allowed.
    role : {"text", "numeric", "ci"}
        Rendering role. The first two draw cell text; ``"ci"`` draws point
        estimates and intervals.
    width : float
        Finite positive relative column width.
    alignment : {"left", "center", "right"}, default "left"
        Horizontal alignment for the header and body cells.

    Notes
    -----
    Display fields may use supported vertical XLSX merges. A CI column is a
    layout slot and does not need to be a physical file field; records target
    it through ``_ci_column``. The sequence passed as ``columns`` is the sole
    authority for final left-to-right order, so text columns can follow CI
    columns even when the input-file fields are arranged differently.
    """

    key: str
    header: str
    role: str
    width: float
    alignment: str = "left"


@dataclass(frozen=True)
class ColumnGeometry:
    """Store the normalized horizontal boundaries of one column.

    Parameters
    ----------
    key : str
        Key of the corresponding :class:`ForestColumn`.
    left : float
        Left boundary.
    right : float
        Right boundary, which is greater than ``left``.
    """

    key: str
    left: float
    right: float


@dataclass(frozen=True)
class ForestSeriesStyle:
    """Define the color, marker, and legend label for one series.

    Parameters
    ----------
    label : str
        Display label used in the legend.
    color : str
        Matplotlib color specification.
    marker : str, default "s"
        Matplotlib marker for ordinary estimates.
    summary_marker : {"diamond", "same"}, default "diamond"
        Summary marker. ``"diamond"`` draws a diamond; ``"same"`` reuses
        ``marker``.

    Notes
    -----
    In :func:`forestploter.forest`, ``series_styles`` is keyed by ``_series``
    values, so styling is independent of source-record order.
    """

    label: str
    color: str
    marker: str = "s"
    summary_marker: str = "diamond"


@dataclass(frozen=True)
class ForestLegendSpec:
    """Place and arrange the series legend.

    Parameters
    ----------
    location : {"header", "bottom"}, default "header"
        Place the legend in a column-header region or below the table.
    column_key : str or None, default None
        Required for ``location="header"`` and may point to any display or CI
        column. For ``location="bottom"``, omit it to center the legend below
        all active CI columns, or provide it to center below one column.
    ncol : int, default 2
        Number of legend columns; must be a positive integer.
    """

    location: Literal["header", "bottom"] = "header"
    column_key: str | None = None
    ncol: int = 2


@dataclass(frozen=True)
class ForestTableLayoutSpec:
    """Configure automatic column widths, header wrapping, and margins.

    Parameters
    ----------
    auto_width : bool, default True
        Whether to measure visible text and adjust column widths.
    auto_wrap_headers : bool, default True
        Whether to wrap headers automatically at word boundaries.
    column_padding_pt : float, default 6
        Left and right cell padding in points.
    edge_padding_pt : float, default 4
        Left and right figure-edge padding in points.
    max_header_lines : int, default 3
        Maximum line count for one header.
    max_figure_width : float, default 16
        Maximum automatically expanded Figure width in inches.
    """

    auto_width: bool = True
    auto_wrap_headers: bool = True
    column_padding_pt: float = 6.0
    edge_padding_pt: float = 4.0
    max_header_lines: int = 3
    max_figure_width: float = 16.0


@dataclass(frozen=True)
class ForestReferenceLegendSpec:
    """Place and label reference-line and ideal-line legend entries.

    Parameters
    ----------
    reference_label : str or None, default None
        Legend label for ``ref_line``.
    ideal_label : str or None, default None
        Legend label for ``ideal_line``.
    location : {"header", "bottom"}, default "bottom"
        Place the legend in a column-header region or below the table.
    column_key : str or None, default None
        Uses the same placement rules as :class:`ForestLegendSpec`.
    ncol : int, default 2
        Number of legend columns; must be a positive integer.
    """

    reference_label: str | None = None
    ideal_label: str | None = None
    location: Literal["header", "bottom"] = "bottom"
    column_key: str | None = None
    ncol: int = 2


@dataclass(frozen=True)
class ForestLayoutDiagnostics:
    """Store layout diagnostics suitable for automated acceptance checks.

    Parameters
    ----------
    series_gap_used : float
        Always ``0.0`` because the explicit long-table model never offsets
        series implicitly.
    row_bounds : tuple of tuple of float
        ``(bottom, top)`` pairs in unique ``_plot_row`` order.
    row_scales : tuple of float
        Relative height multiplier for every visual row.
    wrapped_headers : tuple of tuple of str
        ``(column_key, final_header)`` pairs.
    final_figure_width : float
        Final Figure width in inches.
    header_overflow_count : int
        Number of headers overflowing their column or Figure boundary.
    plot_row_ids : tuple
        Visual-row identifiers in the same order as ``row_bounds`` and the
        result's ``row_centers``.
    observation_positions : tuple of tuple
        ``(plot_row, series, ci_column, y)`` for every drawable observation.
    resolved_spans : tuple of tuple
        ``(column_key, start_plot_row, end_plot_row, bottom, top)`` for each
        resolved merged-cell span.
    legend_bounds : tuple of tuple
        ``(kind, left, bottom, right, top)`` bounds for every legend in data
        coordinates.
    """

    series_gap_used: float
    row_bounds: tuple[tuple[float, float], ...]
    row_scales: tuple[float, ...]
    wrapped_headers: tuple[tuple[str, str], ...]
    final_figure_width: float
    header_overflow_count: int
    plot_row_ids: tuple[Any, ...] = ()
    observation_positions: tuple[tuple[Any, str, str, float], ...] = ()
    resolved_spans: tuple[tuple[str, Any, Any, float, float], ...] = ()
    legend_bounds: tuple[tuple[str, float, float, float, float], ...] = ()


def compute_column_geometry(columns: Sequence[ForestColumn]) -> tuple[ColumnGeometry, ...]:
    """Convert relative widths to contiguous boundaries within ``[0, 1]``.

    Parameters
    ----------
    columns : sequence of ForestColumn
        Column definitions in final left-to-right plot order.

    Returns
    -------
    tuple of ColumnGeometry
        Boundaries corresponding one-to-one with the input sequence.

    Raises
    ------
    ValueError
        Raised for an empty sequence, duplicate keys, unsupported roles or
        alignments, or non-finite/non-positive widths.
    """

    if not columns:
        raise ValueError("At least one forest column is required.")
    keys = [column.key for column in columns]
    if any(not isinstance(key, str) or not key for key in keys):
        raise ValueError("Forest column keys must be non-empty strings.")
    if len(keys) != len(set(keys)):
        raise ValueError("Forest column keys must be unique.")
    if any(not isinstance(column.header, str) for column in columns):
        raise ValueError("Forest column headers must be strings.")
    invalid_roles = sorted({column.role for column in columns} - {"text", "numeric", "ci"})
    if invalid_roles:
        raise ValueError(f"Unsupported forest column roles: {invalid_roles}")
    invalid_alignments = sorted(
        {column.alignment for column in columns} - {"left", "center", "right"}
    )
    if invalid_alignments:
        raise ValueError(f"Unsupported forest column alignments: {invalid_alignments}")
    widths = np.asarray([column.width for column in columns], dtype=float)
    if not np.isfinite(widths).all() or np.any(widths <= 0):
        raise ValueError("Forest column widths must be finite and positive.")
    edges = np.concatenate([[0.0], np.cumsum(widths) / widths.sum()])
    return tuple(
        ColumnGeometry(column.key, float(edges[index]), float(edges[index + 1]))
        for index, column in enumerate(columns)
    )


__all__ = [
    "ColumnGeometry",
    "ForestColumn",
    "ForestLayoutDiagnostics",
    "ForestLegendSpec",
    "ForestReferenceLegendSpec",
    "ForestSeriesStyle",
    "ForestTableLayoutSpec",
    "compute_column_geometry",
]

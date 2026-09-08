"""Visual theme for table-style forest plots.

The theme stores rendering styles only; it does not validate data or determine
axis ranges and layout. Colors and line styles are passed directly to
Matplotlib and therefore accept Matplotlib-supported string specifications.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ForestTheme:
    """Define visual styles for the table, text, intervals, and guide lines.

    Parameters
    ----------
    base_font_size : float, default 8.5
        Base font size for headers, body text, ticks, and legends, in points.
    header_fill : str, default "#EAF0F6"
        Header background color.
    alternate_fill : str, default "#F7F9FC"
        Alternating fill used for odd-indexed rows that are neither spacers nor
        group headers.
    group_fill : str, default "#F0F4F8"
        Background color for ``"header"`` group rows.
    text_color : str, default "#202B33"
        Header, body, tick, and default series-text color.
    muted_color : str, default "#667085"
        Color for secondary text such as bottom direction labels.
    ci_colors : tuple of str, default ("#1F4E79", "#D97706", "#4472C4")
        Colors cycled across series when ``series_styles`` is omitted. The
        tuple must contain at least one color when default styles are used.
    summary_fill : str, default "#1F4E79"
        Reserved summary-diamond fill. The current renderer uses the matching
        series ``color`` and does not yet read this field.
    grid_color : str, default "#D0D5DD"
        Color for horizontal rules, optional vertical rules, and borders.
    reference_color : str, default "#344054"
        Color for ``ref_line`` and its legend entry.
    ideal_color : str, default "#C69C3C"
        Color for ``ideal_line`` and its legend entry.
    show_vertical_grid : bool, default False
        Whether to draw vertical column separators. This setting is
        independent of ``show_table_border``.
    reference_line_style : str, default "--"
        Matplotlib line style for the reference line.
    ideal_line_style : str, default ":"
        Matplotlib line style for the ideal line.
    show_table_border : bool, default False
        Whether to add side borders and internal horizontal row separators.
        The default is a three-rule table: a rule above and below the column
        headers, plus a bottom rule, with no internal row separators or side
        borders. These three rules remain visible with either setting. Set
        ``show_vertical_grid=True`` as well for a fully boxed table.

    Notes
    -----
    Theme objects are frozen data classes and can be reused safely. Create a
    new instance for per-call changes instead of mutating during rendering.
    """

    base_font_size: float = 8.5
    header_fill: str = "#EAF0F6"
    alternate_fill: str = "#F7F9FC"
    group_fill: str = "#F0F4F8"
    text_color: str = "#202B33"
    muted_color: str = "#667085"
    ci_colors: tuple[str, ...] = ("#1F4E79", "#D97706", "#4472C4")
    summary_fill: str = "#1F4E79"
    grid_color: str = "#D0D5DD"
    reference_color: str = "#344054"
    ideal_color: str = "#C69C3C"
    show_vertical_grid: bool = False
    reference_line_style: str = "--"
    ideal_line_style: str = ":"
    show_table_border: bool = False


__all__ = ["ForestTheme"]

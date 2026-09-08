"""Executable plotting functions used by the example gallery and test suite.

Each function accepts ``df``, the :class:`forestploter.ForestData` returned by
:func:`forestploter.read_forest_data` (a compatible ``pandas.DataFrame`` is
also accepted). Keeping plotting code here gives the documentation, image
renderer, and regression tests one shared source of truth.
"""

from __future__ import annotations

import pandas as pd

from .core import ForestPlotResult, forest
from .data import ForestData
from .layout import (
    ForestColumn,
    ForestLegendSpec,
    ForestReferenceLegendSpec,
    ForestSeriesStyle,
    ForestTableLayoutSpec,
)
from .theme import ForestTheme

ForestInput = ForestData | pd.DataFrame


def plot_single_series(df: ForestInput) -> ForestPlotResult:
    """Plot case 01: display columns on both sides of the CI column."""

    columns = (
        ForestColumn("label", "Outcome / study", "text", 2.8),
        ForestColumn("n", "N", "numeric", 0.7, "right"),
        ForestColumn("ci", "Treatment effect", "ci", 3.3, "center"),
        ForestColumn("effect_display", "Mean difference [95% CI]", "numeric", 2.0, "right"),
    )
    return forest(
        df,
        columns=columns,
        ref_line=0.0,
        ideal_line=-0.25,
        xlim=(-1.0, 1.0),
        ticks_at=(-1.0, -0.5, 0.0, 0.5, 1.0),
        arrow_lab=("Favours treatment", "Favours control"),
        title="Single-series efficacy and safety results",
        figure_width=11.5,
        reference_legend=ForestReferenceLegendSpec(
            reference_label="No difference",
            ideal_label="Target effect",
            location="bottom",
            column_key="ci",
            ncol=2,
        ),
    )


def plot_multi_series(df: ForestInput) -> ForestPlotResult:
    """Plot case 02: three series in one CI column."""

    columns = (
        ForestColumn("outcome", "Outcome", "text", 2.8),
        ForestColumn("participants", "Participants", "numeric", 0.9, "right"),
        ForestColumn("ci", "", "ci", 4.6, "center"),
    )
    styles = {
        "Treatment A": ForestSeriesStyle("Treatment A", "#1F4E79", marker="s"),
        "Treatment B": ForestSeriesStyle("Treatment B", "#D97706", marker="o"),
        "Treatment C": ForestSeriesStyle("Treatment C", "#5B8C5A", marker="^"),
    }
    return forest(
        df,
        columns=columns,
        ref_line=1.0,
        xlim=(0.4, 1.6),
        ticks_at=(0.4, 0.7, 1.0, 1.3, 1.6),
        arrow_lab=("Favours treatment", "Favours control"),
        title="Three treatment series, one explicit visual row per series",
        figure_width=10.8,
        series_styles=styles,
        legend=ForestLegendSpec(location="header", column_key="ci", ncol=3),
    )


def plot_dual_ci_columns(df: ForestInput) -> ForestPlotResult:
    """Plot case 03: one series aligned across two CI columns."""

    columns = (
        ForestColumn("endpoint", "Endpoint", "text", 2.5),
        ForestColumn("n", "N", "numeric", 0.6, "right"),
        ForestColumn("ci_30d", "30-day risk ratio [95% CI]", "ci", 3.0, "center"),
        ForestColumn("ci_90d", "90-day risk ratio [95% CI]", "ci", 3.0, "center"),
    )
    return forest(
        df,
        columns=columns,
        ref_line=1.0,
        xlim=(0.4, 1.6),
        ticks_at=(0.4, 0.7, 1.0, 1.3, 1.6),
        title="The same plot row aligned across two follow-up columns",
        figure_width=12.0,
        series_styles={"Observed": ForestSeriesStyle("Observed", "#1F4E79", marker="s")},
    )


def plot_clipping_stress(df: ForestInput) -> ForestPlotResult:
    """Plot case 04: partially and fully off-scale intervals."""

    columns = (
        ForestColumn("scenario", "Scenario", "text", 2.4),
        ForestColumn("expected_clipping", "Expected clipping", "text", 1.2),
        ForestColumn("interval_display", "Estimate [95% CI]", "numeric", 1.8, "right"),
        ForestColumn("ci", "Displayed range: -1 to 1", "ci", 3.2, "center"),
    )
    return forest(
        df,
        columns=columns,
        ref_line=0.0,
        xlim=(-1.0, 1.0),
        ticks_at=(-1.0, -0.5, 0.0, 0.5, 1.0),
        arrow_lab=("Lower", "Higher"),
        title="Clipping and fully off-scale interval stress test",
        figure_width=12.0,
    )


def plot_long_layout(df: ForestInput) -> ForestPlotResult:
    """Plot case 05: long labels, multilingual text, and auto layout."""

    columns = (
        ForestColumn("subgroup", "Prespecified participant subgroup", "text", 2.8),
        ForestColumn("region", "Geographic recruitment region", "text", 1.1),
        ForestColumn("participants", "Participants analyzed", "numeric", 0.8, "right"),
        ForestColumn(
            "effect_display", "Adjusted mean difference [95% CI]", "numeric", 1.8, "right"
        ),
        ForestColumn("ci", "Adjusted treatment effect [95% CI]", "ci", 2.8, "center"),
    )
    return forest(
        df,
        columns=columns,
        ref_line=0.0,
        xlim=(-1.0, 1.0),
        ticks_at=(-1.0, -0.5, 0.0, 0.5, 1.0),
        arrow_lab=("Favours treatment", "Favours control"),
        title="Layout stress test: long labels and multilingual text",
        figure_width=7.5,
        row_height=0.42,
        theme=ForestTheme(base_font_size=8.25),
        table_layout=ForestTableLayoutSpec(
            auto_width=True,
            auto_wrap_headers=True,
            column_padding_pt=7.0,
            edge_padding_pt=6.0,
            max_header_lines=3,
            max_figure_width=16.0,
        ),
    )


def plot_auto_scale_mixed_effects(df: ForestInput) -> ForestPlotResult:
    """Plot case 06: automatic limits for heterogeneous effects."""

    columns = (
        ForestColumn("outcome", "Outcome", "text", 2.5),
        ForestColumn("scale", "Measurement scale", "text", 1.3),
        ForestColumn("n", "N", "numeric", 0.6, "right"),
        ForestColumn("effect_display", "Standardized effect [95% CI]", "numeric", 2.0, "right"),
        ForestColumn("ci", "Automatically derived axis", "ci", 3.4, "center"),
    )
    return forest(
        df,
        columns=columns,
        ref_line=0.0,
        ideal_line=-0.5,
        xlim=None,
        ticks_at=None,
        arrow_lab=("Lower standardized effect", "Higher standardized effect"),
        title="Automatic axis range across heterogeneous effect magnitudes",
        figure_width=12.5,
        reference_legend=ForestReferenceLegendSpec(
            reference_label="No difference",
            ideal_label="Target effect",
            location="bottom",
            ncol=2,
        ),
    )


def plot_four_series_dense(df: ForestInput) -> ForestPlotResult:
    """Plot case 07: four dense series with a bottom legend."""

    columns = (
        ForestColumn("endpoint", "Endpoint", "text", 2.5),
        ForestColumn("participants", "Participants", "numeric", 0.8, "right"),
        ForestColumn("ci", "", "ci", 5.2, "center"),
    )
    styles = {
        "Regimen A": ForestSeriesStyle("Regimen A", "#1F4E79", marker="s"),
        "Regimen B": ForestSeriesStyle("Regimen B", "#D97706", marker="o"),
        "Regimen C": ForestSeriesStyle("Regimen C", "#5B8C5A", marker="^"),
        "Regimen D": ForestSeriesStyle("Regimen D", "#A23B72", marker="D", summary_marker="same"),
    }
    return forest(
        df,
        columns=columns,
        ref_line=1.0,
        xlim=(0.4, 1.6),
        ticks_at=(0.4, 0.7, 1.0, 1.3, 1.6),
        arrow_lab=("Favours regimen", "Favours comparator"),
        title="Four dense treatment series as explicit source rows",
        figure_width=11.5,
        series_styles=styles,
        legend=ForestLegendSpec(location="bottom", ncol=2),
    )


def plot_two_by_two_ci_columns(df: ForestInput) -> ForestPlotResult:
    """Plot case 08: two series, two aligned CI columns, then text."""

    columns = (
        ForestColumn("outcome", "Outcome", "text", 2.4),
        ForestColumn("n", "N", "numeric", 0.6, "right"),
        ForestColumn("ci_crude", "Crude model [95% CI]", "ci", 3.4, "center"),
        ForestColumn("ci_adjusted", "Adjusted model [95% CI]", "ci", 3.4, "center"),
        ForestColumn("cohort", "Cohort", "text", 1.1),
    )
    styles = {
        "Cohort A": ForestSeriesStyle("Cohort A", "#1F4E79", marker="s"),
        "Cohort B": ForestSeriesStyle("Cohort B", "#D97706", marker="o"),
    }
    return forest(
        df,
        columns=columns,
        ref_line=1.0,
        xlim=(0.5, 1.5),
        ticks_at=(0.5, 0.75, 1.0, 1.25, 1.5),
        title="Two cohorts aligned across crude and adjusted CI columns",
        figure_width=14.5,
        series_styles=styles,
        legend=ForestLegendSpec(location="header", column_key="cohort", ncol=1),
    )


def plot_deep_hierarchy_many_rows(df: ForestInput) -> ForestPlotResult:
    """Plot case 09: deep indentation and many rows."""

    columns = (
        ForestColumn("label", "Region / subgroup", "text", 3.0),
        ForestColumn("n", "N", "numeric", 0.7, "right"),
        ForestColumn("effect_display", "Mean difference [95% CI]", "numeric", 2.0, "right"),
        ForestColumn("ci", "Regional treatment effect", "ci", 3.5, "center"),
    )
    return forest(
        df,
        columns=columns,
        ref_line=0.0,
        xlim=(-1.0, 1.0),
        ticks_at=(-1.0, -0.5, 0.0, 0.5, 1.0),
        arrow_lab=("Favours treatment", "Favours control"),
        title="Deep hierarchy and many-row layout stress test",
        figure_width=11.8,
        row_height=0.31,
    )


def plot_unicode_custom_theme(df: ForestInput) -> ForestPlotResult:
    """Plot case 10: Unicode labels and a custom theme."""

    columns = (
        ForestColumn("结局", "结局 / Outcome", "text", 2.2),
        ForestColumn("人群", "研究人群 / Population", "text", 2.2),
        ForestColumn("样本量", "样本量 N", "numeric", 0.7, "right"),
        ForestColumn("效应值", "效应值 [95% CI]", "numeric", 1.8, "right"),
        ForestColumn("ci", "治疗效应 / Treatment effect", "ci", 3.3, "center"),
    )
    custom_theme = ForestTheme(
        base_font_size=8.8,
        header_fill="#F3E8FF",
        alternate_fill="#FAF7FC",
        group_fill="#EDE9FE",
        ci_colors=("#6B3FA0",),
        summary_fill="#6B3FA0",
        reference_color="#374151",
        ideal_color="#C47F17",
        show_table_border=True,
        show_vertical_grid=True,
    )
    return forest(
        df,
        columns=columns,
        ref_line=0.0,
        ideal_line=-0.2,
        xlim=(-1.0, 1.0),
        ticks_at=(-1.0, -0.5, 0.0, 0.5, 1.0),
        arrow_lab=("治疗 / Treatment", "对照 / Control"),
        title="多语言标签与自定义主题 / Multilingual labels and custom theme",
        figure_width=13.0,
        row_height=0.40,
        theme=custom_theme,
        reference_legend=ForestReferenceLegendSpec(
            reference_label="无差异 / No difference",
            ideal_label="目标效应 / Target",
            location="bottom",
            column_key="ci",
            ncol=2,
        ),
        table_layout=ForestTableLayoutSpec(max_figure_width=16.0),
    )


def plot_boundary_precision(df: ForestInput) -> ForestPlotResult:
    """Plot case 11: exact boundaries and floating-point precision."""

    columns = (
        ForestColumn("scenario", "Numerical scenario", "text", 2.6),
        ForestColumn("position", "Expected position", "text", 1.2),
        ForestColumn("interval_display", "Estimate [95% CI]", "numeric", 2.2, "right"),
        ForestColumn("ci", "High-precision axis", "ci", 3.5, "center"),
    )
    return forest(
        df,
        columns=columns,
        ref_line=0.0,
        ideal_line=0.333333,
        xlim=(-1.0, 1.0),
        ticks_at=(-1.0, -0.333333, 0.0, 0.333333, 1.0),
        arrow_lab=("Lower", "Higher"),
        title="Exact limits, zero-width intervals, and floating-point precision",
        figure_width=12.5,
    )


def plot_multi_series_ci_text_rows(df: ForestInput) -> ForestPlotResult:
    """Plot case 12: one CI text and plot row for every series."""

    columns = (
        ForestColumn("outcome", "Outcome", "text", 2.5),
        ForestColumn("participants", "Participants", "numeric", 0.8, "right"),
        ForestColumn("ci", "", "ci", 4.8, "center"),
        ForestColumn(
            "series_ci_text",
            "Series estimate [95% CI]\nEach text row matches its plot row",
            "numeric",
            2.8,
            "right",
        ),
    )
    styles = {
        "Series A": ForestSeriesStyle("Series A", "#1F4E79", marker="s"),
        "Series B": ForestSeriesStyle("Series B", "#D97706", marker="o"),
        "Series C": ForestSeriesStyle("Series C", "#5B8C5A", marker="^"),
    }
    return forest(
        df,
        columns=columns,
        ref_line=1.0,
        xlim=(0.4, 1.6),
        ticks_at=(0.4, 0.7, 1.0, 1.3, 1.6),
        arrow_lab=("Favours series", "Favours comparator"),
        title="One CI text row and one plot row for every series",
        figure_width=14.0,
        series_styles=styles,
        legend=ForestLegendSpec(location="bottom", ncol=3),
    )


def plot_comprehensive_showcase(df: ForestInput) -> ForestPlotResult:
    """Plot case 13: compact hierarchy with two CI columns and three series."""

    columns = (
        ForestColumn("label", "Outcome / program", "text", 2.05),
        ForestColumn("participants", "N", "numeric", 0.55, "right"),
        ForestColumn("ci_crude", "Crude model\nrisk ratio", "ci", 2.65, "center"),
        ForestColumn(
            "crude_ci_text",
            "Crude RR [95% CI]",
            "numeric",
            1.45,
            "right",
        ),
        ForestColumn("ci_adjusted", "Adjusted model\nrisk ratio", "ci", 2.65, "center"),
        ForestColumn(
            "adjusted_ci_text",
            "Adjusted RR [95% CI]",
            "numeric",
            1.45,
            "right",
        ),
        ForestColumn("note", "Outcome-level note", "text", 1.75),
    )
    styles = {
        "Integrated care": ForestSeriesStyle("Integrated care", "#332288", marker="s"),
        "Digital support": ForestSeriesStyle("Digital support", "#CC6677", marker="o"),
        "Usual care": ForestSeriesStyle("Usual care", "#117733", marker="^"),
    }
    return forest(
        df,
        columns=columns,
        ref_line=1.0,
        ideal_line=0.75,
        ideal_line_columns=("ci_adjusted",),
        xlim=(0.5, 1.5),
        ticks_at=(0.5, 0.75, 1.0, 1.25, 1.5),
        arrow_lab=("Favours integrated care", "Favours usual care"),
        title="Comprehensive showcase: three programs across two models",
        figure_width=16.5,
        row_height=0.16,
        series_styles=styles,
        legend=ForestLegendSpec(location="bottom", ncol=3),
        reference_legend=ForestReferenceLegendSpec(
            reference_label="No effect (RR = 1)",
            ideal_label="Target (RR = 0.75; adjusted panel only)",
            location="bottom",
            ncol=2,
        ),
        theme=ForestTheme(
            base_font_size=8.2,
            header_fill="#ECE8F3",
            alternate_fill="#FAF9FC",
            group_fill="#F3EFF7",
            grid_color="#D9D2E3",
            reference_color="#45404A",
            ideal_color="#7A5542",
        ),
        table_layout=ForestTableLayoutSpec(
            auto_width=True,
            auto_wrap_headers=True,
            max_header_lines=3,
            max_figure_width=18.5,
        ),
    )


GALLERY_FUNCTIONS = {
    "single_series": plot_single_series,
    "multi_series": plot_multi_series,
    "dual_ci_columns": plot_dual_ci_columns,
    "clipping_stress": plot_clipping_stress,
    "long_layout": plot_long_layout,
    "auto_scale_mixed_effects": plot_auto_scale_mixed_effects,
    "four_series_dense": plot_four_series_dense,
    "two_by_two_ci_columns": plot_two_by_two_ci_columns,
    "deep_hierarchy_many_rows": plot_deep_hierarchy_many_rows,
    "unicode_custom_theme": plot_unicode_custom_theme,
    "boundary_precision": plot_boundary_precision,
    "multi_series_ci_text_rows": plot_multi_series_ci_text_rows,
    "comprehensive_showcase": plot_comprehensive_showcase,
}


__all__ = [
    "GALLERY_FUNCTIONS",
    "ForestInput",
    *[item.__name__ for item in GALLERY_FUNCTIONS.values()],
]

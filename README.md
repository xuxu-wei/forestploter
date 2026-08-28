# forestploter for Python

[![CI](https://github.com/xuxu-wei/forestploter/actions/workflows/ci.yml/badge.svg)](https://github.com/xuxu-wei/forestploter/actions/workflows/ci.yml)
[![Documentation](https://github.com/xuxu-wei/forestploter/actions/workflows/docs.yml/badge.svg)](https://xuxu-wei.github.io/forestploter/)
[![PyPI](https://img.shields.io/pypi/v/forestploter.svg)](https://pypi.org/project/forestploter/)
[![Python](https://img.shields.io/pypi/pyversions/forestploter.svg)](https://pypi.org/project/forestploter/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/xuxu-wei/forestploter/blob/main/LICENSE)

`forestploter` is a Python package for publication-ready, table-style forest
plots from auditable XLSX or CSV long tables. It validates the input contract,
keeps text and confidence intervals on shared row geometry, and renders static
PNG or SVG output with Matplotlib. It deliberately does not calculate effect
sizes, confidence intervals, or meta-analysis statistics.

> **Project identity:** this is an independent Python package, not the
> [`forestploter` R package](https://github.com/adayim/forestploter). It is not
> affiliated with, endorsed by, or maintained by the authors or maintainers of
> that R package.

[简体中文说明](https://github.com/xuxu-wei/forestploter/blob/main/README.zh-CN.md)

## Showcase

[![Three series aligned across two forest-plot columns with matching CI text, hierarchical header rows, clipping arrows, shared no-effect lines, one additional target line, direction labels, and bottom legends](https://raw.githubusercontent.com/xuxu-wei/forestploter/main/tests/artifacts/13_comprehensive_showcase.png)](https://xuxu-wei.github.io/forestploter/en/gallery/13_comprehensive_showcase.html)

*Three series remain row-aligned across crude and adjusted CI panels and their
matching text columns in a compact layout. CI text contains values only; marker
styling, the legend, and indented child labels identify each series. Shared
outcome data appear once on group-header rows rather than in merged cells. The
example also combines lower- and upper-bound clipping, no-effect lines in both
panels plus an additional target line in the adjusted panel only, direction
labels, summary diamonds, and bottom legends. Synthetic demonstration data.
[View the exact code and download the XLSX or CSV input](https://xuxu-wei.github.io/forestploter/en/gallery/13_comprehensive_showcase.html).*

## Highlights

- Read one auditable long-table contract from XLSX or CSV, or pass a compatible
  `pandas.DataFrame` directly.
- Express conventional hierarchy with group-header rows and indented children,
  keeping shared values on the header row.
- Preserve supported vertical XLSX merges when a specialized centered multirow
  display is needed.
- Align single or multiple series across one or more CI columns with explicit
  `_plot_row`, `_series`, and `_ci_column` fields.
- Place ordinary text or numeric columns before, between, or after CI plotting
  columns; the `columns` sequence controls the final left-to-right order.
- Render summary diamonds, clipped-interval arrows, shared reference lines,
  additional target lines restricted to selected CI columns, series styles,
  configurable themes, and legends in a header or below the figure.
- Use automatic sizing and layout diagnostics to make dense tables, long text,
  Unicode labels, and PNG/SVG export easier to review.

## Installation

The current release is a public preview, so install the release candidate
explicitly:

```bash
python -m pip install --pre forestploter
```

Python 3.10 or later is required.

## Quick start

[Download the runnable case 01 workbook](https://raw.githubusercontent.com/xuxu-wei/forestploter/main/tests/data/01_single_series.xlsx),
then run:

```python
from forestploter import ForestColumn, forest, read_forest_data

df = read_forest_data("01_single_series.xlsx", sheet_name="Forest")
result = forest(
    df,
    columns=[
        ForestColumn("label", "Outcome / study", "text", 2.8),
        ForestColumn("n", "N", "numeric", 0.7, "right"),
        ForestColumn("ci", "Treatment effect", "ci", 3.3, "center"),
        ForestColumn(
            "effect_display",
            "Mean difference [95% CI]",
            "numeric",
            2.0,
            "right",
        ),
    ],
    xlim=(-1.0, 1.0),
    ticks_at=(-1.0, -0.5, 0.0, 0.5, 1.0),
    ref_line=0.0,
)
result.save("forest.png", dpi=300)
```

The `columns` sequence alone controls the rendered left-to-right order, so
ordinary display columns can appear before or after any CI plotting column
regardless of the physical XLSX/CSV header order.

## Input model at a glance

`read_forest_data()` returns `ForestData`: normalized values are available in
`df.frame`, and supported XLSX merge ranges are retained in `df.spans`. CSV
uses the same logical fields but has no merge metadata.

One source record describes one series in one target CI column with one shared
`estimate/lower/upper` triple. `_plot_row` explicitly selects the visual row.
To show one series in several CI columns, duplicate the record, keep the same
`_plot_row`, and change `_ci_column`.

See the complete [data contract](https://xuxu-wei.github.io/forestploter/en/data_contract.html)
and the [XLSX workbook template](https://raw.githubusercontent.com/xuxu-wei/forestploter/main/tests/data/forest_data_template.xlsx).

## Documentation and examples

- [English and Chinese documentation](https://xuxu-wei.github.io/forestploter/)
- [Getting started](https://xuxu-wei.github.io/forestploter/en/getting_started.html)
- [Example gallery](https://xuxu-wei.github.io/forestploter/en/gallery.html)
- [API reference](https://xuxu-wei.github.io/forestploter/en/api.html)
- [Thirteen XLSX/CSV/PNG regression examples](https://github.com/xuxu-wei/forestploter/blob/main/tests/README.md)

## Current scope and status

The `0.1` series is a quality-first public preview. Python 3.10 through 3.14
are covered by CI, with additional Windows and macOS smoke tests. Public APIs
may still evolve with documented deprecations before `1.0`.

All CI columns currently share one global linear axis configuration. Independent
per-column axes and logarithmic scales are planned; see the
[roadmap](https://github.com/xuxu-wei/forestploter/blob/main/ROADMAP.md).

## Support, contribution, and citation

- [Support](https://github.com/xuxu-wei/forestploter/blob/main/SUPPORT.md)
- [Contributing](https://github.com/xuxu-wei/forestploter/blob/main/CONTRIBUTING.md)
- [Security policy](https://github.com/xuxu-wei/forestploter/blob/main/SECURITY.md)
- [Changelog](https://github.com/xuxu-wei/forestploter/blob/main/CHANGELOG.md)
- [Citation metadata](https://github.com/xuxu-wei/forestploter/blob/main/CITATION.cff)

## Acknowledgments and development transparency

The table-oriented forest-plot workflow in this project was inspired by the R
package [`forestploter`](https://github.com/adayim/forestploter), created by
Alimu Dayimu. This repository is a separate implementation for the Python
ecosystem, with its own API and data contract. It is not an official Python
port and is not affiliated with, endorsed by, or maintained by the authors or
maintainers of the R package.

The implementation, tests, documentation, release engineering, and maintenance
workflow of this project include substantial AI-assisted contributions from
[OpenAI Codex](https://developers.openai.com/codex/). All changes and releases
are directed, reviewed, and approved by Xuxu Wei, the package author and
maintainer. OpenAI is not a project maintainer or sponsor.

## License

MIT © 2026 Xuxu Wei. See the
[license](https://github.com/xuxu-wei/forestploter/blob/main/LICENSE).

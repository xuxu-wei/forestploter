# forestploter

[![CI](https://github.com/xuxu-wei/forestploter/actions/workflows/ci.yml/badge.svg)](https://github.com/xuxu-wei/forestploter/actions/workflows/ci.yml)
[![Documentation](https://github.com/xuxu-wei/forestploter/actions/workflows/docs.yml/badge.svg)](https://xuxu-wei.github.io/forestploter/)
[![PyPI](https://img.shields.io/pypi/v/forestploter.svg)](https://pypi.org/project/forestploter/)
[![Python](https://img.shields.io/pypi/pyversions/forestploter.svg)](https://pypi.org/project/forestploter/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

`forestploter` creates auditable, table-style forest plots from XLSX or CSV
long tables. It validates the input contract, aligns text and confidence
intervals in shared row geometry, and renders with Matplotlib. It deliberately
does not calculate effect sizes, confidence intervals, or meta-analysis
statistics.

> This independent Python project is not affiliated with the R package that
> uses the same name.

[简体中文说明](README.zh-CN.md)

## Installation

```bash
python -m pip install forestploter
```

Before the first final release, install the release candidate explicitly:

```bash
python -m pip install --pre forestploter
```

Python 3.10 or later is required.

## Quick start

```python
from forestploter import ForestColumn, forest, read_forest_data

df = read_forest_data("forest_input.xlsx", sheet_name="Forest")
result = forest(
    df,
    columns=[
        ForestColumn("Outcome", "Outcome", "text", 2.5),
        ForestColumn("ci", "Treatment effect", "ci", 3.5, "center"),
        ForestColumn("Effect", "Effect [95% CI]", "numeric", 2.0, "right"),
    ],
    xlim=(0.4, 1.6),
    ref_line=1.0,
)
result.save("forest.png")
```

The `columns` sequence alone controls the rendered left-to-right order, so
ordinary text can appear before or after any CI plotting column regardless of
the physical XLSX/CSV header order.

## Data model

One source record describes one series in one target CI column with one shared
`estimate/lower/upper` triple. `_plot_row` explicitly selects the visual row.
To show one series in several CI columns, duplicate the record, keep the same
`_plot_row`, and change `_ci_column`.

XLSX is recommended when vertically merged display cells are useful. CSV uses
the same logical fields without merge metadata.

## Documentation and examples

- [English and Chinese documentation](https://xuxu-wei.github.io/forestploter/)
- [Data contract](https://xuxu-wei.github.io/forestploter/en/data_contract.html)
- [Example gallery](https://xuxu-wei.github.io/forestploter/en/gallery.html)
- [API reference](https://xuxu-wei.github.io/forestploter/en/api.html)
- [Workbook template](tests/data/forest_data_template.xlsx)
- [Twelve XLSX/CSV/PNG regression examples](tests/README.md)

## Project status

The `0.1` series is a quality-first public preview. The long-table contract is
the intended stable foundation, while public APIs may still evolve with
documented deprecations before `1.0`.

See [CONTRIBUTING.md](CONTRIBUTING.md), [SUPPORT.md](SUPPORT.md),
[SECURITY.md](SECURITY.md), and [CHANGELOG.md](CHANGELOG.md).

## License

MIT © 2026 Xuxu Wei. See [LICENSE](LICENSE).

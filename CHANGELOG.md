# Changelog

All notable changes are recorded here. Versions follow PEP 440, and public API
compatibility follows the policy described in `ROADMAP.md`.

## Unreleased

No changes yet.

## 0.1.0rc1 - 2026-08-28

### Added

- XLSX/CSV long-table input through `read_forest_data()` and `ForestData`.
- Auditable source-cell coordinates and supported vertical XLSX display-cell
  merges.
- Explicit `_plot_row` alignment across series and multiple CI columns.
- Ordinary estimate markers, summary diamonds, truncation arrows, themes,
  automatic layout, legends, and layout diagnostics.
- Header and bottom placement for series and reference-line legends.
- Twelve matched XLSX/CSV/PNG regression cases and a bilingual workbook
  template.
- English and Simplified Chinese Sphinx documentation with generated API pages,
  data-contract guidance, and an executable example gallery.

### Changed

- `forest()` accepts the long-table `ForestData` model or a compatible
  `pandas.DataFrame`.
- A clipped side uses an outward arrow without a vertical end cap; a completely
  out-of-range interval no longer draws a fabricated CI segment or point.
- `clipped_intervals` consistently counts intervals with at least one endpoint
  outside the visible axis.

### Removed

- The former wide-table arguments `est`, `lower`, `upper`, `ci_column`,
  `group_labels`, `series_layout`, and `series_text`.
- `ForestSeriesLayoutSpec` and `ForestSeriesTextSpec`.

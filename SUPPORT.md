# Support

## Where to ask

- Use a GitHub issue for reproducible defects, feature proposals, or unclear
  documentation: https://github.com/xuxu-wei/forestploter/issues
- Use the private security advisory form for vulnerabilities; see
  [SECURITY.md](SECURITY.md).

When reporting a plotting defect, include the `forestploter`, Python, pandas,
Matplotlib, and openpyxl versions; a minimal anonymized XLSX/CSV example; the
plot configuration; and the observed layout diagnostics.

## Scope

The project validates and renders statistics supplied by the caller. Support
does not cover calculating effect sizes, confidence intervals, missing-value
imputation, or meta-analysis models.

Only the latest release in the current `0.1.x` line receives routine fixes.
Compatibility support follows the Python versions declared in
`pyproject.toml` and verified by continuous integration.

# Contributing to forestploter

Thank you for helping improve `forestploter`. Contributions should preserve
the package's central guarantees: explicit row alignment, auditable data
validation, deterministic layout diagnostics, and readable static output.

## Development setup

```bash
git clone https://github.com/xuxu-wei/forestploter.git
cd forestploter
python -m venv .venv
python -m pip install --upgrade pip
python -m pip install -e ".[test,docs,dev]"
pre-commit install
```

## Required checks

```bash
ruff check .
mypy src/forestploter
python -m pytest -q
python docs/build_bilingual.py all
python -m tests.render_visual_cases --output-dir tests/.cache/review-images
python -m build
python -m twine check --strict dist/*
```

`nox` provides equivalent repeatable sessions for linting, type checking,
tests, documentation, and package construction.

## Changes to behavior or public APIs

- Add or update tests before changing rendering or validation semantics.
- Maintain complete English NumPy-style docstrings for public objects.
- Update the English guide and the Simplified Chinese gettext catalog.
- Add a changelog entry under `Unreleased`.
- For data-contract changes, update the workbook template and relevant
  XLSX/CSV/PNG example as one reviewable unit.
- Do not accept unexplained visual regressions or new `xfail` markers.

## Pull requests

Keep each pull request focused and explain the user-visible outcome, test
coverage, and any compatibility impact. Generated build directories, caches,
compiled translation files, and local environments must not be committed.

By participating, you agree to follow [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

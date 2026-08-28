# Release procedure

`forestploter` uses PEP 440 versions and publishes one source distribution and
one pure-Python wheel. `pyproject.toml` is the version source of truth.

## Prepare

1. Move completed entries from `Unreleased` into a dated release section in
   `CHANGELOG.md`.
2. Set `[project].version` in `pyproject.toml`.
3. Confirm the same version appears in the documentation build and runtime
   package metadata.
4. Run:

   ```bash
   ruff check .
   mypy src/forestploter
   python -m pytest -q
   python docs/build_bilingual.py all
   python -m build
   python -m twine check --strict dist/*
   check-wheel-contents dist/*.whl
   ```

5. Install both the wheel and an sdist-built wheel in clean environments and
   run the release smoke test.

## Tag and publish

1. Merge the reviewed release commit into `main`.
2. Create an annotated tag matching the metadata version:

   ```bash
   git tag -a v0.1.0rc1 -m "forestploter 0.1.0rc1"
   git push origin main v0.1.0rc1
   ```

3. The tag triggers `.github/workflows/release.yml`. It builds and validates
   the artifacts once, then publishes those exact files through the protected
   `pypi` environment and PyPI Trusted Publishing.
4. Create a GitHub Release from the same tag using the corresponding changelog
   section.

## Verify

Use a clean environment outside the source tree:

```bash
python -m pip install --pre forestploter==0.1.0rc1
python -c "import forestploter; print(forestploter.__version__)"
```

Also verify the PyPI description, project links, license, Python classifiers,
wheel contents, documentation version, XLSX loading, and PNG/SVG rendering.

## Recovery

Published files and versions are immutable. For a broken release, publish a
new patch or candidate version. Yank the affected version on PyPI only when it
is unsafe or unusable, document the reason, and never replace files under an
existing version number.

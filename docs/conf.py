"""Sphinx configuration for the bilingual forestploter documentation."""

from __future__ import annotations

import sys
from pathlib import Path

import tomllib

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

with (PROJECT_ROOT / "pyproject.toml").open("rb") as pyproject_file:
    release = tomllib.load(pyproject_file)["project"]["version"]

project = "forestploter"
author = "Xuxu Wei"
copyright = "2026, Xuxu Wei"
version = release

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx.ext.doctest",
    "numpydoc",
    "myst_parser",
]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}
master_doc = "index"
language = "en"
locale_dirs = ["locale"]
gettext_compact = "forestploter"
gettext_location = True
gettext_allow_fuzzy_translations = False
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "internal/**",
]

autosummary_generate = True
autodoc_member_order = "bysource"
autodoc_typehints = "description"
autodoc_typehints_format = "short"
autodoc_preserve_defaults = True
autoclass_content = "class"

# Public API pages are quality gates: malformed pandas/NumPy docstrings fail
# strict builds instead of silently producing incomplete references.
numpydoc_validate = True
numpydoc_validation_checks = {
    "GL08",
    "PR01",
    "PR02",
    "PR04",
    "PR07",
    "RT01",
    "RT03",
}
numpydoc_show_class_members = False
numpydoc_class_members_toctree = False
numpydoc_xref_param_type = False
numpydoc_xref_aliases = {
    "Axes": "matplotlib.axes.Axes",
    "DataFrame": "pandas.DataFrame",
    "Figure": "matplotlib.figure.Figure",
    "ForestData": "forestploter.ForestData",
    "ForestDataMapping": "forestploter.ForestDataMapping",
    "Mapping": "collections.abc.Mapping",
    "Path": "pathlib.Path",
    "Sequence": "collections.abc.Sequence",
}

doctest_test_doctest_blocks = "default"
doctest_global_setup = """
import matplotlib
matplotlib.use("Agg", force=True)
"""

html_theme = "sphinx_rtd_theme"
html_title = f"forestploter {release} documentation"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_js_files = ["language-switch.js"]
html_theme_options = {
    "collapse_navigation": False,
    "navigation_depth": 3,
    "sticky_navigation": True,
    "style_external_links": True,
}
html_show_sourcelink = True
html_show_sphinx = True

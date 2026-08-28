"""Regression tests for the bilingual user documentation and public API."""

from __future__ import annotations

import ast
import inspect
import re
from pathlib import Path

import forestploter
from forestploter.gallery_cases import GALLERY_FUNCTIONS
from tests.visual_cases import (
    CASE_CSV_FILES,
    CASE_DATA_FILES,
    artifact_name_for_case,
)

PROJECT_DIR = Path(__file__).resolve().parents[1]
DOCS_DIR = PROJECT_DIR / "docs"
PUBLIC_RST = (
    DOCS_DIR / "index.rst",
    DOCS_DIR / "getting_started.rst",
    DOCS_DIR / "data_contract.rst",
    DOCS_DIR / "gallery.rst",
    DOCS_DIR / "api.rst",
    *sorted((DOCS_DIR / "gallery").glob("*.rst")),
)
EXPECTED_API_ORDER = (
    "read_forest_data",
    "forest",
    "ForestPlotResult",
    "ForestData",
    "ForestDataMapping",
    "ForestCellSpan",
    "ForestColumn",
    "ForestSeriesStyle",
    "ForestTheme",
    "ForestTableLayoutSpec",
    "ForestLegendSpec",
    "ForestReferenceLegendSpec",
    "ForestLayoutDiagnostics",
    "ColumnGeometry",
    "compute_column_geometry",
)


def test_api_reference_lists_every_public_export_once_in_user_workflow_order() -> None:
    api_source = (DOCS_DIR / "api.rst").read_text(encoding="utf-8")
    documented = re.findall(
        r"^\s{3,}(?:forestploter\.)?([A-Za-z_]\w*)\s*$",
        api_source,
        re.MULTILINE,
    )
    assert tuple(documented) == EXPECTED_API_ORDER
    assert len(documented) == len(set(documented))
    assert set(documented) == set(forestploter.__all__)


def test_every_public_export_has_an_english_docstring() -> None:
    missing = []
    chinese = []
    for name in forestploter.__all__:
        doc = inspect.getdoc(getattr(forestploter, name, None)) or ""
        if not doc:
            missing.append(name)
        if re.search(r"[\u3400-\u9fff]", doc):
            chinese.append(name)
    assert missing == []
    assert chinese == []


def test_public_rst_is_english_single_source_and_internal_pages_are_excluded() -> None:
    assert len(PUBLIC_RST) == 17
    for source in PUBLIC_RST:
        text = source.read_text(encoding="utf-8")
        assert not re.search(r"[\u3400-\u9fff]", text), source
    assert {item.name for item in (DOCS_DIR / "internal").glob("*.rst")} == {
        "acceptance.rst",
        "development.rst",
        "migration.rst",
    }
    index = (DOCS_DIR / "index.rst").read_text(encoding="utf-8")
    assert all(f"   {name}\n" not in index for name in ("acceptance", "development", "migration"))
    conf = (DOCS_DIR / "conf.py").read_text(encoding="utf-8")
    assert '"internal/**"' in conf


def test_gallery_has_one_detail_page_with_assets_and_shared_code_per_case() -> None:
    detail_pages = sorted((DOCS_DIR / "gallery").glob("*.rst"))
    assert len(detail_pages) == len(CASE_DATA_FILES) == 12
    overview = (DOCS_DIR / "gallery.rst").read_text(encoding="utf-8")
    for (case_name, data_name), page in zip(CASE_DATA_FILES.items(), detail_pages, strict=True):
        csv_name = CASE_CSV_FILES[case_name]
        image_name = artifact_name_for_case(case_name)
        source = page.read_text(encoding="utf-8")
        function_name = GALLERY_FUNCTIONS[case_name].__name__
        assert page.stem in overview
        assert data_name in source
        assert csv_name in source
        assert image_name in source
        assert "df = read_forest_data" in source
        assert f":pyobject: {function_name}" in source
        assert "../../src/forestploter/gallery_cases.py" in source


def test_xlsx_contract_explains_types_orders_rows_merges_and_alignment() -> None:
    reader_doc = inspect.getdoc(forestploter.read_forest_data) or ""
    forest_doc = inspect.getdoc(forestploter.forest) or ""
    contract = (DOCS_DIR / "data_contract.rst").read_text(encoding="utf-8")
    for text in (reader_doc, forest_doc, contract):
        assert "_plot_row" in text
        assert "_ci_column" in text
        assert "merge" in text.lower()
        assert "columns" in text
    for phrase in (
        "Two independent column orders",
        "Field dictionary",
        "Row-type recipes",
        "Complete single-CI example",
        "Multiple series: one visual row per series",
        "Multiple CI columns: duplicate records, share a visual row",
        "Multiple series, multiple CI columns, and trailing text",
        "Accepted versus recommended input",
        "3*k",
    ):
        assert phrase in contract


def test_language_switch_and_bilingual_build_configuration_are_present() -> None:
    conf = (DOCS_DIR / "conf.py").read_text(encoding="utf-8")
    switch = (DOCS_DIR / "_static" / "language-switch.js").read_text(encoding="utf-8")
    build = (DOCS_DIR / "build_bilingual.py").read_text(encoding="utf-8")
    assert 'language = "en"' in conf
    assert 'gettext_compact = "forestploter"' in conf
    assert "zh_CN" in switch and "/en/" in switch
    assert 'LANGUAGES = ("en", "zh_CN")' in build
    assert 'content="0; url=en/index.html"' in build


def _po_translation(block: str) -> str:
    lines = block.splitlines()
    for index, line in enumerate(lines):
        if not line.startswith("msgstr "):
            continue
        parts = [ast.literal_eval(line.removeprefix("msgstr "))]
        for continuation in lines[index + 1 :]:
            if not continuation.startswith('"'):
                break
            parts.append(ast.literal_eval(continuation))
        return "".join(parts)
    return ""


def test_chinese_catalog_has_no_empty_or_fuzzy_messages() -> None:
    path = DOCS_DIR / "locale" / "zh_CN" / "LC_MESSAGES" / "forestploter.po"
    assert path.exists()
    blocks = path.read_text(encoding="utf-8").split("\n\n")
    checked = 0
    for block in blocks:
        if "msgid " not in block or "#:" not in block:
            continue
        checked += 1
        assert "fuzzy" not in block
        assert _po_translation(block), block[:160]
    assert checked >= 700


def test_documentation_css_defines_narrow_screen_fallbacks() -> None:
    css = (DOCS_DIR / "_static" / "custom.css").read_text(encoding="utf-8")
    assert "@media screen and (max-width: 768px)" in css
    assert "dl.field-list" in css and "display: block" in css
    assert "table.docutils" in css and "overflow-x: auto" in css
    assert ".rst-content pre" in css and "white-space: pre" in css
    assert ".forest-language-switch" in css

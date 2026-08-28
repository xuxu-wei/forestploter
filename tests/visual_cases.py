"""Repeatable XLSX/CSV visual-regression cases."""

from __future__ import annotations

import sys
from collections.abc import Callable
from pathlib import Path

import matplotlib
import pandas as pd
from matplotlib import font_manager

PROJECT_DIR = Path(__file__).resolve().parents[1]
SOURCE_DIR = PROJECT_DIR / "src"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from forestploter import ForestData, ForestPlotResult, read_forest_data  # noqa: E402
from forestploter.gallery_cases import GALLERY_FUNCTIONS  # noqa: E402

DATA_DIR = Path(__file__).resolve().parent / "data"
ARTIFACT_DIR = Path(__file__).resolve().parent / "artifacts"

CASE_DATA_FILES = {
    "single_series": "01_single_series.xlsx",
    "multi_series": "02_multi_series.xlsx",
    "dual_ci_columns": "03_dual_ci_columns.xlsx",
    "clipping_stress": "04_clipping_stress.xlsx",
    "long_layout": "05_long_layout.xlsx",
    "auto_scale_mixed_effects": "06_auto_scale_mixed_effects.xlsx",
    "four_series_dense": "07_four_series_dense.xlsx",
    "two_by_two_ci_columns": "08_two_by_two_ci_columns.xlsx",
    "deep_hierarchy_many_rows": "09_deep_hierarchy_many_rows.xlsx",
    "unicode_custom_theme": "10_unicode_custom_theme.xlsx",
    "boundary_precision": "11_boundary_precision.xlsx",
    "multi_series_ci_text_rows": "12_multi_series_ci_text_rows.xlsx",
}
CASE_CSV_FILES = {
    case_name: Path(file_name).with_suffix(".csv").name
    for case_name, file_name in CASE_DATA_FILES.items()
}


def configure_test_font() -> str | None:
    """Prefer a local font with English and Chinese glyph coverage on Windows."""

    candidates = (
        Path("C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/simhei.ttf"),
        Path("C:/Windows/Fonts/arialuni.ttf"),
    )
    for candidate in candidates:
        if candidate.exists():
            font_manager.fontManager.addfont(candidate)
            family = font_manager.FontProperties(fname=candidate).get_name()
            matplotlib.rcParams["font.family"] = family
            matplotlib.rcParams["axes.unicode_minus"] = False
            return family
    return None


CONFIGURED_TEST_FONT = configure_test_font()


def load_case_data(case_name: str, *, source_format: str = "xlsx") -> ForestData:
    """Read an XLSX primary fixture or its CSV companion."""

    if source_format not in {"xlsx", "csv"}:
        raise ValueError("source_format must be 'xlsx' or 'csv'.")
    files = CASE_DATA_FILES if source_format == "xlsx" else CASE_CSV_FILES
    try:
        file_name = files[case_name]
    except KeyError as error:
        raise ValueError(f"Unknown visual case: {case_name}") from error
    return read_forest_data(DATA_DIR / file_name)


def artifact_name_for_case(case_name: str) -> str:
    """Return the PNG name that exactly matches the data-file stem."""

    try:
        file_name = CASE_DATA_FILES[case_name]
    except KeyError as error:
        raise ValueError(f"Unknown visual case: {case_name}") from error
    return Path(file_name).with_suffix(".png").name


ForestInput = ForestData | pd.DataFrame
CASE_BUILDERS: dict[str, Callable[[ForestInput], ForestPlotResult]] = GALLERY_FUNCTIONS


def build_case(case_name: str, data: ForestInput | None = None) -> ForestPlotResult:
    """Build a named visual case from supplied or bundled data."""

    try:
        builder = CASE_BUILDERS[case_name]
    except KeyError as error:
        raise ValueError(f"Unknown visual case: {case_name}") from error
    df = load_case_data(case_name) if data is None else data
    return builder(df)


__all__ = [
    "ARTIFACT_DIR",
    "CASE_BUILDERS",
    "CASE_CSV_FILES",
    "CASE_DATA_FILES",
    "CONFIGURED_TEST_FONT",
    "DATA_DIR",
    "artifact_name_for_case",
    "build_case",
    "load_case_data",
]

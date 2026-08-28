"""XLSX/CSV long-table interface for table-style forest plots.

The package namespace exposes :func:`forest`, :class:`ForestPlotResult`, the
file reader, and column, series, legend, layout, and theme configuration.
forestploter validates input and renders tables and graphics; it does not
calculate effect sizes, confidence intervals, or meta-analysis statistics.
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("forestploter")
except PackageNotFoundError:  # pragma: no cover - source tree without installation
    __version__ = "0+unknown"

from .core import ForestPlotResult, forest
from .data import ForestCellSpan, ForestData, ForestDataMapping, read_forest_data
from .layout import (
    ColumnGeometry,
    ForestColumn,
    ForestLayoutDiagnostics,
    ForestLegendSpec,
    ForestReferenceLegendSpec,
    ForestSeriesStyle,
    ForestTableLayoutSpec,
    compute_column_geometry,
)
from .theme import ForestTheme

del PackageNotFoundError, version

__all__ = [
    "ColumnGeometry",
    "ForestCellSpan",
    "ForestColumn",
    "ForestData",
    "ForestDataMapping",
    "ForestLayoutDiagnostics",
    "ForestLegendSpec",
    "ForestPlotResult",
    "ForestReferenceLegendSpec",
    "ForestSeriesStyle",
    "ForestTableLayoutSpec",
    "ForestTheme",
    "compute_column_geometry",
    "forest",
    "read_forest_data",
]

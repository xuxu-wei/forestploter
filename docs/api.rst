API reference
=============

The 15 public objects are organized below in the order most users encounter
them. ``autosummary`` regenerates the detail pages from current signatures and
pandas/NumPy-style docstrings on every documentation build.

.. currentmodule:: forestploter

Core workflow
-------------

Read data, render a plot, and work with the returned figure and diagnostics.

.. autosummary::
   :toctree: api/generated
   :nosignatures:

   read_forest_data
   forest
   ForestPlotResult

Data model
----------

Inspect normalized values, source-cell locations, field mappings, and XLSX
merge spans.

.. autosummary::
   :toctree: api/generated
   :nosignatures:

   ForestData
   ForestDataMapping
   ForestCellSpan

Configuration
-------------

Define output columns, series styles, themes, automatic table layout, and
series/reference legends.

.. autosummary::
   :toctree: api/generated
   :nosignatures:

   ForestColumn
   ForestSeriesStyle
   ForestTheme
   ForestTableLayoutSpec
   ForestLegendSpec
   ForestReferenceLegendSpec

Diagnostics and geometry
------------------------

Audit visual rows, observation coordinates, merged spans, legend bounds, and
normalized column boundaries.

.. autosummary::
   :toctree: api/generated
   :nosignatures:

   ForestLayoutDiagnostics
   ColumnGeometry
   compute_column_geometry

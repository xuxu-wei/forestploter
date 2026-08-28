Example gallery
===============

Each case has one XLSX primary file, one semantically equivalent CSV companion,
one PNG with the same filename stem, and the exact plotting function used by
the renderer and regression tests. On every detail page, ``df`` means the
:class:`forestploter.ForestData` returned by
:func:`forestploter.read_forest_data`.

:download:`Download the general XLSX long-table template <../tests/data/forest_data_template.xlsx>`

.. container:: gallery-index

   :doc:`gallery/01_single_series`
      Display text on both sides of one CI column, group rows, summary diamonds,
      reference and ideal lines.

   :doc:`gallery/02_multi_series`
      Three series in one CI column with one explicit visual row per series.

   :doc:`gallery/03_dual_ci_columns`
      One series aligned across two follow-up CI columns.

   :doc:`gallery/04_clipping_stress`
      Single-sided, two-sided, and fully off-scale clipping behavior.

   :doc:`gallery/05_long_layout`
      Long headers, long cells, multilingual content, wrapping, and auto width.

   :doc:`gallery/06_auto_scale_mixed_effects`
      Automatic limits and ticks across heterogeneous effects.

   :doc:`gallery/07_four_series_dense`
      Four series, four markers, summary rows, and a bottom legend.

   :doc:`gallery/08_two_by_two_ci_columns`
      Two series aligned across two CI columns, followed by a text column whose
      header contains the legend.

   :doc:`gallery/09_deep_hierarchy_many_rows`
      Thirty visual rows, two indentation levels, subtotals, and spacers.

   :doc:`gallery/10_unicode_custom_theme`
      Chinese, English, Greek, mathematical symbols, and a custom theme.

   :doc:`gallery/11_boundary_precision`
      Exact limits, zero-width intervals, narrow intervals, and tiny overflows.

   :doc:`gallery/12_multi_series_ci_text_rows`
      Three independent CI-text rows placed after the CI column and aligned
      one-to-one with the corresponding series graphics.

   :doc:`gallery/13_comprehensive_showcase`
      Three series aligned across crude and adjusted CI columns with paired
      value-only CI text, compact outcome headers and indented series children,
      two-sided clipping, shared no-effect lines, an additional target line in
      one panel, direction labels, and bottom legends. This case uses no merges.

.. toctree::
   :hidden:

   gallery/01_single_series
   gallery/02_multi_series
   gallery/03_dual_ci_columns
   gallery/04_clipping_stress
   gallery/05_long_layout
   gallery/06_auto_scale_mixed_effects
   gallery/07_four_series_dense
   gallery/08_two_by_two_ci_columns
   gallery/09_deep_hierarchy_many_rows
   gallery/10_unicode_custom_theme
   gallery/11_boundary_precision
   gallery/12_multi_series_ci_text_rows
   gallery/13_comprehensive_showcase

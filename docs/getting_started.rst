Getting started
===============

Install
-------

Install the current release from PyPI:

.. code-block:: console

   $ python -m pip install forestploter

For a release candidate, allow prereleases explicitly with
``python -m pip install --pre forestploter``. Contributors can instead install
an editable checkout with ``python -m pip install -e .``.

XLSX is the recommended input format. Begin with the
:download:`long-table workbook template <../tests/data/forest_data_template.xlsx>`.
Its first worksheet is ``Forest`` and its ``README`` worksheet contains an
English/Chinese field dictionary, entry rules, and validated drop-down fields.

Read a file
-----------

.. code-block:: python

   from forestploter import read_forest_data

   df = read_forest_data("forest_input.xlsx", sheet_name="Forest")

Despite the familiar variable name, ``df`` is a :class:`forestploter.ForestData`
object. Its ``frame`` attribute is the underlying DataFrame, while ``spans``
contains supported XLSX merges. CSV uses the same fields but has no merge
metadata:

.. code-block:: python

   df = read_forest_data("forest_input.csv")

Minimal long table
------------------

Each source record contains at most one ``estimate/lower/upper`` triple.
``_plot_row`` determines the visual row, ``_series`` selects the series style,
and ``_ci_column`` selects the target CI plotting column.

The physical field order below follows the recommended entry layout: visible
fields before the first CI, the statistical triple, visible fields after the
CI, and finally the six control fields. The rendered order is controlled only
by ``columns``.

.. doctest:: getting-started

   >>> import pandas as pd
   >>> from forestploter import ForestColumn, forest
   >>> df = pd.DataFrame(
   ...     {
   ...         "study": ["Study A", "Study B", "Pooled result"],
   ...         "estimate": [0.18, -0.06, 0.07],
   ...         "lower": [-0.04, -0.31, -0.08],
   ...         "upper": [0.40, 0.19, 0.22],
   ...         "effect_text": [
   ...             "0.18 [-0.04, 0.40]",
   ...             "-0.06 [-0.31, 0.19]",
   ...             "0.07 [-0.08, 0.22]",
   ...         ],
   ...         "_plot_row": ["study-a", "study-b", "pooled"],
   ...         "_series": ["Treatment", "Treatment", "Treatment"],
   ...         "_ci_column": ["ci", "ci", "ci"],
   ...         "_row_type": ["estimate", "estimate", "summary"],
   ...         "_indent": [0, 0, 0],
   ...         "_is_summary": [False, False, True],
   ...     }
   ... )
   >>> columns = (
   ...     ForestColumn("study", "Study", "text", 2.0),
   ...     ForestColumn("ci", "Treatment effect", "ci", 3.0, "center"),
   ...     ForestColumn("effect_text", "Effect [95% CI]", "numeric", 1.8, "right"),
   ... )
   >>> result = forest(
   ...     df,
   ...     columns=columns,
   ...     xlim=(-0.5, 0.5),
   ...     ticks_at=(-0.5, -0.25, 0, 0.25, 0.5),
   ...     ref_line=0,
   ...     arrow_lab=("Favours treatment", "Favours control"),
   ...     title="Treatment effect",
   ... )
   >>> result.row_centers
   (2.5, 1.5, 0.5)
   >>> result.clipped_intervals
   0
   >>> result.layout_diagnostics.plot_row_ids
   ('study-a', 'study-b', 'pooled')

Table borders
-------------

The default is a three-rule table: one rule above the column headers, one below
them, and one at the table bottom. Data rows have no internal separators or
side borders. Pass ``theme=ForestTheme(show_table_border=True)`` to
:func:`forestploter.forest` to add those borders. Set ``show_vertical_grid=True``
on the same theme when vertical column separators are also needed.

Column-header height automatically adapts to the rendered text and header
legends, including multiline text, mathematical expressions, and larger
fonts. Only the header grows; body rows keep their spacing. This also works
with ``auto_width=False`` or ``auto_wrap_headers=False``. Use
``table_layout=ForestTableLayoutSpec(header_padding_pt=4)`` to set the minimum
top and bottom padding in points. Explicit newline characters remain useful
for choosing where a heading breaks.

Save the result
---------------

.. code-block:: python

   result.save("outputs/treatment_effect.png", dpi=300)
   result.save("outputs/treatment_effect.svg")

Close the Figure after batch rendering:

.. doctest:: getting-started

   >>> import matplotlib.pyplot as plt
   >>> plt.close(result.figure)

Next steps
----------

* Read :doc:`data_contract` for XLSX merges, row recipes, and multi-CI
  alignment.
* Browse :doc:`gallery` for thirteen downloadable XLSX/CSV/PNG cases with the
  exact plotting code.
* Consult :func:`forestploter.read_forest_data` and
  :func:`forestploter.forest` for API details.

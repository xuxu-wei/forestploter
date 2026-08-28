Data contract
=============

``forestploter`` does not calculate effect sizes, confidence intervals, or
meta-analysis models. Store already calculated values in the input file; the
package reads, validates, lays out, and renders them.

Two independent column orders
-----------------------------

Do not confuse the plot order with the physical file order:

``columns`` sequence
   The only authority for the final left-to-right image order. A CI plotting
   column may be first, last, or between display columns. Text can therefore be
   appended after a CI without changing the reader or the source-field names.

XLSX/CSV header order
   An entry-time convention for human readability. It never controls the plot
   layout. The recommended order is:

   #. display fields that appear before the first CI;
   #. the shared ``estimate``, ``lower``, ``upper`` triple, representing the
      first CI position in a physical file;
   #. display fields that appear after the first CI;
   #. the six controls, always last and in this exact order:
      ``_plot_row``, ``_series``, ``_ci_column``, ``_row_type``, ``_indent``,
      ``_is_summary``.

For example, this file order supports a rendered “study → CI → effect text”
layout:

.. code-block:: text

   study, estimate, lower, upper, effect_text,
   _plot_row, _series, _ci_column, _row_type, _indent, _is_summary

The matching plot order is explicit:

.. code-block:: python

   columns = (
       ForestColumn("study", "Study", "text", 2.0),
       ForestColumn("ci", "Treatment effect", "ci", 3.0, "center"),
       ForestColumn("effect_text", "Effect [95% CI]", "numeric", 2.0, "right"),
   )

Field dictionary
----------------

One source record means “one series in one target CI column”. The following
rules use the default :class:`forestploter.ForestDataMapping` names.

.. list-table::
   :header-rows: 1
   :widths: 16 17 24 43

   * - Field
     - Accepted type
     - Allowed values
     - Required and blank rules
   * - display fields
     - Any scalar suitable for ``str()``
     - Text, number, boolean, date-like value, or blank
     - Required only when referenced by a ``text`` or ``numeric``
       :class:`forestploter.ForestColumn`. All nonblank values within one
       ``_plot_row`` must agree. Blanks are not forward-filled.
   * - ``estimate``
     - Finite number
     - Any finite numeric value
     - On ``estimate`` and ``summary`` records, the three statistics must be
       all present or all blank. A fully blank triple explicitly skips drawing.
   * - ``lower``
     - Finite number
     - ``lower <= estimate``
     - Uses the same all-present/all-blank rule as ``estimate``.
   * - ``upper``
     - Finite number
     - ``estimate <= upper``
     - Uses the same all-present/all-blank rule as ``estimate``.
   * - ``_plot_row``
     - Nonblank hashable scalar
     - Any stable identifier
     - Required on every record. Equal values share exactly one y coordinate,
       and all records for one value must be contiguous. Stable strings are
       recommended.
   * - ``_series``
     - String-like scalar
     - A key used by ``series_styles``
     - Required and nonblank for ``estimate`` and ``summary``; blank for
       ``header`` and ``spacer``. Records sharing ``_plot_row`` must agree.
   * - ``_ci_column``
     - String-like scalar
     - The ``key`` of a ``ForestColumn(role="ci")``
     - Required and nonblank for ``estimate`` and ``summary``; blank for
       ``header`` and ``spacer``. A ``(_plot_row, _ci_column)`` target may
       occur only once.
   * - ``_row_type``
     - String enum
     - ``header``, ``estimate``, ``summary``, ``spacer``
     - Required on every record and identical within one ``_plot_row``.
   * - ``_indent``
     - Finite non-negative number
     - ``>= 0``
     - Required on every record and identical within one ``_plot_row``.
       Integer levels are recommended, although decimals are currently
       accepted.
   * - ``_is_summary``
     - Actual boolean
     - ``TRUE``/``FALSE`` in XLSX; ``True``/``False`` in CSV
     - Required on every record and identical within one ``_plot_row``. It
       controls marker shape only. Strings and numeric ``0``/``1`` are rejected.

``text`` and ``numeric`` display roles currently both render text; the role
communicates intent and default alignment rather than coercing source values.

Row-type recipes
----------------

.. list-table::
   :header-rows: 1
   :widths: 16 18 18 22 13 13

   * - ``_row_type``
     - ``_series``
     - ``_ci_column``
     - Statistics
     - ``_indent``
     - ``_is_summary``
   * - ``header``
     - blank
     - blank
     - all blank
     - usually 0
     - ``FALSE``
   * - ``estimate``
     - required
     - required
     - all present, or all blank to skip
     - >= 0
     - normally ``FALSE``
   * - ``summary``
     - required
     - required
     - all present, or all blank to skip
     - usually 0
     - normally ``TRUE``
   * - ``spacer``
     - blank
     - blank
     - all blank
     - usually 0
     - ``FALSE``

``_row_type`` determines row semantics, while ``_is_summary`` determines only
the marker form. They are intentionally separate fields.

Complete single-CI example
--------------------------

The displayed effect text follows the CI in the image even though the CI
itself has no physical source field.

.. list-table::
   :header-rows: 1

   * - study
     - estimate
     - lower
     - upper
     - effect_text
     - ``_plot_row``
     - ``_series``
     - ``_ci_column``
     - ``_row_type``
     - ``_indent``
     - ``_is_summary``
   * - Study A
     - 0.72
     - 0.58
     - 0.90
     - 0.72 [0.58, 0.90]
     - os-a
     - Treatment
     - ci
     - estimate
     - 0
     - FALSE
   * - Pooled result
     - 0.79
     - 0.71
     - 0.88
     - 0.79 [0.71, 0.88]
     - pooled
     - Treatment
     - ci
     - summary
     - 0
     - TRUE

Multiple series: header row and indented children
-------------------------------------------------

The recommended structure uses one ``header`` record for shared outcome-level
data, followed by one indented visual row per series. Put the outcome,
participant count, and other shared values on the header. Put the series label
and its CI text on the child row with ``_indent=1``. This conventional hierarchy
uses no merges and has the same structure in XLSX and CSV.

.. list-table::
   :header-rows: 1

   * - label
     - participants
     - estimate
     - lower
     - upper
     - series_ci_text
     - ``_plot_row``
     - ``_series``
     - ``_ci_column``
     - ``_row_type``
     - ``_indent``
     - ``_is_summary``
   * - Overall survival
     - 1240
     -
     -
     -
     -
     - os-header
     -
     -
     - header
     - 0
     - FALSE
   * - Series A
     -
     - 0.72
     - 0.58
     - 0.90
     - 0.72 [0.58, 0.90]
     - os-a
     - Series A
     - ci
     - estimate
     - 1
     - FALSE
   * - Series B
     -
     - 0.81
     - 0.67
     - 0.98
     - 0.81 [0.67, 0.98]
     - os-b
     - Series B
     - ci
     - estimate
     - 1
     - FALSE
   * - Series C
     -
     - 0.95
     - 0.79
     - 1.14
     - 0.95 [0.79, 1.14]
     - os-c
     - Series C
     - ci
     - estimate
     - 1
     - FALSE

Do not create ``estimate_a/lower_a/upper_a`` and similar ``3*k`` wide-form
fields. Do not combine several series' CI text into one multiline cell.
Supported vertical XLSX merges are still accepted for specialized layouts; see
`XLSX merge rules`_. They are not needed to express this parent-child hierarchy.

Multiple CI columns: duplicate records, share a visual row
----------------------------------------------------------

One series shown in crude and adjusted CI columns uses two records. The records
share ``_plot_row`` and ``_series`` but have different ``_ci_column`` values.
They therefore share the exact same y coordinate.

For a display value shared by those two source records, either fill it once and
leave the other cell blank, or repeat the same value in both records. The
renderer aggregates non-conflicting values within that ``_plot_row``; it does
not forward-fill source data.

.. list-table::
   :header-rows: 1

   * - outcome
     - estimate
     - lower
     - upper
     - ``_plot_row``
     - ``_series``
     - ``_ci_column``
     - ``_row_type``
     - ``_indent``
     - ``_is_summary``
   * - Readmission
     - 0.74
     - 0.63
     - 0.87
     - readmit-a
     - Cohort A
     - ci_crude
     - estimate
     - 0
     - FALSE
   * - Readmission
     - 0.79
     - 0.67
     - 0.93
     - readmit-a
     - Cohort A
     - ci_adjusted
     - estimate
     - 0
     - FALSE

Multiple series, multiple CI columns, and trailing text
-------------------------------------------------------

The following table is a specialized merged-layout example, not the recommended
way to express a routine parent-child hierarchy. Use it only when a display
value specifically needs to be centered across several source records.

Repeat the two-record pattern for each series, giving each series a different
``_plot_row``. A trailing display field such as ``cohort`` may be merged over
the two records for that visual row. It is rendered after both CI columns when
listed last in ``columns``:

.. code-block:: python

   columns = (
       ForestColumn("outcome", "Outcome", "text", 2.4),
       ForestColumn("ci_crude", "Crude", "ci", 3.4, "center"),
       ForestColumn("ci_adjusted", "Adjusted", "ci", 3.4, "center"),
       ForestColumn("cohort", "Cohort", "text", 1.1),
   )

.. list-table::
   :header-rows: 1

   * - outcome
     - estimate
     - lower
     - upper
     - cohort
     - ``_plot_row``
     - ``_series``
     - ``_ci_column``
   * - Readmission (merge 4 rows)
     - 0.74
     - 0.63
     - 0.87
     - Cohort A (merge 2 rows)
     - readmit-a
     - Cohort A
     - ci_crude
   * -
     - 0.79
     - 0.67
     - 0.93
     -
     - readmit-a
     - Cohort A
     - ci_adjusted
   * -
     - 0.86
     - 0.73
     - 1.01
     - Cohort B (merge 2 rows)
     - readmit-b
     - Cohort B
     - ci_crude
   * -
     - 0.89
     - 0.75
     - 1.05
     -
     - readmit-b
     - Cohort B
     - ci_adjusted

This structure prevents independent per-CI series offsets: alignment is stated
directly by ``(_plot_row, _series)`` in the data.

XLSX merge rules
----------------

:func:`forestploter.read_forest_data` accepts a merge only when it is:

* below the header;
* vertical and confined to one display-field column;
* at least two physical records tall; and
* aligned with complete ``_plot_row`` record groups.

Merges in statistics or controls, horizontal merges, rectangles, header
crossings, and partial visual-row groups raise an error. Merged text is drawn
once at the span center, with internal horizontal rules suppressed in that
column.

CSV compatibility
-----------------

CSV uses exactly the same fields and record ordering. It cannot store merge
ranges, so repeat shared display values explicitly. Normalized plot rows,
observations, clipping counts, and y positions should remain equivalent between
the two formats.

Accepted versus recommended input
---------------------------------

The validator intentionally accepts more than the template recommends:

.. list-table::
   :header-rows: 1
   :widths: 31 34 35

   * - Topic
     - Currently accepted
     - Recommended for maintainability
   * - Physical field order
     - Any unique header order
     - Display-before-CI, triple, trailing display, then six controls
   * - ``_plot_row`` type
     - Any nonblank hashable scalar
     - Stable descriptive string
   * - ``_indent``
     - Any finite number >= 0
     - Small non-negative integer
   * - Parent-child hierarchy
     - Header rows, indentation, and supported vertical display merges
     - Shared values on a header row; child labels on rows with ``_indent=1``
   * - Merge usage
     - Supported single-column vertical display merges
     - Optional for specialized centered displays, not routine hierarchy
   * - Display value type
     - Any scalar with a useful string representation
     - Text for ``text``; numbers or formatted effect text for ``numeric``
   * - Estimate-row triple
     - All present or all blank
     - All present unless intentionally suppressing that interval
   * - File style
     - Styling is ignored
     - Use the supplied template colors, widths, and validation only as data
       entry aids

Clipping semantics
------------------

An arrow replaces the vertical cap on every clipped side. An interval spanning
both limits shows its visible line and two arrows, with no endpoint caps. An
interval entirely left or right of the range shows only the nearest outward
arrow and no line, cap, or fabricated marker. ``clipped_intervals`` counts
affected intervals, so each interval contributes at most one.

forestploter documentation
==========================

.. rubric:: Auditable forest plots from XLSX/CSV long tables

``forestploter`` places table text, statistical estimates, and confidence
intervals in one shared row-and-column geometry. XLSX preserves values, record
order, and supported vertical merges; CSV uses the same logical fields. You
calculate the statistics, while the package reads, validates, lays out, and
renders the figure.

Current capabilities
--------------------

* recommended XLSX input and compatible UTF-8 CSV input;
* single or multiple series and one or more CI columns;
* explicit cross-column alignment through ``_plot_row``;
* ordinary estimates, summary diamonds, clipping arrows, guide lines, and
  legends;
* borderless tables by default with optional outlines, row separators, and
  vertical column separators;
* independently editable per-series CI text aligned with each plotted row;
* vertically merged display cells with centered text and suppressed internal
  rules;
* header wrapping, automatic width growth, hierarchical indentation, themes,
  and layout diagnostics;
* PNG, SVG, and other Matplotlib-supported static exports.

Start with :doc:`getting_started`, use :doc:`data_contract` when preparing
non-trivial workbooks, browse the :doc:`gallery`, and consult :doc:`api` for
complete signatures and parameter definitions.

.. note::

   Version |release| is a quality-first public preview. All CI columns
   currently share one global linear coordinate configuration.

.. toctree::
   :maxdepth: 2
   :caption: User guide

   getting_started
   data_contract
   gallery

.. toctree::
   :maxdepth: 2
   :caption: Reference

   api

Indexes
-------

* :ref:`genindex`
* :ref:`search`

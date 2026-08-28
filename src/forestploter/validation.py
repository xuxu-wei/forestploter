"""Validate and normalize the forest-plot long-table contract.

Validation checks structure, types, and numeric relationships only. It does
not calculate effect sizes, confidence intervals, or meta-analysis statistics.
The renderer consumes normalized objects from this module and remains
independent of XLSX/CSV reading details.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from .data import ForestData, ForestDataMapping
from .layout import ForestColumn

VALID_ROW_TYPES = frozenset({"header", "summary", "estimate", "spacer"})
"""Row-semantic names supported by the renderer."""


@dataclass(frozen=True)
class _NormalizedObservation:
    record_index: int
    plot_row: Any
    series: str
    ci_column: str
    estimate: float | None
    lower: float | None
    upper: float | None
    row_type: str
    is_summary: bool


@dataclass(frozen=True)
class _NormalizedPlotRow:
    plot_row: Any
    record_indices: tuple[int, ...]
    row_type: str
    indent: float
    is_summary: bool
    series: str | None
    display_values: tuple[tuple[str, Any], ...]

    def value(self, column_key: str) -> Any:
        return dict(self.display_values).get(column_key)


@dataclass(frozen=True)
class _NormalizedSpan:
    column_key: str
    start_record: int
    end_record: int
    start_row: int
    end_row: int
    value: Any


@dataclass(frozen=True)
class _NormalizedForestTable:
    frame: pd.DataFrame
    mapping: ForestDataMapping
    plot_rows: tuple[_NormalizedPlotRow, ...]
    observations: tuple[_NormalizedObservation, ...]
    spans: tuple[_NormalizedSpan, ...]
    series_order: tuple[str, ...]
    ci_columns: tuple[str, ...]


def _is_blank(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    try:
        result = pd.isna(value)
    except (TypeError, ValueError):
        return False
    return bool(result) if isinstance(result, (bool, np.bool_)) else False


def _display_value(values: list[Any], *, column_key: str, plot_row: Any) -> Any:
    nonblank = [value for value in values if not _is_blank(value)]
    if not nonblank:
        return None
    first = nonblank[0]
    for value in nonblank[1:]:
        try:
            equal = bool(value == first)
        except (TypeError, ValueError):
            equal = False
        if not equal:
            raise ValueError(
                f"Display field {column_key!r} has conflicting values within plot row {plot_row!r}."
            )
    return first


def _coerce_number(value: Any, *, field: str, record: int) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(
            f"Forest field {field!r} must be numeric at source record {record + 1}."
        ) from error
    if not np.isfinite(number):
        raise ValueError(f"Forest field {field!r} must be finite at source record {record + 1}.")
    return number


def normalize_forest_data(
    data: ForestData | pd.DataFrame,
    *,
    columns: Sequence[ForestColumn],
) -> _NormalizedForestTable:
    """Validate and normalize a ``ForestData`` or long-form ``DataFrame``.

    Parameters
    ----------
    data : ForestData or pandas.DataFrame
        File-reader result or a long table using default reserved field names.
    columns : sequence of ForestColumn
        Display and CI columns in final left-to-right order.

    Returns
    -------
    _NormalizedForestTable
        Unique visual rows, observations, and merged spans for the renderer.

    Raises
    ------
    TypeError
        Raised for an unsupported input object.
    ValueError
        Raised when fields, row groups, numbers, boolean flags, CI targets, or
        merged spans violate the contract.

    Notes
    -----
    Records sharing ``_plot_row`` must be contiguous and agree on series, row
    type, indentation, and summary flag. Each ``(_plot_row, _ci_column)`` may
    have at most one record.
    """

    if isinstance(data, ForestData):
        source = data
    elif isinstance(data, pd.DataFrame):
        source = ForestData(frame=data, mapping=ForestDataMapping())
    else:
        raise TypeError("Forest data must be a ForestData object or pandas DataFrame.")
    frame = source.frame
    mapping = source.mapping
    if not isinstance(frame, pd.DataFrame):
        raise TypeError("ForestData.frame must be a pandas DataFrame.")
    if frame.empty:
        raise ValueError("Forest data must contain at least one record.")
    compute_keys = [column.key for column in columns]
    if len(compute_keys) != len(set(compute_keys)):
        raise ValueError("Forest column keys must be unique.")
    display_columns = tuple(column.key for column in columns if column.role != "ci")
    defined_ci = tuple(column.key for column in columns if column.role == "ci")
    if not defined_ci:
        raise ValueError("At least one ForestColumn must use role='ci'.")
    required = set(mapping.technical_fields()) | set(display_columns)
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"Forest data lacks required fields: {missing}")

    row_ids = frame[mapping.plot_row].tolist()
    if any(_is_blank(value) for value in row_ids):
        raise ValueError(f"Forest field {mapping.plot_row!r} must not contain blank values.")
    for value in row_ids:
        try:
            hash(value)
        except TypeError as error:
            raise ValueError(
                "Forest plot-row identifiers must be hashable scalar values."
            ) from error

    groups: list[tuple[Any, list[int]]] = []
    closed: set[Any] = set()
    current_id: Any = object()
    for index, plot_row in enumerate(row_ids):
        if not groups or plot_row != current_id:
            if plot_row in closed:
                raise ValueError(
                    f"Records for plot row {plot_row!r} must be contiguous in source order."
                )
            if groups:
                closed.add(current_id)
            groups.append((plot_row, [index]))
            current_id = plot_row
        else:
            groups[-1][1].append(index)

    plot_rows: list[_NormalizedPlotRow] = []
    observations: list[_NormalizedObservation] = []
    series_order: list[str] = []
    ci_order: list[str] = []
    record_to_row: dict[int, int] = {}
    seen_targets: set[tuple[Any, str]] = set()

    for row_index, (plot_row, indices) in enumerate(groups):
        subset = frame.iloc[indices]
        row_types = [str(value).strip() for value in subset[mapping.row_type]]
        if len(set(row_types)) != 1:
            raise ValueError(f"Plot row {plot_row!r} contains inconsistent row_type values.")
        kind = row_types[0]
        if kind not in VALID_ROW_TYPES:
            raise ValueError(f"Unsupported forest row types: {[kind]}")

        indent_values = [
            _coerce_number(value, field=mapping.indent, record=index)
            for index, value in zip(indices, subset[mapping.indent], strict=True)
        ]
        if any(value < 0 for value in indent_values):
            raise ValueError("Forest indentation must contain non-negative numbers.")
        if not np.allclose(indent_values, indent_values[0], rtol=0, atol=0):
            raise ValueError(f"Plot row {plot_row!r} contains inconsistent indentation values.")

        summary_values = subset[mapping.is_summary].tolist()
        if any(not isinstance(value, (bool, np.bool_)) for value in summary_values):
            raise ValueError(
                f"Forest summary field {mapping.is_summary!r} must contain boolean values only."
            )
        if len({bool(value) for value in summary_values}) != 1:
            raise ValueError(f"Plot row {plot_row!r} contains inconsistent summary flags.")
        summary = bool(summary_values[0])

        raw_series = subset[mapping.series].tolist()
        series_values = [None if _is_blank(value) else str(value).strip() for value in raw_series]
        nonblank_series = {value for value in series_values if value is not None}
        if len(nonblank_series) > 1:
            raise ValueError(f"Plot row {plot_row!r} contains inconsistent series values.")
        series_value = next(iter(nonblank_series), None)
        if any(value != series_value for value in series_values) and kind in {
            "estimate",
            "summary",
        }:
            raise ValueError(f"Plot row {plot_row!r} contains blank and nonblank series values.")

        display_values = tuple(
            (
                column_key,
                _display_value(
                    subset[column_key].tolist(), column_key=column_key, plot_row=plot_row
                ),
            )
            for column_key in display_columns
        )
        plot_rows.append(
            _NormalizedPlotRow(
                plot_row=plot_row,
                record_indices=tuple(indices),
                row_type=kind,
                indent=float(indent_values[0]),
                is_summary=summary,
                series=series_value,
                display_values=display_values,
            )
        )
        for record_index in indices:
            record_to_row[record_index] = row_index
            record = frame.iloc[record_index]
            series = (
                None if _is_blank(record[mapping.series]) else str(record[mapping.series]).strip()
            )
            ci_column = (
                None
                if _is_blank(record[mapping.ci_column])
                else str(record[mapping.ci_column]).strip()
            )
            interval_values = [
                record[mapping.estimate],
                record[mapping.lower],
                record[mapping.upper],
            ]
            blank_interval = [_is_blank(value) for value in interval_values]
            if kind in {"estimate", "summary"}:
                if series is None or ci_column is None:
                    raise ValueError(
                        f"Estimate/summary record {record_index + 1} requires nonblank series and ci_column."
                    )
                if ci_column not in defined_ci:
                    raise ValueError(
                        f"Forest CI target {ci_column!r} at source record {record_index + 1} "
                        "does not name a column with role='ci'."
                    )
                target_key = (plot_row, ci_column)
                if target_key in seen_targets:
                    raise ValueError(
                        f"Plot row {plot_row!r} contains more than one record for CI column {ci_column!r}."
                    )
                seen_targets.add(target_key)
                if series not in series_order:
                    series_order.append(series)
                if ci_column not in ci_order:
                    ci_order.append(ci_column)
            if all(blank_interval):
                continue
            if any(blank_interval):
                raise ValueError(
                    f"Estimate, lower and upper must be all present or all blank at source record {record_index + 1}."
                )
            if kind not in {"estimate", "summary"}:
                raise ValueError(
                    f"Row type {kind!r} cannot contain a confidence interval at source record {record_index + 1}."
                )
            if series is None:
                raise ValueError(f"Forest series is blank at source record {record_index + 1}.")
            if ci_column is None:
                raise ValueError(f"Forest CI column is blank at source record {record_index + 1}.")
            estimate = _coerce_number(
                interval_values[0], field=mapping.estimate, record=record_index
            )
            lower = _coerce_number(interval_values[1], field=mapping.lower, record=record_index)
            upper = _coerce_number(interval_values[2], field=mapping.upper, record=record_index)
            if not lower <= estimate <= upper:
                raise ValueError(
                    f"Confidence interval does not contain its estimate at source record {record_index + 1}."
                )
            observations.append(
                _NormalizedObservation(
                    record_index=record_index,
                    plot_row=plot_row,
                    series=series,
                    ci_column=ci_column,
                    estimate=estimate,
                    lower=lower,
                    upper=upper,
                    row_type=kind,
                    is_summary=summary,
                )
            )

    spans: list[_NormalizedSpan] = []
    span_coverage: dict[str, set[int]] = {}
    for span in source.spans:
        if span.column_key not in display_columns:
            raise ValueError(
                f"Merged field {span.column_key!r} must name a displayed text or numeric column."
            )
        if (
            span.start_record < 0
            or span.end_record >= len(frame)
            or span.start_record > span.end_record
        ):
            raise ValueError(f"Merged field {span.column_key!r} has invalid record bounds.")
        start_row = record_to_row[span.start_record]
        end_row = record_to_row[span.end_record]
        if plot_rows[start_row].record_indices[0] != span.start_record:
            raise ValueError(
                f"Merged field {span.column_key!r} must begin at the first record of a plot-row group."
            )
        if plot_rows[end_row].record_indices[-1] != span.end_record:
            raise ValueError(
                f"Merged field {span.column_key!r} must end at the last record of a plot-row group."
            )
        covered = set(range(start_row, end_row + 1))
        prior = span_coverage.setdefault(span.column_key, set())
        if prior & covered:
            raise ValueError(f"Merged regions overlap in display field {span.column_key!r}.")
        prior.update(covered)
        value = frame.iloc[span.start_record][span.column_key]
        if _is_blank(value):
            raise ValueError(f"Merged field {span.column_key!r} has a blank top-left value.")
        spans.append(
            _NormalizedSpan(
                span.column_key,
                span.start_record,
                span.end_record,
                start_row,
                end_row,
                value,
            )
        )

    return _NormalizedForestTable(
        frame=frame,
        mapping=mapping,
        plot_rows=tuple(plot_rows),
        observations=tuple(observations),
        spans=tuple(spans),
        series_order=tuple(series_order),
        ci_columns=tuple(ci_order),
    )


__all__ = ["VALID_ROW_TYPES", "normalize_forest_data"]

"""Deterministic validation for datasets before they enter the database."""

from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping

import pandas as pd


@dataclass(frozen=True)
class DatasetSpec:
    """Rules for one source table."""

    required_columns: tuple[str, ...] = ()
    non_nullable_columns: tuple[str, ...] = ()
    date_columns: tuple[str, ...] = ()
    numeric_columns: tuple[str, ...] = ()
    non_negative_columns: tuple[str, ...] = ()
    unique_columns: tuple[str, ...] = ()
    allowed_values: Mapping[str, frozenset[Any]] = field(default_factory=dict)
    reference_values: Mapping[str, Iterable[Any]] = field(default_factory=dict)
    reconciliation: tuple[str, str, float] | None = None


@dataclass
class ValidationResult:
    status: str = "PASS"
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    records_processed: int = 0
    records_rejected: int = 0
    _rejected_indices: set[Any] = field(default_factory=set, repr=False)

    def reject(self, indices: Iterable[Any]) -> None:
        self._rejected_indices.update(indices)
        self.records_rejected = len(self._rejected_indices)

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "errors": self.errors,
            "warnings": self.warnings,
            "records_processed": self.records_processed,
            "records_rejected": self.records_rejected,
        }


class DataValidationAgent:
    """Run configured data-quality checks without calculating business metrics."""

    def validate(self, frame: pd.DataFrame, spec: DatasetSpec) -> ValidationResult:
        result = ValidationResult(records_processed=len(frame))
        self._check_required_columns(frame, spec, result)
        self._check_missing_values(frame, spec, result)
        self._check_types(frame, spec, result)
        self._check_dates(frame, spec, result)
        self._check_duplicates(frame, spec, result)
        self._check_domains(frame, spec, result)
        self._check_references(frame, spec, result)
        self._check_reconciliation(frame, spec, result)
        result.status = "FAIL" if result.errors else ("PASS_WITH_WARNINGS" if result.warnings else "PASS")
        return result

    @staticmethod
    def _check_required_columns(frame: pd.DataFrame, spec: DatasetSpec, result: ValidationResult) -> None:
        missing = sorted(set(spec.required_columns) - set(frame.columns))
        if missing:
            result.errors.append(f"Missing required columns: {', '.join(missing)}")
            result.reject(frame.index)

    @staticmethod
    def _check_missing_values(frame: pd.DataFrame, spec: DatasetSpec, result: ValidationResult) -> None:
        for column in spec.non_nullable_columns:
            if column not in frame:
                continue
            count = int(frame[column].isna().sum())
            if count:
                result.errors.append(f"{column} contains {count} missing values")
                result.reject(frame.index[frame[column].isna()])

    @staticmethod
    def _check_types(frame: pd.DataFrame, spec: DatasetSpec, result: ValidationResult) -> None:
        for column in spec.numeric_columns:
            if column not in frame:
                continue
            invalid = pd.to_numeric(frame[column], errors="coerce").isna() & frame[column].notna()
            if invalid.any():
                result.errors.append(f"{column} contains {int(invalid.sum())} non-numeric values")
                result.reject(frame.index[invalid])

    @staticmethod
    def _check_dates(frame: pd.DataFrame, spec: DatasetSpec, result: ValidationResult) -> None:
        for column in spec.date_columns:
            if column not in frame:
                continue
            parsed = pd.to_datetime(frame[column], errors="coerce")
            invalid = parsed.isna() & frame[column].notna()
            if invalid.any():
                result.errors.append(f"{column} contains {int(invalid.sum())} invalid dates")
                result.reject(frame.index[invalid])

    @staticmethod
    def _check_duplicates(frame: pd.DataFrame, spec: DatasetSpec, result: ValidationResult) -> None:
        columns = [column for column in spec.unique_columns if column in frame]
        if columns:
            count = int(frame.duplicated(subset=columns).sum())
            if count:
                result.errors.append(f"Found {count} duplicate records for {', '.join(columns)}")
                result.reject(frame.index[frame.duplicated(subset=columns)])

    @staticmethod
    def _check_domains(frame: pd.DataFrame, spec: DatasetSpec, result: ValidationResult) -> None:
        for column, allowed in spec.allowed_values.items():
            if column not in frame:
                continue
            invalid = frame[column].notna() & ~frame[column].isin(allowed)
            if invalid.any():
                result.errors.append(f"{column} contains {int(invalid.sum())} invalid values")
                result.reject(frame.index[invalid])
        for column in spec.non_negative_columns:
            if column not in frame:
                continue
            values = pd.to_numeric(frame[column], errors="coerce")
            count = int((values < 0).sum())
            if count:
                result.errors.append(f"{column} contains {count} negative values")
                result.reject(frame.index[values < 0])

    @staticmethod
    def _check_references(frame: pd.DataFrame, spec: DatasetSpec, result: ValidationResult) -> None:
        for column, reference in spec.reference_values.items():
            if column not in frame:
                continue
            allowed = set(reference)
            invalid = frame[column].notna() & ~frame[column].isin(allowed)
            if invalid.any():
                result.errors.append(f"{column} contains {int(invalid.sum())} unknown references")
                result.reject(frame.index[invalid])

    @staticmethod
    def _check_reconciliation(frame: pd.DataFrame, spec: DatasetSpec, result: ValidationResult) -> None:
        if not spec.reconciliation:
            return
        total_column, parts_column, tolerance = spec.reconciliation
        if total_column not in frame or parts_column not in frame:
            return
        difference = (pd.to_numeric(frame[total_column], errors="coerce") - pd.to_numeric(frame[parts_column], errors="coerce")).abs()
        count = int((difference > tolerance).sum())
        if count:
            result.warnings.append(f"{count} records failed {total_column} reconciliation")
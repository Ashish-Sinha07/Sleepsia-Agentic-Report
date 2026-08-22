import pandas as pd

from agents.validation_agent import DataValidationAgent, DatasetSpec


def test_validation_reports_multiple_data_quality_failures():
    frame = pd.DataFrame(
        {
            "order_id": [1, 1],
            "order_date": ["2026-01-01", "bad-date"],
            "platform": ["Amazon", "Unknown"],
            "units": [2, -1],
        }
    )
    spec = DatasetSpec(
        required_columns=("order_id", "order_date", "platform", "units"),
        date_columns=("order_date",),
        non_negative_columns=("units",),
        unique_columns=("order_id",),
        allowed_values={"platform": frozenset({"Amazon", "Flipkart"})},
    )

    result = DataValidationAgent().validate(frame, spec)

    assert result.status == "FAIL"
    assert result.records_processed == 2
    assert len(result.errors) == 4


def test_reconciliation_is_a_warning_not_a_hard_failure():
    frame = pd.DataFrame({"revenue": [100], "components": [90]})

    result = DataValidationAgent().validate(
        frame, DatasetSpec(reconciliation=("revenue", "components", 0.01))
    )

    assert result.status == "PASS_WITH_WARNINGS"
    assert result.errors == []
    assert result.warnings
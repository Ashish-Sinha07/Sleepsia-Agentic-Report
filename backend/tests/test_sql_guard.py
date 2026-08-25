"""SQL guard tests (spec section 19.B / 19.E): validation, allowlisting,
row-limit clamping, and rejection of destructive/multi-statement SQL.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from app.services.sql_guard import validate_select_sql, execute_safe_select, SQLValidationError, ALLOWED_VIEWS


def test_valid_select_against_allowed_view_passes():
    validate_select_sql("SELECT platform, SUM(net_sales) FROM vw_product_platform_daily GROUP BY platform")


@pytest.mark.parametrize(
    "sql",
    [
        "DELETE FROM vw_product_platform_daily",
        "UPDATE vw_product_platform_daily SET net_sales = 0",
        "DROP TABLE daily_sales",
        "INSERT INTO daily_sales VALUES (1)",
        "TRUNCATE daily_sales",
        "ALTER TABLE daily_sales ADD COLUMN x INT",
        "GRANT ALL ON *.* TO 'x'@'%'",
        "CALL some_procedure()",
    ],
)
def test_destructive_statements_are_rejected(sql):
    with pytest.raises(SQLValidationError):
        validate_select_sql(sql)


def test_multiple_statements_are_rejected():
    with pytest.raises(SQLValidationError):
        validate_select_sql("SELECT * FROM vw_product_platform_daily; DROP TABLE daily_sales;")


def test_comments_are_rejected_as_an_injection_smuggling_vector():
    with pytest.raises(SQLValidationError):
        validate_select_sql("SELECT * FROM vw_product_platform_daily -- ; DROP TABLE daily_sales")
    with pytest.raises(SQLValidationError):
        validate_select_sql("SELECT * FROM vw_product_platform_daily /* comment */")


def test_raw_table_access_is_rejected_view_allowlist_only():
    with pytest.raises(SQLValidationError):
        validate_select_sql("SELECT * FROM daily_sales")
    with pytest.raises(SQLValidationError):
        validate_select_sql("SELECT * FROM users")


def test_non_select_statements_are_rejected():
    with pytest.raises(SQLValidationError):
        validate_select_sql("SHOW TABLES")
    with pytest.raises(SQLValidationError):
        validate_select_sql("USE sleepsia")


def test_every_allowed_view_is_individually_accepted():
    for view in ALLOWED_VIEWS:
        validate_select_sql(f"SELECT * FROM {view}")


def test_execute_safe_select_clamps_row_limit(db_session):
    rows = execute_safe_select(
        db_session,
        "SELECT platform FROM vw_product_platform_daily LIMIT 500",
        max_rows=5,
        timeout_ms=5000,
    )
    assert len(rows) <= 5


def test_execute_safe_select_rejects_destructive_sql(db_session):
    with pytest.raises(SQLValidationError):
        execute_safe_select(db_session, "DELETE FROM daily_sales", max_rows=10, timeout_ms=5000)

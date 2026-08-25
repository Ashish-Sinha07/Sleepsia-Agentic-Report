"""SQL execution guardrails for the AI Assistant's SQL path.

Nothing in this project lets an LLM emit raw SQL text: query templates are
fixed, parameterized strings (see `sql_tools.py`) and the LLM only ever picks
a template name and fills in bind-parameter values (platform, sku, date
range, limit). This module is the enforcement layer underneath that choice:
it validates the final rendered SQL text before every execution (defense in
depth, in case a future change makes template generation more dynamic),
clamps row limits, and enforces a server-side statement timeout.

Allowed: single, read-only SELECT statements against the fixed analytical
view surface below. Never: INSERT/UPDATE/DELETE/DROP/ALTER/TRUNCATE/CREATE/
GRANT/REVOKE/CALL/EXEC, multiple statements, or access to any table/view
outside the allowlist (including the system schema).
"""

import logging
import re
from typing import Any, Dict, List, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class SQLValidationError(ValueError):
    """Raised when a query fails the read-only / allowlist validation."""


# The only objects a generated query may ever read from. All are
# already-aggregated analytical views (sql/schema.sql) - never a raw table.
ALLOWED_VIEWS = {
    "vw_product_platform_daily",
    "vw_platform_performance",
    "vw_product_performance",
    "vw_profitability",
    "vw_inventory_health",
    "vw_warehouse_summary",
    "vw_regional_performance",
    "vw_daily_kpi_summary",
}

_FORBIDDEN_KEYWORDS = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|CREATE|GRANT|REVOKE|CALL|EXECUTE|"
    r"MERGE|REPLACE|LOCK|UNLOCK|SET|SHOW|USE|LOAD)\b",
    re.IGNORECASE,
)
_COMMENT_RE = re.compile(r"(--|#|/\*)")
_FROM_JOIN_TABLE_RE = re.compile(r"\b(?:FROM|JOIN)\s+`?([a-zA-Z_][a-zA-Z0-9_]*)`?", re.IGNORECASE)


def validate_select_sql(sql: str) -> None:
    """Raise SQLValidationError unless `sql` is a single read-only SELECT
    against an allowlisted view, with no comments and no other statements."""
    if not sql or not sql.strip():
        raise SQLValidationError("Empty SQL")

    stripped = sql.strip()

    if _COMMENT_RE.search(stripped):
        raise SQLValidationError("SQL comments are not allowed")

    body = stripped[:-1] if stripped.endswith(";") else stripped
    if ";" in body:
        raise SQLValidationError("Multiple SQL statements are not allowed")

    if not re.match(r"^\s*SELECT\b", body, re.IGNORECASE):
        raise SQLValidationError("Only SELECT statements are allowed")

    if _FORBIDDEN_KEYWORDS.search(body):
        raise SQLValidationError("Query contains a forbidden keyword")

    tables = {m.group(1).lower() for m in _FROM_JOIN_TABLE_RE.finditer(body)}
    if not tables:
        raise SQLValidationError("Could not determine the queried view")
    disallowed = tables - {v.lower() for v in ALLOWED_VIEWS}
    if disallowed:
        raise SQLValidationError(f"Query references non-allowlisted table(s): {sorted(disallowed)}")


def _clamp_limit(sql: str, max_rows: int) -> str:
    """Ensure the query's LIMIT is no greater than max_rows, appending one if absent."""
    match = re.search(r"\bLIMIT\s+(\d+)\b", sql, re.IGNORECASE)
    if match:
        requested = int(match.group(1))
        if requested > max_rows:
            sql = sql[: match.start(1)] + str(max_rows) + sql[match.end(1):]
        return sql
    return f"{sql.rstrip().rstrip(';')} LIMIT {max_rows}"


def execute_safe_select(
    db: Session,
    sql: str,
    params: Optional[Dict[str, Any]] = None,
    max_rows: int = 200,
    timeout_ms: int = 5000,
) -> List[Dict[str, Any]]:
    """Validate, row-limit, and time-box a read-only SELECT; returns rows as dicts."""
    validate_select_sql(sql)
    guarded_sql = _clamp_limit(sql, max_rows)

    # MySQL optimizer hint enforces a server-side wall-clock cap per statement.
    # Applied only after our own validation, to our own already-checked SQL.
    hinted_sql = re.sub(
        r"^\s*SELECT\b",
        f"SELECT /*+ MAX_EXECUTION_TIME({int(timeout_ms)}) */",
        guarded_sql,
        count=1,
        flags=re.IGNORECASE,
    )

    result = db.execute(text(hinted_sql), params or {})
    columns = list(result.keys())
    rows = result.fetchmany(max_rows)
    return [dict(zip(columns, row)) for row in rows]

"""Parameterized, bind-safe query templates for the AI Assistant's SQL path.

Replaces the old ad hoc tool functions in `ai_assistant_service.py`, two of
which built SQL via f-string interpolation of LLM-controlled input
(`_get_platform_metrics`, `_get_product_metrics`) - a SQL-injection surface.
Every template here uses only SQLAlchemy bind parameters (`:name`) for
user/LLM-controlled values; the only place a value is ever interpolated
directly into SQL text is `limit`, and only after it has been coerced with
Python's `int()` (which raises on anything that isn't a plain integer, so it
can never carry injected SQL text).

Each tool is exposed to Groq as a function-calling "tool" (same JSON schema
shape the previous implementation used) so the LLM picks a tool name and
fills in structured parameters - it never writes SQL itself. The rendered
SQL is still re-validated by `sql_guard.execute_safe_select` before running,
as defense in depth.
"""

from datetime import date
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.config import settings
from app.services.sql_guard import execute_safe_select

_ALLOWED_ORDER_COLUMNS = {"revenue", "profit", "units_sold"}


def _run(db: Session, sql: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
    return execute_safe_select(
        db, sql, params, max_rows=settings.SQL_MAX_ROWS, timeout_ms=settings.SQL_TIMEOUT_MS
    )


def _num(value: Any) -> float:
    return float(value) if value is not None else 0.0


def get_kpi_summary(db: Session, date_from: Optional[str] = None, date_to: Optional[str] = None, **_) -> Dict[str, Any]:
    """Overall business KPI summary: revenue, units, ROAS, profit margin, returns/cancellations."""
    sql = """
        SELECT
            SUM(total_orders) AS total_orders,
            SUM(total_units_sold) AS total_units_sold,
            SUM(total_gross_sales) AS total_gross_sales,
            SUM(total_net_sales) AS total_net_sales,
            SUM(total_ad_spend) AS total_ad_spend,
            SUM(total_contribution) AS total_contribution,
            CASE WHEN SUM(total_net_sales) > 0
                THEN ROUND(SUM(total_contribution) / SUM(total_net_sales) * 100, 2)
                ELSE NULL END AS overall_profit_margin_pct,
            CASE WHEN SUM(total_ad_spend) > 0
                THEN ROUND(SUM(total_ad_sales) / SUM(total_ad_spend), 2)
                ELSE NULL END AS overall_roas,
            SUM(total_units_returned) AS total_units_returned,
            SUM(total_units_cancelled) AS total_units_cancelled
        FROM vw_daily_kpi_summary
        WHERE (:date_from IS NULL OR date >= :date_from)
          AND (:date_to IS NULL OR date <= :date_to)
    """
    rows = _run(db, sql, {"date_from": date_from, "date_to": date_to})
    row = rows[0] if rows else {}
    return {
        "total_orders": int(row.get("total_orders") or 0),
        "total_units_sold": int(row.get("total_units_sold") or 0),
        "total_gross_sales": _num(row.get("total_gross_sales")),
        "total_net_sales": _num(row.get("total_net_sales")),
        "total_ad_spend": _num(row.get("total_ad_spend")),
        "total_contribution": _num(row.get("total_contribution")),
        "overall_profit_margin_pct": _num(row.get("overall_profit_margin_pct")),
        "overall_roas": _num(row.get("overall_roas")),
        "total_units_returned": int(row.get("total_units_returned") or 0),
        "total_units_cancelled": int(row.get("total_units_cancelled") or 0),
    }


def get_platform_metrics(
    db: Session, platform: Optional[str] = None, date_from: Optional[str] = None, date_to: Optional[str] = None, **_
) -> Dict[str, Any]:
    """Revenue/profit/ROAS per e-commerce platform, optionally filtered to one platform and/or date range."""
    platform = None if (platform or "").lower() in ("", "all") else platform
    sql = """
        SELECT
            platform,
            SUM(net_sales) AS revenue,
            SUM(units_sold) AS units_sold,
            SUM(contribution_inr) AS profit,
            CASE WHEN SUM(net_sales) > 0
                THEN ROUND(SUM(contribution_inr) / SUM(net_sales) * 100, 2)
                ELSE NULL END AS profit_margin_pct,
            CASE WHEN SUM(ad_spend) > 0
                THEN ROUND(SUM(ad_attributed_sales) / SUM(ad_spend), 2)
                ELSE NULL END AS roas
        FROM vw_product_platform_daily
        WHERE (:platform IS NULL OR platform = :platform)
          AND (:date_from IS NULL OR date >= :date_from)
          AND (:date_to IS NULL OR date <= :date_to)
        GROUP BY platform
        ORDER BY revenue DESC
    """
    rows = _run(db, sql, {"platform": platform, "date_from": date_from, "date_to": date_to})
    return {
        "platforms": [
            {
                "platform": r["platform"],
                "revenue": _num(r.get("revenue")),
                "units_sold": int(r.get("units_sold") or 0),
                "profit": _num(r.get("profit")),
                "profit_margin_pct": _num(r.get("profit_margin_pct")),
                "roas": _num(r.get("roas")),
            }
            for r in rows
        ]
    }


def get_product_metrics(
    db: Session,
    sku: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    order_by: str = "profit",
    limit: int = 10,
    **_,
) -> Dict[str, Any]:
    """Revenue/profit/units per product (SKU), ranked by the requested metric."""
    order_column = order_by if order_by in _ALLOWED_ORDER_COLUMNS else "profit"
    safe_limit = max(1, min(int(limit), settings.SQL_MAX_ROWS))
    sql = f"""
        SELECT
            sku,
            product_name,
            SUM(net_sales) AS revenue,
            SUM(contribution_inr) AS profit,
            SUM(units_sold) AS units_sold
        FROM vw_product_platform_daily
        WHERE (:sku IS NULL OR sku = :sku)
          AND (:date_from IS NULL OR date >= :date_from)
          AND (:date_to IS NULL OR date <= :date_to)
        GROUP BY sku, product_name
        ORDER BY {order_column} DESC
        LIMIT {safe_limit}
    """
    rows = _run(db, sql, {"sku": sku, "date_from": date_from, "date_to": date_to})
    return {
        "products": [
            {
                "sku": r["sku"],
                "product_name": r["product_name"],
                "revenue": _num(r.get("revenue")),
                "profit": _num(r.get("profit")),
                "units_sold": int(r.get("units_sold") or 0),
            }
            for r in rows
        ]
    }


def get_advertising_metrics(
    db: Session, platform: Optional[str] = None, date_from: Optional[str] = None, date_to: Optional[str] = None, **_
) -> Dict[str, Any]:
    """ROAS, ACOS, and ad spend, optionally filtered by platform and/or date range."""
    platform = None if (platform or "").lower() in ("", "all") else platform
    sql = """
        SELECT
            CASE WHEN SUM(ad_spend) > 0
                THEN ROUND(SUM(ad_attributed_sales) / SUM(ad_spend), 2)
                ELSE NULL END AS roas,
            CASE WHEN SUM(ad_attributed_sales) > 0
                THEN ROUND(SUM(ad_spend) / SUM(ad_attributed_sales) * 100, 2)
                ELSE NULL END AS acos_pct,
            SUM(ad_spend) AS ad_spend,
            SUM(ad_attributed_sales) AS ad_attributed_sales
        FROM vw_product_platform_daily
        WHERE (:platform IS NULL OR platform = :platform)
          AND (:date_from IS NULL OR date >= :date_from)
          AND (:date_to IS NULL OR date <= :date_to)
    """
    rows = _run(db, sql, {"platform": platform, "date_from": date_from, "date_to": date_to})
    row = rows[0] if rows else {}
    return {
        "roas": _num(row.get("roas")),
        "acos_pct": _num(row.get("acos_pct")),
        "ad_spend": _num(row.get("ad_spend")),
        "ad_attributed_sales": _num(row.get("ad_attributed_sales")),
    }


def get_inventory_status(db: Session, warehouse: Optional[str] = None, **_) -> Dict[str, Any]:
    """Warehouse inventory levels and days-of-cover, lowest stock first."""
    warehouse = None if (warehouse or "").lower() in ("", "all") else warehouse
    sql = """
        SELECT
            warehouse_name,
            city,
            region,
            SUM(closing_stock) AS total_stock,
            AVG(days_of_cover) AS avg_days_of_cover,
            COUNT(DISTINCT sku) AS sku_count
        FROM vw_inventory_health
        WHERE (:warehouse IS NULL OR city = :warehouse OR warehouse_name = :warehouse OR region = :warehouse)
        GROUP BY warehouse_name, city, region
        ORDER BY total_stock ASC
    """
    rows = _run(db, sql, {"warehouse": warehouse})
    return {
        "warehouses": [
            {
                "warehouse_name": r["warehouse_name"],
                "city": r["city"],
                "region": r["region"],
                "total_stock": _num(r.get("total_stock")),
                "avg_days_of_cover": _num(r.get("avg_days_of_cover")),
                "sku_count": int(r.get("sku_count") or 0),
            }
            for r in rows
        ]
    }


def get_quality_metrics(
    db: Session, platform: Optional[str] = None, date_from: Optional[str] = None, date_to: Optional[str] = None, **_
) -> Dict[str, Any]:
    """Return rate and cancellation rate, optionally filtered by platform and/or date range."""
    platform = None if (platform or "").lower() in ("", "all") else platform
    sql = """
        SELECT
            CASE WHEN SUM(units_sold) > 0
                THEN ROUND(SUM(units_returned) / SUM(units_sold) * 100, 2)
                ELSE NULL END AS return_rate_pct,
            CASE WHEN SUM(orders) > 0
                THEN ROUND(SUM(units_cancelled) / SUM(orders) * 100, 2)
                ELSE NULL END AS cancellation_rate_pct,
            SUM(units_returned) AS units_returned,
            SUM(units_cancelled) AS units_cancelled
        FROM vw_product_platform_daily
        WHERE (:platform IS NULL OR platform = :platform)
          AND (:date_from IS NULL OR date >= :date_from)
          AND (:date_to IS NULL OR date <= :date_to)
    """
    rows = _run(db, sql, {"platform": platform, "date_from": date_from, "date_to": date_to})
    row = rows[0] if rows else {}
    return {
        "return_rate_pct": _num(row.get("return_rate_pct")),
        "cancellation_rate_pct": _num(row.get("cancellation_rate_pct")),
        "units_returned": int(row.get("units_returned") or 0),
        "units_cancelled": int(row.get("units_cancelled") or 0),
    }


# Registry consumed by both the Groq tool-calling definitions and the executor
# dispatch, so the two can never drift out of sync with each other.
SQL_TOOLS = {
    "get_kpi_summary": {
        "description": "Get overall business KPI summary: revenue, units sold, ROAS, profit margin, returns/cancellations.",
        "executor": get_kpi_summary,
        "parameters": {
            "date_from": {"type": "string", "description": "Start date (YYYY-MM-DD), optional"},
            "date_to": {"type": "string", "description": "End date (YYYY-MM-DD), optional"},
        },
    },
    "get_platform_metrics": {
        "description": "Get revenue, profit, and ROAS per e-commerce platform (Amazon, Flipkart, Blinkit, Myntra, JioMart).",
        "executor": get_platform_metrics,
        "parameters": {
            "platform": {"type": "string", "description": "Platform name, or omit/'all' for every platform"},
            "date_from": {"type": "string", "description": "Start date (YYYY-MM-DD), optional"},
            "date_to": {"type": "string", "description": "End date (YYYY-MM-DD), optional"},
        },
    },
    "get_product_metrics": {
        "description": "Get revenue, profit, and units sold per product, ranked by revenue/profit/units_sold.",
        "executor": get_product_metrics,
        "parameters": {
            "sku": {"type": "string", "description": "Specific product SKU, optional"},
            "date_from": {"type": "string", "description": "Start date (YYYY-MM-DD), optional"},
            "date_to": {"type": "string", "description": "End date (YYYY-MM-DD), optional"},
            "order_by": {"type": "string", "description": "One of: revenue, profit, units_sold"},
            "limit": {"type": "integer", "description": "Max number of products to return, default 10"},
        },
    },
    "get_advertising_metrics": {
        "description": "Get ROAS, ACOS, and advertising spend, optionally filtered by platform and/or date range.",
        "executor": get_advertising_metrics,
        "parameters": {
            "platform": {"type": "string", "description": "Platform name, or omit/'all' for every platform"},
            "date_from": {"type": "string", "description": "Start date (YYYY-MM-DD), optional"},
            "date_to": {"type": "string", "description": "End date (YYYY-MM-DD), optional"},
        },
    },
    "get_inventory_status": {
        "description": "Get warehouse inventory levels and days-of-cover, lowest stock first.",
        "executor": get_inventory_status,
        "parameters": {
            "warehouse": {"type": "string", "description": "Warehouse city/name/region, or omit/'all' for every warehouse"},
        },
    },
    "get_quality_metrics": {
        "description": "Get return rate and cancellation rate, optionally filtered by platform and/or date range.",
        "executor": get_quality_metrics,
        "parameters": {
            "platform": {"type": "string", "description": "Platform name, or omit/'all' for every platform"},
            "date_from": {"type": "string", "description": "Start date (YYYY-MM-DD), optional"},
            "date_to": {"type": "string", "description": "End date (YYYY-MM-DD), optional"},
        },
    },
}


def _nullable_params(parameters: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Widen each param's JSON-schema type to allow null.

    Groq validates tool-call arguments strictly against the declared schema
    and rejects the call outright if the model passes `null` for an optional
    field typed as plain "string" - which it does routinely for parameters
    the question didn't mention. Every parameter here is optional, so every
    type must explicitly admit null.
    """
    widened = {}
    for name, param_spec in parameters.items():
        param_type = param_spec.get("type")
        if param_type in (None, "null") or isinstance(param_type, list):
            widened[name] = param_spec
        else:
            widened[name] = {**param_spec, "type": [param_type, "null"]}
    return widened


def get_groq_tool_definitions() -> List[Dict[str, Any]]:
    """Groq/OpenAI-style function-calling schema for every registered SQL tool."""
    definitions = []
    for name, spec in SQL_TOOLS.items():
        definitions.append(
            {
                "type": "function",
                "function": {
                    "name": name,
                    "description": spec["description"],
                    "parameters": {
                        "type": "object",
                        "properties": _nullable_params(spec["parameters"]),
                    },
                },
            }
        )
    return definitions


def execute_tool(db: Session, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
    """Run a registered SQL tool by name with LLM-supplied structured parameters."""
    spec = SQL_TOOLS.get(tool_name)
    if not spec:
        return {"error": f"Unknown tool: {tool_name}"}
    try:
        return spec["executor"](db, **tool_input)
    except Exception as e:
        return {"error": str(e)}

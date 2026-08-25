from pydantic import BaseModel
from datetime import date
from typing import Optional, List, Dict, Any
from decimal import Decimal
from app.schemas.common import DateRange, KpiMetrics


class KpiResponse(BaseModel):
    """Response for KPI endpoints."""

    period: DateRange
    kpis: KpiMetrics
    trends: Optional[Dict[str, str]] = None
    comparisons: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "period": {
                    "start_date": "2026-08-01",
                    "end_date": "2026-08-21",
                },
                "kpis": {
                    "total_revenue": 4250000.00,
                    "net_revenue": 4050000.00,
                    "total_profit": 820000.00,
                },
                "trends": {
                    "revenue_trend": "upward",
                    "profit_trend": "stable",
                },
                "comparisons": {
                    "vs_previous_period": {
                        "revenue_change_pct": 12.4,
                        "profit_change_pct": 8.7,
                    }
                },
            }
        }


class DailyKpiResponse(BaseModel):
    """Daily KPI data point."""

    date: date
    total_revenue: Decimal
    net_revenue: Decimal
    total_profit: Decimal
    profit_margin_pct: Optional[Decimal] = None
    units_sold: int
    orders: int
    ad_spend: Decimal
    roas: Optional[Decimal] = None
    total_units_returned: int
    total_units_cancelled: int


class DailyKpisResponse(BaseModel):
    """Response for daily KPIs endpoint."""

    period: DateRange
    data: List[DailyKpiResponse]
    total: int

    class Config:
        json_schema_extra = {
            "example": {
                "period": {
                    "start_date": "2026-08-01",
                    "end_date": "2026-08-21",
                },
                "data": [
                    {
                        "date": "2026-08-01",
                        "total_revenue": 150000.00,
                        "net_revenue": 140000.00,
                        "total_profit": 25000.00,
                    }
                ],
                "total": 21,
            }
        }

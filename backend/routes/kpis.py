"""KPI endpoints for executive dashboard."""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()


class KPIResponse(BaseModel):
    """KPI response model."""
    total_revenue: float
    gross_profit: float
    profit_margin: float
    total_orders: int
    avg_order_value: float
    return_rate: float
    cancellation_rate: float
    ads_spend: float
    roas: float
    acos: float


@router.get("/kpis")
async def get_kpis(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    platform: Optional[str] = Query(None, description="Platform filter"),
    warehouse: Optional[str] = Query(None, description="Warehouse filter"),
) -> dict:
    """
    Get KPIs for the executive dashboard.

    Filters:
    - date range (start_date, end_date)
    - platform (amazon, flipkart, blinkit, myntra, jiomart)
    - warehouse
    """
    # TODO: Integrate with MetricsEngine and agents
    # This is a placeholder that returns sample structure
    return {
        "status": "success",
        "data": {
            "total_revenue": 1250000,
            "gross_profit": 375000,
            "profit_margin": 30.0,
            "total_orders": 2500,
            "avg_order_value": 500,
            "return_rate": 8.5,
            "cancellation_rate": 5.2,
            "ads_spend": 50000,
            "roas": 15.0,
            "acos": 6.67,
            "timestamp": datetime.now().isoformat(),
        }
    }

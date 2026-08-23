from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, Any, Dict, List
from decimal import Decimal


class DateRange(BaseModel):
    """Date range specification."""

    start_date: date
    end_date: date


class PaginationParams(BaseModel):
    """Pagination parameters."""

    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)


class ApiResponse(BaseModel):
    """Standard API response wrapper."""

    success: bool = True
    data: Optional[Any] = None
    error: Optional[str] = None
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {},
                "timestamp": "2026-08-23T12:00:00",
            }
        }


class KpiMetrics(BaseModel):
    """Standard KPI metrics."""

    total_revenue: Decimal
    net_revenue: Decimal
    total_profit: Decimal
    profit_margin_pct: Optional[Decimal] = None
    units_sold: int
    orders: int
    ad_spend: Decimal
    roas: Optional[Decimal] = None
    acos_pct: Optional[Decimal] = None
    return_rate_pct: Optional[Decimal] = None
    cancellation_rate_pct: Optional[Decimal] = None
    organic_sales: Decimal
    ad_attributed_sales: Decimal

    class Config:
        json_schema_extra = {
            "example": {
                "total_revenue": 4250000.00,
                "net_revenue": 4050000.00,
                "total_profit": 820000.00,
                "profit_margin_pct": 20.25,
                "units_sold": 15000,
                "orders": 1200,
                "ad_spend": 450000.00,
                "roas": 3.2,
                "acos_pct": 31.25,
                "return_rate_pct": 3.5,
                "cancellation_rate_pct": 2.1,
                "organic_sales": 3200000.00,
                "ad_attributed_sales": 850000.00,
            }
        }

from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal


class PlatformMetric(BaseModel):
    """Single platform metrics."""

    platform_id: str
    platform_name: str
    revenue: Decimal
    units_sold: int
    orders: int
    ad_spend: Decimal
    roas: Optional[Decimal] = None
    acos_pct: Optional[Decimal] = None
    contribution: Decimal
    margin: Optional[Decimal] = None
    profit_margin_pct: Optional[Decimal] = None
    units_returned: int
    units_cancelled: int
    return_rate_pct: Optional[Decimal] = None

    class Config:
        json_schema_extra = {
            "example": {
                "platform_id": "AMZ",
                "platform_name": "Amazon",
                "revenue": 1000000.00,
                "units_sold": 5000,
                "orders": 400,
                "ad_spend": 300000.00,
                "roas": 2.5,
                "acos_pct": 40.0,
                "contribution": 200000.00,
                "margin": 20.0,
                "profit_margin_pct": 20.0,
                "units_returned": 150,
                "units_cancelled": 50,
                "return_rate_pct": 3.0,
            }
        }


class PlatformPerformanceResponse(BaseModel):
    """Response for platform performance."""

    platforms: List[PlatformMetric]
    total: int

    class Config:
        json_schema_extra = {
            "example": {
                "platforms": [
                    {
                        "platform_id": "AMZ",
                        "platform_name": "Amazon",
                        "revenue": 1000000.00,
                    }
                ],
                "total": 5,
            }
        }

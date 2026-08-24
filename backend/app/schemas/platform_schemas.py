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


class PlatformProfitability(BaseModel):
    """Profitability metrics for a platform."""

    platform_id: str
    platform_name: str
    revenue: Decimal
    total_cost: Decimal
    gross_profit: Decimal
    profit_margin_pct: Optional[Decimal] = None
    contribution_inr: Decimal
    ad_spend: Decimal
    ad_roi: Optional[Decimal] = None
    net_profit: Optional[Decimal] = None
    profitability_ratio: Optional[Decimal] = None

    class Config:
        json_schema_extra = {
            "example": {
                "platform_id": "AMZ",
                "platform_name": "Amazon",
                "revenue": 1000000.00,
                "total_cost": 800000.00,
                "gross_profit": 200000.00,
                "profit_margin_pct": 20.0,
                "contribution_inr": 200000.00,
                "ad_spend": 300000.00,
                "ad_roi": 2.33,
                "net_profit": 150000.00,
                "profitability_ratio": 0.20,
            }
        }


class PlatformProfitabilityResponse(BaseModel):
    """Response for platform profitability analysis."""

    platforms: List[PlatformProfitability]
    total: int
    total_revenue: Decimal
    total_contribution: Decimal
    total_ad_spend: Decimal
    avg_profit_margin: Optional[Decimal] = None

    class Config:
        json_schema_extra = {
            "example": {
                "platforms": [],
                "total": 5,
                "total_revenue": 1800000.00,
                "total_contribution": 450000.00,
                "total_ad_spend": 50000.00,
                "avg_profit_margin": 25.0,
            }
        }


class PlatformAdvertising(BaseModel):
    """Advertising metrics for a platform."""

    platform_id: str
    platform_name: str
    ad_spend: Decimal
    attributed_sales: Decimal
    attributed_orders: int
    attributed_units: int
    roas: Optional[Decimal] = None
    acos_pct: Optional[Decimal] = None
    organic_sales: Decimal
    organic_share_pct: Optional[Decimal] = None
    organic_orders: int
    ctr: Optional[Decimal] = None
    avg_cpc: Optional[Decimal] = None

    class Config:
        json_schema_extra = {
            "example": {
                "platform_id": "AMZ",
                "platform_name": "Amazon",
                "ad_spend": 300000.00,
                "attributed_sales": 750000.00,
                "attributed_orders": 1500,
                "attributed_units": 3000,
                "roas": 2.5,
                "acos_pct": 40.0,
                "organic_sales": 250000.00,
                "organic_share_pct": 25.0,
                "organic_orders": 500,
                "ctr": 5.0,
                "avg_cpc": 12.0,
            }
        }


class PlatformAdvertisingResponse(BaseModel):
    """Response for platform advertising analysis."""

    platforms: List[PlatformAdvertising]
    total: int
    total_ad_spend: Decimal
    total_attributed_sales: Decimal
    overall_roas: Optional[Decimal] = None
    overall_acos: Optional[Decimal] = None
    organic_vs_paid_ratio: Optional[Decimal] = None

    class Config:
        json_schema_extra = {
            "example": {
                "platforms": [],
                "total": 5,
                "total_ad_spend": 50000.00,
                "total_attributed_sales": 750000.00,
                "overall_roas": 15.0,
                "overall_acos": 6.67,
                "organic_vs_paid_ratio": 0.25,
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

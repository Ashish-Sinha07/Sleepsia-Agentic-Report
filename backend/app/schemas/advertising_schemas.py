from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal


class AdvertisingPlatformMetric(BaseModel):
    """Advertising performance for a single platform."""

    platform_id: str
    platform_name: str
    impressions: int
    clicks: int
    orders: int
    ad_spend: Decimal
    attributed_sales: Decimal
    roas: Optional[Decimal] = None
    ctr_pct: Optional[Decimal] = None
    acos_pct: Optional[Decimal] = None


class AdvertisingSummary(BaseModel):
    """Aggregate advertising performance across all platforms."""

    impressions: int
    clicks: int
    orders: int
    ad_spend: Decimal
    attributed_sales: Decimal
    roas: Optional[Decimal] = None
    ctr_pct: Optional[Decimal] = None
    acos_pct: Optional[Decimal] = None


class AdvertisingResponse(BaseModel):
    """Response for the advertising analysis endpoint."""

    summary: AdvertisingSummary
    platforms: List[AdvertisingPlatformMetric]

    class Config:
        json_schema_extra = {
            "example": {
                "summary": {
                    "impressions": 735764,
                    "clicks": 32450,
                    "orders": 2458,
                    "ad_spend": 603699.73,
                    "attributed_sales": 2744179.72,
                    "roas": 4.55,
                    "ctr_pct": 4.41,
                    "acos_pct": 22.0,
                },
                "platforms": [],
            }
        }

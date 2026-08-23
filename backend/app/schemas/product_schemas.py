from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal


class ProductMetric(BaseModel):
    """Single product metrics."""

    sku: str
    product_name: str
    platform_id: Optional[str] = None
    platform: Optional[str] = None
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
    ad_share_pct: Optional[Decimal] = None

    class Config:
        json_schema_extra = {
            "example": {
                "sku": "SLP-1001",
                "product_name": "Contour Pillow",
                "revenue": 425000.00,
                "units_sold": 1000,
                "profit_margin_pct": 22.5,
                "roas": 3.2,
            }
        }


class ProductPerformanceResponse(BaseModel):
    """Response for product performance."""

    products: List[ProductMetric]
    total: int

    class Config:
        json_schema_extra = {
            "example": {
                "products": [
                    {
                        "sku": "SLP-1001",
                        "product_name": "Contour Pillow",
                        "revenue": 425000.00,
                    }
                ],
                "total": 45,
            }
        }


class TopProductsResponse(BaseModel):
    """Response for top/bottom products."""

    products: List[ProductMetric]
    total: int
    sort_by: str
    limit: int

    class Config:
        json_schema_extra = {
            "example": {
                "products": [],
                "total": 45,
                "sort_by": "revenue",
                "limit": 10,
            }
        }

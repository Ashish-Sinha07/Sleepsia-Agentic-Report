from pydantic import BaseModel
from datetime import date
from typing import List, Optional
from decimal import Decimal


class InventoryItem(BaseModel):
    """Single inventory item."""

    warehouse_id: str
    warehouse_name: str
    sku: str
    product_name: str
    closing_stock: int
    avg_daily_demand_7d: int
    days_of_cover: Optional[Decimal] = None
    reorder_point: int
    recommended_reorder_qty: int
    stock_status: str

    class Config:
        json_schema_extra = {
            "example": {
                "warehouse_id": "WH-NCR",
                "warehouse_name": "Delhi NCR Warehouse",
                "sku": "SLP-1001",
                "product_name": "Contour Pillow",
                "closing_stock": 500,
                "avg_daily_demand_7d": 10,
                "days_of_cover": 50.0,
                "stock_status": "Healthy",
            }
        }


class InventoryListResponse(BaseModel):
    """Response for inventory list."""

    inventory: List[InventoryItem]
    total: int

    class Config:
        json_schema_extra = {
            "example": {
                "inventory": [],
                "total": 250,
            }
        }

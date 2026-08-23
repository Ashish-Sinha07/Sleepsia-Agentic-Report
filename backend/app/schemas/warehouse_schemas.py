from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal


class WarehouseInfo(BaseModel):
    """Warehouse information and status."""

    warehouse_id: str
    warehouse_name: str
    region: str
    zone: str
    city: str
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    totalInventory: int
    total_stock_units: int
    healthy_skus: int
    low_stock_skus: int
    lowStockSkus: Optional[int] = None
    critical_skus: int
    stockout_skus: int
    stockoutSkus: Optional[int] = None
    warehouse_health: str
    health_status: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "warehouse_id": "WH-NCR",
                "warehouse_name": "Delhi NCR Warehouse",
                "region": "Delhi NCR",
                "city": "Gurugram",
                "latitude": 28.4595,
                "longitude": 77.0266,
                "totalInventory": 24520,
                "healthy_skus": 120,
                "low_stock_skus": 8,
                "stockout_skus": 2,
                "warehouse_health": "At Risk",
            }
        }


class WarehouseListResponse(BaseModel):
    """Response for warehouses list."""

    warehouses: List[WarehouseInfo]
    total: int

    class Config:
        json_schema_extra = {
            "example": {
                "warehouses": [],
                "total": 5,
            }
        }

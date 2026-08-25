from pydantic import BaseModel
from datetime import date
from typing import List, Optional


class Alert(BaseModel):
    """Alert item."""

    alert_id: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    alert_type: str
    entity: str  # SKU
    product_name: Optional[str] = None
    warehouse: Optional[str] = None
    region: Optional[str] = None
    metric: str
    current_value: int
    threshold: int
    gap: int
    avg_daily_demand: int
    days_of_cover: float
    recommended_reorder_qty: int = 0
    stock_status: Optional[str] = None
    recommendation: str
    created_at: date

    class Config:
        json_schema_extra = {
            "example": {
                "alert_id": "ALR-001",
                "severity": "CRITICAL",
                "alert_type": "Replenishment",
                "entity": "SLP-1001",
                "warehouse": "WAR-001",
                "region": "Mumbai",
                "metric": "Stock",
                "current_value": 9,
                "threshold": 20,
                "gap": -11,
                "avg_daily_demand": 5,
                "days_of_cover": 1.8,
                "stock_status": "Low Stock",
                "recommendation": "Create replenishment order immediately",
                "created_at": "2024-08-21"
            }
        }


class AlertsResponse(BaseModel):
    """Response for alerts."""

    alerts: List[Alert]
    total: int
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0

    class Config:
        json_schema_extra = {
            "example": {
                "alerts": [],
                "total": 0,
                "critical_count": 2,
                "high_count": 3,
                "medium_count": 1,
            }
        }

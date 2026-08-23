from pydantic import BaseModel
from datetime import date
from typing import List, Optional


class Alert(BaseModel):
    """Alert item."""

    alert_id: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    alert_type: str
    entity: str
    platform: Optional[str] = None
    metric: str
    current_value: str
    threshold: str
    recommendation: str
    created_at: date

    class Config:
        json_schema_extra = {
            "example": {
                "alert_id": "ALR-001",
                "severity": "CRITICAL",
                "alert_type": "Stockout",
                "entity": "SLP-1001",
                "platform": "Gurgaon",
                "metric": "Stock",
                "current_value": "0",
                "recommendation": "Replenish immediately",
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

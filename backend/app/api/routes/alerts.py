from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from app.database import get_db
from app.services.alert_service import AlertService
from app.schemas.alert_schemas import AlertsResponse
from app.api.dependencies import get_date_range

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("", response_model=AlertsResponse)
async def get_alerts(
    db: Session = Depends(get_db),
    date_range: tuple[date, date] = Depends(get_date_range),
    priority: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
):
    """Get active alerts within the selected date range."""
    start_date, end_date = date_range
    return AlertService.get_alerts(db, start_date, end_date, priority, limit)

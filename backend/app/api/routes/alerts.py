from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from backend.app.database import get_db
from backend.app.services.alert_service import AlertService
from backend.app.schemas.alert_schemas import AlertsResponse

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("", response_model=AlertsResponse)
async def get_alerts(
    db: Session = Depends(get_db),
    filter_date: Optional[date] = Query(None),
    priority: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
):
    """Get active alerts."""
    return AlertService.get_alerts(db, filter_date, priority, limit)

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date, timedelta
from typing import Optional
from app.database import get_db
from app.config import settings
from app.services.kpi_service import KpiService
from app.schemas.kpi_schemas import KpiResponse, DailyKpisResponse
from app.api.dependencies import get_date_range

router = APIRouter(prefix="/kpis", tags=["KPIs"])


@router.get("", response_model=KpiResponse)
async def get_kpis(
    db: Session = Depends(get_db),
    date_range: tuple[date, date] = Depends(get_date_range),
    platform_id: Optional[str] = Query(None),
):
    """Get aggregate KPIs for selected period."""
    start_date, end_date = date_range
    return KpiService.get_daily_kpis(db, start_date, end_date, platform_id)


@router.get("/by-date", response_model=DailyKpisResponse)
async def get_kpis_by_date(
    db: Session = Depends(get_db),
    date_range: tuple[date, date] = Depends(get_date_range),
):
    """Get KPIs for each day in the range."""
    start_date, end_date = date_range
    return KpiService.get_daily_kpis_timeseries(db, start_date, end_date)

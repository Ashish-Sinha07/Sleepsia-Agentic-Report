from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from app.database import get_db
from app.services.advertising_service import AdvertisingService
from app.schemas.advertising_schemas import AdvertisingResponse
from app.api.dependencies import get_date_range

router = APIRouter(prefix="/advertising", tags=["Advertising"])


@router.get("", response_model=AdvertisingResponse)
async def get_advertising(
    db: Session = Depends(get_db),
    date_range: tuple[date, date] = Depends(get_date_range),
    platform_id: Optional[str] = Query(None),
):
    """Get advertising performance for the selected period, by platform."""
    start_date, end_date = date_range
    return AdvertisingService.get_advertising_performance(
        db, start_date, end_date, platform_id
    )

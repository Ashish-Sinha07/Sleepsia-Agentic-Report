from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from app.database import get_db
from app.services.platform_service import PlatformService
from app.schemas.platform_schemas import PlatformPerformanceResponse
from app.api.dependencies import get_date_range

router = APIRouter(prefix="/platform-performance", tags=["Platforms"])


@router.get("", response_model=PlatformPerformanceResponse)
async def get_platform_performance(
    db: Session = Depends(get_db),
    date_range: tuple[date, date] = Depends(get_date_range),
    platform_id: Optional[str] = Query(None),
):
    """Get performance metrics for all or specific platforms."""
    start_date, end_date = date_range
    return PlatformService.get_platform_performance(db, start_date, end_date, platform_id)

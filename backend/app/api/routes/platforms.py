from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from backend.app.database import get_db
from backend.app.services.platform_service import PlatformService
from backend.app.schemas.platform_schemas import (
    PlatformPerformanceResponse,
    PlatformProfitabilityResponse,
    PlatformAdvertisingResponse,
)
from backend.app.api.dependencies import get_date_range

router = APIRouter(prefix="/platform-performance", tags=["Platforms"])


@router.get("", response_model=PlatformPerformanceResponse)
async def get_platform_performance(
    db: Session = Depends(get_db),
    date_range: tuple[date, date] = Depends(get_date_range),
    platform_id: Optional[str] = Query(None),
):
    """
    Get comprehensive performance metrics for all or specific platforms.

    Includes:
    - Revenue and units sold
    - Orders and order value analysis
    - Advertising metrics (ROAS, ACOS)
    - Contribution and profit margins
    - Returns and cancellations
    """
    start_date, end_date = date_range
    return PlatformService.get_platform_performance(db, start_date, end_date, platform_id)


@router.get("/profitability", response_model=PlatformProfitabilityResponse)
async def get_platform_profitability(
    db: Session = Depends(get_db),
    date_range: tuple[date, date] = Depends(get_date_range),
    platform_id: Optional[str] = Query(None),
):
    """
    Get detailed profitability analysis by platform.

    Includes:
    - Revenue and total costs (COGS + platform fees)
    - Gross profit and net profit
    - Profit margins
    - Advertising ROI (contribution / ad spend)
    - Profitability ratios
    - Platform-wise contribution analysis
    """
    start_date, end_date = date_range
    return PlatformService.get_platform_profitability(db, start_date, end_date, platform_id)


@router.get("/advertising", response_model=PlatformAdvertisingResponse)
async def get_platform_advertising(
    db: Session = Depends(get_db),
    date_range: tuple[date, date] = Depends(get_date_range),
    platform_id: Optional[str] = Query(None),
):
    """
    Get detailed advertising performance analysis by platform.

    Includes:
    - Advertising spend and attributed sales
    - ROAS (Return on Ad Spend) and ACOS (Advertising Cost of Sale)
    - Attributed orders and units
    - Organic vs paid sales comparison
    - Organic market share by platform
    - Average CPC and CTR metrics
    """
    start_date, end_date = date_range
    return PlatformService.get_platform_advertising(db, start_date, end_date, platform_id)

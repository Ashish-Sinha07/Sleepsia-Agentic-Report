from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date, timedelta
from typing import Optional
import logging

from backend.app.database import get_db
from backend.app.config import settings
from backend.app.services.kpi_service import KpiService
from backend.app.services.kpi_orchestrator import KpiOrchestrator
from backend.app.schemas.kpi_schemas import KpiResponse, DailyKpisResponse
from backend.app.schemas.common import ApiResponse
from backend.app.api.dependencies import get_date_range

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/kpis", tags=["KPIs"])


@router.get("", response_model=None)
async def get_kpis(
    db: Session = Depends(get_db),
    date_range: tuple[date, date] = Depends(get_date_range),
    platform_id: Optional[str] = Query(None),
):
    """
    Get aggregate KPIs for selected period with optional insights.

    Features:
    - Database query with date/platform filtering
    - Data validation against business rules
    - Metric calculation and analysis
    - Insight generation
    - Recommendation generation
    - Executive summary

    Query Parameters:
    - start_date: Period start date (YYYY-MM-DD)
    - end_date: Period end date (YYYY-MM-DD)
    - platform: Optional platform filter (amazon, flipkart, blinkit, myntra, jiomart)
    - include_insights: Whether to generate insights and recommendations (default: true)

    Returns:
    - period: Date range
    - kpis: Aggregated KPI metrics
    - metrics_analysis: Detailed metric analysis
    - validation: Data validation results
    - insights: Generated business insights
    - recommendations: Recommended actions
    - summary: Executive summary
    """
    start_date, end_date = date_range
    return KpiService.get_daily_kpis(db, start_date, end_date, platform_id)

    try:
        if include_insights:
            # Use orchestrator for full analysis
            logger.info(f"Get KPIs with insights: {start_date} to {end_date}, platform={platform}")
            orchestrator = KpiOrchestrator(db)
            result = orchestrator.get_kpis_with_insights(start_date, end_date, platform)
            return result
        else:
            # Use simple KpiService for basic KPIs only
            logger.info(f"Get basic KPIs: {start_date} to {end_date}, platform={platform}")
            return KpiService.get_daily_kpis(db, start_date, end_date, platform)

    except Exception as e:
        logger.error(f"Error retrieving KPIs: {str(e)}", exc_info=True)
        raise


@router.get("/by-date", response_model=dict)
async def get_kpis_by_date(
    db: Session = Depends(get_db),
    date_range: tuple[date, date] = Depends(get_date_range),
    include_trends: bool = Query(True, description="Include trend analysis"),
):
    """
    Get KPIs for each day in the range with optional trend analysis.

    Features:
    - Daily KPI data from database
    - Trend analysis across days
    - Revenue/profit/order trends
    - Trend direction and statistics

    Query Parameters:
    - start_date: Period start date (YYYY-MM-DD)
    - end_date: Period end date (YYYY-MM-DD)
    - include_trends: Whether to include trend analysis (default: true)

    Returns:
    - period: Date range
    - daily_data: Array of daily KPI data points
    - trend_analysis: Analysis of trends across period
    - total_days: Number of days in period
    """
    start_date, end_date = date_range

    try:
        if include_trends:
            # Use orchestrator for trend analysis
            logger.info(f"Get daily KPIs with trends: {start_date} to {end_date}")
            orchestrator = KpiOrchestrator(db)
            result = orchestrator.get_daily_kpis_with_analysis(start_date, end_date)
            return result
        else:
            # Use simple KpiService for daily KPIs only
            logger.info(f"Get basic daily KPIs: {start_date} to {end_date}")
            return KpiService.get_daily_kpis_timeseries(db, start_date, end_date)

    except Exception as e:
        logger.error(f"Error retrieving daily KPIs: {str(e)}", exc_info=True)
        raise


@router.get("/health", response_model=ApiResponse)
async def kpi_health_check(db: Session = Depends(get_db)):
    """
    Health check for KPI service.

    Validates:
    - Database connectivity
    - Required tables exist
    - Sample data retrievable
    """
    try:
        from sqlalchemy import text

        # Test database connection
        db.execute(text("SELECT 1"))

        # Test KPI view exists
        db.execute(text("SELECT 1 FROM vw_daily_kpi_summary LIMIT 1"))

        logger.info("KPI service health check passed")
        return ApiResponse(
            success=True,
            data={
                "service": "kpi",
                "status": "healthy",
                "database": "connected",
                "tables": "available",
            },
        )

    except Exception as e:
        logger.error(f"KPI health check failed: {str(e)}")
        return ApiResponse(
            success=False,
            error=str(e),
            error_code="kpi_health_check_failed",
        )

from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from decimal import Decimal
from app.schemas.platform_schemas import PlatformPerformanceResponse, PlatformMetric
from app.schemas.common import DateRange


class PlatformService:
    """Service for platform analysis."""

    @staticmethod
    def get_platform_performance(
        db: Session,
        start_date: date,
        end_date: date,
        platform_id: Optional[str] = None,
    ) -> PlatformPerformanceResponse:
        """Get performance metrics for all or specific platforms."""
        query = """
        SELECT
            platform_id,
            platform,
            COALESCE(SUM(gross_sales), 0) as gross_sales,
            COALESCE(SUM(net_sales), 0) as net_sales,
            COALESCE(SUM(units_sold), 0) as units_sold,
            COALESCE(SUM(orders), 0) as orders,
            COALESCE(SUM(ad_spend), 0) as ad_spend,
            COALESCE(AVG(roas), NULL) as avg_roas,
            COALESCE(AVG(acos_pct), NULL) as avg_acos,
            COALESCE(SUM(contribution_inr), 0) as contribution,
            COALESCE(AVG(profit_margin_pct), NULL) as profit_margin,
            COALESCE(SUM(units_returned), 0) as units_returned,
            COALESCE(SUM(units_cancelled), 0) as units_cancelled
        FROM vw_product_platform_daily
        WHERE date BETWEEN :start_date AND :end_date
        """

        params = {"start_date": start_date, "end_date": end_date}

        if platform_id:
            query += " AND platform_id = :platform_id"
            params["platform_id"] = platform_id

        query += " GROUP BY platform_id, platform ORDER BY net_sales DESC"

        results = db.execute(text(query), params).fetchall()

        platforms = []
        for row in results:
            units_sold = row[4] or 0
            orders = row[5] or 0
            ad_spend = row[6] or Decimal(0)
            ad_sales = Decimal(0)  # Will calculate from revenue if needed

            # Calculate return rate
            return_rate = None
            if units_sold > 0 and row[11]:
                return_rate = (row[11] / units_sold) * 100

            metric = PlatformMetric(
                platform_id=row[0],
                platform_name=row[1],
                revenue=row[3] or Decimal(0),
                units_sold=units_sold,
                orders=orders,
                ad_spend=ad_spend,
                roas=row[7],
                acos_pct=row[8],
                contribution=row[9] or Decimal(0),
                profit_margin_pct=row[10],
                units_returned=row[11] or 0,
                units_cancelled=row[12] or 0,
                return_rate_pct=return_rate,
                margin=row[10],  # For frontend compatibility
            )
            platforms.append(metric)

        return PlatformPerformanceResponse(
            platforms=platforms,
            total=len(platforms),
        )

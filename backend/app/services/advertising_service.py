from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from decimal import Decimal
from app.schemas.advertising_schemas import (
    AdvertisingResponse,
    AdvertisingSummary,
    AdvertisingPlatformMetric,
)


class AdvertisingService:
    """Service for advertising performance analysis."""

    @staticmethod
    def get_advertising_performance(
        db: Session,
        start_date: date,
        end_date: date,
        platform_id: Optional[str] = None,
    ) -> AdvertisingResponse:
        """Get advertising performance aggregated by platform, plus overall totals."""
        query = """
        SELECT
            platform_id,
            platform,
            COALESCE(SUM(impressions), 0) as impressions,
            COALESCE(SUM(clicks), 0) as clicks,
            COALESCE(SUM(attributed_orders), 0) as orders,
            COALESCE(SUM(ad_spend), 0) as ad_spend,
            COALESCE(SUM(ad_attributed_sales), 0) as attributed_sales
        FROM vw_product_platform_daily
        WHERE date BETWEEN :start_date AND :end_date
        """

        params = {"start_date": start_date, "end_date": end_date}

        if platform_id:
            query += " AND platform_id = :platform_id"
            params["platform_id"] = platform_id

        query += " GROUP BY platform_id, platform ORDER BY ad_spend DESC"

        results = db.execute(text(query), params).fetchall()

        platforms = []
        total_impressions = 0
        total_clicks = 0
        total_orders = 0
        total_ad_spend = Decimal(0)
        total_attributed_sales = Decimal(0)

        for row in results:
            impressions = row[2] or 0
            clicks = row[3] or 0
            orders = row[4] or 0
            ad_spend = row[5] or Decimal(0)
            attributed_sales = row[6] or Decimal(0)

            roas = (attributed_sales / ad_spend) if ad_spend and ad_spend > 0 else None
            ctr_pct = (Decimal(clicks) / Decimal(impressions) * 100) if impressions and impressions > 0 else None
            acos_pct = (ad_spend / attributed_sales * 100) if attributed_sales and attributed_sales > 0 else None

            platforms.append(
                AdvertisingPlatformMetric(
                    platform_id=row[0],
                    platform_name=row[1],
                    impressions=impressions,
                    clicks=clicks,
                    orders=orders,
                    ad_spend=ad_spend,
                    attributed_sales=attributed_sales,
                    roas=roas,
                    ctr_pct=ctr_pct,
                    acos_pct=acos_pct,
                )
            )

            total_impressions += impressions
            total_clicks += clicks
            total_orders += orders
            total_ad_spend += ad_spend
            total_attributed_sales += attributed_sales

        summary = AdvertisingSummary(
            impressions=total_impressions,
            clicks=total_clicks,
            orders=total_orders,
            ad_spend=total_ad_spend,
            attributed_sales=total_attributed_sales,
            roas=(total_attributed_sales / total_ad_spend) if total_ad_spend > 0 else None,
            ctr_pct=(Decimal(total_clicks) / Decimal(total_impressions) * 100) if total_impressions > 0 else None,
            acos_pct=(total_ad_spend / total_attributed_sales * 100) if total_attributed_sales > 0 else None,
        )

        return AdvertisingResponse(summary=summary, platforms=platforms)

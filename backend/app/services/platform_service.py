from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from decimal import Decimal
from app.schemas.platform_schemas import (
    PlatformPerformanceResponse,
    PlatformMetric,
    PlatformProfitabilityResponse,
    PlatformProfitability,
    PlatformAdvertisingResponse,
    PlatformAdvertising,
)
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

    @staticmethod
    def get_platform_profitability(
        db: Session,
        start_date: date,
        end_date: date,
        platform_id: Optional[str] = None,
    ) -> PlatformProfitabilityResponse:
        """Get profitability metrics by platform."""
        query = """
        SELECT
            platform_id,
            platform,
            COALESCE(SUM(net_sales), 0) as net_sales,
            COALESCE(SUM(cogs), 0) as cogs,
            COALESCE(SUM(platform_fees), 0) as platform_fees,
            COALESCE(SUM(contribution_inr), 0) as contribution,
            COALESCE(SUM(ad_spend), 0) as ad_spend,
            COALESCE(AVG(profit_margin_pct), NULL) as profit_margin,
            COALESCE(SUM(gross_sales), 0) as gross_sales,
            COALESCE(SUM(ad_spend), 0) as total_ad_cost
        FROM vw_product_platform_daily
        WHERE date BETWEEN :start_date AND :end_date
        """

        params = {"start_date": start_date, "end_date": end_date}

        if platform_id:
            query += " AND platform_id = :platform_id"
            params["platform_id"] = platform_id

        query += " GROUP BY platform_id, platform ORDER BY contribution DESC"

        results = db.execute(text(query), params).fetchall()

        platforms = []
        total_revenue = Decimal(0)
        total_contribution = Decimal(0)
        total_ad_spend = Decimal(0)
        profit_margins = []

        for row in results:
            revenue = row[2] or Decimal(0)
            total_cost = (row[3] or Decimal(0)) + (row[4] or Decimal(0))
            contribution = row[5] or Decimal(0)
            ad_spend = row[6] or Decimal(0)
            profit_margin = row[7]
            gross_profit = revenue - total_cost

            # Calculate ad ROI
            ad_roi = None
            if ad_spend and ad_spend > 0:
                ad_roi = round(contribution / ad_spend, 2)

            # Calculate net profit (contribution - ad spend)
            net_profit = contribution - ad_spend

            # Calculate profitability ratio
            profitability_ratio = None
            if revenue and revenue > 0:
                profitability_ratio = round(contribution / revenue, 4)

            metric = PlatformProfitability(
                platform_id=row[0],
                platform_name=row[1],
                revenue=revenue,
                total_cost=total_cost,
                gross_profit=gross_profit,
                profit_margin_pct=profit_margin,
                contribution_inr=contribution,
                ad_spend=ad_spend,
                ad_roi=ad_roi,
                net_profit=net_profit,
                profitability_ratio=profitability_ratio,
            )
            platforms.append(metric)

            total_revenue += revenue
            total_contribution += contribution
            total_ad_spend += ad_spend
            if profit_margin:
                profit_margins.append(profit_margin)

        # Calculate average profit margin
        avg_profit_margin = None
        if profit_margins:
            avg_profit_margin = round(sum(profit_margins) / len(profit_margins), 2)

        return PlatformProfitabilityResponse(
            platforms=platforms,
            total=len(platforms),
            total_revenue=total_revenue,
            total_contribution=total_contribution,
            total_ad_spend=total_ad_spend,
            avg_profit_margin=avg_profit_margin,
        )

    @staticmethod
    def get_platform_advertising(
        db: Session,
        start_date: date,
        end_date: date,
        platform_id: Optional[str] = None,
    ) -> PlatformAdvertisingResponse:
        """Get advertising metrics by platform."""
        query = """
        SELECT
            platform_id,
            platform,
            COALESCE(SUM(ad_spend), 0) as ad_spend,
            COALESCE(SUM(net_sales), 0) as net_sales,
            COALESCE(SUM(orders), 0) as orders,
            COALESCE(SUM(units_sold), 0) as units_sold,
            COALESCE(AVG(roas), NULL) as roas,
            COALESCE(AVG(acos_pct), NULL) as acos,
            COALESCE(SUM(contribution_inr), 0) as contribution,
            COALESCE(AVG(organic_share_pct), NULL) as organic_share
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
        total_ad_spend = Decimal(0)
        total_attributed_sales = Decimal(0)
        overall_roas_list = []

        for row in results:
            ad_spend = row[2] or Decimal(0)
            attributed_sales = row[3] or Decimal(0)
            attributed_orders = row[4] or 0
            attributed_units = row[5] or 0
            roas = row[6]
            acos = row[7]
            organic_share = row[9]

            # Calculate organic sales (assuming organic share is percentage)
            organic_sales = Decimal(0)
            if organic_share and organic_share > 0 and attributed_sales > 0:
                # organic_share is the organic percentage
                total_sales = attributed_sales / ((100 - float(organic_share)) / 100) if organic_share < 100 else attributed_sales
                organic_sales = total_sales - attributed_sales
            else:
                # If no organic share data, estimate from contribution
                organic_sales = (row[8] or Decimal(0)) - attributed_sales
                if organic_sales < 0:
                    organic_sales = Decimal(0)

            # Calculate organic orders (proportional to units)
            organic_orders = 0
            if attributed_units > 0 and attributed_orders > 0:
                organic_orders = int(attributed_orders * (1 - ((100 - float(organic_share)) / 100))) if organic_share else 0

            # Calculate CTR and avg CPC (if data available)
            ctr = None
            avg_cpc = None
            if ad_spend and ad_spend > 0:
                avg_cpc = round(ad_spend / max(attributed_orders, 1), 2)

            # Recalculate organic share percentage
            organic_share_pct = None
            if organic_sales and (organic_sales + attributed_sales) > 0:
                organic_share_pct = round(
                    (organic_sales / (organic_sales + attributed_sales)) * 100, 2
                )

            metric = PlatformAdvertising(
                platform_id=row[0],
                platform_name=row[1],
                ad_spend=ad_spend,
                attributed_sales=attributed_sales,
                attributed_orders=attributed_orders,
                attributed_units=attributed_units,
                roas=roas,
                acos_pct=acos,
                organic_sales=organic_sales,
                organic_share_pct=organic_share_pct,
                organic_orders=organic_orders,
                ctr=ctr,
                avg_cpc=avg_cpc,
            )
            platforms.append(metric)

            total_ad_spend += ad_spend
            total_attributed_sales += attributed_sales
            if roas:
                overall_roas_list.append(roas)

        # Calculate overall ROAS and ACOS
        overall_roas = None
        overall_acos = None
        if total_ad_spend and total_ad_spend > 0:
            overall_roas = round(total_attributed_sales / total_ad_spend, 2)
            overall_acos = round((total_ad_spend / total_attributed_sales) * 100, 2) if total_attributed_sales > 0 else None

        # Calculate organic vs paid ratio
        total_organic_sales = sum(p.organic_sales for p in platforms)
        organic_vs_paid_ratio = None
        if total_attributed_sales and total_attributed_sales > 0 and total_organic_sales > 0:
            organic_vs_paid_ratio = round(total_organic_sales / total_attributed_sales, 2)

        return PlatformAdvertisingResponse(
            platforms=platforms,
            total=len(platforms),
            total_ad_spend=total_ad_spend,
            total_attributed_sales=total_attributed_sales,
            overall_roas=overall_roas,
            overall_acos=overall_acos,
            organic_vs_paid_ratio=organic_vs_paid_ratio,
        )

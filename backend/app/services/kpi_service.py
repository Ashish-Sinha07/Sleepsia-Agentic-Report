from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import date
from typing import Dict, List, Any, Optional
from decimal import Decimal
from backend.app.schemas.kpi_schemas import KpiResponse, DailyKpiResponse, KpiMetrics, DailyKpisResponse
from backend.app.schemas.common import DateRange


class KpiService:
    """Service for KPI calculations and aggregations."""

    @staticmethod
    def get_daily_kpis(
        db: Session,
        start_date: date,
        end_date: date,
        platform_id: Optional[str] = None,
    ) -> KpiResponse:
        """Get aggregated KPIs for date range, optionally filtered by platform.

        Aggregates directly from vw_product_platform_daily (rather than the
        pre-aggregated vw_daily_kpi_summary) so an optional platform filter can
        be applied, and derives ratios from summed totals rather than averaging
        already-computed per-row percentages.
        """
        query = """
        SELECT
            COALESCE(SUM(orders), 0) as total_orders,
            COALESCE(SUM(units_sold), 0) as total_units_sold,
            COALESCE(SUM(gross_sales), 0) as total_gross_sales,
            COALESCE(SUM(discount), 0) as total_discount,
            COALESCE(SUM(net_sales), 0) as total_net_sales,
            COALESCE(SUM(ad_attributed_sales), 0) as total_ad_sales,
            COALESCE(SUM(organic_sales), 0) as total_organic_sales,
            COALESCE(SUM(ad_spend), 0) as total_ad_spend,
            COALESCE(SUM(contribution_inr), 0) as total_contribution,
            COALESCE(SUM(units_returned), 0) as total_units_returned,
            COALESCE(SUM(units_cancelled), 0) as total_units_cancelled
        FROM vw_product_platform_daily
        WHERE date BETWEEN :start_date AND :end_date
        """

        params = {"start_date": start_date, "end_date": end_date}

        if platform_id:
            query += " AND platform_id = :platform_id"
            params["platform_id"] = platform_id

        result = db.execute(text(query), params).fetchone()

        orders = result[0] or 0
        units_sold = result[1] or 0
        total_net_sales = result[4] or Decimal(0)
        ad_sales = result[5] or Decimal(0)
        total_ad_spend = result[7] or Decimal(0)
        total_contribution = result[8] or Decimal(0)
        units_returned = result[9] or 0
        units_cancelled = result[10] or 0

        profit_margin_pct = (
            (total_contribution / total_net_sales) * 100 if total_net_sales > 0 else None
        )
        roas = (ad_sales / total_ad_spend) if total_ad_spend > 0 else None
        acos = (total_ad_spend / ad_sales) * 100 if ad_sales > 0 else None
        return_rate = (Decimal(units_returned) / units_sold) * 100 if units_sold > 0 else None
        cancel_rate = (Decimal(units_cancelled) / orders) * 100 if orders > 0 else None

        kpis = KpiMetrics(
            total_revenue=result[2] or Decimal(0),
            net_revenue=total_net_sales,
            total_profit=total_contribution,
            profit_margin_pct=profit_margin_pct,
            units_sold=units_sold,
            orders=orders,
            ad_spend=total_ad_spend,
            roas=roas,
            acos_pct=acos,
            return_rate_pct=return_rate,
            cancellation_rate_pct=cancel_rate,
            organic_sales=result[6] or Decimal(0),
            ad_attributed_sales=ad_sales,
        )

        return KpiResponse(
            period=DateRange(start_date=start_date, end_date=end_date),
            kpis=kpis,
        )

    @staticmethod
    def get_daily_kpis_timeseries(
        db: Session,
        start_date: date,
        end_date: date,
    ) -> DailyKpisResponse:
        """Get KPIs for each day in the range."""
        query = """
        SELECT
            date,
            total_orders,
            total_units_sold,
            total_net_sales,
            total_gross_sales,
            total_ad_spend,
            total_ad_sales,
            total_contribution,
            overall_profit_margin_pct,
            overall_roas,
            total_units_returned,
            total_units_cancelled
        FROM vw_daily_kpi_summary
        WHERE date BETWEEN :start_date AND :end_date
        ORDER BY date ASC
        """

        results = db.execute(
            text(query),
            {"start_date": start_date, "end_date": end_date},
        ).fetchall()

        data = [
            DailyKpiResponse(
                date=row[0],
                total_revenue=row[4] or Decimal(0),
                net_revenue=row[3] or Decimal(0),
                total_profit=row[7] or Decimal(0),
                profit_margin_pct=row[8],
                units_sold=row[2] or 0,
                orders=row[1] or 0,
                ad_spend=row[5] or Decimal(0),
                roas=row[9],
                total_units_returned=row[10] or 0,
                total_units_cancelled=row[11] or 0,
            )
            for row in results
        ]

        return DailyKpisResponse(
            period=DateRange(start_date=start_date, end_date=end_date),
            data=data,
            total=len(data),
        )

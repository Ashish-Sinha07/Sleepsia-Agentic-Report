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
        """Get aggregated KPIs for date range."""
        query = """
        SELECT
            SUM(total_orders) as total_orders,
            SUM(total_units_sold) as total_units_sold,
            SUM(total_gross_sales) as total_gross_sales,
            SUM(total_discount) as total_discount,
            SUM(total_net_sales) as total_net_sales,
            SUM(total_ad_sales) as total_ad_sales,
            SUM(total_organic_sales) as total_organic_sales,
            SUM(total_ad_spend) as total_ad_spend,
            SUM(total_contribution) as total_contribution,
            SUM(total_units_returned) as total_units_returned,
            SUM(total_units_cancelled) as total_units_cancelled,
            AVG(overall_profit_margin_pct) as overall_profit_margin_pct,
            AVG(overall_roas) as overall_roas
        FROM vw_daily_kpi_summary
        WHERE date BETWEEN :start_date AND :end_date
        """

        result = db.execute(
            text(query),
            {"start_date": start_date, "end_date": end_date},
        ).fetchone()

        if not result or result[0] is None:
            # Return zeros if no data
            kpis = KpiMetrics(
                total_revenue=Decimal(0),
                net_revenue=Decimal(0),
                total_profit=Decimal(0),
                profit_margin_pct=None,
                units_sold=0,
                orders=0,
                ad_spend=Decimal(0),
                roas=None,
                acos_pct=None,
                return_rate_pct=None,
                cancellation_rate_pct=None,
                organic_sales=Decimal(0),
                ad_attributed_sales=Decimal(0),
            )
        else:
            units_sold = result[1] or 0
            ad_sales = result[5] or Decimal(0)

            # Calculate ACOS if we have ad sales
            acos = None
            if ad_sales and ad_sales > 0 and result[7]:  # total_ad_spend
                acos = (result[7] / ad_sales) * 100

            # Calculate return rate
            return_rate = None
            if units_sold and units_sold > 0 and result[9]:  # total_units_returned
                return_rate = (result[9] / units_sold) * 100

            # Calculate cancellation rate
            cancel_rate = None
            orders = result[0] or 0
            if orders and orders > 0 and result[10]:  # total_units_cancelled
                cancel_rate = (result[10] / orders) * 100

            kpis = KpiMetrics(
                total_revenue=result[2] or Decimal(0),
                net_revenue=result[4] or Decimal(0),
                total_profit=result[8] or Decimal(0),
                profit_margin_pct=result[12],
                units_sold=units_sold,
                orders=orders,
                ad_spend=result[7] or Decimal(0),
                roas=result[11],
                acos_pct=acos,
                return_rate_pct=return_rate,
                cancellation_rate_pct=cancel_rate,
                organic_sales=result[6] or Decimal(0),
                ad_attributed_sales=result[5] or Decimal(0),
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

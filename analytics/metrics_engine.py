"""Deterministic business metrics calculation engine."""

from datetime import date, timedelta
from typing import Optional
import pandas as pd
import numpy as np

from analytics.models import (
    ProductMetrics,
    PlatformMetrics,
    DailyMetrics,
    TrendMetrics,
    MetricComparison,
)


class MetricsEngine:
    """Calculate deterministic business metrics from validated data."""

    PROFITABILITY_THRESHOLDS = {
        "healthy": 15.0,
        "at_risk": 0.0,
    }

    @staticmethod
    def calculate_roas(sales: float, ad_spend: float) -> float:
        """Return on Ad Spend = Sales / Ad Spend."""
        return sales / ad_spend if ad_spend > 0 else 0.0

    @staticmethod
    def calculate_acos(ad_spend: float, sales: float) -> float:
        """Advertising Cost of Sale = (Ad Spend / Sales) * 100."""
        return (ad_spend / sales * 100) if sales > 0 else 0.0

    @staticmethod
    def calculate_organic_sales(
        total_sales: float, ad_attributed_sales: float
    ) -> tuple[float, float]:
        """
        Organic sales = Total sales - Ad attributed sales.
        Returns (organic_sales, organic_share_percent).
        """
        organic_sales = total_sales - ad_attributed_sales
        organic_share = (organic_sales / total_sales * 100) if total_sales > 0 else 0.0
        return organic_sales, organic_share

    @staticmethod
    def calculate_return_rate(units_returned: int, units_sold: int) -> float:
        """Return rate % = (Units returned / Units sold) * 100."""
        return (units_returned / units_sold * 100) if units_sold > 0 else 0.0

    @staticmethod
    def calculate_cancellation_rate(units_cancelled: int, units_sold: int) -> float:
        """Cancellation rate % = (Units cancelled / Units sold) * 100."""
        return (units_cancelled / units_sold * 100) if units_sold > 0 else 0.0

    @staticmethod
    def calculate_contribution(
        net_sales: float,
        product_cost: float,
        platform_fee: float,
        shipping_cost: float,
        payment_fee: float,
        other_cost: float,
        refund: float = 0.0,
    ) -> float:
        """
        Contribution = Net Sales - All costs - Refunds.
        This is gross profit after direct variable costs.
        """
        total_costs = (
            product_cost + platform_fee + shipping_cost + payment_fee + other_cost
        )
        contribution = net_sales - total_costs - refund
        return contribution

    @staticmethod
    def calculate_profit_margin(contribution: float, net_sales: float) -> float:
        """Profit margin % = (Contribution / Net Sales) * 100."""
        return (contribution / net_sales * 100) if net_sales > 0 else 0.0

    @staticmethod
    def determine_profitability_status(profit_margin_pct: float) -> str:
        """
        Determine profitability status based on margin.
        - Healthy: >= 15%
        - At Risk: 0% to 14.99%
        - Unprofitable: < 0%
        """
        if profit_margin_pct >= MetricsEngine.PROFITABILITY_THRESHOLDS["healthy"]:
            return "Healthy"
        elif profit_margin_pct >= MetricsEngine.PROFITABILITY_THRESHOLDS["at_risk"]:
            return "At Risk"
        else:
            return "Unprofitable"

    def calculate_product_metrics(
        self,
        sku: str,
        product_name: str,
        units_sold: int,
        gross_sales: float,
        net_sales: float,
        discount: float,
        ad_spend: float,
        ad_attributed_units: int,
        ad_attributed_sales: float,
        product_cost: float,
        platform_fee: float,
        shipping_cost: float,
        payment_fee: float,
        other_cost: float,
        units_returned: int,
        refund_amount: float,
        units_cancelled: int,
    ) -> ProductMetrics:
        """Calculate all metrics for a single product."""
        organic_units = units_sold - ad_attributed_units
        organic_sales, organic_share = self.calculate_organic_sales(
            net_sales, ad_attributed_sales
        )

        roas = self.calculate_roas(ad_attributed_sales, ad_spend)
        acos = self.calculate_acos(ad_spend, ad_attributed_sales)

        return_rate = self.calculate_return_rate(units_returned, units_sold)
        cancellation_rate = self.calculate_cancellation_rate(units_cancelled, units_sold)

        contribution = self.calculate_contribution(
            net_sales,
            product_cost,
            platform_fee,
            shipping_cost,
            payment_fee,
            other_cost,
            refund_amount,
        )
        profit_margin = self.calculate_profit_margin(contribution, net_sales)
        profitability_status = self.determine_profitability_status(profit_margin)

        return ProductMetrics(
            sku=sku,
            product_name=product_name,
            units_sold=units_sold,
            gross_sales_inr=gross_sales,
            net_sales_inr=net_sales,
            discount_inr=discount,
            ad_spend_inr=ad_spend,
            ad_attributed_units=ad_attributed_units,
            ad_attributed_sales_inr=ad_attributed_sales,
            organic_units=organic_units,
            organic_sales_inr=organic_sales,
            organic_share_pct=organic_share,
            roas=roas,
            acos_pct=acos,
            product_cost_inr=product_cost,
            platform_fee_inr=platform_fee,
            shipping_cost_inr=shipping_cost,
            payment_fee_inr=payment_fee,
            other_cost_inr=other_cost,
            total_cost_inr=product_cost + platform_fee + shipping_cost + payment_fee + other_cost,
            units_returned=units_returned,
            refund_amount_inr=refund_amount,
            return_rate_pct=return_rate,
            units_cancelled=units_cancelled,
            cancellation_rate_pct=cancellation_rate,
            contribution_inr=contribution,
            profit_margin_pct=profit_margin,
            profitability_status=profitability_status,
        )

    def calculate_platform_metrics(
        self, product_metrics_list: list[ProductMetrics], platform_id: str, platform_name: str
    ) -> PlatformMetrics:
        """Aggregate product metrics to platform level."""
        if not product_metrics_list:
            return PlatformMetrics(
                platform_id=platform_id,
                platform_name=platform_name,
                total_orders=0,
                total_units_sold=0,
                total_gross_sales_inr=0.0,
                total_net_sales_inr=0.0,
                total_discount_inr=0.0,
                total_ad_spend_inr=0.0,
                total_ad_attributed_units=0,
                total_ad_attributed_sales_inr=0.0,
                total_organic_units=0,
                total_organic_sales_inr=0.0,
                platform_roas=0.0,
                platform_acos_pct=0.0,
                total_product_cost_inr=0.0,
                total_platform_fee_inr=0.0,
                total_shipping_cost_inr=0.0,
                total_payment_fee_inr=0.0,
                total_other_cost_inr=0.0,
                total_cost_inr=0.0,
                total_returns=0,
                total_refund_inr=0.0,
                overall_return_rate_pct=0.0,
                total_cancellations=0,
                overall_cancellation_rate_pct=0.0,
                total_contribution_inr=0.0,
                overall_profit_margin_pct=0.0,
                product_count=0,
            )

        totals = {
            "units_sold": sum(m.units_sold for m in product_metrics_list),
            "gross_sales": sum(m.gross_sales_inr for m in product_metrics_list),
            "net_sales": sum(m.net_sales_inr for m in product_metrics_list),
            "discount": sum(m.discount_inr for m in product_metrics_list),
            "ad_spend": sum(m.ad_spend_inr for m in product_metrics_list),
            "ad_attributed_units": sum(m.ad_attributed_units for m in product_metrics_list),
            "ad_attributed_sales": sum(m.ad_attributed_sales_inr for m in product_metrics_list),
            "organic_units": sum(m.organic_units for m in product_metrics_list),
            "organic_sales": sum(m.organic_sales_inr for m in product_metrics_list),
            "product_cost": sum(m.product_cost_inr for m in product_metrics_list),
            "platform_fee": sum(m.platform_fee_inr for m in product_metrics_list),
            "shipping_cost": sum(m.shipping_cost_inr for m in product_metrics_list),
            "payment_fee": sum(m.payment_fee_inr for m in product_metrics_list),
            "other_cost": sum(m.other_cost_inr for m in product_metrics_list),
            "units_returned": sum(m.units_returned for m in product_metrics_list),
            "refund": sum(m.refund_amount_inr for m in product_metrics_list),
            "units_cancelled": sum(m.units_cancelled for m in product_metrics_list),
            "contribution": sum(m.contribution_inr for m in product_metrics_list),
        }

        total_cost = (
            totals["product_cost"] + totals["platform_fee"] +
            totals["shipping_cost"] + totals["payment_fee"] + totals["other_cost"]
        )

        platform_roas = self.calculate_roas(totals["ad_attributed_sales"], totals["ad_spend"])
        platform_acos = self.calculate_acos(totals["ad_spend"], totals["ad_attributed_sales"])

        return_rate = self.calculate_return_rate(totals["units_returned"], totals["units_sold"])
        cancellation_rate = self.calculate_cancellation_rate(
            totals["units_cancelled"], totals["units_sold"]
        )

        overall_margin = self.calculate_profit_margin(
            totals["contribution"], totals["net_sales"]
        )

        top_product = max(product_metrics_list, key=lambda m: m.net_sales_inr, default=None)

        return PlatformMetrics(
            platform_id=platform_id,
            platform_name=platform_name,
            total_orders=sum(1 for m in product_metrics_list),
            total_units_sold=totals["units_sold"],
            total_gross_sales_inr=totals["gross_sales"],
            total_net_sales_inr=totals["net_sales"],
            total_discount_inr=totals["discount"],
            total_ad_spend_inr=totals["ad_spend"],
            total_ad_attributed_units=totals["ad_attributed_units"],
            total_ad_attributed_sales_inr=totals["ad_attributed_sales"],
            total_organic_units=totals["organic_units"],
            total_organic_sales_inr=totals["organic_sales"],
            platform_roas=platform_roas,
            platform_acos_pct=platform_acos,
            total_product_cost_inr=totals["product_cost"],
            total_platform_fee_inr=totals["platform_fee"],
            total_shipping_cost_inr=totals["shipping_cost"],
            total_payment_fee_inr=totals["payment_fee"],
            total_other_cost_inr=totals["other_cost"],
            total_cost_inr=total_cost,
            total_returns=totals["units_returned"],
            total_refund_inr=totals["refund"],
            overall_return_rate_pct=return_rate,
            total_cancellations=totals["units_cancelled"],
            overall_cancellation_rate_pct=cancellation_rate,
            total_contribution_inr=totals["contribution"],
            overall_profit_margin_pct=overall_margin,
            product_count=len(product_metrics_list),
            top_product_sku=top_product.sku if top_product else None,
            top_product_sales_inr=top_product.net_sales_inr if top_product else None,
        )

    def calculate_daily_metrics(
        self, daily_data: pd.DataFrame
    ) -> DailyMetrics:
        """Calculate daily aggregated metrics."""
        if daily_data.empty:
            return DailyMetrics(
                date=date.today(),
                total_orders=0,
                total_units_sold=0,
                total_gross_sales_inr=0.0,
                total_net_sales_inr=0.0,
                total_ad_spend_inr=0.0,
                total_ad_attributed_units=0,
                total_ad_attributed_sales_inr=0.0,
                total_organic_units=0,
                total_organic_sales_inr=0.0,
                total_cost_inr=0.0,
                total_contribution_inr=0.0,
                overall_profit_margin_pct=0.0,
                total_returns=0,
                total_refund_inr=0.0,
                total_cancellations=0,
            )

        date_val = pd.Timestamp(daily_data.iloc[0]["date"]).date()

        units_sold = daily_data["UnitsSold"].sum()
        ad_attr_units = daily_data["AdAttributedUnits"].sum()
        organic_units = units_sold - ad_attr_units
        net_sales = daily_data["NetSales_INR"].sum()
        ad_attr_sales = daily_data["AdAttributedSales_INR"].sum()
        organic_sales = net_sales - ad_attr_sales

        total_cost = (
            daily_data["ProductCost_INR"].sum() +
            daily_data["PlatformFee_INR"].sum() +
            daily_data["ShippingCost_INR"].sum() +
            daily_data["PaymentFee_INR"].sum() +
            daily_data["OtherVariableCost_INR"].sum()
        )

        contribution = net_sales - total_cost

        return DailyMetrics(
            date=date_val,
            total_orders=daily_data["Orders"].sum(),
            total_units_sold=units_sold,
            total_gross_sales_inr=daily_data["GrossSales_INR"].sum(),
            total_net_sales_inr=net_sales,
            total_ad_spend_inr=daily_data["AdSpend_INR"].sum(),
            total_ad_attributed_units=ad_attr_units,
            total_ad_attributed_sales_inr=ad_attr_sales,
            total_organic_units=organic_units,
            total_organic_sales_inr=organic_sales,
            total_cost_inr=total_cost,
            total_contribution_inr=contribution,
            overall_profit_margin_pct=self.calculate_profit_margin(contribution, net_sales),
            total_returns=0,
            total_refund_inr=0.0,
            total_cancellations=0,
        )

    def calculate_trend(
        self,
        metric_name: str,
        daily_values: list[tuple[date, float]],
        period_start: date,
        period_end: date,
    ) -> TrendMetrics:
        """
        Calculate trend metrics for a given metric over a time period.
        daily_values: List of (date, value) tuples, sorted by date.
        """
        if not daily_values:
            return TrendMetrics(
                metric_name=metric_name,
                period_start=period_start,
                period_end=period_end,
                days=0,
                average_daily=0.0,
                min_daily=0.0,
                max_daily=0.0,
            )

        values = [v[1] for v in daily_values]
        days = len(daily_values)

        avg_daily = np.mean(values)
        min_daily = np.min(values)
        max_daily = np.max(values)

        day_7_avg = None
        if len(values) >= 7:
            day_7_avg = np.mean(values[-7:])

        day_30_avg = None
        if len(values) >= 30:
            day_30_avg = np.mean(values[-30:])

        trend_direction = "stable"
        trend_strength = 0.0

        if len(values) >= 2:
            first_half = np.mean(values[: len(values) // 2])
            second_half = np.mean(values[len(values) // 2 :])

            if second_half > first_half:
                trend_direction = "upward"
                trend_strength = (second_half - first_half) / first_half if first_half > 0 else 0
            elif second_half < first_half:
                trend_direction = "downward"
                trend_strength = (first_half - second_half) / first_half if first_half > 0 else 0

        return TrendMetrics(
            metric_name=metric_name,
            period_start=period_start,
            period_end=period_end,
            days=days,
            average_daily=avg_daily,
            min_daily=min_daily,
            max_daily=max_daily,
            day_7_average=day_7_avg,
            day_30_average=day_30_avg,
            trend_direction=trend_direction,
            trend_strength=trend_strength,
        )

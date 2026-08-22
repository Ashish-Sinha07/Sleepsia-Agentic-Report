"""Report builder - constructs canonical Report objects deterministically."""

import uuid
from datetime import date, datetime
from typing import Optional, List
from analytics.report_models import (
    Report,
    ReportType,
    OverallMetrics,
    ProductSection,
    PlatformSection,
    AdvertisingSection,
    ProfitabilitySection,
    QualitySection,
    Insight,
    Recommendation,
    KeyMetric,
)
from analytics.models import (
    ProductMetrics,
    PlatformMetrics,
    DailyMetrics,
)
from analytics.insight_models import (
    BusinessInsight,
    InsightRecommendationResult,
)


class ReportBuilder:
    """Deterministically constructs Report objects from metrics and analysis."""

    @staticmethod
    def build_product_platform_report(
        report_date: date,
        sku: str,
        product_name: str,
        platform_id: str,
        platform_name: str,
        product_metrics: ProductMetrics,
        insight_result: Optional[InsightRecommendationResult] = None,
    ) -> Report:
        """Build a product × platform daily report."""
        report_id = f"RPT-{uuid.uuid4().hex[:8].upper()}"

        overall_metrics = ReportBuilder._build_overall_metrics(
            report_date,
            product_metrics,
        )

        product_section = ReportBuilder._build_product_section(
            product_metrics,
            insight_result,
        )

        advertising_section = ReportBuilder._build_advertising_section(
            product_metrics,
        )

        profitability_section = ReportBuilder._build_profitability_section(
            [product_metrics],
        )

        quality_section = ReportBuilder._build_quality_section(
            [product_metrics],
        )

        executive_summary = f"Daily report for {product_name} on {platform_name}. "
        if product_metrics.profit_margin_pct < 0:
            executive_summary += "Product is unprofitable. "
        elif product_metrics.profit_margin_pct < 15:
            executive_summary += "Product is at-risk. "
        else:
            executive_summary += f"Healthy margin of {product_metrics.profit_margin_pct:.1f}%. "

        if product_metrics.roas > 0 and product_metrics.roas < 2.0:
            executive_summary += f"ROAS of {product_metrics.roas:.2f}x below target. "

        insights = ReportBuilder._extract_insights(insight_result)
        recommendations = ReportBuilder._extract_recommendations(insight_result)

        return Report(
            report_id=report_id,
            report_date=report_date,
            report_type=ReportType.PRODUCT_PLATFORM_DAILY,
            title=f"{product_name} - {platform_name} - {report_date}",
            executive_summary=executive_summary.strip(),
            overall_metrics=overall_metrics,
            product_sections=[product_section],
            advertising_section=advertising_section,
            profitability_section=profitability_section,
            quality_section=quality_section,
            insights=insights,
            recommendations=recommendations,
        )

    @staticmethod
    def build_product_report(
        report_date: date,
        sku: str,
        product_name: str,
        product_metrics: ProductMetrics,
        insight_result: Optional[InsightRecommendationResult] = None,
    ) -> Report:
        """Build a product daily report."""
        report_id = f"RPT-{uuid.uuid4().hex[:8].upper()}"

        overall_metrics = ReportBuilder._build_overall_metrics(
            report_date,
            product_metrics,
        )

        product_section = ReportBuilder._build_product_section(
            product_metrics,
            insight_result,
        )

        advertising_section = ReportBuilder._build_advertising_section(
            product_metrics,
        )

        profitability_section = ReportBuilder._build_profitability_section(
            [product_metrics],
        )

        quality_section = ReportBuilder._build_quality_section(
            [product_metrics],
        )

        executive_summary = f"Daily report for {product_name}. "
        executive_summary += f"Units sold: {product_metrics.units_sold}, "
        executive_summary += f"Net sales: ₹{product_metrics.net_sales_inr:,.0f}, "
        executive_summary += f"Margin: {product_metrics.profit_margin_pct:.1f}%"

        insights = ReportBuilder._extract_insights(insight_result)
        recommendations = ReportBuilder._extract_recommendations(insight_result)

        return Report(
            report_id=report_id,
            report_date=report_date,
            report_type=ReportType.PRODUCT_DAILY,
            title=f"{product_name} - {report_date}",
            executive_summary=executive_summary,
            overall_metrics=overall_metrics,
            product_sections=[product_section],
            advertising_section=advertising_section,
            profitability_section=profitability_section,
            quality_section=quality_section,
            insights=insights,
            recommendations=recommendations,
        )

    @staticmethod
    def build_platform_report(
        report_date: date,
        platform_metrics: PlatformMetrics,
        product_metrics_list: List[ProductMetrics],
        insight_result: Optional[InsightRecommendationResult] = None,
    ) -> Report:
        """Build a platform daily report."""
        report_id = f"RPT-{uuid.uuid4().hex[:8].upper()}"

        overall_metrics = ReportBuilder._build_overall_metrics_from_platform(
            report_date,
            platform_metrics,
        )

        platform_section = ReportBuilder._build_platform_section(
            platform_metrics,
            insight_result,
        )

        advertising_section = ReportBuilder._build_advertising_section_from_platform(
            platform_metrics,
        )

        profitability_section = ReportBuilder._build_profitability_section(
            product_metrics_list,
        )

        quality_section = ReportBuilder._build_quality_section(
            product_metrics_list,
        )

        executive_summary = f"Platform report for {platform_metrics.platform_name}. "
        executive_summary += f"Products: {platform_metrics.product_count}, "
        executive_summary += f"Net sales: ₹{platform_metrics.total_net_sales_inr:,.0f}, "
        executive_summary += f"Margin: {platform_metrics.overall_profit_margin_pct:.1f}%"

        insights = ReportBuilder._extract_insights(insight_result)
        recommendations = ReportBuilder._extract_recommendations(insight_result)

        return Report(
            report_id=report_id,
            report_date=report_date,
            report_type=ReportType.PLATFORM_DAILY,
            title=f"{platform_metrics.platform_name} - {report_date}",
            executive_summary=executive_summary,
            overall_metrics=overall_metrics,
            platform_sections=[platform_section],
            advertising_section=advertising_section,
            profitability_section=profitability_section,
            quality_section=quality_section,
            insights=insights,
            recommendations=recommendations,
        )

    @staticmethod
    def _build_overall_metrics(
        report_date: date,
        product_metrics: ProductMetrics,
    ) -> OverallMetrics:
        """Build overall metrics section from product metrics."""
        return OverallMetrics(
            report_date=report_date,
            total_orders=1,
            total_units_sold=product_metrics.units_sold,
            total_net_sales_inr=product_metrics.net_sales_inr,
            total_gross_sales_inr=product_metrics.gross_sales_inr,
            total_ad_spend_inr=product_metrics.ad_spend_inr,
            total_organic_sales_inr=product_metrics.organic_sales_inr,
            organic_share_pct=product_metrics.organic_share_pct,
            total_cost_inr=product_metrics.total_cost_inr,
            total_contribution_inr=product_metrics.contribution_inr,
            overall_profit_margin_pct=product_metrics.profit_margin_pct,
            total_return_rate_pct=product_metrics.return_rate_pct,
            total_cancellation_rate_pct=product_metrics.cancellation_rate_pct,
            product_count=1,
            platform_count=1,
        )

    @staticmethod
    def _build_overall_metrics_from_platform(
        report_date: date,
        platform_metrics: PlatformMetrics,
    ) -> OverallMetrics:
        """Build overall metrics section from platform metrics."""
        return OverallMetrics(
            report_date=report_date,
            total_orders=platform_metrics.total_orders,
            total_units_sold=platform_metrics.total_units_sold,
            total_net_sales_inr=platform_metrics.total_net_sales_inr,
            total_gross_sales_inr=platform_metrics.total_gross_sales_inr,
            total_ad_spend_inr=platform_metrics.total_ad_spend_inr,
            total_organic_sales_inr=platform_metrics.total_organic_sales_inr,
            organic_share_pct=(
                (platform_metrics.total_organic_sales_inr / platform_metrics.total_net_sales_inr * 100)
                if platform_metrics.total_net_sales_inr > 0 else 0
            ),
            total_cost_inr=platform_metrics.total_cost_inr,
            total_contribution_inr=platform_metrics.total_contribution_inr,
            overall_profit_margin_pct=platform_metrics.overall_profit_margin_pct,
            total_return_rate_pct=platform_metrics.overall_return_rate_pct,
            total_cancellation_rate_pct=platform_metrics.overall_cancellation_rate_pct,
            product_count=platform_metrics.product_count,
            platform_count=1,
        )

    @staticmethod
    def _build_product_section(
        product_metrics: ProductMetrics,
        insight_result: Optional[InsightRecommendationResult] = None,
    ) -> ProductSection:
        """Build a product section."""
        key_metrics = [
            KeyMetric(
                name="Units Sold",
                value=float(product_metrics.units_sold),
                unit="units",
            ),
            KeyMetric(
                name="Net Sales",
                value=product_metrics.net_sales_inr,
                unit="INR",
            ),
            KeyMetric(
                name="ROAS",
                value=product_metrics.roas,
                unit="x",
                threshold=2.0,
                status="healthy" if product_metrics.roas >= 2.0 else "at-risk",
            ),
            KeyMetric(
                name="Profit Margin",
                value=product_metrics.profit_margin_pct,
                unit="%",
                threshold=15.0,
                status="healthy" if product_metrics.profit_margin_pct >= 15.0 else "at-risk",
            ),
        ]

        insights = []
        if insight_result:
            for insight in insight_result.insights:
                if insight.sku == product_metrics.sku:
                    insights.append(f"{insight.title}: {insight.description}")

        return ProductSection(
            sku=product_metrics.sku,
            product_name=product_metrics.product_name,
            units_sold=product_metrics.units_sold,
            net_sales_inr=product_metrics.net_sales_inr,
            ad_spend_inr=product_metrics.ad_spend_inr,
            roas=product_metrics.roas,
            acos_pct=product_metrics.acos_pct,
            organic_share_pct=product_metrics.organic_share_pct,
            profit_margin_pct=product_metrics.profit_margin_pct,
            profitability_status=product_metrics.profitability_status,
            return_rate_pct=product_metrics.return_rate_pct,
            cancellation_rate_pct=product_metrics.cancellation_rate_pct,
            key_metrics=key_metrics,
            insights=insights,
        )

    @staticmethod
    def _build_platform_section(
        platform_metrics: PlatformMetrics,
        insight_result: Optional[InsightRecommendationResult] = None,
    ) -> PlatformSection:
        """Build a platform section."""
        key_metrics = [
            KeyMetric(
                name="Products",
                value=float(platform_metrics.product_count),
                unit="count",
            ),
            KeyMetric(
                name="Total Sales",
                value=platform_metrics.total_net_sales_inr,
                unit="INR",
            ),
            KeyMetric(
                name="Platform ROAS",
                value=platform_metrics.platform_roas,
                unit="x",
                threshold=2.0,
            ),
        ]

        insights = []
        if insight_result:
            for insight in insight_result.insights:
                if insight.platform_id == platform_metrics.platform_id:
                    insights.append(f"{insight.title}: {insight.description}")

        return PlatformSection(
            platform_id=platform_metrics.platform_id,
            platform_name=platform_metrics.platform_name,
            total_units_sold=platform_metrics.total_units_sold,
            total_net_sales_inr=platform_metrics.total_net_sales_inr,
            total_ad_spend_inr=platform_metrics.total_ad_spend_inr,
            platform_roas=platform_metrics.platform_roas,
            platform_acos_pct=platform_metrics.platform_acos_pct,
            total_organic_sales_inr=platform_metrics.total_organic_sales_inr,
            organic_share_pct=(
                (platform_metrics.total_organic_sales_inr / platform_metrics.total_net_sales_inr * 100)
                if platform_metrics.total_net_sales_inr > 0 else 0
            ),
            overall_profit_margin_pct=platform_metrics.overall_profit_margin_pct,
            product_count=platform_metrics.product_count,
            top_product=platform_metrics.top_product_sku,
            key_metrics=key_metrics,
            insights=insights,
        )

    @staticmethod
    def _build_advertising_section(
        product_metrics: ProductMetrics,
    ) -> AdvertisingSection:
        """Build advertising section from product metrics."""
        return AdvertisingSection(
            total_ad_spend_inr=product_metrics.ad_spend_inr,
            total_attributed_sales_inr=product_metrics.ad_attributed_sales_inr,
            overall_roas=product_metrics.roas,
            overall_acos_pct=product_metrics.acos_pct,
            impressions=0,
            clicks=0,
            ctr_pct=0.0,
            attributed_units=product_metrics.ad_attributed_units,
            attributed_orders=0,
            cpc_inr=(
                product_metrics.ad_spend_inr / product_metrics.ad_attributed_units
                if product_metrics.ad_attributed_units > 0 else 0
            ),
            cps_inr=(
                product_metrics.ad_spend_inr / product_metrics.ad_attributed_sales_inr
                if product_metrics.ad_attributed_sales_inr > 0 else 0
            ),
        )

    @staticmethod
    def _build_advertising_section_from_platform(
        platform_metrics: PlatformMetrics,
    ) -> AdvertisingSection:
        """Build advertising section from platform metrics."""
        return AdvertisingSection(
            total_ad_spend_inr=platform_metrics.total_ad_spend_inr,
            total_attributed_sales_inr=platform_metrics.total_ad_attributed_sales_inr,
            overall_roas=platform_metrics.platform_roas,
            overall_acos_pct=platform_metrics.platform_acos_pct,
            impressions=0,
            clicks=0,
            ctr_pct=0.0,
            attributed_units=platform_metrics.total_ad_attributed_units,
            attributed_orders=0,
        )

    @staticmethod
    def _build_profitability_section(
        product_metrics_list: List[ProductMetrics],
    ) -> ProfitabilitySection:
        """Build profitability section."""
        total_sales = sum(m.net_sales_inr for m in product_metrics_list)
        total_cost = sum(m.total_cost_inr for m in product_metrics_list)
        total_contribution = sum(m.contribution_inr for m in product_metrics_list)

        healthy = len([m for m in product_metrics_list if m.profit_margin_pct >= 15.0])
        at_risk = len([m for m in product_metrics_list if 0 <= m.profit_margin_pct < 15.0])
        unprofitable = len([m for m in product_metrics_list if m.profit_margin_pct < 0])

        margin_pct = (
            (total_contribution / total_sales * 100) if total_sales > 0 else 0
        )

        return ProfitabilitySection(
            total_net_sales_inr=total_sales,
            total_cost_inr=total_cost,
            total_contribution_inr=total_contribution,
            overall_profit_margin_pct=margin_pct,
            cost_breakdown={
                "product_cost": sum(m.product_cost_inr for m in product_metrics_list),
                "platform_fee": sum(m.platform_fee_inr for m in product_metrics_list),
                "shipping": sum(m.shipping_cost_inr for m in product_metrics_list),
                "payment_fee": sum(m.payment_fee_inr for m in product_metrics_list),
                "other": sum(m.other_cost_inr for m in product_metrics_list),
            },
            products_healthy=healthy,
            products_at_risk=at_risk,
            products_unprofitable=unprofitable,
        )

    @staticmethod
    def _build_quality_section(
        product_metrics_list: List[ProductMetrics],
    ) -> QualitySection:
        """Build quality section."""
        total_sold = sum(m.units_sold for m in product_metrics_list)
        total_returned = sum(m.units_returned for m in product_metrics_list)
        total_refund = sum(m.refund_amount_inr for m in product_metrics_list)
        total_cancelled = sum(m.units_cancelled for m in product_metrics_list)

        return_rate = (
            (total_returned / total_sold * 100) if total_sold > 0 else 0
        )
        cancel_rate = (
            (total_cancelled / total_sold * 100) if total_sold > 0 else 0
        )

        return QualitySection(
            total_units_sold=total_sold,
            total_units_returned=total_returned,
            total_refund_amount_inr=total_refund,
            overall_return_rate_pct=return_rate,
            total_units_cancelled=total_cancelled,
            overall_cancellation_rate_pct=cancel_rate,
        )

    @staticmethod
    def _extract_insights(
        insight_result: Optional[InsightRecommendationResult],
    ) -> List[Insight]:
        """Extract insights from analysis result."""
        if not insight_result:
            return []

        return [
            Insight(
                title=insight.title,
                description=insight.description,
                priority=insight.priority.value,
                category=insight.category.value,
            )
            for insight in insight_result.critical_insights()[:5]
        ]

    @staticmethod
    def _extract_recommendations(
        insight_result: Optional[InsightRecommendationResult],
    ) -> List[Recommendation]:
        """Extract recommendations from analysis result."""
        if not insight_result:
            return []

        return [
            Recommendation(
                action=rec.action,
                rationale=rec.rationale,
                owner=rec.owner,
                priority=rec.priority.value,
                timeline=rec.timeline,
            )
            for rec in insight_result.recommendations[:5]
        ]

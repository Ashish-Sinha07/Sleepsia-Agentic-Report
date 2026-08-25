"""KPI orchestration service that coordinates database queries, validation, and analytics."""

import logging
from datetime import date
from typing import Optional
from decimal import Decimal

from sqlalchemy.orm import Session
from sqlalchemy import text

from app.services.kpi_service import KpiService
from app.schemas.kpi_schemas import KpiResponse, DailyKpisResponse, KpiMetrics
from app.schemas.common import DateRange
from analytics.business_rules import BusinessRules
from analytics.metrics_engine import MetricsEngine
from analytics.insight_engine import InsightEngine
from analytics.recommendation_engine import RecommendationEngine
from analytics.insight_models import BusinessInsight, InsightCategory, Priority

logger = logging.getLogger(__name__)


class KpiOrchestrator:
    """
    Orchestrates the complete KPI pipeline:
    1. Query database for raw data
    2. Validate data integrity
    3. Calculate metrics
    4. Analyze trends and patterns
    5. Generate insights and recommendations
    """

    def __init__(self, db: Session):
        """Initialize orchestrator with database session and engines."""
        self.db = db
        self.business_rules = BusinessRules()
        self.metrics_engine = MetricsEngine()
        self.insight_engine = InsightEngine(self.business_rules)
        self.recommendation_engine = RecommendationEngine(self.business_rules)

    def get_kpis_with_insights(
        self,
        start_date: date,
        end_date: date,
        platform_id: Optional[str] = None,
    ) -> dict:
        """
        Get aggregate KPIs with insights and recommendations.

        Flow:
        1. Query database for raw KPI data
        2. Validate data
        3. Calculate derived metrics
        4. Generate insights from metrics
        5. Generate recommendations from insights
        6. Return comprehensive KPI response

        Args:
            start_date: Period start date
            end_date: Period end date
            platform_id: Optional filter by platform

        Returns:
            Dictionary with KPIs, trends, insights, and recommendations
        """
        logger.info(
            f"Orchestrating KPI retrieval: {start_date} to {end_date}, platform={platform_id}"
        )

        # Step 1: Query raw data from database
        logger.debug("Step 1: Querying database for raw KPI data")
        kpi_response = KpiService.get_daily_kpis(self.db, start_date, end_date, platform_id)

        # Step 2: Validate data
        logger.debug("Step 2: Validating KPI data")
        validation_passed, validation_errors = self._validate_kpi_data(kpi_response.kpis)
        if not validation_passed:
            logger.warning(f"Data validation issues: {validation_errors}")

        # Step 3: Calculate metrics and analyze
        logger.debug("Step 3: Calculating metrics and analyzing trends")
        metrics_analysis = self._analyze_kpi_metrics(kpi_response.kpis)

        # Step 4: Generate insights
        logger.debug("Step 4: Generating insights from metrics")
        insights = self._generate_insights_from_kpis(
            kpi_response.kpis, metrics_analysis, start_date, end_date
        )

        # Step 5: Generate recommendations
        logger.debug("Step 5: Generating recommendations from insights")
        recommendations = self.recommendation_engine.generate_recommendations(insights)

        # Step 6: Build comprehensive response
        logger.debug("Step 6: Building comprehensive KPI response")
        response = {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
            "kpis": kpi_response.kpis.model_dump(),
            "metrics_analysis": metrics_analysis,
            "validation": {
                "passed": validation_passed,
                "errors": validation_errors,
            },
            "insights": [
                {
                    "insight_id": insight.insight_id,
                    "category": insight.category.value,
                    "priority": insight.priority.value,
                    "title": insight.title,
                    "description": insight.description,
                    "metric_name": insight.metric_name,
                    "metric_value": float(insight.metric_value) if isinstance(insight.metric_value, Decimal) else insight.metric_value,
                    "threshold": float(insight.threshold) if isinstance(insight.threshold, Decimal) else insight.threshold,
                    "confidence_pct": insight.confidence_pct,
                    "business_impact": insight.business_impact,
                }
                for insight in insights
            ],
            "recommendations": [
                {
                    "recommendation_id": rec.recommendation_id,
                    "priority": rec.priority.value,
                    "action": rec.action,
                    "rationale": rec.rationale,
                    "expected_impact": rec.expected_impact,
                    "owner": rec.owner,
                    "timeline": rec.timeline,
                    "risk_level": rec.risk_level,
                    "confidence_pct": rec.confidence_pct,
                }
                for rec in recommendations
            ],
            "summary": self._generate_executive_summary(kpi_response.kpis, insights),
        }

        logger.info(f"KPI orchestration complete: {len(insights)} insights, {len(recommendations)} recommendations")
        return response

    def get_daily_kpis_with_analysis(
        self,
        start_date: date,
        end_date: date,
    ) -> dict:
        """
        Get daily KPIs with trend analysis.

        Flow:
        1. Query daily KPI data from database
        2. Calculate daily metrics
        3. Analyze trends across days
        4. Generate time-series insights

        Args:
            start_date: Period start date
            end_date: Period end date

        Returns:
            Dictionary with daily data and trend analysis
        """
        logger.info(f"Orchestrating daily KPI analysis: {start_date} to {end_date}")

        # Query daily data
        daily_response = KpiService.get_daily_kpis_timeseries(self.db, start_date, end_date)

        # Analyze trends
        trend_analysis = self._analyze_daily_trends(daily_response.data)

        # Build response
        response = {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
            "daily_data": [
                {
                    "date": daily.date.isoformat(),
                    "total_revenue": float(daily.total_revenue),
                    "net_revenue": float(daily.net_revenue),
                    "total_profit": float(daily.total_profit),
                    "profit_margin_pct": float(daily.profit_margin_pct) if daily.profit_margin_pct else None,
                    "units_sold": daily.units_sold,
                    "orders": daily.orders,
                    "ad_spend": float(daily.ad_spend),
                    "roas": float(daily.roas) if daily.roas else None,
                    "total_units_returned": daily.total_units_returned,
                    "total_units_cancelled": daily.total_units_cancelled,
                }
                for daily in daily_response.data
            ],
            "trend_analysis": trend_analysis,
            "total_days": daily_response.total,
        }

        logger.info(f"Daily KPI analysis complete: {len(daily_response.data)} days analyzed")
        return response

    def _validate_kpi_data(self, kpis: KpiMetrics) -> tuple[bool, list[str]]:
        """
        Validate KPI data integrity.

        Checks:
        - Total revenue >= net revenue
        - Profit <= net revenue
        - Return rate between 0-100%
        - Cancellation rate between 0-100%
        - ROAS >= 0
        - ACOS percentage between 0-100%

        Args:
            kpis: KPI metrics to validate

        Returns:
            (validation_passed, list_of_errors)
        """
        errors = []

        # Validate revenue hierarchy
        if kpis.net_revenue > kpis.total_revenue:
            errors.append("Net revenue cannot exceed total revenue")

        # Validate profit
        if kpis.total_profit > kpis.net_revenue:
            errors.append("Total profit cannot exceed net revenue")

        # Validate percentages
        if kpis.return_rate_pct and (kpis.return_rate_pct < 0 or kpis.return_rate_pct > 100):
            errors.append(f"Return rate {kpis.return_rate_pct}% is outside valid range 0-100%")

        if kpis.cancellation_rate_pct and (
            kpis.cancellation_rate_pct < 0 or kpis.cancellation_rate_pct > 100
        ):
            errors.append(
                f"Cancellation rate {kpis.cancellation_rate_pct}% is outside valid range 0-100%"
            )

        if kpis.profit_margin_pct and (kpis.profit_margin_pct < -100 or kpis.profit_margin_pct > 100):
            errors.append(f"Profit margin {kpis.profit_margin_pct}% is outside valid range -100% to 100%")

        # Validate advertising metrics
        if kpis.acos_pct and (kpis.acos_pct < 0 or kpis.acos_pct > 200):
            errors.append(f"ACOS {kpis.acos_pct}% is unusually high (typically 0-200%)")

        if kpis.roas and kpis.roas < 0:
            errors.append(f"ROAS cannot be negative")

        validation_passed = len(errors) == 0
        logger.info(f"KPI validation: {'PASSED' if validation_passed else 'FAILED'} ({len(errors)} errors)")

        return validation_passed, errors

    def _analyze_kpi_metrics(self, kpis: KpiMetrics) -> dict:
        """
        Analyze KPI metrics and calculate derived insights.

        Args:
            kpis: KPI metrics to analyze

        Returns:
            Dictionary with metric analysis
        """
        analysis = {
            "revenue_metrics": {},
            "profitability_metrics": {},
            "advertising_metrics": {},
            "quality_metrics": {},
            "business_rules_compliance": {},
        }

        # Revenue analysis
        if kpis.total_revenue > 0:
            organic_ratio = float(kpis.organic_sales / kpis.total_revenue * 100)
            ad_ratio = float(kpis.ad_attributed_sales / kpis.total_revenue * 100)
            analysis["revenue_metrics"] = {
                "total_revenue": float(kpis.total_revenue),
                "organic_sales": float(kpis.organic_sales),
                "ad_attributed_sales": float(kpis.ad_attributed_sales),
                "organic_ratio_pct": organic_ratio,
                "ad_ratio_pct": ad_ratio,
                "avg_order_value": float(kpis.total_revenue / kpis.orders)
                if kpis.orders > 0
                else 0,
            }

        # Profitability analysis
        if kpis.profit_margin_pct:
            profitability_status = self.metrics_engine.determine_profitability_status(
                float(kpis.profit_margin_pct)
            )
            analysis["profitability_metrics"] = {
                "total_profit": float(kpis.total_profit),
                "profit_margin_pct": float(kpis.profit_margin_pct),
                "profitability_status": profitability_status,
            }

        # Advertising analysis
        if kpis.roas and kpis.acos_pct:
            ad_efficiency = "Efficient" if float(kpis.roas) >= 2.0 else "Needs Improvement"
            analysis["advertising_metrics"] = {
                "ad_spend": float(kpis.ad_spend),
                "roas": float(kpis.roas),
                "acos_pct": float(kpis.acos_pct),
                "ad_efficiency": ad_efficiency,
            }

        # Quality metrics
        analysis["quality_metrics"] = {
            "return_rate_pct": float(kpis.return_rate_pct) if kpis.return_rate_pct else 0,
            "cancellation_rate_pct": float(kpis.cancellation_rate_pct) if kpis.cancellation_rate_pct else 0,
            "total_units_sold": kpis.units_sold,
        }

        # Business rules compliance
        analysis["business_rules_compliance"] = {
            "roas_compliance": {
                "passes": float(kpis.roas) >= self.business_rules.minimum_roas if kpis.roas else False,
                "threshold": self.business_rules.minimum_roas,
                "actual": float(kpis.roas) if kpis.roas else 0,
            },
            "acos_compliance": {
                "passes": float(kpis.acos_pct) <= self.business_rules.maximum_acos_pct if kpis.acos_pct else True,
                "threshold": self.business_rules.maximum_acos_pct,
                "actual": float(kpis.acos_pct) if kpis.acos_pct else 0,
            },
            "margin_compliance": {
                "passes": float(kpis.profit_margin_pct) >= self.business_rules.minimum_profit_margin_pct if kpis.profit_margin_pct else False,
                "threshold": self.business_rules.minimum_profit_margin_pct,
                "actual": float(kpis.profit_margin_pct) if kpis.profit_margin_pct else 0,
            },
            "return_rate_compliance": {
                "passes": float(kpis.return_rate_pct) <= self.business_rules.maximum_return_rate_pct if kpis.return_rate_pct else True,
                "threshold": self.business_rules.maximum_return_rate_pct,
                "actual": float(kpis.return_rate_pct) if kpis.return_rate_pct else 0,
            },
        }

        return analysis

    def _generate_insights_from_kpis(
        self,
        kpis: KpiMetrics,
        metrics_analysis: dict,
        start_date: date,
        end_date: date,
    ) -> list[BusinessInsight]:
        """
        Generate business insights from KPI analysis.

        Args:
            kpis: KPI metrics
            metrics_analysis: Analysis results
            start_date: Period start
            end_date: Period end

        Returns:
            List of business insights
        """
        insights = []

        # Profitability insights
        if kpis.profit_margin_pct:
            margin = float(kpis.profit_margin_pct)
            threshold = self.business_rules.minimum_profit_margin_pct

            if margin < threshold:
                insight = BusinessInsight(
                    insight_id="margin_001",
                    category=InsightCategory.PROFITABILITY,
                    priority=Priority.CRITICAL if margin < 0 else Priority.HIGH,
                    title="Profitability Below Target",
                    description=f"Current profit margin ({margin:.2f}%) is below the minimum threshold ({threshold}%)",
                    metric_name="profit_margin_pct",
                    metric_value=margin,
                    threshold=threshold,
                    confidence_pct=95,
                    business_impact=f"At current rate, losing ~${abs(float(kpis.net_revenue) * (threshold - margin) / 100):,.0f} in potential profit",
                )
                insights.append(insight)

        # ROAS insights
        if kpis.roas:
            roas = float(kpis.roas)
            threshold = self.business_rules.minimum_roas

            if roas < threshold:
                insight = BusinessInsight(
                    insight_id="roas_001",
                    category=InsightCategory.ADVERTISING,
                    priority=Priority.HIGH,
                    title="Advertising ROI Below Target",
                    description=f"Current ROAS ({roas:.2f}) is below the minimum threshold ({threshold})",
                    metric_name="roas",
                    metric_value=roas,
                    threshold=threshold,
                    confidence_pct=95,
                    business_impact=f"Ad spend efficiency needs improvement to meet profitability targets",
                )
                insights.append(insight)

        # Return rate insights
        if kpis.return_rate_pct:
            return_rate = float(kpis.return_rate_pct)
            threshold = self.business_rules.maximum_return_rate_pct

            if return_rate > threshold:
                insight = BusinessInsight(
                    insight_id="returns_001",
                    category=InsightCategory.RETURNS,
                    priority=Priority.MEDIUM,
                    title="Return Rate Elevated",
                    description=f"Current return rate ({return_rate:.2f}%) exceeds the maximum threshold ({threshold}%)",
                    metric_name="return_rate_pct",
                    metric_value=return_rate,
                    threshold=threshold,
                    confidence_pct=95,
                    business_impact=f"Quality or satisfaction issues may be impacting customer lifetime value",
                )
                insights.append(insight)

        # Revenue mix insight
        if kpis.total_revenue > 0 and metrics_analysis.get("revenue_metrics"):
            organic_ratio = metrics_analysis["revenue_metrics"].get("organic_ratio_pct", 0)
            if organic_ratio > 80:
                insight = BusinessInsight(
                    insight_id="organic_001",
                    category=InsightCategory.SALES,
                    priority=Priority.INFO,
                    title="Strong Organic Sales Presence",
                    description=f"Organic sales represent {organic_ratio:.1f}% of total revenue - strong market presence",
                    metric_name="organic_ratio",
                    metric_value=organic_ratio,
                    threshold=50,
                    confidence_pct=95,
                    business_impact="Demonstrates strong brand presence and customer loyalty",
                )
                insights.append(insight)

        logger.info(f"Generated {len(insights)} insights from KPI analysis")
        return insights

    def _analyze_daily_trends(self, daily_data: list) -> dict:
        """
        Analyze trends across daily data points.

        Args:
            daily_data: List of daily KPI responses

        Returns:
            Dictionary with trend analysis
        """
        if not daily_data or len(daily_data) == 0:
            return {}

        revenues = [float(d.total_revenue) for d in daily_data]
        profits = [float(d.total_profit) for d in daily_data if d.total_profit]
        orders_list = [d.orders for d in daily_data]

        analysis = {
            "total_days": len(daily_data),
            "revenue_trend": {
                "min": min(revenues),
                "max": max(revenues),
                "avg": sum(revenues) / len(revenues),
                "direction": "increasing"
                if revenues[-1] > revenues[0]
                else "decreasing",
            },
        }

        if profits:
            analysis["profit_trend"] = {
                "min": min(profits),
                "max": max(profits),
                "avg": sum(profits) / len(profits),
            }

        if orders_list:
            analysis["orders_trend"] = {
                "min": min(orders_list),
                "max": max(orders_list),
                "avg": sum(orders_list) / len(orders_list),
            }

        return analysis

    def _generate_executive_summary(self, kpis: KpiMetrics, insights: list[BusinessInsight]) -> str:
        """
        Generate executive summary of KPI performance.

        Args:
            kpis: KPI metrics
            insights: Generated insights

        Returns:
            Executive summary string
        """
        summary_lines = [
            f"Total Revenue: ${float(kpis.total_revenue):,.0f}",
            f"Net Revenue: ${float(kpis.net_revenue):,.0f}",
            f"Total Profit: ${float(kpis.total_profit):,.0f}",
        ]

        if kpis.profit_margin_pct:
            summary_lines.append(f"Profit Margin: {float(kpis.profit_margin_pct):.1f}%")

        if kpis.roas:
            summary_lines.append(f"ROAS: {float(kpis.roas):.2f}x")

        high_priority_insights = [i for i in insights if i.priority == "high"]
        if high_priority_insights:
            summary_lines.append(f"⚠️ {len(high_priority_insights)} high-priority items require attention")

        return " | ".join(summary_lines)

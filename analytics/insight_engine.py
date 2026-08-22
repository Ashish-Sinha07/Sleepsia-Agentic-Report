"""Insight generation engine from analysis results."""

import uuid
from typing import Optional
from analytics.models import (
    AnalysisResult,
    PerformanceFinding,
    ProductMetrics,
    PlatformMetrics,
)
from analytics.insight_models import (
    BusinessInsight,
    InsightCategory,
    Priority,
)
from analytics.priority_engine import PriorityEngine
from analytics.business_rules import BusinessRules


class InsightEngine:
    """Generate structured business insights from analysis results."""

    def __init__(self, business_rules: BusinessRules = None):
        """Initialize with business rules."""
        self.rules = business_rules or BusinessRules()
        self.priority_engine = PriorityEngine(self.rules)

    def generate_insights_from_analysis(
        self,
        analysis_result: AnalysisResult,
        product_metrics: Optional[ProductMetrics] = None,
        platform_metrics: Optional[PlatformMetrics] = None,
    ) -> list[BusinessInsight]:
        """
        Generate structured insights from an analysis result.

        Args:
            analysis_result: The AnalysisResult from DataAnalysisAgent or LLMAnalysisAgent
            product_metrics: Optional ProductMetrics for context
            platform_metrics: Optional PlatformMetrics for context

        Returns:
            List of BusinessInsight objects with evidence traceability
        """
        insights = []

        if not analysis_result.performance_findings:
            return insights

        for finding in analysis_result.performance_findings:
            insight = self._convert_finding_to_insight(
                finding,
                analysis_result,
                product_metrics,
                platform_metrics,
            )
            if insight:
                insights.append(insight)

        if analysis_result.risks_identified:
            for risk in analysis_result.risks_identified:
                insight = self._create_risk_insight(risk, analysis_result)
                if insight:
                    insights.append(insight)

        if analysis_result.anomalies_detected:
            for anomaly in analysis_result.anomalies_detected:
                insight = self._create_anomaly_insight(anomaly, analysis_result)
                if insight:
                    insights.append(insight)

        return insights

    def _convert_finding_to_insight(
        self,
        finding: PerformanceFinding,
        analysis_result: AnalysisResult,
        product_metrics: Optional[ProductMetrics] = None,
        platform_metrics: Optional[PlatformMetrics] = None,
    ) -> Optional[BusinessInsight]:
        """Convert a PerformanceFinding to a BusinessInsight with priority."""
        insight_id = str(uuid.uuid4())[:8]

        category = self._map_finding_to_category(finding.finding_type)
        priority = self._determine_priority_from_finding(finding, product_metrics)

        insight = BusinessInsight(
            insight_id=insight_id,
            category=category,
            priority=priority,
            title=self._create_insight_title(finding),
            description=finding.description,
            metric_name=finding.metric_name,
            metric_value=finding.metric_value,
            threshold=finding.threshold,
            sku=finding.sku,
            platform_id=finding.platform_id,
            evidence=[finding.recommendation] if finding.recommendation else [],
            confidence_pct=self._calculate_confidence(finding),
            business_impact=self._calculate_business_impact(finding, product_metrics),
        )

        if product_metrics:
            insight.product_name = product_metrics.product_name

        if platform_metrics:
            insight.platform_name = platform_metrics.platform_name

        return insight

    def _create_risk_insight(
        self,
        risk_description: str,
        analysis_result: AnalysisResult,
    ) -> Optional[BusinessInsight]:
        """Create an insight from a risk description."""
        if not risk_description:
            return None

        insight_id = str(uuid.uuid4())[:8]

        insight = BusinessInsight(
            insight_id=insight_id,
            category=InsightCategory.ANOMALY,
            priority=Priority.HIGH,
            title=f"Risk: {risk_description[:50]}",
            description=risk_description,
            evidence=[risk_description],
        )

        return insight

    def _create_anomaly_insight(
        self,
        anomaly_description: str,
        analysis_result: AnalysisResult,
    ) -> Optional[BusinessInsight]:
        """Create an insight from an anomaly description."""
        if not anomaly_description:
            return None

        insight_id = str(uuid.uuid4())[:8]

        insight = BusinessInsight(
            insight_id=insight_id,
            category=InsightCategory.ANOMALY,
            priority=Priority.MEDIUM,
            title=f"Anomaly: {anomaly_description[:50]}",
            description=anomaly_description,
            evidence=[anomaly_description],
        )

        return insight

    def _map_finding_to_category(self, finding_type: str) -> InsightCategory:
        """Map finding type to insight category."""
        mapping = {
            "profitability": InsightCategory.PROFITABILITY,
            "quality": InsightCategory.RETURNS,
            "fulfillment": InsightCategory.CANCELLATIONS,
            "advertising": InsightCategory.ADVERTISING,
            "channel_mix": InsightCategory.SALES,
            "trend": InsightCategory.TREND,
            "volatility": InsightCategory.ANOMALY,
            "platform_profitability": InsightCategory.PLATFORM,
            "platform_quality": InsightCategory.RETURNS,
            "platform_advertising": InsightCategory.ADVERTISING,
            "anomaly": InsightCategory.ANOMALY,
        }
        return mapping.get(finding_type, InsightCategory.ANOMALY)

    def _determine_priority_from_finding(
        self,
        finding: PerformanceFinding,
        product_metrics: Optional[ProductMetrics] = None,
    ) -> Priority:
        """Determine priority level for a finding."""
        severity_to_priority = {
            "critical": Priority.CRITICAL,
            "high": Priority.HIGH,
            "medium": Priority.MEDIUM,
            "low": Priority.LOW,
        }

        priority = severity_to_priority.get(finding.severity, Priority.MEDIUM)

        if finding.finding_type == "profitability" and product_metrics:
            priority = self.priority_engine.determine_profitability_priority(
                product_metrics.profit_margin_pct,
                product=product_metrics.sku,
            )

        elif finding.finding_type == "advertising" and product_metrics:
            priority = self.priority_engine.determine_advertising_priority(
                product_metrics.roas,
                product_metrics.acos_pct,
                product=product_metrics.sku,
            )

        elif finding.finding_type == "quality" and product_metrics:
            priority = self.priority_engine.determine_quality_priority(
                product_metrics.return_rate_pct,
                product_metrics.cancellation_rate_pct,
                product=product_metrics.sku,
            )

        return priority

    def _create_insight_title(self, finding: PerformanceFinding) -> str:
        """Create a concise insight title."""
        if finding.sku:
            return f"{finding.finding_type.title()}: {finding.sku}"
        elif finding.platform_id:
            return f"{finding.finding_type.title()}: {finding.platform_id}"
        else:
            return f"{finding.finding_type.title()}: {finding.metric_name}"

    def _calculate_confidence(self, finding: PerformanceFinding) -> float:
        """Calculate confidence percentage."""
        severity_confidence = {
            "critical": 95.0,
            "high": 90.0,
            "medium": 80.0,
            "low": 70.0,
        }
        return severity_confidence.get(finding.severity, 75.0)

    def _calculate_business_impact(
        self,
        finding: PerformanceFinding,
        product_metrics: Optional[ProductMetrics] = None,
    ) -> str:
        """Calculate business impact statement."""
        if not product_metrics:
            return "Unknown impact"

        if finding.finding_type == "profitability":
            lost_margin = (
                self.rules.minimum_profit_margin_pct - finding.metric_value
            )
            estimated_loss = (
                product_metrics.net_sales_inr * (lost_margin / 100)
            )
            return f"Estimated margin loss: ₹{estimated_loss:,.0f}"

        elif finding.finding_type == "quality":
            refund_impact = (
                product_metrics.units_sold * product_metrics.refund_amount_inr
            )
            return f"Estimated refund impact: ₹{refund_impact:,.0f}"

        elif finding.finding_type == "advertising":
            wasted_spend = (
                product_metrics.ad_spend_inr * (
                    (self.rules.maximum_acos_pct - product_metrics.acos_pct) / 100
                )
            )
            return f"Potential efficiency improvement: ₹{wasted_spend:,.0f}"

        return "Material business impact"

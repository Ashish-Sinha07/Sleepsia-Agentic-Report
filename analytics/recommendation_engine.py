"""Recommendation generation engine from insights."""

import uuid
from typing import Optional
from analytics.insight_models import (
    BusinessInsight,
    Recommendation,
    Priority,
    InsightCategory,
)
from analytics.business_rules import BusinessRules


class RecommendationEngine:
    """Generate evidence-based recommendations from business insights."""

    def __init__(self, business_rules: BusinessRules = None):
        """Initialize with business rules."""
        self.rules = business_rules or BusinessRules()

    def generate_recommendations(
        self,
        insights: list[BusinessInsight],
    ) -> list[Recommendation]:
        """
        Generate evidence-based recommendations from insights.

        Args:
            insights: List of BusinessInsight objects

        Returns:
            List of Recommendation objects with evidence traceability
        """
        recommendations = []

        for insight in insights:
            rec = self._generate_recommendation_from_insight(insight)
            if rec:
                recommendations.append(rec)

        return recommendations

    def _generate_recommendation_from_insight(
        self,
        insight: BusinessInsight,
    ) -> Optional[Recommendation]:
        """Generate a recommendation from a single insight."""
        if insight.category == InsightCategory.PROFITABILITY:
            return self._recommend_for_profitability(insight)

        elif insight.category == InsightCategory.ADVERTISING:
            return self._recommend_for_advertising(insight)

        elif insight.category == InsightCategory.RETURNS:
            return self._recommend_for_returns(insight)

        elif insight.category == InsightCategory.CANCELLATIONS:
            return self._recommend_for_cancellations(insight)

        elif insight.category == InsightCategory.SALES:
            return self._recommend_for_sales(insight)

        elif insight.category == InsightCategory.TREND:
            return self._recommend_for_trend(insight)

        elif insight.category == InsightCategory.PLATFORM:
            return self._recommend_for_platform(insight)

        elif insight.category == InsightCategory.ANOMALY:
            return self._recommend_for_anomaly(insight)

        return None

    def _recommend_for_profitability(self, insight: BusinessInsight) -> Recommendation:
        """Generate recommendation for profitability issues."""
        rec_id = str(uuid.uuid4())[:8]

        action = "Review pricing and cost structure"
        if insight.metric_value is not None and insight.threshold is not None:
            gap = insight.threshold - insight.metric_value
            action = f"Improve profit margin by at least {gap:.1f} percentage points"

        return Recommendation(
            recommendation_id=rec_id,
            action=action,
            rationale="Negative or at-risk profit margins erode business sustainability",
            expected_impact="Restore healthy profitability and improve cash flow",
            owner="Product/Finance Manager",
            priority=self._determine_recommendation_priority(insight.priority),
            sku=insight.sku,
            product_name=insight.product_name,
            platform_id=insight.platform_id,
            platform_name=insight.platform_name,
            evidence=insight.evidence,
            confidence_pct=insight.confidence_pct,
            timeline="Within 30 days",
            risk_level="high",
        )

    def _recommend_for_advertising(self, insight: BusinessInsight) -> Recommendation:
        """Generate recommendation for advertising efficiency."""
        rec_id = str(uuid.uuid4())[:8]

        action = "Optimize advertising campaigns"
        if insight.metric_name == "roas":
            action = "Increase ad spend or improve conversion rate to achieve minimum ROAS"
        elif insight.metric_name == "acos_pct":
            action = "Reduce advertising cost per sale through better targeting"

        return Recommendation(
            recommendation_id=rec_id,
            action=action,
            rationale="Poor advertising efficiency wastes marketing budget",
            expected_impact="Improve ROI on advertising spend and reduce ACOS",
            owner="Marketing Manager",
            priority=self._determine_recommendation_priority(insight.priority),
            sku=insight.sku,
            product_name=insight.product_name,
            platform_id=insight.platform_id,
            platform_name=insight.platform_name,
            evidence=insight.evidence,
            confidence_pct=insight.confidence_pct,
            timeline="Within 2 weeks",
            risk_level="medium",
        )

    def _recommend_for_returns(self, insight: BusinessInsight) -> Recommendation:
        """Generate recommendation for high return rates."""
        rec_id = str(uuid.uuid4())[:8]

        return Recommendation(
            recommendation_id=rec_id,
            action="Investigate root cause of returns and implement quality improvement",
            rationale="High return rates indicate quality, fit, or description issues",
            expected_impact="Reduce returns, improve customer satisfaction, and protect margins",
            owner="Quality/Product Manager",
            priority=self._determine_recommendation_priority(insight.priority),
            sku=insight.sku,
            product_name=insight.product_name,
            platform_id=insight.platform_id,
            platform_name=insight.platform_name,
            evidence=insight.evidence,
            confidence_pct=insight.confidence_pct,
            timeline="Within 1 week (investigation), 30 days (resolution)",
            risk_level="high",
        )

    def _recommend_for_cancellations(self, insight: BusinessInsight) -> Recommendation:
        """Generate recommendation for high cancellation rates."""
        rec_id = str(uuid.uuid4())[:8]

        return Recommendation(
            recommendation_id=rec_id,
            action="Review fulfillment process and inventory availability",
            rationale="High cancellations indicate fulfillment or availability issues",
            expected_impact="Reduce cancellations and improve order completion rate",
            owner="Operations/Fulfillment Manager",
            priority=self._determine_recommendation_priority(insight.priority),
            sku=insight.sku,
            product_name=insight.product_name,
            platform_id=insight.platform_id,
            platform_name=insight.platform_name,
            evidence=insight.evidence,
            confidence_pct=insight.confidence_pct,
            timeline="Within 2 weeks",
            risk_level="medium",
        )

    def _recommend_for_sales(self, insight: BusinessInsight) -> Recommendation:
        """Generate recommendation for sales/channel opportunities."""
        rec_id = str(uuid.uuid4())[:8]

        return Recommendation(
            recommendation_id=rec_id,
            action="Optimize channel and promotional strategy",
            rationale="Sales channel imbalance or organic growth potential",
            expected_impact="Increase overall sales and improve channel efficiency",
            owner="Sales Manager",
            priority=Priority.LOW,
            sku=insight.sku,
            product_name=insight.product_name,
            platform_id=insight.platform_id,
            platform_name=insight.platform_name,
            evidence=insight.evidence,
            confidence_pct=insight.confidence_pct,
            timeline="Within 30 days",
            risk_level="low",
        )

    def _recommend_for_trend(self, insight: BusinessInsight) -> Recommendation:
        """Generate recommendation for trend-based insights."""
        rec_id = str(uuid.uuid4())[:8]

        action = "Monitor trend and investigate drivers"
        if "downward" in insight.description.lower():
            action = "Investigate and reverse downward trend"

        return Recommendation(
            recommendation_id=rec_id,
            action=action,
            rationale="Metric trends indicate changing business conditions",
            expected_impact="Maintain or improve key performance metrics",
            owner="Business Analyst",
            priority=self._determine_recommendation_priority(insight.priority),
            evidence=insight.evidence,
            confidence_pct=insight.confidence_pct,
            timeline="Within 1 week (analysis), 2 weeks (action)",
            risk_level="medium",
        )

    def _recommend_for_platform(self, insight: BusinessInsight) -> Recommendation:
        """Generate recommendation for platform-level issues."""
        rec_id = str(uuid.uuid4())[:8]

        return Recommendation(
            recommendation_id=rec_id,
            action="Conduct platform-wide performance review",
            rationale="Platform-level issues affect entire business segment",
            expected_impact="Improve platform profitability and overall business health",
            owner="Platform Manager",
            priority=self._determine_recommendation_priority(insight.priority),
            platform_id=insight.platform_id,
            platform_name=insight.platform_name,
            evidence=insight.evidence,
            confidence_pct=insight.confidence_pct,
            timeline="Within 1 week (review), 30 days (implementation)",
            risk_level="high",
        )

    def _recommend_for_anomaly(self, insight: BusinessInsight) -> Recommendation:
        """Generate recommendation for anomalies."""
        rec_id = str(uuid.uuid4())[:8]

        return Recommendation(
            recommendation_id=rec_id,
            action="Investigate statistical anomaly",
            rationale="Unusual metrics may indicate data quality or operational issues",
            expected_impact="Clarify situation and take corrective action if needed",
            owner="Data Analyst",
            priority=Priority.MEDIUM,
            sku=insight.sku,
            product_name=insight.product_name,
            platform_id=insight.platform_id,
            platform_name=insight.platform_name,
            evidence=insight.evidence,
            confidence_pct=insight.confidence_pct,
            timeline="Within 3 days",
            risk_level="low",
        )

    def _determine_recommendation_priority(self, insight_priority: Priority) -> Priority:
        """Map insight priority to recommendation priority."""
        priority_mapping = {
            Priority.CRITICAL: Priority.CRITICAL,
            Priority.HIGH: Priority.HIGH,
            Priority.MEDIUM: Priority.MEDIUM,
            Priority.LOW: Priority.LOW,
            Priority.INFO: Priority.INFO,
        }
        return priority_mapping.get(insight_priority, Priority.MEDIUM)

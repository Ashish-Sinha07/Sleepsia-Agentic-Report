"""Insight & Recommendation Agent - Phase 3 of the analysis pipeline."""

from datetime import date
from typing import Optional
from analytics.models import (
    AnalysisResult,
    ProductMetrics,
    PlatformMetrics,
)
from analytics.insight_models import (
    InsightRecommendationResult,
    Priority,
)
from analytics.business_rules import BusinessRules
from analytics.insight_engine import InsightEngine
from analytics.recommendation_engine import RecommendationEngine
from analytics.summary_generator import ManagementSummaryGenerator


class InsightRecommendationAgent:
    """
    Phase 3: Converts analyzed metrics into management-ready insights and recommendations.

    CRITICAL CONSTRAINTS:
    1. Never recalculates financial metrics (receives them pre-calculated)
    2. Only uses supplied analysis results as evidence
    3. Never invents missing data
    4. All priorities are deterministic based on BusinessRules
    5. Every recommendation is traceable to supporting evidence
    6. Returns only structured output with full evidence chains
    """

    def __init__(self, business_rules: Optional[BusinessRules] = None):
        """Initialize with business rules."""
        self.rules = business_rules or BusinessRules()
        self.insight_engine = InsightEngine(self.rules)
        self.recommendation_engine = RecommendationEngine(self.rules)

    def analyze(
        self,
        analysis_result: AnalysisResult,
        product_metrics: Optional[ProductMetrics] = None,
        platform_metrics: Optional[PlatformMetrics] = None,
        data_completeness: float = 1.0,
        generated_at: Optional[date] = None,
    ) -> InsightRecommendationResult:
        """
        Convert analysis results into insights and recommendations.

        Args:
            analysis_result: AnalysisResult from DataAnalysisAgent or LLMAnalysisAgent
            product_metrics: Optional ProductMetrics for context
            platform_metrics: Optional PlatformMetrics for context
            data_completeness: Percentage of expected data available (0-1)
            generated_at: Date insights were generated (defaults to today)

        Returns:
            InsightRecommendationResult with insights, recommendations, and management summary
        """
        if generated_at is None:
            generated_at = date.today()

        insights = self.insight_engine.generate_insights_from_analysis(
            analysis_result,
            product_metrics,
            platform_metrics,
        )

        recommendations = self.recommendation_engine.generate_recommendations(insights)

        for rec in recommendations:
            for insight in insights:
                if self._recommendation_relates_to_insight(rec, insight):
                    rec.add_insight_source(insight.insight_id)
                    insight.add_finding_source(rec.recommendation_id)

        management_summary = ManagementSummaryGenerator.generate_summary(
            period_start=analysis_result.period_start,
            period_end=analysis_result.period_end,
            insights=insights,
            recommendations=recommendations,
            data_completeness_pct=data_completeness * 100,
            generated_at=generated_at,
        )

        confidence = self._determine_overall_confidence(insights, data_completeness)

        result = InsightRecommendationResult(
            analysis_period_start=analysis_result.period_start,
            analysis_period_end=analysis_result.period_end,
            generated_at=generated_at,
            insights=insights,
            recommendations=recommendations,
            management_summary=management_summary,
            overall_confidence=confidence,
            data_completeness=data_completeness,
        )

        return result

    def _recommendation_relates_to_insight(
        self,
        recommendation,
        insight,
    ) -> bool:
        """Check if a recommendation relates to an insight."""
        if (
            recommendation.sku
            and insight.sku
            and recommendation.sku == insight.sku
        ):
            return True

        if (
            recommendation.platform_id
            and insight.platform_id
            and recommendation.platform_id == insight.platform_id
        ):
            return True

        if (
            recommendation.action.lower()
            and insight.title.lower()
            and any(
                word in recommendation.action.lower()
                for word in insight.title.lower().split()
            )
        ):
            return True

        return False

    def _determine_overall_confidence(
        self,
        insights,
        data_completeness: float,
    ) -> str:
        """Determine overall analysis confidence."""
        if data_completeness < 0.7:
            return "low"

        critical_insights = [i for i in insights if i.priority == Priority.CRITICAL]
        high_insights = [i for i in insights if i.priority == Priority.HIGH]

        total_issues = len(critical_insights) + len(high_insights)

        if total_issues > 0:
            avg_confidence = (
                sum(i.confidence_pct for i in critical_insights + high_insights)
                / total_issues
            )

            if avg_confidence < 70:
                return "medium"
            else:
                return "high"

        return "medium"

    def export_for_llm_refinement(
        self,
        result: InsightRecommendationResult,
    ) -> dict:
        """
        Export insights and recommendations for LLM-powered refinement.

        The LLM can then:
        - Explain implications in business terms
        - Suggest additional actions
        - Summarize key findings
        """
        return {
            "period_start": result.analysis_period_start.isoformat(),
            "period_end": result.analysis_period_end.isoformat(),
            "generated_at": result.generated_at.isoformat(),
            "insights": [
                {
                    "insight_id": i.insight_id,
                    "category": i.category.value,
                    "priority": i.priority.value,
                    "title": i.title,
                    "description": i.description,
                    "metric_name": i.metric_name,
                    "metric_value": i.metric_value,
                    "threshold": i.threshold,
                    "sku": i.sku,
                    "product_name": i.product_name,
                    "platform_id": i.platform_id,
                    "platform_name": i.platform_name,
                    "evidence": i.evidence,
                    "confidence_pct": i.confidence_pct,
                    "business_impact": i.business_impact,
                }
                for i in result.insights
            ],
            "recommendations": [
                {
                    "recommendation_id": r.recommendation_id,
                    "action": r.action,
                    "rationale": r.rationale,
                    "expected_impact": r.expected_impact,
                    "owner": r.owner,
                    "priority": r.priority.value,
                    "sku": r.sku,
                    "product_name": r.product_name,
                    "platform_id": r.platform_id,
                    "platform_name": r.platform_name,
                    "evidence": r.evidence,
                    "confidence_pct": r.confidence_pct,
                    "timeline": r.timeline,
                    "estimated_financial_impact_inr": r.estimated_financial_impact_inr,
                    "risk_level": r.risk_level,
                }
                for r in result.recommendations
            ],
            "management_summary": {
                "period_start": result.management_summary.period_start.isoformat(),
                "period_end": result.management_summary.period_end.isoformat(),
                "executive_summary": result.management_summary.executive_summary,
                "critical_issues": result.management_summary.critical_issues,
                "high_priority_items": result.management_summary.high_priority_items,
                "key_opportunities": result.management_summary.key_opportunities,
                "top_recommendations": result.management_summary.top_recommendations,
                "overall_health_score": result.management_summary.overall_health_score,
                "data_completeness_pct": result.management_summary.data_completeness_pct,
            },
            "overall_confidence": result.overall_confidence,
            "data_completeness": result.data_completeness,
            "issues_count": result.issues_count,
            "opportunities_count": result.opportunities_count,
        }

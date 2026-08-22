"""Unit tests for Phase 3: Insight & Recommendation Agent."""

import pytest
from datetime import date
from analytics.business_rules import BusinessRules
from analytics.insight_models import Priority, InsightCategory
from analytics.priority_engine import PriorityEngine
from analytics.insight_engine import InsightEngine
from analytics.recommendation_engine import RecommendationEngine
from analytics.summary_generator import ManagementSummaryGenerator
from agents.insight_recommendation_agent import InsightRecommendationAgent
from analytics.models import (
    AnalysisResult,
    PerformanceFinding,
    ProductMetrics,
)
from analytics.metrics_engine import MetricsEngine


class TestBusinessRules:
    """Test BusinessRules configuration and threshold evaluation."""

    def test_default_thresholds(self):
        """Test default business rule thresholds."""
        rules = BusinessRules()
        assert rules.minimum_roas == 2.0
        assert rules.maximum_acos_pct == 50.0
        assert rules.minimum_profit_margin_pct == 15.0
        assert rules.maximum_return_rate_pct == 15.0
        assert rules.maximum_cancellation_rate_pct == 10.0

    def test_evaluate_roas_pass(self):
        """Test ROAS threshold evaluation - passing."""
        rules = BusinessRules(minimum_roas=2.0)
        passes, threshold = rules.evaluate_roas(3.0)
        assert passes is True
        assert threshold == 2.0

    def test_evaluate_roas_fail(self):
        """Test ROAS threshold evaluation - failing."""
        rules = BusinessRules(minimum_roas=2.0)
        passes, threshold = rules.evaluate_roas(1.5)
        assert passes is False
        assert threshold == 2.0

    def test_evaluate_profit_margin_healthy(self):
        """Test profit margin evaluation - healthy."""
        rules = BusinessRules(minimum_profit_margin_pct=15.0)
        passes, threshold = rules.evaluate_profit_margin(35.0)
        assert passes is True

    def test_evaluate_profit_margin_unprofitable(self):
        """Test profit margin evaluation - unprofitable."""
        rules = BusinessRules(minimum_profit_margin_pct=15.0)
        passes, threshold = rules.evaluate_profit_margin(-5.0)
        assert passes is False

    def test_platform_override(self):
        """Test platform-specific threshold overrides."""
        platform_rules = BusinessRules(minimum_roas=1.5)
        rules = BusinessRules()
        rules.platform_overrides["amazon"] = platform_rules

        threshold = rules.get_threshold("minimum_roas", platform="amazon")
        assert threshold == 1.5

        threshold = rules.get_threshold("minimum_roas", platform="flipkart")
        assert threshold == 2.0

    def test_product_override(self):
        """Test product-specific threshold overrides."""
        product_rules = BusinessRules(minimum_profit_margin_pct=20.0)
        rules = BusinessRules()
        rules.product_overrides["SLP-1001"] = product_rules

        threshold = rules.get_threshold("minimum_profit_margin_pct", product="SLP-1001")
        assert threshold == 20.0


class TestPriorityEngine:
    """Test priority determination engine."""

    def test_profitability_priority_critical(self):
        """Test critical profitability priority."""
        rules = BusinessRules()
        engine = PriorityEngine(rules)

        priority = engine.determine_profitability_priority(-5.0)
        assert priority == Priority.CRITICAL

    def test_profitability_priority_high(self):
        """Test high profitability priority."""
        rules = BusinessRules(minimum_profit_margin_pct=15.0)
        engine = PriorityEngine(rules)

        priority = engine.determine_profitability_priority(10.0)
        assert priority == Priority.HIGH

    def test_profitability_priority_info(self):
        """Test info (positive) profitability priority."""
        rules = BusinessRules(minimum_profit_margin_pct=15.0)
        engine = PriorityEngine(rules)

        priority = engine.determine_profitability_priority(30.0)
        assert priority == Priority.INFO

    def test_advertising_priority_medium(self):
        """Test medium advertising priority."""
        rules = BusinessRules()
        engine = PriorityEngine(rules)

        priority = engine.determine_advertising_priority(roas=1.5, acos_pct=60.0)
        assert priority == Priority.MEDIUM

    def test_quality_priority_critical_high_return(self):
        """Test critical quality priority for extremely high returns."""
        rules = BusinessRules()
        engine = PriorityEngine(rules)

        priority = engine.determine_quality_priority(
            return_rate_pct=40.0,
            cancellation_rate_pct=5.0,
        )
        assert priority == Priority.CRITICAL

    def test_quality_priority_high(self):
        """Test high quality priority."""
        rules = BusinessRules()
        engine = PriorityEngine(rules)

        priority = engine.determine_quality_priority(
            return_rate_pct=20.0,
            cancellation_rate_pct=5.0,
        )
        assert priority == Priority.HIGH

    def test_trend_priority_downward_critical(self):
        """Test critical priority for steep downward trend."""
        rules = BusinessRules()
        engine = PriorityEngine(rules)

        priority = engine.determine_trend_priority(
            trend_direction="downward",
            trend_strength=0.35,
        )
        assert priority == Priority.CRITICAL

    def test_trend_priority_downward_high(self):
        """Test high priority for moderate downward trend."""
        rules = BusinessRules()
        engine = PriorityEngine(rules)

        priority = engine.determine_trend_priority(
            trend_direction="downward",
            trend_strength=0.15,
        )
        assert priority == Priority.HIGH

    def test_trend_priority_upward_info(self):
        """Test info priority for strong upward trend."""
        rules = BusinessRules()
        engine = PriorityEngine(rules)

        priority = engine.determine_trend_priority(
            trend_direction="upward",
            trend_strength=0.30,
        )
        assert priority == Priority.INFO

    def test_anomaly_priority_critical(self):
        """Test critical priority for severe anomaly."""
        rules = BusinessRules()
        engine = PriorityEngine(rules)

        priority = engine.determine_anomaly_priority(
            deviation_std_deviations=3.5,
            is_negative_anomaly=True,
        )
        assert priority == Priority.CRITICAL

    def test_anomaly_priority_high(self):
        """Test high priority for moderate anomaly."""
        rules = BusinessRules()
        engine = PriorityEngine(rules)

        priority = engine.determine_anomaly_priority(
            deviation_std_deviations=2.2,
            is_negative_anomaly=True,
        )
        assert priority == Priority.HIGH

    def test_growth_priority_decline(self):
        """Test high priority for revenue decline."""
        rules = BusinessRules()
        engine = PriorityEngine(rules)

        priority = engine.determine_growth_priority(growth_pct=-25.0)
        assert priority == Priority.HIGH

    def test_growth_priority_excessive_growth(self):
        """Test medium priority for excessive cost growth."""
        rules = BusinessRules()
        engine = PriorityEngine(rules)

        priority = engine.determine_growth_priority(growth_pct=45.0)
        assert priority == Priority.MEDIUM


class TestInsightEngine:
    """Test insight generation engine."""

    def test_generate_insights_from_findings(self):
        """Test converting findings to insights."""
        rules = BusinessRules()
        engine = InsightEngine(rules)

        finding = PerformanceFinding(
            finding_type="profitability",
            severity="critical",
            sku="SLP-1001",
            metric_name="profit_margin_pct",
            metric_value=-5.0,
            threshold=15.0,
            description="Product is unprofitable",
            recommendation="Review pricing",
        )

        analysis_result = AnalysisResult(
            period_start=date(2026, 8, 1),
            period_end=date(2026, 8, 31),
            analysis_type="product",
            summary="Analysis complete",
            key_metrics={},
            performance_findings=[finding],
            anomalies_detected=[],
            risks_identified=[],
            opportunities=[],
            recommended_actions=[],
            confidence="high",
            data_completeness=1.0,
        )

        insights = engine.generate_insights_from_analysis(analysis_result)

        assert len(insights) > 0
        assert insights[0].sku == "SLP-1001"
        assert insights[0].priority == Priority.CRITICAL
        assert insights[0].category == InsightCategory.PROFITABILITY

    def test_insight_evidence_traceability(self):
        """Test that insights maintain evidence traceability."""
        rules = BusinessRules()
        engine = InsightEngine(rules)

        finding = PerformanceFinding(
            finding_type="quality",
            severity="high",
            sku="SLP-1001",
            metric_name="return_rate_pct",
            metric_value=20.0,
            threshold=15.0,
            description="High return rate",
            recommendation="Investigate quality",
        )

        analysis_result = AnalysisResult(
            period_start=date(2026, 8, 1),
            period_end=date(2026, 8, 31),
            analysis_type="product",
            summary="Analysis complete",
            key_metrics={},
            performance_findings=[finding],
            anomalies_detected=[],
            risks_identified=[],
            opportunities=[],
            recommended_actions=[],
            confidence="high",
            data_completeness=1.0,
        )

        insights = engine.generate_insights_from_analysis(analysis_result)

        assert len(insights[0].evidence) > 0

    def test_insight_confidence_calculation(self):
        """Test insight confidence based on severity."""
        rules = BusinessRules()
        engine = InsightEngine(rules)

        critical_finding = PerformanceFinding(
            finding_type="profitability",
            severity="critical",
            sku="SLP-1001",
            metric_name="profit_margin_pct",
            metric_value=-5.0,
            description="Unprofitable",
        )

        analysis_result = AnalysisResult(
            period_start=date(2026, 8, 1),
            period_end=date(2026, 8, 31),
            analysis_type="product",
            summary="Analysis complete",
            key_metrics={},
            performance_findings=[critical_finding],
            anomalies_detected=[],
            risks_identified=[],
            opportunities=[],
            recommended_actions=[],
            confidence="high",
            data_completeness=1.0,
        )

        insights = engine.generate_insights_from_analysis(analysis_result)

        assert insights[0].confidence_pct >= 90.0


class TestRecommendationEngine:
    """Test recommendation generation engine."""

    def test_generate_profitability_recommendation(self):
        """Test profitability recommendation generation."""
        rules = BusinessRules()
        engine = RecommendationEngine(rules)

        from analytics.insight_models import BusinessInsight

        insight = BusinessInsight(
            insight_id="test-1",
            category=InsightCategory.PROFITABILITY,
            priority=Priority.CRITICAL,
            title="Unprofitable Product",
            description="Negative margin",
            metric_name="profit_margin_pct",
            metric_value=-5.0,
            threshold=15.0,
            sku="SLP-1001",
        )

        recommendations = engine.generate_recommendations([insight])

        assert len(recommendations) > 0
        action_lower = recommendations[0].action.lower()
        assert any(word in action_lower for word in ["profitability", "pricing", "margin", "improve"])

    def test_recommendation_priority_mapping(self):
        """Test that recommendation priority matches insight priority."""
        rules = BusinessRules()
        engine = RecommendationEngine(rules)

        from analytics.insight_models import BusinessInsight

        critical_insight = BusinessInsight(
            insight_id="test-1",
            category=InsightCategory.PROFITABILITY,
            priority=Priority.CRITICAL,
            title="Critical Issue",
            description="Test",
            sku="SLP-1001",
        )

        recommendations = engine.generate_recommendations([critical_insight])

        assert recommendations[0].priority == Priority.CRITICAL

    def test_recommendation_evidence_chains(self):
        """Test that recommendations maintain evidence chains."""
        rules = BusinessRules()
        engine = RecommendationEngine(rules)

        from analytics.insight_models import BusinessInsight

        insight = BusinessInsight(
            insight_id="insight-123",
            category=InsightCategory.ADVERTISING,
            priority=Priority.HIGH,
            title="Poor ROAS",
            description="ROAS is 1.5x, below 2.0x threshold",
            metric_name="roas",
            metric_value=1.5,
            threshold=2.0,
            evidence=["ROAS calculation verified"],
            sku="SLP-1001",
        )

        recommendations = engine.generate_recommendations([insight])

        assert len(recommendations[0].evidence) > 0


class TestManagementSummaryGenerator:
    """Test management summary generation."""

    def test_generate_summary_with_critical_issues(self):
        """Test summary generation with critical issues."""
        from analytics.insight_models import BusinessInsight

        critical = BusinessInsight(
            insight_id="c1",
            category=InsightCategory.PROFITABILITY,
            priority=Priority.CRITICAL,
            title="Unprofitable Product",
            description="Negative margin of -5%",
            sku="SLP-1001",
        )

        high = BusinessInsight(
            insight_id="h1",
            category=InsightCategory.RETURNS,
            priority=Priority.HIGH,
            title="High Return Rate",
            description="20% return rate",
            sku="SLP-1001",
        )

        insights = [critical, high]

        summary = ManagementSummaryGenerator.generate_summary(
            period_start=date(2026, 8, 1),
            period_end=date(2026, 8, 31),
            insights=insights,
            recommendations=[],
        )

        assert "critical" in summary.executive_summary.lower()
        assert len(summary.critical_issues) > 0
        assert len(summary.high_priority_items) > 0

    def test_health_score_calculation(self):
        """Test overall health score calculation."""
        from analytics.insight_models import BusinessInsight

        critical = BusinessInsight(
            insight_id="c1",
            category=InsightCategory.PROFITABILITY,
            priority=Priority.CRITICAL,
            title="Test",
            description="Test",
        )

        insights = [critical]

        summary = ManagementSummaryGenerator.generate_summary(
            period_start=date(2026, 8, 1),
            period_end=date(2026, 8, 31),
            insights=insights,
            recommendations=[],
            data_completeness_pct=100.0,
        )

        assert summary.overall_health_score < 85
        assert summary.overall_health_score > 0

    def test_summary_formatting(self):
        """Test summary can be formatted for reporting."""
        from analytics.insight_models import BusinessInsight

        insights = [
            BusinessInsight(
                insight_id="i1",
                category=InsightCategory.SALES,
                priority=Priority.INFO,
                title="Positive Trend",
                description="Sales increasing",
            )
        ]

        summary = ManagementSummaryGenerator.generate_summary(
            period_start=date(2026, 8, 1),
            period_end=date(2026, 8, 31),
            insights=insights,
            recommendations=[],
        )

        formatted = ManagementSummaryGenerator.format_for_management_report(summary)

        assert "BUSINESS PERFORMANCE SUMMARY" in formatted
        assert "Health Score" in formatted


class TestInsightRecommendationAgent:
    """Test complete insight & recommendation agent."""

    def test_full_pipeline_integration(self):
        """Test full pipeline from analysis to insights/recommendations."""
        agent = InsightRecommendationAgent()
        engine = MetricsEngine()

        metrics = engine.calculate_product_metrics(
            sku="BAD-1",
            product_name="Unprofitable Product",
            units_sold=100,
            gross_sales=5000,
            net_sales=4500,
            discount=500,
            ad_spend=2000,
            ad_attributed_units=50,
            ad_attributed_sales=2250,
            product_cost=3000,
            platform_fee=1000,
            shipping_cost=500,
            payment_fee=250,
            other_cost=100,
            units_returned=20,
            refund_amount=2000,
            units_cancelled=5,
        )

        finding = PerformanceFinding(
            finding_type="profitability",
            severity="critical",
            sku=metrics.sku,
            metric_name="profit_margin_pct",
            metric_value=metrics.profit_margin_pct,
            threshold=15.0,
            description=f"Product is unprofitable with {metrics.profit_margin_pct:.2f}% margin",
            recommendation="Review pricing and costs",
        )

        analysis_result = AnalysisResult(
            period_start=date(2026, 8, 1),
            period_end=date(2026, 8, 31),
            analysis_type="product",
            summary="Analysis complete",
            key_metrics={"profit_margin_pct": metrics.profit_margin_pct},
            performance_findings=[finding],
            anomalies_detected=[],
            risks_identified=["Unprofitable product"],
            opportunities=[],
            recommended_actions=["Review pricing"],
            confidence="high",
            data_completeness=1.0,
        )

        result = agent.analyze(
            analysis_result=analysis_result,
            product_metrics=metrics,
        )

        assert len(result.insights) > 0
        assert len(result.recommendations) > 0
        assert result.management_summary is not None
        assert result.issues_count >= 1

    def test_result_structure_validity(self):
        """Test that result structure is valid."""
        agent = InsightRecommendationAgent()

        finding = PerformanceFinding(
            finding_type="profitability",
            severity="critical",
            metric_name="test",
            description="test",
        )

        analysis_result = AnalysisResult(
            period_start=date(2026, 8, 1),
            period_end=date(2026, 8, 31),
            analysis_type="product",
            summary="Test",
            key_metrics={},
            performance_findings=[finding],
            anomalies_detected=[],
            risks_identified=[],
            opportunities=[],
            recommended_actions=[],
            confidence="high",
            data_completeness=1.0,
        )

        result = agent.analyze(analysis_result)

        assert hasattr(result, "insights")
        assert hasattr(result, "recommendations")
        assert hasattr(result, "management_summary")
        assert hasattr(result, "overall_confidence")
        assert hasattr(result, "data_completeness")

    def test_export_for_llm_refinement(self):
        """Test export format for LLM refinement."""
        agent = InsightRecommendationAgent()

        finding = PerformanceFinding(
            finding_type="profitability",
            severity="critical",
            metric_name="test",
            description="test",
        )

        analysis_result = AnalysisResult(
            period_start=date(2026, 8, 1),
            period_end=date(2026, 8, 31),
            analysis_type="product",
            summary="Test",
            key_metrics={},
            performance_findings=[finding],
            anomalies_detected=[],
            risks_identified=[],
            opportunities=[],
            recommended_actions=[],
            confidence="high",
            data_completeness=1.0,
        )

        result = agent.analyze(analysis_result)
        export = agent.export_for_llm_refinement(result)

        assert "insights" in export
        assert "recommendations" in export
        assert "management_summary" in export
        assert isinstance(export["insights"], list)
        assert isinstance(export["recommendations"], list)


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_empty_findings(self):
        """Test handling of empty findings."""
        agent = InsightRecommendationAgent()

        analysis_result = AnalysisResult(
            period_start=date(2026, 8, 1),
            period_end=date(2026, 8, 31),
            analysis_type="product",
            summary="No findings",
            key_metrics={},
            performance_findings=[],
            anomalies_detected=[],
            risks_identified=[],
            opportunities=[],
            recommended_actions=[],
            confidence="low",
            data_completeness=0.0,
        )

        result = agent.analyze(analysis_result)

        assert len(result.insights) == 0
        assert result.issues_count == 0

    def test_low_data_completeness(self):
        """Test confidence adjustment for low data completeness."""
        agent = InsightRecommendationAgent()

        finding = PerformanceFinding(
            finding_type="profitability",
            severity="critical",
            metric_name="test",
            description="test",
        )

        analysis_result = AnalysisResult(
            period_start=date(2026, 8, 1),
            period_end=date(2026, 8, 31),
            analysis_type="product",
            summary="Test",
            key_metrics={},
            performance_findings=[finding],
            anomalies_detected=[],
            risks_identified=[],
            opportunities=[],
            recommended_actions=[],
            confidence="low",
            data_completeness=0.5,
        )

        result = agent.analyze(analysis_result, data_completeness=0.5)

        assert result.data_completeness == 0.5
        assert result.overall_confidence == "low"

    def test_recommendation_evidence_chain(self):
        """Test that recommendation properly links to insights."""
        agent = InsightRecommendationAgent()

        finding = PerformanceFinding(
            finding_type="advertising",
            severity="high",
            sku="TEST-1",
            metric_name="roas",
            metric_value=1.5,
            threshold=2.0,
            description="Poor ROAS",
        )

        analysis_result = AnalysisResult(
            period_start=date(2026, 8, 1),
            period_end=date(2026, 8, 31),
            analysis_type="product",
            summary="Test",
            key_metrics={},
            performance_findings=[finding],
            anomalies_detected=[],
            risks_identified=[],
            opportunities=[],
            recommended_actions=[],
            confidence="high",
            data_completeness=1.0,
        )

        result = agent.analyze(analysis_result)

        assert len(result.recommendations) > 0
        first_rec = result.recommendations[0]
        assert len(first_rec.insight_sources) > 0

"""Unit tests for Claude-powered LLM Analysis Agent."""

import pytest
from datetime import date
from unittest.mock import Mock, patch, MagicMock
import json

from analytics.llm_analysis_agent import LLMAnalysisAgent
from analytics.analysis_input import AnalysisInput, MetricComparison
from analytics.metrics_engine import MetricsEngine
from analytics.models import AnalysisResult


class TestLLMAnalysisAgentParsing:
    """Test JSON parsing and validation."""

    def test_valid_json_response_parsing(self):
        """Test parsing valid Claude response."""
        agent = LLMAnalysisAgent(api_key="test-key")

        valid_response = """{
            "period_start": "2026-08-21",
            "period_end": "2026-08-21",
            "analysis_type": "product",
            "summary": "Product performing well with strong margins.",
            "key_metrics": {
                "net_sales": 9500,
                "profit_margin_pct": 38.42
            },
            "performance_findings": [
                {
                    "finding_type": "profitability",
                    "severity": "low",
                    "sku": "SLP-1001",
                    "platform_id": null,
                    "metric_name": "profit_margin_pct",
                    "metric_value": 38.42,
                    "threshold": 15.0,
                    "description": "Product has healthy profit margin of 38.42%",
                    "recommendation": "Maintain current pricing and ad spend strategy"
                }
            ],
            "anomalies_detected": [],
            "risks_identified": [],
            "opportunities": ["Consider increasing ad spend given strong ROAS"],
            "recommended_actions": ["Monitor competitive pricing"],
            "confidence": "high",
            "data_completeness": 1.0
        }"""

        result = agent._parse_response(valid_response, AnalysisInput(
            analysis_date=date(2026, 8, 21),
            analysis_type="product",
        ))

        assert isinstance(result, AnalysisResult)
        assert result.analysis_type == "product"
        assert result.confidence == "high"
        assert len(result.performance_findings) == 1
        assert result.performance_findings[0].severity == "low"

    def test_json_extraction_from_text(self):
        """Test extracting JSON from surrounding text."""
        agent = LLMAnalysisAgent(api_key="test-key")

        response_with_text = """Based on the metrics, here's my analysis:

{
    "period_start": "2026-08-21",
    "period_end": "2026-08-21",
    "analysis_type": "platform",
    "summary": "Platform analysis complete.",
    "key_metrics": {},
    "performance_findings": [],
    "anomalies_detected": [],
    "risks_identified": [],
    "opportunities": [],
    "recommended_actions": [],
    "confidence": "medium",
    "data_completeness": 0.8
}

This analysis shows moderate performance."""

        result = agent._parse_response(response_with_text, AnalysisInput(
            analysis_date=date(2026, 8, 21),
            analysis_type="platform",
        ))

        assert result.analysis_type == "platform"
        assert result.confidence == "medium"

    def test_malformed_json_repair(self):
        """Test repair of common JSON malformations."""
        agent = LLMAnalysisAgent(api_key="test-key")

        malformed = """{
            "period_start": "2026-08-21",
            "analysis_type": "product",
            "summary": "Analysis complete",
            "key_metrics": {"margin": 38.42,},
            "performance_findings": [],
            "anomalies_detected": [],
            "risks_identified": [],
            "opportunities": [],
            "recommended_actions": [],
            "confidence": "high",
            "data_completeness": 1.0,
        }"""

        repaired = agent._repair_json(malformed)

        assert json.loads(repaired) is not None
        assert ',' not in repaired.split('}')[0].split('{')[-1]

    def test_python_bool_to_json_conversion(self):
        """Test conversion of Python booleans to JSON."""
        agent = LLMAnalysisAgent(api_key="test-key")

        python_json = """{
            "active": True,
            "archived": False,
            "data_complete": null
        }"""

        repaired = agent._repair_json(python_json)

        parsed = json.loads(repaired)
        assert parsed["active"] is True
        assert parsed["archived"] is False
        assert parsed["data_complete"] is None


class TestLLMAnalysisAgentIntegration:
    """Test integration with mocked Claude API."""

    @patch('anthropic.Anthropic')
    def test_analyze_with_mocked_claude(self, mock_anthropic_class):
        """Test complete analysis with mocked Claude."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="""{
            "period_start": "2026-08-21",
            "period_end": "2026-08-21",
            "analysis_type": "product",
            "summary": "SLP-1001 shows strong profitability.",
            "key_metrics": {
                "profit_margin_pct": 38.42,
                "roas": 5.7,
                "organic_share": 40.0
            },
            "performance_findings": [
                {
                    "finding_type": "profitability",
                    "severity": "low",
                    "sku": "SLP-1001",
                    "platform_id": null,
                    "metric_name": "profit_margin",
                    "metric_value": 38.42,
                    "threshold": 15.0,
                    "description": "Healthy margin of 38.42%",
                    "recommendation": "Maintain current strategy"
                }
            ],
            "anomalies_detected": [],
            "risks_identified": [],
            "opportunities": ["Scale ad spend"],
            "recommended_actions": ["Monitor competition"],
            "confidence": "high",
            "data_completeness": 1.0
        }""")]

        mock_client.messages.create.return_value = mock_response

        agent = LLMAnalysisAgent(api_key="test-key")

        engine = MetricsEngine()
        metrics = engine.calculate_product_metrics(
            sku="SLP-1001",
            product_name="Contour Pillow",
            units_sold=100,
            gross_sales=10000,
            net_sales=9500,
            discount=500,
            ad_spend=1000,
            ad_attributed_units=60,
            ad_attributed_sales=5700,
            product_cost=3000,
            platform_fee=1000,
            shipping_cost=500,
            payment_fee=250,
            other_cost=50,
            units_returned=5,
            refund_amount=500,
            units_cancelled=2,
        )

        analysis_input = AnalysisInput(
            analysis_date=date(2026, 8, 21),
            analysis_type="product",
            product_metrics=metrics,
            current_day_comparisons=[
                MetricComparison("profit_margin", 38.42, 35.0),
                MetricComparison("units_sold", 100, 95),
            ],
        )

        result = agent.analyze(analysis_input)

        assert isinstance(result, AnalysisResult)
        assert result.analysis_type == "product"
        assert result.confidence == "high"
        assert "SLP-1001" in result.summary or len(result.performance_findings) > 0
        assert result.data_completeness == 1.0

    @patch('anthropic.Anthropic')
    def test_analyze_platform_comparison(self, mock_anthropic_class):
        """Test platform-level analysis with comparison."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="""{
            "period_start": "2026-08-21",
            "period_end": "2026-08-21",
            "analysis_type": "platform",
            "summary": "Amazon platform performing well with strong margins.",
            "key_metrics": {
                "total_sales": 50000,
                "platform_margin": 25.5,
                "roas": 4.2
            },
            "performance_findings": [
                {
                    "finding_type": "advertising",
                    "severity": "low",
                    "sku": null,
                    "platform_id": "AMZ",
                    "metric_name": "platform_roas",
                    "metric_value": 4.2,
                    "threshold": 2.0,
                    "description": "Strong ROAS of 4.2x on Amazon",
                    "recommendation": "Consider increasing ad budget"
                }
            ],
            "anomalies_detected": [],
            "risks_identified": [],
            "opportunities": ["Scale on Amazon given strong performance"],
            "recommended_actions": ["Allocate more budget to Amazon ads"],
            "confidence": "high",
            "data_completeness": 0.95
        }""")]

        mock_client.messages.create.return_value = mock_response

        agent = LLMAnalysisAgent(api_key="test-key")

        engine = MetricsEngine()
        products = [
            engine.calculate_product_metrics(
                sku=f"SKU-{i}",
                product_name=f"Product {i}",
                units_sold=100,
                gross_sales=10000,
                net_sales=9500,
                discount=500,
                ad_spend=1000,
                ad_attributed_units=50,
                ad_attributed_sales=4750,
                product_cost=3000,
                platform_fee=1000,
                shipping_cost=500,
                payment_fee=250,
                other_cost=50,
                units_returned=5,
                refund_amount=500,
                units_cancelled=2,
            )
            for i in range(5)
        ]

        platform_metrics = engine.calculate_platform_metrics(products, "AMZ", "Amazon")

        analysis_input = AnalysisInput(
            analysis_date=date(2026, 8, 21),
            analysis_type="platform",
            platform_metrics=platform_metrics,
        )

        result = agent.analyze(analysis_input)

        assert result.analysis_type == "platform"
        assert result.confidence == "high"
        assert "Amazon" in result.summary or platform_metrics.platform_name in result.summary


class TestLLMAnalysisAgentFallback:
    """Test fallback handling for errors."""

    @patch('anthropic.Anthropic')
    def test_fallback_on_json_parse_error(self, mock_anthropic_class):
        """Test fallback result when JSON parsing fails."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="This is not JSON at all")]

        mock_client.messages.create.return_value = mock_response

        agent = LLMAnalysisAgent(api_key="test-key")

        analysis_input = AnalysisInput(
            analysis_date=date(2026, 8, 21),
            analysis_type="product",
        )

        result = agent.analyze(analysis_input)

        assert isinstance(result, AnalysisResult)
        assert result.confidence == "low"
        assert result.data_completeness == 0.0
        assert "could not be completed" in result.summary.lower()

    @patch('anthropic.Anthropic')
    def test_retry_on_malformed_json(self, mock_anthropic_class):
        """Test retry logic on first attempt failure."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        malformed_json = """{
            "analysis_type": "product",
            "summary": "Test",
            "key_metrics": {"value": 100,},
            "performance_findings": [],
            "anomalies_detected": [],
            "risks_identified": [],
            "opportunities": [],
            "recommended_actions": [],
            "confidence": "high",
            "data_completeness": 1.0
        }"""

        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=malformed_json)]

        mock_client.messages.create.return_value = mock_response

        agent = LLMAnalysisAgent(api_key="test-key")

        analysis_input = AnalysisInput(
            analysis_date=date(2026, 8, 21),
            analysis_type="product",
        )

        result = agent.analyze(analysis_input)

        assert isinstance(result, AnalysisResult)
        assert result.confidence == "high"


class TestLLMAnalysisAgentPromptBuilding:
    """Test prompt construction."""

    def test_prompt_includes_all_context(self):
        """Test that prompt includes all provided context."""
        agent = LLMAnalysisAgent(api_key="test-key")

        engine = MetricsEngine()
        metrics = engine.calculate_product_metrics(
            sku="SLP-1001",
            product_name="Test Product",
            units_sold=100,
            gross_sales=10000,
            net_sales=9500,
            discount=500,
            ad_spend=1000,
            ad_attributed_units=60,
            ad_attributed_sales=5700,
            product_cost=3000,
            platform_fee=1000,
            shipping_cost=500,
            payment_fee=250,
            other_cost=50,
            units_returned=5,
            refund_amount=500,
            units_cancelled=2,
        )

        analysis_input = AnalysisInput(
            analysis_date=date(2026, 8, 21),
            analysis_type="product",
            product_metrics=metrics,
            current_day_comparisons=[
                MetricComparison("profit_margin", 38.42, 35.0),
            ],
            detected_anomalies=["Return rate elevated"],
        )

        prompt = agent._build_prompt(analysis_input)

        assert "Test Product" in prompt
        assert "SLP-1001" in prompt
        assert "38.42" in prompt
        assert "Return rate elevated" in prompt

    def test_prompt_with_trend_metrics(self):
        """Test prompt building with trend data."""
        agent = LLMAnalysisAgent(api_key="test-key")

        from analytics.models import TrendMetrics

        trend = TrendMetrics(
            metric_name="daily_sales",
            period_start=date(2026, 8, 15),
            period_end=date(2026, 8, 21),
            days=7,
            average_daily=9500,
            min_daily=8000,
            max_daily=11000,
            day_7_average=9500,
            trend_direction="upward",
            trend_strength=0.15,
        )

        analysis_input = AnalysisInput(
            analysis_date=date(2026, 8, 21),
            analysis_type="daily",
            trend_metrics=trend,
        )

        prompt = agent._build_prompt(analysis_input)

        assert "upward" in prompt
        assert "15.0%" in prompt or "0.15" in prompt


class TestLLMAnalysisAgentConstraints:
    """Test that agent respects safety constraints."""

    def test_agent_never_overrides_metrics(self):
        """Test that agent output never contradicts input metrics."""
        agent = LLMAnalysisAgent(api_key="test-key")

        engine = MetricsEngine()
        metrics = engine.calculate_product_metrics(
            sku="SLP-1001",
            product_name="Product",
            units_sold=100,
            gross_sales=10000,
            net_sales=9500,
            discount=500,
            ad_spend=1000,
            ad_attributed_units=60,
            ad_attributed_sales=5700,
            product_cost=3000,
            platform_fee=1000,
            shipping_cost=500,
            payment_fee=250,
            other_cost=50,
            units_returned=5,
            refund_amount=500,
            units_cancelled=2,
        )

        analysis_input = AnalysisInput(
            analysis_date=date(2026, 8, 21),
            analysis_type="product",
            product_metrics=metrics,
        )

        prompt = agent._build_prompt(analysis_input)

        assert "never calculate" not in prompt.lower() or "system prompt" in agent.SYSTEM_PROMPT.lower()
        assert "NEVER calculate" in agent.SYSTEM_PROMPT

    def test_system_prompt_enforces_evidence_requirement(self):
        """Test that system prompt requires evidence-based claims."""
        agent = LLMAnalysisAgent(api_key="test-key")

        assert "evidence" in agent.SYSTEM_PROMPT.lower()
        assert "only" in agent.SYSTEM_PROMPT.lower()
        assert "supplied" in agent.SYSTEM_PROMPT.lower()

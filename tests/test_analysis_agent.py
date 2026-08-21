"""Unit tests for the Data Analysis Agent."""

import pytest
from datetime import date
from analytics.analysis_agent import DataAnalysisAgent
from analytics.metrics_engine import MetricsEngine
from analytics.models import ProductMetrics, PlatformMetrics


class TestDataAnalysisAgentProductAnalysis:
    """Test product-level performance analysis."""

    def test_unprofitable_product_detection(self):
        """Test detection of unprofitable products."""
        agent = DataAnalysisAgent()
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
            units_returned=10,
            refund_amount=1000,
            units_cancelled=5,
        )

        findings = agent.analyze_product_performance(metrics)

        assert len(findings) > 0
        critical_findings = [f for f in findings if f.severity == "critical"]
        assert len(critical_findings) > 0
        assert any(f.finding_type == "profitability" for f in critical_findings)

    def test_high_return_rate_detection(self):
        """Test detection of high return rates."""
        agent = DataAnalysisAgent()
        engine = MetricsEngine()

        metrics = engine.calculate_product_metrics(
            sku="RET-1",
            product_name="High Return Product",
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
            units_returned=20,
            refund_amount=2000,
            units_cancelled=2,
        )

        findings = agent.analyze_product_performance(metrics)

        return_findings = [f for f in findings if f.finding_type == "quality"]
        assert len(return_findings) > 0
        assert any(f.severity == "high" for f in return_findings)

    def test_poor_roas_detection(self):
        """Test detection of poor advertising ROI."""
        agent = DataAnalysisAgent()
        engine = MetricsEngine()

        metrics = engine.calculate_product_metrics(
            sku="ADS-1",
            product_name="Poor ROAS Product",
            units_sold=100,
            gross_sales=10000,
            net_sales=9500,
            discount=500,
            ad_spend=8000,
            ad_attributed_units=20,
            ad_attributed_sales=1900,
            product_cost=3000,
            platform_fee=1000,
            shipping_cost=500,
            payment_fee=250,
            other_cost=50,
            units_returned=5,
            refund_amount=500,
            units_cancelled=2,
        )

        findings = agent.analyze_product_performance(metrics)

        ad_findings = [f for f in findings if f.finding_type == "advertising"]
        assert len(ad_findings) > 0
        assert metrics.roas < agent.THRESHOLDS["poor_roas"]

    def test_high_organic_share_opportunity(self):
        """Test identification of organic sales opportunities."""
        agent = DataAnalysisAgent()
        engine = MetricsEngine()

        metrics = engine.calculate_product_metrics(
            sku="ORG-1",
            product_name="High Organic Product",
            units_sold=100,
            gross_sales=10000,
            net_sales=9500,
            discount=500,
            ad_spend=200,
            ad_attributed_units=10,
            ad_attributed_sales=950,
            product_cost=2000,
            platform_fee=800,
            shipping_cost=400,
            payment_fee=200,
            other_cost=50,
            units_returned=2,
            refund_amount=200,
            units_cancelled=1,
        )

        findings = agent.analyze_product_performance(metrics)

        opportunity_findings = [f for f in findings if f.finding_type == "channel_mix"]
        assert len(opportunity_findings) > 0
        assert metrics.organic_share_pct > agent.THRESHOLDS["high_organic_share"]

    def test_healthy_product_minimal_findings(self):
        """Test that healthy products generate fewer findings."""
        agent = DataAnalysisAgent()
        engine = MetricsEngine()

        metrics = engine.calculate_product_metrics(
            sku="GOOD-1",
            product_name="Healthy Product",
            units_sold=100,
            gross_sales=10000,
            net_sales=9500,
            discount=500,
            ad_spend=1000,
            ad_attributed_units=50,
            ad_attributed_sales=4750,
            product_cost=2000,
            platform_fee=800,
            shipping_cost=400,
            payment_fee=200,
            other_cost=50,
            units_returned=2,
            refund_amount=200,
            units_cancelled=1,
        )

        findings = agent.analyze_product_performance(metrics)

        critical_findings = [f for f in findings if f.severity == "critical"]
        assert len(critical_findings) == 0


class TestDataAnalysisAgentPlatformAnalysis:
    """Test platform-level performance analysis."""

    def test_unprofitable_platform_detection(self):
        """Test detection of unprofitable platforms."""
        agent = DataAnalysisAgent()
        engine = MetricsEngine()

        products = [
            engine.calculate_product_metrics(
                sku=f"SKU-{i}",
                product_name=f"Product {i}",
                units_sold=50,
                gross_sales=3000,
                net_sales=2700,
                discount=300,
                ad_spend=1500,
                ad_attributed_units=30,
                ad_attributed_sales=1350,
                product_cost=1500,
                platform_fee=800,
                shipping_cost=300,
                payment_fee=150,
                other_cost=50,
                units_returned=5,
                refund_amount=500,
                units_cancelled=2,
            )
            for i in range(3)
        ]

        platform = engine.calculate_platform_metrics(
            products, "TEST-PLATFORM", "Test Platform"
        )

        findings = agent.analyze_platform_performance(platform)

        if platform.overall_profit_margin_pct < 0:
            critical_findings = [f for f in findings if f.severity == "critical"]
            assert len(critical_findings) > 0

    def test_high_platform_return_rate_detection(self):
        """Test detection of platform-wide return issues."""
        agent = DataAnalysisAgent()
        engine = MetricsEngine()

        products = [
            engine.calculate_product_metrics(
                sku=f"HIGH-RET-{i}",
                product_name=f"High Return Product {i}",
                units_sold=100,
                gross_sales=8000,
                net_sales=7600,
                discount=400,
                ad_spend=800,
                ad_attributed_units=40,
                ad_attributed_sales=3040,
                product_cost=2400,
                platform_fee=600,
                shipping_cost=300,
                payment_fee=150,
                other_cost=40,
                units_returned=18,
                refund_amount=1800,
                units_cancelled=2,
            )
            for i in range(2)
        ]

        platform = engine.calculate_platform_metrics(
            products, "HIGH-RET", "High Return Platform"
        )

        findings = agent.analyze_platform_performance(platform)

        if platform.overall_return_rate_pct > agent.THRESHOLDS["high_return_rate"]:
            quality_findings = [f for f in findings if f.finding_type == "platform_quality"]
            assert len(quality_findings) > 0


class TestDataAnalysisAgentTrendAnalysis:
    """Test trend analysis functionality."""

    def test_upward_trend_detection(self):
        """Test detection of upward trends."""
        agent = DataAnalysisAgent()
        engine = MetricsEngine()

        daily_values = [
            (date(2026, 8, 1), 1000),
            (date(2026, 8, 2), 1100),
            (date(2026, 8, 3), 1200),
            (date(2026, 8, 4), 1300),
            (date(2026, 8, 5), 1400),
        ]

        trend = engine.calculate_trend(
            "sales", daily_values, date(2026, 8, 1), date(2026, 8, 5)
        )

        findings = agent.analyze_daily_trend(trend)

        trend_findings = [f for f in findings if f.finding_type == "trend"]
        assert len(trend_findings) > 0
        assert any(f.severity == "low" for f in trend_findings)

    def test_downward_trend_detection(self):
        """Test detection of downward trends."""
        agent = DataAnalysisAgent()
        engine = MetricsEngine()

        daily_values = [
            (date(2026, 8, 1), 1400),
            (date(2026, 8, 2), 1300),
            (date(2026, 8, 3), 1200),
            (date(2026, 8, 4), 1100),
            (date(2026, 8, 5), 1000),
        ]

        trend = engine.calculate_trend(
            "sales", daily_values, date(2026, 8, 1), date(2026, 8, 5)
        )

        findings = agent.analyze_daily_trend(trend)

        trend_findings = [f for f in findings if f.finding_type == "trend"]
        assert len(trend_findings) > 0
        assert any(f.severity == "high" for f in trend_findings)

    def test_volatility_detection(self):
        """Test detection of high volatility."""
        agent = DataAnalysisAgent()
        engine = MetricsEngine()

        daily_values = [
            (date(2026, 8, 1), 500),
            (date(2026, 8, 2), 2000),
            (date(2026, 8, 3), 600),
            (date(2026, 8, 4), 1900),
            (date(2026, 8, 5), 700),
        ]

        trend = engine.calculate_trend(
            "sales", daily_values, date(2026, 8, 1), date(2026, 8, 5)
        )

        findings = agent.analyze_daily_trend(trend)

        volatility_findings = [f for f in findings if f.finding_type == "volatility"]
        assert len(volatility_findings) > 0


class TestDataAnalysisAgentAnomalyDetection:
    """Test anomaly detection functionality."""

    def test_statistical_outlier_detection(self):
        """Test detection of statistical outliers."""
        agent = DataAnalysisAgent()
        engine = MetricsEngine()

        metrics_list = [
            engine.calculate_product_metrics(
                sku=f"SKU-{i}",
                product_name=f"Normal Product {i}",
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

        outlier = engine.calculate_product_metrics(
            sku="SKU-OUTLIER",
            product_name="Outlier Product",
            units_sold=100,
            gross_sales=5000,
            net_sales=4500,
            discount=500,
            ad_spend=3000,
            ad_attributed_units=80,
            ad_attributed_sales=3600,
            product_cost=3500,
            platform_fee=1500,
            shipping_cost=500,
            payment_fee=300,
            other_cost=100,
            units_returned=10,
            refund_amount=1000,
            units_cancelled=3,
        )

        metrics_list.append(outlier)

        anomalies = agent.detect_anomalies(metrics_list)

        assert len(anomalies) > 0


class TestDataAnalysisAgentSynthesis:
    """Test synthesis of analysis results."""

    def test_analysis_result_generation(self):
        """Test generating analysis results."""
        agent = DataAnalysisAgent()
        engine = MetricsEngine()

        metrics = engine.calculate_product_metrics(
            sku="TEST-1",
            product_name="Test Product",
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

        findings = agent.analyze_product_performance(metrics)
        anomalies = agent.detect_anomalies([metrics])

        result = agent.generate_analysis_result(
            period_start=date(2026, 8, 1),
            period_end=date(2026, 8, 31),
            analysis_type="product_performance",
            findings=findings,
            anomalies=anomalies,
            key_metrics={
                "units_sold": metrics.units_sold,
                "net_sales": metrics.net_sales_inr,
                "contribution": metrics.contribution_inr,
            },
        )

        assert result.period_start == date(2026, 8, 1)
        assert result.period_end == date(2026, 8, 31)
        assert result.analysis_type == "product_performance"
        assert result.summary is not None
        assert len(result.summary) > 0
        assert result.data_completeness >= 0.0
        assert result.data_completeness <= 1.0
        assert result.confidence in ["high", "medium", "low"]

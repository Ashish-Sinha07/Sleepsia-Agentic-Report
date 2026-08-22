"""Unit tests for the Business Metrics Engine."""

import pytest
from datetime import date
from analytics.metrics_engine import MetricsEngine
from analytics.models import ProductMetrics, PlatformMetrics


class TestMetricsEngineCalculations:
    """Test deterministic metric calculations."""

    def test_roas_calculation(self):
        """Test Return on Ad Spend calculation."""
        engine = MetricsEngine()

        assert engine.calculate_roas(sales=1000, ad_spend=200) == 5.0
        assert engine.calculate_roas(sales=500, ad_spend=500) == 1.0
        assert engine.calculate_roas(sales=100, ad_spend=0) == 0.0
        assert engine.calculate_roas(sales=0, ad_spend=100) == 0.0

    def test_acos_calculation(self):
        """Test Advertising Cost of Sale calculation."""
        engine = MetricsEngine()

        assert engine.calculate_acos(ad_spend=100, sales=1000) == 10.0
        assert engine.calculate_acos(ad_spend=500, sales=1000) == 50.0
        assert engine.calculate_acos(ad_spend=0, sales=1000) == 0.0
        assert engine.calculate_acos(ad_spend=100, sales=0) == 0.0

    def test_organic_sales_calculation(self):
        """Test organic sales and share calculation."""
        engine = MetricsEngine()

        organic, share = engine.calculate_organic_sales(
            total_sales=1000, ad_attributed_sales=600
        )
        assert organic == 400
        assert share == 40.0

        organic, share = engine.calculate_organic_sales(
            total_sales=500, ad_attributed_sales=500
        )
        assert organic == 0
        assert share == 0.0

        organic, share = engine.calculate_organic_sales(
            total_sales=0, ad_attributed_sales=0
        )
        assert organic == 0
        assert share == 0.0

    def test_return_rate_calculation(self):
        """Test return rate calculation."""
        engine = MetricsEngine()

        assert engine.calculate_return_rate(units_returned=10, units_sold=100) == 10.0
        assert engine.calculate_return_rate(units_returned=0, units_sold=100) == 0.0
        assert engine.calculate_return_rate(units_returned=50, units_sold=100) == 50.0
        assert engine.calculate_return_rate(units_returned=1, units_sold=0) == 0.0

    def test_cancellation_rate_calculation(self):
        """Test cancellation rate calculation."""
        engine = MetricsEngine()

        assert engine.calculate_cancellation_rate(units_cancelled=5, units_sold=100) == 5.0
        assert engine.calculate_cancellation_rate(units_cancelled=0, units_sold=100) == 0.0
        assert engine.calculate_cancellation_rate(units_cancelled=25, units_sold=100) == 25.0
        assert engine.calculate_cancellation_rate(units_cancelled=1, units_sold=0) == 0.0

    def test_contribution_calculation(self):
        """Test contribution (gross profit) calculation."""
        engine = MetricsEngine()

        contribution = engine.calculate_contribution(
            net_sales=1000,
            product_cost=300,
            platform_fee=150,
            shipping_cost=50,
            payment_fee=30,
            other_cost=20,
            refund=0,
        )
        assert contribution == 450  # 1000 - (300+150+50+30+20)

        contribution = engine.calculate_contribution(
            net_sales=1000,
            product_cost=600,
            platform_fee=200,
            shipping_cost=100,
            payment_fee=50,
            other_cost=50,
            refund=100,
        )
        assert contribution == -100  # 1000 - (600+200+100+50+50) - 100 = -100

    def test_profit_margin_calculation(self):
        """Test profit margin percentage calculation."""
        engine = MetricsEngine()

        assert engine.calculate_profit_margin(contribution=200, net_sales=1000) == 20.0
        assert engine.calculate_profit_margin(contribution=0, net_sales=1000) == 0.0
        assert engine.calculate_profit_margin(contribution=-100, net_sales=1000) == -10.0
        assert engine.calculate_profit_margin(contribution=100, net_sales=0) == 0.0

    def test_profitability_status(self):
        """Test profitability status determination."""
        engine = MetricsEngine()

        assert engine.determine_profitability_status(20.0) == "Healthy"
        assert engine.determine_profitability_status(15.0) == "Healthy"
        assert engine.determine_profitability_status(14.9) == "At Risk"
        assert engine.determine_profitability_status(5.0) == "At Risk"
        assert engine.determine_profitability_status(0.0) == "At Risk"
        assert engine.determine_profitability_status(-5.0) == "Unprofitable"
        assert engine.determine_profitability_status(-50.0) == "Unprofitable"

    def test_product_metrics_calculation(self):
        """Test complete product metrics calculation."""
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
            platform_fee=1500,
            shipping_cost=500,
            payment_fee=250,
            other_cost=100,
            units_returned=5,
            refund_amount=500,
            units_cancelled=2,
        )

        assert metrics.sku == "SLP-1001"
        assert metrics.units_sold == 100
        assert metrics.net_sales_inr == 9500
        assert metrics.organic_units == 40
        assert metrics.organic_share_pct == 40.0
        assert metrics.roas == pytest.approx(5.7)
        assert metrics.return_rate_pct == 5.0
        assert metrics.cancellation_rate_pct == 2.0
        assert metrics.total_cost_inr == 5350
        assert metrics.contribution_inr == pytest.approx(3650)
        assert metrics.profit_margin_pct == pytest.approx(38.42, rel=0.01)
        assert metrics.profitability_status == "Healthy"

    def test_negative_margin_product(self):
        """Test handling of unprofitable products."""
        engine = MetricsEngine()

        metrics = engine.calculate_product_metrics(
            sku="SLP-2001",
            product_name="Unprofitable Product",
            units_sold=50,
            gross_sales=5000,
            net_sales=4500,
            discount=500,
            ad_spend=1500,
            ad_attributed_units=30,
            ad_attributed_sales=2700,
            product_cost=3000,
            platform_fee=1200,
            shipping_cost=400,
            payment_fee=200,
            other_cost=150,
            units_returned=3,
            refund_amount=500,
            units_cancelled=1,
        )

        assert metrics.contribution_inr < 0
        assert metrics.profit_margin_pct < 0
        assert metrics.profitability_status == "Unprofitable"

    def test_platform_metrics_aggregation(self):
        """Test platform-level metrics aggregation."""
        engine = MetricsEngine()

        product1 = engine.calculate_product_metrics(
            sku="SKU-1",
            product_name="Product 1",
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

        product2 = engine.calculate_product_metrics(
            sku="SKU-2",
            product_name="Product 2",
            units_sold=80,
            gross_sales=8000,
            net_sales=7600,
            discount=400,
            ad_spend=800,
            ad_attributed_units=40,
            ad_attributed_sales=2400,
            product_cost=2400,
            platform_fee=800,
            shipping_cost=400,
            payment_fee=200,
            other_cost=40,
            units_returned=2,
            refund_amount=200,
            units_cancelled=1,
        )

        platform = engine.calculate_platform_metrics(
            [product1, product2],
            platform_id="AMZ",
            platform_name="Amazon",
        )

        assert platform.platform_id == "AMZ"
        assert platform.total_units_sold == 180
        assert platform.total_net_sales_inr == pytest.approx(17100)
        assert platform.total_ad_spend_inr == 1800
        assert platform.total_returns == 7
        assert platform.total_cancellations == 3
        assert platform.product_count == 2
        assert platform.overall_profit_margin_pct > 0

    def test_empty_metrics_list(self):
        """Test platform aggregation with empty metrics list."""
        engine = MetricsEngine()

        platform = engine.calculate_platform_metrics([], "TEST", "Test Platform")

        assert platform.total_units_sold == 0
        assert platform.total_net_sales_inr == 0.0
        assert platform.product_count == 0
        assert platform.overall_profit_margin_pct == 0.0

    def test_trend_calculation(self):
        """Test trend analysis calculation."""
        engine = MetricsEngine()

        daily_values = [
            (date(2026, 8, 1), 100),
            (date(2026, 8, 2), 110),
            (date(2026, 8, 3), 120),
            (date(2026, 8, 4), 130),
            (date(2026, 8, 5), 140),
        ]

        trend = engine.calculate_trend(
            "sales",
            daily_values,
            date(2026, 8, 1),
            date(2026, 8, 5),
        )

        assert trend.metric_name == "sales"
        assert trend.days == 5
        assert trend.average_daily == 120.0
        assert trend.min_daily == 100.0
        assert trend.max_daily == 140.0
        assert trend.trend_direction == "upward"
        assert trend.trend_strength > 0

    def test_downward_trend(self):
        """Test downward trend detection."""
        engine = MetricsEngine()

        daily_values = [
            (date(2026, 8, 1), 100),
            (date(2026, 8, 2), 95),
            (date(2026, 8, 3), 90),
            (date(2026, 8, 4), 85),
            (date(2026, 8, 5), 80),
        ]

        trend = engine.calculate_trend(
            "sales",
            daily_values,
            date(2026, 8, 1),
            date(2026, 8, 5),
        )

        assert trend.trend_direction == "downward"
        assert trend.trend_strength > 0

    def test_stable_trend(self):
        """Test stable trend detection."""
        engine = MetricsEngine()

        daily_values = [
            (date(2026, 8, 1), 1000),
            (date(2026, 8, 2), 1000),
            (date(2026, 8, 3), 1000),
            (date(2026, 8, 4), 1000),
            (date(2026, 8, 5), 1000),
        ]

        trend = engine.calculate_trend(
            "sales",
            daily_values,
            date(2026, 8, 1),
            date(2026, 8, 5),
        )

        assert trend.trend_direction == "stable"
        assert trend.trend_strength == 0.0

    def test_trend_with_7_day_average(self):
        """Test 7-day average calculation."""
        engine = MetricsEngine()

        daily_values = [(date(2026, 8, 1) + __import__('datetime').timedelta(days=i), 100 + i * 10) for i in range(15)]

        trend = engine.calculate_trend(
            "sales",
            daily_values,
            date(2026, 8, 1),
            date(2026, 8, 15),
        )

        assert trend.day_7_average is not None
        assert trend.day_30_average is None


class TestMetricsEngineEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_zero_values_handling(self):
        """Test handling of zero values across metrics."""
        engine = MetricsEngine()

        metrics = engine.calculate_product_metrics(
            sku="ZERO-1",
            product_name="Zero Product",
            units_sold=0,
            gross_sales=0,
            net_sales=0,
            discount=0,
            ad_spend=0,
            ad_attributed_units=0,
            ad_attributed_sales=0,
            product_cost=0,
            platform_fee=0,
            shipping_cost=0,
            payment_fee=0,
            other_cost=0,
            units_returned=0,
            refund_amount=0,
            units_cancelled=0,
        )

        assert metrics.roas == 0.0
        assert metrics.acos_pct == 0.0
        assert metrics.organic_share_pct == 0.0
        assert metrics.return_rate_pct == 0.0
        assert metrics.contribution_inr == 0.0
        assert metrics.profit_margin_pct == 0.0

    def test_very_high_profitability(self):
        """Test handling of very profitable products."""
        engine = MetricsEngine()

        metrics = engine.calculate_product_metrics(
            sku="MARGIN-99",
            product_name="High Margin Product",
            units_sold=10,
            gross_sales=10000,
            net_sales=9900,
            discount=100,
            ad_spend=100,
            ad_attributed_units=5,
            ad_attributed_sales=5000,
            product_cost=1000,
            platform_fee=500,
            shipping_cost=100,
            payment_fee=50,
            other_cost=50,
            units_returned=0,
            refund_amount=0,
            units_cancelled=0,
        )

        assert metrics.profit_margin_pct > 50
        assert metrics.profitability_status == "Healthy"
        assert metrics.contribution_inr > 6000

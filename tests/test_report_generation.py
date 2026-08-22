"""Unit tests for Phase 4: Report Generation."""

import pytest
from datetime import date
from analytics.report_models import (
    Report,
    ReportType,
    OverallMetrics,
    ProductSection,
    PlatformSection,
)
from analytics.report_builder import ReportBuilder
from analytics.html_renderer import HTMLRenderer
from analytics.excel_renderer import ExcelRenderer
from analytics.pdf_renderer import PDFRenderer
from agents.report_agent import ReportAgent
from analytics.models import ProductMetrics
from analytics.metrics_engine import MetricsEngine


class TestReportModels:
    """Test report model creation and validation."""

    def test_create_overall_metrics(self):
        """Test creating overall metrics."""
        metrics = OverallMetrics(
            report_date=date(2026, 8, 21),
            total_orders=100,
            total_units_sold=500,
            total_net_sales_inr=50000,
            total_gross_sales_inr=52000,
            total_ad_spend_inr=5000,
            total_organic_sales_inr=30000,
            organic_share_pct=60.0,
            total_cost_inr=35000,
            total_contribution_inr=15000,
            overall_profit_margin_pct=30.0,
            total_return_rate_pct=5.0,
            total_cancellation_rate_pct=2.0,
            product_count=10,
            platform_count=3,
        )

        assert metrics.report_date == date(2026, 8, 21)
        assert metrics.total_orders == 100
        assert metrics.overall_profit_margin_pct == 30.0

    def test_create_product_section(self):
        """Test creating product section."""
        section = ProductSection(
            sku="SLP-1001",
            product_name="Contour Pillow",
            units_sold=100,
            net_sales_inr=10000,
            ad_spend_inr=1000,
            roas=5.0,
            acos_pct=10.0,
            organic_share_pct=40.0,
            profit_margin_pct=35.0,
            profitability_status="Healthy",
            return_rate_pct=5.0,
            cancellation_rate_pct=2.0,
        )

        assert section.sku == "SLP-1001"
        assert section.roas == 5.0
        assert section.profitability_status == "Healthy"

    def test_create_report(self):
        """Test creating a complete report."""
        metrics = OverallMetrics(
            report_date=date(2026, 8, 21),
            total_orders=100,
            total_units_sold=500,
            total_net_sales_inr=50000,
            total_gross_sales_inr=52000,
            total_ad_spend_inr=5000,
            total_organic_sales_inr=30000,
            organic_share_pct=60.0,
            total_cost_inr=35000,
            total_contribution_inr=15000,
            overall_profit_margin_pct=30.0,
            total_return_rate_pct=5.0,
            total_cancellation_rate_pct=2.0,
            product_count=10,
            platform_count=3,
        )

        report = Report(
            report_id="RPT-TEST001",
            report_date=date(2026, 8, 21),
            report_type=ReportType.PRODUCT_DAILY,
            title="Test Report",
            executive_summary="This is a test report.",
            overall_metrics=metrics,
        )

        assert report.report_id == "RPT-TEST001"
        assert report.report_type == ReportType.PRODUCT_DAILY
        assert len(report.product_sections) == 0


class TestReportBuilder:
    """Test report builder functionality."""

    def test_build_product_report(self):
        """Test building a product report."""
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

        report = ReportBuilder.build_product_report(
            report_date=date(2026, 8, 21),
            sku="SLP-1001",
            product_name="Contour Pillow",
            product_metrics=metrics,
        )

        assert report.report_type == ReportType.PRODUCT_DAILY
        assert report.overall_metrics.total_units_sold == 100
        assert report.overall_metrics.overall_profit_margin_pct > 0

    def test_product_report_has_required_sections(self):
        """Test that product report has all required sections."""
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

        report = ReportBuilder.build_product_report(
            report_date=date(2026, 8, 21),
            sku="SLP-1001",
            product_name="Contour Pillow",
            product_metrics=metrics,
        )

        assert report.overall_metrics is not None
        assert len(report.product_sections) > 0
        assert report.advertising_section is not None
        assert report.profitability_section is not None
        assert report.quality_section is not None

    def test_report_aggregations_are_correct(self):
        """Test that report aggregations sum correctly."""
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

        report = ReportBuilder.build_product_report(
            report_date=date(2026, 8, 21),
            sku="SLP-1001",
            product_name="Contour Pillow",
            product_metrics=metrics,
        )

        assert report.overall_metrics.total_net_sales_inr == metrics.net_sales_inr
        assert report.overall_metrics.total_ad_spend_inr == metrics.ad_spend_inr

    def test_unprofitable_product_report(self):
        """Test report for unprofitable product."""
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

        report = ReportBuilder.build_product_report(
            report_date=date(2026, 8, 21),
            sku="BAD-1",
            product_name="Unprofitable Product",
            product_metrics=metrics,
        )

        assert report.overall_metrics.overall_profit_margin_pct < 0
        assert "unprofitable" in report.executive_summary.lower()


class TestHTMLRenderer:
    """Test HTML report rendering."""

    def test_render_html_report(self):
        """Test rendering a report to HTML."""
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

        report = ReportBuilder.build_product_report(
            report_date=date(2026, 8, 21),
            sku="SLP-1001",
            product_name="Contour Pillow",
            product_metrics=metrics,
        )

        html = HTMLRenderer.render(report)

        assert isinstance(html, str)
        assert "<!DOCTYPE html>" in html
        assert report.title in html
        assert "Executive Summary" in html

    def test_html_contains_all_sections(self):
        """Test that HTML contains all report sections."""
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

        report = ReportBuilder.build_product_report(
            report_date=date(2026, 8, 21),
            sku="SLP-1001",
            product_name="Contour Pillow",
            product_metrics=metrics,
        )

        html = HTMLRenderer.render(report)

        assert "Overall Metrics" in html
        assert "Product Performance" in html
        assert "Advertising Performance" in html


class TestExcelRenderer:
    """Test Excel report rendering."""

    def test_excel_renderer_available(self):
        """Test that Excel renderer is available."""
        try:
            import openpyxl
            assert True
        except ImportError:
            pytest.skip("openpyxl not installed")

    def test_render_excel_report(self):
        """Test rendering a report to Excel."""
        try:
            import openpyxl
        except ImportError:
            pytest.skip("openpyxl not installed")

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

        report = ReportBuilder.build_product_report(
            report_date=date(2026, 8, 21),
            sku="SLP-1001",
            product_name="Contour Pillow",
            product_metrics=metrics,
        )

        excel_bytes = ExcelRenderer.render(report)

        assert isinstance(excel_bytes, bytes)
        assert len(excel_bytes) > 0


class TestPDFRenderer:
    """Test PDF report rendering."""

    def test_pdf_renderer_available(self):
        """Test that PDF renderer is available."""
        try:
            import reportlab
            assert True
        except ImportError:
            pytest.skip("reportlab not installed")

    def test_render_pdf_report(self):
        """Test rendering a report to PDF."""
        try:
            import reportlab
        except ImportError:
            pytest.skip("reportlab not installed")

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

        report = ReportBuilder.build_product_report(
            report_date=date(2026, 8, 21),
            sku="SLP-1001",
            product_name="Contour Pillow",
            product_metrics=metrics,
        )

        pdf_bytes = PDFRenderer.render(report)

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b"%PDF")


class TestReportAgent:
    """Test report agent LLM integration."""

    def test_fallback_result_structure(self):
        """Test that fallback result has correct structure."""
        agent = ReportAgent()
        result = agent._fallback_result()

        assert "executive_summary" in result
        assert "executive_narrative" in result
        assert "product_insights" in result
        assert "advertising_insights" in result
        assert "profitability_insights" in result
        assert "key_risks" in result
        assert "key_opportunities" in result

    def test_fallback_result_has_content(self):
        """Test that fallback result has non-empty content."""
        agent = ReportAgent()
        result = agent._fallback_result()

        for value in result.values():
            assert isinstance(value, str)
            assert len(value) > 0


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_report_with_empty_products(self):
        """Test report generation with no products."""
        metrics = OverallMetrics(
            report_date=date(2026, 8, 21),
            total_orders=0,
            total_units_sold=0,
            total_net_sales_inr=0,
            total_gross_sales_inr=0,
            total_ad_spend_inr=0,
            total_organic_sales_inr=0,
            organic_share_pct=0,
            total_cost_inr=0,
            total_contribution_inr=0,
            overall_profit_margin_pct=0,
            total_return_rate_pct=0,
            total_cancellation_rate_pct=0,
            product_count=0,
            platform_count=0,
        )

        report = Report(
            report_id="RPT-EMPTY",
            report_date=date(2026, 8, 21),
            report_type=ReportType.PRODUCT_DAILY,
            title="Empty Report",
            executive_summary="No data available.",
            overall_metrics=metrics,
        )

        assert len(report.product_sections) == 0
        assert report.overall_metrics.total_units_sold == 0

    def test_html_renders_empty_report(self):
        """Test that HTML renderer handles empty report."""
        metrics = OverallMetrics(
            report_date=date(2026, 8, 21),
            total_orders=0,
            total_units_sold=0,
            total_net_sales_inr=0,
            total_gross_sales_inr=0,
            total_ad_spend_inr=0,
            total_organic_sales_inr=0,
            organic_share_pct=0,
            total_cost_inr=0,
            total_contribution_inr=0,
            overall_profit_margin_pct=0,
            total_return_rate_pct=0,
            total_cancellation_rate_pct=0,
            product_count=0,
            platform_count=0,
        )

        report = Report(
            report_id="RPT-EMPTY",
            report_date=date(2026, 8, 21),
            report_type=ReportType.PRODUCT_DAILY,
            title="Empty Report",
            executive_summary="No data available.",
            overall_metrics=metrics,
        )

        html = HTMLRenderer.render(report)

        assert "Empty Report" in html
        assert "<!DOCTYPE html>" in html

    def test_report_financial_metrics_never_recalculated(self):
        """Test that report uses pre-calculated metrics exactly."""
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

        report = ReportBuilder.build_product_report(
            report_date=date(2026, 8, 21),
            sku="SLP-1001",
            product_name="Test Product",
            product_metrics=metrics,
        )

        assert report.product_sections[0].profit_margin_pct == metrics.profit_margin_pct
        assert report.product_sections[0].roas == metrics.roas
        assert report.product_sections[0].acos_pct == metrics.acos_pct
        assert report.overall_metrics.overall_profit_margin_pct == metrics.profit_margin_pct

"""
Tests for report data models.

Tests the OmniChannelReport and related data structures for:
- Correct initialization
- Field validation
- Data type correctness
- Required field checks
"""

import pytest
from datetime import datetime
from decimal import Decimal

from reports.models.report_models import (
    ProductMetrics,
    PlatformSummary,
    ConsolidatedProductMetrics,
    PnLStatement,
    ChannelEfficiency,
    ReportMetadata,
    ManagementSummary,
    OmniChannelReport,
)


class TestReportMetadata:
    """Test ReportMetadata model."""

    def test_metadata_creation(self):
        """Test metadata can be created with required fields."""
        metadata = ReportMetadata(
            report_type="Test Report",
            audit_date=datetime(2026, 8, 20),
            organization="Sleepsia India",
            scope="Test Scope",
            status="Test Status",
        )

        assert metadata.report_type == "Test Report"
        assert metadata.organization == "Sleepsia India"
        assert metadata.audit_date.year == 2026

    def test_metadata_with_periods(self):
        """Test metadata with report period."""
        metadata = ReportMetadata(
            report_type="Test Report",
            audit_date=datetime(2026, 8, 20),
            organization="Sleepsia",
            scope="All",
            status="Verified",
            report_period_start=datetime(2026, 8, 1),
            report_period_end=datetime(2026, 8, 20),
        )

        assert metadata.report_period_start is not None
        assert metadata.report_period_end is not None


class TestProductMetrics:
    """Test ProductMetrics model."""

    def test_product_metrics_creation(self):
        """Test product metrics creation."""
        metrics = ProductMetrics(
            sku="SLP-1001",
            product_name="Test Product",
            units_sold=100,
            gross_revenue=Decimal("5000"),
            returns_count=5,
            returns_percentage=Decimal("5.0"),
            organic_units=60,
            paid_units=40,
            ad_spend=Decimal("500"),
            net_ad_cost=Decimal("100"),
            tacos_percentage=Decimal("2.0"),
            net_profit=Decimal("1000"),
            margin_percentage=Decimal("20.0"),
        )

        assert metrics.sku == "SLP-1001"
        assert metrics.units_sold == 100
        assert metrics.gross_revenue == Decimal("5000")
        assert metrics.margin_percentage == Decimal("20.0")

    def test_product_metrics_with_platform(self):
        """Test product metrics with platform assignment."""
        metrics = ProductMetrics(
            sku="SLP-1001",
            product_name="Test Product",
            units_sold=100,
            gross_revenue=Decimal("5000"),
            returns_count=5,
            returns_percentage=Decimal("5.0"),
            organic_units=60,
            paid_units=40,
            ad_spend=Decimal("500"),
            net_ad_cost=Decimal("100"),
            tacos_percentage=Decimal("2.0"),
            net_profit=Decimal("1000"),
            margin_percentage=Decimal("20.0"),
            platform="Amazon",
        )

        assert metrics.platform == "Amazon"


class TestPlatformSummary:
    """Test PlatformSummary model."""

    def test_platform_summary_creation(self):
        """Test platform summary creation."""
        platform = PlatformSummary(
            platform_name="Amazon India",
            gross_revenue=Decimal("500000"),
            returns_refunds=Decimal("10000"),
            returns_percentage=Decimal("2.0"),
            net_revenue=Decimal("490000"),
            fulfillment_otif=Decimal("100.0"),
            ad_spend=Decimal("50000"),
            net_ad_cost=Decimal("60000"),
            tacos_percentage=Decimal("12.2"),
            net_profit=Decimal("100000"),
            margin_percentage=Decimal("20.4"),
        )

        assert platform.platform_name == "Amazon India"
        assert platform.net_revenue == Decimal("490000")
        assert len(platform.products) == 0  # Initially empty

    def test_platform_summary_with_products(self):
        """Test platform summary with product breakdown."""
        product = ProductMetrics(
            sku="SLP-1001",
            product_name="Test Product",
            units_sold=100,
            gross_revenue=Decimal("5000"),
            returns_count=5,
            returns_percentage=Decimal("5.0"),
            organic_units=60,
            paid_units=40,
            ad_spend=Decimal("500"),
            net_ad_cost=Decimal("100"),
            tacos_percentage=Decimal("2.0"),
            net_profit=Decimal("1000"),
            margin_percentage=Decimal("20.0"),
        )

        platform = PlatformSummary(
            platform_name="Amazon India",
            gross_revenue=Decimal("500000"),
            returns_refunds=Decimal("10000"),
            returns_percentage=Decimal("2.0"),
            net_revenue=Decimal("490000"),
            fulfillment_otif=Decimal("100.0"),
            ad_spend=Decimal("50000"),
            net_ad_cost=Decimal("60000"),
            tacos_percentage=Decimal("12.2"),
            net_profit=Decimal("100000"),
            margin_percentage=Decimal("20.4"),
            products=[product],
        )

        assert len(platform.products) == 1
        assert platform.products[0].sku == "SLP-1001"


class TestPnLStatement:
    """Test PnLStatement model."""

    def test_pnl_creation(self):
        """Test P&L statement creation."""
        pnl = PnLStatement(
            total_gross_gmv=Decimal("1000000"),
            less_returns_refunds=Decimal("20000"),
            less_returns_percentage=Decimal("2.0"),
            net_revenue=Decimal("980000"),
            less_cogs=Decimal("600000"),
            less_cogs_percentage=Decimal("60.0"),
            less_ad_spend=Decimal("200000"),
            less_ad_spend_percentage=Decimal("20.0"),
            less_commission_logistics=Decimal("100000"),
            less_commission_logistics_percentage=Decimal("10.0"),
            grand_net_operating_profit=Decimal("80000"),
            margin_percentage=Decimal("8.2"),
        )

        assert pnl.total_gross_gmv == Decimal("1000000")
        assert pnl.net_revenue == Decimal("980000")
        assert pnl.grand_net_operating_profit == Decimal("80000")


class TestOmniChannelReport:
    """Test complete OmniChannelReport model."""

    def test_report_validation_empty(self):
        """Test validation fails with empty report."""
        report = OmniChannelReport(
            metadata=ReportMetadata(
                report_type="Test",
                audit_date=datetime.now(),
                organization="Test",
                scope="Test",
                status="Test",
            )
        )

        with pytest.raises(ValueError, match="At least one platform"):
            report.validate()

    def test_report_with_metadata(self):
        """Test report creation with metadata."""
        metadata = ReportMetadata(
            report_type="Test Report",
            audit_date=datetime(2026, 8, 20),
            organization="Sleepsia",
            scope="All Channels",
            status="Verified",
        )

        report = OmniChannelReport(metadata=metadata)

        assert report.metadata.report_type == "Test Report"
        assert report.metadata.organization == "Sleepsia"

    def test_report_complete_validation(self):
        """Test complete report passes validation."""
        # This would require creating a full report with all sections
        # For now, just test that the structure is sound
        report = OmniChannelReport(
            metadata=ReportMetadata(
                report_type="Test",
                audit_date=datetime.now(),
                organization="Test",
                scope="Test",
                status="Test",
            ),
            platforms=[
                PlatformSummary(
                    platform_name="Test Platform",
                    gross_revenue=Decimal("1000"),
                    returns_refunds=Decimal("0"),
                    returns_percentage=Decimal("0"),
                    net_revenue=Decimal("1000"),
                    fulfillment_otif=Decimal("100"),
                    ad_spend=Decimal("0"),
                    net_ad_cost=Decimal("0"),
                    tacos_percentage=Decimal("0"),
                    net_profit=Decimal("100"),
                    margin_percentage=Decimal("10"),
                )
            ],
            consolidated_products=[
                ConsolidatedProductMetrics(
                    sku="TEST-1",
                    product_name="Test",
                    all_units=10,
                    total_gross=Decimal("1000"),
                    all_returns=0,
                    returns_percentage=Decimal("0"),
                    organic_paid_split="10/0",
                    total_ad_cost=Decimal("0"),
                    net_ad_cost=Decimal("0"),
                    tacos_percentage=Decimal("0"),
                    net_profit=Decimal("100"),
                    margin_percentage=Decimal("10"),
                    stock_dos=Decimal("30"),
                )
            ],
            pnl=PnLStatement(
                total_gross_gmv=Decimal("1000"),
                less_returns_refunds=Decimal("0"),
                less_returns_percentage=Decimal("0"),
                net_revenue=Decimal("1000"),
                less_cogs=Decimal("500"),
                less_cogs_percentage=Decimal("50"),
                less_ad_spend=Decimal("0"),
                less_ad_spend_percentage=Decimal("0"),
                less_commission_logistics=Decimal("100"),
                less_commission_logistics_percentage=Decimal("10"),
                grand_net_operating_profit=Decimal("400"),
                margin_percentage=Decimal("40"),
            ),
        )

        assert report.validate() is True


class TestManagementSummary:
    """Test ManagementSummary model."""

    def test_summary_creation(self):
        """Test management summary creation."""
        summary = ManagementSummary(
            summary_text="Test summary",
            key_findings=["Finding 1", "Finding 2"],
            recommendations=["Recommendation 1"],
            alerts=["Alert 1"],
            opportunities=["Opportunity 1"],
        )

        assert summary.summary_text == "Test summary"
        assert len(summary.key_findings) == 2
        assert len(summary.recommendations) == 1
        assert len(summary.alerts) == 1
        assert len(summary.opportunities) == 1

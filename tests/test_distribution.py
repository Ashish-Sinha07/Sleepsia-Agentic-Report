"""Unit tests for Phase 5: Distribution & Delivery."""

import pytest
from datetime import date, datetime
from analytics.distribution_config import (
    DistributionConfig,
    Schedule,
    Recipient,
    RetryConfiguration,
    RetryPolicy,
    ReportType,
    Channel,
    AttachmentType,
    Priority,
)
from analytics.delivery_state import DeliveryRecord, DeliveryState
from analytics.email_provider import MockEmailProvider, EmailMessage
from analytics.distribution_service import DistributionService
from analytics.attachment_service import AttachmentService
from analytics.report_models import Report, OverallMetrics
from analytics.metrics_engine import MetricsEngine
from analytics.report_builder import ReportBuilder


class TestDistributionConfig:
    """Test distribution configuration."""

    def test_create_distribution_config(self):
        """Test creating a distribution configuration."""
        config = DistributionConfig(
            config_id="config-1",
            report_type=ReportType.PRODUCT_DAILY,
            schedule=Schedule(time="09:00"),
            recipients=[
                Recipient(email="manager@example.com", name="Manager"),
                Recipient(email="analyst@example.com", name="Analyst"),
            ],
        )

        assert config.config_id == "config-1"
        assert len(config.recipients) == 2
        assert config.enabled is True

    def test_get_active_recipients(self):
        """Test getting active recipients."""
        config = DistributionConfig(
            config_id="config-1",
            report_type=ReportType.PRODUCT_DAILY,
            recipients=[
                Recipient(email="manager@example.com", priority_threshold=Priority.HIGH),
                Recipient(email="analyst@example.com", priority_threshold=Priority.LOW),
            ],
        )

        high_priority = config.get_active_recipients(Priority.CRITICAL)
        assert "manager@example.com" in high_priority
        assert "analyst@example.com" in high_priority

        low_priority = config.get_active_recipients(Priority.LOW)
        assert "analyst@example.com" in low_priority

    def test_blocked_recipients_excluded(self):
        """Test that blocked recipients are excluded."""
        config = DistributionConfig(
            config_id="config-1",
            report_type=ReportType.PRODUCT_DAILY,
            recipients=[
                Recipient(email="active@example.com"),
                Recipient(email="blocked@example.com"),
            ],
            blocked_recipients=["blocked@example.com"],
        )

        active = config.get_active_recipients()
        assert "active@example.com" in active
        assert "blocked@example.com" not in active


class TestDeliveryState:
    """Test delivery state machine."""

    def test_create_delivery_record(self):
        """Test creating a delivery record."""
        record = DeliveryRecord(
            delivery_id="DEL-001",
            report_id="RPT-001",
            report_type="product_daily",
            generation_timestamp=datetime.now(),
        )

        assert record.delivery_id == "DEL-001"
        assert record.current_state == DeliveryState.GENERATED

    def test_add_attempt(self):
        """Test adding delivery attempts."""
        record = DeliveryRecord(
            delivery_id="DEL-001",
            report_id="RPT-001",
            report_type="product_daily",
            generation_timestamp=datetime.now(),
        )

        attempt = record.add_attempt(
            state=DeliveryState.QUEUED,
            channel="email",
            recipient="test@example.com",
        )

        assert attempt.attempt_number == 1
        assert attempt.state == DeliveryState.QUEUED
        assert record.current_state == DeliveryState.QUEUED

    def test_delivery_tracking(self):
        """Test delivery success tracking."""
        record = DeliveryRecord(
            delivery_id="DEL-001",
            report_id="RPT-001",
            report_type="product_daily",
            generation_timestamp=datetime.now(),
            recipients=["test@example.com"],
        )

        record.add_attempt(
            state=DeliveryState.SENDING,
            channel="email",
            recipient="test@example.com",
        )

        record.add_attempt(
            state=DeliveryState.DELIVERED,
            channel="email",
            recipient="test@example.com",
            success=True,
        )

        assert record.is_successfully_delivered()
        assert record.first_delivered_at is not None

    def test_can_retry(self):
        """Test retry eligibility."""
        record = DeliveryRecord(
            delivery_id="DEL-001",
            report_id="RPT-001",
            report_type="product_daily",
            generation_timestamp=datetime.now(),
        )

        assert record.can_retry(3) is True

        record.add_attempt(
            state=DeliveryState.FAILED,
            channel="email",
            recipient="test@example.com",
            error_message="Connection timeout",
        )

        assert record.can_retry(3) is True
        assert record.can_retry(1) is False

    def test_max_retries_exceeded(self):
        """Test when max retries are exceeded."""
        record = DeliveryRecord(
            delivery_id="DEL-001",
            report_id="RPT-001",
            report_type="product_daily",
            generation_timestamp=datetime.now(),
        )

        for i in range(3):
            record.add_attempt(
                state=DeliveryState.RETRYING,
                channel="email",
                recipient="test@example.com",
                error_message=f"Attempt {i+1} failed",
            )

        assert record.can_retry(3) is False


class TestEmailProvider:
    """Test email provider abstraction."""

    def test_mock_email_provider(self):
        """Test mock email provider."""
        provider = MockEmailProvider()

        assert provider.validate_configuration() is True

        message = EmailMessage(
            subject="Test",
            body="Test body",
            recipients=["test@example.com"],
        )

        result = provider.send(message, "test@example.com")

        assert result.success is True
        assert provider.get_sent_count() == 1

    def test_mock_provider_failure(self):
        """Test mock provider can simulate failures."""
        provider = MockEmailProvider()
        provider.should_fail = True
        provider.failure_message = "Network error"

        message = EmailMessage(
            subject="Test",
            body="Test body",
            recipients=["test@example.com"],
        )

        result = provider.send(message, "test@example.com")

        assert result.success is False
        assert "Network error" in result.error


class TestDistributionService:
    """Test distribution service."""

    def test_create_delivery_record(self):
        """Test creating delivery record from report."""
        email_provider = MockEmailProvider()
        service = DistributionService(email_provider)

        config = DistributionConfig(
            config_id="config-1",
            report_type=ReportType.PRODUCT_DAILY,
            recipients=[Recipient(email="test@example.com")],
        )

        report = Report(
            report_id="RPT-001",
            report_date=date(2026, 8, 21),
            report_type="product_daily",
            title="Test Report",
            executive_summary="Test",
            overall_metrics=OverallMetrics(
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
            ),
        )

        record = service.create_delivery_record(report, config)

        assert record.report_id == "RPT-001"
        assert "test@example.com" in record.recipients

    def test_queue_delivery(self):
        """Test queueing a delivery."""
        email_provider = MockEmailProvider()
        service = DistributionService(email_provider)

        record = DeliveryRecord(
            delivery_id="DEL-001",
            report_id="RPT-001",
            report_type="product_daily",
            generation_timestamp=datetime.now(),
            recipients=["test@example.com"],
            distribution_enabled=True,
        )

        success = service.queue_delivery(record)

        assert success is True
        assert record.current_state == DeliveryState.QUEUED

    def test_queue_delivery_disabled(self):
        """Test queuing fails when distribution is disabled."""
        email_provider = MockEmailProvider()
        service = DistributionService(email_provider)

        record = DeliveryRecord(
            delivery_id="DEL-001",
            report_id="RPT-001",
            report_type="product_daily",
            generation_timestamp=datetime.now(),
            distribution_enabled=False,
        )

        success = service.queue_delivery(record)

        assert success is False

    def test_duplicate_delivery_prevention(self):
        """Test that duplicate deliveries are prevented."""
        email_provider = MockEmailProvider()
        service = DistributionService(email_provider)

        config = DistributionConfig(
            config_id="config-1",
            report_type=ReportType.PRODUCT_DAILY,
        )

        engine = MetricsEngine()
        metrics = engine.calculate_product_metrics(
            sku="SLP-1001",
            product_name="Test",
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
            product_name="Test",
            product_metrics=metrics,
        )

        record = DeliveryRecord(
            delivery_id="DEL-001",
            report_id=report.report_id,
            report_type="product_daily",
            generation_timestamp=datetime.now(),
            recipients=["test@example.com"],
            distribution_enabled=True,
        )

        record.add_attempt(
            state=DeliveryState.DELIVERED,
            channel="email",
            recipient="test@example.com",
            success=True,
        )

        is_duplicate = service._is_duplicate_delivery(record, "test@example.com")
        assert is_duplicate is True

    def test_retry_delivery(self):
        """Test delivery retry logic."""
        email_provider = MockEmailProvider()
        service = DistributionService(email_provider)

        config = DistributionConfig(
            config_id="config-1",
            report_type=ReportType.PRODUCT_DAILY,
        )

        engine = MetricsEngine()
        metrics = engine.calculate_product_metrics(
            sku="SLP-1001",
            product_name="Test",
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
            product_name="Test",
            product_metrics=metrics,
        )

        record = DeliveryRecord(
            delivery_id="DEL-001",
            report_id=report.report_id,
            report_type="product_daily",
            generation_timestamp=datetime.now(),
            recipients=["test@example.com"],
            distribution_enabled=True,
        )

        record.add_attempt(
            state=DeliveryState.FAILED,
            channel="email",
            recipient="test@example.com",
            error_message="Temporary failure",
        )

        success = service.retry_delivery(record, report, config, {}, max_retries=3)
        assert success is True

    def test_escalation_on_max_retries(self):
        """Test escalation when max retries exceeded."""
        email_provider = MockEmailProvider()
        service = DistributionService(email_provider)

        config = DistributionConfig(
            config_id="config-1",
            report_type=ReportType.PRODUCT_DAILY,
            retry_config=RetryConfiguration(
                max_retries=1,
                escalation_enabled=True,
                escalation_recipients=["escalation@example.com"],
            ),
        )

        record = DeliveryRecord(
            delivery_id="DEL-001",
            report_id="RPT-001",
            report_type="product_daily",
            generation_timestamp=datetime.now(),
            recipients=["test@example.com"],
            distribution_enabled=True,
        )

        report = Report(
            report_id="RPT-001",
            report_date=date(2026, 8, 21),
            report_type="product_daily",
            title="Test",
            executive_summary="Test",
            overall_metrics=OverallMetrics(
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
            ),
        )

        for i in range(2):
            record.add_attempt(
                state=DeliveryState.FAILED,
                channel="email",
                recipient="test@example.com",
                error_message="Persistent failure",
            )

        service._escalate_delivery(record, config)

        assert record.current_state == DeliveryState.ESCALATED
        assert record.escalation_notified is True


class TestAttachmentService:
    """Test attachment generation."""

    def test_generate_html_attachment(self):
        """Test HTML attachment generation."""
        engine = MetricsEngine()
        metrics = engine.calculate_product_metrics(
            sku="SLP-1001",
            product_name="Test",
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
            product_name="Test",
            product_metrics=metrics,
        )

        filename, content = AttachmentService.generate_html_attachment(report)

        assert filename.endswith(".html")
        assert len(content) > 0
        assert b"<!DOCTYPE html>" in content

    def test_generate_excel_attachment(self):
        """Test Excel attachment generation."""
        try:
            import openpyxl
        except ImportError:
            pytest.skip("openpyxl not installed")

        engine = MetricsEngine()
        metrics = engine.calculate_product_metrics(
            sku="SLP-1001",
            product_name="Test",
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
            product_name="Test",
            product_metrics=metrics,
        )

        filename, content = AttachmentService.generate_excel_attachment(report)

        assert filename.endswith(".xlsx")
        assert len(content) > 0

    def test_validate_attachments(self):
        """Test attachment validation."""
        attachments = {
            "report.html": b"<html>...</html>",
            "report.xlsx": b"PK...",
        }

        valid = AttachmentService.validate_attachments(attachments, ["html", "xlsx"])
        assert valid is True

        invalid = AttachmentService.validate_attachments(attachments, ["html", "pdf"])
        assert invalid is False


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_no_recipients(self):
        """Test handling reports with no recipients."""
        email_provider = MockEmailProvider()
        service = DistributionService(email_provider)

        config = DistributionConfig(
            config_id="config-1",
            report_type=ReportType.PRODUCT_DAILY,
            recipients=[],
        )

        report = Report(
            report_id="RPT-001",
            report_date=date(2026, 8, 21),
            report_type="product_daily",
            title="Test",
            executive_summary="Test",
            overall_metrics=OverallMetrics(
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
            ),
        )

        record = service.create_delivery_record(report, config)

        assert record.distribution_enabled is False

    def test_audit_logging(self):
        """Test audit log functionality."""
        email_provider = MockEmailProvider()
        service = DistributionService(email_provider)

        record = DeliveryRecord(
            delivery_id="DEL-001",
            report_id="RPT-001",
            report_type="product_daily",
            generation_timestamp=datetime.now(),
        )

        service.delivery_records["DEL-001"] = record

        audit_log = service.get_audit_log()
        assert isinstance(audit_log, list)

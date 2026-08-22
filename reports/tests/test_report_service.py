"""
Tests for Report Service.

Tests the main orchestration service for:
- Report validation
- PDF generation
- Excel generation
- File saving
- Metadata extraction
"""

import pytest
import os
import tempfile
from decimal import Decimal

from reports.report_service import ReportService
from reports.sample_data.sample_data_generator import generate_sample_report_data
from reports.models.report_models import OmniChannelReport, ReportMetadata
from datetime import datetime


class TestReportService:
    """Test ReportService class."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test outputs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def service(self, temp_dir):
        """Create report service with temp directory."""
        return ReportService(output_dir=temp_dir)

    @pytest.fixture
    def sample_report(self):
        """Generate sample report data."""
        return generate_sample_report_data()

    def test_service_initialization(self, temp_dir):
        """Test service initialization."""
        service = ReportService(output_dir=temp_dir)
        assert service.output_dir == temp_dir
        assert os.path.exists(temp_dir)

    def test_service_default_output_dir(self):
        """Test service uses default output directory."""
        service = ReportService()
        assert service.output_dir is not None
        assert os.path.exists(service.output_dir)

    def test_validate_report_data_success(self, service, sample_report):
        """Test successful report validation."""
        result = service.validate_report_data(sample_report)
        assert result is True

    def test_validate_report_data_invalid(self, service):
        """Test validation fails with invalid report."""
        invalid_report = OmniChannelReport(
            metadata=ReportMetadata(
                report_type="Test",
                audit_date=datetime.now(),
                organization="Test",
                scope="Test",
                status="Test",
            )
        )

        with pytest.raises(ValueError):
            service.validate_report_data(invalid_report)

    def test_generate_pdf_report(self, service, sample_report):
        """Test PDF generation returns bytes."""
        pdf_bytes = service.generate_pdf_report(sample_report)

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0

    def test_generate_excel_report(self, service, sample_report):
        """Test Excel generation returns bytes."""
        excel_bytes = service.generate_excel_report(sample_report)

        assert isinstance(excel_bytes, bytes)
        assert len(excel_bytes) > 0

    def test_save_pdf_report(self, service, sample_report, temp_dir):
        """Test PDF report is saved to disk."""
        pdf_bytes = service.generate_pdf_report(sample_report)
        filepath = service.save_pdf_report(sample_report, pdf_bytes)

        assert os.path.exists(filepath)
        assert filepath.endswith(".pdf")
        assert "Sleepsia" in filepath

        # Verify file contains data
        with open(filepath, "rb") as f:
            saved_bytes = f.read()
            assert saved_bytes == pdf_bytes

    def test_save_excel_report(self, service, sample_report, temp_dir):
        """Test Excel report is saved to disk."""
        excel_bytes = service.generate_excel_report(sample_report)
        filepath = service.save_excel_report(sample_report, excel_bytes)

        assert os.path.exists(filepath)
        assert filepath.endswith(".xlsx")
        assert "Sleepsia" in filepath

        # Verify file contains data
        with open(filepath, "rb") as f:
            saved_bytes = f.read()
            assert saved_bytes == excel_bytes

    def test_save_with_custom_filename(self, service, sample_report, temp_dir):
        """Test saving with custom filename."""
        pdf_bytes = service.generate_pdf_report(sample_report)
        custom_name = "custom_report.pdf"
        filepath = service.save_pdf_report(sample_report, pdf_bytes, filename=custom_name)

        assert filepath.endswith(custom_name)
        assert os.path.exists(filepath)

    def test_generate_and_save_reports_both(self, service, sample_report, temp_dir):
        """Test generating and saving both PDF and Excel."""
        results = service.generate_and_save_reports(
            sample_report, formats=["pdf", "excel"]
        )

        assert "pdf" in results
        assert "excel" in results
        assert os.path.exists(results["pdf"])
        assert os.path.exists(results["excel"])

    def test_generate_and_save_reports_pdf_only(self, service, sample_report, temp_dir):
        """Test generating and saving PDF only."""
        results = service.generate_and_save_reports(
            sample_report, formats=["pdf"]
        )

        assert "pdf" in results
        assert "excel" not in results
        assert os.path.exists(results["pdf"])

    def test_generate_and_save_reports_excel_only(self, service, sample_report, temp_dir):
        """Test generating and saving Excel only."""
        results = service.generate_and_save_reports(
            sample_report, formats=["excel"]
        )

        assert "excel" in results
        assert "pdf" not in results
        assert os.path.exists(results["excel"])

    def test_generate_and_save_reports_default(self, service, sample_report, temp_dir):
        """Test generating and saving with default formats (both)."""
        results = service.generate_and_save_reports(sample_report)

        assert "pdf" in results
        assert "excel" in results

    def test_get_report_metadata(self, service, sample_report):
        """Test extracting report metadata."""
        metadata = service.get_report_metadata(sample_report)

        assert metadata["report_type"] == sample_report.metadata.report_type
        assert metadata["organization"] == sample_report.metadata.organization
        assert metadata["total_platforms"] == len(sample_report.platforms)
        assert metadata["total_products"] == len(sample_report.consolidated_products)


class TestReportServiceIntegration:
    """Integration tests for complete report generation workflow."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test outputs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_complete_workflow(self, temp_dir):
        """Test complete workflow from data to saved files."""
        # Generate sample data (in real system, this comes from Analytics layer)
        report_data = generate_sample_report_data()

        # Create service
        service = ReportService(output_dir=temp_dir)

        # Validate
        assert service.validate_report_data(report_data)

        # Generate and save
        results = service.generate_and_save_reports(report_data)

        # Verify files exist and have content
        assert os.path.exists(results["pdf"])
        assert os.path.exists(results["excel"])

        pdf_size = os.path.getsize(results["pdf"])
        excel_size = os.path.getsize(results["excel"])

        assert pdf_size > 0
        assert excel_size > 0

        # Get metadata
        metadata = service.get_report_metadata(report_data)
        assert metadata["total_platforms"] > 0
        assert metadata["total_products"] > 0

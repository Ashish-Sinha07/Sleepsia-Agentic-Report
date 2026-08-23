"""
Report Service

Main orchestration service for report generation. Provides high-level API for:
- Generating PDF reports
- Generating Excel reports
- Validating report data
- Retrieving report metadata
- Listing generated reports

This service sits between the Analytics layer (which provides report data) and
the report generators (PDF and Excel).

Integration Flow:
1. Analytics layer computes metrics and returns OmniChannelReport
2. Report Service validates the data
3. Report Service generates PDF and/or Excel
4. Report Service returns file paths or bytes

The Report Service does NOT:
- Calculate metrics (Analytics layer does this)
- Handle file storage (handled by backend/API layer)
- Handle email/distribution (Power Automate does this)
"""

import os
from datetime import datetime
from typing import Optional, Tuple
from pathlib import Path
import logging

from reports.models.report_models import OmniChannelReport
from reports.generators.pdf_generator import PDFReportGenerator
from reports.generators.excel_generator import ExcelReportGenerator

logger = logging.getLogger(__name__)


class ReportService:
    """
    Service for generating and managing reports.

    Usage:
        # Create service
        service = ReportService()

        # Generate reports
        report_data = analytics_layer.get_omnichannel_report(start_date, end_date)
        service.validate_report_data(report_data)

        pdf_bytes = service.generate_pdf_report(report_data)
        excel_bytes = service.generate_excel_report(report_data)

        # Save to files
        pdf_path = service.save_pdf_report(report_data, pdf_bytes)
        excel_path = service.save_excel_report(report_data, excel_bytes)
    """

    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize Report Service.

        Args:
            output_dir: Directory to save generated reports. If None, uses default temp directory.
        """
        self.output_dir = output_dir or os.path.join(os.path.expanduser("~"), ".sleepsia", "reports")
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info(f"Report service initialized with output directory: {self.output_dir}")

    def validate_report_data(self, report_data: OmniChannelReport) -> bool:
        """
        Validate that report data is complete and well-formed.

        Checks:
        - All required fields are populated
        - No null values in critical metrics
        - Data types are correct
        - Totals are consistent

        Args:
            report_data: OmniChannelReport to validate

        Returns:
            True if valid, raises ValueError otherwise

        Raises:
            ValueError: If validation fails
        """
        try:
            # Use built-in validation
            report_data.validate()

            # Additional checks
            if not report_data.platforms:
                raise ValueError("At least one platform summary is required")

            for platform in report_data.platforms:
                if not platform.platform_name:
                    raise ValueError("Platform name is required")
                if platform.gross_revenue is None:
                    raise ValueError(f"Gross revenue is required for {platform.platform_name}")

            if not report_data.consolidated_products:
                raise ValueError("Consolidated product metrics are required")

            logger.info(f"Report data validation passed. Platforms: {len(report_data.platforms)}, Products: {len(report_data.consolidated_products)}")
            return True

        except Exception as e:
            logger.error(f"Report data validation failed: {e}")
            raise

    def generate_pdf_report(self, report_data: OmniChannelReport) -> bytes:
        """
        Generate PDF report from report data.

        Args:
            report_data: OmniChannelReport object

        Returns:
            PDF file content as bytes

        Raises:
            ValueError: If report data is invalid
            RuntimeError: If PDF generation fails
        """
        try:
            self.validate_report_data(report_data)

            logger.info("Generating PDF report...")
            generator = PDFReportGenerator(report_data)
            pdf_bytes = generator.generate()

            logger.info(f"PDF report generated successfully ({len(pdf_bytes)} bytes)")
            return pdf_bytes

        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            raise RuntimeError(f"Failed to generate PDF report: {e}") from e

    def generate_excel_report(self, report_data: OmniChannelReport) -> bytes:
        """
        Generate Excel report from report data.

        Args:
            report_data: OmniChannelReport object

        Returns:
            Excel file content as bytes

        Raises:
            ValueError: If report data is invalid
            RuntimeError: If Excel generation fails
        """
        try:
            self.validate_report_data(report_data)

            logger.info("Generating Excel report...")
            generator = ExcelReportGenerator(report_data)
            excel_bytes = generator.generate()

            logger.info(f"Excel report generated successfully ({len(excel_bytes)} bytes)")
            return excel_bytes

        except Exception as e:
            logger.error(f"Excel generation failed: {e}")
            raise RuntimeError(f"Failed to generate Excel report: {e}") from e

    def save_pdf_report(
        self,
        report_data: OmniChannelReport,
        pdf_bytes: bytes,
        filename: Optional[str] = None,
    ) -> str:
        """
        Save PDF report to disk.

        Args:
            report_data: Report metadata for naming
            pdf_bytes: PDF file content
            filename: Optional custom filename. If None, generates from metadata.

        Returns:
            Path to saved PDF file
        """
        if not filename:
            audit_date = report_data.metadata.audit_date.strftime("%Y-%m-%d")
            filename = f"Sleepsia_OmniChannel_Platform_Product_Audit_{audit_date}.pdf"

        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, "wb") as f:
            f.write(pdf_bytes)

        logger.info(f"PDF report saved to {filepath}")
        return filepath

    def save_excel_report(
        self,
        report_data: OmniChannelReport,
        excel_bytes: bytes,
        filename: Optional[str] = None,
    ) -> str:
        """
        Save Excel report to disk.

        Args:
            report_data: Report metadata for naming
            excel_bytes: Excel file content
            filename: Optional custom filename. If None, generates from metadata.

        Returns:
            Path to saved Excel file
        """
        if not filename:
            audit_date = report_data.metadata.audit_date.strftime("%Y-%m-%d")
            filename = f"Sleepsia_Report_ALL_{audit_date}.xlsx"

        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, "wb") as f:
            f.write(excel_bytes)

        logger.info(f"Excel report saved to {filepath}")
        return filepath

    def generate_and_save_reports(
        self,
        report_data: OmniChannelReport,
        formats: Optional[list] = None,
    ) -> dict:
        """
        Generate and save reports in specified formats.

        Convenience method to generate all requested formats and save to disk in one call.

        Args:
            report_data: OmniChannelReport object
            formats: List of formats to generate. Options: ['pdf', 'excel']. If None, generates both.

        Returns:
            Dictionary with keys 'pdf' and/or 'excel' containing file paths

        Example:
            >>> service = ReportService()
            >>> results = service.generate_and_save_reports(report_data)
            >>> print(results['pdf'])   # Path to PDF file
            >>> print(results['excel']) # Path to Excel file
        """
        if formats is None:
            formats = ["pdf", "excel"]

        results = {}

        try:
            if "pdf" in formats:
                pdf_bytes = self.generate_pdf_report(report_data)
                pdf_path = self.save_pdf_report(report_data, pdf_bytes)
                results["pdf"] = pdf_path

            if "excel" in formats:
                excel_bytes = self.generate_excel_report(report_data)
                excel_path = self.save_excel_report(report_data, excel_bytes)
                results["excel"] = excel_path

            logger.info(f"Reports generated and saved: {results}")
            return results

        except Exception as e:
            logger.error(f"Failed to generate reports: {e}")
            raise

    def get_report_metadata(self, report_data: OmniChannelReport) -> dict:
        """
        Extract metadata about the report.

        Args:
            report_data: OmniChannelReport object

        Returns:
            Dictionary with report metadata
        """
        return {
            "report_type": report_data.metadata.report_type,
            "audit_date": report_data.metadata.audit_date.isoformat(),
            "organization": report_data.metadata.organization,
            "scope": report_data.metadata.scope,
            "status": report_data.metadata.status,
            "total_platforms": len(report_data.platforms),
            "active_platforms": report_data.active_platforms,
            "total_products": len(report_data.consolidated_products),
            "total_skus": report_data.total_skus,
            "currency": report_data.currency,
            "period_start": report_data.metadata.report_period_start.isoformat() if report_data.metadata.report_period_start else None,
            "period_end": report_data.metadata.report_period_end.isoformat() if report_data.metadata.report_period_end else None,
        }

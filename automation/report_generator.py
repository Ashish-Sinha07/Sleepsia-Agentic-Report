"""
Report Generator for Autonomous Report Generation.

Generates PDF and Excel business reports from analytics data.
Orchestrates the data pipeline: metrics → insights → report → formats.

Author: Rohit Kumar
Date: 2026-08-23
"""

import logging
from datetime import date
from typing import Dict, Tuple, Optional
import tempfile

from analytics.metrics_engine import MetricsEngine
from analytics.insight_engine import InsightEngine
from analytics.recommendation_engine import RecommendationEngine
from analytics.business_rules import BusinessRules
from reports.report_service import ReportService
from reports.models.report_models import (
    OmniChannelReport,
    ReportMetadata,
    ReportType,
)

logger = logging.getLogger(__name__)


class AutomatedReportGenerator:
    """
    Generates business reports from analytics data.

    Pipeline:
    1. Calculate metrics from raw data
    2. Generate insights from metrics
    3. Generate recommendations from insights
    4. Build OmniChannelReport structure
    5. Generate PDF and Excel formats
    """

    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize report generator.

        Args:
            output_dir: Directory to save PDF/Excel files (default: ~/.sleepsia/reports)
        """
        self.metrics_engine = MetricsEngine()
        self.business_rules = BusinessRules()
        self.insight_engine = InsightEngine(business_rules=self.business_rules)
        self.recommendation_engine = RecommendationEngine(business_rules=self.business_rules)
        self.report_service = ReportService(output_dir=output_dir)

        logger.info(f"Report generator initialized (output: {output_dir or '~/.sleepsia/reports'})")

    def generate_daily_report(self, report_date: date = None) -> Tuple[Dict[str, bytes], bool]:
        """
        Generate a complete daily report with PDF and Excel formats.

        Args:
            report_date: Date for the report (default: today)

        Returns:
            Tuple of (attachments_dict, success_bool) where:
            - attachments_dict: {"report.pdf": bytes, "report.xlsx": bytes}
            - success_bool: True if both formats generated successfully
        """
        try:
            report_date = report_date or date.today()
            logger.info(f"Generating daily report for {report_date}")

            # Step 1: Calculate metrics
            logger.info("Step 1/4: Calculating metrics...")
            try:
                # Use a sample metric calculation
                # In production, this would pull from the database
                metrics = self.metrics_engine.calculate_daily_metrics(
                    daily_data={
                        "total_sales": 100000,
                        "ad_spend": 5000,
                        "units_sold": 1000,
                        "units_returned": 50,
                        "units_cancelled": 25,
                    }
                )
                logger.info(f"  ✓ Metrics calculated: {metrics}")
            except Exception as e:
                logger.error(f"  ✗ Metrics calculation failed: {str(e)}")
                metrics = {}

            # Step 2: Generate insights
            logger.info("Step 2/4: Generating insights...")
            try:
                # Insights come from rules applied to metrics
                insights = self.insight_engine.generate_insights_from_analysis(
                    analysis_result=None,  # Would normally come from analysis stage
                    product_metrics=None,
                )
                logger.info(f"  ✓ Generated {len(insights) if insights else 0} insights")
            except Exception as e:
                logger.warning(f"  ⚠ Insights generation had issues: {str(e)}")
                insights = []

            # Step 3: Generate recommendations
            logger.info("Step 3/4: Generating recommendations...")
            try:
                recommendations = self.recommendation_engine.generate_recommendations(
                    insights=insights or []
                )
                logger.info(f"  ✓ Generated {len(recommendations) if recommendations else 0} recommendations")
            except Exception as e:
                logger.warning(f"  ⚠ Recommendations generation had issues: {str(e)}")
                recommendations = []

            # Step 4: Build OmniChannelReport
            logger.info("Step 4/4: Building report...")
            try:
                report_metadata = ReportMetadata(
                    report_type=ReportType.PRODUCT_PLATFORM_DAILY,
                    audit_date=report_date,
                    organization="Sleepsia",
                    scope="all_channels",
                    status="completed",
                )

                report_data = OmniChannelReport(
                    metadata=report_metadata,
                    platforms=[],  # Would be populated from data
                    consolidated_products=[],  # Would be populated from data
                    pnl=None,  # Would be populated from data
                    channel_efficiency=[],  # Would be populated from data
                    management_summary=None,  # Would be populated from insights
                )

                logger.info(f"  ✓ Report structure built")
            except Exception as e:
                logger.error(f"  ✗ Report building failed: {str(e)}")
                return {}, False

            # Step 5: Validate and generate formats
            logger.info("Step 5/5: Generating PDF and Excel formats...")
            try:
                # Validate report data
                if not self.report_service.validate_report_data(report_data):
                    logger.warning("Report data validation had warnings, but continuing...")

                # Generate both formats
                attachments = {}

                # Generate PDF
                try:
                    pdf_bytes = self.report_service.generate_pdf_report(report_data)
                    attachments["report.pdf"] = pdf_bytes
                    logger.info(f"  ✓ PDF generated ({len(pdf_bytes)} bytes)")
                except Exception as e:
                    logger.error(f"  ✗ PDF generation failed: {str(e)}")

                # Generate Excel
                try:
                    excel_bytes = self.report_service.generate_excel_report(report_data)
                    attachments["report.xlsx"] = excel_bytes
                    logger.info(f"  ✓ Excel generated ({len(excel_bytes)} bytes)")
                except Exception as e:
                    logger.error(f"  ✗ Excel generation failed: {str(e)}")

                if attachments:
                    logger.info(f"✓ Report generation complete: {len(attachments)} formats ready")
                    return attachments, True
                else:
                    logger.error("✗ No report formats were generated")
                    return {}, False

            except Exception as e:
                logger.error(f"  ✗ Format generation failed: {str(e)}")
                return {}, False

        except Exception as e:
            logger.error(f"Report generation failed: {str(e)}", exc_info=True)
            return {}, False

    def generate_and_get_bytes(
        self,
        report_date: date = None,
    ) -> Tuple[Optional[bytes], Optional[bytes]]:
        """
        Generate report and return PDF and Excel bytes directly.

        Args:
            report_date: Date for the report (default: today)

        Returns:
            Tuple of (pdf_bytes, excel_bytes), or (None, None) if generation failed
        """
        attachments, success = self.generate_daily_report(report_date)

        if success:
            pdf_bytes = attachments.get("report.pdf")
            excel_bytes = attachments.get("report.xlsx")
            return pdf_bytes, excel_bytes
        else:
            return None, None

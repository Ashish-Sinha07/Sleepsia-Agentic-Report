#!/usr/bin/env python3
"""
Generate and Send Report On-Demand.

Generates and emails a report immediately (not on schedule).
Useful for testing and ad-hoc report generation.

Usage:
    # Generate today's report
    python backend/scripts/generate_report_now.py

    # Generate for a specific date
    python backend/scripts/generate_report_now.py --date 2026-08-22

    # Generate without sending (test only)
    python backend/scripts/generate_report_now.py --no-send

Author: Rohit Kumar
Date: 2026-08-23
"""

import sys
import os
import logging
import argparse
from pathlib import Path
from datetime import date, datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from automation.scheduler import ReportScheduler
from automation.report_generator import AutomatedReportGenerator
from automation.email_service import ReportEmailService
from backend.app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("generate_report.log"),
    ],
)

logger = logging.getLogger(__name__)


def main():
    """Generate a report on-demand."""
    parser = argparse.ArgumentParser(description="Generate and send reports on-demand")
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="Report date (YYYY-MM-DD format, default: today)",
    )
    parser.add_argument(
        "--no-send",
        action="store_true",
        help="Generate report without sending email",
    )

    args = parser.parse_args()

    try:
        logger.info("=" * 80)
        logger.info("Sleepsia On-Demand Report Generation")
        logger.info("=" * 80)

        # Parse report date
        if args.date:
            try:
                report_date = datetime.strptime(args.date, "%Y-%m-%d").date()
            except ValueError:
                logger.error(f"Invalid date format: {args.date}. Use YYYY-MM-DD")
                return 1
        else:
            report_date = date.today()

        logger.info(f"Report date: {report_date}")
        logger.info(f"Send email: {not args.no_send}")

        # Generate report
        logger.info("\n[1/2] Generating report...")
        generator = AutomatedReportGenerator()
        attachments, success = generator.generate_daily_report(report_date)

        if not success or not attachments:
            logger.error("✗ Report generation failed")
            return 1

        logger.info(f"✓ Report generated with {len(attachments)} formats")

        # Send email (if requested)
        if not args.no_send:
            logger.info("\n[2/2] Sending report via email...")
            email_service = ReportEmailService()

            email_success = email_service.send_report(
                subject=f"Sleepsia Daily Report - {report_date}",
                body=f"""
Dear Recipient,

Please find attached your business report for {report_date}.

Report includes:
- Platform performance metrics
- Product performance analysis
- Advertising ROI and efficiency
- Profitability analysis
- Key recommendations

If you have any questions, please reach out.

Best regards,
Sleepsia Analytics System
                """.strip(),
                recipients=[settings.REPORT_RECIPIENT_EMAIL],
                cc=settings.REPORT_CC_EMAILS.split(",") if settings.REPORT_CC_EMAILS else None,
                bcc=settings.REPORT_BCC_EMAILS.split(",") if settings.REPORT_BCC_EMAILS else None,
                attachments=attachments,
            )

            if email_success:
                logger.info("✓ Email sent successfully")
            else:
                logger.error("✗ Email send failed")

            logger.info("=" * 80)
            result = email_success
        else:
            logger.info("(Skipped email send as requested)")
            logger.info("=" * 80)
            result = success

        return 0 if result else 1

    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

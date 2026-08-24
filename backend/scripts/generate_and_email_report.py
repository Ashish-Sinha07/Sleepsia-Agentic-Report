#!/usr/bin/env python3
"""
Generate comprehensive business reports (PDF, Excel, JSON) and send via email.

Generates a complete business report with:
- PDF formatted report (management-friendly)
- Excel data sheets (detailed analysis)
- JSON data (raw structured data)

All files are sent as email attachments.

Usage:
    python generate_and_email_report.py
    python generate_and_email_report.py --date 2026-08-24
    python generate_and_email_report.py --date 2026-08-24 --email user@example.com
"""

import sys
import logging
from datetime import date, datetime, timedelta
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.app.database import SessionLocal
from backend.app.config import settings
from automation.enhanced_report_generator import EnhancedReportGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Generate and email comprehensive reports."""
    parser = argparse.ArgumentParser(
        description="Generate comprehensive business reports (PDF, Excel, JSON) and send via email"
    )
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="Report date (YYYY-MM-DD format, default: today)"
    )
    parser.add_argument(
        "--email",
        type=str,
        default=None,
        help="Email recipient (default: from settings)"
    )
    parser.add_argument(
        "--cc",
        type=str,
        default=None,
        help="CC recipients (comma-separated)"
    )
    parser.add_argument(
        "--no-pdf",
        action="store_true",
        help="Skip PDF generation"
    )
    parser.add_argument(
        "--no-excel",
        action="store_true",
        help="Skip Excel generation"
    )
    parser.add_argument(
        "--send",
        action="store_true",
        default=True,
        help="Send email after generation (default: true)"
    )

    args = parser.parse_args()

    # Parse date
    if args.date:
        try:
            report_date = datetime.strptime(args.date, "%Y-%m-%d").date()
        except ValueError:
            logger.error(f"Invalid date format: {args.date}. Use YYYY-MM-DD")
            return 1
    else:
        report_date = date.today()

    # Get database session
    db = SessionLocal()

    try:
        logger.info("=" * 80)
        logger.info("COMPREHENSIVE REPORT GENERATION AND EMAIL DISTRIBUTION")
        logger.info("=" * 80)
        logger.info(f"Date: {report_date}")
        logger.info(f"Generate PDF: {not args.no_pdf}")
        logger.info(f"Generate Excel: {not args.no_excel}")
        logger.info(f"Send Email: {args.send}")
        logger.info("=" * 80)

        # Initialize report generator
        generator = EnhancedReportGenerator(db=db)

        # Generate reports in all formats
        result = generator.generate_comprehensive_report(
            report_type="executive_summary",
            start_date=report_date,
            end_date=report_date,
            include_pdf=not args.no_pdf,
            include_excel=not args.no_excel,
        )

        if not result.get("success"):
            logger.error(f"Report generation failed: {result.get('error')}")
            return 1

        report_id = result.get("report_id")
        logger.info(f"\nReport generated successfully: {report_id}")
        logger.info(f"Formats created: {list(result.get('formats', {}).keys())}")

        # Send email if requested
        if args.send:
            # Determine recipients
            recipients = [args.email] if args.email else [settings.REPORT_RECIPIENT_EMAIL]
            cc_list = args.cc.split(",") if args.cc else (
                settings.REPORT_CC_EMAILS.split(",") if settings.REPORT_CC_EMAILS else None
            )
            bcc_list = settings.REPORT_BCC_EMAILS.split(",") if settings.REPORT_BCC_EMAILS else None

            logger.info(f"\nSending report to: {recipients}")
            if cc_list:
                logger.info(f"CC: {cc_list}")

            email_success = generator.send_report_via_email(
                report_id=report_id,
                recipients=recipients,
                cc=cc_list,
                bcc=bcc_list,
            )

            if email_success:
                logger.info("\n" + "=" * 80)
                logger.info("REPORT GENERATION AND DISTRIBUTION COMPLETE")
                logger.info("=" * 80)
                logger.info(f"Report ID: {report_id}")
                logger.info(f"Files: {', '.join(result.get('formats', {}).keys())}")
                logger.info(f"Recipients: {recipients}")
                logger.info("=" * 80)
                return 0
            else:
                logger.error("Email sending failed")
                return 1
        else:
            logger.info("\n" + "=" * 80)
            logger.info("REPORT GENERATION COMPLETE (EMAIL NOT SENT)")
            logger.info("=" * 80)
            logger.info(f"Report ID: {report_id}")
            logger.info(f"Files: {', '.join(result.get('formats', {}).keys())}")
            logger.info("Files are ready in: backend/reports/")
            logger.info("=" * 80)
            return 0

    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
        return 1

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return 1

    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())

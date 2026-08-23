#!/usr/bin/env python3
"""
Manual Report Generation Script.

Generates and distributes a report on-demand (not on schedule).
Useful for immediate report generation, testing, or ad-hoc execution.

Usage:
    python backend/scripts/run_manual_report.py [--date YYYY-MM-DD] [--no-send]

Arguments:
    --date YYYY-MM-DD: Report date (default: today)
    --no-send: Generate report without sending email (for testing)

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

from analytics.scheduler import ReportScheduler
from backend.app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("manual_report.log"),
    ],
)

logger = logging.getLogger(__name__)


def main():
    """Execute a manual on-demand report generation."""
    parser = argparse.ArgumentParser(
        description="Generate and distribute reports on-demand",
    )
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
        logger.info("Sleepsia Manual Report Generation")
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

        # Create scheduler instance
        checkpoint_dir = "./checkpoints"
        Path(checkpoint_dir).mkdir(parents=True, exist_ok=True)

        scheduler = ReportScheduler(checkpoint_dir=checkpoint_dir)

        # Log configuration
        logger.info(f"SMTP Host: {settings.SMTP_HOST}:{settings.SMTP_PORT}")
        logger.info(f"From: {settings.SMTP_FROM_EMAIL}")
        logger.info(f"Recipient: {settings.REPORT_RECIPIENT_EMAIL}")

        # Execute the report
        logger.info("Executing report generation...")
        result = scheduler._execute_daily_report()

        logger.info("=" * 80)
        logger.info("Report generation complete!")

        if result.get("status") == "failed":
            logger.error(f"Report generation failed: {result.get('error')}")
            return 1

        logger.info("Report generation successful")
        logger.info("=" * 80)

        return 0

    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

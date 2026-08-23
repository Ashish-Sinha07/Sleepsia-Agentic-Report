#!/usr/bin/env python3
"""
Start the Autonomous Report Scheduler.

Runs the daily report generation and email distribution system in the background.

Usage:
    python backend/scripts/start_report_scheduler.py

Environment variables (from .env):
    REPORT_SCHEDULE_HOUR: Hour to run (0-23, default 6)
    REPORT_SCHEDULE_MINUTE: Minute to run (0-59, default 0)
    REPORT_RECIPIENT_EMAIL: Primary recipient
    REPORT_CC_EMAILS: CC recipients (comma-separated, optional)
    REPORT_BCC_EMAILS: BCC recipients (comma-separated, optional)
    SMTP_HOST, SMTP_USERNAME, SMTP_PASSWORD: Email config

Author: Rohit Kumar
Date: 2026-08-23
"""

import sys
import os
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from automation.scheduler import start_daily_scheduler
from backend.app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("report_scheduler.log"),
    ],
)

logger = logging.getLogger(__name__)


def main():
    """Start the report scheduler."""
    try:
        logger.info("=" * 80)
        logger.info("Sleepsia Autonomous Report Scheduler")
        logger.info("=" * 80)

        # Log configuration
        logger.info(f"Schedule: {settings.REPORT_SCHEDULE_HOUR:02d}:{settings.REPORT_SCHEDULE_MINUTE:02d} (UTC)")
        logger.info(f"Recipient: {settings.REPORT_RECIPIENT_EMAIL}")
        if settings.REPORT_CC_EMAILS:
            logger.info(f"CC: {settings.REPORT_CC_EMAILS}")
        if settings.REPORT_BCC_EMAILS:
            logger.info(f"BCC: {settings.REPORT_BCC_EMAILS}")
        logger.info(f"SMTP: {settings.SMTP_FROM_EMAIL} via {settings.SMTP_HOST}:{settings.SMTP_PORT}")

        # Start scheduler
        scheduler = start_daily_scheduler(
            hour=settings.REPORT_SCHEDULE_HOUR,
            minute=settings.REPORT_SCHEDULE_MINUTE,
            day_of_week="mon-fri",
        )

        next_run = scheduler.get_next_run()
        logger.info(f"Next run: {next_run}")
        logger.info("=" * 80)
        logger.info("Scheduler is running. Press Ctrl+C to stop.")
        logger.info("=" * 80)

        # Keep running
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\nShutdown signal received...")
            scheduler.stop()
            logger.info("Scheduler stopped gracefully")

        return 0

    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

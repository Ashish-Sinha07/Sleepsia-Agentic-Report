#!/usr/bin/env python3
"""
Autonomous Report Scheduler Startup Script.

This script starts the APScheduler-based report generation and distribution system.
It runs continuously in the background, executing the full reporting pipeline
on the configured schedule.

Usage:
    python backend/scripts/run_autonomous_scheduler.py

Environment variables (from .env):
    REPORT_SCHEDULE_HOUR: Hour to run reports (0-23, default 6)
    REPORT_SCHEDULE_MINUTE: Minute to run reports (0-59, default 0)
    REPORT_RECIPIENT_EMAIL: Email address for report distribution
    SMTP_*: Email configuration

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

from analytics.scheduler import schedule_daily_reports
from backend.app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("reports_scheduler.log"),
    ],
)

logger = logging.getLogger(__name__)


def main():
    """Start the autonomous report scheduler."""
    try:
        logger.info("=" * 80)
        logger.info("Sleepsia Autonomous Report Scheduler")
        logger.info("=" * 80)

        # Log configuration
        logger.info(f"Schedule: Daily at {settings.REPORT_SCHEDULE_HOUR:02d}:{settings.REPORT_SCHEDULE_MINUTE:02d}")
        logger.info(f"Recipient: {settings.REPORT_RECIPIENT_EMAIL}")
        logger.info(f"SMTP Host: {settings.SMTP_HOST}:{settings.SMTP_PORT}")
        logger.info(f"From: {settings.SMTP_FROM_EMAIL}")

        # Create checkpoint directory if it doesn't exist
        checkpoint_dir = "./checkpoints"
        Path(checkpoint_dir).mkdir(parents=True, exist_ok=True)
        logger.info(f"Checkpoint directory: {checkpoint_dir}")

        # Schedule the daily report
        scheduler = schedule_daily_reports(
            hour=settings.REPORT_SCHEDULE_HOUR,
            minute=settings.REPORT_SCHEDULE_MINUTE,
            day_of_week="mon-fri",  # Weekdays only
            timezone="UTC",
        )

        # Start the scheduler
        scheduler.start()

        # Keep the scheduler running
        logger.info("Scheduler is running. Press Ctrl+C to stop.")
        logger.info("=" * 80)

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

"""
Autonomous Report Scheduler.

Runs the full report generation and email distribution pipeline on a schedule.
Uses APScheduler for reliable background scheduling.

Author: Rohit Kumar
Date: 2026-08-23
"""

import logging
from datetime import date, datetime
from pathlib import Path
import pytz
from sqlalchemy.orm import Session
from sqlalchemy import text

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from automation.email_service import ReportEmailService
from backend.app.config import settings
from backend.app.database import SessionLocal
from backend.app.services.report_service import ReportService

logger = logging.getLogger(__name__)


class ReportScheduler:
    """
    Schedules autonomous daily report generation and email distribution.

    Workflow:
    1. Read validated data from MySQL
    2. Generate a deterministic database-backed report
    3. Optionally send the report via email
    3. Run on configured schedule (default: 6 AM daily, Monday-Friday)
    """

    def __init__(self):
        """Initialize the scheduler with all components."""
        self.scheduler = BackgroundScheduler()
        self.email_service = ReportEmailService()
        self.timezone = pytz.timezone(settings.AUTOMATION_TIMEZONE)

        logger.info("Report scheduler initialized")

    def run_report_pipeline(self) -> bool:
        """
        Execute the complete report generation and distribution pipeline.

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("=" * 80)
            logger.info(f"Starting report pipeline at {datetime.now(self.timezone).isoformat()}")
            logger.info("=" * 80)

            db: Session = SessionLocal()
            try:
                latest_date = db.execute(
                    text("SELECT MAX(sale_date) FROM daily_sales")
                ).scalar()
                report_date = latest_date or date.today()
                logger.info("\n[1/2] Generating database-backed report...")
                report = ReportService.generate_report(
                    db=db,
                    report_type="executive_summary",
                    start_date=report_date,
                    end_date=report_date,
                    format="json",
                )
            finally:
                db.close()

            logger.info(f"Report generated: {report['report_id']}")

            if not settings.SEND_REPORT_EMAIL:
                logger.info("[2/2] Email disabled; report saved locally")
                return True

            logger.info("\n[2/2] Sending report via email...")
            report_path = Path(ReportService.REPORTS_DIR) / f"{report['report_id']}.json"
            email_success = self.email_service.send_report(
                subject=f"Sleepsia Daily Report - {report_date}",
                body="""
Dear Recipient,

Please find attached your daily business report for Sleepsia.

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
                attachments={report_path.name: report_path.read_bytes()},
            )

            if email_success:
                logger.info("[OK] Email sent successfully")
            else:
                logger.error("[FAIL] Email send failed")

            logger.info("=" * 80)
            logger.info(f"Report pipeline complete at {datetime.now(self.timezone).isoformat()}")
            logger.info("=" * 80)

            return email_success

        except Exception as e:
            logger.error(f"Report pipeline failed: {str(e)}", exc_info=True)
            return False

    def schedule_daily(
        self,
        hour: int = None,
        minute: int = None,
        day_of_week: str = "mon-fri",
    ) -> None:
        """
        Schedule the report pipeline to run daily.

        Args:
            hour: Hour to run (0-23, default from REPORT_SCHEDULE_HOUR setting)
            minute: Minute to run (0-59, default from REPORT_SCHEDULE_MINUTE setting)
            day_of_week: Cron day-of-week pattern (default weekdays only)
        """
        hour = settings.REPORT_SCHEDULE_HOUR if hour is None else hour
        minute = settings.REPORT_SCHEDULE_MINUTE if minute is None else minute

        trigger = CronTrigger(
            hour=hour,
            minute=minute,
            day_of_week=day_of_week,
            timezone=self.timezone,
        )

        logger.info(f"Scheduling report pipeline for {hour:02d}:{minute:02d} {day_of_week}")

        self.scheduler.add_job(
            self.run_report_pipeline,
            trigger=trigger,
            id="daily_report",
            name="Daily Report Generation & Distribution",
            replace_existing=True,
        )

        logger.info("Schedule configured")

    def start(self) -> None:
        """Start the scheduler in background."""
        if self.scheduler.running:
            logger.warning("Scheduler already running")
            return

        logger.info("Starting scheduler...")
        self.scheduler.start()
        logger.info("✓ Scheduler started (running in background)")

    def stop(self) -> None:
        """Stop the scheduler."""
        if not self.scheduler.running:
            logger.warning("Scheduler not running")
            return

        logger.info("Stopping scheduler...")
        self.scheduler.shutdown()
        logger.info("✓ Scheduler stopped")

    def execute_now(self) -> bool:
        """Manually trigger report generation (for testing)."""
        logger.info("Manually triggering report pipeline...")
        return self.run_report_pipeline()

    def is_running(self) -> bool:
        """Check if scheduler is active."""
        return self.scheduler.running

    def get_next_run(self) -> datetime:
        """Get the next scheduled report time."""
        job = self.scheduler.get_job("daily_report")
        if job:
            return job.next_run_time
        return None


# Module-level scheduler instance
_scheduler = None


def get_scheduler() -> ReportScheduler:
    """Get or create the global scheduler instance."""
    global _scheduler
    if _scheduler is None:
        _scheduler = ReportScheduler()
    return _scheduler


def start_daily_scheduler(
    hour: int = None,
    minute: int = None,
    day_of_week: str = "mon-fri",
) -> ReportScheduler:
    """
    Convenience function to start the daily report scheduler.

    Args:
        hour: Hour to run (default from settings)
        minute: Minute to run (default from settings)
        day_of_week: Cron day pattern (default weekdays)

    Returns:
        The configured ReportScheduler instance
    """
    scheduler = get_scheduler()
    scheduler.schedule_daily(hour=hour, minute=minute, day_of_week=day_of_week)
    scheduler.start()
    return scheduler

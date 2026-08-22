"""Distribution configuration models."""

from dataclasses import dataclass, field
from datetime import time
from enum import Enum
from typing import Optional


class ReportType(str, Enum):
    """Report types for distribution."""
    PRODUCT_PLATFORM_DAILY = "product_platform_daily"
    PRODUCT_DAILY = "product_daily"
    PLATFORM_DAILY = "platform_daily"
    MANAGEMENT_DAILY_SUMMARY = "management_daily_summary"


class Channel(str, Enum):
    """Delivery channels."""
    EMAIL = "email"
    WEBHOOK = "webhook"
    SLACK = "slack"
    TEAMS = "teams"


class AttachmentType(str, Enum):
    """Supported attachment types."""
    PDF = "pdf"
    XLSX = "xlsx"
    CSV = "csv"
    HTML = "html"


class Priority(str, Enum):
    """Distribution priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RetryPolicy(str, Enum):
    """Retry policies."""
    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    FIXED = "fixed"


@dataclass
class Schedule:
    """Report delivery schedule."""
    enabled: bool = True
    frequency: str = "daily"  # daily, weekly, monthly, once
    time: str = "09:00"  # HH:MM format
    timezone: str = "UTC"
    days_of_week: list[str] = field(default_factory=lambda: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
    cron_expression: Optional[str] = None


@dataclass
class RetryConfiguration:
    """Retry and escalation settings."""
    max_retries: int = 3
    retry_policy: RetryPolicy = RetryPolicy.EXPONENTIAL
    initial_delay_seconds: int = 60
    max_delay_seconds: int = 3600
    escalation_recipients: list[str] = field(default_factory=list)
    escalation_enabled: bool = True


@dataclass
class Recipient:
    """Email recipient configuration."""
    email: str
    name: Optional[str] = None
    priority_threshold: Optional[Priority] = None


@dataclass
class DistributionConfig:
    """Configuration for a single distribution rule."""

    config_id: str
    report_type: ReportType

    enabled: bool = True

    schedule: Schedule = field(default_factory=Schedule)

    channels: list[Channel] = field(default_factory=lambda: [Channel.EMAIL])
    attachment_types: list[AttachmentType] = field(default_factory=lambda: [AttachmentType.PDF])

    recipients: list[Recipient] = field(default_factory=list)
    cc_recipients: list[str] = field(default_factory=list)
    bcc_recipients: list[str] = field(default_factory=list)

    retry_config: RetryConfiguration = field(default_factory=RetryConfiguration)

    subject_template: str = "Sleepsia Daily Report: {report_type}"
    body_template: str = "Please find attached the daily report."

    blocked_recipients: list[str] = field(default_factory=list)
    tags: dict[str, str] = field(default_factory=dict)

    def is_scheduled_now(self, current_time: time, current_timezone: str) -> bool:
        """Check if report should be sent at current time."""
        if not self.enabled or not self.schedule.enabled:
            return False

        # Simplified check - in production would use pytz and proper scheduling
        config_time = time.fromisoformat(self.schedule.time)
        return current_time >= config_time and current_time < time(
            hour=config_time.hour,
            minute=min(config_time.minute + 5, 59),
        )

    def should_escalate(self) -> bool:
        """Check if escalation is configured."""
        return (
            self.retry_config.escalation_enabled
            and len(self.retry_config.escalation_recipients) > 0
        )

    def get_active_recipients(self, priority: Priority = Priority.MEDIUM) -> list[str]:
        """Get recipients that should receive this report."""
        active = []

        for recipient in self.recipients:
            if recipient.email in self.blocked_recipients:
                continue

            if recipient.priority_threshold is None:
                active.append(recipient.email)
            elif priority.value in [
                Priority.CRITICAL.value,
                Priority.HIGH.value,
                Priority.MEDIUM.value,
                Priority.LOW.value,
            ]:
                threshold_rank = ["low", "medium", "high", "critical"].index(
                    recipient.priority_threshold.value
                )
                current_rank = ["low", "medium", "high", "critical"].index(priority.value)
                if current_rank >= threshold_rank:
                    active.append(recipient.email)

        return active

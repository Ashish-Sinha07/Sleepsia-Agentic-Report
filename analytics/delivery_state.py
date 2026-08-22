"""Delivery state machine and audit logging."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class DeliveryState(str, Enum):
    """Delivery state machine states."""
    GENERATED = "generated"
    QUEUED = "queued"
    SENDING = "sending"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"
    ESCALATED = "escalated"


@dataclass
class DeliveryAttempt:
    """Record of a single delivery attempt."""
    attempt_number: int
    timestamp: datetime
    state: DeliveryState
    channel: str
    recipient: str
    success: bool = False
    error_message: Optional[str] = None


@dataclass
class DeliveryRecord:
    """Complete delivery tracking record."""
    delivery_id: str
    report_id: str
    report_type: str

    generation_timestamp: datetime
    generation_success: bool = True
    generation_error: Optional[str] = None

    distribution_enabled: bool = True

    current_state: DeliveryState = DeliveryState.GENERATED

    recipients: list[str] = field(default_factory=list)
    cc_recipients: list[str] = field(default_factory=list)
    bcc_recipients: list[str] = field(default_factory=list)

    channel: str = "email"
    attachment_types: list[str] = field(default_factory=list)

    attempts: list[DeliveryAttempt] = field(default_factory=list)

    first_queued_at: Optional[datetime] = None
    first_delivered_at: Optional[datetime] = None
    last_attempt_at: Optional[datetime] = None

    escalation_notified: bool = False
    escalation_recipients: list[str] = field(default_factory=list)

    tags: dict[str, str] = field(default_factory=dict)

    def add_attempt(
        self,
        state: DeliveryState,
        channel: str,
        recipient: str,
        success: bool = False,
        error_message: Optional[str] = None,
    ) -> DeliveryAttempt:
        """Record a delivery attempt."""
        attempt = DeliveryAttempt(
            attempt_number=len(self.attempts) + 1,
            timestamp=datetime.now(),
            state=state,
            channel=channel,
            recipient=recipient,
            success=success,
            error_message=error_message,
        )

        self.attempts.append(attempt)
        self.current_state = state
        self.last_attempt_at = attempt.timestamp

        if state == DeliveryState.QUEUED and self.first_queued_at is None:
            self.first_queued_at = attempt.timestamp

        if state == DeliveryState.DELIVERED and self.first_delivered_at is None:
            self.first_delivered_at = attempt.timestamp

        return attempt

    def is_successfully_delivered(self) -> bool:
        """Check if report was successfully delivered."""
        return (
            self.current_state == DeliveryState.DELIVERED
            and self.first_delivered_at is not None
        )

    def can_retry(self, max_retries: int) -> bool:
        """Check if delivery can be retried."""
        return len(self.attempts) < max_retries and not self.is_successfully_delivered()

    def get_delivery_duration_seconds(self) -> Optional[float]:
        """Get time from generation to delivery."""
        if self.first_delivered_at is None:
            return None

        return (self.first_delivered_at - self.generation_timestamp).total_seconds()

    def get_last_error(self) -> Optional[str]:
        """Get the last error message."""
        for attempt in reversed(self.attempts):
            if attempt.error_message:
                return attempt.error_message
        return None

"""Report distribution service - deterministic orchestration."""

import uuid
from datetime import datetime
from typing import Optional
from analytics.distribution_config import (
    DistributionConfig,
    Channel,
    AttachmentType,
    Priority,
)
from analytics.delivery_state import DeliveryRecord, DeliveryState
from analytics.email_provider import EmailProvider, EmailMessage
from analytics.report_models import Report


class DistributionService:
    """
    Orchestrates deterministic report distribution.

    Does NOT use LLM for:
    - Scheduling decisions
    - Recipient selection
    - Retry logic
    - Delivery orchestration
    """

    def __init__(self, email_provider: EmailProvider):
        """Initialize distribution service."""
        self.email_provider = email_provider
        self.delivery_records = {}
        self.distribution_history = []

    def create_delivery_record(
        self,
        report: Report,
        config: DistributionConfig,
    ) -> DeliveryRecord:
        """Create a delivery record for a report."""
        delivery_id = f"DEL-{uuid.uuid4().hex[:8].upper()}"

        recipients = config.get_active_recipients()

        if not recipients:
            enabled = False
        else:
            enabled = config.enabled

        record = DeliveryRecord(
            delivery_id=delivery_id,
            report_id=report.report_id,
            report_type=config.report_type.value,
            generation_timestamp=report.generated_at,
            generation_success=True,
            distribution_enabled=enabled,
            recipients=recipients,
            cc_recipients=config.cc_recipients,
            bcc_recipients=config.bcc_recipients,
            channel=config.channels[0].value if config.channels else "email",
            attachment_types=[at.value for at in config.attachment_types],
        )

        self.delivery_records[delivery_id] = record
        return record

    def queue_delivery(
        self,
        record: DeliveryRecord,
    ) -> bool:
        """Queue a delivery record for sending."""
        if not record.distribution_enabled:
            record.add_attempt(
                state=DeliveryState.GENERATED,
                channel=record.channel,
                recipient="none",
                success=False,
                error_message="Distribution disabled",
            )
            return False

        if record.generation_error:
            record.add_attempt(
                state=DeliveryState.FAILED,
                channel=record.channel,
                recipient="none",
                success=False,
                error_message=f"Report generation failed: {record.generation_error}",
            )
            return False

        record.add_attempt(
            state=DeliveryState.QUEUED,
            channel=record.channel,
            recipient=record.recipients[0] if record.recipients else "unknown",
        )

        return True

    def send_delivery(
        self,
        record: DeliveryRecord,
        report: Report,
        config: DistributionConfig,
        attachment_bytes: dict[str, bytes],
    ) -> bool:
        """Send a queued delivery."""
        if record.is_successfully_delivered():
            return True

        if record.current_state == DeliveryState.DELIVERED:
            return True

        if record.current_state != DeliveryState.QUEUED and record.current_state != DeliveryState.RETRYING:
            return False

        record.add_attempt(
            state=DeliveryState.SENDING,
            channel=record.channel,
            recipient=record.recipients[0] if record.recipients else "unknown",
        )

        success = True
        last_error = None

        for recipient in record.recipients:
            if recipient in record.cc_recipients or recipient in record.bcc_recipients:
                continue

            if self._is_duplicate_delivery(record, recipient):
                record.add_attempt(
                    state=DeliveryState.DELIVERED,
                    channel=record.channel,
                    recipient=recipient,
                    success=True,
                    error_message="Duplicate delivery prevented",
                )
                continue

            message = self._build_email_message(
                report,
                config,
                recipient,
                record,
                attachment_bytes,
            )

            result = self.email_provider.send(message, recipient)

            if result.success:
                record.add_attempt(
                    state=DeliveryState.DELIVERED,
                    channel=record.channel,
                    recipient=recipient,
                    success=True,
                )
            else:
                success = False
                last_error = result.error
                record.add_attempt(
                    state=DeliveryState.FAILED,
                    channel=record.channel,
                    recipient=recipient,
                    success=False,
                    error_message=result.error,
                )

        if success:
            record.current_state = DeliveryState.DELIVERED
        else:
            record.current_state = DeliveryState.FAILED

        self.distribution_history.append({
            "delivery_id": record.delivery_id,
            "report_id": record.report_id,
            "timestamp": datetime.now(),
            "success": success,
            "error": last_error,
        })

        return success

    def retry_delivery(
        self,
        record: DeliveryRecord,
        report: Report,
        config: DistributionConfig,
        attachment_bytes: dict[str, bytes],
        max_retries: int = 3,
    ) -> bool:
        """Retry a failed delivery."""
        if record.is_successfully_delivered():
            return True

        if not record.can_retry(max_retries):
            if config.retry_config.escalation_enabled:
                self._escalate_delivery(record, config)
            return False

        record.add_attempt(
            state=DeliveryState.RETRYING,
            channel=record.channel,
            recipient=record.recipients[0] if record.recipients else "unknown",
        )

        return self.send_delivery(record, report, config, attachment_bytes)

    def _is_duplicate_delivery(
        self,
        record: DeliveryRecord,
        recipient: str,
    ) -> bool:
        """Check if this recipient already received this report."""
        for attempt in record.attempts:
            if attempt.recipient == recipient and attempt.success:
                return True
        return False

    def _build_email_message(
        self,
        report: Report,
        config: DistributionConfig,
        recipient: str,
        record: DeliveryRecord,
        attachment_bytes: dict[str, bytes],
    ) -> EmailMessage:
        """Build an email message for delivery."""
        subject = config.subject_template.format(
            report_type=config.report_type.value,
            date=report.report_date.isoformat(),
        )

        body = config.body_template

        attachments = {}
        for filename, content in attachment_bytes.items():
            attachments[filename] = content

        return EmailMessage(
            subject=subject,
            body=body,
            recipients=[recipient],
            cc_recipients=config.cc_recipients,
            bcc_recipients=config.bcc_recipients,
            attachments=attachments,
        )

    def _escalate_delivery(
        self,
        record: DeliveryRecord,
        config: DistributionConfig,
    ) -> None:
        """Escalate a failed delivery."""
        if not config.retry_config.escalation_enabled:
            return

        record.current_state = DeliveryState.ESCALATED
        record.escalation_recipients = config.retry_config.escalation_recipients
        record.escalation_notified = True

        self.distribution_history.append({
            "delivery_id": record.delivery_id,
            "report_id": record.report_id,
            "timestamp": datetime.now(),
            "event": "escalated",
            "escalation_recipients": config.retry_config.escalation_recipients,
            "error": record.get_last_error(),
        })

    def get_delivery_record(self, delivery_id: str) -> Optional[DeliveryRecord]:
        """Get a delivery record by ID."""
        return self.delivery_records.get(delivery_id)

    def get_delivery_records_by_report(self, report_id: str) -> list[DeliveryRecord]:
        """Get all delivery records for a report."""
        return [
            r for r in self.delivery_records.values()
            if r.report_id == report_id
        ]

    def get_pending_deliveries(self) -> list[DeliveryRecord]:
        """Get all pending deliveries."""
        return [
            r for r in self.delivery_records.values()
            if r.current_state in (
                DeliveryState.QUEUED,
                DeliveryState.RETRYING,
            )
        ]

    def get_failed_deliveries(self) -> list[DeliveryRecord]:
        """Get all failed deliveries."""
        return [
            r for r in self.delivery_records.values()
            if r.current_state in (
                DeliveryState.FAILED,
                DeliveryState.ESCALATED,
            )
        ]

    def get_audit_log(self) -> list[dict]:
        """Get complete audit log."""
        return self.distribution_history.copy()

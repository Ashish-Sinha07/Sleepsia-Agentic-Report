"""
Email Service for Report Distribution.

Clean interface for sending reports via SMTP.
Wraps the underlying email provider with report-specific logic.

Author: Rohit Kumar
Date: 2026-08-23
"""

import logging
from typing import Dict, List, Optional
from analytics.email_provider import EmailMessage as ProviderEmailMessage
from analytics.email_provider import SMTPEmailProvider
from backend.app.config import settings

logger = logging.getLogger(__name__)


class EmailMessage:
    """Represents a single email message with attachments."""

    def __init__(
        self,
        subject: str,
        body: str,
        recipients: List[str],
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        attachments: Optional[Dict[str, bytes]] = None,
    ):
        """
        Create an email message.

        Args:
            subject: Email subject
            body: Email body text
            recipients: List of recipient email addresses
            cc: Optional list of CC recipients
            bcc: Optional list of BCC recipients
            attachments: Dict of filename -> file bytes (e.g., {"report.pdf": pdf_bytes})
        """
        self.subject = subject
        self.body = body
        self.recipients = recipients
        self.cc = cc or []
        self.bcc = bcc or []
        self.attachments = attachments or {}


class ReportEmailService:
    """
    Service for sending reports via email.

    Provides a clean interface for sending report PDFs/Excel files to recipients.
    """

    def __init__(
        self,
        smtp_host: str = None,
        smtp_port: int = None,
        smtp_username: str = None,
        smtp_password: str = None,
        from_email: str = None,
        from_name: str = None,
    ):
        """
        Initialize email service with SMTP configuration.

        Args:
            smtp_host: SMTP server hostname (default from settings)
            smtp_port: SMTP server port (default from settings)
            smtp_username: SMTP username (default from settings)
            smtp_password: SMTP password (default from settings)
            from_email: From address (default from settings)
            from_name: From name (default from settings)
        """
        self.smtp_host = smtp_host or settings.SMTP_HOST
        self.smtp_port = smtp_port or settings.SMTP_PORT
        self.smtp_username = smtp_username or settings.SMTP_USERNAME
        self.smtp_password = smtp_password or settings.SMTP_PASSWORD
        self.from_email = from_email or settings.SMTP_FROM_EMAIL
        self.from_name = from_name or settings.SMTP_FROM_NAME

        # Initialize SMTP provider
        self.smtp_provider = SMTPEmailProvider(
            smtp_host=self.smtp_host,
            smtp_port=self.smtp_port,
            sender_email=self.from_email,
            sender_name=self.from_name,
            username=self.smtp_username,
            password=self.smtp_password,
        )

        logger.info(f"Email service initialized: {self.from_email} via {self.smtp_host}:{self.smtp_port}")

    def send_report(
        self,
        subject: str,
        body: str,
        recipients: List[str],
        attachments: Optional[Dict[str, bytes]] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        html_body: Optional[str] = None,
    ) -> bool:
        """
        Send a report email to recipients.

        Args:
            subject: Email subject line
            body: Email body text
            recipients: List of recipient email addresses
            attachments: Dict of filename -> file bytes (e.g., {"report.pdf": pdf_bytes})
            cc: Optional list of CC recipients
            bcc: Optional list of BCC recipients
            html_body: Optional HTML version of the email body

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            logger.info(f"Preparing email: {subject}")
            logger.info(f"  Recipients: {recipients}")
            if cc:
                logger.info(f"  CC: {cc}")
            if bcc:
                logger.info(f"  BCC: {bcc}")
            if attachments:
                logger.info(f"  Attachments: {list(attachments.keys())}")
            if html_body:
                logger.info(f"  HTML Body: {len(html_body)} characters")
            else:
                logger.info("  HTML Body: None (plain text only)")

            msg = ProviderEmailMessage(
                subject=subject,
                body=body,
                recipients=recipients,
                cc_recipients=cc or [],
                bcc_recipients=bcc or [],
                attachments=attachments or {},
                html_body=html_body,
            )

            # Send to each recipient
            all_recipients = recipients + (cc or []) + (bcc or [])
            success_count = 0
            fail_count = 0

            for recipient in recipients:
                try:
                    result = self.smtp_provider.send(
                        message=msg,
                        recipient=recipient,
                    )
                    if result.success:
                        logger.info(f"  [OK] Sent to {recipient}")
                        success_count += 1
                    else:
                        logger.error(f"  [FAIL] Failed to send to {recipient}: {result.error}")
                        fail_count += 1
                except Exception as e:
                    logger.error(f"  [FAIL] Exception sending to {recipient}: {str(e)}")
                    fail_count += 1

            # Send to CC recipients (if any)
            for cc_recipient in (cc or []):
                try:
                    result = self.smtp_provider.send(
                        message=msg,
                        recipient=cc_recipient,
                    )
                    if result.success:
                        logger.info(f"  [OK] CC sent to {cc_recipient}")
                        success_count += 1
                    else:
                        logger.error(f"  [FAIL] CC failed to {cc_recipient}: {result.error}")
                        fail_count += 1
                except Exception as e:
                    logger.error(f"  [FAIL] Exception CC to {cc_recipient}: {str(e)}")
                    fail_count += 1

            # Log result
            logger.info(f"Email send result: {success_count} succeeded, {fail_count} failed")
            return fail_count == 0

        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}", exc_info=True)
            return False

    def test_connection(self) -> bool:
        """Test SMTP connection without sending an email."""
        try:
            logger.info(f"Testing SMTP connection to {self.smtp_host}:{self.smtp_port}...")
            result = self.smtp_provider.validate_configuration()
            if result:
                logger.info("[OK] SMTP connection test successful")
            else:
                logger.error("[FAIL] SMTP connection test failed - check credentials")
            return result
        except Exception as e:
            logger.error(f"[FAIL] SMTP connection test failed: {str(e)}")
            return False

"""Email provider abstraction and implementations."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class EmailMessage:
    """Email message to send."""
    subject: str
    body: str
    recipients: list[str]
    cc_recipients: list[str] = None
    bcc_recipients: list[str] = None
    html_body: Optional[str] = None
    attachments: dict[str, bytes] = None

    def __post_init__(self):
        if self.cc_recipients is None:
            self.cc_recipients = []
        if self.bcc_recipients is None:
            self.bcc_recipients = []
        if self.attachments is None:
            self.attachments = {}

    def get_all_recipients(self) -> list[str]:
        """Get all unique recipients."""
        all_recipients = set(self.recipients)
        all_recipients.update(self.cc_recipients)
        all_recipients.update(self.bcc_recipients)
        return list(all_recipients)


@dataclass
class SendResult:
    """Result of sending an email."""
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None
    recipient: Optional[str] = None


class EmailProvider(ABC):
    """Abstract base class for email providers."""

    @abstractmethod
    def send(self, message: EmailMessage, recipient: str) -> SendResult:
        """
        Send an email message.

        Args:
            message: Email message to send
            recipient: Single recipient (required for idempotency)

        Returns:
            SendResult with success status
        """
        pass

    @abstractmethod
    def validate_configuration(self) -> bool:
        """Validate that provider is configured correctly."""
        pass


class MockEmailProvider(EmailProvider):
    """Mock email provider for testing."""

    def __init__(self):
        """Initialize mock provider."""
        self.sent_emails = []
        self.should_fail = False
        self.failure_message = "Mock email failure"

    def send(self, message: EmailMessage, recipient: str) -> SendResult:
        """Send email (mock implementation)."""
        if self.should_fail:
            return SendResult(
                success=False,
                error=self.failure_message,
                recipient=recipient,
            )

        self.sent_emails.append({
            "subject": message.subject,
            "body": message.body,
            "recipient": recipient,
            "cc": message.cc_recipients,
            "bcc": message.bcc_recipients,
            "attachments": list(message.attachments.keys()),
            "timestamp": __import__("datetime").datetime.now(),
        })

        return SendResult(
            success=True,
            message_id=f"mock-{len(self.sent_emails)}",
            recipient=recipient,
        )

    def validate_configuration(self) -> bool:
        """Mock provider is always valid."""
        return True

    def get_sent_count(self) -> int:
        """Get count of sent emails."""
        return len(self.sent_emails)

    def get_last_sent(self) -> Optional[dict]:
        """Get the last sent email."""
        return self.sent_emails[-1] if self.sent_emails else None

    def clear(self):
        """Clear sent emails."""
        self.sent_emails = []


class SMTPEmailProvider(EmailProvider):
    """SMTP-based email provider."""

    def __init__(
        self,
        smtp_host: str,
        smtp_port: int = 587,
        sender_email: str = None,
        sender_name: str = "Sleepsia Reports",
        username: str = None,
        password: str = None,
    ):
        """Initialize SMTP provider."""
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_name = sender_name
        self.username = username or sender_email
        self.password = password

    def send(self, message: EmailMessage, recipient: str) -> SendResult:
        """Send email via SMTP."""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            msg = MIMEMultipart("alternative")
            msg["Subject"] = message.subject
            msg["From"] = f"{self.sender_name} <{self.sender_email}>"
            msg["To"] = recipient

            if message.cc_recipients:
                msg["Cc"] = ", ".join(message.cc_recipients)

            text_part = MIMEText(message.body, "plain")
            msg.attach(text_part)

            if message.html_body:
                html_part = MIMEText(message.html_body, "html")
                msg.attach(html_part)

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)

                all_recipients = [recipient] + message.cc_recipients
                if message.bcc_recipients:
                    all_recipients.extend(message.bcc_recipients)

                server.sendmail(self.sender_email, all_recipients, msg.as_string())

            return SendResult(
                success=True,
                message_id=f"smtp-{__import__('uuid').uuid4().hex[:8]}",
                recipient=recipient,
            )

        except Exception as e:
            return SendResult(
                success=False,
                error=str(e),
                recipient=recipient,
            )

    def validate_configuration(self) -> bool:
        """Validate SMTP configuration."""
        return (
            self.smtp_host is not None
            and self.sender_email is not None
            and self.username is not None
            and self.password is not None
        )

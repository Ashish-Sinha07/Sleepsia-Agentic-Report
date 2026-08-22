"""Attachment generation service."""

from analytics.report_models import Report
from analytics.html_renderer import HTMLRenderer
from analytics.excel_renderer import ExcelRenderer


class AttachmentService:
    """Generate report attachments in various formats."""

    @staticmethod
    def generate_html_attachment(report: Report) -> tuple[str, bytes]:
        """Generate HTML attachment."""
        html = HTMLRenderer.render(report)
        filename = f"{report.report_id}.html"
        return filename, html.encode("utf-8")

    @staticmethod
    def generate_excel_attachment(report: Report) -> tuple[str, bytes]:
        """Generate Excel attachment."""
        try:
            excel_bytes = ExcelRenderer.render(report)
            filename = f"{report.report_id}.xlsx"
            return filename, excel_bytes
        except ImportError:
            raise ImportError("openpyxl is required for Excel generation")

    @staticmethod
    def generate_attachments(
        report: Report,
        formats: list[str],
    ) -> dict[str, bytes]:
        """
        Generate attachments in requested formats.

        Args:
            report: Report to generate attachments for
            formats: List of formats ('html', 'xlsx', 'pdf')

        Returns:
            Dictionary of filename -> bytes
        """
        attachments = {}

        for format_type in formats:
            if format_type == "html":
                filename, content = AttachmentService.generate_html_attachment(report)
                attachments[filename] = content

            elif format_type == "xlsx":
                try:
                    filename, content = AttachmentService.generate_excel_attachment(report)
                    attachments[filename] = content
                except ImportError:
                    pass

            elif format_type == "pdf":
                try:
                    filename, content = AttachmentService.generate_pdf_attachment(report)
                    attachments[filename] = content
                except ImportError:
                    pass

        return attachments

    @staticmethod
    def generate_pdf_attachment(report: Report) -> tuple[str, bytes]:
        """Generate PDF attachment."""
        try:
            from analytics.pdf_renderer import PDFRenderer
            pdf_bytes = PDFRenderer.render(report)
            filename = f"{report.report_id}.pdf"
            return filename, pdf_bytes
        except ImportError:
            raise ImportError("reportlab is required for PDF generation")

    @staticmethod
    def validate_attachments(
        attachments: dict[str, bytes],
        required_formats: list[str],
    ) -> bool:
        """
        Validate that attachments match required formats.

        Args:
            attachments: Generated attachments
            required_formats: Required format list

        Returns:
            True if all required formats are present
        """
        if not required_formats:
            return True

        present_formats = set()

        for filename in attachments.keys():
            if filename.endswith(".html"):
                present_formats.add("html")
            elif filename.endswith(".xlsx"):
                present_formats.add("xlsx")
            elif filename.endswith(".pdf"):
                present_formats.add("pdf")
            elif filename.endswith(".csv"):
                present_formats.add("csv")

        required_set = set(required_formats)
        return required_set.issubset(present_formats)

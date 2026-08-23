"""
PDF Report Generator

Generates professional PDF reports from OmniChannelReport data structures.

Uses reportlab for PDF generation and follows the structure of the reference audit report.

The PDF includes:
- Header and metadata
- Executive summary
- Platform-wise performance breakdown
- Product-wise consolidated analysis
- P&L statement
- Channel efficiency rankings
- Recommendations
"""

import io
from datetime import datetime
from decimal import Decimal
from typing import Optional

from reports.models.report_models import OmniChannelReport
from reports.utils.formatting import (
    format_currency,
    format_percentage,
    format_roas,
    format_units,
)

# reportlab will be installed as dependency, but we'll provide fallback
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate,
        Table,
        TableStyle,
        Paragraph,
        Spacer,
        PageBreak,
        Image,
    )
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False


class PDFReportGenerator:
    """
    Generate professional PDF reports from report data.

    The PDF structure mirrors the reference audit report:
    1. Cover page with metadata
    2. Executive summary and key findings
    3. Platform-wise performance (1.1-1.6)
    4. Consolidated product analysis (2.0)
    5. P&L and channel efficiency (3.0)
    6. Recommendations
    """

    def __init__(self, report_data: OmniChannelReport):
        """
        Initialize PDF generator with report data.

        Args:
            report_data: OmniChannelReport object with all metrics
        """
        self.report_data = report_data

    def generate(self) -> bytes:
        """
        Generate complete PDF report.

        Returns:
            PDF file content as bytes
        """
        if not HAS_REPORTLAB:
            return self._generate_fallback()

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=0.5 * inch,
            leftMargin=0.5 * inch,
            topMargin=0.5 * inch,
            bottomMargin=0.5 * inch,
        )

        story = []
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=20,
            textColor=colors.HexColor("#1a3a52"),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName="Helvetica-Bold",
        )

        heading_style = ParagraphStyle(
            "CustomHeading",
            parent=styles["Heading2"],
            fontSize=12,
            textColor=colors.HexColor("#2c5aa0"),
            spaceAfter=8,
            fontName="Helvetica-Bold",
        )

        # Cover Page
        story.append(Spacer(1, 0.3 * inch))
        story.append(
            Paragraph(self.report_data.metadata.report_type, title_style)
        )
        story.append(Spacer(1, 0.1 * inch))
        story.append(
            Paragraph(self.report_data.metadata.organization, heading_style)
        )
        story.append(
            Paragraph(
                f"<i>Audit Date: {self.report_data.metadata.audit_date.strftime('%d %b %Y')}</i>",
                styles["Normal"],
            )
        )
        story.append(
            Paragraph(
                f"<i>Scope: {self.report_data.metadata.scope}</i>",
                styles["Normal"],
            )
        )
        story.append(
            Paragraph(
                f"<i>Status: {self.report_data.metadata.status}</i>",
                styles["Normal"],
            )
        )

        story.append(Spacer(1, 0.3 * inch))
        story.append(PageBreak())

        # Executive Summary
        story.append(Paragraph("Executive Summary", title_style))
        if self.report_data.management_summary:
            story.append(
                Paragraph(
                    self.report_data.management_summary.summary_text,
                    styles["Normal"],
                )
            )
            story.append(Spacer(1, 0.1 * inch))

            # Key Findings
            if self.report_data.management_summary.key_findings:
                story.append(Paragraph("Key Findings:", heading_style))
                for finding in self.report_data.management_summary.key_findings[
                    :5
                ]:
                    story.append(
                        Paragraph(f"• {finding}", styles["Normal"])
                    )

        story.append(Spacer(1, 0.2 * inch))
        story.append(PageBreak())

        # Platform Performance Sections
        for idx, platform in enumerate(self.report_data.platforms, 1):
            story.append(
                Paragraph(
                    f"1.{idx} Platform Overview & Product Stats: {platform.platform_name}",
                    heading_style,
                )
            )

            # KPI Summary
            kpi_data = [
                ["Metric", "Value"],
                ["Gross Revenue", format_currency(platform.gross_revenue)],
                [
                    "Returns & Refunds",
                    f"{format_currency(platform.returns_refunds)} ({format_percentage(platform.returns_percentage)})",
                ],
                ["Net Realized Revenue", format_currency(platform.net_revenue)],
                ["Fulfillment OTIF", format_percentage(platform.fulfillment_otif)],
                ["Ad Spend (AdCost)", format_currency(platform.ad_spend)],
                [
                    "Net Ad Cost (Ad+Ref)",
                    format_currency(platform.net_ad_cost),
                ],
                [
                    "TACoS Efficiency",
                    f"{format_percentage(platform.tacos_percentage)} of Net Rev",
                ],
                [
                    "Net Profit & Margin",
                    f"{format_currency(platform.net_profit)} ({format_percentage(platform.margin_percentage)})",
                ],
            ]

            kpi_table = Table(kpi_data, colWidths=[3.5 * inch, 2.5 * inch])
            kpi_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c5aa0")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 9),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                        ("FONTSIZE", (0, 1), (-1, -1), 8),
                    ]
                )
            )
            story.append(kpi_table)
            story.append(Spacer(1, 0.15 * inch))

            # Product breakdown
            story.append(
                Paragraph(
                    f"Product-Specific Performance Breakdown on {platform.platform_name}:",
                    styles["Normal"],
                )
            )
            story.append(Spacer(1, 0.05 * inch))

            product_data = [
                [
                    "SKU",
                    "Product",
                    "Units",
                    "Gross Rev",
                    "Returns",
                    "Ad Spend",
                    "TACoS",
                    "Net Profit",
                    "Margin",
                ]
            ]

            for product in platform.products:
                product_data.append(
                    [
                        product.sku,
                        truncate_product_name(product.product_name),
                        str(product.units_sold),
                        format_currency(product.gross_revenue),
                        f"{product.returns_count} ({format_percentage(product.returns_percentage)})",
                        format_currency(product.ad_spend),
                        format_percentage(product.tacos_percentage),
                        format_currency(product.net_profit),
                        format_percentage(product.margin_percentage),
                    ]
                )

            product_table = Table(
                product_data,
                colWidths=[
                    0.6 * inch,
                    1.5 * inch,
                    0.5 * inch,
                    0.7 * inch,
                    0.6 * inch,
                    0.6 * inch,
                    0.5 * inch,
                    0.6 * inch,
                    0.5 * inch,
                ],
            )
            product_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4a7ab7")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 7),
                        ("FONTSIZE", (0, 1), (-1, -1), 6),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 4),
                        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                    ]
                )
            )
            story.append(product_table)
            story.append(Spacer(1, 0.2 * inch))
            story.append(PageBreak())

        # Consolidated Analysis
        story.append(Paragraph("Overall Report for Each Product Across All Platforms", heading_style))
        story.append(Spacer(1, 0.1 * inch))

        consolidated_data = [
            [
                "SKU",
                "Product",
                "Units",
                "Gross",
                "Returns",
                "Ad Cost",
                "TACoS",
                "Net Profit",
                "Margin",
                "Stock DOS",
            ]
        ]

        for product in self.report_data.consolidated_products:
            consolidated_data.append(
                [
                    product.sku,
                    truncate_product_name(product.product_name),
                    format_units(product.all_units),
                    format_currency(product.total_gross),
                    f"{product.all_returns} ({format_percentage(product.returns_percentage)})",
                    format_currency(product.total_ad_cost),
                    format_percentage(product.tacos_percentage),
                    format_currency(product.net_profit),
                    format_percentage(product.margin_percentage),
                    f"{product.stock_dos:.0f}d",
                ]
            )

        consolidated_table = Table(
            consolidated_data,
            colWidths=[
                0.5 * inch,
                1.2 * inch,
                0.5 * inch,
                0.6 * inch,
                0.5 * inch,
                0.6 * inch,
                0.5 * inch,
                0.6 * inch,
                0.5 * inch,
                0.5 * inch,
            ],
        )
        consolidated_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4a7ab7")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 7),
                    ("FONTSIZE", (0, 1), (-1, -1), 6),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                ]
            )
        )
        story.append(consolidated_table)
        story.append(Spacer(1, 0.2 * inch))
        story.append(PageBreak())

        # P&L Statement
        story.append(Paragraph("Grand Executive Summary & Consolidated Omni-Channel P&L", heading_style))
        story.append(Spacer(1, 0.1 * inch))

        if self.report_data.pnl:
            pnl_data = [
                ["P&L Statement Line Item", "Amount (INR)", "Revenue %"],
                [
                    "Total Gross Sales Turnover (GMV)",
                    format_currency(self.report_data.pnl.total_gross_gmv),
                    "100.0%",
                ],
                [
                    "Less: Returns & Customer Refunds",
                    f"({format_currency(self.report_data.pnl.less_returns_refunds)})",
                    f"{format_percentage(self.report_data.pnl.less_returns_percentage)}",
                ],
                [
                    "Net Realized Sales Turnover",
                    format_currency(self.report_data.pnl.net_revenue),
                    "100.0%",
                ],
                [
                    "Less: Cost of Goods Sold (COGS)",
                    f"({format_currency(self.report_data.pnl.less_cogs)})",
                    f"{format_percentage(self.report_data.pnl.less_cogs_percentage)}",
                ],
                [
                    "Less: Total Marketing & Ad Spend (AdCost)",
                    f"({format_currency(self.report_data.pnl.less_ad_spend)})",
                    f"{format_percentage(self.report_data.pnl.less_ad_spend_percentage)}",
                ],
                [
                    "Less: Marketplace Commission & Logistics",
                    f"({format_currency(self.report_data.pnl.less_commission_logistics)})",
                    f"{format_percentage(self.report_data.pnl.less_commission_logistics_percentage)}",
                ],
                [
                    "GRAND NET OPERATING PROFIT (EBITDA)",
                    format_currency(self.report_data.pnl.grand_net_operating_profit),
                    f"{format_percentage(self.report_data.pnl.margin_percentage)} Margin",
                ],
            ]

            pnl_table = Table(pnl_data, colWidths=[3.5 * inch, 1.5 * inch, 1.0 * inch])
            pnl_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c5aa0")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (0, -1), "LEFT"),
                        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 8),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#d9e8f5")),
                        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                    ]
                )
            )
            story.append(pnl_table)

        story.append(Spacer(1, 0.2 * inch))
        story.append(PageBreak())

        # Channel Efficiency
        if self.report_data.channel_efficiency:
            story.append(Paragraph("Channel Efficiency & Operating Margin Contribution Ranking:", heading_style))
            story.append(Spacer(1, 0.1 * inch))

            channel_data = [
                ["#", "Platform", "Orders", "Units", "Gross Sales", "Sales Share", "TACoS", "Net Profit", "Margin %", "OTIF %"]
            ]

            for channel in self.report_data.channel_efficiency:
                channel_data.append(
                    [
                        str(channel.rank),
                        channel.platform_name,
                        str(channel.orders),
                        format_units(channel.units),
                        format_currency(channel.gross_sales),
                        format_percentage(channel.sales_share_percentage),
                        format_percentage(channel.tacos_percentage),
                        format_currency(channel.net_profit),
                        format_percentage(channel.margin_percentage),
                        format_percentage(channel.otif_percentage),
                    ]
                )

            channel_table = Table(
                channel_data,
                colWidths=[
                    0.3 * inch,
                    1.5 * inch,
                    0.6 * inch,
                    0.5 * inch,
                    0.7 * inch,
                    0.7 * inch,
                    0.5 * inch,
                    0.6 * inch,
                    0.6 * inch,
                    0.5 * inch,
                ],
            )
            channel_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c5aa0")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 7),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                    ]
                )
            )
            story.append(channel_table)
            story.append(Spacer(1, 0.2 * inch))
            story.append(PageBreak())

        # Recommendations
        if self.report_data.management_summary and self.report_data.management_summary.recommendations:
            story.append(Paragraph("Recommendations", heading_style))
            story.append(Spacer(1, 0.1 * inch))

            for rec in self.report_data.management_summary.recommendations:
                story.append(Paragraph(f"• {rec}", styles["Normal"]))
                story.append(Spacer(1, 0.05 * inch))

        # Build PDF
        doc.build(story)
        pdf_content = buffer.getvalue()
        buffer.close()

        return pdf_content

    def _generate_fallback(self) -> bytes:
        """
        Generate a simple text-based report if reportlab is not available.

        This provides basic functionality for development without reportlab dependency.
        """
        content = f"""
SLEEPSIA OMNI-CHANNEL E-COMMERCE PLATFORM & PRODUCT AUDIT
{self.report_data.metadata.organization}

Audit Date: {self.report_data.metadata.audit_date.strftime('%d %b %Y')}
Scope: {self.report_data.metadata.scope}
Status: {self.report_data.metadata.status}

EXECUTIVE SUMMARY
{self.report_data.management_summary.summary_text if self.report_data.management_summary else 'N/A'}

P&L STATEMENT
Total Gross Sales: {format_currency(self.report_data.pnl.total_gross_gmv) if self.report_data.pnl else 'N/A'}
Net Revenue: {format_currency(self.report_data.pnl.net_revenue) if self.report_data.pnl else 'N/A'}
Net Profit: {format_currency(self.report_data.pnl.grand_net_operating_profit) if self.report_data.pnl else 'N/A'}

GENERATED: {datetime.now().strftime('%d %b %Y %H:%M:%S')}
"""
        return content.encode("utf-8")


def truncate_product_name(name: str, max_len: int = 30) -> str:
    """Truncate product name for table display."""
    if len(name) > max_len:
        return name[: max_len - 3] + "..."
    return name

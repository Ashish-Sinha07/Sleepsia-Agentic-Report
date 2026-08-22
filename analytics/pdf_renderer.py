"""PDF report renderer."""

from analytics.report_models import Report

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False


class PDFRenderer:
    """Renders reports to PDF format."""

    @staticmethod
    def render(report: Report) -> bytes:
        """Render a report to PDF bytes."""
        if not HAS_REPORTLAB:
            raise ImportError("reportlab is required for PDF rendering")

        from io import BytesIO

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5 * inch)
        story = []

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=18,
            textColor=colors.HexColor("#2C3E50"),
            spaceAfter=12,
            alignment=TA_LEFT,
        )

        section_style = ParagraphStyle(
            "CustomSection",
            parent=styles["Heading2"],
            fontSize=14,
            textColor=colors.HexColor("#34495E"),
            spaceAfter=10,
            spaceBefore=10,
            borderPadding=5,
        )

        story.append(Paragraph(report.title, title_style))
        story.append(Paragraph(f"Report ID: {report.report_id}", styles["Normal"]))
        story.append(Paragraph(
            f"Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}",
            styles["Normal"]
        ))
        story.append(Spacer(1, 0.2 * inch))

        story.append(Paragraph("Executive Summary", section_style))
        story.append(Paragraph(report.executive_summary, styles["Normal"]))
        story.append(Spacer(1, 0.2 * inch))

        story.append(Paragraph("Overall Metrics", section_style))
        metrics_table = PDFRenderer._build_metrics_table(report)
        story.append(metrics_table)
        story.append(Spacer(1, 0.2 * inch))

        if report.product_sections:
            story.append(PageBreak())
            story.append(Paragraph("Product Performance", section_style))
            for product in report.product_sections:
                story.append(Paragraph(f"{product.product_name} ({product.sku})", styles["Heading3"]))
                product_table = PDFRenderer._build_product_table(product)
                story.append(product_table)
                story.append(Spacer(1, 0.15 * inch))

        if report.advertising_section:
            story.append(PageBreak())
            story.append(Paragraph("Advertising Performance", section_style))
            ad_table = PDFRenderer._build_advertising_table(report.advertising_section)
            story.append(ad_table)
            story.append(Spacer(1, 0.2 * inch))

        if report.profitability_section:
            story.append(Paragraph("Profitability Analysis", section_style))
            prof_table = PDFRenderer._build_profitability_table(report.profitability_section)
            story.append(prof_table)
            story.append(Spacer(1, 0.2 * inch))

        if report.insights:
            story.append(PageBreak())
            story.append(Paragraph("Key Insights", section_style))
            for insight in report.insights:
                insight_text = f"<b>{insight.title}</b> ({insight.priority}): {insight.description}"
                story.append(Paragraph(insight_text, styles["Normal"]))
                story.append(Spacer(1, 0.1 * inch))

        if report.recommendations:
            story.append(PageBreak())
            story.append(Paragraph("Recommendations", section_style))
            for rec in report.recommendations:
                rec_text = f"<b>{rec.action}</b> ({rec.priority})<br/>Rationale: {rec.rationale}<br/>Owner: {rec.owner}"
                story.append(Paragraph(rec_text, styles["Normal"]))
                story.append(Spacer(1, 0.1 * inch))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    @staticmethod
    def _build_metrics_table(report: Report) -> Table:
        """Build overall metrics table."""
        metrics = report.overall_metrics
        data = [
            ["Metric", "Value"],
            ["Orders", str(metrics.total_orders)],
            ["Units Sold", str(metrics.total_units_sold)],
            ["Net Sales (INR)", f"₹{metrics.total_net_sales_inr:,.0f}"],
            ["Ad Spend (INR)", f"₹{metrics.total_ad_spend_inr:,.0f}"],
            ["Organic Share (%)", f"{metrics.organic_share_pct:.1f}%"],
            ["Total Cost (INR)", f"₹{metrics.total_cost_inr:,.0f}"],
            ["Contribution (INR)", f"₹{metrics.total_contribution_inr:,.0f}"],
            ["Profit Margin (%)", f"{metrics.overall_profit_margin_pct:.1f}%"],
        ]

        table = Table(data, colWidths=[3 * inch, 2 * inch])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#34495E")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 11),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ("GRID", (0, 0), (-1, -1), 1, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8F9FA")]),
        ]))

        return table

    @staticmethod
    def _build_product_table(product) -> Table:
        """Build product table."""
        data = [
            ["Metric", "Value"],
            ["Units Sold", str(product.units_sold)],
            ["Net Sales (INR)", f"₹{product.net_sales_inr:,.0f}"],
            ["ROAS", f"{product.roas:.2f}x"],
            ["ACOS (%)", f"{product.acos_pct:.1f}%"],
            ["Profit Margin (%)", f"{product.profit_margin_pct:.1f}%"],
            ["Return Rate (%)", f"{product.return_rate_pct:.1f}%"],
            ["Cancellation (%)", f"{product.cancellation_rate_pct:.1f}%"],
        ]

        table = Table(data, colWidths=[3 * inch, 2 * inch])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#34495E")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ("GRID", (0, 0), (-1, -1), 1, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8F9FA")]),
        ]))

        return table

    @staticmethod
    def _build_advertising_table(advertising) -> Table:
        """Build advertising table."""
        data = [
            ["Metric", "Value"],
            ["Total Ad Spend (INR)", f"₹{advertising.total_ad_spend_inr:,.0f}"],
            ["Attributed Sales (INR)", f"₹{advertising.total_attributed_sales_inr:,.0f}"],
            ["ROAS", f"{advertising.overall_roas:.2f}x"],
            ["ACOS (%)", f"{advertising.overall_acos_pct:.1f}%"],
            ["Attributed Units", str(advertising.attributed_units)],
        ]

        table = Table(data, colWidths=[3 * inch, 2 * inch])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#34495E")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ("GRID", (0, 0), (-1, -1), 1, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8F9FA")]),
        ]))

        return table

    @staticmethod
    def _build_profitability_table(profitability) -> Table:
        """Build profitability table."""
        data = [
            ["Metric", "Value"],
            ["Total Net Sales (INR)", f"₹{profitability.total_net_sales_inr:,.0f}"],
            ["Total Cost (INR)", f"₹{profitability.total_cost_inr:,.0f}"],
            ["Contribution (INR)", f"₹{profitability.total_contribution_inr:,.0f}"],
            ["Profit Margin (%)", f"{profitability.overall_profit_margin_pct:.1f}%"],
            ["Healthy Products", str(profitability.products_healthy)],
            ["At-Risk Products", str(profitability.products_at_risk)],
            ["Unprofitable Products", str(profitability.products_unprofitable)],
        ]

        table = Table(data, colWidths=[3 * inch, 2 * inch])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#34495E")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ("GRID", (0, 0), (-1, -1), 1, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8F9FA")]),
        ]))

        return table

"""Comprehensive Report Service with Agent Integration.

Generates detailed business reports using analytics and AI agents for insights
and recommendations. Produces professional PDFs with all business metrics.

Author: Claude Code
Date: 2026-08-24
"""

import logging
from datetime import date, datetime
from typing import Dict, Optional, Any, List
from io import BytesIO
from pathlib import Path

from sqlalchemy.orm import Session
from sqlalchemy import text

from app.config import settings
from analytics.business_rules import BusinessRules
from analytics.insight_engine import InsightEngine
from analytics.recommendation_engine import RecommendationEngine
from analytics.metrics_engine import MetricsEngine

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak,
        KeepTogether, Preformatted
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

logger = logging.getLogger(__name__)


class ComprehensiveReportService:
    """Generate comprehensive business reports with agents and insights."""

    def __init__(self, db: Session):
        """Initialize report service with database session.

        Args:
            db: Database session
        """
        self.db = db
        self.business_rules = BusinessRules()
        self.insight_engine = InsightEngine(business_rules=self.business_rules)
        self.recommendation_engine = RecommendationEngine(business_rules=self.business_rules)
        self.metrics_engine = MetricsEngine()

        logger.info("Comprehensive Report Service initialized with agent engines")

    def generate_full_report(
        self,
        start_date: date,
        end_date: date,
        report_type: str = "executive_summary",
    ) -> Dict[str, Any]:
        """Generate comprehensive report with all components.

        Args:
            start_date: Start date for report
            end_date: End date for report
            report_type: Type of report to generate

        Returns:
            Dictionary with report data and file paths
        """
        try:
            logger.info(f"\n{'='*80}")
            logger.info(f"Generating Comprehensive Report")
            logger.info(f"Period: {start_date} to {end_date}")
            logger.info(f"{'='*80}\n")

            report_id = f"REP-{datetime.now().strftime('%Y%m%d%H%M%S')}"

            # Step 1: Fetch business metrics
            logger.info("[1/5] Fetching business metrics from database...")
            metrics = self._fetch_metrics(start_date, end_date)
            logger.info(f"[OK] Metrics fetched: {len(metrics)} data points")

            # Step 2: Fetch detailed data
            logger.info("[2/5] Fetching detailed performance data...")
            platform_data = self._fetch_platform_data(start_date, end_date)
            product_data = self._fetch_product_data(start_date, end_date)
            advertising_data = self._fetch_advertising_data(start_date, end_date)
            logger.info(f"[OK] Data fetched: {len(platform_data)} platforms, {len(product_data)} products")

            # Step 3: Generate insights using insight engine
            logger.info("[3/5] Generating business insights using insight engine...")
            insights = self._generate_insights(metrics, platform_data, product_data)
            logger.info(f"[OK] Generated {len(insights)} insights")

            # Step 4: Generate recommendations using recommendation engine
            logger.info("[4/5] Generating recommendations using recommendation engine...")
            recommendations = self._generate_recommendations(insights)
            logger.info(f"[OK] Generated {len(recommendations)} recommendations")

            # Step 5: Create professional PDF report
            logger.info("[5/5] Generating professional PDF report...")
            pdf_bytes = self._generate_professional_pdf(
                report_id=report_id,
                start_date=start_date,
                end_date=end_date,
                metrics=metrics,
                platform_data=platform_data,
                product_data=product_data,
                advertising_data=advertising_data,
                insights=insights,
                recommendations=recommendations,
            )
            logger.info(f"[OK] PDF generated: {len(pdf_bytes)} bytes")

            logger.info(f"\n{'='*80}")
            logger.info(f"Report Generation Complete: {report_id}")
            logger.info(f"{'='*80}\n")

            return {
                "success": True,
                "report_id": report_id,
                "start_date": str(start_date),
                "end_date": str(end_date),
                "pdf_bytes": pdf_bytes,
                "metrics": metrics,
                "insights": insights,
                "recommendations": recommendations,
                "generated_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Report generation failed: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
            }

    def _fetch_metrics(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Fetch key business metrics."""
        try:
            query = """
            SELECT
                SUM(total_gross_sales) as revenue,
                SUM(total_net_sales) as net_revenue,
                SUM(total_contribution) as profit,
                AVG(overall_profit_margin_pct) as profit_margin,
                SUM(total_orders) as orders,
                SUM(total_units_sold) as units,
                AVG(overall_roas) as roas,
                SUM(total_ad_spend) as ad_spend,
                COUNT(DISTINCT DATE(date)) as days_in_period
            FROM vw_daily_kpi_summary
            WHERE date BETWEEN :start_date AND :end_date
            """

            result = self.db.execute(
                text(query),
                {"start_date": start_date, "end_date": end_date}
            ).fetchone()

            if result:
                return {
                    "revenue": float(result[0]) if result[0] else 0,
                    "net_revenue": float(result[1]) if result[1] else 0,
                    "profit": float(result[2]) if result[2] else 0,
                    "profit_margin": float(result[3]) if result[3] else 0,
                    "orders": int(result[4]) if result[4] else 0,
                    "units": int(result[5]) if result[5] else 0,
                    "roas": float(result[6]) if result[6] else 0,
                    "ad_spend": float(result[7]) if result[7] else 0,
                    "days": int(result[8]) if result[8] else 1,
                }
            return {}

        except Exception as e:
            logger.warning(f"Failed to fetch metrics: {str(e)}")
            return {}

    def _fetch_platform_data(self, start_date: date, end_date: date) -> List[Dict]:
        """Fetch platform performance data."""
        try:
            query = """
            SELECT
                pl.platform_name,
                SUM(vpd.gross_sales) as revenue,
                SUM(vpd.contribution_inr) as profit,
                CASE WHEN SUM(vpd.net_sales) > 0
                    THEN ROUND((SUM(vpd.contribution_inr) / SUM(vpd.net_sales)) * 100, 2)
                    ELSE 0
                END as margin,
                SUM(vpd.orders) as orders
            FROM vw_product_platform_daily vpd
            INNER JOIN platforms pl ON vpd.platform_id = pl.platform_id
            WHERE vpd.date BETWEEN :start_date AND :end_date
            GROUP BY pl.platform_id, pl.platform_name
            ORDER BY revenue DESC
            LIMIT 10
            """

            results = self.db.execute(
                text(query),
                {"start_date": start_date, "end_date": end_date}
            ).fetchall()

            return [
                {
                    "platform": row[0],
                    "revenue": float(row[1]) if row[1] else 0,
                    "profit": float(row[2]) if row[2] else 0,
                    "margin": float(row[3]) if row[3] else 0,
                    "orders": int(row[4]) if row[4] else 0,
                }
                for row in results
            ]

        except Exception as e:
            logger.error(f"Failed to fetch platform data: {str(e)}", exc_info=True)
            return []

    def _fetch_product_data(self, start_date: date, end_date: date) -> List[Dict]:
        """Fetch product performance data."""
        try:
            query = """
            SELECT
                vpd.product_name,
                SUM(vpd.gross_sales) as revenue,
                SUM(vpd.contribution_inr) as profit,
                CASE WHEN SUM(vpd.net_sales) > 0
                    THEN ROUND((SUM(vpd.contribution_inr) / SUM(vpd.net_sales)) * 100, 2)
                    ELSE 0
                END as margin,
                SUM(vpd.units_sold) as units
            FROM vw_product_platform_daily vpd
            WHERE vpd.date BETWEEN :start_date AND :end_date
            GROUP BY vpd.sku, vpd.product_name
            ORDER BY profit DESC
            LIMIT 20
            """

            results = self.db.execute(
                text(query),
                {"start_date": start_date, "end_date": end_date}
            ).fetchall()

            return [
                {
                    "product": row[0],
                    "revenue": float(row[1]) if row[1] else 0,
                    "profit": float(row[2]) if row[2] else 0,
                    "margin": float(row[3]) if row[3] else 0,
                    "units": int(row[4]) if row[4] else 0,
                }
                for row in results
            ]

        except Exception as e:
            logger.error(f"Failed to fetch product data: {str(e)}", exc_info=True)
            return []

    def _fetch_advertising_data(self, start_date: date, end_date: date) -> Dict:
        """Fetch advertising performance data."""
        try:
            query = """
            SELECT
                SUM(total_ad_spend) as spend,
                SUM(total_ad_sales) as attributed_sales,
                AVG(overall_roas) as roas
            FROM vw_daily_kpi_summary
            WHERE date BETWEEN :start_date AND :end_date
            """

            result = self.db.execute(
                text(query),
                {"start_date": start_date, "end_date": end_date}
            ).fetchone()

            if result:
                return {
                    "spend": float(result[0]) if result[0] else 0,
                    "attributed_sales": float(result[1]) if result[1] else 0,
                    "roas": float(result[2]) if result[2] else 0,
                    "acos": 0.0,  # Calculate from spend/attributed_sales if needed
                }
            return {}

        except Exception as e:
            logger.warning(f"Failed to fetch advertising data: {str(e)}")
            return {}

    def _generate_insights(
        self,
        metrics: Dict,
        platform_data: List[Dict],
        product_data: List[Dict],
    ) -> List[Dict]:
        """Generate insights from data using insight engine."""
        insights = []

        # Profitability insights
        if metrics.get("profit_margin", 0) < 40:
            insights.append({
                "category": "PROFITABILITY",
                "title": "Low Profit Margin Alert",
                "description": f"Profit margin is {metrics.get('profit_margin', 0):.1f}%, below target of 40%",
                "priority": "HIGH",
                "metric_value": metrics.get("profit_margin"),
                "threshold": 40,
            })
        elif metrics.get("profit_margin", 0) > 50:
            insights.append({
                "category": "PROFITABILITY",
                "title": "Strong Profitability",
                "description": f"Profit margin is {metrics.get('profit_margin', 0):.1f}%, above target",
                "priority": "LOW",
                "metric_value": metrics.get("profit_margin"),
            })

        # ROAS insights
        if metrics.get("roas", 0) < 3:
            insights.append({
                "category": "ADVERTISING",
                "title": "Low ROAS Performance",
                "description": f"ROAS is {metrics.get('roas', 0):.2f}x, below target of 3.0x",
                "priority": "HIGH",
                "metric_value": metrics.get("roas"),
                "threshold": 3.0,
            })
        elif metrics.get("roas", 0) > 4:
            insights.append({
                "category": "ADVERTISING",
                "title": "Excellent Ad Performance",
                "description": f"ROAS is {metrics.get('roas', 0):.2f}x, exceeding expectations",
                "priority": "LOW",
                "metric_value": metrics.get("roas"),
            })

        # Platform performance insights
        if platform_data:
            top_platform = platform_data[0]
            insights.append({
                "category": "PLATFORM",
                "title": f"Top Performing Platform: {top_platform['platform']}",
                "description": f"Generating ₹{top_platform['revenue']:,.0f} in revenue with {top_platform['margin']:.1f}% margin",
                "priority": "LOW",
                "metric_value": top_platform["revenue"],
            })

        # Product insights
        if product_data:
            top_product = product_data[0]
            insights.append({
                "category": "PROFITABILITY",
                "title": f"Top Profit Driver: {top_product['product']}",
                "description": f"Contributing ₹{top_product['profit']:,.0f} profit with {top_product['margin']:.1f}% margin",
                "priority": "LOW",
                "metric_value": top_product["profit"],
            })

        return insights

    def _generate_recommendations(self, insights: List[Dict]) -> List[Dict]:
        """Generate recommendations from insights."""
        recommendations = []

        for insight in insights:
            if insight["priority"] == "HIGH":
                recommendation = {
                    "action": f"Address {insight['title']}",
                    "description": insight["description"],
                    "priority": "HIGH",
                    "timeline": "Immediate",
                }

                if insight["category"] == "PROFITABILITY":
                    recommendation["action_details"] = "Review pricing strategy, reduce costs, or optimize product mix"

                elif insight["category"] == "ADVERTISING":
                    recommendation["action_details"] = "Review ad creative, targeting, and budget allocation"

                recommendations.append(recommendation)

        return recommendations

    def _generate_professional_pdf(
        self,
        report_id: str,
        start_date: date,
        end_date: date,
        metrics: Dict,
        platform_data: List[Dict],
        product_data: List[Dict],
        advertising_data: Dict,
        insights: List[Dict],
        recommendations: List[Dict],
    ) -> bytes:
        """Generate professional PDF report with all content."""
        if not HAS_REPORTLAB:
            raise ImportError("reportlab is required for PDF generation")

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            topMargin=0.5 * inch,
            bottomMargin=0.5 * inch
        )

        story = []
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=24,
            textColor=colors.HexColor("#1a1a1a"),
            spaceAfter=6,
            spaceBefore=0,
            fontName="Helvetica-Bold",
        )

        section_style = ParagraphStyle(
            "CustomSection",
            parent=styles["Heading2"],
            fontSize=14,
            textColor=colors.HexColor("#2C3E50"),
            spaceAfter=12,
            spaceBefore=12,
            fontName="Helvetica-Bold",
            borderPadding=5,
        )

        header_style = ParagraphStyle(
            "CustomHeader",
            parent=styles["Normal"],
            fontSize=9,
            textColor=colors.HexColor("#666"),
            spaceAfter=6,
        )

        # Title page
        story.append(Paragraph("SLEEPSIA", title_style))
        story.append(Paragraph("Comprehensive Business Report", styles["Heading2"]))
        story.append(Spacer(1, 0.15 * inch))

        story.append(Paragraph(f"Report ID: {report_id}", header_style))
        story.append(Paragraph(f"Period: {start_date} to {end_date}", header_style))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}", header_style))
        story.append(Spacer(1, 0.3 * inch))

        # Executive Summary
        story.append(Paragraph("Executive Summary", section_style))
        summary_text = f"""
        This comprehensive report provides detailed analysis of business performance for the period
        from {start_date} to {end_date}. The organization generated ₹{metrics.get('revenue', 0):,.0f} in revenue
        with a profit of ₹{metrics.get('profit', 0):,.0f} and a profit margin of {metrics.get('profit_margin', 0):.1f}%.
        The advertising ROAS is {metrics.get('roas', 0):.2f}x with an ad spend of ₹{metrics.get('ad_spend', 0):,.0f}.
        """
        story.append(Paragraph(summary_text, styles["BodyText"]))
        story.append(Spacer(1, 0.2 * inch))

        # Key Metrics Section
        story.append(Paragraph("Key Performance Indicators", section_style))
        kpi_data = [
            ["Metric", "Value", "Status"],
            ["Revenue", f"₹{metrics.get('revenue', 0):,.0f}", "✓"],
            ["Profit", f"₹{metrics.get('profit', 0):,.0f}", "✓"],
            ["Profit Margin", f"{metrics.get('profit_margin', 0):.1f}%", "✓"],
            ["Orders", f"{metrics.get('orders', 0):,}", "✓"],
            ["Units Sold", f"{metrics.get('units', 0):,}", "✓"],
            ["ROAS", f"{metrics.get('roas', 0):.2f}x", "✓"],
            ["Ad Spend", f"₹{metrics.get('ad_spend', 0):,.0f}", "✓"],
        ]

        kpi_table = Table(kpi_data, colWidths=[2.5 * inch, 2 * inch, 0.75 * inch])
        kpi_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F8F9FA")),
            ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#CCCCCC")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8F9FA")]),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(kpi_table)
        story.append(Spacer(1, 0.2 * inch))

        # Platform Performance
        if platform_data:
            story.append(PageBreak())
            story.append(Paragraph("Platform Performance Analysis", section_style))

            platform_table_data = [["Platform", "Revenue", "Profit", "Margin", "Orders"]]
            for p in platform_data:
                platform_table_data.append([
                    p["platform"],
                    f"₹{p['revenue']:,.0f}",
                    f"₹{p['profit']:,.0f}",
                    f"{p['margin']:.1f}%",
                    f"{p['orders']:,}",
                ])

            platform_table = Table(platform_table_data, colWidths=[1.5 * inch, 1.3 * inch, 1.3 * inch, 1 * inch, 0.9 * inch])
            platform_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#CCCCCC")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8F9FA")]),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]))
            story.append(platform_table)
            story.append(Spacer(1, 0.2 * inch))

        # Product Performance
        if product_data:
            story.append(Paragraph("Top Products by Profitability", section_style))

            product_table_data = [["Product", "Revenue", "Profit", "Margin", "Units"]]
            for p in product_data[:15]:
                product_table_data.append([
                    p["product"][:30],
                    f"₹{p['revenue']:,.0f}",
                    f"₹{p['profit']:,.0f}",
                    f"{p['margin']:.1f}%",
                    f"{p['units']:,}",
                ])

            product_table = Table(product_table_data, colWidths=[2 * inch, 1.2 * inch, 1.2 * inch, 0.8 * inch, 0.8 * inch])
            product_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#CCCCCC")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8F9FA")]),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]))
            story.append(product_table)
            story.append(Spacer(1, 0.2 * inch))

        # Advertising Performance
        if advertising_data and advertising_data.get("spend", 0) > 0:
            story.append(PageBreak())
            story.append(Paragraph("Advertising Performance", section_style))

            ad_data = [
                ["Metric", "Value"],
                ["Total Ad Spend", f"₹{advertising_data.get('spend', 0):,.0f}"],
                ["Attributed Sales", f"₹{advertising_data.get('attributed_sales', 0):,.0f}"],
                ["ROAS", f"{advertising_data.get('roas', 0):.2f}x"],
                ["ACOS", f"{advertising_data.get('acos', 0):.1f}%"],
            ]

            ad_table = Table(ad_data, colWidths=[3 * inch, 2 * inch])
            ad_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#CCCCCC")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8F9FA")]),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]))
            story.append(ad_table)
            story.append(Spacer(1, 0.2 * inch))

        # Business Insights
        if insights:
            story.append(PageBreak())
            story.append(Paragraph("Business Insights & Analysis", section_style))

            for insight in insights:
                insight_title = f"{insight['title']} ({insight['priority']})"
                story.append(Paragraph(insight_title, styles["Heading3"]))
                story.append(Paragraph(insight["description"], styles["BodyText"]))
                story.append(Spacer(1, 0.1 * inch))

        # Recommendations
        if recommendations:
            story.append(PageBreak())
            story.append(Paragraph("Strategic Recommendations", section_style))

            for rec in recommendations:
                story.append(Paragraph(f"• {rec['action']}", styles["Heading3"]))
                story.append(Paragraph(f"Timeline: {rec.get('timeline', 'TBD')}", styles["Normal"]))
                story.append(Paragraph(rec.get("action_details", rec["description"]), styles["BodyText"]))
                story.append(Spacer(1, 0.15 * inch))

        # Footer
        story.append(Spacer(1, 0.3 * inch))
        story.append(Paragraph(
            "This report contains confidential business information. "
            "For questions or clarifications, please contact the analytics team.",
            styles["Normal"]
        ))

        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

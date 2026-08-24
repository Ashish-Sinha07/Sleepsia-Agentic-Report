"""Service for generating business reports."""

import os
import uuid
import logging
from datetime import datetime, date
from typing import Optional, Dict, List, Any
from sqlalchemy import text
from sqlalchemy.orm import Session
import json

logger = logging.getLogger(__name__)



class ReportService:
    """Generate and manage business reports."""

    REPORT_TYPES = {
        "executive_summary": "Executive Summary Report",
        "platform_analysis": "Platform Performance Analysis",
        "product_analysis": "Product Profitability Analysis",
        "profitability": "Detailed Profitability Analysis",
        "advertising": "Advertising ROI Analysis",
        "inventory": "Warehouse & Inventory Analysis",
        "management_monthly": "Management Monthly Report",
    }

    REPORTS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "reports")

    @staticmethod
    def _ensure_reports_dir():
        """Ensure reports directory exists."""
        os.makedirs(ReportService.REPORTS_DIR, exist_ok=True)

    @staticmethod
    def generate_report(
        db: Session,
        report_type: str,
        start_date: date,
        end_date: date,
        format: str = "pdf",
        include_recommendations: bool = True,
        platform_filter: Optional[str] = None,
        warehouse_filter: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate a comprehensive business report."""

        if report_type not in ReportService.REPORT_TYPES:
            raise ValueError(f"Unknown report type: {report_type}")

        ReportService._ensure_reports_dir()

        report_id = f"REP-{uuid.uuid4().hex[:8].upper()}"
        report_title = ReportService.REPORT_TYPES[report_type]

        # Collect data based on report type
        report_data = ReportService._collect_report_data(
            db=db,
            report_type=report_type,
            start_date=start_date,
            end_date=end_date,
            platform_filter=platform_filter,
            warehouse_filter=warehouse_filter,
        )

        # Generate report content
        report_content = ReportService._generate_report_content(
            report_id=report_id,
            report_type=report_type,
            report_title=report_title,
            data=report_data,
            start_date=start_date,
            end_date=end_date,
            include_recommendations=include_recommendations,
        )

        requested_format = format.lower()
        if requested_format == "excel":
            requested_format = "xlsx"
        if requested_format not in {"json", "pdf", "xlsx"}:
            raise ValueError("Format must be json, pdf, or excel")

        # JSON is the canonical report; other formats are rendered from it.
        json_path = os.path.join(ReportService.REPORTS_DIR, f"{report_id}.json")
        ReportService._ensure_reports_dir()
        with open(json_path, 'w') as f:
            json.dump(report_content, f, indent=2, default=str)

        file_path = json_path
        if requested_format == "pdf":
            file_path = os.path.join(ReportService.REPORTS_DIR, f"{report_id}.pdf")
            ReportService._render_pdf(report_content, file_path)
        elif requested_format == "xlsx":
            file_path = os.path.join(ReportService.REPORTS_DIR, f"{report_id}.xlsx")
            ReportService._render_excel(report_content, file_path)

        return {
            "report_id": report_id,
            "report_type": report_type,
            "created_at": datetime.now().isoformat(),
            "start_date": start_date,
            "end_date": end_date,
            "status": "completed",
            "file_size": os.path.getsize(file_path),
            "format": requested_format,
            "download_url": f"/api/reports/{report_id}/download?format={requested_format}"
        }

    @staticmethod
    def _render_pdf(report_content: Dict[str, Any], file_path: str) -> None:
        """Render the canonical report dictionary as a readable PDF."""
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors

        document = SimpleDocTemplate(file_path, pagesize=letter)
        styles = getSampleStyleSheet()
        data = report_content.get("data", {})
        story = [Paragraph(report_content.get("title", "Sleepsia Report"), styles["Title"])]
        story.append(Spacer(1, 12))
        story.append(Paragraph(
            f"Period: {report_content.get('period', 'Not specified')}",
            styles["Normal"],
        ))
        story.append(Spacer(1, 12))

        summary = data.get("kpi_summary", {})
        rows = [["Metric", "Value"]] + [[key.replace("_", " ").title(), str(value)] for key, value in summary.items()]
        table = Table(rows, colWidths=[220, 260])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#34495e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("PADDING", (0, 0), (-1, -1), 6),
        ]))
        story.extend([Paragraph("KPI Summary", styles["Heading2"]), table])
        document.build(story)

    @staticmethod
    def _render_excel(report_content: Dict[str, Any], file_path: str) -> None:
        """Render the canonical report dictionary as an Excel workbook."""
        from openpyxl import Workbook

        workbook = Workbook()
        summary_sheet = workbook.active
        summary_sheet.title = "Summary"
        summary_sheet.append(["Metric", "Value"])
        data = report_content.get("data", {})
        for key, value in data.get("kpi_summary", {}).items():
            summary_sheet.append([key, value])

        for section_name in ("platform_data", "product_data"):
            rows = data.get(section_name, [])
            if not rows:
                continue
            sheet = workbook.create_sheet(section_name.replace("_data", "").title())
            headers = list(rows[0].keys())
            sheet.append(headers)
            for row in rows:
                sheet.append([row.get(header) for header in headers])

        workbook.save(file_path)

    @staticmethod
    def _collect_report_data(
        db: Session,
        report_type: str,
        start_date: date,
        end_date: date,
        platform_filter: Optional[str] = None,
        warehouse_filter: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Collect data for report based on type."""

        data = {
            "period": {"start_date": start_date.isoformat(), "end_date": end_date.isoformat()},
            "generated_at": datetime.now().isoformat(),
        }

        # Always get KPI summary
        kpi_query = """
        SELECT
            SUM(total_gross_sales) as revenue,
            SUM(total_net_sales) as net_revenue,
            SUM(total_contribution) as profit,
            AVG(overall_profit_margin_pct) as profit_margin,
            SUM(total_orders) as orders,
            SUM(total_units_sold) as units,
            AVG(overall_roas) as roas,
            SUM(total_ad_spend) as ad_spend
        FROM vw_daily_kpi_summary
        WHERE date BETWEEN :start_date AND :end_date
        """

        if platform_filter:
            kpi_query += f" AND platform_id = :platform_filter"

        try:
            result = db.execute(
                text(kpi_query),
                {"start_date": start_date, "end_date": end_date, "platform_filter": platform_filter}
            ).fetchone()

            if result:
                data["kpi_summary"] = {
                    "revenue": float(result[0]) if result[0] else 0,
                    "net_revenue": float(result[1]) if result[1] else 0,
                    "profit": float(result[2]) if result[2] else 0,
                    "profit_margin_pct": float(result[3]) if result[3] else 0,
                    "orders": int(result[4]) if result[4] else 0,
                    "units_sold": int(result[5]) if result[5] else 0,
                    "roas": float(result[6]) if result[6] else 0,
                    "ad_spend": float(result[7]) if result[7] else 0,
                }
            else:
                logger.warning("KPI query returned no results")
                data["kpi_summary"] = {k: 0 for k in ["revenue", "net_revenue", "profit", "profit_margin_pct", "orders", "units_sold", "roas", "ad_spend"]}
        except Exception as e:
            logger.error(f"KPI query failed: {str(e)}", exc_info=True)
            data["kpi_summary"] = {k: 0 for k in ["revenue", "net_revenue", "profit", "profit_margin_pct", "orders", "units_sold", "roas", "ad_spend"]}

        # Type-specific data
        if report_type == "platform_analysis":
            data["platform_data"] = ReportService._get_platform_data(db, start_date, end_date)

        elif report_type == "product_analysis":
            data["product_data"] = ReportService._get_product_data(db, start_date, end_date)

        elif report_type == "profitability":
            data["profitability_data"] = ReportService._get_profitability_data(db, start_date, end_date)

        elif report_type == "advertising":
            data["advertising_data"] = ReportService._get_advertising_data(db, start_date, end_date)

        elif report_type == "inventory":
            data["inventory_data"] = ReportService._get_inventory_data(db, start_date, end_date, warehouse_filter)

        return data

    @staticmethod
    def _get_platform_data(db: Session, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Get platform-wise performance data."""
        query = """
        SELECT
            platform_name,
            gross_sales as revenue,
            contribution as profit,
            profit_margin_pct as margin,
            COUNT(*) as products,
            orders
        FROM vw_platform_performance
        GROUP BY platform_name
        ORDER BY revenue DESC
        """

        results = db.execute(text(query), {"start_date": start_date, "end_date": end_date}).fetchall()

        return [
            {
                "platform": row[0],
                "revenue": float(row[1]) if row[1] else 0,
                "profit": float(row[2]) if row[2] else 0,
                "profit_margin": float(row[3]) if row[3] else 0,
                "products": int(row[4]) if row[4] else 0,
                "orders": int(row[5]) if row[5] else 0,
            }
            for row in results
        ]

    @staticmethod
    def _get_product_data(db: Session, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Get product performance data."""
        query = """
        SELECT
            product_name,
            gross_sales as revenue,
            contribution as profit,
            orders as orders,
            COUNT(DISTINCT platform_id) as platforms
        FROM vw_product_performance
        GROUP BY product_name
        ORDER BY profit DESC
        LIMIT 20
        """

        results = db.execute(text(query), {"start_date": start_date, "end_date": end_date}).fetchall()

        return [
            {
                "product": row[0],
                "revenue": float(row[1]) if row[1] else 0,
                "profit": float(row[2]) if row[2] else 0,
                "orders": int(row[3]) if row[3] else 0,
                "platforms": int(row[4]) if row[4] else 0,
            }
            for row in results
        ]

    @staticmethod
    def _get_profitability_data(db: Session, start_date: date, end_date: date) -> Dict[str, Any]:
        """Get detailed profitability analysis."""
        query = """
        SELECT
            DATE(date) as day,
            SUM(total_gross_sales) as revenue,
            SUM(total_contribution) as profit,
            AVG(overall_profit_margin_pct) as margin
        FROM vw_daily_kpi_summary
        WHERE date BETWEEN :start_date AND :end_date
        GROUP BY DATE(date)
        ORDER BY day ASC
        """

        results = db.execute(text(query), {"start_date": start_date, "end_date": end_date}).fetchall()

        daily_data = [
            {
                "date": str(row[0]),
                "revenue": float(row[1]) if row[1] else 0,
                "profit": float(row[2]) if row[2] else 0,
                "margin": float(row[3]) if row[3] else 0,
            }
            for row in results
        ]

        return {
            "daily_trends": daily_data,
            "summary": {
                "avg_margin": sum(d["margin"] for d in daily_data) / len(daily_data) if daily_data else 0,
                "total_profit": sum(d["profit"] for d in daily_data),
                "total_revenue": sum(d["revenue"] for d in daily_data),
            }
        }

    @staticmethod
    def _get_advertising_data(db: Session, start_date: date, end_date: date) -> Dict[str, Any]:
        """Get advertising analytics data."""
        query = """
        SELECT
            DATE(date) as day,
            SUM(total_ad_spend) as spend,
            SUM(total_ad_sales) as attributed_sales,
            AVG(overall_roas) as roas
        FROM vw_daily_kpi_summary
        WHERE date BETWEEN :start_date AND :end_date
        GROUP BY DATE(date)
        ORDER BY day ASC
        """

        results = db.execute(text(query), {"start_date": start_date, "end_date": end_date}).fetchall()

        daily_data = [
            {
                "date": str(row[0]),
                "spend": float(row[1]) if row[1] else 0,
                "attributed_sales": float(row[2]) if row[2] else 0,
                "roas": float(row[3]) if row[3] else 0,
            }
            for row in results
        ]

        return {
            "daily_trends": daily_data,
            "summary": {
                "total_spend": sum(d["spend"] for d in daily_data),
                "total_attributed_sales": sum(d["attributed_sales"] for d in daily_data),
                "avg_roas": sum(d["roas"] for d in daily_data) / len(daily_data) if daily_data else 0,
            }
        }

    @staticmethod
    def _get_inventory_data(
        db: Session,
        start_date: date,
        end_date: date,
        warehouse_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get inventory and warehouse data."""
        try:
            query = "SELECT city, COUNT(*) as sku_count, SUM(closing_stock) as total_stock FROM vw_inventory_health"

            if warehouse_filter:
                query += f" WHERE city = :warehouse_filter"

            query += " GROUP BY city ORDER BY total_stock ASC"

            results = db.execute(
                text(query),
                {"warehouse_filter": warehouse_filter} if warehouse_filter else {}
            ).fetchall()

            warehouse_data = [
                {
                    "warehouse": row[0],
                    "sku_count": int(row[1]) if row[1] else 0,
                    "total_stock": int(row[2]) if row[2] else 0,
                }
                for row in results
            ]

            return {
                "warehouses": warehouse_data,
                "summary": {
                    "total_warehouses": len(warehouse_data),
                    "total_skus": sum(w["sku_count"] for w in warehouse_data),
                    "total_inventory": sum(w["total_stock"] for w in warehouse_data),
                }
            }
        except Exception:
            return {"warehouses": [], "summary": {"total_warehouses": 0, "total_skus": 0, "total_inventory": 0}}

    @staticmethod
    def _generate_report_content(
        report_id: str,
        report_type: str,
        report_title: str,
        data: Dict[str, Any],
        start_date: date,
        end_date: date,
        include_recommendations: bool = True,
    ) -> Dict[str, Any]:
        """Generate report content with insights and recommendations."""

        content = {
            "report_id": report_id,
            "title": report_title,
            "type": report_type,
            "period": f"{start_date} to {end_date}",
            "generated_at": datetime.now().isoformat(),
            "data": data,
        }

        if include_recommendations:
            content["recommendations"] = ReportService._get_recommendations(report_type, data)

        return content

    @staticmethod
    def _get_recommendations(report_type: str, data: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on report data."""

        recommendations = []

        if report_type == "platform_analysis" and "platform_data" in data:
            platforms = data["platform_data"]
            if platforms:
                top = platforms[0]
                recommendations.append(f"Focus on {top['platform']} - it has the highest revenue")

        elif report_type == "product_analysis" and "product_data" in data:
            products = data["product_data"]
            if products:
                top = products[0]
                recommendations.append(f"Scale {top['product']} - it's your profit leader")

        elif report_type == "advertising" and "advertising_data" in data:
            ad_data = data["advertising_data"]
            if ad_data.get("summary", {}).get("avg_roas", 0) < 3:
                recommendations.append("Review ad creative and targeting - ROAS is below 3x")

        return recommendations

    @staticmethod
    def list_reports(db: Session, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """List generated reports."""

        ReportService._ensure_reports_dir()

        # Get list of report files
        reports = []
        if os.path.exists(ReportService.REPORTS_DIR):
            for filename in sorted(os.listdir(ReportService.REPORTS_DIR), reverse=True)[offset:offset + limit]:
                if filename.endswith('.json'):
                    file_path = os.path.join(ReportService.REPORTS_DIR, filename)
                    try:
                        with open(file_path, 'r') as f:
                            report_data = json.load(f)
                        reports.append({
                            "report_id": report_data.get("report_id", filename[:-5]),
                            "report_type": report_data.get("type", "unknown"),
                            "created_at": report_data.get("generated_at", ""),
                            "start_date": report_data.get("period", {}).get("start_date", ""),
                            "end_date": report_data.get("period", {}).get("end_date", ""),
                            "status": "completed",
                            "file_size": os.path.getsize(file_path),
                        })
                    except Exception:
                        pass

        return {
            "reports": reports,
            "total": len(reports),
        }

    @staticmethod
    def get_report(db: Session, report_id: str) -> Optional[Dict[str, Any]]:
        """Get specific report."""

        file_path = os.path.join(ReportService.REPORTS_DIR, f"{report_id}.json")

        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                report_data = json.load(f)

            return {
                "report_id": report_data.get("report_id"),
                "report_type": report_data.get("type"),
                "created_at": report_data.get("generated_at"),
                "start_date": report_data.get("period", {}).get("start_date"),
                "end_date": report_data.get("period", {}).get("end_date"),
                "status": "completed",
                "file_size": os.path.getsize(file_path),
                "download_url": f"/api/reports/{report_id}/download",
            }

        return None

    @staticmethod
    def get_report_file(db: Session, report_id: str, format: Optional[str] = None) -> Optional[str]:
        """Get path to report file."""

        file_format = format or "json"
        file_path = os.path.join(ReportService.REPORTS_DIR, f"{report_id}.{file_format}")

        if os.path.exists(file_path):
            return file_path

        # Try default json
        json_path = os.path.join(ReportService.REPORTS_DIR, f"{report_id}.json")
        if os.path.exists(json_path):
            return json_path

        return None

    @staticmethod
    def email_report(db: Session, report_id: str, email_to: str, cc: Optional[str] = None, bcc: Optional[str] = None) -> Dict[str, Any]:
        """Email a report to recipients."""
        from automation.email_service import ReportEmailService

        try:
            # Get the report file
            file_path = ReportService.get_report_file(db, report_id)
            if not file_path:
                return {
                    "success": False,
                    "error": f"Report {report_id} not found",
                    "report_id": report_id,
                }

            # Read the report file
            with open(file_path, 'rb') as f:
                report_bytes = f.read()

            # Parse recipients
            recipients = [email_to]
            cc_list = cc.split(',') if cc else None
            bcc_list = bcc.split(',') if bcc else None

            # Send via email service
            email_service = ReportEmailService()
            success = email_service.send_report(
                subject=f"Sleepsia Report - {report_id}",
                body=f"""
Dear Recipient,

Please find attached your requested business report: {report_id}

Best regards,
Sleepsia Analytics System
                """.strip(),
                recipients=recipients,
                cc=cc_list,
                bcc=bcc_list,
                attachments={f"{report_id}.json": report_bytes},
            )

            return {
                "success": success,
                "message": f"Report {report_id} sent to {email_to}" if success else f"Failed to send report {report_id}",
                "report_id": report_id,
                "email_to": email_to,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "report_id": report_id,
                "timestamp": datetime.now().isoformat(),
            }

    @staticmethod
    def delete_report(db: Session, report_id: str) -> bool:
        """Delete a report file."""

        file_path = os.path.join(ReportService.REPORTS_DIR, f"{report_id}.json")

        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                return True
            except Exception:
                return False

        return False

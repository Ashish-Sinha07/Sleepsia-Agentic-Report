"""Orchestrator that coordinates all agents for business intelligence."""

import logging
from typing import Optional
from datetime import datetime, date

from agents import (
    DataValidationAgent,
    DataAnalysisAgent,
    InsightRecommendationAgent,
    LLMAnalysisAgent,
    ReportAgent,
)
from analytics.metrics_engine import MetricsEngine
from analytics.models import ProductMetrics, PlatformMetrics
from backend.app.config import settings

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Central orchestrator for all business intelligence agents.

    Coordinates:
    1. Validation Agent - validates source data
    2. Metrics Engine - calculates financial metrics
    3. Analysis Agent - analyzes metrics and finds patterns
    4. Insight Recommendation Agent - generates recommendations
    5. LLM Analysis Agent - provides natural language insights
    6. Report Agent - generates management reports
    """

    def __init__(self):
        """Initialize all agents."""
        self.validation_agent = DataValidationAgent()
        self.metrics_engine = MetricsEngine()
        self.analysis_agent = DataAnalysisAgent()
        self.insight_agent = InsightRecommendationAgent()
        self.llm_agent = LLMAnalysisAgent(
            api_key=settings.GROQ_API_KEY,
            model=settings.GROQ_MODEL,
        )
        self.report_agent = ReportAgent(
            api_key=settings.GROQ_API_KEY,
            model=settings.GROQ_MODEL,
        )

    def get_kpis(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        platform: Optional[str] = None,
        warehouse: Optional[str] = None,
    ) -> dict:
        """
        Get KPIs for the executive dashboard.

        Flow:
        1. Query database for raw data (filtered by date/platform/warehouse)
        2. Calculate metrics using MetricsEngine
        3. Return aggregated KPIs
        """
        logger.info(f"Getting KPIs: start_date={start_date}, end_date={end_date}, platform={platform}")

        try:
            from sqlalchemy import text
            from backend.app.database import SessionLocal

            db = SessionLocal()

            # Build query for KPI aggregation
            query = """
            SELECT
                COALESCE(SUM(total_orders), 0) as total_orders,
                COALESCE(SUM(total_units_sold), 0) as total_units_sold,
                COALESCE(SUM(total_gross_sales), 0) as total_gross_sales,
                COALESCE(SUM(total_net_sales), 0) as total_net_sales,
                COALESCE(SUM(total_contribution), 0) as total_contribution,
                COALESCE(SUM(total_ad_spend), 0) as total_ad_spend,
                COALESCE(SUM(total_units_returned), 0) as total_units_returned,
                COALESCE(SUM(total_units_cancelled), 0) as total_units_cancelled,
                COALESCE(AVG(overall_profit_margin_pct), 0) as profit_margin,
                COALESCE(AVG(overall_roas), 0) as roas,
                COALESCE(SUM(total_ad_sales), 0) as ad_sales,
                COALESCE(SUM(total_organic_sales), 0) as organic_sales
            FROM vw_daily_kpi_summary
            WHERE date BETWEEN :start_date AND :end_date
            """

            params = {"start_date": start_date, "end_date": end_date}

            if platform:
                query += " AND platform_id = :platform"
                params["platform"] = platform

            if warehouse:
                query += " AND warehouse_id = :warehouse"
                params["warehouse"] = warehouse

            result = db.execute(text(query), params).fetchone()
            db.close()

            if result:
                total_orders = float(result[0]) if result[0] else 0
                total_units = float(result[1]) if result[1] else 0
                revenue = float(result[2]) if result[2] else 0
                net_revenue = float(result[3]) if result[3] else 0
                profit = float(result[4]) if result[4] else 0
                ad_spend = float(result[5]) if result[5] else 0
                units_returned = float(result[6]) if result[6] else 0
                units_cancelled = float(result[7]) if result[7] else 0
                profit_margin = float(result[8]) if result[8] else 0
                roas = float(result[9]) if result[9] else 0
                ad_sales = float(result[10]) if result[10] else 0
                organic_sales = float(result[11]) if result[11] else 0

                return {
                    "period": {"start_date": str(start_date), "end_date": str(end_date)},
                    "total_revenue": revenue,
                    "net_revenue": net_revenue,
                    "gross_profit": profit,
                    "profit_margin_pct": profit_margin,
                    "total_orders": total_orders,
                    "total_units_sold": total_units,
                    "avg_order_value": revenue / total_orders if total_orders > 0 else 0,
                    "return_rate_pct": (units_returned / total_units * 100) if total_units > 0 else 0,
                    "cancellation_rate_pct": (units_cancelled / total_orders * 100) if total_orders > 0 else 0,
                    "ad_spend": ad_spend,
                    "ad_sales": ad_sales,
                    "organic_sales": organic_sales,
                    "roas": roas,
                    "acos_pct": (ad_spend / ad_sales * 100) if ad_sales > 0 else 0,
                }

            return {
                "error": "No data available for the selected period",
                "period": {"start_date": str(start_date), "end_date": str(end_date)},
            }

        except Exception as e:
            logger.error(f"Error getting KPIs: {str(e)}", exc_info=True)
            return {"error": str(e)}

    def analyze_product_performance(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        platform: Optional[str] = None,
    ) -> dict:
        """
        Analyze product performance across all dimensions.

        Flow:
        1. Query database for product sales data
        2. Calculate product metrics using MetricsEngine
        3. Analyze metrics using DataAnalysisAgent
        4. Generate insights using InsightRecommendationAgent
        """
        logger.info(f"Analyzing product performance: start_date={start_date}, end_date={end_date}")

        try:
            from sqlalchemy import text
            from backend.app.database import SessionLocal

            db = SessionLocal()

            # Query database for product data
            query = """
            SELECT
                product_name,
                SUM(total_gross_sales) as revenue,
                SUM(total_net_sales) as net_revenue,
                SUM(total_contribution) as profit,
                SUM(total_contribution) / NULLIF(SUM(total_gross_sales), 0) * 100 as profit_margin,
                SUM(total_units_sold) as units_sold,
                SUM(total_orders) as orders,
                SUM(total_units_returned) / NULLIF(SUM(total_units_sold), 0) * 100 as return_rate,
                COUNT(DISTINCT platform_id) as platforms
            FROM vw_product_performance
            WHERE date BETWEEN :start_date AND :end_date
            """

            params = {"start_date": start_date, "end_date": end_date}

            if platform:
                query += " AND platform_id = :platform"
                params["platform"] = platform

            query += " GROUP BY product_name ORDER BY profit DESC"

            results = db.execute(text(query), params).fetchall()

            products = [
                {
                    "product_name": row[0],
                    "revenue": float(row[1]) if row[1] else 0,
                    "net_revenue": float(row[2]) if row[2] else 0,
                    "profit": float(row[3]) if row[3] else 0,
                    "profit_margin_pct": float(row[4]) if row[4] else 0,
                    "units_sold": int(row[5]) if row[5] else 0,
                    "orders": int(row[6]) if row[6] else 0,
                    "return_rate_pct": float(row[7]) if row[7] else 0,
                    "platforms": int(row[8]) if row[8] else 0,
                }
                for row in results
            ]

            db.close()

            # Categorize products by profitability
            healthy = [p for p in products if p["profit_margin_pct"] >= 15]
            at_risk = [p for p in products if 5 <= p["profit_margin_pct"] < 15]
            unprofitable = [p for p in products if p["profit_margin_pct"] < 5]

            return {
                "total_products": len(products),
                "healthy_products": len(healthy),
                "at_risk_products": len(at_risk),
                "unprofitable_products": len(unprofitable),
                "products": products[:10],  # Top 10 products
                "healthy_list": [p["product_name"] for p in healthy],
                "at_risk_list": [p["product_name"] for p in at_risk],
                "unprofitable_list": [p["product_name"] for p in unprofitable],
            }

        except Exception as e:
            logger.error(f"Error analyzing product performance: {str(e)}", exc_info=True)
            return {"error": str(e)}

    def analyze_platform_performance(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> dict:
        """
        Analyze platform-wise performance.

        Flow:
        1. Query database for each platform
        2. Calculate platform metrics
        3. Compare platforms using analysis agent
        4. Generate comparative insights
        """
        logger.info(f"Analyzing platform performance: start_date={start_date}, end_date={end_date}")

        try:
            from sqlalchemy import text
            from backend.app.database import SessionLocal

            db = SessionLocal()

            # Query database for platform data
            query = """
            SELECT
                platform_id,
                platform_name,
                SUM(total_gross_sales) as revenue,
                SUM(total_net_sales) as net_revenue,
                SUM(total_contribution) as profit,
                SUM(total_contribution) / NULLIF(SUM(total_gross_sales), 0) * 100 as profit_margin,
                SUM(total_orders) as orders,
                SUM(total_units_sold) as units_sold,
                SUM(total_ad_spend) as ad_spend,
                AVG(overall_roas) as roas,
                COUNT(DISTINCT product_id) as products
            FROM vw_platform_performance
            WHERE date BETWEEN :start_date AND :end_date
            GROUP BY platform_id, platform_name
            ORDER BY revenue DESC
            """

            params = {"start_date": start_date, "end_date": end_date}
            results = db.execute(text(query), params).fetchall()

            platforms = [
                {
                    "platform_id": row[0],
                    "platform_name": row[1],
                    "revenue": float(row[2]) if row[2] else 0,
                    "net_revenue": float(row[3]) if row[3] else 0,
                    "profit": float(row[4]) if row[4] else 0,
                    "profit_margin_pct": float(row[5]) if row[5] else 0,
                    "orders": int(row[6]) if row[6] else 0,
                    "units_sold": int(row[7]) if row[7] else 0,
                    "ad_spend": float(row[8]) if row[8] else 0,
                    "roas": float(row[9]) if row[9] else 0,
                    "products": int(row[10]) if row[10] else 0,
                }
                for row in results
            ]

            db.close()

            # Generate comparative analysis
            if platforms:
                top_revenue = platforms[0]["platform_name"]
                top_profit = max(platforms, key=lambda p: p["profit_margin_pct"])
                highest_roas = max(platforms, key=lambda p: p["roas"])

                return {
                    "platforms": [p["platform_name"] for p in platforms],
                    "analysis": {
                        "top_revenue_platform": top_revenue,
                        "highest_margin_platform": top_profit["platform_name"],
                        "best_roas_platform": highest_roas["platform_name"],
                        "platform_count": len(platforms),
                    },
                    "platform_details": platforms,
                }

            return {
                "platforms": [],
                "analysis": {},
            }

        except Exception as e:
            logger.error(f"Error analyzing platform performance: {str(e)}", exc_info=True)
            return {"error": str(e)}

    def get_alerts(self) -> dict:
        """
        Generate business alerts based on metrics and thresholds.

        Flow:
        1. Calculate current metrics
        2. Compare against thresholds
        3. Generate alerts using analysis agent
        4. Rank by severity
        """
        logger.info("Generating business alerts")

        try:
            from datetime import timedelta
            from sqlalchemy import text
            from backend.app.database import SessionLocal

            db = SessionLocal()

            today = date.today()
            seven_days_ago = today - timedelta(days=7)

            # Get latest metrics
            query = """
            SELECT
                AVG(overall_profit_margin_pct) as avg_margin,
                AVG(overall_roas) as avg_roas,
                SUM(total_units_returned) / NULLIF(SUM(total_units_sold), 0) * 100 as return_rate,
                SUM(total_units_cancelled) / NULLIF(SUM(total_orders), 0) * 100 as cancel_rate
            FROM vw_daily_kpi_summary
            WHERE date BETWEEN :start_date AND :end_date
            """

            result = db.execute(
                text(query),
                {"start_date": seven_days_ago, "end_date": today}
            ).fetchone()

            db.close()

            alerts = {
                "critical": [],
                "warning": [],
                "info": [],
            }

            if result:
                profit_margin = float(result[0]) if result[0] else 0
                roas = float(result[1]) if result[1] else 0
                return_rate = float(result[2]) if result[2] else 0
                cancel_rate = float(result[3]) if result[3] else 0

                # Critical alerts
                if profit_margin < 5:
                    alerts["critical"].append({
                        "severity": "critical",
                        "metric": "profit_margin",
                        "value": profit_margin,
                        "threshold": 5,
                        "message": f"Critical: Profit margin is {profit_margin:.1f}%, below 5% threshold"
                    })

                if roas < 1:
                    alerts["critical"].append({
                        "severity": "critical",
                        "metric": "roas",
                        "value": roas,
                        "threshold": 1,
                        "message": f"Critical: ROAS is {roas:.2f}x, your ads are losing money"
                    })

                # Warning alerts
                if 5 <= profit_margin < 10:
                    alerts["warning"].append({
                        "severity": "warning",
                        "metric": "profit_margin",
                        "value": profit_margin,
                        "threshold": 10,
                        "message": f"Warning: Profit margin is {profit_margin:.1f}%, below healthy 10% threshold"
                    })

                if 1 <= roas < 3:
                    alerts["warning"].append({
                        "severity": "warning",
                        "metric": "roas",
                        "value": roas,
                        "threshold": 3,
                        "message": f"Warning: ROAS is {roas:.2f}x, below optimal 3x threshold"
                    })

                if return_rate > 15:
                    alerts["warning"].append({
                        "severity": "warning",
                        "metric": "return_rate",
                        "value": return_rate,
                        "threshold": 15,
                        "message": f"Warning: Return rate is {return_rate:.1f}%, indicating quality issues"
                    })

                if cancel_rate > 8:
                    alerts["warning"].append({
                        "severity": "warning",
                        "metric": "cancel_rate",
                        "value": cancel_rate,
                        "threshold": 8,
                        "message": f"Warning: Cancellation rate is {cancel_rate:.1f}%, check delivery/pricing"
                    })

                # Info alerts
                if profit_margin >= 20:
                    alerts["info"].append({
                        "severity": "info",
                        "metric": "profit_margin",
                        "value": profit_margin,
                        "message": f"Excellent: Profit margin is {profit_margin:.1f}%, operating efficiently"
                    })

            return alerts

        except Exception as e:
            logger.error(f"Error generating alerts: {str(e)}", exc_info=True)
            return {"error": str(e), "critical": [], "warning": [], "info": []}

    def ask_question(self, question: str, context: Optional[dict] = None) -> dict:
        """
        Answer a business question using the AI assistant.

        Flow:
        1. Parse question intent (LLMAnalysisAgent)
        2. Identify required metrics and data
        3. Query database and calculate metrics
        4. Generate natural language response
        5. Provide recommendations
        """
        logger.info(f"Processing question: {question}")

        try:
            from backend.app.services.ai_assistant_service import AIAssistantService
            from backend.app.database import SessionLocal

            db = SessionLocal()

            # Use AIAssistantService to answer the question
            # This service uses pattern-based logic with database queries
            response = AIAssistantService.answer_question(
                db=db,
                question=question,
                context=context
            )

            db.close()

            return response

        except Exception as e:
            logger.error(f"Error processing question: {str(e)}", exc_info=True)
            return {
                "question": question,
                "answer": f"I encountered an error processing your question: {str(e)}",
                "confidence": 0.0,
                "data_sources": [],
                "recommendations": [],
            }

    def generate_report(
        self,
        report_type: str,
        start_date: date,
        end_date: date,
        format: str = "pdf",
        filters: Optional[dict] = None,
    ) -> dict:
        """
        Generate a comprehensive business report.

        Flow:
        1. Query all relevant data
        2. Calculate all metrics
        3. Generate insights
        4. Render report using ReportAgent
        5. Return report file
        """
        logger.info(f"Generating {report_type} report: {start_date} to {end_date}")

        try:
            from backend.app.services.report_service import ReportService
            from backend.app.database import SessionLocal

            db = SessionLocal()

            # Use ReportService to generate the report
            report = ReportService.generate_report(
                db=db,
                report_type=report_type,
                start_date=start_date,
                end_date=end_date,
                format=format,
                include_recommendations=True,
                platform_filter=filters.get("platform") if filters else None,
                warehouse_filter=filters.get("warehouse") if filters else None,
            )

            db.close()

            return report

        except Exception as e:
            logger.error(f"Error generating report: {str(e)}", exc_info=True)
            return {
                "report_id": None,
                "report_type": report_type,
                "status": "failed",
                "error": str(e),
            }

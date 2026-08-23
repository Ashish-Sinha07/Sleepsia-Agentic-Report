"""Service for AI-powered business assistant."""

from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import Optional, Dict, List, Any
import json
import re


class AIAssistantService:
    """Handle natural language questions about business data."""

    # Metric definitions for explanations
    METRIC_DEFINITIONS = {
        "revenue": {
            "definition": "Total sales value from all channels",
            "formula": "Gross Sales - Discounts",
            "interpretation": "Higher revenue indicates better sales performance. Track daily to identify trends."
        },
        "profit": {
            "definition": "Revenue minus all costs and expenses",
            "formula": "Net Revenue - (Product Cost + Platform Fees + Ad Spend + Other Costs)",
            "interpretation": "Profit margin shows business efficiency. Healthy margin is 15-30% depending on category."
        },
        "profit_margin": {
            "definition": "Profit as a percentage of revenue",
            "formula": "(Profit / Revenue) * 100",
            "interpretation": "Higher margin is better. 20%+ is excellent. Below 10% needs attention."
        },
        "roas": {
            "definition": "Return on Ad Spend - revenue generated per rupee spent on ads",
            "formula": "Ad-Attributed Sales / Ad Spend",
            "interpretation": "ROAS > 3 is good. ROAS > 5 is excellent. Below 2 means unprofitable advertising."
        },
        "acos": {
            "definition": "Advertising Cost of Sale - percentage of ad sales spent on advertising",
            "formula": "(Ad Spend / Ad-Attributed Sales) * 100",
            "interpretation": "ACOS < 30% is good. ACOS > 50% means you're losing money on ads."
        },
        "return_rate": {
            "definition": "Percentage of sold units that are returned",
            "formula": "(Units Returned / Units Sold) * 100",
            "interpretation": "Industry average is 5-15%. Above 20% indicates product quality issues."
        },
        "cancellation_rate": {
            "definition": "Percentage of orders cancelled by customers",
            "formula": "(Orders Cancelled / Total Orders) * 100",
            "interpretation": "Below 5% is healthy. Above 10% suggests delivery or product issues."
        },
    }

    # Suggested questions
    SUGGESTED_QUESTIONS = [
        {
            "question": "Which platform is most profitable?",
            "category": "platform_analysis",
            "description": "Compare profit margins across Amazon, Flipkart, Blinkit, Myntra, and JioMart"
        },
        {
            "question": "Which products are losing money?",
            "category": "product_analysis",
            "description": "Identify unprofitable SKUs and their cost structure"
        },
        {
            "question": "Which platform has the best ROAS?",
            "category": "advertising",
            "description": "Compare ad efficiency across all marketing channels"
        },
        {
            "question": "Which warehouse needs replenishment?",
            "category": "inventory",
            "description": "Find low-stock warehouses that need urgent restocking"
        },
        {
            "question": "What are today's critical alerts?",
            "category": "alerts",
            "description": "View urgent business issues that need attention"
        },
        {
            "question": "Compare Amazon and Flipkart.",
            "category": "platform_comparison",
            "description": "Side-by-side performance comparison of two platforms"
        },
        {
            "question": "Which products have declining sales?",
            "category": "product_trends",
            "description": "Find products with negative sales momentum"
        },
        {
            "question": "What is my profit margin trend?",
            "category": "profitability",
            "description": "View how profit margins change over time"
        },
    ]

    @staticmethod
    def answer_question(
        db: Session,
        question: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Answer a business question using data from the database.

        Process:
        1. Parse the question to understand intent
        2. Identify relevant metrics and dimensions
        3. Query the database
        4. Generate insights
        5. Provide recommendations
        """
        question_lower = question.lower()
        answer = ""
        data_sources = []
        recommendations = []
        confidence = 0.0

        # Intent detection - simplified pattern matching
        if any(word in question_lower for word in ["platform", "channel", "amazon", "flipkart", "blinkit", "myntra", "jiomart"]):
            answer, sources, recs = AIAssistantService._answer_platform_question(db, question)
            data_sources.extend(sources)
            recommendations.extend(recs)
            confidence = 0.8

        elif any(word in question_lower for word in ["product", "sku", "item"]):
            answer, sources, recs = AIAssistantService._answer_product_question(db, question)
            data_sources.extend(sources)
            recommendations.extend(recs)
            confidence = 0.85

        elif any(word in question_lower for word in ["profit", "margin", "cost", "expense"]):
            answer, sources, recs = AIAssistantService._answer_profitability_question(db, question)
            data_sources.extend(sources)
            recommendations.extend(recs)
            confidence = 0.9

        elif any(word in question_lower for word in ["ad", "advertising", "roas", "acos", "spend", "impression"]):
            answer, sources, recs = AIAssistantService._answer_advertising_question(db, question)
            data_sources.extend(sources)
            recommendations.extend(recs)
            confidence = 0.85

        elif any(word in question_lower for word in ["inventory", "stock", "warehouse", "restock", "replenish"]):
            answer, sources, recs = AIAssistantService._answer_inventory_question(db, question)
            data_sources.extend(sources)
            recommendations.extend(recs)
            confidence = 0.8

        elif any(word in question_lower for word in ["return", "cancel", "quality", "issue"]):
            answer, sources, recs = AIAssistantService._answer_quality_question(db, question)
            data_sources.extend(sources)
            recommendations.extend(recs)
            confidence = 0.75

        else:
            answer = "I'm not sure how to answer that question. Try asking about platforms, products, profitability, advertising, inventory, or quality metrics."
            confidence = 0.2

        return {
            "question": question,
            "answer": answer,
            "confidence": confidence,
            "data_sources": list(set(data_sources)),
            "recommendations": recommendations
        }

    @staticmethod
    def _answer_platform_question(db: Session, question: str) -> tuple[str, List[str], List[str]]:
        """Answer questions about platform performance."""
        try:
            query = """
            SELECT
                platform_name,
                SUM(total_gross_sales) as revenue,
                SUM(total_contribution) as profit,
                SUM(total_gross_sales) > 0 AND SUM(total_contribution) / SUM(total_gross_sales) as profit_margin,
                COUNT(DISTINCT sku) as product_count
            FROM vw_daily_kpi_summary
            GROUP BY platform_name
            ORDER BY revenue DESC
            LIMIT 5
            """

            results = db.execute(text(query)).fetchall()

            if not results:
                return "No platform data available.", [], []

            # Build answer from top platform
            top_platform = results[0]
            answer = f"Based on recent data, **{top_platform[0]}** is your top platform by revenue with {float(top_platform[1]):,.0f} in sales. "

            # Find most profitable
            profitable = sorted(results, key=lambda x: x[3] or 0, reverse=True)[0]
            answer += f"**{profitable[0]}** has the highest profit margin. "

            # Provide recommendations
            recommendations = [
                f"Focus marketing investments on {top_platform[0]} - it generates the most revenue",
                f"Improve product selection on {profitable[0]} - it has the best profitability",
            ]

            data_sources = ["vw_daily_kpi_summary", "Platform Performance Data"]

            return answer, data_sources, recommendations

        except Exception as e:
            return f"Error analyzing platform data: {str(e)}", ["error_log"], []

    @staticmethod
    def _answer_product_question(db: Session, question: str) -> tuple[str, List[str], List[str]]:
        """Answer questions about product performance."""
        try:
            # Get top profitable products
            query = """
            SELECT
                product_name,
                SUM(total_contribution) as profit,
                SUM(total_gross_sales) as revenue,
                COUNT(distinct platform_name) as platforms
            FROM vw_daily_kpi_summary
            WHERE total_contribution > 0
            GROUP BY product_name
            ORDER BY profit DESC
            LIMIT 5
            """

            results = db.execute(text(query)).fetchall()

            if not results:
                return "No product data available.", [], []

            # Get unprofitable products
            loss_query = """
            SELECT product_name, SUM(total_contribution) as loss
            FROM vw_daily_kpi_summary
            WHERE total_contribution < 0
            GROUP BY product_name
            ORDER BY loss ASC
            LIMIT 3
            """

            loss_results = db.execute(text(loss_query)).fetchall()

            answer = f"Your best performing product is **{results[0][0]}** with ₹{float(results[0][1]):,.0f} in profit. "

            if loss_results:
                answer += f"However, **{loss_results[0][0]}** is losing ₹{abs(float(loss_results[0][1])):,.0f}. This needs immediate attention."

            recommendations = [
                f"Scale {results[0][0]} - it's your profit leader",
                "Review cost structure or remove unprofitable products",
                "Cross-sell top performers with struggling products"
            ]

            data_sources = ["vw_daily_kpi_summary", "Product Performance Data"]

            return answer, data_sources, recommendations

        except Exception as e:
            return f"Error analyzing product data: {str(e)}", ["error_log"], []

    @staticmethod
    def _answer_profitability_question(db: Session, question: str) -> tuple[str, List[str], List[str]]:
        """Answer profitability and cost questions."""
        try:
            query = """
            SELECT
                AVG(overall_profit_margin_pct) as avg_margin,
                MAX(overall_profit_margin_pct) as max_margin,
                MIN(overall_profit_margin_pct) as min_margin
            FROM vw_daily_kpi_summary
            """

            result = db.execute(text(query)).fetchone()

            if not result or result[0] is None:
                return "No profitability data available.", [], []

            avg_margin = float(result[0]) if result[0] else 0
            answer = f"Your average profit margin is **{avg_margin:.1f}%**. "

            if avg_margin > 20:
                answer += "This is excellent - you're operating efficiently!"
            elif avg_margin > 10:
                answer += "This is healthy. Look for opportunities to optimize costs."
            else:
                answer += "This is concerning. Review your cost structure urgently."

            recommendations = [
                "Analyze platform fees - negotiate better rates",
                "Review product costs - consider sourcing alternatives",
                "Optimize shipping costs through better logistics",
                "Reduce ad spend on low-performing campaigns"
            ]

            data_sources = ["vw_daily_kpi_summary", "Cost Analysis Data"]

            return answer, data_sources, recommendations

        except Exception as e:
            return f"Error analyzing profitability: {str(e)}", ["error_log"], []

    @staticmethod
    def _answer_advertising_question(db: Session, question: str) -> tuple[str, List[str], List[str]]:
        """Answer advertising and ROAS/ACOS questions."""
        try:
            query = """
            SELECT
                AVG(overall_roas) as avg_roas,
                SUM(total_ad_spend) as total_spend,
                SUM(total_ad_sales) as ad_sales
            FROM vw_daily_kpi_summary
            """

            result = db.execute(text(query)).fetchone()

            if not result:
                return "No advertising data available.", [], []

            roas = float(result[0]) if result[0] else 0
            ad_spend = float(result[1]) if result[1] else 0

            answer = f"Your average ROAS is **{roas:.1f}x**. "

            if roas > 5:
                answer += "Excellent! Your ads are generating strong returns."
            elif roas > 3:
                answer += "Good performance. Consider scaling your ad budget."
            elif roas > 1:
                answer += "Your ads are profitable but there's room for improvement."
            else:
                answer += "Your ROAS is below 1 - you're losing money on ads."

            answer += f" You've spent ₹{ad_spend:,.0f} on advertising."

            recommendations = [
                "Focus budget on high-performing campaigns",
                "Pause ads with ROAS below 2x",
                "A/B test ad creatives and copy",
                "Optimize landing pages to improve conversion"
            ]

            data_sources = ["vw_daily_kpi_summary", "Advertising Analytics"]

            return answer, data_sources, recommendations

        except Exception as e:
            return f"Error analyzing advertising: {str(e)}", ["error_log"], []

    @staticmethod
    def _answer_inventory_question(db: Session, question: str) -> tuple[str, List[str], List[str]]:
        """Answer inventory and warehouse questions."""
        try:
            query = """
            SELECT
                warehouse_city,
                COUNT(*) as sku_count,
                SUM(quantity_on_hand) as total_inventory
            FROM inventory
            GROUP BY warehouse_city
            ORDER BY total_inventory ASC
            LIMIT 5
            """

            results = db.execute(text(query)).fetchall()

            if not results:
                return "No inventory data available.", [], []

            lowest = results[0]
            answer = f"**{lowest[0]} warehouse** has the lowest inventory with {lowest[2]} units across {lowest[1]} SKUs. "
            answer += "This warehouse may need replenishment soon."

            recommendations = [
                f"Plan replenishment for {lowest[0]} warehouse",
                "Check 'days of cover' to forecast stockout dates",
                "Balance inventory across warehouses to meet regional demand"
            ]

            data_sources = ["inventory", "Warehouse Data"]

            return answer, data_sources, recommendations

        except Exception as e:
            return f"Error analyzing inventory: {str(e)}", ["error_log"], []

    @staticmethod
    def _answer_quality_question(db: Session, question: str) -> tuple[str, List[str], List[str]]:
        """Answer questions about product quality and customer satisfaction."""
        try:
            query = """
            SELECT
                AVG(total_units_returned) / SUM(total_units_sold) * 100 as return_rate,
                AVG(total_units_cancelled) / SUM(total_orders) * 100 as cancel_rate
            FROM vw_daily_kpi_summary
            """

            result = db.execute(text(query)).fetchone()

            if not result:
                return "No quality data available.", [], []

            return_rate = float(result[0]) if result[0] else 0
            cancel_rate = float(result[1]) if result[1] else 0

            answer = f"Your return rate is **{return_rate:.1f}%** and cancellation rate is **{cancel_rate:.1f}%**. "

            if return_rate > 15:
                answer += "Your return rate is high - investigate product quality or description accuracy. "

            if cancel_rate > 8:
                answer += "High cancellations suggest delivery time or pricing issues."

            recommendations = [
                "Review product descriptions and images",
                "Improve shipping/delivery times",
                "Enhance product packaging quality",
                "Offer better customer support for returns"
            ]

            data_sources = ["vw_daily_kpi_summary", "Quality Metrics"]

            return answer, data_sources, recommendations

        except Exception as e:
            return f"Error analyzing quality metrics: {str(e)}", ["error_log"], []

    @staticmethod
    def get_suggested_questions(db: Session) -> List[Dict[str, str]]:
        """Get list of suggested questions based on business data."""
        return AIAssistantService.SUGGESTED_QUESTIONS

    @staticmethod
    def explain_metric(db: Session, metric: str) -> Optional[Dict[str, str]]:
        """Get explanation for a business metric."""
        metric_key = metric.lower().replace(" ", "_").replace("%", "").strip()

        if metric_key in AIAssistantService.METRIC_DEFINITIONS:
            definition = AIAssistantService.METRIC_DEFINITIONS[metric_key]
            return {
                "metric": metric,
                "definition": definition["definition"],
                "formula": definition["formula"],
                "interpretation": definition["interpretation"]
            }

        return None

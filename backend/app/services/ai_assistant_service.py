"""Service for AI-powered business assistant with Groq integration."""

from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import Optional, Dict, List, Any
import json
import logging
from app.config import settings

logger = logging.getLogger(__name__)

# Try to import Groq client
try:
    from groq import Groq
    GROQ_AVAILABLE = bool(settings.GROQ_API_KEY)
except ImportError:
    GROQ_AVAILABLE = False


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

    # Conversation history for multi-turn support
    _conversation_history = {}

    @staticmethod
    def answer_question(
        db: Session,
        question: str,
        context: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Answer a business question using Groq AI and database queries.

        Process:
        1. Use Groq to understand intent and identify required tools
        2. Execute appropriate database queries
        3. Use Groq to synthesize insights
        4. Provide recommendations based on data
        """
        try:
            if GROQ_AVAILABLE:
                return AIAssistantService._answer_with_groq(db, question, context, session_id)
            else:
                logger.warning("Groq API not available, using fallback keyword matching")
                return AIAssistantService._answer_with_fallback(db, question, context)
        except Exception as e:
            logger.error(f"Error answering question: {str(e)}", exc_info=True)
            return {
                "question": question,
                "answer": f"I encountered an error while processing your question: {str(e)}",
                "confidence": 0.0,
                "data_sources": [],
                "recommendations": []
            }

    @staticmethod
    def _answer_with_groq(
        db: Session,
        question: str,
        context: Optional[Dict[str, Any]],
        session_id: Optional[str]
    ) -> Dict[str, Any]:
        """Answer question using Groq AI."""
        client = Groq(api_key=settings.GROQ_API_KEY)

        # Initialize or get conversation history
        if session_id and session_id in AIAssistantService._conversation_history:
            messages = AIAssistantService._conversation_history[session_id]
        else:
            messages = []

        # System prompt with database schema information
        system_prompt = """You are a business intelligence analyst for Sleepsia, an e-commerce analytics platform.

You have access to the following business data:
- Sales data from Amazon, Flipkart, Blinkit, Myntra, and JioMart
- Product performance and profitability metrics
- Advertising spend and ROI metrics (ROAS, ACOS)
- Inventory levels across 5 warehouses (Delhi NCR, Jaipur, Mumbai, Bengaluru, Hyderabad)
- Return and cancellation rates
- Daily KPI summaries

Your responsibilities:
1. Understand the user's business question
2. Identify what metrics and data are needed
3. Request specific tool calls to fetch data
4. Analyze the data and provide insights
5. Give actionable recommendations
6. Always cite data sources when making claims
7. Be honest about data limitations

Available tools:
- get_platform_metrics: Get performance data for specific platforms
- get_product_metrics: Get product sales and profitability
- get_profitability_analysis: Analyze profit margins and costs
- get_advertising_metrics: Get ROAS, ACOS, ad spend
- get_inventory_status: Check warehouse inventory levels
- get_quality_metrics: Return and cancellation rates
- get_kpi_summary: Overall business KPI summary

Respond in natural, conversational language. When you need data, request it clearly."""

        # Add user message
        messages.append({"role": "user", "content": question})

        # Get tool definitions
        tools = AIAssistantService._get_groq_tool_definitions()

        # Call Groq with tools for intent understanding
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            max_tokens=2000
        )

        # Process Groq's response
        final_answer = ""
        confidence = 0.8
        tool_results = []

        # Extract text and tool calls from response
        if response.choices[0].message.content:
            final_answer = response.choices[0].message.content

        # Handle tool calls if present
        if response.choices[0].message.tool_calls:
            for tool_call in response.choices[0].message.tool_calls:
                tool_name = tool_call.function.name
                tool_input = json.loads(tool_call.function.arguments)

                try:
                    result = AIAssistantService._execute_tool(db, tool_name, tool_input)
                    tool_results.append({
                        "type": "tool",
                        "name": tool_name,
                        "result": json.dumps(result)
                    })
                except Exception as e:
                    logger.error(f"Tool execution error for {tool_name}: {str(e)}")
                    tool_results.append({
                        "type": "tool",
                        "name": tool_name,
                        "result": json.dumps({"error": str(e)})
                    })

            # If tools were executed, get Groq's final analysis
            if tool_results:
                # Add assistant response and tool results
                messages.append({"role": "assistant", "content": response.choices[0].message.content})

                # Format tool results for Groq
                tool_result_text = "\n".join([
                    f"Tool: {tr['name']}\nResult: {tr['result']}"
                    for tr in tool_results
                ])
                messages.append({"role": "user", "content": f"Here are the tool results:\n{tool_result_text}\n\nPlease analyze this data and provide insights and recommendations."})

                # Get final analysis from Groq
                final_response = client.chat.completions.create(
                    model=settings.GROQ_MODEL,
                    messages=messages,
                    max_tokens=2000
                )

                final_answer = final_response.choices[0].message.content

        # Store conversation history
        if session_id:
            AIAssistantService._conversation_history[session_id] = messages[-10:]  # Keep last 10 messages

        # Extract recommendations from Groq's response
        recommendations = AIAssistantService._extract_recommendations(final_answer)

        return {
            "question": question,
            "answer": final_answer,
            "confidence": confidence,
            "data_sources": ["Sleepsia Analytics Database"],
            "recommendations": recommendations
        }

    @staticmethod
    def _answer_with_fallback(
        db: Session,
        question: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Fallback keyword-based answer when Claude is not available."""
        question_lower = question.lower()
        answer = ""
        data_sources = []
        recommendations = []
        confidence = 0.0

        if any(word in question_lower for word in ["platform", "channel", "amazon", "flipkart", "blinkit", "myntra", "jiomart"]):
            answer, sources, recs = AIAssistantService._answer_platform_question(db, question)
            confidence = 0.8
        elif any(word in question_lower for word in ["product", "sku", "item"]):
            answer, sources, recs = AIAssistantService._answer_product_question(db, question)
            confidence = 0.85
        elif any(word in question_lower for word in ["profit", "margin", "cost", "expense"]):
            answer, sources, recs = AIAssistantService._answer_profitability_question(db, question)
            confidence = 0.9
        elif any(word in question_lower for word in ["ad", "advertising", "roas", "acos", "spend", "impression"]):
            answer, sources, recs = AIAssistantService._answer_advertising_question(db, question)
            confidence = 0.85
        elif any(word in question_lower for word in ["inventory", "stock", "warehouse", "restock", "replenish"]):
            answer, sources, recs = AIAssistantService._answer_inventory_question(db, question)
            confidence = 0.8
        elif any(word in question_lower for word in ["return", "cancel", "quality", "issue"]):
            answer, sources, recs = AIAssistantService._answer_quality_question(db, question)
            confidence = 0.75
        else:
            answer = "I'm not sure how to answer that question. Try asking about platforms, products, profitability, advertising, inventory, or quality metrics."
            confidence = 0.2

        data_sources = sources if answer else []
        recommendations = recs if answer else []

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
                SUM(gross_sales) as revenue,
                SUM(contribution) as profit,
                SUM(contribution) / NULLIF(SUM(gross_sales), 0) as profit_margin,
                0 as product_count
            FROM vw_platform_performance
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
                SUM(contribution) as profit,
                SUM(gross_sales) as revenue,
                COUNT(DISTINCT platform_id) as platforms
            FROM vw_product_performance
            GROUP BY product_name
            ORDER BY profit DESC
            LIMIT 5
            """

            results = db.execute(text(query)).fetchall()

            if not results:
                return "No product data available.", [], []

            # Get unprofitable products
            loss_query = """
            SELECT product_name, SUM(contribution) as loss
            FROM vw_product_performance
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
                city,
                COUNT(*) as sku_count,
                SUM(closing_stock) as total_inventory
            FROM vw_inventory_health
            GROUP BY city
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

    @staticmethod
    def _get_groq_tool_definitions() -> List[Dict]:
        """Get Groq tool definitions for business queries (OpenAI format)."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_platform_metrics",
                    "description": "Get performance metrics for specific e-commerce platforms (Amazon, Flipkart, Blinkit, Myntra, JioMart)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "platform": {
                                "type": "string",
                                "description": "Platform name or 'all' for all platforms"
                            },
                            "metric": {
                                "type": "string",
                                "description": "Specific metric to retrieve (revenue, profit, profit_margin, orders, units)"
                            }
                        },
                        "required": ["platform"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_product_metrics",
                    "description": "Get product performance metrics including sales, profit, and profitability by product",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "metric": {
                                "type": "string",
                                "description": "Metric to retrieve (profit, revenue, margin, platforms)"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Number of products to return (default 10)"
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_profitability_analysis",
                    "description": "Get profit margin analysis and cost breakdown",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "analysis_type": {
                                "type": "string",
                                "description": "Type of analysis: margin_trend, cost_breakdown, or overall"
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_advertising_metrics",
                    "description": "Get advertising performance metrics including ROAS, ACOS, and ad spend",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "platform": {
                                "type": "string",
                                "description": "Platform name or 'all' for all platforms"
                            },
                            "metric": {
                                "type": "string",
                                "description": "Specific metric: roas, acos, spend, or all"
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_inventory_status",
                    "description": "Get inventory status across warehouses including stock levels and health",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "warehouse": {
                                "type": "string",
                                "description": "Warehouse city or 'all' for all warehouses"
                            },
                            "include_health": {
                                "type": "boolean",
                                "description": "Include warehouse health status"
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_quality_metrics",
                    "description": "Get product quality metrics including return rates and cancellation rates",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "metric": {
                                "type": "string",
                                "description": "Metric to retrieve: return_rate, cancel_rate, or both"
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_kpi_summary",
                    "description": "Get overall business KPI summary for the current period",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "include_trends": {
                                "type": "boolean",
                                "description": "Include trend information"
                            }
                        }
                    }
                }
            }
        ]

    @staticmethod
    def _execute_tool(db: Session, tool_name: str, tool_input: Dict) -> Dict:
        """Execute the requested tool and return results."""
        try:
            if tool_name == "get_platform_metrics":
                return AIAssistantService._get_platform_metrics(db, tool_input)
            elif tool_name == "get_product_metrics":
                return AIAssistantService._get_product_metrics(db, tool_input)
            elif tool_name == "get_profitability_analysis":
                return AIAssistantService._get_profitability_analysis(db, tool_input)
            elif tool_name == "get_advertising_metrics":
                return AIAssistantService._get_advertising_metrics(db, tool_input)
            elif tool_name == "get_inventory_status":
                return AIAssistantService._get_inventory_status(db, tool_input)
            elif tool_name == "get_quality_metrics":
                return AIAssistantService._get_quality_metrics(db, tool_input)
            elif tool_name == "get_kpi_summary":
                return AIAssistantService._get_kpi_summary(db, tool_input)
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            logger.error(f"Tool execution error: {str(e)}", exc_info=True)
            return {"error": str(e)}

    @staticmethod
    def _get_platform_metrics(db: Session, tool_input: Dict) -> Dict:
        """Get platform metrics."""
        platform = tool_input.get("platform", "all")
        try:
            query = """
            SELECT platform_name, SUM(gross_sales) as revenue, SUM(contribution) as profit,
                   SUM(contribution) / NULLIF(SUM(gross_sales), 0) * 100 as profit_margin
            FROM vw_platform_performance
            """
            if platform != "all":
                query += f" WHERE platform_name ILIKE '%{platform}%'"
            query += " GROUP BY platform_name ORDER BY revenue DESC"

            results = db.execute(text(query)).fetchall()
            return {
                "platforms": [
                    {"name": r[0], "revenue": float(r[1] or 0), "profit": float(r[2] or 0), "profit_margin": float(r[3] or 0)}
                    for r in results
                ]
            }
        except Exception as e:
            logger.error(f"Platform metrics error: {str(e)}")
            return {"error": str(e)}

    @staticmethod
    def _get_product_metrics(db: Session, tool_input: Dict) -> Dict:
        """Get product performance metrics."""
        limit = tool_input.get("limit", 10)
        try:
            query = f"""
            SELECT product_name, SUM(contribution) as profit, SUM(gross_sales) as revenue
            FROM vw_product_performance
            GROUP BY product_name
            ORDER BY profit DESC
            LIMIT {limit}
            """
            results = db.execute(text(query)).fetchall()
            return {
                "products": [
                    {"name": r[0], "profit": float(r[1] or 0), "revenue": float(r[2] or 0)}
                    for r in results
                ]
            }
        except Exception as e:
            logger.error(f"Product metrics error: {str(e)}")
            return {"error": str(e)}

    @staticmethod
    def _get_profitability_analysis(db: Session, tool_input: Dict) -> Dict:
        """Get profitability analysis."""
        try:
            query = """
            SELECT AVG(overall_profit_margin_pct) as avg_margin,
                   MAX(overall_profit_margin_pct) as max_margin,
                   MIN(overall_profit_margin_pct) as min_margin,
                   SUM(total_revenue) as total_revenue,
                   SUM(total_profit) as total_profit
            FROM vw_daily_kpi_summary
            """
            result = db.execute(text(query)).fetchone()
            return {
                "average_margin_pct": float(result[0] or 0),
                "max_margin_pct": float(result[1] or 0),
                "min_margin_pct": float(result[2] or 0),
                "total_revenue": float(result[3] or 0),
                "total_profit": float(result[4] or 0)
            }
        except Exception as e:
            logger.error(f"Profitability analysis error: {str(e)}")
            return {"error": str(e)}

    @staticmethod
    def _get_advertising_metrics(db: Session, tool_input: Dict) -> Dict:
        """Get advertising performance metrics."""
        try:
            query = """
            SELECT AVG(overall_roas) as avg_roas,
                   SUM(total_ad_spend) as total_spend,
                   SUM(total_ad_sales) as ad_sales,
                   AVG(overall_acos_pct) as avg_acos
            FROM vw_daily_kpi_summary
            """
            result = db.execute(text(query)).fetchone()
            return {
                "average_roas": float(result[0] or 0),
                "total_ad_spend": float(result[1] or 0),
                "ad_attributed_sales": float(result[2] or 0),
                "average_acos_pct": float(result[3] or 0)
            }
        except Exception as e:
            logger.error(f"Advertising metrics error: {str(e)}")
            return {"error": str(e)}

    @staticmethod
    def _get_inventory_status(db: Session, tool_input: Dict) -> Dict:
        """Get inventory status."""
        try:
            query = """
            SELECT city, COUNT(*) as sku_count, SUM(closing_stock) as total_stock,
                   AVG(days_of_cover) as avg_days_cover
            FROM vw_inventory_health
            GROUP BY city
            ORDER BY total_stock ASC
            """
            results = db.execute(text(query)).fetchall()
            return {
                "warehouses": [
                    {"city": r[0], "sku_count": int(r[1]), "total_stock": float(r[2] or 0), "days_of_cover": float(r[3] or 0)}
                    for r in results
                ]
            }
        except Exception as e:
            logger.error(f"Inventory status error: {str(e)}")
            return {"error": str(e)}

    @staticmethod
    def _get_quality_metrics(db: Session, tool_input: Dict) -> Dict:
        """Get quality metrics."""
        try:
            query = """
            SELECT AVG(CASE WHEN total_units_sold > 0 THEN (total_units_returned / total_units_sold * 100) ELSE 0 END) as return_rate,
                   AVG(CASE WHEN total_orders > 0 THEN (total_units_cancelled / total_orders * 100) ELSE 0 END) as cancel_rate
            FROM vw_daily_kpi_summary
            """
            result = db.execute(text(query)).fetchone()
            return {
                "return_rate_pct": float(result[0] or 0),
                "cancellation_rate_pct": float(result[1] or 0)
            }
        except Exception as e:
            logger.error(f"Quality metrics error: {str(e)}")
            return {"error": str(e)}

    @staticmethod
    def _get_kpi_summary(db: Session, tool_input: Dict) -> Dict:
        """Get KPI summary."""
        try:
            query = """
            SELECT COUNT(*) as record_count,
                   SUM(total_revenue) as total_revenue,
                   SUM(total_profit) as total_profit,
                   SUM(total_orders) as total_orders,
                   SUM(total_units_sold) as total_units
            FROM vw_daily_kpi_summary
            """
            result = db.execute(text(query)).fetchone()
            return {
                "total_revenue": float(result[1] or 0),
                "total_profit": float(result[2] or 0),
                "total_orders": int(result[3] or 0),
                "total_units": int(result[4] or 0),
                "record_count": int(result[0] or 0)
            }
        except Exception as e:
            logger.error(f"KPI summary error: {str(e)}")
            return {"error": str(e)}

    @staticmethod
    def _extract_recommendations(text: str) -> List[str]:
        """Extract recommendations from Claude's response."""
        recommendations = []
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in ['recommend', 'suggest', 'should', 'consider', 'improve', 'focus', 'increase', 'decrease', 'optimize']):
                if len(line) > 10 and not line.startswith('#'):
                    # Clean up bullet points and numbering
                    line = line.lstrip('•-*123456789. ')
                    if line and line[0].isupper():
                        recommendations.append(line)
        return recommendations[:5]  # Return top 5 recommendations

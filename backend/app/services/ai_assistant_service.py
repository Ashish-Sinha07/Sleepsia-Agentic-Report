"""Hybrid SQL + RAG business assistant service.

Every question is classified by `QueryRouter` into SQL / RAG / HYBRID /
CLARIFICATION, then dispatched accordingly:

  SQL      -> a Groq tool-call picks one of the hardened, parameterized
              query templates in `sql_tools.py` (read-only, view-allowlisted,
              row/time-limited via `sql_guard.py`), then Groq explains the
              result in natural language.
  RAG      -> the question is embedded, the vector store is searched, and
              Groq answers strictly grounded in the retrieved chunks.
  HYBRID   -> both of the above run, and Groq combines the database fact
              with the document context, distinguishing the two explicitly.
  CLARIFICATION -> the assistant asks the user to narrow the question rather
              than guessing.

This replaces the previous implementation's `_answer_with_groq`/
`_answer_with_fallback` tool-calling path, two of whose tool functions
(`_get_platform_metrics`, `_get_product_metrics`) built SQL via f-string
interpolation of LLM-controlled input - a SQL-injection surface. Every SQL
template here uses bind parameters exclusively; see `sql_tools.py`.
"""

from typing import Optional, Dict, List, Any
import json
import logging

from sqlalchemy.orm import Session

from app.config import settings
from app.services import sql_tools
from app.services.query_router import ROUTE_CLARIFICATION, ROUTE_HYBRID, ROUTE_RAG, ROUTE_SQL, get_query_router
from app.rag.answer_generator import generate_hybrid_answer, generate_rag_answer
from app.rag.prompts import CLARIFICATION_MESSAGE_TEMPLATE, SQL_UNAVAILABLE_MESSAGE
from app.rag.retriever import get_retriever

logger = logging.getLogger(__name__)

try:
    from groq import Groq

    GROQ_AVAILABLE = bool(settings.GROQ_API_KEY)
except ImportError:
    GROQ_AVAILABLE = False


_CURRENCY_NOTE = (
    "All monetary figures in this business (revenue, sales, cost, spend, profit, contribution, refunds, etc.) "
    "are in Indian Rupees. Always format money with the ₹ symbol (e.g. ₹64,90,253.01) - never $, USD, or any "
    "other currency symbol."
)

_SQL_SYSTEM_PROMPT_TEMPLATE = """You are a business intelligence analyst for Sleepsia, an e-commerce analytics platform.

You have READ-ONLY access to business data via a fixed set of tools. You cannot create, update, or delete any
data, and you must never claim to have done so - if the user asks you to modify, delete, or export raw data,
politely refuse and explain you only have read access to aggregated reporting metrics.

{filter_context_note}

Pick exactly one tool that best answers the question. Do not answer from memory - always use a tool."""

_SQL_EXPLAIN_SYSTEM_PROMPT = (
    "You explain business database results in clear, concise, conversational language for a business user. "
    "Only use the numbers you were given in the database result - never invent or recompute a number. "
    "Bold key figures with **markdown**. "
    f"{_CURRENCY_NOTE} "
    "You have READ-ONLY access to this data. If the user's question asked to create, update, delete, export, "
    "or otherwise modify data, do not provide SQL, steps, or instructions for doing so, even as a suggestion or "
    "tutorial - state plainly that you only have read access to aggregated reporting metrics and cannot perform "
    "or explain that action, then optionally offer the read-only figures below if they are relevant context."
)


def _filter_context_note(context: Optional[Dict[str, Any]]) -> str:
    if not context:
        return "No dashboard filters are currently active."
    parts = []
    if context.get("startDate"):
        parts.append(f"date from {str(context['startDate'])[:10]}")
    if context.get("endDate"):
        parts.append(f"to {str(context['endDate'])[:10]}")
    if context.get("platform") and context["platform"] != "all":
        parts.append(f"platform = {context['platform']}")
    if not parts:
        return "No dashboard filters are currently active."
    return (
        "The user currently has these dashboard filters active: "
        + ", ".join(parts)
        + ". Use them as defaults for date range / platform unless the question clearly asks about something else."
    )


class AIAssistantService:
    """Handle natural language business questions via the hybrid SQL+RAG router."""

    METRIC_DEFINITIONS = {
        "revenue": {
            "definition": "Total sales value from all channels",
            "formula": "Gross Sales - Discounts",
            "interpretation": "Higher revenue indicates better sales performance. Track daily to identify trends.",
        },
        "profit": {
            "definition": "Revenue minus all costs and expenses",
            "formula": "Net Revenue - (Product Cost + Platform Fees + Ad Spend + Other Costs)",
            "interpretation": "Profit margin shows business efficiency. Healthy margin is 15-30% depending on category.",
        },
        "profit_margin": {
            "definition": "Profit as a percentage of revenue",
            "formula": "(Profit / Revenue) * 100",
            "interpretation": "Higher margin is better. 20%+ is excellent. Below 10% needs attention.",
        },
        "roas": {
            "definition": "Return on Ad Spend - revenue generated per rupee spent on ads",
            "formula": "Ad-Attributed Sales / Ad Spend",
            "interpretation": "ROAS > 3 is good. ROAS > 5 is excellent. Below 2 means unprofitable advertising.",
        },
        "acos": {
            "definition": "Advertising Cost of Sale - percentage of ad sales spent on advertising",
            "formula": "(Ad Spend / Ad-Attributed Sales) * 100",
            "interpretation": "ACOS < 30% is good. ACOS > 50% means you're losing money on ads.",
        },
        "return_rate": {
            "definition": "Percentage of sold units that are returned",
            "formula": "(Units Returned / Units Sold) * 100",
            "interpretation": "Industry average is 5-15%. Above 20% indicates product quality issues.",
        },
        "cancellation_rate": {
            "definition": "Percentage of orders cancelled by customers",
            "formula": "(Orders Cancelled / Total Orders) * 100",
            "interpretation": "Below 5% is healthy. Above 10% suggests delivery or product issues.",
        },
    }

    SUGGESTED_QUESTIONS = [
        {
            "question": "Which platform is most profitable?",
            "category": "platform_analysis",
            "description": "Compare profit margins across Amazon, Flipkart, Blinkit, Myntra, and JioMart",
        },
        {
            "question": "Which products are losing money?",
            "category": "product_analysis",
            "description": "Identify unprofitable SKUs and their cost structure",
        },
        {
            "question": "Which platform has the best ROAS?",
            "category": "advertising",
            "description": "Compare ad efficiency across all marketing channels",
        },
        {
            "question": "Which warehouse needs replenishment?",
            "category": "inventory",
            "description": "Find low-stock warehouses that need urgent restocking",
        },
        {
            "question": "What is our return policy?",
            "category": "knowledge_base",
            "description": "Ask about business policies and guidelines",
        },
        {
            "question": "Compare Amazon and Flipkart.",
            "category": "platform_comparison",
            "description": "Side-by-side performance comparison of two platforms",
        },
        {
            "question": "What are the business rules for replenishment?",
            "category": "knowledge_base",
            "description": "Ask about inventory/replenishment guidelines",
        },
        {
            "question": "Our revenue dropped last month - what do the guidelines say about that?",
            "category": "hybrid",
            "description": "Combine live metrics with business guidance",
        },
    ]

    # ------------------------------------------------------------------
    # Public entry points
    # ------------------------------------------------------------------

    @staticmethod
    def answer_question(
        db: Session,
        question: str,
        context: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Route and answer a business question. Never raises - always returns a response dict."""
        try:
            if not question or not question.strip():
                return AIAssistantService._response(
                    question, "Please enter a question.", 0.0, [], [], ROUTE_CLARIFICATION, []
                )

            decision = get_query_router().classify(question)

            if decision.route == ROUTE_CLARIFICATION or decision.needs_clarification:
                answer = CLARIFICATION_MESSAGE_TEMPLATE.format(aspect="what you'd like to know")
                if decision.reason:
                    answer = f"{answer} ({decision.reason})"
                response = AIAssistantService._response(
                    question, answer, decision.confidence, [], [], ROUTE_CLARIFICATION, []
                )
            elif decision.route == ROUTE_SQL:
                response = AIAssistantService._answer_sql(db, question, context)
            elif decision.route == ROUTE_RAG:
                response = AIAssistantService._answer_rag(question)
            else:
                response = AIAssistantService._answer_hybrid(db, question, context)

            response["route_confidence"] = decision.confidence
            response["route_reason"] = decision.reason
            return response
        except Exception as e:
            logger.error(f"Error answering question: {str(e)}", exc_info=True)
            return AIAssistantService._response(
                question,
                f"I encountered an error while processing your question: {str(e)}",
                0.0,
                [],
                [],
                None,
                [],
            )

    @staticmethod
    def get_suggested_questions(db: Session) -> List[Dict[str, str]]:
        return AIAssistantService.SUGGESTED_QUESTIONS

    @staticmethod
    def explain_metric(db: Session, metric: str) -> Optional[Dict[str, str]]:
        metric_key = metric.lower().replace(" ", "_").replace("%", "").strip()
        if metric_key in AIAssistantService.METRIC_DEFINITIONS:
            definition = AIAssistantService.METRIC_DEFINITIONS[metric_key]
            return {
                "metric": metric,
                "definition": definition["definition"],
                "formula": definition["formula"],
                "interpretation": definition["interpretation"],
            }
        return None

    # ------------------------------------------------------------------
    # Route handlers
    # ------------------------------------------------------------------

    @staticmethod
    def _answer_sql(db: Session, question: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        tool_name, result = AIAssistantService._run_sql_tool_call(db, question, context)

        if not result or "error" in result:
            return AIAssistantService._response(
                question, SQL_UNAVAILABLE_MESSAGE, 0.0, [], [], ROUTE_SQL, []
            )

        facts_text = json.dumps(result, indent=2, default=str)
        answer = None
        if GROQ_AVAILABLE:
            try:
                client = Groq(api_key=settings.GROQ_API_KEY)
                completion = client.chat.completions.create(
                    model=settings.GROQ_MODEL,
                    messages=[
                        {"role": "system", "content": _SQL_EXPLAIN_SYSTEM_PROMPT},
                        {
                            "role": "user",
                            "content": f"Question: {question}\n\nDatabase result ({tool_name}):\n{facts_text}",
                        },
                    ],
                    max_tokens=500,
                )
                answer = completion.choices[0].message.content
            except Exception:
                logger.exception("SQL answer synthesis failed")

        if not answer:
            answer = f"Here is what the data shows:\n\n{facts_text}"

        recommendations = AIAssistantService._extract_recommendations(answer)
        sources = [{"type": "database", "source": tool_name}]
        return AIAssistantService._response(
            question, answer, 0.9, [f"MySQL: {tool_name}"], recommendations, ROUTE_SQL, sources
        )

    @staticmethod
    def _answer_rag(question: str) -> Dict[str, Any]:
        retriever = get_retriever()
        chunks = retriever.retrieve(question)
        context_text = retriever.build_context(chunks)
        result = generate_rag_answer(question, chunks, context_text)
        data_sources = [s["source"] for s in result["sources"]]
        return AIAssistantService._response(
            question, result["answer"], result["confidence"], data_sources, [], ROUTE_RAG, result["sources"]
        )

    @staticmethod
    def _answer_hybrid(db: Session, question: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        tool_name, db_result = AIAssistantService._run_sql_tool_call(db, question, context)
        db_facts = db_result if db_result and "error" not in db_result else None

        retriever = get_retriever()
        chunks = retriever.retrieve(question)
        context_text = retriever.build_context(chunks)

        result = generate_hybrid_answer(question, db_facts, tool_name, chunks, context_text)
        data_sources = [s["source"] for s in result["sources"]]
        return AIAssistantService._response(
            question, result["answer"], result["confidence"], data_sources, [], ROUTE_HYBRID, result["sources"]
        )

    # ------------------------------------------------------------------
    # SQL tool selection helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _run_sql_tool_call(
        db: Session, question: str, context: Optional[Dict[str, Any]]
    ) -> "tuple[Optional[str], Dict[str, Any]]":
        """Pick and execute exactly one SQL tool; returns (tool_name, result)."""
        if GROQ_AVAILABLE:
            try:
                client = Groq(api_key=settings.GROQ_API_KEY)
                tools = sql_tools.get_groq_tool_definitions()
                system_prompt = _SQL_SYSTEM_PROMPT_TEMPLATE.format(
                    filter_context_note=_filter_context_note(context)
                )
                response = client.chat.completions.create(
                    model=settings.GROQ_MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": question},
                    ],
                    tools=tools,
                    tool_choice="auto",
                    max_tokens=500,
                )
                message = response.choices[0].message
                if message.tool_calls:
                    call = message.tool_calls[0]
                    tool_name = call.function.name
                    try:
                        tool_input = json.loads(call.function.arguments or "{}")
                    except json.JSONDecodeError:
                        tool_input = {}
                    tool_input = AIAssistantService._apply_filter_context(tool_input, context)
                    result = sql_tools.execute_tool(db, tool_name, tool_input)
                    return tool_name, result
            except Exception:
                logger.exception("Groq SQL tool-calling failed, falling back to deterministic tool pick")

        tool_name, params = AIAssistantService._pick_tool_deterministic(question)
        params = AIAssistantService._apply_filter_context(params, context)
        result = sql_tools.execute_tool(db, tool_name, params)
        return tool_name, result

    @staticmethod
    def _pick_tool_deterministic(question: str) -> "tuple[str, Dict[str, Any]]":
        """Keyword-based tool choice used when Groq is unavailable (fail-gracefully path)."""
        q = question.lower()
        if any(w in q for w in ["inventory", "stock", "warehouse", "replenish", "reorder"]):
            return "get_inventory_status", {}
        if any(w in q for w in ["roas", "acos", "advertising", "ad spend"]):
            return "get_advertising_metrics", {}
        if any(w in q for w in ["return", "cancel"]):
            return "get_quality_metrics", {}
        if any(w in q for w in ["product", "sku"]):
            return "get_product_metrics", {}
        if any(w in q for w in ["platform", "amazon", "flipkart", "blinkit", "myntra", "jiomart"]):
            return "get_platform_metrics", {}
        return "get_kpi_summary", {}

    @staticmethod
    def _apply_filter_context(params: Dict[str, Any], context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Backfill date range / platform from the dashboard's active filters,
        without overriding anything the LLM/user already specified explicitly."""
        if not context:
            return params
        merged = dict(params)
        if context.get("startDate") and not merged.get("date_from"):
            merged["date_from"] = str(context["startDate"])[:10]
        if context.get("endDate") and not merged.get("date_to"):
            merged["date_to"] = str(context["endDate"])[:10]
        if context.get("platform") and context["platform"] != "all" and not merged.get("platform"):
            merged["platform"] = context["platform"]
        if context.get("sku") and context["sku"] != "all" and not merged.get("sku"):
            merged["sku"] = context["sku"]
        if context.get("warehouse") and context["warehouse"] != "all" and not merged.get("warehouse"):
            merged["warehouse"] = context["warehouse"]
        return merged

    @staticmethod
    def _extract_recommendations(text: str) -> List[str]:
        recommendations = []
        for line in text.split("\n"):
            line = line.strip()
            if any(
                keyword in line.lower()
                for keyword in ["recommend", "suggest", "should", "consider", "improve", "focus", "increase", "decrease", "optimize"]
            ):
                if len(line) > 10 and not line.startswith("#"):
                    line = line.lstrip("•-*123456789. ")
                    if line and line[0].isupper():
                        recommendations.append(line)
        return recommendations[:5]

    @staticmethod
    def _response(
        question: str,
        answer: str,
        confidence: float,
        data_sources: List[str],
        recommendations: List[str],
        route: Optional[str],
        sources: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        return {
            "question": question,
            "answer": answer,
            "confidence": confidence,
            "data_sources": data_sources,
            "recommendations": recommendations,
            "route": route,
            "sources": sources,
        }

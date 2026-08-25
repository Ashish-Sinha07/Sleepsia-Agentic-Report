"""Query router: classifies a user question into SQL / RAG / HYBRID / CLARIFICATION.

Uses deterministic phrase rules first (fast, free, and covers the large
majority of realistic business questions) and only falls back to an LLM
classification call for genuinely ambiguous questions - avoiding a Groq round
trip on every single message (see spec section 23, Performance).

The deterministic pass distinguishes *specific metric terms* (revenue,
ROAS, profit...) which are strong SQL signals on their own, from *bare
domain nouns* (inventory, platform, warehouse...) which are only routed to
SQL when paired with a superlative/quantifier cue ("highest", "how many").
This avoids the naive bug where "What are the guidelines for handling
inventory?" (a RAG question) would get misrouted to HYBRID just because
"inventory" and "guidelines" both appear in it.
"""

from dataclasses import asdict, dataclass
import json
import logging
import re
from typing import Optional

from app.config import settings

logger = logging.getLogger(__name__)

try:
    from groq import Groq

    _GROQ_IMPORT_OK = True
except ImportError:  # pragma: no cover - groq is a declared dependency
    _GROQ_IMPORT_OK = False


ROUTE_SQL = "SQL"
ROUTE_RAG = "RAG"
ROUTE_HYBRID = "HYBRID"
ROUTE_CLARIFICATION = "CLARIFICATION"
VALID_ROUTES = {ROUTE_SQL, ROUTE_RAG, ROUTE_HYBRID, ROUTE_CLARIFICATION}


@dataclass
class RouteDecision:
    route: str
    confidence: float
    reason: str
    needs_clarification: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


# Unambiguous business-metric terms - a strong SQL signal on their own.
_STRONG_SQL_METRIC_TERMS = [
    "revenue", "sales", "sale", "profit", "margin", "roas", "acos",
    "units sold", "units", "orders", "order", "ad spend", "advertising spend",
    "spend", "expense", "expenses", "contribution", "return rate",
    "cancellation rate", "units returned", "units cancelled", "kpi",
]

# Bare domain nouns - not enough signal alone, only count toward SQL when
# paired with a superlative/quantifier cue below.
_DOMAIN_NOUNS = [
    "platform", "product", "sku", "warehouse", "inventory", "stock",
    "region", "amazon", "flipkart", "blinkit", "myntra", "jiomart",
    "replenish", "reorder",
]
_SUPERLATIVE_OR_QUANTIFIER_TERMS = [
    "highest", "lowest", "top", "best", "worst", "most", "least",
    "biggest", "smallest", "how many", "how much", "total", "what was our",
    "what is our", "what were our",
]

# Phrases that point at the document/knowledge-base RAG path.
_RAG_PHRASES = [
    "policy", "policies", "guideline", "guidelines", "sop",
    "business rule", "business rules", "rule for", "rules for",
    "define", "definition", "what does", "means", "explain", "strategy",
    "recommend", "recommendation", "document", "documents", "excel report",
    "uploaded", "summarize", "summarise", "summary of", "planning document",
    "according to",
]

_CLASSIFIER_SYSTEM_PROMPT = """You are a query router for a business analytics chatbot. Classify the user's
question into exactly one route:

- SQL: the question asks for a numeric/structured business metric (revenue, sales, profit, ROAS, ACOS, units,
  inventory, warehouse stock, returns, cancellations, platform/product performance) that lives in a MySQL
  database.
- RAG: the question asks about a business definition, policy, guideline, SOP, strategy, or the content of an
  uploaded/business document - not a live numeric metric.
- HYBRID: the question genuinely needs BOTH a database metric AND document/policy context to answer (e.g. "our
  revenue dropped, what do the guidelines say about that").
- CLARIFICATION: the question is too vague/ambiguous to route confidently, or is unrelated to Sleepsia's
  business data/knowledge entirely.

Respond with ONLY a JSON object, no other text:
{"route": "SQL"|"RAG"|"HYBRID"|"CLARIFICATION", "confidence": <0..1 float>, "reason": "<one short sentence>",
"needs_clarification": <true|false>}"""


class QueryRouter:
    """Classifies a question into SQL / RAG / HYBRID / CLARIFICATION."""

    def __init__(self, groq_api_key: Optional[str] = None, groq_model: Optional[str] = None):
        # `None` means "use the configured default"; an explicit "" must
        # actually disable Groq rather than silently falling back to it.
        self._groq_api_key = settings.GROQ_API_KEY if groq_api_key is None else groq_api_key
        self._groq_model = settings.GROQ_MODEL if groq_model is None else groq_model

    def classify(self, question: str) -> RouteDecision:
        if not question or not question.strip():
            return RouteDecision(ROUTE_CLARIFICATION, 1.0, "Empty question", True)

        decision = self._classify_deterministic(question)
        if decision is not None:
            return decision

        if _GROQ_IMPORT_OK and self._groq_api_key:
            llm_decision = self._classify_with_llm(question)
            if llm_decision is not None:
                return llm_decision

        # No deterministic signal and no usable LLM classifier available:
        # ask for clarification rather than guessing a route.
        return RouteDecision(
            ROUTE_CLARIFICATION,
            0.3,
            "Question did not clearly match a business-metric or business-knowledge pattern",
            True,
        )

    def _classify_deterministic(self, question: str) -> Optional[RouteDecision]:
        q = question.lower()

        sql_hit = any(term in q for term in _STRONG_SQL_METRIC_TERMS)
        if not sql_hit:
            has_cue = any(t in q for t in _SUPERLATIVE_OR_QUANTIFIER_TERMS)
            has_noun = any(t in q for t in _DOMAIN_NOUNS)
            sql_hit = has_cue and has_noun

        rag_hit = any(phrase in q for phrase in _RAG_PHRASES)

        if sql_hit and rag_hit:
            return RouteDecision(
                ROUTE_HYBRID,
                0.85,
                "Question references both a business metric and business guidance/policy content",
                False,
            )
        if sql_hit:
            return RouteDecision(
                ROUTE_SQL, 0.9, "Question asks for a structured business metric available in MySQL", False
            )
        if rag_hit:
            return RouteDecision(
                ROUTE_RAG, 0.85, "Question asks about a definition, policy, or document content", False
            )
        return None

    def _classify_with_llm(self, question: str) -> Optional[RouteDecision]:
        try:
            client = Groq(api_key=self._groq_api_key)
            response = client.chat.completions.create(
                model=self._groq_model,
                messages=[
                    {"role": "system", "content": _CLASSIFIER_SYSTEM_PROMPT},
                    {"role": "user", "content": question},
                ],
                max_tokens=200,
                temperature=0,
            )
            content = response.choices[0].message.content or ""
            data = _extract_json(content)
            if not data:
                return None
            route = str(data.get("route", "")).upper()
            if route not in VALID_ROUTES:
                return None
            return RouteDecision(
                route=route,
                confidence=float(data.get("confidence", 0.6) or 0.6),
                reason=str(data.get("reason", "LLM classification"))[:300],
                needs_clarification=bool(data.get("needs_clarification", route == ROUTE_CLARIFICATION)),
            )
        except Exception:
            logger.exception("LLM query routing failed")
            return None


def _extract_json(text: str) -> Optional[dict]:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


_default_router: Optional[QueryRouter] = None


def get_query_router() -> QueryRouter:
    global _default_router
    if _default_router is None:
        _default_router = QueryRouter()
    return _default_router

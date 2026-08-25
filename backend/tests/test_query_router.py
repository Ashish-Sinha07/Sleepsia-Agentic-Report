"""Router tests (spec section 19.A): deterministic classification must route
every example question from the business requirement to the right lane
without needing an LLM call - the QueryRouter is constructed with an empty
API key so these tests are hermetic (no network, no Groq dependency).
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from app.services.query_router import QueryRouter, ROUTE_SQL, ROUTE_RAG, ROUTE_HYBRID, ROUTE_CLARIFICATION


@pytest.fixture
def router():
    # No API key -> deterministic-only, no network call, no flaky LLM behavior.
    return QueryRouter(groq_api_key="")


@pytest.mark.parametrize(
    "question",
    [
        "What was our revenue last month?",
        "What was our total revenue?",
        "Which platform generated the highest revenue?",
        "What is our ROAS?",
        "How many units did we sell?",
        "Which warehouse has the lowest inventory?",
        "What were our advertising expenses?",
        "Show me sales for Amazon.",
        "What was our profit in July?",
        "Which product had the highest sales?",
        "Which platform is most profitable?",
    ],
)
def test_sql_questions_route_to_sql(router, question):
    decision = router.classify(question)
    assert decision.route == ROUTE_SQL
    assert decision.confidence > 0.5
    assert not decision.needs_clarification


@pytest.mark.parametrize(
    "question",
    [
        "What does this business metric mean?",
        "What is our return policy?",
        "What are the guidelines for handling inventory?",
        "Explain our advertising strategy.",
        "What does this product category mean?",
        "What are the business rules for replenishment?",
        "What does the uploaded Excel report say about this?",
        "Summarize the information in the uploaded business document.",
        "What recommendations are mentioned in the planning document?",
    ],
)
def test_rag_questions_route_to_rag(router, question):
    decision = router.classify(question)
    assert decision.route == ROUTE_RAG


@pytest.mark.parametrize(
    "question",
    [
        "Our revenue dropped last month. According to the business guidelines, what could be the likely reasons?",
        "Which warehouse has the lowest stock, and what does our inventory policy recommend?",
        "Amazon has the highest revenue. What does the business strategy document recommend for Amazon?",
        "What is our current ROAS and how does it compare with the target mentioned in the business document?",
    ],
)
def test_hybrid_questions_route_to_hybrid(router, question):
    decision = router.classify(question)
    assert decision.route == ROUTE_HYBRID


def test_empty_question_needs_clarification(router):
    decision = router.classify("")
    assert decision.route == ROUTE_CLARIFICATION
    assert decision.needs_clarification


def test_unrelated_question_without_llm_falls_back_to_clarification(router):
    decision = router.classify("What is the meaning of life?")
    assert decision.route == ROUTE_CLARIFICATION
    assert decision.needs_clarification


def test_rag_topic_noun_alone_is_not_misrouted_to_hybrid(router):
    """Regression: a bare domain noun ("inventory") inside a RAG-phrased
    question ("guidelines for...") must not get bumped to HYBRID just
    because the noun also appears in the SQL keyword vocabulary."""
    decision = router.classify("What are the guidelines for handling inventory?")
    assert decision.route == ROUTE_RAG

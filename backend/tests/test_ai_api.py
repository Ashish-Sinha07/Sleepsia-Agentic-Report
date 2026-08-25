"""API contract tests for POST /api/ai/ask (spec section 19.F)."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_ask_valid_sql_question_returns_expected_shape(client):
    response = client.post("/api/ai/ask", json={"question": "What was our total revenue?"})
    assert response.status_code == 200
    data = response.json()
    for field in ("question", "answer", "confidence", "data_sources", "recommendations", "route", "sources"):
        assert field in data
    assert data["route"] in ("SQL", "RAG", "HYBRID", "CLARIFICATION")


def test_ask_empty_question_returns_400(client):
    response = client.post("/api/ai/ask", json={"question": ""})
    assert response.status_code == 400


def test_ask_whitespace_only_question_returns_400(client):
    response = client.post("/api/ai/ask", json={"question": "   "})
    assert response.status_code == 400


def test_ask_missing_question_field_returns_422(client):
    response = client.post("/api/ai/ask", json={})
    assert response.status_code == 422


def test_ask_does_not_expose_generated_sql_text(client):
    """The API response must never leak raw SQL to the caller - only a tool
    name/source label, per spec section 14 (API contract)."""
    response = client.post("/api/ai/ask", json={"question": "What was our total revenue?"})
    body = response.text.lower()
    assert "select " not in body
    assert " from vw_" not in body


def test_get_suggestions_returns_a_list(client):
    response = client.get("/api/ai/suggestions")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0


def test_explain_known_metric(client):
    response = client.post("/api/ai/explain-metric", json={"metric": "roas"})
    assert response.status_code == 200
    data = response.json()
    assert data["metric"] == "roas"
    assert "formula" in data


def test_explain_unknown_metric_returns_404(client):
    response = client.post("/api/ai/explain-metric", json={"metric": "not_a_real_metric_xyz"})
    assert response.status_code == 404

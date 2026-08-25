"""Grounded answer generation for the RAG and HYBRID routes.

Wraps retrieved chunks / SQL facts in the prompts defined in `prompts.py` and
calls Groq to synthesize a natural-language answer. Falls back to surfacing
the raw retrieved/computed data with an explicit disclaimer if Groq is
unavailable, rather than fabricating an answer without an LLM (spec section
22, Failure Handling: never fabricate as a fallback).
"""

import json
import logging
from typing import Any, Dict, List, Optional

from app.config import settings
from app.rag.prompts import (
    HYBRID_SYSTEM_PROMPT,
    INSUFFICIENT_CONTEXT_MESSAGE,
    RAG_SYSTEM_PROMPT,
    RAG_UNAVAILABLE_MESSAGE,
    build_hybrid_user_prompt,
    build_rag_user_prompt,
)
from app.rag.retriever import RetrievedChunk

logger = logging.getLogger(__name__)

try:
    from groq import Groq

    _GROQ_IMPORT_OK = True
except ImportError:  # pragma: no cover
    _GROQ_IMPORT_OK = False


def _groq_client():
    if not _GROQ_IMPORT_OK or not settings.GROQ_API_KEY:
        return None
    return Groq(api_key=settings.GROQ_API_KEY)


def _sources_from_chunks(chunks: List[RetrievedChunk]) -> List[Dict[str, Any]]:
    seen = set()
    sources = []
    for c in chunks:
        key = (c.source_file, c.sheet_name)
        if key in seen:
            continue
        seen.add(key)
        sources.append({"type": "document", "source": c.source_file, "sheet": c.sheet_name or None})
    return sources


def generate_rag_answer(question: str, chunks: List[RetrievedChunk], context: str) -> Dict[str, Any]:
    """Answer a knowledge-base question grounded strictly in `chunks`."""
    if not chunks:
        return {"answer": INSUFFICIENT_CONTEXT_MESSAGE, "confidence": 0.2, "sources": []}

    client = _groq_client()
    if client is None:
        preview = "\n\n".join(c.text for c in chunks[:3])
        return {
            "answer": f"{RAG_UNAVAILABLE_MESSAGE} Here is the most relevant material found in the knowledge base:\n\n{preview}",
            "confidence": 0.4,
            "sources": _sources_from_chunks(chunks),
        }

    try:
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": RAG_SYSTEM_PROMPT},
                {"role": "user", "content": build_rag_user_prompt(question, context)},
            ],
            max_tokens=800,
            temperature=0.2,
        )
        answer = response.choices[0].message.content or INSUFFICIENT_CONTEXT_MESSAGE
        avg_score = sum(c.score for c in chunks) / len(chunks)
        confidence = round(min(0.95, 0.5 + avg_score * 0.5), 2)
        return {"answer": answer, "confidence": confidence, "sources": _sources_from_chunks(chunks)}
    except Exception:
        logger.exception("RAG answer generation failed")
        return {"answer": RAG_UNAVAILABLE_MESSAGE, "confidence": 0.0, "sources": _sources_from_chunks(chunks)}


def generate_hybrid_answer(
    question: str,
    database_facts: Optional[Dict[str, Any]],
    db_tool_name: Optional[str],
    chunks: List[RetrievedChunk],
    context: str,
) -> Dict[str, Any]:
    """Answer a question that needs both a database fact and document guidance."""
    sources: List[Dict[str, Any]] = []
    if database_facts:
        sources.append({"type": "database", "source": db_tool_name or "business_database"})
    sources.extend(_sources_from_chunks(chunks))

    facts_text = json.dumps(database_facts, indent=2, default=str) if database_facts else ""

    client = _groq_client()
    if client is None:
        parts = []
        if facts_text:
            parts.append(f"Database facts:\n{facts_text}")
        if context:
            parts.append(f"Related document context:\n{context}")
        answer = "\n\n".join(parts) if parts else RAG_UNAVAILABLE_MESSAGE
        return {"answer": answer, "confidence": 0.4, "sources": sources}

    try:
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": HYBRID_SYSTEM_PROMPT},
                {"role": "user", "content": build_hybrid_user_prompt(question, facts_text, context)},
            ],
            max_tokens=800,
            temperature=0.2,
        )
        answer = response.choices[0].message.content or INSUFFICIENT_CONTEXT_MESSAGE
        if database_facts and chunks:
            confidence = 0.85
        elif database_facts or chunks:
            confidence = 0.6
        else:
            confidence = 0.2
        return {"answer": answer, "confidence": confidence, "sources": sources}
    except Exception:
        logger.exception("Hybrid answer generation failed")
        return {"answer": RAG_UNAVAILABLE_MESSAGE, "confidence": 0.0, "sources": sources}

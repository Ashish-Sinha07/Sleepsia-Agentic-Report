"""Semantic retrieval over the RAG knowledge base."""

from dataclasses import dataclass
from typing import List, Optional
import logging

from app.rag.vector_store import VectorStore

logger = logging.getLogger(__name__)

# Rough token estimate (no tokenizer dependency needed for a soft context budget).
_CHARS_PER_TOKEN = 4


@dataclass
class RetrievedChunk:
    text: str
    source_file: str
    sheet_name: str
    section: str
    score: float


class Retriever:
    """Embeds the question, searches the vector store, filters and budgets context."""

    def __init__(self, vector_store: VectorStore, top_k: int, min_similarity: float, max_context_tokens: int):
        self._store = vector_store
        self._top_k = top_k
        self._min_similarity = min_similarity
        self._max_context_chars = max_context_tokens * _CHARS_PER_TOKEN

    def retrieve(self, question: str, top_k: Optional[int] = None) -> List[RetrievedChunk]:
        try:
            results = self._store.search(question, top_k=top_k or self._top_k)
        except Exception:
            logger.exception("Vector store search failed")
            return []
        return [
            RetrievedChunk(
                text=r.text,
                source_file=r.metadata.get("source_file", "unknown"),
                sheet_name=r.metadata.get("sheet_name", ""),
                section=r.metadata.get("section", ""),
                score=r.score,
            )
            for r in results
            if r.score >= self._min_similarity
        ]

    def build_context(self, chunks: List[RetrievedChunk]) -> str:
        """Assemble retrieved chunks into one context block, capped to a token budget.

        Never sends the whole knowledge base to the LLM - only the top-scoring
        chunks that fit the configured RAG_MAX_CONTEXT_TOKENS budget.
        """
        blocks: List[str] = []
        total_chars = 0
        for i, chunk in enumerate(chunks):
            label = f"[Source {i + 1}: {chunk.source_file}"
            label += f" / {chunk.sheet_name}]" if chunk.sheet_name else "]"
            block = f"{label}\n{chunk.text}"
            if blocks and total_chars + len(block) > self._max_context_chars:
                break
            blocks.append(block)
            total_chars += len(block)
        return "\n\n---\n\n".join(blocks)


def get_retriever() -> Retriever:
    from app.config import settings
    from app.rag.vector_store import get_vector_store

    return Retriever(
        vector_store=get_vector_store(),
        top_k=settings.RAG_TOP_K,
        min_similarity=settings.RAG_MIN_SIMILARITY,
        max_context_tokens=settings.RAG_MAX_CONTEXT_TOKENS,
    )

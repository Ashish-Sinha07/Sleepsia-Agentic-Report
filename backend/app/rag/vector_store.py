"""Vector store abstraction for the RAG knowledge base.

Kept behind a small interface so the backing implementation (ChromaDB today)
can be swapped for another vector database later without touching callers
(retriever, ingestion service, knowledge admin routes).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Dict, List, Optional
import logging
import re

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    id: str
    text: str
    metadata: Dict[str, Any]
    score: float  # similarity, higher = more relevant, roughly in [0, 1]


class VectorStore(ABC):
    """Abstract interface every vector store backend must implement."""

    @abstractmethod
    def add_documents(self, ids: List[str], texts: List[str], metadatas: List[Dict[str, Any]]) -> None:
        ...

    @abstractmethod
    def delete_documents(self, ids: Optional[List[str]] = None, where: Optional[Dict[str, Any]] = None) -> int:
        ...

    @abstractmethod
    def search(self, query: str, top_k: int = 5, where: Optional[Dict[str, Any]] = None) -> List[SearchResult]:
        ...

    @abstractmethod
    def health_check(self) -> bool:
        ...

    @abstractmethod
    def list_sources(self) -> List[Dict[str, Any]]:
        ...


_METADATA_VALUE_MAX_LEN = 500


def sanitize_metadata_value(value: Any) -> Any:
    """Coerce a metadata value into a type Chroma accepts and cap its length.

    Document content (including any Excel cell or markdown text) only ever
    flows into vector-store *documents*, not metadata keys/values, but we cap
    string length here too as defense in depth against oversized/garbage
    metadata from untrusted uploads.
    """
    if value is None:
        return ""
    if isinstance(value, bool) or isinstance(value, (int, float)):
        return value
    text = value if isinstance(value, str) else str(value)
    return text[:_METADATA_VALUE_MAX_LEN]


class ChromaVectorStore(VectorStore):
    """ChromaDB-backed implementation, persisted locally on disk."""

    def __init__(self, persist_path: str, collection_name: str):
        import chromadb
        from chromadb.utils import embedding_functions

        self._client = chromadb.PersistentClient(path=persist_path)
        self._embedding_function = embedding_functions.DefaultEmbeddingFunction()
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            embedding_function=self._embedding_function,
            metadata={"hnsw:space": "cosine"},
        )

    def add_documents(self, ids: List[str], texts: List[str], metadatas: List[Dict[str, Any]]) -> None:
        if not ids:
            return
        clean_metadatas = [
            {k: sanitize_metadata_value(v) for k, v in (m or {}).items()}
            for m in metadatas
        ]
        self._collection.upsert(ids=ids, documents=texts, metadatas=clean_metadatas)

    def delete_documents(self, ids: Optional[List[str]] = None, where: Optional[Dict[str, Any]] = None) -> int:
        if not ids and not where:
            return 0
        if ids:
            existing = self._collection.get(ids=ids)
            count = len(existing.get("ids", []))
            if count:
                self._collection.delete(ids=ids)
            return count
        existing = self._collection.get(where=where)
        matched_ids = existing.get("ids", [])
        if matched_ids:
            self._collection.delete(where=where)
        return len(matched_ids)

    def search(self, query: str, top_k: int = 5, where: Optional[Dict[str, Any]] = None) -> List[SearchResult]:
        if not query or not query.strip():
            return []
        result = self._collection.query(
            query_texts=[query],
            n_results=top_k,
            where=where,
        )
        out: List[SearchResult] = []
        ids = result.get("ids", [[]])[0]
        docs = result.get("documents", [[]])[0]
        metas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]
        for doc_id, doc, meta, dist in zip(ids, docs, metas, distances):
            # Chroma returns cosine *distance* here; convert to a similarity score.
            similarity = max(0.0, 1.0 - float(dist))
            out.append(SearchResult(id=doc_id, text=doc, metadata=meta or {}, score=similarity))
        return out

    def health_check(self) -> bool:
        try:
            self._collection.count()
            return True
        except Exception:
            logger.exception("Vector store health check failed")
            return False

    def list_sources(self) -> List[Dict[str, Any]]:
        """Return one summary row per distinct source_file currently indexed."""
        data = self._collection.get(include=["metadatas"])
        metadatas = data.get("metadatas", []) or []
        summary: Dict[str, Dict[str, Any]] = {}
        for meta in metadatas:
            meta = meta or {}
            source = meta.get("source_file", "unknown")
            entry = summary.setdefault(
                source,
                {
                    "source_file": source,
                    "document_type": meta.get("document_type", ""),
                    "chunk_count": 0,
                },
            )
            entry["chunk_count"] += 1
        return sorted(summary.values(), key=lambda r: r["source_file"])


_SAFE_ID_CHARS = re.compile(r"[^a-zA-Z0-9_.-]")


def make_chunk_id(source_file: str, sheet_or_section: str, index: int) -> str:
    """Build a deterministic, filesystem/id-safe chunk id.

    Deterministic so re-ingesting the same source overwrites (upserts) its
    previous chunks rather than accumulating duplicates.
    """
    safe_source = _SAFE_ID_CHARS.sub("_", source_file)[:80]
    safe_section = _SAFE_ID_CHARS.sub("_", sheet_or_section)[:60]
    return f"{safe_source}__{safe_section}__{index}"


@lru_cache(maxsize=1)
def get_vector_store() -> VectorStore:
    """Process-wide singleton vector store, built from app settings."""
    from app.config import settings

    return ChromaVectorStore(
        persist_path=settings.VECTOR_STORE_PATH_ABS,
        collection_name=settings.RAG_COLLECTION_NAME,
    )

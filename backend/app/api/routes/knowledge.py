"""Knowledge-base admin API: upload/list/delete documents for the RAG pipeline.

This project has no authentication system at all today (every other endpoint
is unauthenticated). Rather than bolt on a full auth system for this one
feature, these endpoints are protected by a single shared-secret header
(`X-Admin-Key`, checked against `settings.KNOWLEDGE_ADMIN_API_KEY`) - a
deliberately minimal gate that at least closes off "anyone on the network can
rewrite the knowledge base," while being honest that it is not a real
authorization system. If `KNOWLEDGE_ADMIN_API_KEY` is unset, these endpoints
refuse every request (fail closed, not open).
"""

import logging
import secrets
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile
from pydantic import BaseModel

from app.config import settings
from app.rag.ingestion import IngestionError, IngestionService
from app.rag.vector_store import get_vector_store

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/knowledge", tags=["Knowledge Base"])


def require_admin_key(x_admin_key: Optional[str] = Header(default=None)) -> None:
    configured = settings.KNOWLEDGE_ADMIN_API_KEY
    if not configured:
        raise HTTPException(
            status_code=503,
            detail="Knowledge base admin endpoints are disabled: KNOWLEDGE_ADMIN_API_KEY is not configured.",
        )
    if not x_admin_key or not secrets.compare_digest(x_admin_key, configured):
        raise HTTPException(status_code=401, detail="Invalid or missing X-Admin-Key header")


def get_ingestion_service() -> IngestionService:
    return IngestionService(get_vector_store())


class IngestionSummaryResponse(BaseModel):
    filename: str
    sheets_processed: int
    documents_created: int
    chunks_created: int
    status: str
    error: Optional[str] = None


class DocumentSummary(BaseModel):
    source_file: str
    document_type: str
    chunk_count: int


class DeleteResponse(BaseModel):
    source_file: str
    deleted_chunks: int


@router.post("/upload", response_model=IngestionSummaryResponse, dependencies=[Depends(require_admin_key)])
async def upload_document(file: UploadFile = File(...)) -> dict:
    """Upload an Excel/CSV/Markdown document into the RAG knowledge base.

    Flow: validate (type/size) -> parse -> chunk -> embed -> store -> return summary.
    """
    content = await file.read()
    service = get_ingestion_service()
    try:
        summary = service.ingest_bytes(
            file.filename or "upload", content, max_upload_mb=settings.KNOWLEDGE_MAX_UPLOAD_MB
        )
    except IngestionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if summary.status != "success":
        raise HTTPException(status_code=422, detail=summary.error or "Ingestion failed")
    return summary.to_dict()


@router.get("/documents", response_model=List[DocumentSummary], dependencies=[Depends(require_admin_key)])
async def list_documents() -> list:
    """List every distinct source document currently indexed, with its chunk count."""
    return get_ingestion_service().list_sources()


@router.delete(
    "/documents/{source_file}", response_model=DeleteResponse, dependencies=[Depends(require_admin_key)]
)
async def delete_document(source_file: str) -> dict:
    """Remove all indexed chunks for one source document."""
    deleted = get_ingestion_service().delete_source(source_file)
    if deleted == 0:
        raise HTTPException(status_code=404, detail=f"No indexed chunks found for '{source_file}'")
    return {"source_file": source_file, "deleted_chunks": deleted}


@router.post(
    "/reindex-corpus", response_model=List[IngestionSummaryResponse], dependencies=[Depends(require_admin_key)]
)
async def reindex_bundled_corpus() -> list:
    """Re-run ingestion of the bundled knowledge corpus (business-rules.md and the
    Business_Config/Supply_Chain_Config/README/TABLE_DIRECTORY sheets of the main
    workbook). Uploaded documents aren't retained as raw files after ingestion, so
    only this bundled corpus can be re-indexed on demand; re-indexing an uploaded
    document requires re-uploading it.
    """
    from pathlib import Path

    project_root = Path(__file__).resolve().parents[4]
    backend_root = project_root / "backend"
    service = get_ingestion_service()
    summaries = []

    rules_path = project_root / ".claude" / "business-rules.md"
    if rules_path.exists():
        summaries.append(service.ingest_bytes("business-rules.md", rules_path.read_bytes()).to_dict())

    workbook_path = backend_root / "data" / "final_sleepsia_report_data.xlsx"
    if workbook_path.exists():
        summaries.append(
            service.ingest_bytes(
                workbook_path.name,
                workbook_path.read_bytes(),
                knowledge_sheets=["Business_Config", "Supply_Chain_Config", "README", "TABLE_DIRECTORY"],
            ).to_dict()
        )

    if not summaries:
        raise HTTPException(status_code=404, detail="Bundled corpus files not found on disk")
    return summaries

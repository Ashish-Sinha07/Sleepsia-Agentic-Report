#!/usr/bin/env python3
"""Ingest the bundled business-knowledge corpus into the RAG vector store.

Idempotent: re-running replaces each source file's previously-indexed chunks
rather than accumulating duplicates (IngestionService._store_chunks deletes-
then-inserts by source_file).

Sources ingested:
  - .claude/business-rules.md (prose business rules/formulas/thresholds)
  - Business_Config, Supply_Chain_Config, README, TABLE_DIRECTORY sheets from
    the main Sleepsia workbook (config/policy sheets the ETL pipeline
    deliberately never loads into MySQL - see backend/etl/loader.py)

Usage:
    python backend/scripts/ingest_knowledge_base.py
"""

import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_ROOT))
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("ingest_knowledge_base")

KNOWLEDGE_SHEETS = ["Business_Config", "Supply_Chain_Config", "README", "TABLE_DIRECTORY"]


def main() -> int:
    from app.rag.ingestion import IngestionService
    from app.rag.vector_store import get_vector_store

    service = IngestionService(get_vector_store())
    summaries = []

    rules_path = PROJECT_ROOT / ".claude" / "business-rules.md"
    if rules_path.exists():
        content = rules_path.read_bytes()
        summary = service.ingest_bytes("business-rules.md", content)
        summaries.append(summary)
        logger.info("Ingested %s: %s", rules_path.name, summary.to_dict())
    else:
        logger.warning("business-rules.md not found at %s, skipping", rules_path)

    workbook_path = BACKEND_ROOT / "data" / "final_sleepsia_report_data.xlsx"
    if not workbook_path.exists():
        workbook_path = PROJECT_ROOT / "data" / "final_sleepsia_report_data.xlsx"
    if workbook_path.exists():
        content = workbook_path.read_bytes()
        summary = service.ingest_bytes(
            workbook_path.name, content, knowledge_sheets=KNOWLEDGE_SHEETS
        )
        summaries.append(summary)
        logger.info("Ingested %s (knowledge sheets only): %s", workbook_path.name, summary.to_dict())
    else:
        logger.warning("Source workbook not found, skipping")

    total_chunks = sum(s.chunks_created for s in summaries)
    logger.info("Done. %d source(s) ingested, %d total chunks indexed.", len(summaries), total_chunks)
    logger.info("Indexed sources: %s", [s.filename for s in summaries])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

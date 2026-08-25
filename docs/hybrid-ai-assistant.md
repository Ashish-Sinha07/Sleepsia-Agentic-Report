# Hybrid SQL + RAG AI Assistant

Documentation for the query-routing system behind the `/api/ai/ask` endpoint and the
dashboard's AI Business Assistant chatbot.

## 1. Architecture

```
                USER QUESTION
                     |
                     v
              QueryRouter (app/services/query_router.py)
              /      |       \
             /       |        \
          SQL       RAG      HYBRID
           |          |          |
           v          v          v
     sql_tools   Retriever   both of the above
     + sql_guard  (ChromaDB)      |
           |          |           |
           +----------+-----------+
                      |
                      v
          Groq synthesizes a grounded answer
          (app/rag/answer_generator.py)
                      |
                      v
              AskQuestionResponse
              (route, sources, data_sources,
               recommendations, confidence)
                      |
                      v
              dashboard chatbot UI
```

Every question submitted to `POST /api/ai/ask` is classified by `QueryRouter` into
`SQL`, `RAG`, `HYBRID`, or `CLARIFICATION`, then dispatched by
`AIAssistantService.answer_question` (`backend/app/services/ai_assistant_service.py`).

## 2. Query routing

`backend/app/services/query_router.py`. Two-tier classification, in order:

1. **Deterministic phrase rules** (no LLM call, no network dependency): distinguishes
   unambiguous metric terms (`revenue`, `ROAS`, `profit`, ...) - a strong SQL signal on
   their own - from bare domain nouns (`inventory`, `platform`, `warehouse`, ...), which
   only count toward SQL when paired with a superlative/quantifier cue (`highest`,
   `how many`, `total`). This avoids misrouting a question like *"What are the
   guidelines for handling inventory?"* to HYBRID just because "inventory" and
   "guidelines" both appear in it.
2. **Groq JSON-mode classification**, only when the deterministic pass finds no
   signal at all. Returns `{route, confidence, reason, needs_clarification}`.

If neither stage produces a confident route (e.g. Groq is unreachable and no
deterministic keyword matched), the router returns `CLARIFICATION` rather than
guessing.

## 3. SQL flow

`backend/app/services/sql_tools.py` + `backend/app/services/sql_guard.py`.

**Design decision:** the LLM never writes raw SQL text. Instead, Groq picks one of six
fixed, bind-parameterized query templates (`get_kpi_summary`, `get_platform_metrics`,
`get_product_metrics`, `get_advertising_metrics`, `get_inventory_status`,
`get_quality_metrics`) and supplies structured arguments (platform, sku, date range,
limit, order_by). This was chosen over freeform NL→SQL generation because the
underlying schema is small and well-known (8 analytical views) - a fixed template
surface is fully auditable and can't emit anything outside the allowlist, whereas
validating arbitrary generated SQL text robustly would need a full SQL parser this
project doesn't otherwise depend on.

`sql_guard.execute_safe_select` is still run underneath every template call, as
defense in depth:
- Rejects anything that isn't a single, comment-free `SELECT` statement.
- Rejects `INSERT/UPDATE/DELETE/DROP/ALTER/TRUNCATE/CREATE/GRANT/REVOKE/CALL/...`.
- Rejects any table/view outside `ALLOWED_VIEWS` (the raw transactional tables are
  never queryable directly - only the pre-aggregated views in `sql/schema.sql`).
- Clamps `LIMIT` to `SQL_MAX_ROWS` (default 200).
- Adds a MySQL `MAX_EXECUTION_TIME` optimizer hint from `SQL_TIMEOUT_MS` (default 5s).

Dashboard filters (date range, platform, sku, warehouse) are forwarded from
`FilterContext` and backfill any parameter the LLM/deterministic picker didn't already
set (`AIAssistantService._apply_filter_context`) - they're never applied to RAG-only
questions.

If Groq is unavailable, `AIAssistantService._pick_tool_deterministic` selects a tool by
keyword instead, so the SQL path still works without an LLM (see Failure Handling).

## 4. RAG flow

`backend/app/rag/`. Question → embed → search → filter by similarity → build a
token-budgeted context block → Groq answers strictly grounded in that context
(`generate_rag_answer`). If nothing clears `RAG_MIN_SIMILARITY`, or the model decides
the retrieved chunks don't actually answer the question, the response says so
explicitly rather than fabricating an answer.

## 5. Hybrid flow

Runs the SQL tool-call and the RAG retrieval independently, then
`generate_hybrid_answer` asks Groq to combine `DATABASE_FACTS` (JSON) with
`DOCUMENT_CONTEXT` (retrieved chunks), with an explicit instruction to keep every
number traceable to `DATABASE_FACTS` and every policy claim traceable to
`DOCUMENT_CONTEXT`.

## 6. Excel/document ingestion

`backend/app/rag/ingestion.py` + `backend/app/rag/chunking.py`.

Only static business-knowledge content is ever ingested - never the transactional ETL
sheets that already feed MySQL via `backend/etl/loader.py`. Two chunking strategies,
chosen to preserve semantic structure instead of splitting text at a fixed length:

- **Markdown** (`chunk_markdown`): splits on the document's own `---` section
  separators, carrying the nearest `# Group` heading forward as context for every
  `## Rule` section.
- **Spreadsheet rows** (`chunk_sheet_rows`): one chunk per row, rendered as
  `Field: value` lines with empty cells dropped - a config/policy row (e.g.
  `Business_Config`) is already one complete, self-contained rule.

Re-ingesting a source file replaces its previously-indexed chunks (`source_file` is the
dedup key) rather than accumulating duplicates.

The bundled corpus - `.claude/business-rules.md` plus the `Business_Config`,
`Supply_Chain_Config`, `README`, and `TABLE_DIRECTORY` sheets of
`data/final_sleepsia_report_data.xlsx` - is ingested by
`backend/scripts/ingest_knowledge_base.py`.

## 7. Vector store

`backend/app/rag/vector_store.py`. A `VectorStore` abstract interface
(`add_documents` / `delete_documents` / `search` / `health_check` / `list_sources`)
with one implementation today, `ChromaVectorStore`, backed by a local, embedded,
persistent ChromaDB collection at `VECTOR_STORE_PATH`. Swapping to another vector
database later means writing a new class against the same interface - nothing else in
the codebase depends on ChromaDB specifics.

## 8. Embedding model

ChromaDB's bundled default embedding function (`all-MiniLM-L6-v2`, ONNX runtime,
384-dim). Chosen over `sentence-transformers`/PyTorch (much larger install) and over an
external embeddings API (extra API key, and business document content would leave the
server). The model (~80MB) downloads once on first use and is cached locally; no
network calls happen on subsequent embeddings.

## 9. Environment variables

Added to `.env.example` / `backend/app/config.py`:

| Variable | Default | Purpose |
|---|---|---|
| `SQL_MAX_ROWS` | `200` | Row cap enforced by `sql_guard` regardless of what's requested |
| `SQL_TIMEOUT_MS` | `5000` | MySQL `MAX_EXECUTION_TIME` hint per query |
| `VECTOR_STORE_PATH` | `backend/data/chroma_store` | ChromaDB persistence directory (resolved to an absolute path via `settings.VECTOR_STORE_PATH_ABS`, anchored to the project root, regardless of the process's working directory) |
| `RAG_COLLECTION_NAME` | `sleepsia_knowledge` | Chroma collection name |
| `EMBEDDING_MODEL` | `chromadb-default-onnx-minilm-l6-v2` | Informational; see section 8 |
| `RAG_TOP_K` | `5` | Chunks retrieved per query before filtering |
| `RAG_MIN_SIMILARITY` | `0.2` | Chunks below this cosine similarity are discarded |
| `RAG_MAX_CONTEXT_TOKENS` | `1500` | Soft budget for how much retrieved text reaches the LLM |
| `KNOWLEDGE_ADMIN_API_KEY` | *(empty)* | Shared secret for `/api/knowledge/*`; endpoints refuse all requests while empty |
| `KNOWLEDGE_MAX_UPLOAD_MB` | `10` | Upload size cap for the knowledge admin endpoint |

## 10. Security

- **SQL**: read-only by construction (fixed templates, no write/delete tool exists at
  all) plus `sql_guard` validation as defense in depth; row limit and statement timeout
  enforced server-side; the two pre-existing SQL-injection points in the previous
  `ai_assistant_service.py` (`_get_platform_metrics`, `_get_product_metrics`, which
  built SQL via f-string interpolation of LLM-controlled input) were removed, not
  patched - the new templates use bind parameters exclusively.
- **Prompt injection**: retrieved document content is wrapped in the RAG/HYBRID system
  prompts (`app/rag/prompts.py`) with an explicit instruction to treat it as untrusted
  data, never as instructions - even if a cell/paragraph contains text like "ignore
  previous instructions." Verified in `tests/test_rag_ingestion.py` and by design in
  the prompt templates.
- **Uploads**: extension allowlist (`.xlsx/.xls/.csv/.md`), size cap, filename
  sanitization against path traversal (`ingestion.sanitize_filename`).
- **Knowledge admin endpoints**: gated by a shared-secret `X-Admin-Key` header (see
  section 11) - the project has no authentication system at all today, so this is a
  deliberately minimal gate, not a claim of full authorization.
- **No secrets in prompts/logs**; the `.env.example` credential leak found during the
  audit for this feature was scrubbed separately.

## 11. API

- `POST /api/ai/ask` - unchanged request shape (`question`, `context`, `session_id`);
  response extended with `route` (`SQL|RAG|HYBRID|CLARIFICATION`) and `sources`
  (`[{type: "database"|"document", source, sheet}]`) alongside the original `answer`,
  `confidence`, `data_sources`, `recommendations`. Generated SQL is never exposed in
  the response - only a tool name (e.g. `"MySQL: get_kpi_summary"`).
- `GET /api/ai/suggestions`, `POST /api/ai/explain-metric` - unchanged.
- `POST /api/knowledge/upload`, `GET /api/knowledge/documents`,
  `DELETE /api/knowledge/documents/{source_file}`, `POST /api/knowledge/reindex-corpus`
  - all require `X-Admin-Key`. `reindex-corpus` only re-runs the bundled corpus (raw
  uploaded files aren't retained after ingestion, only their embeddings - re-indexing
  an uploaded document means re-uploading it).

## 12. Testing

`backend/tests/`: `test_query_router.py`, `test_sql_guard.py`, `test_rag_ingestion.py`,
`test_ai_assistant_hybrid.py`, `test_ai_api.py`, `test_knowledge_api.py`. Router and
SQL-guard tests are fully hermetic (no network/DB). RAG ingestion tests use an isolated
temporary vector store. The hybrid/API tests run against the real dev MySQL database
(matching this project's existing test convention) with Groq forced off via
monkeypatch for determinism, plus one test that exercises the live Groq path when a key
is configured. Run: `pytest backend/tests/ -v` (from the `backend/` directory, with
`PYTHONPATH` including the project root).

## 13. Troubleshooting

- **RAG always says "insufficient information"**: the knowledge base is probably
  empty. Run `python backend/scripts/ingest_knowledge_base.py` from the project root,
  or check `GET /api/knowledge/documents`.
- **Vector store path issues**: `VECTOR_STORE_PATH` is resolved via
  `settings.VECTOR_STORE_PATH_ABS`, anchored to the project root regardless of the
  process's current working directory - if you see the knowledge base as unexpectedly
  empty after ingesting, confirm the script and the running server are pointed at the
  same resolved path (`python -c "from app.config import settings; print(settings.VECTOR_STORE_PATH_ABS)"`
  from `backend/`).
- **SQL answers reference the wrong period**: check `FilterContext`'s active date
  range/platform in the dashboard - the SQL path defaults to those filters when the
  question doesn't specify its own.
- **Knowledge admin endpoints return 503**: `KNOWLEDGE_ADMIN_API_KEY` is unset; set it
  in `.env`.

## 14. Adding/re-indexing Excel data

- **New document via the UI**: Knowledge Base page (`/knowledge` in the dashboard) →
  enter the admin key → upload an `.xlsx`/`.xls`/`.csv`/`.md` file. All sheets in an
  ad hoc upload are ingested (an admin uploading through this endpoint is presumed to
  be curating knowledge content, not raw transactional data).
- **Re-seed the bundled corpus**: `POST /api/knowledge/reindex-corpus` (or re-run
  `backend/scripts/ingest_knowledge_base.py`) after editing `.claude/business-rules.md`
  or the `Business_Config`/`Supply_Chain_Config` sheets.
- **Remove a document**: `DELETE /api/knowledge/documents/{source_file}` or the
  Knowledge Base page's delete button.

## 15. Replacing the vector database later

Implement the `VectorStore` interface (`backend/app/rag/vector_store.py`) against the
new backend, then change `get_vector_store()` to construct it instead of
`ChromaVectorStore`. Nothing in `ingestion.py`, `retriever.py`, or the knowledge admin
routes references ChromaDB directly - they only call the interface methods.

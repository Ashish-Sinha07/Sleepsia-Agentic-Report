"""Semantic chunking for the RAG knowledge base.

Deliberately does NOT split text every N characters. Markdown documents are
split on their own section boundaries; spreadsheet rows are kept whole (one
config/policy row already *is* one complete, self-contained rule) instead of
being split at arbitrary cell/character boundaries.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import re


@dataclass
class Chunk:
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)


_SECTION_SPLIT_RE = re.compile(r"\n-{3,}\n")


def chunk_markdown(text: str, source_file: str) -> List[Chunk]:
    """Chunk a markdown SOP/policy document by its own `---`-separated sections.

    Documents like `.claude/business-rules.md` are already organized as
    `# Group heading` / `## Rule heading` / body, with `---` between rules.
    We split on that existing structure and carry the nearest preceding `#`
    group heading forward as context, rather than cutting at a fixed length
    (which would risk splitting a formula from its explanation).
    """
    text = text.replace("\r\n", "\n")
    sections = _SECTION_SPLIT_RE.split(text)

    chunks: List[Chunk] = []
    current_group = ""
    idx = 0
    for section in sections:
        section = section.strip("\n")
        if not section.strip():
            continue

        heading = ""
        body_lines: List[str] = []
        for line in section.split("\n"):
            stripped = line.strip()
            if stripped.startswith("## "):
                if not heading:
                    heading = stripped[3:].strip()
                    continue
            elif stripped.startswith("# "):
                current_group = stripped[2:].strip()
                continue
            body_lines.append(line)

        body = "\n".join(body_lines).strip()
        if not body:
            continue

        title = f"{current_group} - {heading}" if heading else (current_group or "General")
        chunks.append(
            Chunk(
                text=f"{title}\n\n{body}",
                metadata={
                    "source_file": source_file,
                    "sheet_name": current_group or "General",
                    "section": heading or current_group or "General",
                    "row_number": idx,
                    "document_type": "business_knowledge",
                },
            )
        )
        idx += 1
    return chunks


def chunk_sheet_rows(
    rows: List[Dict[str, Any]],
    sheet_name: str,
    source_file: str,
    document_type: str = "business_knowledge",
    header_row_offset: int = 2,
) -> List[Chunk]:
    """One chunk per spreadsheet/CSV row, rendered as `Field: value` lines.

    Each row in the config/knowledge sheets we ingest (Business_Config,
    Supply_Chain_Config, README, TABLE_DIRECTORY) already represents one
    complete, self-contained rule or fact - grouping unrelated rows together
    would only dilute retrieval precision, and splitting a single row's
    cells apart would break it. Empty cells are dropped so a chunk only
    contains the fields that actually carry information.
    """
    chunks: List[Chunk] = []
    for i, row in enumerate(rows):
        lines = [f"Sheet: {sheet_name}"]
        for key, value in row.items():
            if value is None:
                continue
            text_value = str(value).strip()
            if not text_value:
                continue
            lines.append(f"{key}: {text_value}")

        if len(lines) <= 1:
            continue  # row was entirely empty after stripping

        chunks.append(
            Chunk(
                text="\n".join(lines),
                metadata={
                    "source_file": source_file,
                    "sheet_name": sheet_name,
                    "row_number": i + header_row_offset,
                    "document_type": document_type,
                },
            )
        )
    return chunks

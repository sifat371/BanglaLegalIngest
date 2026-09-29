"""Deterministic page-grounded chunk generation for retrieval systems."""

from pathlib import Path

from legal_ingest.schemas import LegalDocument, RetrievalChunk


def _choose_end(text: str, start: int, chunk_size: int) -> int:
    hard_end = min(start + chunk_size, len(text))
    if hard_end >= len(text):
        return len(text)

    window = text[start:hard_end]
    minimum_break = int(chunk_size * 0.60)

    candidates = [
        window.rfind("\n\n"),
        window.rfind(". "),
        window.rfind("। "),
        window.rfind(" "),
    ]
    boundary = max(candidates)

    if boundary >= minimum_break:
        return start + boundary + 1
    return hard_end


def _trim_span(text: str, start: int, end: int) -> tuple[int, int]:
    while start < end and text[start].isspace():
        start += 1
    while end > start and text[end - 1].isspace():
        end -= 1
    return start, end


def to_retrieval_chunks(
    document: LegalDocument,
    *,
    chunk_size: int = 1000,
    overlap: int = 150,
) -> list[RetrievalChunk]:
    """Create deterministic page-local chunks with exact character provenance."""

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")
    if overlap < 0:
        raise ValueError("overlap cannot be negative")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")
    if not document.pages:
        raise ValueError(
            "Page-aware retrieval chunks require document.pages; "
            "ingest with preserve_page_text=True."
        )

    chunks: list[RetrievalChunk] = []

    for page in document.pages:
        text = page.text
        start = 0
        chunk_index = 0

        while start < len(text):
            end = _choose_end(text, start, chunk_size)
            trimmed_start, trimmed_end = _trim_span(text, start, end)

            if trimmed_start < trimmed_end:
                chunks.append(
                    RetrievalChunk(
                        chunk_id=f"{document.document_id}:p{page.page_number}:c{chunk_index}",
                        document_id=document.document_id,
                        source_filename=document.source_filename,
                        source_sha256=document.source_sha256,
                        page_start=page.page_number,
                        page_end=page.page_number,
                        chunk_index=chunk_index,
                        char_start=trimmed_start,
                        char_end=trimmed_end,
                        text=text[trimmed_start:trimmed_end],
                        case_number=document.metadata.case_number,
                        case_type=document.metadata.case_type,
                        court=document.metadata.court,
                        district=document.metadata.district,
                        judges=document.metadata.judges,
                        citations=document.metadata.citations,
                    )
                )
                chunk_index += 1

            if end >= len(text):
                break

            start = max(end - overlap, start + 1)

    return chunks


def chunks_to_jsonl(chunks: list[RetrievalChunk]) -> str:
    """Serialize chunks as newline-delimited JSON."""

    if not chunks:
        return ""
    return "\n".join(chunk.model_dump_json() for chunk in chunks) + "\n"


def write_chunks_jsonl(chunks: list[RetrievalChunk], path: str | Path) -> Path:
    """Write retrieval chunks as UTF-8 JSONL."""

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(chunks_to_jsonl(chunks), encoding="utf-8")
    return output

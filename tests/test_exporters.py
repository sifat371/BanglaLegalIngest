import json

import pytest

from legal_ingest.exporters import (
    chunks_to_jsonl,
    to_json,
    to_markdown,
    to_retrieval_chunks,
    write_chunks_jsonl,
    write_json,
    write_markdown,
)
from legal_ingest.schemas import (
    ExtractionDiagnostics,
    IngestionResult,
    LegalDocument,
    LegalMetadata,
    PageContent,
)


def make_result() -> IngestionResult:
    document = LegalDocument(
        document_id="abc123",
        source_filename="judgment.pdf",
        source_sha256="abc123",
        metadata=LegalMetadata(
            case_number="Writ Petition No. 12 of 2026",
            case_type="Writ Petition",
            court="Supreme Court of Bangladesh High Court Division",
            district="Rajshahi",
            judges=["Example Justice"],
            citations=["section 1 of the Penal Code"],
        ),
        pages=[
            PageContent(
                page_number=1,
                text=(
                    "First paragraph about a legal question. "
                    "Second sentence provides more context. " * 12
                ),
            ),
            PageContent(page_number=2, text="Short second page."),
        ],
        text="combined",
    )
    return IngestionResult(
        document=document,
        diagnostics=ExtractionDiagnostics(extractor="pdfplumber"),
    )


def test_json_export_is_canonical() -> None:
    payload = json.loads(to_json(make_result()))

    assert payload["document"]["source_filename"] == "judgment.pdf"
    assert payload["document"]["metadata"]["case_number"] == "Writ Petition No. 12 of 2026"


def test_markdown_export_preserves_page_headings() -> None:
    markdown = to_markdown(make_result())

    assert "# judgment.pdf" in markdown
    assert "### Page 1" in markdown
    assert "### Page 2" in markdown
    assert "Writ Petition No. 12 of 2026" in markdown


def test_retrieval_chunks_are_page_grounded_and_deterministic() -> None:
    result = make_result()
    chunks = to_retrieval_chunks(
        result.document,
        chunk_size=180,
        overlap=30,
    )

    assert len(chunks) > 2
    assert chunks[0].chunk_id == "abc123:p1:c0"
    assert all(chunk.page_start == chunk.page_end for chunk in chunks)
    assert all(
        chunk.text
        == result.document.pages[chunk.page_start - 1].text[
            chunk.char_start:chunk.char_end
        ]
        for chunk in chunks
    )
    assert chunks[0].case_number == "Writ Petition No. 12 of 2026"


def test_chunks_require_page_payload() -> None:
    document = LegalDocument(
        document_id="abc",
        source_filename="flat.pdf",
        text="flat text only",
    )

    with pytest.raises(ValueError):
        to_retrieval_chunks(document)


def test_export_writers_create_explicit_files(tmp_path) -> None:
    result = make_result()
    chunks = to_retrieval_chunks(result.document, chunk_size=200, overlap=20)

    json_path = write_json(result, tmp_path / "result.json")
    markdown_path = write_markdown(result, tmp_path / "result.md")
    chunks_path = write_chunks_jsonl(chunks, tmp_path / "chunks.jsonl")

    assert json_path.exists()
    assert markdown_path.exists()
    assert chunks_path.exists()
    assert len(chunks_to_jsonl(chunks).splitlines()) == len(chunks)

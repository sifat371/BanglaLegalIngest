import hashlib

import pytest

from legal_ingest import LegalDocumentPipeline, PipelineConfig
from legal_ingest.exceptions import ExtractionError, UnsupportedDocumentError
from legal_ingest.extractors.base import DocumentExtractor
from legal_ingest.schemas import ExtractedContent, PageContent


class FakeExtractor(DocumentExtractor):
    name = "fake"

    def __init__(self, text: str = "A sufficiently long legal document.") -> None:
        self.text = text

    def extract(self, _path):
        pages = [
            PageContent(page_number=1, text=self.text),
            PageContent(page_number=2, text="Second page."),
        ]
        return ExtractedContent(
            pages=pages,
            text=f"{self.text}\n\nSecond page.",
        )


def test_pipeline_returns_canonical_result_and_hash(tmp_path) -> None:
    path = tmp_path / "case.pdf"
    raw = b"fake-pdf-content"
    path.write_bytes(raw)

    pipeline = LegalDocumentPipeline(
        PipelineConfig(min_extracted_characters=1),
        extractor=FakeExtractor(),
    )
    result = pipeline.ingest(path)

    expected_hash = hashlib.sha256(raw).hexdigest()
    assert result.document.document_id == expected_hash
    assert result.document.source_sha256 == expected_hash
    assert result.document.source_filename == "case.pdf"
    assert [page.page_number for page in result.document.pages] == [1, 2]
    assert result.diagnostics.extractor == "fake"
    assert result.diagnostics.fallback_used is False


def test_pipeline_can_omit_page_payload_but_keep_full_text(tmp_path) -> None:
    path = tmp_path / "case.pdf"
    path.write_bytes(b"fake")

    pipeline = LegalDocumentPipeline(
        PipelineConfig(
            min_extracted_characters=1,
            preserve_page_text=False,
        ),
        extractor=FakeExtractor(),
    )
    result = pipeline.ingest(path)

    assert result.document.pages == []
    assert "Second page." in result.document.text


def test_auto_uses_pypdf_when_pdfplumber_is_too_short(tmp_path, monkeypatch) -> None:
    path = tmp_path / "case.pdf"
    path.write_bytes(b"fake")

    class NamedFake(FakeExtractor):
        def __init__(self, name: str, text: str) -> None:
            super().__init__(text)
            self.name = name

    extractors = {
        "pdfplumber": NamedFake("pdfplumber", "x"),
        "pypdf": NamedFake("pypdf", "long enough"),
    }

    monkeypatch.setattr(
        "legal_ingest.pipeline.create_extractor",
        lambda name: extractors[name],
    )

    pipeline = LegalDocumentPipeline(PipelineConfig(min_extracted_characters=5))
    result = pipeline.ingest(path)

    assert result.diagnostics.extractor == "pypdf"
    assert result.diagnostics.fallback_used is True
    assert any("below the configured minimum" in warning for warning in result.diagnostics.warnings)


def test_explicit_extractor_enforces_minimum_text(tmp_path) -> None:
    path = tmp_path / "case.pdf"
    path.write_bytes(b"fake")

    pipeline = LegalDocumentPipeline(
        PipelineConfig(min_extracted_characters=100),
        extractor=FakeExtractor(text="short"),
    )

    with pytest.raises(ExtractionError):
        pipeline.ingest(path)


def test_pipeline_rejects_non_pdf(tmp_path) -> None:
    path = tmp_path / "case.txt"
    path.write_text("text")

    with pytest.raises(UnsupportedDocumentError):
        LegalDocumentPipeline(extractor=FakeExtractor()).ingest(path)


def test_pipeline_rejects_missing_file(tmp_path) -> None:
    path = tmp_path / "missing.pdf"

    with pytest.raises(FileNotFoundError):
        LegalDocumentPipeline(extractor=FakeExtractor()).ingest(path)

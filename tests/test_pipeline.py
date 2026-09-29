import hashlib

import pytest

from legal_ingest import LegalDocumentPipeline, PipelineConfig
from legal_ingest.exceptions import ExtractionError, UnsupportedDocumentError
from legal_ingest.extractors.base import DocumentExtractor
from legal_ingest.schemas import EncodingKind, ExtractedContent, PageContent


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
    assert result.document.encoding.kind == EncodingKind.NONE


def test_pipeline_parses_metadata_from_page_content(tmp_path) -> None:
    path = tmp_path / "case.pdf"
    path.write_bytes(b"fake")
    caption = (
        "District: Rajshahi.\n"
        "Supreme Court of Bangladesh High Court Division\n"
        "Writ Petition No. 12 of 2026"
    )

    pipeline = LegalDocumentPipeline(
        PipelineConfig(min_extracted_characters=1),
        extractor=FakeExtractor(text=caption),
    )
    result = pipeline.ingest(path)

    assert result.document.metadata.case_number == "Writ Petition No. 12 of 2026"
    assert result.document.metadata.district == "Rajshahi"
    assert result.diagnostics.quality_metrics["metadata_fields_populated"] >= 2


def test_pipeline_can_disable_metadata_parsing(tmp_path) -> None:
    path = tmp_path / "case.pdf"
    path.write_bytes(b"fake")
    caption = "Writ Petition No. 12 of 2026"

    pipeline = LegalDocumentPipeline(
        PipelineConfig(min_extracted_characters=1, parse_metadata=False),
        extractor=FakeExtractor(text=caption),
    )
    result = pipeline.ingest(path)

    assert result.document.metadata.case_number is None
    assert result.document.metadata.evidence == {}


def test_pipeline_detects_bijoy_even_when_conversion_is_disabled(tmp_path) -> None:
    path = tmp_path / "case.pdf"
    path.write_bytes(b"fake")
    bijoy_text = "Avwg AvBb ‡K †"

    pipeline = LegalDocumentPipeline(
        PipelineConfig(
            min_extracted_characters=1,
            convert_bijoy=False,
        ),
        extractor=FakeExtractor(text=bijoy_text),
    )
    result = pipeline.ingest(path)

    assert result.document.encoding.kind == EncodingKind.BIJOY
    assert result.document.encoding.bijoy_candidate_lines == 1
    assert result.document.encoding.normalization_applied is False
    assert result.document.pages[0].text == bijoy_text


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

    class NamedFake(DocumentExtractor):
        def __init__(self, name: str, text: str) -> None:
            self.name = name
            self.text = text

        def extract(self, _path):
            return ExtractedContent(
                pages=[PageContent(page_number=1, text=self.text)],
                text=self.text,
            )

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

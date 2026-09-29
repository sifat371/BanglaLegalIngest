from legal_ingest import LegalDocumentPipeline, PipelineConfig
from legal_ingest.extractors.base import DocumentExtractor
from legal_ingest.schemas import ExtractedContent, PageContent


class FakeExtractor(DocumentExtractor):
    def __init__(self, name: str, pages: list[str]) -> None:
        self.name = name
        self._pages = pages

    def extract(self, _path):
        page_models = [
            PageContent(page_number=index, text=text)
            for index, text in enumerate(self._pages, start=1)
        ]
        return ExtractedContent(
            pages=page_models,
            text="\n\n".join(self._pages),
        )


def test_auto_quality_routing_prefers_better_fallback(tmp_path, monkeypatch) -> None:
    path = tmp_path / "case.pdf"
    path.write_bytes(b"fake")

    extractors = {
        "pdfplumber": FakeExtractor("pdfplumber", ["x" * 120, ""]),
        "pypdf": FakeExtractor("pypdf", ["A" * 700, "B" * 700]),
    }
    monkeypatch.setattr(
        "legal_ingest.pipeline.create_extractor",
        lambda name: extractors[name],
    )

    pipeline = LegalDocumentPipeline(
        PipelineConfig(
            min_extracted_characters=100,
            min_quality_score=0.80,
            parse_metadata=False,
        )
    )
    result = pipeline.ingest(path)

    assert result.diagnostics.extractor == "pypdf"
    assert result.diagnostics.fallback_used is True
    assert [attempt.extractor for attempt in result.diagnostics.attempted_extractors] == [
        "pdfplumber",
        "pypdf",
    ]
    assert result.diagnostics.quality is not None
    assert result.diagnostics.quality.usability_score >= 0.80


def test_auto_uses_best_available_when_threshold_is_not_met(tmp_path, monkeypatch) -> None:
    path = tmp_path / "case.pdf"
    path.write_bytes(b"fake")

    extractors = {
        "pdfplumber": FakeExtractor("pdfplumber", ["a" * 130]),
        "pypdf": FakeExtractor("pypdf", ["b" * 200]),
    }
    monkeypatch.setattr(
        "legal_ingest.pipeline.create_extractor",
        lambda name: extractors[name],
    )

    pipeline = LegalDocumentPipeline(
        PipelineConfig(
            min_extracted_characters=100,
            min_quality_score=0.99,
            parse_metadata=False,
        )
    )
    result = pipeline.ingest(path)

    assert result.diagnostics.extractor == "pypdf"
    assert any(
        "No automatic extractor met" in warning
        for warning in result.diagnostics.warnings
    )

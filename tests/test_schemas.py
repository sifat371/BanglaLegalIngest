import pytest
from pydantic import ValidationError

from legal_ingest.schemas import (
    EncodingInfo,
    EncodingKind,
    ExtractionDiagnostics,
    IngestionResult,
    LegalDocument,
    LegalMetadata,
    PageContent,
    Party,
)


def test_canonical_result_round_trip() -> None:
    result = IngestionResult(
        document=LegalDocument(
            document_id="case-001",
            source_filename="case.pdf",
            metadata=LegalMetadata(
                case_number="Writ Petition No. 1 of 2026",
                judges=["Example Justice"],
                parties=[Party(name="The State", role="respondent")],
            ),
            encoding=EncodingInfo(
                kind=EncodingKind.MIXED,
                has_bangla=True,
                unicode_bangla_chars=24,
                bijoy_indicators=3,
                normalization_applied=True,
            ),
            pages=[PageContent(page_number=1, text="Example text")],
            text="Example text",
        ),
        diagnostics=ExtractionDiagnostics(
            extractor="pdfplumber",
            quality_metrics={"printable_ratio": 1.0},
        ),
    )

    restored = IngestionResult.model_validate_json(result.model_dump_json())

    assert restored.document.metadata.case_number == "Writ Petition No. 1 of 2026"
    assert restored.document.pages[0].page_number == 1
    assert restored.diagnostics.extractor == "pdfplumber"


def test_page_numbers_are_one_based() -> None:
    with pytest.raises(ValidationError):
        PageContent(page_number=0, text="invalid")


def test_schema_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        LegalMetadata(case_number="1", unexpected="value")

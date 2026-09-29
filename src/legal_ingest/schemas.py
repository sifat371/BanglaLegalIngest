"""Canonical data contracts shared by all ingestion backends."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    """Base model that rejects accidental schema drift."""

    model_config = ConfigDict(extra="forbid")


class EncodingKind(StrEnum):
    """High-level text-encoding classification used by the pipeline."""

    UNICODE_BANGLA = "unicode_bangla"
    BIJOY = "bijoy"
    MIXED = "mixed"
    NONE = "none"
    UNKNOWN = "unknown"


class PageContent(StrictModel):
    """Text extracted from one source page."""

    page_number: int = Field(ge=1)
    text: str


class Party(StrictModel):
    """A named party in a legal matter."""

    name: str
    role: str | None = None


class EvidenceSpan(StrictModel):
    """Source evidence supporting an extracted metadata field."""

    page_number: int = Field(ge=1)
    text: str
    start_char: int | None = Field(default=None, ge=0)
    end_char: int | None = Field(default=None, ge=0)


class LegalMetadata(StrictModel):
    """Normalized legal metadata independent of extraction backend."""

    case_number: str | None = None
    case_type: str | None = None
    court: str | None = None
    district: str | None = None
    judges: list[str] = Field(default_factory=list)
    parties: list[Party] = Field(default_factory=list)
    hearing_dates: list[str] = Field(default_factory=list)
    judgment_date: str | None = None
    citations: list[str] = Field(default_factory=list)


class EncodingInfo(StrictModel):
    """Encoding/language diagnostics captured during ingestion."""

    kind: EncodingKind = EncodingKind.UNKNOWN
    has_bangla: bool = False
    unicode_bangla_chars: int = Field(default=0, ge=0)
    bijoy_indicators: int = Field(default=0, ge=0)
    normalization_applied: bool = False


class ExtractionDiagnostics(StrictModel):
    """Observable extraction behavior and quality signals."""

    extractor: str
    fallback_used: bool = False
    processing_seconds: float | None = Field(default=None, ge=0)
    quality_metrics: dict[str, float] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


class LegalDocument(StrictModel):
    """Canonical representation produced by every future extractor path."""

    schema_version: str = "1.0"
    document_id: str
    source_filename: str
    source_sha256: str | None = None
    metadata: LegalMetadata = Field(default_factory=LegalMetadata)
    encoding: EncodingInfo = Field(default_factory=EncodingInfo)
    pages: list[PageContent] = Field(default_factory=list)
    text: str = ""


class IngestionResult(StrictModel):
    """Top-level result returned by the public ingestion API."""

    document: LegalDocument
    diagnostics: ExtractionDiagnostics

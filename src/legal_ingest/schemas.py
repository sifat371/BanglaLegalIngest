"""Canonical data contracts shared by all ingestion backends."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    """Base model that rejects accidental schema drift."""

    model_config = ConfigDict(extra="forbid")


class EncodingKind(StrEnum):
    """High-level source text-encoding classification."""

    UNICODE_BANGLA = "unicode_bangla"
    BIJOY = "bijoy"
    MIXED = "mixed"
    NONE = "none"
    UNKNOWN = "unknown"


class PageContent(StrictModel):
    """Text extracted from one source page."""

    page_number: int = Field(ge=1)
    text: str


class ExtractedContent(StrictModel):
    """Backend-neutral, page-aware output returned by extractors."""

    pages: list[PageContent] = Field(default_factory=list)
    text: str = ""
    warnings: list[str] = Field(default_factory=list)


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
    """Normalized legal metadata plus page-level extraction evidence."""

    case_number: str | None = None
    case_type: str | None = None
    court: str | None = None
    district: str | None = None
    judges: list[str] = Field(default_factory=list)
    parties: list[Party] = Field(default_factory=list)
    hearing_dates: list[str] = Field(default_factory=list)
    judgment_date: str | None = None
    citations: list[str] = Field(default_factory=list)
    evidence: dict[str, list[EvidenceSpan]] = Field(default_factory=dict)


class EncodingInfo(StrictModel):
    """Source encoding diagnostics and normalization outcome."""

    kind: EncodingKind = EncodingKind.UNKNOWN
    has_bangla: bool = False
    unicode_bangla_chars: int = Field(default=0, ge=0)
    bijoy_indicators: int = Field(default=0, ge=0)
    total_characters: int = Field(default=0, ge=0)
    bijoy_candidate_lines: int = Field(default=0, ge=0)
    normalization_applied: bool = False
    converted_lines: int = Field(default=0, ge=0)
    conversion_failures: int = Field(default=0, ge=0)


class ExtractionQuality(StrictModel):
    """Transparent text-extraction usability signals."""

    page_count: int = Field(ge=0)
    non_empty_page_ratio: float = Field(ge=0.0, le=1.0)
    printable_ratio: float = Field(ge=0.0, le=1.0)
    replacement_char_ratio: float = Field(ge=0.0, le=1.0)
    control_char_ratio: float = Field(ge=0.0, le=1.0)
    average_chars_per_page: float = Field(ge=0.0)
    usability_score: float = Field(ge=0.0, le=1.0)


class RoutingAttempt(StrictModel):
    """One extractor attempt made by automatic routing."""

    extractor: str
    succeeded: bool
    extracted_characters: int = Field(default=0, ge=0)
    quality_score: float | None = Field(default=None, ge=0.0, le=1.0)
    error: str | None = None


class ExtractionDiagnostics(StrictModel):
    """Observable extraction behavior and routing signals."""

    extractor: str
    fallback_used: bool = False
    processing_seconds: float | None = Field(default=None, ge=0)
    quality: ExtractionQuality | None = None
    attempted_extractors: list[RoutingAttempt] = Field(default_factory=list)
    quality_metrics: dict[str, float] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


class LegalDocument(StrictModel):
    """Canonical representation produced by every ingestion path."""

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


class RetrievalChunk(StrictModel):
    """Page-grounded chunk suitable for downstream retrieval/indexing."""

    chunk_id: str
    document_id: str
    source_filename: str
    source_sha256: str | None = None
    page_start: int = Field(ge=1)
    page_end: int = Field(ge=1)
    chunk_index: int = Field(ge=0)
    char_start: int = Field(ge=0)
    char_end: int = Field(ge=0)
    text: str
    case_number: str | None = None
    case_type: str | None = None
    court: str | None = None
    district: str | None = None
    judges: list[str] = Field(default_factory=list)
    citations: list[str] = Field(default_factory=list)

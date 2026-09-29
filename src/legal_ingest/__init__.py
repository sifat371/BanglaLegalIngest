"""Public package interface for legal-document-ingestion."""

from legal_ingest.config import PipelineConfig
from legal_ingest.schemas import (
    EncodingInfo,
    EncodingKind,
    EvidenceSpan,
    ExtractionDiagnostics,
    IngestionResult,
    LegalDocument,
    LegalMetadata,
    PageContent,
    Party,
)

__version__ = "0.1.0a1"

__all__ = [
    "__version__",
    "PipelineConfig",
    "EncodingInfo",
    "EncodingKind",
    "EvidenceSpan",
    "ExtractionDiagnostics",
    "IngestionResult",
    "LegalDocument",
    "LegalMetadata",
    "PageContent",
    "Party",
]

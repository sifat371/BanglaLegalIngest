"""Public package interface for legal-document-ingestion."""

from legal_ingest.config import PipelineConfig
from legal_ingest.encoding import BanglaEncodingNormalizer, detect_encoding, is_bijoy_line
from legal_ingest.parsing import parse_legal_metadata
from legal_ingest.pipeline import LegalDocumentPipeline
from legal_ingest.schemas import (
    EncodingInfo,
    EncodingKind,
    EvidenceSpan,
    ExtractedContent,
    ExtractionDiagnostics,
    IngestionResult,
    LegalDocument,
    LegalMetadata,
    PageContent,
    Party,
)

__version__ = "0.4.0a1"

__all__ = [
    "__version__",
    "BanglaEncodingNormalizer",
    "LegalDocumentPipeline",
    "PipelineConfig",
    "detect_encoding",
    "is_bijoy_line",
    "parse_legal_metadata",
    "EncodingInfo",
    "EncodingKind",
    "EvidenceSpan",
    "ExtractedContent",
    "ExtractionDiagnostics",
    "IngestionResult",
    "LegalDocument",
    "LegalMetadata",
    "PageContent",
    "Party",
]

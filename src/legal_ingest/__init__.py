"""Public package interface for legal-document-ingestion."""

from legal_ingest.config import PipelineConfig
from legal_ingest.encoding import BanglaEncodingNormalizer, detect_encoding, is_bijoy_line
from legal_ingest.exporters import (
    chunks_to_jsonl,
    to_json,
    to_markdown,
    to_retrieval_chunks,
    write_chunks_jsonl,
    write_json,
    write_markdown,
)
from legal_ingest.parsing import parse_legal_metadata
from legal_ingest.pipeline import LegalDocumentPipeline
from legal_ingest.quality import assess_extraction_quality
from legal_ingest.schemas import (
    EncodingInfo,
    EncodingKind,
    EvidenceSpan,
    ExtractedContent,
    ExtractionDiagnostics,
    ExtractionQuality,
    IngestionResult,
    LegalDocument,
    LegalMetadata,
    PageContent,
    Party,
    RetrievalChunk,
    RoutingAttempt,
)

__version__ = "0.5.0a1"

__all__ = [
    "__version__",
    "BanglaEncodingNormalizer",
    "LegalDocumentPipeline",
    "PipelineConfig",
    "assess_extraction_quality",
    "chunks_to_jsonl",
    "detect_encoding",
    "is_bijoy_line",
    "parse_legal_metadata",
    "to_json",
    "to_markdown",
    "to_retrieval_chunks",
    "write_chunks_jsonl",
    "write_json",
    "write_markdown",
    "EncodingInfo",
    "EncodingKind",
    "EvidenceSpan",
    "ExtractedContent",
    "ExtractionDiagnostics",
    "ExtractionQuality",
    "IngestionResult",
    "LegalDocument",
    "LegalMetadata",
    "PageContent",
    "Party",
    "RetrievalChunk",
    "RoutingAttempt",
]

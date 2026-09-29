"""Public document-ingestion pipeline."""

import hashlib
import time
from collections.abc import Iterable
from pathlib import Path
from typing import TypeAlias

from legal_ingest.config import ExtractorName, PipelineConfig
from legal_ingest.encoding import process_extracted_content
from legal_ingest.exceptions import ExtractionError, LegalIngestError, UnsupportedDocumentError
from legal_ingest.extractors import DocumentExtractor, create_extractor
from legal_ingest.parsing import parse_legal_metadata
from legal_ingest.schemas import ExtractionDiagnostics, IngestionResult, LegalDocument, LegalMetadata

PathInput: TypeAlias = str | Path


class LegalDocumentPipeline:
    """Coordinate extraction, encoding normalization, and metadata parsing."""

    def __init__(
        self,
        config: PipelineConfig | None = None,
        *,
        extractor: ExtractorName | DocumentExtractor | None = None,
    ) -> None:
        self.config = config or PipelineConfig()
        self._custom_extractor: DocumentExtractor | None = None

        if isinstance(extractor, DocumentExtractor):
            self._custom_extractor = extractor
        elif extractor is not None:
            self.config = self.config.model_copy(update={"extractor": extractor})

    def ingest(self, source: PathInput) -> IngestionResult:
        """Ingest one PDF and return a canonical, page-aware result."""

        path = self._validate_source(source)
        started = time.perf_counter()

        if self._custom_extractor is not None:
            content = self._custom_extractor.extract(path)
            self._require_minimum_text(content.text, self._custom_extractor.name)
            extractor_name = self._custom_extractor.name
            fallback_used = False
            warnings = list(content.warnings)
        elif self.config.extractor == "auto":
            content, extractor_name, fallback_used, warnings = self._extract_auto(path)
        else:
            backend = create_extractor(self.config.extractor)
            content = backend.extract(path)
            self._require_minimum_text(content.text, backend.name)
            extractor_name = backend.name
            fallback_used = False
            warnings = list(content.warnings)

        content, encoding = process_extracted_content(
            content,
            convert_bijoy=self.config.convert_bijoy,
        )
        warnings = list(dict.fromkeys([*warnings, *content.warnings]))

        metadata = (
            parse_legal_metadata(content.pages)
            if self.config.parse_metadata
            else LegalMetadata()
        )

        source_sha256 = self._sha256(path)
        elapsed = time.perf_counter() - started

        document = LegalDocument(
            document_id=source_sha256,
            source_filename=path.name,
            source_sha256=source_sha256,
            metadata=metadata,
            encoding=encoding,
            pages=content.pages if self.config.preserve_page_text else [],
            text=content.text,
        )
        diagnostics = ExtractionDiagnostics(
            extractor=extractor_name,
            fallback_used=fallback_used,
            processing_seconds=elapsed,
            quality_metrics={
                "page_count": float(len(content.pages)),
                "extracted_characters": float(len(content.text)),
                "unicode_bangla_chars": float(encoding.unicode_bangla_chars),
                "bijoy_indicators": float(encoding.bijoy_indicators),
                "bijoy_candidate_lines": float(encoding.bijoy_candidate_lines),
                "metadata_fields_populated": float(self._metadata_field_count(metadata)),
            },
            warnings=warnings,
        )
        return IngestionResult(document=document, diagnostics=diagnostics)

    def ingest_many(self, sources: Iterable[PathInput]) -> list[IngestionResult]:
        """Ingest several explicit document paths in order."""

        return [self.ingest(source) for source in sources]

    def _extract_auto(self, path: Path):
        warnings: list[str] = []
        primary_error: str | None = None

        try:
            primary = create_extractor("pdfplumber")
            content = primary.extract(path)
            if self._has_minimum_text(content.text):
                return content, primary.name, False, list(content.warnings)
            primary_error = (
                f"pdfplumber extracted {len(content.text)} characters, below the configured "
                f"minimum of {self.config.min_extracted_characters}."
            )
            warnings.extend(content.warnings)
            warnings.append(primary_error)
        except LegalIngestError as exc:
            primary_error = str(exc)
            warnings.append(f"pdfplumber unavailable or failed: {exc}")

        try:
            fallback = create_extractor("pypdf")
            content = fallback.extract(path)
            self._require_minimum_text(content.text, fallback.name)
            warnings.extend(content.warnings)
            return content, fallback.name, True, warnings
        except LegalIngestError as exc:
            message = "Automatic extraction failed with both pdfplumber and pypdf."
            if primary_error:
                message += f" Primary: {primary_error}"
            message += f" Fallback: {exc}"
            raise ExtractionError(message) from exc

    def _has_minimum_text(self, text: str) -> bool:
        return len(text.strip()) >= self.config.min_extracted_characters

    def _require_minimum_text(self, text: str, extractor_name: str) -> None:
        if not self._has_minimum_text(text):
            raise ExtractionError(
                f"{extractor_name} extracted {len(text.strip())} characters, below the configured "
                f"minimum of {self.config.min_extracted_characters}."
            )

    @staticmethod
    def _metadata_field_count(metadata: LegalMetadata) -> int:
        values = (
            metadata.case_number,
            metadata.case_type,
            metadata.court,
            metadata.district,
            metadata.judges,
            metadata.parties,
            metadata.hearing_dates,
            metadata.judgment_date,
            metadata.citations,
        )
        return sum(bool(value) for value in values)

    @staticmethod
    def _validate_source(source: PathInput) -> Path:
        path = Path(source).expanduser()

        if not path.exists():
            raise FileNotFoundError(f"Document does not exist: {path}")
        if not path.is_file():
            raise UnsupportedDocumentError(f"Expected a file, received: {path}")
        if path.suffix.lower() != ".pdf":
            raise UnsupportedDocumentError(
                f"PDF input is currently required, received: {path.suffix or 'no extension'}"
            )
        return path

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
        return digest.hexdigest()

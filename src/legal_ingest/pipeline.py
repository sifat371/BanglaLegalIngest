"""Public document-ingestion pipeline."""

import hashlib
import time
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import TypeAlias

from legal_ingest.config import ExtractorName, PipelineConfig
from legal_ingest.encoding import process_extracted_content
from legal_ingest.exceptions import ExtractionError, LegalIngestError, UnsupportedDocumentError
from legal_ingest.extractors import DocumentExtractor, create_extractor
from legal_ingest.parsing import parse_legal_metadata
from legal_ingest.quality import assess_extraction_quality
from legal_ingest.schemas import (
    ExtractedContent,
    ExtractionDiagnostics,
    ExtractionQuality,
    IngestionResult,
    LegalDocument,
    LegalMetadata,
    RoutingAttempt,
)

PathInput: TypeAlias = str | Path


@dataclass(slots=True)
class _ExtractionSelection:
    content: ExtractedContent
    extractor_name: str
    fallback_used: bool
    warnings: list[str]
    quality: ExtractionQuality
    attempts: list[RoutingAttempt]


class LegalDocumentPipeline:
    """Coordinate extraction, quality routing, normalization, and metadata parsing."""

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
        selection = self._select_extraction(path)

        content, encoding = process_extracted_content(
            selection.content,
            convert_bijoy=self.config.convert_bijoy,
        )
        warnings = list(dict.fromkeys([*selection.warnings, *content.warnings]))

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
            extractor=selection.extractor_name,
            fallback_used=selection.fallback_used,
            processing_seconds=elapsed,
            quality=selection.quality,
            attempted_extractors=selection.attempts,
            quality_metrics={
                "page_count": float(len(content.pages)),
                "extracted_characters": float(len(content.text)),
                "extraction_usability_score": selection.quality.usability_score,
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

    def _select_extraction(self, path: Path) -> _ExtractionSelection:
        if self._custom_extractor is not None:
            content = self._custom_extractor.extract(path)
            self._require_minimum_text(content.text, self._custom_extractor.name)
            quality = assess_extraction_quality(content)
            attempt = self._successful_attempt(self._custom_extractor.name, content, quality)
            return _ExtractionSelection(
                content=content,
                extractor_name=self._custom_extractor.name,
                fallback_used=False,
                warnings=list(content.warnings),
                quality=quality,
                attempts=[attempt],
            )

        if self.config.extractor == "auto":
            return self._extract_auto(path)

        backend = create_extractor(self.config.extractor)
        content = backend.extract(path)
        self._require_minimum_text(content.text, backend.name)
        quality = assess_extraction_quality(content)
        attempt = self._successful_attempt(backend.name, content, quality)
        return _ExtractionSelection(
            content=content,
            extractor_name=backend.name,
            fallback_used=False,
            warnings=list(content.warnings),
            quality=quality,
            attempts=[attempt],
        )

    def _extract_auto(self, path: Path) -> _ExtractionSelection:
        names = ["pdfplumber", "pypdf"]
        if self.config.auto_docling_fallback:
            names.append("docling")

        attempts: list[RoutingAttempt] = []
        warnings: list[str] = []
        candidates: list[tuple[str, ExtractedContent, ExtractionQuality]] = []

        for name in names:
            try:
                backend = create_extractor(name)
                content = backend.extract(path)
            except LegalIngestError as exc:
                attempts.append(
                    RoutingAttempt(
                        extractor=name,
                        succeeded=False,
                        error=str(exc),
                    )
                )
                warnings.append(f"{name} unavailable or failed: {exc}")
                continue

            quality = assess_extraction_quality(content)
            attempts.append(self._successful_attempt(name, content, quality))

            enough_text = self._has_minimum_text(content.text)
            if enough_text:
                candidates.append((name, content, quality))

            if enough_text and quality.usability_score >= self.config.min_quality_score:
                return _ExtractionSelection(
                    content=content,
                    extractor_name=name,
                    fallback_used=name != names[0],
                    warnings=[*warnings, *content.warnings],
                    quality=quality,
                    attempts=attempts,
                )

            warnings.extend(content.warnings)
            if not enough_text:
                warnings.append(
                    f"{name} extracted {len(content.text.strip())} characters, below the "
                    f"configured minimum of {self.config.min_extracted_characters}."
                )
            else:
                warnings.append(
                    f"{name} extraction usability score "
                    f"{quality.usability_score:.3f} was below the configured threshold "
                    f"{self.config.min_quality_score:.3f}."
                )

        if candidates:
            name, content, quality = max(
                candidates,
                key=lambda candidate: candidate[2].usability_score,
            )
            warnings.append(
                "No automatic extractor met the configured usability threshold; "
                f"selected the best available candidate: {name} "
                f"({quality.usability_score:.3f})."
            )
            return _ExtractionSelection(
                content=content,
                extractor_name=name,
                fallback_used=name != names[0],
                warnings=list(dict.fromkeys([*warnings, *content.warnings])),
                quality=quality,
                attempts=attempts,
            )

        raise ExtractionError(
            "Automatic extraction failed: no configured backend produced the minimum "
            f"{self.config.min_extracted_characters} characters."
        )

    @staticmethod
    def _successful_attempt(
        name: str,
        content: ExtractedContent,
        quality: ExtractionQuality,
    ) -> RoutingAttempt:
        return RoutingAttempt(
            extractor=name,
            succeeded=True,
            extracted_characters=len(content.text),
            quality_score=quality.usability_score,
        )

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

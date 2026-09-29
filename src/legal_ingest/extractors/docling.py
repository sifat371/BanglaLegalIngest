"""Optional Docling extraction backend."""

from collections.abc import Callable
from pathlib import Path
from typing import Any

from legal_ingest.exceptions import ConfigurationError, ExtractionError
from legal_ingest.extractors.base import DocumentExtractor, combine_pages
from legal_ingest.schemas import ExtractedContent, PageContent


class DoclingExtractor(DocumentExtractor):
    """Extract page-aware Markdown through Docling.

    A converter factory can be injected for tests or advanced integrations. The default path
    imports Docling lazily so the base package does not require the heavy dependency.
    """

    name = "docling"

    def __init__(self, converter_factory: Callable[[], Any] | None = None) -> None:
        self._converter_factory = converter_factory

    def _create_converter(self) -> Any:
        if self._converter_factory is not None:
            return self._converter_factory()

        try:
            from docling.document_converter import DocumentConverter
        except ImportError as exc:
            raise ConfigurationError(
                'Docling is not installed. Install with: pip install -e ".[docling]"'
            ) from exc

        return DocumentConverter()

    def extract(self, path: Path) -> ExtractedContent:
        try:
            conversion_result = self._create_converter().convert(str(path))
            document = conversion_result.document
        except (ConfigurationError, ExtractionError):
            raise
        except Exception as exc:
            raise ExtractionError(f"Docling failed to convert {path.name}: {exc}") from exc

        raw_pages = getattr(document, "pages", None)
        if not raw_pages:
            raise ExtractionError(
                "Docling did not expose page metadata; Stage 2 refuses to discard provenance."
            )

        if isinstance(raw_pages, dict):
            page_numbers = sorted(int(page_number) for page_number in raw_pages)
        else:
            page_numbers = list(range(1, len(raw_pages) + 1))

        pages: list[PageContent] = []
        warnings: list[str] = []

        for page_number in page_numbers:
            try:
                text = document.export_to_markdown(page_no=page_number) or ""
            except TypeError as exc:
                raise ExtractionError(
                    "Installed Docling version does not support page-aware Markdown export."
                ) from exc
            except Exception as exc:
                raise ExtractionError(
                    f"Docling failed to export page {page_number} from {path.name}: {exc}"
                ) from exc

            if not text.strip():
                warnings.append(f"Page {page_number} contained no extractable text.")
            pages.append(PageContent(page_number=page_number, text=text))

        return ExtractedContent(
            pages=pages,
            text=combine_pages(pages),
            warnings=warnings,
        )

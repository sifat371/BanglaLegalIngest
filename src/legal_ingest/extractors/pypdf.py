"""pypdf extraction backend."""

from pathlib import Path

from legal_ingest.exceptions import ConfigurationError, ExtractionError
from legal_ingest.extractors.base import DocumentExtractor, combine_pages
from legal_ingest.schemas import ExtractedContent, PageContent


class PyPDFExtractor(DocumentExtractor):
    """Extract text page-by-page with pypdf."""

    name = "pypdf"

    def extract(self, path: Path) -> ExtractedContent:
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise ConfigurationError(
                'pypdf is not installed. Install with: pip install -e ".[manual]"'
            ) from exc

        pages: list[PageContent] = []
        warnings: list[str] = []

        try:
            reader = PdfReader(path)
            for page_number, page in enumerate(reader.pages, start=1):
                text = page.extract_text() or ""
                if not text.strip():
                    warnings.append(f"Page {page_number} contained no extractable text.")
                pages.append(PageContent(page_number=page_number, text=text))
        except Exception as exc:
            raise ExtractionError(f"pypdf failed to extract {path.name}: {exc}") from exc

        return ExtractedContent(
            pages=pages,
            text=combine_pages(pages),
            warnings=warnings,
        )

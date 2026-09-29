"""Common interface implemented by every extraction backend."""

from abc import ABC, abstractmethod
from pathlib import Path

from legal_ingest.schemas import ExtractedContent, PageContent


class DocumentExtractor(ABC):
    """Backend contract for page-aware document extraction."""

    name: str

    @abstractmethod
    def extract(self, path: Path) -> ExtractedContent:
        """Extract a PDF into backend-neutral page content."""


def combine_pages(pages: list[PageContent]) -> str:
    """Combine page text without inserting synthetic page markers."""

    return "\n\n".join(page.text.strip() for page in pages if page.text.strip())

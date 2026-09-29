"""Extractor backends and factory helpers."""

from legal_ingest.extractors.base import DocumentExtractor
from legal_ingest.extractors.docling import DoclingExtractor
from legal_ingest.extractors.pdfplumber import PdfPlumberExtractor
from legal_ingest.extractors.pypdf import PyPDFExtractor


def create_extractor(name: str) -> DocumentExtractor:
    """Create an extractor by stable backend name."""

    if name == "pdfplumber":
        return PdfPlumberExtractor()
    if name == "pypdf":
        return PyPDFExtractor()
    if name == "docling":
        return DoclingExtractor()
    raise ValueError(f"Unknown extractor: {name}")


__all__ = [
    "DocumentExtractor",
    "DoclingExtractor",
    "PdfPlumberExtractor",
    "PyPDFExtractor",
    "create_extractor",
]

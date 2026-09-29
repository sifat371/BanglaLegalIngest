"""Domain-specific exceptions for legal-document-ingestion."""


class LegalIngestError(Exception):
    """Base exception for the package."""


class ConfigurationError(LegalIngestError):
    """Raised when pipeline configuration cannot be honored."""


class ExtractionError(LegalIngestError):
    """Raised when document extraction fails."""


class EncodingDetectionError(LegalIngestError):
    """Raised when text encoding analysis fails."""


class MetadataParseError(LegalIngestError):
    """Raised when legal metadata parsing fails unexpectedly."""


class UnsupportedDocumentError(LegalIngestError):
    """Raised when an input document type is unsupported."""

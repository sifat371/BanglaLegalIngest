"""Bangla encoding detection and conservative Bijoy normalization."""

from legal_ingest.encoding.detector import (
    count_unicode_bangla,
    detect_encoding,
    is_bijoy_line,
    is_legacy_font_line,
)
from legal_ingest.encoding.normalizer import (
    BanglaEncodingNormalizer,
    process_extracted_content,
)

__all__ = [
    "BanglaEncodingNormalizer",
    "count_unicode_bangla",
    "detect_encoding",
    "is_bijoy_line",
    "is_legacy_font_line",
    "process_extracted_content",
]

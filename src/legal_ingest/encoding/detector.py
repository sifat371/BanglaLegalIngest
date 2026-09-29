"""Heuristic detection of Unicode Bangla and legacy Bijoy-like text."""

from legal_ingest.schemas import EncodingInfo, EncodingKind

BIJOY_LINE_MARKERS = frozenset("†‡¨©¯¶ÎïšŒ‰‹Š")

BIJOY_PATTERNS = (
    "Avgvi",
    "Av‡",
    "‡K",
    "Zvwi",
    "Kwi",
    "wQ",
    "gvbyl",
    "ivÎ",
    "UvKv",
    "FY",
    "AvBb",
    "Av`vjZ",
    "Avwg",
    "n‡q",
    "e‡j",
)


def count_unicode_bangla(text: str) -> int:
    """Count characters in the Bengali Unicode block."""

    return sum(1 for char in text if "\u0980" <= char <= "\u09ff")


def _marker_count(line: str) -> int:
    return sum(1 for char in line if char in BIJOY_LINE_MARKERS)


def _pattern_count(line: str) -> int:
    return sum(1 for pattern in BIJOY_PATTERNS if pattern in line)


def is_bijoy_line(line: str, *, marker_threshold: int = 2) -> bool:
    """Return whether a line is a conservative candidate for Bijoy conversion."""

    markers = _marker_count(line)
    patterns = _pattern_count(line)
    return markers >= marker_threshold or (markers >= 1 and patterns >= 1) or patterns >= 2


def count_bijoy_indicators(text: str) -> int:
    """Return a transparent indicator score retained for diagnostics."""

    marker_count = sum(1 for char in text if char in BIJOY_LINE_MARKERS)
    pattern_hits = sum(text.count(pattern) for pattern in BIJOY_PATTERNS)
    return marker_count + (10 * pattern_hits)


def detect_encoding(text: str) -> EncodingInfo:
    """Classify extracted source text before any normalization is applied."""

    unicode_count = count_unicode_bangla(text)
    indicator_count = count_bijoy_indicators(text)
    candidate_lines = sum(1 for line in text.splitlines() if is_bijoy_line(line))

    has_unicode = unicode_count > 0
    has_bijoy = candidate_lines > 0

    if has_unicode and has_bijoy:
        kind = EncodingKind.MIXED
    elif has_unicode:
        kind = EncodingKind.UNICODE_BANGLA
    elif has_bijoy:
        kind = EncodingKind.BIJOY
    else:
        kind = EncodingKind.NONE

    return EncodingInfo(
        kind=kind,
        has_bangla=has_unicode or has_bijoy,
        unicode_bangla_chars=unicode_count,
        bijoy_indicators=indicator_count,
        total_characters=len(text),
        bijoy_candidate_lines=candidate_lines,
    )

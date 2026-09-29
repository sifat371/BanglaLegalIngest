"""Heuristic detection of Unicode Bangla and legacy Bangla encodings."""

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
    "Av\x60vjZ",
    "Avwg",
    "n‡q",
    "e‡j",
)


def count_unicode_bangla(text: str) -> int:
    """Count characters in the Bengali Unicode block."""

    return sum(1 for char in text if "\u0980" <= char <= "\u09ff")


def _legacy_font_glyph_count(line: str) -> int:
    """Count extended glyphs commonly emitted by legacy Bangla PDF fonts."""

    return sum(1 for char in line if "\u00a1" <= char <= "\u024f")


def is_legacy_font_line(
    line: str,
    *,
    minimum_glyphs: int = 4,
    minimum_ratio: float = 0.06,
) -> bool:
    """Detect font-encoded Bangla that should not be sent to bijoy2unicode."""

    visible = [char for char in line if not char.isspace()]
    if not visible:
        return False

    glyph_count = _legacy_font_glyph_count(line)
    return glyph_count >= minimum_glyphs and glyph_count / len(visible) >= minimum_ratio


def _marker_count(line: str) -> int:
    return sum(1 for char in line if char in BIJOY_LINE_MARKERS)


def _pattern_count(line: str) -> int:
    return sum(1 for pattern in BIJOY_PATTERNS if pattern in line)


def is_bijoy_line(line: str, *, marker_threshold: int = 2) -> bool:
    """Return whether a line is a conservative standard-Bijoy conversion candidate."""

    if is_legacy_font_line(line):
        return False

    markers = _marker_count(line)
    patterns = _pattern_count(line)
    return markers >= marker_threshold or (markers >= 1 and patterns >= 1) or patterns >= 2


def count_bijoy_indicators(text: str) -> int:
    """Return a transparent legacy-Bangla indicator score for diagnostics."""

    marker_count = sum(1 for char in text if char in BIJOY_LINE_MARKERS)
    pattern_hits = sum(text.count(pattern) for pattern in BIJOY_PATTERNS)
    legacy_glyphs = sum(_legacy_font_glyph_count(line) for line in text.splitlines())
    return marker_count + (10 * pattern_hits) + legacy_glyphs


def detect_encoding(text: str) -> EncodingInfo:
    """Classify extracted source text before any normalization is applied."""

    unicode_count = count_unicode_bangla(text)
    indicator_count = count_bijoy_indicators(text)
    convertible_lines = sum(1 for line in text.splitlines() if is_bijoy_line(line))
    legacy_font_lines = sum(1 for line in text.splitlines() if is_legacy_font_line(line))
    candidate_lines = convertible_lines + legacy_font_lines

    has_unicode = unicode_count > 0
    has_convertible = convertible_lines > 0
    has_legacy_font = legacy_font_lines > 0
    has_legacy_bangla = has_convertible or has_legacy_font

    if has_unicode and has_legacy_bangla:
        kind = EncodingKind.MIXED
    elif has_convertible and has_legacy_font:
        kind = EncodingKind.MIXED
    elif has_legacy_font:
        kind = EncodingKind.LEGACY_FONT
    elif has_convertible:
        kind = EncodingKind.BIJOY
    elif has_unicode:
        kind = EncodingKind.UNICODE_BANGLA
    else:
        kind = EncodingKind.NONE

    return EncodingInfo(
        kind=kind,
        has_bangla=has_unicode or has_legacy_bangla,
        unicode_bangla_chars=unicode_count,
        bijoy_indicators=indicator_count,
        total_characters=len(text),
        bijoy_candidate_lines=candidate_lines,
        convertible_bijoy_lines=convertible_lines,
        legacy_font_candidate_lines=legacy_font_lines,
    )

"""Transparent metrics for deciding whether extracted text is usable."""

from legal_ingest.schemas import ExtractedContent, ExtractionQuality


def _safe_ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def assess_extraction_quality(content: ExtractedContent) -> ExtractionQuality:
    """Score extraction usability from observable text signals.

    The score is a routing heuristic, not a semantic correctness or legal-accuracy score.
    """

    page_count = len(content.pages)
    non_empty_pages = sum(bool(page.text.strip()) for page in content.pages)
    non_empty_page_ratio = _safe_ratio(non_empty_pages, page_count)

    text = content.text
    total_chars = len(text)

    printable_chars = sum(char.isprintable() or char in "\n\r\t" for char in text)
    printable_ratio = _safe_ratio(printable_chars, total_chars)

    replacement_count = text.count("\ufffd")
    replacement_char_ratio = _safe_ratio(replacement_count, total_chars)

    control_count = sum(
        not char.isprintable() and char not in "\n\r\t"
        for char in text
    )
    control_char_ratio = _safe_ratio(control_count, total_chars)

    average_chars_per_page = _safe_ratio(total_chars, page_count)
    density_component = min(average_chars_per_page / 500.0, 1.0)

    score = (
        0.45 * non_empty_page_ratio
        + 0.30 * printable_ratio
        + 0.25 * density_component
        - min(replacement_char_ratio * 5.0, 0.30)
        - min(control_char_ratio * 2.0, 0.20)
    )
    score = min(max(score, 0.0), 1.0)

    return ExtractionQuality(
        page_count=page_count,
        non_empty_page_ratio=non_empty_page_ratio,
        printable_ratio=printable_ratio,
        replacement_char_ratio=replacement_char_ratio,
        control_char_ratio=control_char_ratio,
        average_chars_per_page=average_chars_per_page,
        usability_score=score,
    )

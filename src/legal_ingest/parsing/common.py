"""Shared helpers for page-aware deterministic metadata parsers."""

import re
from collections.abc import Iterable, Iterator
from re import Match, Pattern

from legal_ingest.schemas import EvidenceSpan, PageContent


def normalize_space(value: str) -> str:
    """Collapse internal whitespace and trim surrounding punctuation/space."""

    return re.sub(r"\s+", " ", value).strip(" \t\r\n,;")


def iter_matches(
    pages: Iterable[PageContent],
    pattern: str | Pattern[str],
    *,
    flags: int = 0,
) -> Iterator[tuple[PageContent, Match[str]]]:
    """Yield regex matches in page order."""

    compiled = re.compile(pattern, flags) if isinstance(pattern, str) else pattern
    for page in pages:
        for match in compiled.finditer(page.text):
            yield page, match


def evidence_from_match(
    page: PageContent,
    match: Match[str],
    group: int | str = 0,
) -> EvidenceSpan:
    """Create an EvidenceSpan from a regex match/group."""

    start, end = match.span(group)
    return EvidenceSpan(
        page_number=page.page_number,
        text=match.group(group).strip(),
        start_char=start,
        end_char=end,
    )


def deduplicate(values: Iterable[str]) -> list[str]:
    """Preserve first-seen ordering while removing duplicates."""

    return list(dict.fromkeys(value for value in values if value))

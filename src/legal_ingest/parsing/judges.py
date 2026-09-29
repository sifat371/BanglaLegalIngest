"""Bench/judge parsing."""

import re

from legal_ingest.parsing.case import CASE_PATTERN
from legal_ingest.parsing.common import deduplicate, normalize_space
from legal_ingest.schemas import EvidenceSpan, PageContent

JUDGE_PATTERN = re.compile(
    r"(?:Mr\.|Ms\.)?\s*Justice\s+"
    r"(?P<name>.+?)"
    r"(?=\s+And\s+(?:Mr\.|Ms\.)?\s*Justice|"
    r"\s+(?:Death Reference|Criminal Appeal|Civil Appeal|Criminal Revision|"
    r"Civil Revision|Writ Petition|Jail Appeal)\b|[\r\n]|$)",
    re.IGNORECASE,
)
VERSUS_PATTERN = re.compile(r"(?:Versus|Vs\.?|V\.)", re.IGNORECASE)


def _caption_text(page: PageContent) -> str:
    """Restrict judge extraction to the caption before the case/party body."""

    candidate = page.text[:5000]
    boundaries: list[int] = []

    case_match = CASE_PATTERN.search(candidate)
    if case_match:
        boundaries.append(case_match.start())

    versus_match = VERSUS_PATTERN.search(candidate)
    if versus_match:
        boundaries.append(versus_match.start())

    if boundaries:
        return candidate[: min(boundaries)]
    return candidate[:1500]


def parse_judges(pages: list[PageContent]) -> tuple[list[str], list[EvidenceSpan]]:
    """Parse judge names from the first-page caption only."""

    if not pages:
        return [], []

    page = pages[0]
    caption = _caption_text(page)
    names: list[str] = []
    evidence: list[EvidenceSpan] = []

    for match in JUDGE_PATTERN.finditer(caption):
        name = normalize_space(match.group("name")).rstrip(".")
        if name in names:
            continue
        names.append(name)
        start, end = match.span("name")
        evidence.append(
            EvidenceSpan(
                page_number=page.page_number,
                text=match.group("name").strip(),
                start_char=start,
                end_char=end,
            )
        )

    return deduplicate(names)[:8], evidence[:8]

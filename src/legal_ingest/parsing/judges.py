"""Bench/judge parsing."""

import re

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


def parse_judges(pages: list[PageContent]) -> tuple[list[str], list[EvidenceSpan]]:
    """Parse judge names from the caption area of the first pages."""

    names: list[str] = []
    evidence: list[EvidenceSpan] = []

    for page in pages[:3]:
        caption = page.text[:5000]
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

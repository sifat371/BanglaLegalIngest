"""Court and district parsing."""

import re

from legal_ingest.parsing.common import evidence_from_match, iter_matches, normalize_space
from legal_ingest.schemas import EvidenceSpan, PageContent

COURT_PATTERN = re.compile(
    r"(Supreme Court of Bangladesh"
    r"(?:\s+(?:High Court|Appellate) Division)?"
    r"(?:\s*\([^)]+\))?)",
    re.IGNORECASE,
)
DISTRICT_PATTERN = re.compile(
    r"\bDistrict\s*:\s*(?P<district>[A-Za-z][A-Za-z .'-]{1,80}?)(?=\.|\n|$)",
    re.IGNORECASE,
)


def parse_court(pages: list[PageContent]) -> tuple[str | None, list[EvidenceSpan]]:
    for page, match in iter_matches(pages[:3], COURT_PATTERN):
        return normalize_space(match.group(1)), [evidence_from_match(page, match, 1)]
    return None, []


def parse_district(pages: list[PageContent]) -> tuple[str | None, list[EvidenceSpan]]:
    for page, match in iter_matches(pages[:3], DISTRICT_PATTERN):
        return normalize_space(match.group("district")).rstrip("."), [
            evidence_from_match(page, match, "district")
        ]
    return None, []

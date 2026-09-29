"""Case-number and case-type parsing."""

import re

from legal_ingest.parsing.common import evidence_from_match, iter_matches, normalize_space
from legal_ingest.schemas import EvidenceSpan, PageContent

CASE_TYPES = (
    "Death Reference",
    "Criminal Appeal",
    "Civil Appeal",
    "Criminal Revision",
    "Civil Revision",
    "Writ Petition",
    "Jail Appeal",
    "Sessions Case",
)

CASE_PATTERN = re.compile(
    rf"(?P<case_type>{'|'.join(re.escape(value) for value in CASE_TYPES)})"
    r"\s+No\.?\s*(?P<number>\d+)\s+of\s+(?P<year>\d{4})",
    re.IGNORECASE,
)


def parse_case_identity(
    pages: list[PageContent],
) -> tuple[str | None, str | None, list[EvidenceSpan]]:
    """Return the first caption-level case number/type and its evidence."""

    for page, match in iter_matches(pages[:3], CASE_PATTERN):
        case_number = normalize_space(match.group(0)).rstrip(".")
        raw_type = match.group("case_type")
        case_type = next(
            (value for value in CASE_TYPES if value.lower() == raw_type.lower()),
            normalize_space(raw_type),
        )
        return case_number, case_type, [evidence_from_match(page, match)]
    return None, None, []


def parse_case_type_only(
    pages: list[PageContent],
) -> tuple[str | None, list[EvidenceSpan]]:
    """Find a known case type when a full case number is unavailable."""

    pattern = re.compile(rf"\b({'|'.join(re.escape(value) for value in CASE_TYPES)})\b", re.I)
    for page, match in iter_matches(pages[:3], pattern):
        raw_type = match.group(1)
        case_type = next(
            (value for value in CASE_TYPES if value.lower() == raw_type.lower()),
            normalize_space(raw_type),
        )
        return case_type, [evidence_from_match(page, match, 1)]
    return None, []

"""Deterministic extraction of statute/section and reported-case citations."""

import re

from legal_ingest.parsing.common import deduplicate, normalize_space
from legal_ingest.schemas import EvidenceSpan, PageContent

REPORTED_CASE_PATTERN = re.compile(
    r"\b\d{1,4}\s+(?:DLR|BLC|BLD|MLR|ADC)"
    r"(?:\s*\([A-Za-z]+\))?\s+\d{1,4}\b",
    re.IGNORECASE,
)

STATUTE_PATTERN = re.compile(
    r"\bsections?\s+\d+(?:/\d+)*(?:\s*(?:,|and)\s*\d+(?:/\d+)*)*"
    r"\s+of\s+the\s+"
    r"(?:Code of Criminal Procedure(?:,\s*\d{4})?|CrPC|Penal Code|Evidence Act|"
    r"Constitution(?: of Bangladesh)?|Code of Civil Procedure(?:,\s*\d{4})?)",
    re.IGNORECASE,
)


def parse_citations(pages: list[PageContent]) -> tuple[list[str], list[EvidenceSpan]]:
    values: list[str] = []
    evidence: list[EvidenceSpan] = []

    for page in pages:
        for pattern in (REPORTED_CASE_PATTERN, STATUTE_PATTERN):
            for match in pattern.finditer(page.text):
                value = normalize_space(match.group(0)).rstrip(".,;")
                if value in values:
                    continue
                values.append(value)
                evidence.append(
                    EvidenceSpan(
                        page_number=page.page_number,
                        text=match.group(0).strip(),
                        start_char=match.start(),
                        end_char=match.end(),
                    )
                )

    return deduplicate(values), evidence

"""Hearing and judgment date parsing."""

import re

from legal_ingest.parsing.common import deduplicate, normalize_space
from legal_ingest.schemas import EvidenceSpan, PageContent

NUMERIC_DATE = r"\d{1,2}[./-]\d{1,2}[./-]\d{4}"
TEXTUAL_DATE = r"\d{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]{3,9}\s*(?:[-,/]\s*)?\d{4}"
DATE_TOKEN = rf"(?:{NUMERIC_DATE}|{TEXTUAL_DATE})"

HEARD_PREFIX = re.compile(r"\bHeard\s+On\b\s*:?", re.IGNORECASE)
JUDGMENT_PREFIX = re.compile(r"\b(?:And\s+)?Judgment\b", re.IGNORECASE)
JUDGMENT_PATTERN = re.compile(
    rf"\bJudgment(?:\s+Delivered)?\s+On\b\s*:?[\s\r\n]*(?P<date>{DATE_TOKEN})",
    re.IGNORECASE,
)
DATE_FINDER = re.compile(DATE_TOKEN, re.IGNORECASE)


def _normalized_date(value: str) -> str:
    return normalize_space(value)


def _hearing_window(text: str, start: int, *, max_chars: int = 300) -> tuple[str, int]:
    tail = text[start : start + max_chars]
    stop = len(tail)

    judgment_match = JUDGMENT_PREFIX.search(tail)
    if judgment_match:
        stop = min(stop, judgment_match.start())

    blank_line = re.search(r"\r?\n\s*\r?\n", tail)
    if blank_line:
        stop = min(stop, blank_line.start())

    return tail[:stop], start + stop


def parse_dates(
    pages: list[PageContent],
) -> tuple[list[str], str | None, list[EvidenceSpan], list[EvidenceSpan]]:
    """Parse common Supreme Court hearing/judgment date caption variants."""

    hearing_dates: list[str] = []
    hearing_evidence: list[EvidenceSpan] = []
    judgment_date: str | None = None
    judgment_evidence: list[EvidenceSpan] = []

    for page in pages[:5]:
        for prefix in HEARD_PREFIX.finditer(page.text):
            segment, absolute_end = _hearing_window(page.text, prefix.end())
            found_dates = [
                _normalized_date(match.group(0))
                for match in DATE_FINDER.finditer(segment)
            ]
            if not found_dates:
                continue

            hearing_dates.extend(found_dates)
            hearing_evidence.append(
                EvidenceSpan(
                    page_number=page.page_number,
                    text=page.text[prefix.start() : absolute_end].strip(),
                    start_char=prefix.start(),
                    end_char=absolute_end,
                )
            )

        if judgment_date is None:
            match = JUDGMENT_PATTERN.search(page.text)
            if match:
                judgment_date = _normalized_date(match.group("date"))
                judgment_evidence.append(
                    EvidenceSpan(
                        page_number=page.page_number,
                        text=match.group(0).strip(),
                        start_char=match.start(),
                        end_char=match.end(),
                    )
                )

    return deduplicate(hearing_dates), judgment_date, hearing_evidence, judgment_evidence

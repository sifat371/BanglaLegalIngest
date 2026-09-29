"""Hearing and judgment date parsing."""

import re

from legal_ingest.parsing.common import deduplicate
from legal_ingest.schemas import EvidenceSpan, PageContent

DATE_TOKEN = r"\d{1,2}[./-]\d{1,2}[./-]\d{4}"
HEARING_PATTERN = re.compile(rf"Heard\s+On\s*:\s*(?P<dates>[^\n]*{DATE_TOKEN}[^\n]*)", re.I)
JUDGMENT_PATTERN = re.compile(
    rf"Judgment\s+Delivered\s+On\s*:\s*(?P<date>{DATE_TOKEN})",
    re.I,
)
DATE_FINDER = re.compile(DATE_TOKEN)


def parse_dates(
    pages: list[PageContent],
) -> tuple[list[str], str | None, list[EvidenceSpan], list[EvidenceSpan]]:
    hearing_dates: list[str] = []
    hearing_evidence: list[EvidenceSpan] = []
    judgment_date: str | None = None
    judgment_evidence: list[EvidenceSpan] = []

    for page in pages[:5]:
        for match in HEARING_PATTERN.finditer(page.text):
            for date_match in DATE_FINDER.finditer(match.group("dates")):
                date = date_match.group(0)
                if date not in hearing_dates:
                    hearing_dates.append(date)
            hearing_evidence.append(
                EvidenceSpan(
                    page_number=page.page_number,
                    text=match.group(0).strip(),
                    start_char=match.start(),
                    end_char=match.end(),
                )
            )

        if judgment_date is None:
            match = JUDGMENT_PATTERN.search(page.text)
            if match:
                judgment_date = match.group("date")
                judgment_evidence.append(
                    EvidenceSpan(
                        page_number=page.page_number,
                        text=match.group(0).strip(),
                        start_char=match.start(),
                        end_char=match.end(),
                    )
                )

    return (
        deduplicate(hearing_dates),
        judgment_date,
        hearing_evidence,
        judgment_evidence,
    )

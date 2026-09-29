"""Caption party parsing without assigning unsupported legal roles."""

import re

from legal_ingest.parsing.common import normalize_space
from legal_ingest.schemas import EvidenceSpan, PageContent, Party

VERSUS_PATTERN = re.compile(
    r"[-\s\x00-\x1f]*(?:Versus|Vs\.?|V\.)[-\s\x00-\x1f]*",
    re.IGNORECASE,
)
ROLE_PATTERN = re.compile(r",?\s*-{2,}\s*(?P<role>[A-Za-z][A-Za-z -]+?)\.?$")
NUMBER_PREFIX = re.compile(r"^\s*\d+\.\s*")
PAREN_PREFIX = re.compile(r"^\s*\([^)]*\)\s*")

DISALLOWED_CONTEXT = (
    "justice ",
    "advocate",
    "attorney general",
    "for the ",
    "district:",
    "heard on:",
    "judgment delivered",
    "present:",
)

ROLE_ONLY_WORDS = {
    "accused",
    "appellant",
    "appellants",
    "condemned",
    "convict",
    "defendant",
    "informant",
    "opposite",
    "parties",
    "party",
    "petitioner",
    "petitioners",
    "plaintiff",
    "prisoner",
    "respondent",
    "respondents",
}


def _line_records(text: str) -> list[tuple[str, int, int]]:
    records: list[tuple[str, int, int]] = []
    offset = 0
    for raw in text.splitlines(keepends=True):
        content = raw.rstrip("\r\n")
        records.append((content, offset, offset + len(content)))
        offset += len(raw)
    if not records and text:
        records.append((text, 0, len(text)))
    return records


def _is_role_only(value: str) -> bool:
    words = re.findall(r"[A-Za-z]+", value.casefold())
    return bool(words) and all(word in ROLE_ONLY_WORDS for word in words)


def _is_party_candidate(value: str) -> bool:
    cleaned = normalize_space(value)
    if not cleaned or cleaned in {".", "-", "--"}:
        return False
    if _is_role_only(cleaned):
        return False
    if VERSUS_PATTERN.search(cleaned):
        return False

    lower = cleaned.lower()
    if any(marker in lower for marker in DISALLOWED_CONTEXT):
        return False
    if re.search(r"\b(?:No\.?\s*\d+\s+of\s+\d{4})\b", cleaned, re.I):
        return False
    return bool(re.search(r"[A-Za-z]", cleaned))


def _clean_party(value: str) -> Party | None:
    value = PAREN_PREFIX.sub("", value)
    value = NUMBER_PREFIX.sub("", value)
    value = normalize_space(value).strip(".- …")
    if not _is_party_candidate(value):
        return None

    role: str | None = None
    role_match = ROLE_PATTERN.search(value)
    if role_match:
        role = normalize_space(role_match.group("role")).strip(".- ")
        value = normalize_space(value[: role_match.start()]).strip(".- …")

    if not value or _is_role_only(value):
        return None
    return Party(name=value, role=role)


def _nearest_candidate(
    records: list[tuple[str, int, int]],
    start_index: int,
    step: int,
) -> tuple[str, int, int] | None:
    index = start_index
    checked = 0
    while 0 <= index < len(records) and checked < 6:
        line, start, end = records[index]
        if _is_party_candidate(line):
            return line, start, end
        index += step
        checked += 1
    return None


def parse_parties(pages: list[PageContent]) -> tuple[list[Party], list[EvidenceSpan]]:
    """Extract parties surrounding caption-level Versus/Vs markers."""

    parties: list[Party] = []
    evidence: list[EvidenceSpan] = []
    seen: set[tuple[str, str | None]] = set()

    for page in pages[:3]:
        records = _line_records(page.text)
        for index, (line, line_start, _line_end) in enumerate(records):
            match = VERSUS_PATTERN.search(line)
            if not match:
                continue

            left_raw = line[: match.start()].strip(" -")
            right_raw = line[match.end() :].strip(" -")

            if _is_party_candidate(left_raw):
                left_record = (left_raw, line_start, line_start + match.start())
            else:
                left_record = _nearest_candidate(records, index - 1, -1)

            if _is_party_candidate(right_raw):
                right_record = (right_raw, line_start + match.end(), line_start + len(line))
            else:
                right_record = _nearest_candidate(records, index + 1, 1)

            for record in (left_record, right_record):
                if record is None:
                    continue
                raw, start, end = record
                party = _clean_party(raw)
                if party is None:
                    continue
                key = (party.name.lower(), party.role.lower() if party.role else None)
                if key in seen:
                    continue
                seen.add(key)
                parties.append(party)
                evidence.append(
                    EvidenceSpan(
                        page_number=page.page_number,
                        text=raw.strip(),
                        start_char=start,
                        end_char=end,
                    )
                )

    return parties, evidence

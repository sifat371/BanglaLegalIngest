"""Input helpers for benchmark manifests and page-marked text fixtures."""

import json
import re
from pathlib import Path

from legal_ingest.schemas import PageContent

PAGE_MARKER = re.compile(r"^--- Page (?P<number>\d+) ---\s*$", re.MULTILINE)


def load_jsonl(path: str | Path) -> list[dict]:
    """Load non-empty JSONL records."""

    records: list[dict] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, start=1):
            line = raw.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL at {path}:{line_number}: {exc}") from exc
    return records


def parse_page_marked_text(text: str) -> list[PageContent]:
    """Parse legacy page markers into canonical page objects."""

    matches = list(PAGE_MARKER.finditer(text))
    if not matches:
        return [PageContent(page_number=1, text=text.strip())] if text.strip() else []

    pages: list[PageContent] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        page_text = text[start:end].strip("\r\n ")
        pages.append(
            PageContent(
                page_number=int(match.group("number")),
                text=page_text,
            )
        )
    return pages


def load_page_marked_file(path: str | Path) -> list[PageContent]:
    """Load a UTF-8 text fixture containing page markers."""

    return parse_page_marked_text(Path(path).read_text(encoding="utf-8"))

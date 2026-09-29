"""Human-readable Markdown export with page provenance."""

from pathlib import Path

from legal_ingest.schemas import IngestionResult


def _metadata_lines(result: IngestionResult) -> list[str]:
    metadata = result.document.metadata
    fields = [
        ("Case number", metadata.case_number),
        ("Case type", metadata.case_type),
        ("Court", metadata.court),
        ("District", metadata.district),
        ("Judges", ", ".join(metadata.judges) if metadata.judges else None),
        ("Hearing dates", ", ".join(metadata.hearing_dates) if metadata.hearing_dates else None),
        ("Judgment date", metadata.judgment_date),
    ]
    return [f"- **{label}:** {value}" for label, value in fields if value]


def to_markdown(result: IngestionResult) -> str:
    """Render a stable Markdown view of one ingestion result."""

    document = result.document
    lines = [
        f"# {document.source_filename}",
        "",
        "## Metadata",
        "",
    ]
    metadata_lines = _metadata_lines(result)
    lines.extend(metadata_lines or ["- No supported metadata fields were extracted."])

    if document.metadata.parties:
        lines.extend(["", "### Parties", ""])
        for party in document.metadata.parties:
            suffix = f" — {party.role}" if party.role else ""
            lines.append(f"- {party.name}{suffix}")

    if document.metadata.citations:
        lines.extend(["", "### Citations", ""])
        lines.extend(f"- {citation}" for citation in document.metadata.citations)

    lines.extend(
        [
            "",
            "## Extraction",
            "",
            f"- **Extractor:** {result.diagnostics.extractor}",
            f"- **Encoding:** {document.encoding.kind.value}",
        ]
    )
    if result.diagnostics.quality is not None:
        lines.append(
            f"- **Extraction usability score:** "
            f"{result.diagnostics.quality.usability_score:.3f}"
        )

    lines.extend(["", "## Pages", ""])

    if document.pages:
        for page in document.pages:
            lines.extend(
                [
                    f"### Page {page.page_number}",
                    "",
                    page.text,
                    "",
                ]
            )
    else:
        lines.extend(
            [
                "_Page payload was not retained. Full normalized text follows._",
                "",
                document.text,
                "",
            ]
        )

    return "\n".join(lines).rstrip() + "\n"


def write_markdown(result: IngestionResult, path: str | Path) -> Path:
    """Write a Markdown representation to an explicit path."""

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(to_markdown(result), encoding="utf-8")
    return output

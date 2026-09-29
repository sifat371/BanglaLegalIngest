"""Canonical JSON export."""

from pathlib import Path

from legal_ingest.schemas import IngestionResult


def to_json(result: IngestionResult, *, indent: int | None = 2) -> str:
    """Serialize an ingestion result using the canonical schema."""

    return result.model_dump_json(indent=indent)


def write_json(
    result: IngestionResult,
    path: str | Path,
    *,
    indent: int | None = 2,
) -> Path:
    """Write canonical UTF-8 JSON to an explicit path."""

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(to_json(result, indent=indent), encoding="utf-8")
    return output

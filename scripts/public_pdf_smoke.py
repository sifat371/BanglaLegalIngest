"""Smoke-test the ingestion pipeline against downloaded public court PDFs."""

import argparse
import json
from pathlib import Path

from legal_ingest import LegalDocumentPipeline, PipelineConfig, to_retrieval_chunks

CASES = [
    {
        "filename": "death_ref_106_2018.pdf",
        "expected_case_number": "Death Reference No 106 of 2018",
    },
    {
        "filename": "death_ref_117_2017.pdf",
        "expected_case_number": "Death Reference No.117 OF 2017",
    },
    {
        "filename": "civil_revision_205_2021.pdf",
        "expected_case_number": "Civil Revision No.205 of 2021",
    },
    {
        "filename": "criminal_appeal_3346_2022.pdf",
        "expected_case_number": "Criminal Appeal No. 3346 of 2022",
    },
]


def _normalize(value: str | None) -> str:
    if not value:
        return ""
    return " ".join(value.lower().replace(".", "").split())


def run(input_dir: Path) -> dict:
    pipeline = LegalDocumentPipeline(
        PipelineConfig(
            extractor="auto",
            min_extracted_characters=100,
            parse_metadata=True,
            preserve_page_text=True,
        )
    )

    records = []
    failures = []

    for case in CASES:
        path = input_dir / case["filename"]
        if not path.exists():
            failures.append(f"missing file: {path}")
            continue

        try:
            result = pipeline.ingest(path)
            chunks = to_retrieval_chunks(result.document)
        except Exception as exc:
            failures.append(f"{case['filename']}: {type(exc).__name__}: {exc}")
            continue

        metadata = result.document.metadata
        expected = case["expected_case_number"]
        record = {
            "filename": case["filename"],
            "file_bytes": path.stat().st_size,
            "extractor": result.diagnostics.extractor,
            "fallback_used": result.diagnostics.fallback_used,
            "attempts": [
                {
                    "extractor": attempt.extractor,
                    "succeeded": attempt.succeeded,
                    "characters": attempt.extracted_characters,
                    "quality_score": attempt.quality_score,
                    "error": attempt.error,
                }
                for attempt in result.diagnostics.attempted_extractors
            ],
            "page_count": len(result.document.pages),
            "characters": len(result.document.text),
            "quality_score": (
                result.diagnostics.quality.usability_score
                if result.diagnostics.quality
                else None
            ),
            "encoding": result.document.encoding.kind.value,
            "case_number": metadata.case_number,
            "expected_case_number": expected,
            "case_number_match": _normalize(metadata.case_number) == _normalize(expected),
            "case_type": metadata.case_type,
            "court": metadata.court,
            "district": metadata.district,
            "judges": metadata.judges,
            "parties": [party.model_dump() for party in metadata.parties],
            "hearing_dates": metadata.hearing_dates,
            "judgment_date": metadata.judgment_date,
            "citations_count": len(metadata.citations),
            "evidence_fields": sorted(metadata.evidence),
            "retrieval_chunks": len(chunks),
            "first_chunk": {
                "chunk_id": chunks[0].chunk_id,
                "page": chunks[0].page_start,
                "chars": [chunks[0].char_start, chunks[0].char_end],
            }
            if chunks
            else None,
            "warnings": result.diagnostics.warnings,
        }
        records.append(record)

        if not result.document.pages:
            failures.append(f"{case['filename']}: extracted no pages")
        if not result.document.text.strip():
            failures.append(f"{case['filename']}: extracted no text")
        if not chunks:
            failures.append(f"{case['filename']}: produced no retrieval chunks")

    return {
        "documents_requested": len(CASES),
        "documents_ingested": len(records),
        "case_number_matches": sum(record["case_number_match"] for record in records),
        "failures": failures,
        "documents": records,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    report = run(args.input_dir)
    rendered = json.dumps(report, indent=2, ensure_ascii=False)
    print(rendered)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")

    return 1 if report["failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

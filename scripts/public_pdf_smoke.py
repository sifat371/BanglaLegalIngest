"""Smoke-test the ingestion pipeline against downloaded public court PDFs."""

import argparse
import json
from pathlib import Path

from legal_ingest import LegalDocumentPipeline, PipelineConfig, to_retrieval_chunks
from legal_ingest.encoding import is_legacy_font_line

CASES = [
    {
        "filename": "death_ref_106_2018.pdf",
        "expected_case_number": "Death Reference No 106 of 2018",
        "expected_court": (
            "Supreme Court of Bangladesh High Court Division "
            "(Criminal Appellate Jurisdiction)"
        ),
        "expected_judges": ["Md Atoar Rahman", "S M Saiful Islam"],
        "expected_hearing_dates": ["09.12.2025", "14.12.2025", "15.12.2025"],
        "expected_judgment_date": "28.01.2026",
        "expected_parties": ["The State", "Md. Shafiqul Islam @ Shafique"],
    },
    {
        "filename": "death_ref_117_2017.pdf",
        "expected_case_number": "Death Reference No.117 OF 2017",
        "expected_court": (
            "SUPREME COURT OF BANGLADESH HIGH COURT DIVISION "
            "(CRIMINAL APPELLATE JURISDICTION)"
        ),
        "expected_judges": ["S M Kuddus Zaman", "Md. Aminul Islam"],
        "expected_hearing_dates": ["15.11.2023"],
        "expected_judgment_date": "23.11.2023",
        "expected_parties": ["The State", "Md. Enamul Haque"],
        "expected_encoding": "legacy_font_bangla",
        "minimum_legacy_font_lines": 5,
        "expect_no_unsafe_conversion": True,
    },
    {
        "filename": "civil_revision_205_2021.pdf",
        "expected_case_number": "Civil Revision No.205 of 2021",
        "expected_court": (
            "Supreme Court of Bangladesh High Court Division "
            "(Civil Revisional Jurisdiction)"
        ),
        "expected_judges": ["Md. Jahangir Hossain"],
        "expected_hearing_dates": ["21.04.2024"],
        "expected_judgment_date": "22nd April -2024",
        "expected_parties": ["Sham Debnath and others", "Shamol Debnath and others"],
    },
    {
        "filename": "criminal_appeal_3346_2022.pdf",
        "expected_case_number": "Criminal Appeal No. 3346 of 2022",
        "expected_court": (
            "SUPREME COURT OF BANGLADESH HIGH COURT DIVISION "
            "(CRIMINAL APPELATE JURISDICTION)"
        ),
        "expected_judges": ["Md. Shohrowardi"],
        "expected_hearing_dates": ["01.06.2025", "02.06.2025", "22.06.2025"],
        "expected_judgment_date": "17.07.2025",
        "expected_parties": ["Nurunnahar", "The State and another"],
    },
]

ROLE_ONLY_PARTIES = {
    "appellant",
    "convict appellant",
    "opposite parties",
    "petitioner",
    "respondent",
    "respondents",
}


def _normalize(value: str | None) -> str:
    if not value:
        return ""
    return " ".join(value.lower().replace(".", "").split())


def _normalized_list(values: list[str]) -> list[str]:
    return [_normalize(value) for value in values]


def _check_metadata(case: dict, result, failures: list[str]) -> dict:
    metadata = result.document.metadata
    filename = case["filename"]

    checks = {
        "case_number": _normalize(metadata.case_number)
        == _normalize(case["expected_case_number"]),
        "court": _normalize(metadata.court) == _normalize(case["expected_court"]),
        "judges": _normalized_list(metadata.judges)
        == _normalized_list(case["expected_judges"]),
        "hearing_dates": _normalized_list(metadata.hearing_dates)
        == _normalized_list(case["expected_hearing_dates"]),
        "judgment_date": _normalize(metadata.judgment_date)
        == _normalize(case["expected_judgment_date"]),
    }

    actual_parties = {_normalize(party.name) for party in metadata.parties}
    checks["parties"] = all(
        _normalize(expected) in actual_parties for expected in case["expected_parties"]
    )
    checks["no_role_only_parties"] = not any(
        _normalize(party.name) in ROLE_ONLY_PARTIES for party in metadata.parties
    )

    if "expected_encoding" in case:
        checks["encoding"] = result.document.encoding.kind.value == case["expected_encoding"]
    if "minimum_legacy_font_lines" in case:
        checks["legacy_font_detection"] = (
            result.document.encoding.legacy_font_candidate_lines
            >= case["minimum_legacy_font_lines"]
        )
    if case.get("expect_no_unsafe_conversion"):
        checks["no_unsafe_conversion"] = (
            result.document.encoding.normalization_applied is False
        )

    for name, passed in checks.items():
        if not passed:
            failures.append(f"{filename}: metadata check failed: {name}")

    return checks


def run(input_dir: Path) -> dict:
    pipeline = LegalDocumentPipeline(
        PipelineConfig(
            extractor="auto",
            min_extracted_characters=100,
            parse_metadata=True,
            preserve_page_text=True,
        )
    )
    no_conversion_pipeline = LegalDocumentPipeline(
        PipelineConfig(
            extractor="auto",
            min_extracted_characters=100,
            parse_metadata=True,
            preserve_page_text=True,
            convert_bijoy=False,
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
        checks = _check_metadata(case, result, failures)

        legacy_font_examples = [
            {
                "page": page.page_number,
                "text": line,
            }
            for page in result.document.pages
            for line in page.text.splitlines()
            if is_legacy_font_line(line)
        ][:3]

        normalization_differences = []
        if result.document.encoding.normalization_applied:
            source_result = no_conversion_pipeline.ingest(path)
            for source_page, normalized_page in zip(
                source_result.document.pages,
                result.document.pages,
                strict=True,
            ):
                source_lines = source_page.text.splitlines()
                normalized_lines = normalized_page.text.splitlines()
                for line_number, (source_line, normalized_line) in enumerate(
                    zip(source_lines, normalized_lines, strict=False),
                    start=1,
                ):
                    if source_line != normalized_line:
                        normalization_differences.append(
                            {
                                "page": source_page.page_number,
                                "line": line_number,
                                "source": source_line,
                                "normalized": normalized_line,
                            }
                        )
                        if len(normalization_differences) >= 5:
                            break
                if len(normalization_differences) >= 5:
                    break

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
            "unicode_bangla_chars": result.document.encoding.unicode_bangla_chars,
            "bijoy_indicators": result.document.encoding.bijoy_indicators,
            "bijoy_candidate_lines": result.document.encoding.bijoy_candidate_lines,
            "convertible_bijoy_lines": result.document.encoding.convertible_bijoy_lines,
            "legacy_font_candidate_lines": (
                result.document.encoding.legacy_font_candidate_lines
            ),
            "legacy_font_examples": legacy_font_examples,
            "normalization_applied": result.document.encoding.normalization_applied,
            "converted_lines": result.document.encoding.converted_lines,
            "conversion_failures": result.document.encoding.conversion_failures,
            "normalization_differences": normalization_differences,
            "case_number": metadata.case_number,
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
            "checks": checks,
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

    checks_total = sum(len(record["checks"]) for record in records)
    checks_passed = sum(
        sum(bool(value) for value in record["checks"].values())
        for record in records
    )

    return {
        "documents_requested": len(CASES),
        "documents_ingested": len(records),
        "checks_passed": checks_passed,
        "checks_total": checks_total,
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

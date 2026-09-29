"""Benchmark runners for metadata parsing and encoding classification."""

from collections import defaultdict
from pathlib import Path
from typing import Any

from legal_ingest.benchmarking.io import load_jsonl, load_page_marked_file
from legal_ingest.benchmarking.metrics import exact_match, safe_mean
from legal_ingest.encoding import detect_encoding
from legal_ingest.parsing import parse_legal_metadata

SUPPORTED_METADATA_FIELDS = {
    "case_number",
    "case_type",
    "court",
    "district",
    "judges",
    "hearing_dates",
    "judgment_date",
    "citations",
}


def _predicted_metadata_value(metadata, field: str):
    if field not in SUPPORTED_METADATA_FIELDS:
        raise ValueError(f"Unsupported benchmark metadata field: {field}")
    return getattr(metadata, field)


def run_metadata_benchmark(
    manifest_path: str | Path,
    *,
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    """Run normalized exact-match evaluation over selected metadata fields."""

    manifest_path = Path(manifest_path)
    repo_root = Path(repo_root)
    cases = load_jsonl(manifest_path)

    field_totals: dict[str, int] = defaultdict(int)
    field_correct: dict[str, int] = defaultdict(int)
    evidence_total = 0
    evidence_present = 0
    exact_cases = 0
    details: list[dict[str, Any]] = []

    for case in cases:
        source_path = repo_root / case["source_path"]
        pages = load_page_marked_file(source_path)
        metadata = parse_legal_metadata(pages)
        expected = case["expected"]

        case_exact = True
        field_results: dict[str, bool] = {}

        for field, expected_value in expected.items():
            predicted_value = _predicted_metadata_value(metadata, field)
            matched = exact_match(predicted_value, expected_value)
            field_results[field] = matched
            field_totals[field] += 1
            field_correct[field] += int(matched)
            case_exact = case_exact and matched

            if expected_value not in (None, "", []):
                evidence_total += 1
                if metadata.evidence.get(field):
                    evidence_present += 1

        exact_cases += int(case_exact)
        details.append(
            {
                "id": case["id"],
                "source_kind": case.get("source_kind", "unspecified"),
                "exact": case_exact,
                "fields": field_results,
            }
        )

    field_metrics = {
        field: {
            "evaluated": field_totals[field],
            "correct": field_correct[field],
            "accuracy": field_correct[field] / field_totals[field],
        }
        for field in sorted(field_totals)
    }

    return {
        "dataset": manifest_path.name,
        "cases": len(cases),
        "field_metrics": field_metrics,
        "macro_field_accuracy": safe_mean(
            metric["accuracy"] for metric in field_metrics.values()
        ),
        "exact_case_rate": exact_cases / len(cases) if cases else 0.0,
        "evidence_coverage": evidence_present / evidence_total if evidence_total else 0.0,
        "details": details,
    }


def run_encoding_benchmark(manifest_path: str | Path) -> dict[str, Any]:
    """Evaluate source-encoding classification on labeled text snippets."""

    manifest_path = Path(manifest_path)
    cases = load_jsonl(manifest_path)
    correct = 0
    details: list[dict[str, Any]] = []

    for case in cases:
        prediction = detect_encoding(case["text"])
        expected_kind = case["expected_kind"]
        matched = prediction.kind.value == expected_kind
        correct += int(matched)
        details.append(
            {
                "id": case["id"],
                "source_kind": case.get("source_kind", "unspecified"),
                "expected_kind": expected_kind,
                "predicted_kind": prediction.kind.value,
                "correct": matched,
            }
        )

    return {
        "dataset": manifest_path.name,
        "cases": len(cases),
        "correct": correct,
        "accuracy": correct / len(cases) if cases else 0.0,
        "details": details,
    }


def run_seed_benchmarks(
    *,
    repo_root: str | Path = ".",
    metadata_manifest: str | Path = "benchmarks/gold/metadata_seed.jsonl",
    encoding_manifest: str | Path = "benchmarks/gold/encoding_seed.jsonl",
) -> dict[str, Any]:
    """Run the committed seed benchmark suite."""

    repo_root = Path(repo_root)
    return {
        "metadata": run_metadata_benchmark(
            repo_root / metadata_manifest,
            repo_root=repo_root,
        ),
        "encoding": run_encoding_benchmark(repo_root / encoding_manifest),
        "limitations": [
            "The committed metadata seed contains one repository sample judgment.",
            "The committed encoding seed is a synthetic characterization set.",
            "These seed results are regression checks, not representative corpus accuracy.",
            "No real-PDF extraction benchmark is reported because raw benchmark PDFs are not "
            "committed to this repository.",
        ],
    }

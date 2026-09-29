from pathlib import Path

from legal_ingest.benchmarking import (
    parse_page_marked_text,
    run_encoding_benchmark,
    run_metadata_benchmark,
    run_seed_benchmarks,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_page_marked_sample_is_split_into_real_pages() -> None:
    text = (REPO_ROOT / "samples/sample_output_pdfplumber.txt").read_text(encoding="utf-8")
    pages = parse_page_marked_text(text)

    assert len(pages) >= 10
    assert pages[0].page_number == 1
    assert "District: Brahmanbaria" in pages[0].text
    assert pages[1].page_number == 2
    assert "Judgment Delivered On: 08.02.2026" in pages[1].text


def test_metadata_seed_matches_verified_fields() -> None:
    report = run_metadata_benchmark(
        REPO_ROOT / "benchmarks/gold/metadata_seed.jsonl",
        repo_root=REPO_ROOT,
    )

    assert report["cases"] == 1
    assert report["macro_field_accuracy"] == 1.0
    assert report["exact_case_rate"] == 1.0
    assert report["evidence_coverage"] == 1.0


def test_encoding_seed_characterizes_detector_behavior() -> None:
    report = run_encoding_benchmark(
        REPO_ROOT / "benchmarks/gold/encoding_seed.jsonl"
    )

    assert report["cases"] == 5
    assert report["accuracy"] == 1.0


def test_combined_seed_report_states_limitations() -> None:
    report = run_seed_benchmarks(repo_root=REPO_ROOT)

    assert report["metadata"]["cases"] == 1
    assert report["encoding"]["cases"] == 5
    assert report["limitations"]

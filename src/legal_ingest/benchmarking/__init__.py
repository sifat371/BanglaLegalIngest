"""Benchmark helpers for measured validation."""

from legal_ingest.benchmarking.io import parse_page_marked_text
from legal_ingest.benchmarking.runner import (
    run_encoding_benchmark,
    run_metadata_benchmark,
    run_seed_benchmarks,
)

__all__ = [
    "parse_page_marked_text",
    "run_encoding_benchmark",
    "run_metadata_benchmark",
    "run_seed_benchmarks",
]

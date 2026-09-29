"""Command-line interface backed by the same public package APIs."""

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from legal_ingest import LegalDocumentPipeline, PipelineConfig, __version__
from legal_ingest.benchmarking import run_seed_benchmarks
from legal_ingest.exporters import (
    chunks_to_jsonl,
    to_json,
    to_markdown,
    to_retrieval_chunks,
)
from legal_ingest.schemas import IngestionResult, LegalDocument


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="legal-ingest",
        description="Reusable ingestion primitives for Bangladesh legal documents.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command")

    schema_parser = subparsers.add_parser(
        "schema",
        help="Print the canonical JSON schema used by downstream systems.",
    )
    schema_parser.add_argument(
        "--model",
        choices=("document", "result"),
        default="result",
        help="Schema to print.",
    )

    ingest_parser = subparsers.add_parser(
        "ingest",
        help="Extract one PDF and render a canonical export.",
    )
    ingest_parser.add_argument("source", help="Path to a PDF file.")
    ingest_parser.add_argument(
        "--extractor",
        choices=("auto", "pdfplumber", "pypdf", "docling"),
        default="auto",
        help="Extraction backend.",
    )
    ingest_parser.add_argument(
        "--min-chars",
        type=int,
        default=100,
        help="Minimum extracted non-whitespace characters required for success.",
    )
    ingest_parser.add_argument(
        "--min-quality",
        type=float,
        default=0.65,
        help="Automatic-routing usability threshold between 0 and 1.",
    )
    ingest_parser.add_argument(
        "--auto-docling",
        action="store_true",
        help="Allow auto mode to try optional Docling after lightweight extractors.",
    )
    ingest_parser.add_argument(
        "--no-convert-bijoy",
        action="store_true",
        help="Detect source encoding but preserve candidate Bijoy text unchanged.",
    )
    ingest_parser.add_argument(
        "--no-metadata",
        action="store_true",
        help="Skip deterministic legal metadata parsing.",
    )
    ingest_parser.add_argument(
        "--format",
        choices=("json", "markdown", "chunks"),
        default="json",
        help="Output representation.",
    )
    ingest_parser.add_argument(
        "--output",
        help="Optional output file. Without this option the export is printed.",
    )
    ingest_parser.add_argument(
        "--chunk-size",
        type=int,
        default=1000,
        help="Maximum characters per retrieval chunk.",
    )
    ingest_parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=150,
        help="Character overlap between retrieval chunks.",
    )
    ingest_parser.add_argument(
        "--compact",
        action="store_true",
        help="Print compact JSON instead of indented JSON.",
    )

    benchmark_parser = subparsers.add_parser(
        "benchmark",
        help="Run the committed metadata and encoding seed validations.",
    )
    benchmark_parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root used to resolve benchmark source paths.",
    )
    benchmark_parser.add_argument(
        "--metadata",
        default="benchmarks/gold/metadata_seed.jsonl",
        help="Metadata benchmark manifest path relative to repo root.",
    )
    benchmark_parser.add_argument(
        "--encoding",
        default="benchmarks/gold/encoding_seed.jsonl",
        help="Encoding benchmark manifest path relative to repo root.",
    )
    benchmark_parser.add_argument(
        "--output",
        help="Optional JSON report path. Without this option the report is printed.",
    )
    return parser


def _render_result(args, result: IngestionResult) -> str:
    if args.format == "markdown":
        return to_markdown(result)
    if args.format == "chunks":
        chunks = to_retrieval_chunks(
            result.document,
            chunk_size=args.chunk_size,
            overlap=args.chunk_overlap,
        )
        return chunks_to_jsonl(chunks)
    return to_json(result, indent=None if args.compact else 2)


def _write_or_print(rendered: str, output_path: str | None) -> None:
    if output_path:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="" if rendered.endswith("\n") else "\n")


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "schema":
        model = LegalDocument if args.model == "document" else IngestionResult
        print(json.dumps(model.model_json_schema(), indent=2, ensure_ascii=False))
        return 0

    if args.command == "ingest":
        config = PipelineConfig(
            extractor=args.extractor,
            min_extracted_characters=args.min_chars,
            min_quality_score=args.min_quality,
            auto_docling_fallback=args.auto_docling,
            convert_bijoy=not args.no_convert_bijoy,
            parse_metadata=not args.no_metadata,
        )
        result = LegalDocumentPipeline(config).ingest(args.source)
        _write_or_print(_render_result(args, result), args.output)
        return 0

    if args.command == "benchmark":
        report = run_seed_benchmarks(
            repo_root=args.repo_root,
            metadata_manifest=args.metadata,
            encoding_manifest=args.encoding,
        )
        rendered = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
        _write_or_print(rendered, args.output)
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Command-line interface backed by the same public pipeline API."""

import argparse
import json
from collections.abc import Sequence

from legal_ingest import LegalDocumentPipeline, PipelineConfig, __version__
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
        help="Extract one PDF and print the canonical ingestion result as JSON.",
    )
    ingest_parser.add_argument("source", help="Path to a PDF file.")
    ingest_parser.add_argument(
        "--extractor",
        choices=("auto", "pdfplumber", "pypdf", "docling"),
        default="auto",
        help="Extraction backend. Auto currently uses pdfplumber with pypdf fallback.",
    )
    ingest_parser.add_argument(
        "--min-chars",
        type=int,
        default=100,
        help="Minimum extracted non-whitespace characters required for success.",
    )
    ingest_parser.add_argument(
        "--compact",
        action="store_true",
        help="Print compact JSON instead of indented JSON.",
    )
    return parser


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
        )
        result = LegalDocumentPipeline(config).ingest(args.source)
        indent = None if args.compact else 2
        print(result.model_dump_json(indent=indent))
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

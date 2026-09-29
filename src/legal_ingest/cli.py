"""Command-line entry point for package inspection during Stage 1."""

import argparse
import json
from collections.abc import Sequence

from legal_ingest import __version__
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
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "schema":
        model = LegalDocument if args.model == "document" else IngestionResult
        print(json.dumps(model.model_json_schema(), indent=2, ensure_ascii=False))
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

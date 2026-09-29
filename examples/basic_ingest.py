"""Minimal legal_ingest example."""

from pathlib import Path

from legal_ingest import LegalDocumentPipeline


def main() -> None:
    pdf_path = Path("judgment.pdf")

    result = LegalDocumentPipeline().ingest(pdf_path)

    print(f"source: {result.document.source_filename}")
    print(f"extractor: {result.diagnostics.extractor}")
    print(f"pages: {len(result.document.pages)}")
    print(f"case: {result.document.metadata.case_number}")
    print(f"court: {result.document.metadata.court}")
    print(f"encoding: {result.document.encoding.kind.value}")

    if result.diagnostics.warnings:
        print("warnings:")
        for warning in result.diagnostics.warnings:
            print(f"- {warning}")


if __name__ == "__main__":
    main()

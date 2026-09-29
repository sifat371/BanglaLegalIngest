"""Create provenance-aware JSONL retrieval chunks from one legal PDF."""

from pathlib import Path

from legal_ingest import (
    LegalDocumentPipeline,
    to_retrieval_chunks,
    write_chunks_jsonl,
)


def main() -> None:
    pdf_path = Path("judgment.pdf")
    output_path = Path("chunks.jsonl")

    result = LegalDocumentPipeline().ingest(pdf_path)
    chunks = to_retrieval_chunks(
        result.document,
        chunk_size=1000,
        overlap=150,
    )
    write_chunks_jsonl(chunks, output_path)

    print(f"wrote {len(chunks)} chunks to {output_path}")


if __name__ == "__main__":
    main()

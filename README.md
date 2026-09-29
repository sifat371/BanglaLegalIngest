# Legal Document Ingestion

A reusable Python module for page-aware ingestion of multilingual Bangladesh legal PDFs, including
quality-aware extraction routing, legacy Bijoy normalization, deterministic legal metadata
extraction, provenance, and retrieval-ready exports.

> Status: Stage 5 implemented. The module contract needed by downstream retrieval systems is now in
> place. Benchmarking and measured validation remain before a stable release.

## Pipeline

~~~text
PDF
 |
 v
quality-aware extraction
 |-- pdfplumber
 |-- pypdf
 |-- optional Docling fallback
 |
 v
page-aware text
 |
 v
Bangla/Bijoy detection + selective normalization
 |
 v
legal metadata + evidence provenance
 |
 v
LegalDocument
 |
 +-- JSON
 +-- Markdown
 +-- page-grounded RetrievalChunk[]
~~~

## Install

Lightweight extraction:

~~~bash
python -m pip install -e ".[manual]"
~~~

Add Bijoy conversion:

~~~bash
python -m pip install -e ".[manual,bangla]"
~~~

Development:

~~~bash
python -m pip install -e ".[manual,bangla,dev]"
~~~

Docling remains optional:

~~~bash
python -m pip install -e ".[docling,bangla]"
~~~

## Python API

~~~python
from legal_ingest import LegalDocumentPipeline, to_retrieval_chunks

result = LegalDocumentPipeline().ingest("judgment.pdf")

print(result.document.metadata.case_number)
print(result.diagnostics.extractor)
print(result.diagnostics.quality.usability_score)

chunks = to_retrieval_chunks(
    result.document,
    chunk_size=1000,
    overlap=150,
)
~~~

Each retrieval chunk carries source-document identity, source page, exact character offsets, and
selected legal metadata.

## CLI

Canonical JSON:

~~~bash
legal-ingest ingest judgment.pdf
~~~

Markdown:

~~~bash
legal-ingest ingest judgment.pdf --format markdown
~~~

Retrieval JSONL:

~~~bash
legal-ingest ingest judgment.pdf --format chunks --output chunks.jsonl
~~~

Allow the heavier optional Docling backend during automatic routing:

~~~bash
legal-ingest ingest judgment.pdf --auto-docling
~~~

## Quality routing

Auto mode assesses extraction usability from non-empty-page coverage, printable characters,
replacement/control characters, and text density. This score is a routing heuristic only; it is
not a measure of legal correctness.

By default, pdfplumber is tried first and pypdf is tried when needed. Docling is an explicit opt-in
fallback because it is heavier.

See docs/quality-routing.md.

## Export contracts

The module provides:

- canonical IngestionResult JSON;
- Markdown with source-page headings;
- deterministic page-local RetrievalChunk objects;
- JSONL chunk export.

See docs/exporters.md and docs/law_buddy_integration.md.

## Known limitations

- PDF input only;
- scanned/image-only PDFs are not yet an OCR baseline;
- quality-routing weights and thresholds are heuristic until benchmarked;
- metadata patterns emphasize common English-language Bangladesh court layouts;
- Bangla caption metadata needs dedicated patterns;
- retrieval chunks are page-local by design;
- no benchmark accuracy numbers are claimed yet.

## Roadmap

1. Package foundation — complete.
2. Unified extraction — complete.
3. Bangla encoding layer — complete, benchmark pending.
4. Legal metadata parsing with provenance — complete, benchmark pending.
5. Quality routing and exporters — implemented.
6. Benchmarking — manually verified gold sets and published metrics.

The original manual_ingestion/ and docling_ingestion/ directories remain for historical
comparison until the migration is complete.

## License

MIT. See LICENSE.

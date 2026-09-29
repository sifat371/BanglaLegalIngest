# Legal Document Ingestion

A reusable Python module for page-aware ingestion of multilingual Bangladesh legal PDFs, including
quality-aware extraction routing, legacy Bijoy normalization, deterministic legal metadata
extraction, provenance, retrieval-ready exports, and executable regression validation.

> Status: Stage 6 validation infrastructure is implemented. The module API is usable downstream,
> but the committed benchmark seed is intentionally small and is not a representative accuracy
> claim.

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
 |
 v
benchmark regression checks
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

Run the committed regression validation:

~~~bash
legal-ingest benchmark
~~~

## Validation scope

The Stage 6 benchmark harness currently evaluates selected metadata fields from one manually
verified repository sample and encoding behavior on a five-case synthetic characterization set.

These results are regression checks only. The repository does not yet contain a sufficiently broad
manually reviewed corpus for general metadata-accuracy claims, nor the raw PDFs required for a
real extraction-fidelity benchmark.

See benchmarks/README.md and docs/benchmarking.md.

## Law Buddy boundary

legal-document-ingestion owns extraction, normalization, metadata, provenance, quality diagnostics,
and retrieval-chunk creation. Law Buddy should own indexing, embeddings, retrieval/ranking, answer
generation, and citation verification.

See docs/law_buddy_integration.md.

## Known limitations

- PDF input only;
- scanned/image-only PDFs are not yet an OCR baseline;
- quality-routing weights and thresholds are heuristic until evaluated on a broader corpus;
- metadata patterns emphasize common English-language Bangladesh court layouts;
- Bangla caption metadata needs dedicated patterns;
- retrieval chunks are page-local by design;
- committed validation data is too small for representative performance claims.

## Roadmap status

1. Package foundation — complete.
2. Unified extraction — complete.
3. Bangla encoding layer — complete.
4. Legal metadata parsing with provenance — complete.
5. Quality routing and exporters — complete.
6. Benchmark harness and seed validation — implemented; corpus expansion remains.

The original manual_ingestion/ and docling_ingestion/ directories remain for historical comparison
until the migration is complete.

## License

MIT. See LICENSE.

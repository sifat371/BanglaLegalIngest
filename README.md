# Legal Document Ingestion

[![CI](https://github.com/sifat371/legal-document-ingestion/actions/workflows/ci.yml/badge.svg)](https://github.com/sifat371/legal-document-ingestion/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](pyproject.toml)
[![Status: Alpha](https://img.shields.io/badge/status-alpha-orange.svg)](CHANGELOG.md)

A reusable Python toolkit for ingesting multilingual Bangladesh legal PDFs into page-aware,
provenance-preserving document objects and retrieval-ready chunks.

The package is designed for legal search, RAG, document analysis, research pipelines, and other
systems that need a stable ingestion layer instead of one-off PDF scripts.

> **Project status:** public alpha. The API is usable and covered by automated tests, but the
> benchmark corpus is still small and some Bangladesh-specific document variants remain unsupported.

## What it does

- extracts page-aware text with **pdfplumber**, **pypdf**, or optional **Docling**;
- routes between lightweight extractors using transparent extraction-usability signals;
- detects Unicode Bangla, standard Bijoy-like text, and legacy PDF-font Bangla;
- converts conservative standard-Bijoy candidates to Unicode when supported;
- preserves unsafe legacy-font glyph text instead of silently corrupting it;
- parses common Bangladesh legal metadata such as case number, court, judges, parties, and dates;
- records page-relative evidence for extracted metadata;
- exports canonical JSON, human-readable Markdown, and retrieval-ready JSONL chunks;
- provides deterministic chunk IDs, page provenance, and character offsets for downstream RAG;
- includes executable seed benchmarks and real-public-PDF smoke validation.

## Why this exists

Bangladesh legal PDFs are not uniform. A single corpus may contain English, Unicode Bangla,
legacy Bijoy-like text, older font-encoded Bangla, inconsistent court captions, connected appeals,
and different text extraction quality across PDF libraries.

This project turns those concerns into a reusable module with explicit schemas and diagnostics:

```text
PDF
 |
 v
quality-aware extraction
 |-- pdfplumber
 |-- pypdf
 |-- Docling (optional)
 |
 v
page-aware text
 |
 v
Bangla / legacy-encoding analysis
 |
 v
deterministic legal metadata parsing
 |
 v
LegalDocument
 |
 +-- JSON
 +-- Markdown
 +-- RetrievalChunk[]
```

## Quick start

### 1. Clone and install

Until the first PyPI release is published, install from source:

```bash
git clone https://github.com/sifat371/legal-document-ingestion.git
cd legal-document-ingestion

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

python -m pip install --upgrade pip
python -m pip install ".[manual,bangla]"
```

Python **3.11+** is required.

### 2. Ingest a PDF

```python
from legal_ingest import LegalDocumentPipeline

result = LegalDocumentPipeline().ingest("judgment.pdf")

print(result.document.source_filename)
print(result.document.metadata.case_number)
print(result.document.metadata.court)
print(result.document.metadata.judges)
print(result.document.encoding.kind)
print(result.diagnostics.extractor)
```

### 3. Create retrieval chunks

```python
from legal_ingest import LegalDocumentPipeline, to_retrieval_chunks

result = LegalDocumentPipeline().ingest("judgment.pdf")

chunks = to_retrieval_chunks(
    result.document,
    chunk_size=1000,
    overlap=150,
)

for chunk in chunks[:3]:
    print(chunk.chunk_id, chunk.page_start, chunk.text[:120])
```

Each chunk retains the source document ID, page number, exact page-relative character offsets, and
selected legal metadata.

## CLI

Canonical JSON:

```bash
legal-ingest ingest judgment.pdf
```

Markdown:

```bash
legal-ingest ingest judgment.pdf --format markdown
```

Retrieval chunks as JSONL:

```bash
legal-ingest ingest judgment.pdf \
  --format chunks \
  --output chunks.jsonl
```

Use a specific extractor:

```bash
legal-ingest ingest judgment.pdf --extractor pypdf
```

Allow optional Docling during automatic routing:

```bash
python -m pip install ".[docling,bangla]"
legal-ingest ingest judgment.pdf --auto-docling
```

Run the committed regression validation:

```bash
legal-ingest benchmark
```

## Output model

The public API returns an `IngestionResult` containing a canonical `LegalDocument` and extraction
diagnostics.

A simplified result looks like this:

```json
{
  "document": {
    "document_id": "<sha256>",
    "source_filename": "judgment.pdf",
    "metadata": {
      "case_number": "Criminal Appeal No. 3346 of 2022",
      "court": "SUPREME COURT OF BANGLADESH HIGH COURT DIVISION",
      "judges": ["Md. Shohrowardi"],
      "parties": [],
      "hearing_dates": ["01.06.2025", "02.06.2025", "22.06.2025"],
      "judgment_date": "17.07.2025"
    },
    "pages": [
      {
        "page_number": 1,
        "text": "..."
      }
    ]
  },
  "diagnostics": {
    "extractor": "pdfplumber",
    "fallback_used": false,
    "warnings": []
  }
}
```

See [Public API](docs/public-api.md) for the stable object boundary used by downstream systems.

## Validation

The repository uses three different levels of validation:

| Validation | Current scope |
| --- | --- |
| Unit/integration suite | 49 tests after the latest real-PDF fixes |
| Committed metadata seed | 1 manually verified sample judgment / 7 scored fields |
| Committed encoding seed | 5 characterization cases |
| Public-PDF smoke test | 4 Bangladesh Supreme Court judgments / 31 explicit checks |

The latest completed public-PDF smoke validation ingested all four documents, created
page-grounded retrieval chunks for every document, and passed **31/31 explicit checks**. Those checks
cover selected metadata fields and safety behavior; they are **not** a statistically representative
accuracy estimate.

See [Validation Results](benchmarks/RESULTS.md), [Benchmarking](docs/benchmarking.md), and
[Public PDF Smoke Test](docs/public-pdf-smoke.md).

## Bangla and legacy-font behavior

The package distinguishes:

- `unicode_bangla` — already-valid Unicode Bangla;
- `bijoy` — conservative standard-Bijoy conversion candidates;
- `legacy_font_bangla` — old PDF-font glyph text that is detected and preserved;
- `mixed` — more than one representation is present;
- `none` — no supported Bangla representation detected.

Legacy PDF-font Bangla is **not automatically converted** because real Supreme Court PDFs showed
that passing those glyph strings through a standard Bijoy converter can produce plausible-looking
but incorrect Unicode. The current behavior prioritizes source fidelity and emits a diagnostic
warning.

See [Encoding and normalization](docs/encoding.md).

## Project layout

```text
src/legal_ingest/
├── benchmarking/   # executable validation helpers
├── encoding/       # Bangla / Bijoy / legacy-font detection and normalization
├── exporters/      # JSON, Markdown, retrieval chunks
├── extractors/     # pdfplumber, pypdf, optional Docling
├── parsing/        # deterministic legal metadata parsers
├── quality/        # transparent extraction-usability metrics
├── cli.py
├── config.py
├── pipeline.py
└── schemas.py

examples/           # small runnable usage examples
tests/              # unit and integration tests
benchmarks/         # committed validation seeds and measured results
docs/               # architecture and usage documentation
```

The older `manual_ingestion/` and `docling_ingestion/` directories are retained as historical
reference implementations. New integrations should use `legal_ingest`.

## Documentation

- [Getting started](docs/getting-started.md)
- [Public API](docs/public-api.md)
- [Architecture](docs/architecture.md)
- [Extractors](docs/extractors.md)
- [Encoding and normalization](docs/encoding.md)
- [Legal metadata](docs/metadata.md)
- [Quality routing](docs/quality-routing.md)
- [Exporters and retrieval chunks](docs/exporters.md)
- [Benchmarking](docs/benchmarking.md)
- [Real public-PDF smoke validation](docs/public-pdf-smoke.md)
- [Law Buddy integration boundary](docs/law_buddy_integration.md)
- [Release process](docs/releasing.md)

## Development

```bash
python -m pip install -e ".[manual,bangla,dev]"
ruff check src tests examples
pytest
legal-ingest benchmark
```

Package metadata can also be validated before a release:

```bash
python -m pip install ".[release]"
python -m build
twine check dist/*
```

## Contributing

Bug reports, parser fixtures, additional court-layout examples, encoding examples, documentation
improvements, and benchmark annotations are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md)
before opening a pull request.

If you discover a security issue, follow [SECURITY.md](SECURITY.md) rather than opening a public
issue.

## Citation

If this software supports academic or research work, see [CITATION.cff](CITATION.cff) for citation
metadata.

## Limitations

- PDF input only;
- scanned/image-only PDFs do not yet have an OCR baseline;
- routing weights and thresholds are heuristic rather than corpus-calibrated;
- metadata patterns focus mainly on common English-language Bangladesh court layouts;
- Bangla-language caption metadata needs broader coverage;
- retrieval chunks are page-local by design;
- legacy PDF-font Bangla is detected and preserved, but not yet decoded to Unicode;
- current benchmark data is too small for general accuracy claims.

## Responsible use

This project is document-processing and retrieval infrastructure. It does **not** provide legal
advice and should not be treated as a substitute for qualified legal review. Downstream systems
should preserve source citations, expose uncertainty, and verify important legal conclusions
against authoritative material.

## License

Released under the [MIT License](LICENSE).

# BanglaLegalIngest

[![CI](https://github.com/sifat371/BanglaLegalIngest/actions/workflows/ci.yml/badge.svg)](https://github.com/sifat371/BanglaLegalIngest/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](pyproject.toml)
[![Status: Alpha](https://img.shields.io/badge/status-alpha-orange.svg)](CHANGELOG.md)

**BanglaLegalIngest** is a reusable Python toolkit for turning Bangladesh legal PDFs containing
English, Bangla, and legacy Bangla encodings into page-aware, provenance-preserving document
objects and retrieval-ready chunks.

It is designed as a standalone ingestion layer for legal search, RAG, document analysis, and
research pipelines—so downstream systems do not need to maintain their own one-off PDF parsing
scripts.

> **Project status:** public alpha. The core API is usable, tested on Python 3.11 and 3.12, and
> validated against several public Bangladesh Supreme Court judgments. The benchmark corpus is
> still small, so the project does not claim representative real-world accuracy.

## Highlights

- **Page-aware extraction** with pdfplumber, pypdf, or optional Docling.
- **Quality-aware routing** between lightweight extractors using transparent usability signals.
- **Bangla encoding analysis** for Unicode Bangla, standard Bijoy-like text, and legacy PDF-font
  Bangla.
- **Conservative normalization** that converts supported Bijoy candidates while preserving unsafe
  legacy-font glyph text instead of silently corrupting it.
- **Legal metadata parsing** for common Bangladesh court fields such as case number, court, judges,
  parties, hearing dates, and judgment date.
- **Evidence provenance** with page-relative source spans for extracted metadata.
- **Retrieval-ready exports** as canonical JSON, Markdown, or page-grounded JSONL chunks.
- **Stable chunk provenance** through document IDs, page numbers, and exact character offsets.
- **Executable validation** through seed benchmarks and a real-public-PDF smoke workflow.

## Why this exists

Bangladesh legal PDFs are not uniform. A single corpus may contain English, Unicode Bangla,
Bijoy-like text, older font-encoded Bangla, inconsistent court captions, connected appeals, and
different extraction quality across PDF libraries.

BanglaLegalIngest turns those concerns into one reusable pipeline with explicit schemas and
diagnostics:

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
git clone https://github.com/sifat371/BanglaLegalIngest.git
cd BanglaLegalIngest

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

python -m pip install --upgrade pip
python -m pip install ".[manual,bangla]"
```

Python **3.11+** is required.

> **Naming note:** the project/distribution name is `BanglaLegalIngest` / `bangla-legal-ingest`,
> while the Python import remains `legal_ingest`. The primary CLI is `bangla-legal-ingest`;
> `legal-ingest` remains available as a compatibility alias. See
> [Project naming and compatibility](docs/naming.md).

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

Each chunk retains source-document identity, the source page, exact page-relative character
offsets, and selected legal metadata.

## CLI

Canonical JSON:

```bash
bangla-legal-ingest ingest judgment.pdf
```

Markdown:

```bash
bangla-legal-ingest ingest judgment.pdf --format markdown
```

Retrieval chunks as JSONL:

```bash
bangla-legal-ingest ingest judgment.pdf \
  --format chunks \
  --output chunks.jsonl
```

Use a specific extractor:

```bash
bangla-legal-ingest ingest judgment.pdf --extractor pypdf
```

Allow optional Docling during automatic routing:

```bash
python -m pip install ".[docling,bangla]"
bangla-legal-ingest ingest judgment.pdf --auto-docling
```

Run the committed regression validation:

```bash
bangla-legal-ingest benchmark
```

Existing scripts that use the older `legal-ingest` command continue to work.

## Output model

The public API returns an `IngestionResult` containing a canonical `LegalDocument` plus extraction
and routing diagnostics.

An abbreviated result has this shape:

```json
{
  "document": {
    "document_id": "<sha256>",
    "source_filename": "judgment.pdf",
    "metadata": {
      "case_number": "Criminal Appeal No. 3346 of 2022",
      "court": "SUPREME COURT OF BANGLADESH HIGH COURT DIVISION",
      "judges": ["Md. Shohrowardi"],
      "parties": [
        {
          "name": "Nurunnahar",
          "role": null
        },
        {
          "name": "The State and another",
          "role": null
        }
      ],
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

See [Public API](docs/public-api.md) for the canonical object boundary used by downstream systems.

## Bangla and legacy-font behavior

The package distinguishes:

- `unicode_bangla` — already-valid Unicode Bangla;
- `bijoy` — conservative standard-Bijoy conversion candidates;
- `legacy_font_bangla` — old PDF-font glyph text that is detected and preserved;
- `mixed` — more than one representation is present;
- `none` — no supported Bangla representation was detected.

Legacy PDF-font Bangla is **not automatically converted**. Real Supreme Court PDFs showed that
passing those glyph strings through a standard Bijoy converter can produce plausible-looking but
incorrect Unicode. BanglaLegalIngest therefore prioritizes source fidelity and emits a diagnostic
warning instead of silently rewriting uncertain text.

See [Encoding and normalization](docs/encoding.md).

## Validation

The repository uses four complementary validation layers:

| Validation | Current scope |
| --- | --- |
| Unit/integration CI | Python 3.11 and 3.12 |
| Committed metadata seed | 1 manually verified sample judgment / 7 scored fields |
| Committed encoding seed | 5 characterization cases |
| Public-PDF smoke test | 4 Bangladesh Supreme Court judgments / 31 explicit checks |

The latest completed public-PDF smoke validation ingested all four documents, created page-grounded
retrieval chunks for every document, and passed **31/31 explicit checks**. Those checks cover
selected metadata fields and safety behavior; they are **not** a statistically representative
accuracy estimate.

The exact unit-test count is intentionally left to CI because it changes as regression coverage
grows.

See [Validation Results](benchmarks/RESULTS.md), [Benchmarking](docs/benchmarking.md), and
[Public PDF Smoke Test](docs/public-pdf-smoke.md).

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
reference implementations. New integrations should use the `legal_ingest` package.

## Documentation

- [Getting started](docs/getting-started.md)
- [Project naming and compatibility](docs/naming.md)
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
bangla-legal-ingest benchmark
```

Validate package metadata before a release:

```bash
python -m pip install ".[release]"
python -m build
twine check dist/*
```

## Contributing

Bug reports, parser fixtures, additional court-layout examples, encoding examples, documentation
improvements, and benchmark annotations are welcome. Please read
[CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

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

BanglaLegalIngest is document-processing and retrieval infrastructure. It does **not** provide
legal advice and should not be treated as a substitute for qualified legal review. Downstream
systems should preserve source citations, expose uncertainty, and verify important legal
conclusions against authoritative material.

## License

Released under the [MIT License](LICENSE).

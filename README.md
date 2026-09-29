# Legal Document Ingestion

A reusable Python module for page-aware ingestion of multilingual Bangladesh legal PDFs, with a
roadmap for legacy Bijoy normalization, legal metadata parsing, and retrieval-ready exports.

> **Status:** Stage 2 active — package foundation and unified extraction API are implemented.
> Bangla encoding normalization and legal metadata migration are the next stages.

## Why this project exists

Bangladesh legal PDFs can combine English and Bangla, legacy Bijoy-encoded text, complex court
layouts, and metadata such as case numbers, benches, parties, dates, and citations. The project
began as two extraction experiments and is being matured into a stable module suitable for
downstream systems such as Law Buddy.

## Install

For the lightweight extraction path:

```bash
python -m pip install -e ".[manual]"
```

For development:

```bash
python -m pip install -e ".[manual,dev]"
```

Docling remains optional:

```bash
python -m pip install -e ".[docling]"
```

## Python API

```python
from legal_ingest import LegalDocumentPipeline

pipeline = LegalDocumentPipeline()
result = pipeline.ingest("judgment.pdf")

print(result.document.source_filename)
print(result.document.pages[0].page_number)
print(result.document.pages[0].text)
print(result.diagnostics.extractor)
```

Choose a backend explicitly:

```python
pipeline = LegalDocumentPipeline(extractor="pypdf")
result = pipeline.ingest("judgment.pdf")
```

The default `auto` mode currently uses pdfplumber and falls back to pypdf if extraction fails or
does not meet the configured minimum text length. Automatic Docling routing is intentionally
deferred until the quality-routing stage.

## CLI

Extract a document and print canonical JSON:

```bash
legal-ingest ingest judgment.pdf
```

Select a backend:

```bash
legal-ingest ingest judgment.pdf --extractor pypdf
legal-ingest ingest judgment.pdf --extractor docling
```

Inspect the stable schema:

```bash
legal-ingest schema --model result
```

## Current architecture

```text
PDF
 |
 v
LegalDocumentPipeline
 |
 +-- pdfplumber
 +-- pypdf
 +-- Docling (optional)
 |
 v
ExtractedContent
 |-- PageContent[]
 |-- combined text
 |-- warnings
 |
 v
LegalDocument + ExtractionDiagnostics
```

Every backend now returns the same page-aware intermediate contract. The public pipeline computes a
deterministic SHA-256 document identity, preserves source pages, and returns objects instead of
writing files through hidden global paths.

See [docs/architecture.md](docs/architecture.md) and
[docs/extractors.md](docs/extractors.md).

## What Stage 2 intentionally does not do

The original manual script already contains experimental Bijoy detection/conversion and metadata
regexes. Those are not silently copied into the new pipeline yet. They will be migrated and tested
as separate stages so extraction, encoding normalization, and legal parsing can be evaluated
independently.

The legacy directories remain available during migration:

- `manual_ingestion/`
- `docling_ingestion/`

## Known limitations

- PDF input only;
- scanned/image-only PDFs are not yet an OCR baseline;
- Docling support depends on a version with page-aware Markdown export;
- `auto` currently routes only between pdfplumber and pypdf;
- encoding information and legal metadata remain empty/default in the new API until Stages 3–4;
- no benchmark results are claimed yet.

## Roadmap

1. **Package foundation** — complete.
2. **Unified extraction** — in progress in this release.
3. **Bangla encoding layer** — tested Bijoy detection and normalization.
4. **Legal metadata parsing** — modular parsers with provenance.
5. **Quality routing and exporters** — automatic routing, JSON/Markdown, retrieval chunks.
6. **Benchmarking** — manually verified gold set and published extraction metrics.

## License

MIT. See [LICENSE](LICENSE).

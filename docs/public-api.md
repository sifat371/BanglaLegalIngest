# Public API

The package aims to keep downstream integrations centered on a small set of public objects and
functions exported from `legal_ingest`.

## Pipeline

### `LegalDocumentPipeline`

Primary entry point:

```python
from legal_ingest import LegalDocumentPipeline

result = LegalDocumentPipeline().ingest("judgment.pdf")
```

Use `ingest_many()` for several explicit paths.

### `PipelineConfig`

Controls extractor selection, minimum text, quality threshold, Bijoy conversion, metadata parsing,
page retention, and optional Docling fallback.

## Canonical models

### `IngestionResult`

Top-level return object.

Contains:

- `document: LegalDocument`
- `diagnostics: ExtractionDiagnostics`

### `LegalDocument`

Canonical downstream document contract.

Important fields include:

- `schema_version`
- `document_id`
- `source_filename`
- `source_sha256`
- `metadata`
- `encoding`
- `pages`
- `text`

### `PageContent`

One-based page number plus extracted page text.

### `LegalMetadata`

Currently supports:

- case number;
- case type;
- court;
- district;
- judges;
- parties;
- hearing dates;
- judgment date;
- selected legal citations;
- evidence spans.

Unsupported fields remain empty instead of being guessed.

### `EvidenceSpan`

Records the page number, source text, and optional page-relative character offsets that supported a
metadata value.

### `EncodingInfo`

Describes the source representation before normalization and records conversion diagnostics.

### `ExtractionDiagnostics`

Records the selected extractor, fallback behavior, routing attempts, quality report, metrics, and
warnings.

### `RetrievalChunk`

Page-grounded chunk contract for indexing/RAG systems. Includes source identity, page number,
character offsets, text, and selected metadata.

## Export helpers

```python
from legal_ingest import (
    to_json,
    to_markdown,
    to_retrieval_chunks,
    write_json,
    write_markdown,
    write_chunks_jsonl,
)
```

## Encoding helpers

```python
from legal_ingest import detect_encoding, is_bijoy_line
```

For legacy PDF-font detection, use:

```python
from legal_ingest.encoding import is_legacy_font_line
```

## Metadata helper

```python
from legal_ingest import parse_legal_metadata
```

This operates on page-aware `PageContent` objects and is useful when text extraction happens
elsewhere.

## Benchmark helpers

The package also exports the seed benchmark runners for reproducible regression checks:

```python
from legal_ingest import run_encoding_benchmark, run_metadata_benchmark, run_seed_benchmarks
```

## Project naming

The repository and public project are named **BanglaLegalIngest**. The Python distribution name is
`bangla-legal-ingest`, the import namespace remains `legal_ingest`, and the primary CLI is
`bangla-legal-ingest`. The older `legal-ingest` CLI name remains as a compatibility alias.

## Compatibility

The project is pre-1.0. Public API changes should be documented in `CHANGELOG.md`. Downstream
systems should pin a version/commit for production use until a stable release is made.

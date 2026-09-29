# Architecture

## Stage 1 boundary

Stage 1 establishes the package and the contracts that later extraction backends must honor.
It does **not** replace the existing manual and Docling scripts yet.

The public package is `legal_ingest`.

## Canonical flow

```text
source document
      |
      v
 extractor backend
      |
      v
 page-aware extracted text
      |
      v
 encoding normalization
      |
      v
 legal metadata parsing
      |
      v
 canonical LegalDocument
      |
      +--> JSON / Markdown
      |
      +--> retrieval-ready chunks
```

Every backend will eventually return the same `IngestionResult`, consisting of:

- `LegalDocument`: normalized content, pages, encoding information, and legal metadata.
- `ExtractionDiagnostics`: extractor identity, fallback behavior, quality metrics, and warnings.

## Design rules

1. **Backend-independent schema** — pdfplumber, pypdf, and Docling must not create incompatible
   output formats.
2. **Page provenance first** — page identity is preserved as structured data rather than embedded
   only as text markers.
3. **Deterministic core** — the base package must not require an LLM or paid API.
4. **Optional heavy dependencies** — Docling remains an optional installation extra.
5. **No hidden filesystem behavior** — future library APIs accept explicit inputs and return
   objects; exporters decide when files are written.
6. **Downstream independence** — Law Buddy can consume the stable schema, but this repository
   never imports Law Buddy.

## Migration plan

The legacy directories are retained during migration:

- `manual_ingestion/`
- `docling_ingestion/`

Stage 2 will move extraction behavior behind backend interfaces while preserving current
functionality. Later stages will migrate encoding normalization, legal metadata parsing, quality
routing, exporters, and benchmark tooling.

# Legal Document Ingestion

Reusable foundations for processing multilingual Bangladesh legal documents, with particular
attention to mixed English/Bangla text and legacy Bijoy-encoded Bangla.

> **Status:** active modularization. The original manual and Docling pipelines are preserved
> while their behavior is migrated into the new `legal_ingest` package.

## Why this project exists

Bangladesh legal PDFs can combine:

- English and Bangla in the same document;
- Unicode Bangla and legacy Bijoy-encoded text;
- complex court-document layouts;
- legal metadata such as case numbers, benches, parties, dates, and citations.

The repository began as an experiment comparing a lightweight pdfplumber/pypdf pipeline with a
layout-aware Docling pipeline. It is now being upgraded into a reusable ingestion module with a
stable output contract suitable for downstream retrieval systems such as Law Buddy.

## Current package foundation

Stage 1 introduces:

- installable `src/legal_ingest` package;
- canonical Pydantic schemas;
- shared pipeline configuration;
- domain-specific exceptions;
- a small CLI for inspecting the canonical JSON schema;
- pytest coverage for the contracts;
- Ruff linting;
- GitHub Actions CI;
- optional dependency groups for lightweight and Docling-based extraction.

The extraction algorithms still live in the legacy directories during this stage. Moving them
behind common extractor interfaces is the next migration step.

## Install

Base package:

```bash
python -m pip install -e .
```

Development tools:

```bash
python -m pip install -e ".[dev]"
```

Legacy lightweight extraction dependencies:

```bash
python -m pip install -e ".[manual]"
```

Docling dependencies:

```bash
python -m pip install -e ".[docling]"
```

## Package contract

```python
from legal_ingest import LegalDocument, PipelineConfig

config = PipelineConfig(extractor="auto", convert_bijoy=True)

document_schema = LegalDocument.model_json_schema()
```

Inspect the schema from the CLI:

```bash
legal-ingest schema --model result
```

## Target architecture

```text
legal PDF
   |
   v
extractor (auto / pdfplumber / pypdf / docling)
   |
   v
page-aware text
   |
   v
Bangla encoding analysis and normalization
   |
   v
legal metadata and structure parsing
   |
   v
canonical LegalDocument
   |
   +--> JSON / Markdown
   |
   +--> provenance-aware retrieval chunks
```

See [docs/architecture.md](docs/architecture.md).

## Existing extraction experiments

### Manual pipeline

The original `manual_ingestion/` implementation currently provides:

- pdfplumber extraction with pypdf fallback;
- heuristic Bangla/Bijoy detection;
- line-level Bijoy-to-Unicode conversion;
- regex-based legal metadata extraction;
- text normalization;
- text and metadata export.

### Docling pipeline

The original `docling_ingestion/` implementation provides:

- layout-aware PDF conversion;
- Markdown export;
- JSON export;
- regex-based legal metadata extraction.

The legacy Docling path has not yet been validated as thoroughly as the manual path and is being
kept separate until the common extractor interface is introduced.

## Known limitations

- legacy metadata extraction is regex-driven and has been tested on only a small set of documents;
- party extraction is not yet reliable across document formats;
- Bijoy detection currently uses heuristics;
- the legacy pipelines have different output structures;
- scanned/image-only PDFs are not yet a supported baseline;
- benchmark results have not yet been established.

These are migration targets rather than hidden production claims.

## Roadmap

1. **Package foundation** — schemas, config, CLI, tests, CI.
2. **Unified extraction** — common pdfplumber, pypdf, and optional Docling backends.
3. **Bangla encoding layer** — tested Bijoy detection and normalization.
4. **Legal metadata parsing** — modular parsers with provenance.
5. **Quality routing and exporters** — automatic fallback, JSON/Markdown, retrieval chunks.
6. **Benchmarking** — manually verified gold set and published extraction metrics.

## Legacy usage

The original scripts remain available during migration.

Manual:

```bash
cd manual_ingestion
pip install -r requirements.txt
python ingest_legal_cases.py
```

Docling:

```bash
cd docling_ingestion
pip install -r requirements.txt
python ingest_with_docling.py
```

## License

MIT. See [LICENSE](LICENSE).

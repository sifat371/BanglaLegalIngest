# Changelog

All notable public-facing changes will be documented here.

The project follows semantic-versioning principles while it remains pre-1.0: minor releases may
still include intentional API changes, and those changes should be documented.

## [0.6.0a1] - 2026-09-29

First public-alpha packaging baseline after the repository maturation work.

### Added

- installable `legal_ingest` Python package and `legal-ingest` CLI;
- page-aware pdfplumber, pypdf, and optional Docling extractors;
- quality-aware automatic extraction routing;
- Unicode Bangla, standard Bijoy, mixed, and legacy-font detection;
- conservative Bijoy-to-Unicode normalization;
- deterministic legal metadata parsing with page-relative evidence;
- canonical JSON and Markdown exporters;
- provenance-aware page-local retrieval chunks and JSONL export;
- benchmark harness and committed seed validation;
- public Bangladesh Supreme Court PDF smoke-test workflow;
- real-document parser/encoding fixes discovered during smoke validation.

### Known limitations

- OCR/scanned-PDF support is not yet implemented;
- legacy PDF-font Bangla is detected and preserved rather than decoded;
- metadata coverage is strongest for common English-language Bangladesh court layouts;
- the benchmark corpus is not large enough for representative accuracy claims.

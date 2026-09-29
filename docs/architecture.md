# Architecture

## Current boundary: Stage 2

The package foundation is now active and extraction backends are being migrated behind one
page-aware contract. The legacy scripts remain in the repository for comparison while the new
module becomes the supported integration surface.

The public package is `legal_ingest`.

## Canonical flow

```text
PDF path
   |
   v
LegalDocumentPipeline
   |
   +--> pdfplumber
   +--> pypdf
   +--> Docling (optional)
   |
   v
ExtractedContent
   |  - pages[]
   |  - combined text
   |  - warnings
   v
LegalDocument + ExtractionDiagnostics
```

Stage 2 does not yet perform Bangla/Bijoy normalization or legal metadata parsing. Those remain
separate migration stages so extractor behavior can be tested independently.

## Extraction policy

Explicit modes run only the requested backend:

- `pdfplumber`
- `pypdf`
- `docling`

`auto` is intentionally conservative in Stage 2:

1. run pdfplumber;
2. accept it when extracted text meets `min_extracted_characters`;
3. otherwise fall back to pypdf;
4. fail clearly when both backends fail or remain below the configured minimum.

Docling is not part of automatic quality routing yet. More advanced quality metrics and routing
belong to Stage 5.

## Design rules

1. **Backend-independent schema** — every backend returns `ExtractedContent`.
2. **Page provenance first** — page identity is structured data, not a synthetic text marker.
3. **No hidden writes** — extraction returns objects and does not write output files.
4. **Deterministic identity** — the pipeline records a SHA-256 source digest as document ID.
5. **Optional heavy dependencies** — Docling is imported lazily.
6. **Deterministic core** — no LLM or paid API is required.
7. **Downstream independence** — Law Buddy can consume the schema later, but this package never
   imports Law Buddy.

## Remaining migration plan

- Stage 3: tested Bangla/Bijoy detection and normalization.
- Stage 4: modular legal metadata parsing with provenance.
- Stage 5: extraction quality routing, exporters, retrieval-ready chunks.
- Stage 6: gold-set benchmarking and published metrics.

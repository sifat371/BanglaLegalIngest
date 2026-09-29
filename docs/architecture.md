# Architecture

## Current boundary: Stage 6

The module now separates extraction, routing, encoding normalization, legal metadata parsing,
canonical assembly, output adapters, and regression validation.

~~~text
PDF
 |
 v
LegalDocumentPipeline
 |
 v
quality-aware extractor routing
 |
 v
page-aware text
 |
 v
Bangla/Bijoy normalization
 |
 v
legal metadata + EvidenceSpan
 |
 v
LegalDocument
 |
 +-- JSON / Markdown
 +-- RetrievalChunk[]
 |
 v
benchmark harness
 +-- metadata seed
 +-- encoding seed
~~~

## Stable boundaries

- extractors do not write output files;
- routing uses observable text signals rather than semantic/legal claims;
- normalization preserves page identity;
- metadata extraction is deterministic and evidence-aware;
- exporters consume canonical models;
- retrieval chunks preserve page and character provenance;
- Law Buddy remains downstream and is not imported by this package;
- benchmark reports distinguish regression seeds from representative accuracy claims.

## Validation boundary

The committed metadata seed currently covers one repository sample judgment. The encoding seed is
synthetic. Real-PDF extraction accuracy is intentionally not reported because the raw PDF benchmark
corpus is not present in the repository.

The next maturity milestone is therefore data expansion rather than another architecture rewrite:
build a larger manually reviewed benchmark before changing routing thresholds or publishing broad
performance numbers.

# Architecture

## Current boundary: Stage 5

The module now separates extraction, routing, encoding normalization, legal metadata parsing,
canonical assembly, and output adapters.

~~~text
PDF
 |
 v
LegalDocumentPipeline
 |
 v
quality-aware extractor routing
 |-- pdfplumber
 |-- pypdf
 |-- Docling (optional opt-in fallback)
 |
 v
ExtractedContent + ExtractionQuality
 |
 v
Bangla/Bijoy detection + selective normalization
 |
 v
deterministic legal metadata parsing + EvidenceSpan
 |
 v
LegalDocument
 |
 +-- canonical JSON
 +-- Markdown
 +-- page-grounded RetrievalChunk[]
                    |
                    v
             downstream RAG / Law Buddy
~~~

## Stable boundaries

- extractors do not write output files;
- routing uses observable text signals, not semantic/legal claims;
- encoding normalization preserves page identity;
- metadata extraction is deterministic and evidence-aware;
- exporters accept canonical models rather than re-parsing source PDFs;
- retrieval chunks preserve page and character provenance;
- Law Buddy remains downstream and is not imported by this package.

## Remaining plan

Stage 6 will add manually verified benchmark sets and measured extraction/metadata results. Those
measurements will determine whether routing thresholds, parser patterns, or chunk defaults should be
changed before a stable non-alpha release.

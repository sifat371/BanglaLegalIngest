# Architecture

## Current boundary: Stage 3

The package now has a common page-aware extraction layer and a deterministic Bangla encoding layer.
Legal metadata parsing remains intentionally separate for Stage 4.

## Canonical flow

~~~text
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
   |
   v
source encoding detection
   |
   +--> Unicode Bangla
   +--> Bijoy-like
   +--> mixed
   +--> none
   |
   v
conservative line-level Bijoy normalization (optional)
   |
   v
LegalDocument + ExtractionDiagnostics
~~~

## Encoding invariants

- classification describes the extracted source before conversion;
- page numbers never change during normalization;
- non-candidate lines are preserved;
- failed conversions preserve original text and surface warnings;
- missing optional conversion dependencies do not prevent detection;
- no LLM or network call is required.

## Extraction policy

Explicit modes run only the requested backend:

- pdfplumber
- pypdf
- docling

Auto mode remains intentionally conservative:

1. run pdfplumber;
2. accept it when extracted text meets min_extracted_characters;
3. otherwise fall back to pypdf;
4. fail clearly when both backends fail or remain below the configured minimum.

Advanced quality routing and automatic Docling selection remain Stage 5 work.

## Remaining migration plan

- Stage 4: modular legal metadata parsing with provenance.
- Stage 5: extraction quality routing, exporters, retrieval-ready chunks.
- Stage 6: gold-set benchmarking and published metrics.

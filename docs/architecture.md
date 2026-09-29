# Architecture

## Current boundary: Stage 4

The module now separates extraction, encoding normalization, legal metadata parsing, and canonical
document assembly.

~~~text
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
ExtractedContent with PageContent[]
 |
 v
Bangla source-encoding detection
 |
 v
selective Bijoy -> Unicode normalization
 |
 v
deterministic legal metadata parsers
 |-- case identity
 |-- court / district
 |-- judges
 |-- parties
 |-- dates
 |-- citations
 |
 v
LegalDocument + page-relative metadata evidence
~~~

Metadata parsing runs on normalized page text, so downstream fields see Unicode text where Bijoy
conversion succeeded.

## Invariants

- extractors preserve one-based page identity;
- encoding classification describes source text before conversion;
- metadata parsers do not call external services or LLMs;
- unsupported metadata stays empty rather than being guessed;
- field evidence points to the page text used by the parser;
- downstream systems can disable metadata parsing without changing extraction behavior.

## Remaining plan

- Stage 5: quality-based extractor routing, exporters, and retrieval-ready chunks.
- Stage 6: manually verified gold sets and published extraction/metadata metrics.

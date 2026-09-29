# Legal Document Ingestion

A reusable Python module for page-aware ingestion of multilingual Bangladesh legal PDFs, including
conservative detection and normalization of legacy Bijoy-encoded Bangla.

> Status: Stage 3 implemented — package foundation, unified extraction, and Bangla encoding
> handling are available. Legal metadata parsing is the next migration stage.

## Why this project exists

Bangladesh legal PDFs can combine English and Bangla, legacy Bijoy-encoded text, complex court
layouts, and metadata such as case numbers, benches, parties, dates, and citations. The project
began as two extraction experiments and is being matured into a stable module suitable for
downstream systems such as Law Buddy.

## Install

Lightweight PDF extraction:

~~~bash
python -m pip install -e ".[manual]"
~~~

Add Bijoy-to-Unicode conversion:

~~~bash
python -m pip install -e ".[manual,bangla]"
~~~

For development:

~~~bash
python -m pip install -e ".[manual,bangla,dev]"
~~~

Docling remains optional:

~~~bash
python -m pip install -e ".[docling,bangla]"
~~~

## Python API

~~~python
from legal_ingest import LegalDocumentPipeline

pipeline = LegalDocumentPipeline()
result = pipeline.ingest("judgment.pdf")

print(result.document.source_filename)
print(result.document.pages[0].page_number)
print(result.document.encoding.kind)
print(result.document.encoding.normalization_applied)
print(result.diagnostics.extractor)
~~~

The default pipeline detects source encoding after extraction. If conservative Bijoy candidate
lines are found and bijoy2unicode is installed, those lines are normalized to Unicode while
non-candidate lines are preserved.

Disable conversion while keeping detection:

~~~python
from legal_ingest import LegalDocumentPipeline, PipelineConfig

pipeline = LegalDocumentPipeline(
    PipelineConfig(convert_bijoy=False)
)
result = pipeline.ingest("judgment.pdf")
~~~

## CLI

~~~bash
legal-ingest ingest judgment.pdf
legal-ingest ingest judgment.pdf --extractor pypdf
legal-ingest ingest judgment.pdf --no-convert-bijoy
~~~

Inspect the canonical schema:

~~~bash
legal-ingest schema --model result
~~~

## Current architecture

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
ExtractedContent
 |
 v
Bangla source-encoding detection
 |
 v
selective Bijoy -> Unicode normalization
 |
 v
LegalDocument + ExtractionDiagnostics
~~~

Every backend uses the same page-aware intermediate contract. The public pipeline computes a
deterministic SHA-256 document identity, preserves page provenance, records encoding diagnostics,
and returns objects instead of writing files through hidden global paths.

See docs/architecture.md, docs/extractors.md, and docs/encoding.md.

## Encoding behavior

The source text is classified as one of:

- unicode_bangla
- bijoy
- mixed
- none

The detector is intentionally conservative and heuristic. It does not claim perfect encoding
identification. Conversion is line-level rather than document-wide to reduce the risk of corrupting
English or already-Unicode text.

The result reports:

~~~text
unicode_bangla_chars
bijoy_indicators
bijoy_candidate_lines
normalization_applied
converted_lines
conversion_failures
~~~

## Known limitations

- the Bijoy detector still needs evaluation on a manually labeled corpus;
- scanned/image-only PDFs are not yet an OCR baseline;
- automatic extraction routing currently uses pdfplumber then pypdf;
- legal metadata in the new API remains empty/default until Stage 4;
- no benchmark numbers are claimed yet.

## Roadmap

1. Package foundation — complete.
2. Unified extraction — complete.
3. Bangla encoding layer — implemented, benchmark pending.
4. Legal metadata parsing — modular parsers with provenance.
5. Quality routing and exporters — automatic routing, JSON/Markdown, retrieval chunks.
6. Benchmarking — manually verified gold set and published extraction metrics.

## Legacy scripts

The original manual_ingestion/ and docling_ingestion/ directories remain for historical comparison
while their useful behavior is migrated into the package.

## License

MIT. See LICENSE.

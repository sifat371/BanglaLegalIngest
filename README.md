# Legal Document Ingestion

A reusable Python module for page-aware ingestion of multilingual Bangladesh legal PDFs, including
legacy Bijoy normalization and deterministic legal metadata extraction with provenance.

> Status: Stage 4 implemented — unified extraction, Bangla encoding handling, and page-aware legal
> metadata parsing are available. Quality routing/exporters are the next stage.

## Python API

~~~python
from legal_ingest import LegalDocumentPipeline

result = LegalDocumentPipeline().ingest("judgment.pdf")

print(result.document.metadata.case_number)
print(result.document.metadata.court)
print(result.document.metadata.judges)
print(result.document.metadata.parties)
print(result.document.metadata.evidence["case_number"][0].page_number)
~~~

The module currently follows this deterministic flow:

~~~text
PDF
 |
 v
page-aware extractor
 |
 v
Bangla/Bijoy detection + selective normalization
 |
 v
legal metadata parsers
 |
 v
LegalDocument
~~~

## Install

Lightweight extraction:

~~~bash
python -m pip install -e ".[manual]"
~~~

Add Bijoy conversion:

~~~bash
python -m pip install -e ".[manual,bangla]"
~~~

Development:

~~~bash
python -m pip install -e ".[manual,bangla,dev]"
~~~

Docling remains optional:

~~~bash
python -m pip install -e ".[docling,bangla]"
~~~

## Metadata fields

Stage 4 can populate case number/type, court, district, judges, caption parties, hearing dates,
judgment date, and supported legal citations. Each parser can attach page-relative EvidenceSpan
records to the metadata field it populated.

Metadata parsing can be disabled without disabling extraction:

~~~python
from legal_ingest import LegalDocumentPipeline, PipelineConfig

pipeline = LegalDocumentPipeline(PipelineConfig(parse_metadata=False))
~~~

CLI:

~~~bash
legal-ingest ingest judgment.pdf
legal-ingest ingest judgment.pdf --no-metadata
~~~

See docs/metadata.md for parser scope and limitations.

## Design principles

The current core is deterministic: no LLM or paid API is required. Unsupported fields remain empty
rather than being guessed. Page provenance is retained through extraction, normalization, and
metadata parsing so later systems such as Law Buddy can cite source material instead of relying on
flat text alone.

## Known limitations

- PDF input only;
- scanned/image-only PDFs are not yet an OCR baseline;
- automatic extraction routing currently uses pdfplumber then pypdf;
- metadata patterns currently emphasize common English-language Bangladesh court layouts;
- Bangla caption metadata needs dedicated patterns;
- no benchmark accuracy numbers are claimed yet.

## Roadmap

1. Package foundation — complete.
2. Unified extraction — complete.
3. Bangla encoding layer — complete, benchmark pending.
4. Legal metadata parsing with provenance — implemented, benchmark pending.
5. Quality routing and exporters — automatic routing, JSON/Markdown, retrieval chunks.
6. Benchmarking — manually verified gold sets and published metrics.

The original manual_ingestion/ and docling_ingestion/ directories remain for historical comparison
until the migration is complete.

## License

MIT. See LICENSE.

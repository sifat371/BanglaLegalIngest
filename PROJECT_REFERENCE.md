# BanglaLegalIngest — Project Reference and Maintainer Source of Truth

> **Purpose of this file**
>
> This document is the long-form technical reference for BanglaLegalIngest. It is intended to help
> future maintainers, contributors, reviewers, downstream integrators, and AI-assisted development
> understand the project before making changes.
>
> The executable code and tests remain authoritative for runtime behavior. This file is the
> canonical explanation of the architecture, design decisions, public contracts, validation scope,
> known limitations, and update rules. If code and this document ever disagree, investigate the
> difference and update both deliberately rather than silently treating either one as disposable.

---

## 1. Current project snapshot

This section is a dated snapshot and should be updated whenever the public package identity,
architecture, compatibility boundary, or validation status changes.

| Item | Current value |
| --- | --- |
| Project name | BanglaLegalIngest |
| GitHub repository | https://github.com/sifat371/BanglaLegalIngest |
| Python distribution | bangla-legal-ingest |
| Python import namespace | legal_ingest |
| Primary CLI | bangla-legal-ingest |
| Compatibility CLI | legal-ingest |
| Current package version | 0.7.0a1 |
| Canonical document schema version | 1.0 |
| Minimum Python | 3.11 |
| License | MIT |
| Project maturity | Public alpha |
| Last synchronized | 2026-09-29 |
| Main branch snapshot used for this document | e01dd0534761d1d5c0f0b55def82dd76ab802851 |

At the time of this snapshot, the latest main-branch CI was green on Python 3.11 and 3.12,
the package build passed, and the unit/integration suite reported 52 passing tests.

The exact test count is not a public API guarantee. Future maintainers should treat CI as the
source of truth for the current count.

---

## 2. Project purpose

BanglaLegalIngest is a reusable ingestion layer for Bangladesh legal PDFs.

Its job is to take a source PDF and turn it into a structured, page-aware, provenance-preserving
representation that downstream systems can safely consume.

The intended downstream use cases include:

- legal search;
- BM25 or vector indexing;
- retrieval-augmented generation;
- document analysis;
- research corpora;
- metadata extraction;
- source-grounded question answering;
- legal document processing pipelines.

The project exists because Bangladesh legal PDFs are heterogeneous. Real documents may contain:

- English text;
- Unicode Bangla;
- standard Bijoy-like text;
- older PDF-font-encoded Bangla glyphs;
- inconsistent spacing and line breaks;
- different court caption layouts;
- connected appeals and references;
- variable text extraction quality;
- pages with no extractable text;
- different behavior across PDF libraries.

BanglaLegalIngest centralizes these concerns so downstream systems do not need to reimplement
PDF parsing, Bangla encoding handling, legal metadata parsing, provenance, and chunk generation.

---

## 3. What the project owns

BanglaLegalIngest owns the following responsibilities:

1. validating supported source files;
2. extracting text page by page;
3. recording extraction warnings;
4. evaluating text-extraction usability;
5. routing between supported extractors;
6. detecting Bangla and legacy text representations;
7. selectively normalizing standard Bijoy-like text;
8. preserving unsafe legacy-font text;
9. parsing deterministic legal metadata;
10. attaching source evidence to parsed metadata;
11. assembling the canonical LegalDocument model;
12. exporting canonical JSON and Markdown;
13. creating page-grounded retrieval chunks;
14. exposing diagnostics for downstream inspection;
15. running committed regression benchmarks;
16. supporting real-public-PDF smoke validation.

---

## 4. What the project deliberately does not own

The following responsibilities are outside the current core package:

- legal advice;
- legal reasoning or case outcome prediction;
- LLM answer generation;
- embeddings;
- vector databases;
- BM25 indexes;
- reranking;
- query rewriting;
- citation verification at answer-generation time;
- user authentication;
- web application UI;
- database persistence;
- OCR for scanned/image-only PDFs;
- general-purpose document management;
- automatic decoding of every legacy Bangla PDF font;
- representative nationwide legal-document accuracy claims.

Downstream applications such as Law Buddy should consume BanglaLegalIngest outputs rather than
move those downstream responsibilities into this package.

---

## 5. Core design principles

The project should continue to follow these principles unless there is a documented reason to
change them.

### 5.1 Preserve provenance

Page identity must survive extraction, encoding handling, metadata parsing, and retrieval chunk
creation.

Do not flatten source material in a way that makes source-page tracing impossible unless the caller
explicitly asks for a flat representation.

### 5.2 Prefer deterministic behavior in the core

The baseline ingestion pipeline does not require an LLM or network call.

Legal metadata parsing, routing, encoding detection, chunking, and export are deterministic.

### 5.3 Preserve uncertain source text

If conversion safety is uncertain, preserve the original text and emit diagnostics.

Do not replace source text with plausible-looking output merely because it looks more readable.

### 5.4 Unsupported metadata stays empty

Do not invent judges, parties, dates, roles, courts, or citations.

A missing field is preferable to an unsupported guess.

### 5.5 Diagnostics must describe observable behavior

The extraction-usability score is a routing heuristic, not a legal-accuracy score.

Do not rename it or market it as confidence, correctness, or semantic accuracy.

### 5.6 Heavy dependencies remain optional

Docling is optional and loaded lazily.

The base package should remain usable without installing heavyweight extraction dependencies.

### 5.7 Downstream systems depend on stable models, not internal parser details

The main integration boundary is the canonical schema and public functions exported from
legal_ingest.

Internal regular expressions and heuristics may evolve without downstream applications depending
on them directly.

---

## 6. End-to-end architecture

The current processing flow is:

~~~text
PDF
 |
 v
source validation
 |
 v
extractor selection
 |-- pdfplumber
 |-- pypdf
 |-- Docling (optional)
 |
 v
ExtractedContent
 |-- PageContent[]
 |-- combined text
 |-- warnings
 |
 v
extraction-usability assessment
 |
 v
quality-aware routing decision
 |
 v
source encoding detection
 |-- Unicode Bangla
 |-- standard Bijoy-like
 |-- legacy PDF-font Bangla
 |-- mixed
 |-- none
 |
 v
safe normalization
 |-- convert supported Bijoy candidates
 |-- preserve legacy-font text
 |
 v
deterministic metadata parsing
 |-- case identity
 |-- court / district
 |-- judges
 |-- parties
 |-- hearing / judgment dates
 |-- selected citations
 |
 v
LegalDocument + ExtractionDiagnostics
 |
 +-- canonical JSON
 +-- Markdown
 +-- RetrievalChunk[]
 |
 v
downstream search / RAG / research systems
~~~

The public orchestration class is:

~~~python
from legal_ingest import LegalDocumentPipeline

result = LegalDocumentPipeline().ingest("judgment.pdf")
~~~

---

## 7. Repository structure

The main active package lives under src/legal_ingest.

~~~text
BanglaLegalIngest/
├── src/
│   └── legal_ingest/
│       ├── __init__.py
│       ├── cli.py
│       ├── config.py
│       ├── exceptions.py
│       ├── pipeline.py
│       ├── schemas.py
│       ├── extractors/
│       ├── encoding/
│       ├── parsing/
│       ├── quality/
│       ├── exporters/
│       └── benchmarking/
├── tests/
├── examples/
├── benchmarks/
│   ├── gold/
│   └── RESULTS.md
├── docs/
├── scripts/
├── manual_ingestion/
├── docling_ingestion/
├── .github/
├── pyproject.toml
├── README.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── SECURITY.md
├── CODE_OF_CONDUCT.md
├── CITATION.cff
└── LICENSE
~~~

The manual_ingestion and docling_ingestion directories are historical reference implementations.
New code should use src/legal_ingest.

Do not build new integrations against the historical scripts.

---

## 8. Project naming and compatibility

The public project intentionally uses different names at different layers.

| Layer | Name |
| --- | --- |
| Repository | BanglaLegalIngest |
| Distribution | bangla-legal-ingest |
| Python package/import | legal_ingest |
| Primary CLI | bangla-legal-ingest |
| Compatibility CLI alias | legal-ingest |

The import namespace should remain:

~~~python
from legal_ingest import LegalDocumentPipeline
~~~

The repository rename does not justify renaming the Python import package.

The older legal-ingest CLI remains a compatibility alias. New documentation should prefer
bangla-legal-ingest.

If the import namespace is ever changed, treat that as an explicit compatibility event, document it
in CHANGELOG.md, update public API documentation, and add a migration path.

---

## 9. Installation model

The base project dependency is Pydantic.

Optional dependency groups currently include:

### manual

Used for lightweight PDF extraction:

- pdfplumber;
- pypdf.

### bangla

Used for standard Bijoy-like conversion:

- bijoy2unicode.

### docling

Used for the optional heavier extractor:

- docling;
- tqdm.

### dev

Used for development:

- pytest;
- ruff.

### release

Used for package validation:

- build;
- twine.

Typical development installation:

~~~bash
python -m pip install -e ".[manual,bangla,dev]"
~~~

Typical lightweight user installation from source:

~~~bash
python -m pip install ".[manual,bangla]"
~~~

Docling-enabled installation:

~~~bash
python -m pip install ".[docling,bangla]"
~~~

The package is prepared for distribution but is not assumed by this document to already be
published on PyPI.

---

## 10. Pipeline configuration contract

PipelineConfig is defined in src/legal_ingest/config.py.

Current fields and defaults:

| Field | Type / values | Default | Meaning |
| --- | --- | --- | --- |
| extractor | auto, pdfplumber, pypdf, docling | auto | extraction backend selection |
| convert_bijoy | bool | true | enable safe standard-Bijoy conversion |
| parse_metadata | bool | true | enable deterministic metadata parsing |
| preserve_page_text | bool | true | retain PageContent objects in final document |
| min_extracted_characters | integer >= 0 | 100 | minimum non-whitespace text needed for successful extraction |
| min_quality_score | float 0..1 | 0.65 | automatic-routing usability threshold |
| auto_docling_fallback | bool | false | allow Docling as third automatic extractor |
| output_encoding | utf-8 | utf-8 | declared output text encoding |

Example:

~~~python
from legal_ingest import LegalDocumentPipeline, PipelineConfig

config = PipelineConfig(
    extractor="auto",
    convert_bijoy=True,
    parse_metadata=True,
    preserve_page_text=True,
    min_extracted_characters=100,
    min_quality_score=0.65,
    auto_docling_fallback=False,
)

pipeline = LegalDocumentPipeline(config)
result = pipeline.ingest("judgment.pdf")
~~~

Important behavior:

- retrieval chunk generation requires page content to be retained;
- turning off metadata parsing does not disable extraction;
- turning off Bijoy conversion still allows source encoding detection;
- automatic Docling fallback is opt-in.

---

## 11. Canonical data model

The canonical models are Pydantic models in src/legal_ingest/schemas.py.

All public models reject unexpected fields through the shared StrictModel configuration. This is
intentional: accidental schema drift should fail clearly.

### 11.1 EncodingKind

Current values:

- unicode_bangla;
- bijoy;
- legacy_font_bangla;
- mixed;
- none;
- unknown.

### 11.2 PageContent

Fields:

| Field | Type | Meaning |
| --- | --- | --- |
| page_number | integer >= 1 | one-based source page |
| text | string | extracted text for the page |

### 11.3 ExtractedContent

Backend-neutral extractor output.

Fields:

- pages: list of PageContent;
- text: combined extracted text;
- warnings: extraction warnings.

### 11.4 Party

Fields:

- name;
- optional role.

A role should be populated only when explicitly supported by the source text.

### 11.5 EvidenceSpan

Fields:

- page_number;
- text;
- optional start_char;
- optional end_char.

Offsets are page-relative when present.

### 11.6 LegalMetadata

Fields:

- case_number;
- case_type;
- court;
- district;
- judges;
- parties;
- hearing_dates;
- judgment_date;
- citations;
- evidence.

The evidence mapping uses field names such as case_number, judges, hearing_dates, and citations.

### 11.7 EncodingInfo

Fields:

- kind;
- has_bangla;
- unicode_bangla_chars;
- bijoy_indicators;
- total_characters;
- bijoy_candidate_lines;
- convertible_bijoy_lines;
- legacy_font_candidate_lines;
- normalization_applied;
- converted_lines;
- conversion_failures.

Encoding classification describes the extracted source representation before normalization.

### 11.8 ExtractionQuality

Fields:

- page_count;
- non_empty_page_ratio;
- printable_ratio;
- replacement_char_ratio;
- control_char_ratio;
- average_chars_per_page;
- usability_score.

The usability score is for extractor routing only.

### 11.9 RoutingAttempt

Fields:

- extractor;
- succeeded;
- extracted_characters;
- quality_score;
- error.

### 11.10 ExtractionDiagnostics

Fields:

- extractor;
- fallback_used;
- processing_seconds;
- quality;
- attempted_extractors;
- quality_metrics;
- warnings.

### 11.11 LegalDocument

Fields:

- schema_version, currently 1.0;
- document_id;
- source_filename;
- source_sha256;
- metadata;
- encoding;
- pages;
- text.

The current document_id is the SHA-256 digest of the source PDF bytes.

### 11.12 IngestionResult

Top-level result:

- document: LegalDocument;
- diagnostics: ExtractionDiagnostics.

### 11.13 RetrievalChunk

Fields:

- chunk_id;
- document_id;
- source_filename;
- source_sha256;
- page_start;
- page_end;
- chunk_index;
- char_start;
- char_end;
- text;
- case_number;
- case_type;
- court;
- district;
- judges;
- citations.

Current chunks are page-local, so page_start and page_end are equal.

---

## 12. Source validation

The public pipeline currently accepts PDF files only.

Validation rules:

- the path must exist;
- it must be a file;
- the suffix must be .pdf, case-insensitive.

Unsupported input raises a project-specific error rather than silently attempting another format.

OCR and image-only input are not currently part of the core baseline.

---

## 13. Extractor subsystem

All extractors implement DocumentExtractor from src/legal_ingest/extractors/base.py.

The contract is:

~~~python
class DocumentExtractor(ABC):
    name: str

    @abstractmethod
    def extract(self, path: Path) -> ExtractedContent:
        ...
~~~

The shared combine_pages helper joins non-empty page text with two newlines and does not insert
synthetic page markers.

### 13.1 pdfplumber

Implementation: src/legal_ingest/extractors/pdfplumber.py

Behavior:

- dependency is imported lazily;
- every PDF page becomes a PageContent object;
- a blank or non-extractable page remains represented as a page with empty text;
- a warning is recorded for pages with no extractable text;
- backend exceptions are wrapped as ExtractionError.

### 13.2 pypdf

Implementation: src/legal_ingest/extractors/pypdf.py

Behavior mirrors the page-preserving pdfplumber path:

- lazy import;
- one PageContent per source page;
- warnings for pages with no extractable text;
- backend errors wrapped as ExtractionError.

### 13.3 Docling

Implementation: src/legal_ingest/extractors/docling.py

Docling is optional and lazily imported.

Important provenance rule:

Docling extraction must expose page metadata and support page-aware Markdown export.

If the installed Docling version cannot provide page-aware content, the extractor fails instead of
silently flattening the document.

This is a deliberate design decision.

---

## 14. Automatic extractor routing

The automatic route is implemented in LegalDocumentPipeline._extract_auto.

Default candidate order:

1. pdfplumber;
2. pypdf;
3. Docling only when auto_docling_fallback is true.

For each attempt the pipeline records:

- extractor name;
- success/failure;
- extracted character count;
- quality score when available;
- error when failed.

A result can be selected early when both conditions are true:

1. extracted text meets min_extracted_characters;
2. usability_score meets min_quality_score.

If none of the successful candidates meets the configured quality threshold but one or more
produced enough text, the highest-scoring available candidate is returned with a warning.

If no candidate produces the minimum text, automatic extraction fails.

This behavior means the threshold is a routing preference, not a hard semantic-quality guarantee.

---

## 15. Extraction-usability score

The current score is defined in src/legal_ingest/quality/metrics.py.

The observable inputs are:

- non-empty-page ratio;
- printable-character ratio;
- replacement-character ratio;
- control-character ratio;
- average characters per page.

The density component is:

~~~text
density_component = min(average_chars_per_page / 500, 1.0)
~~~

The score is:

~~~text
score =
    0.45 * non_empty_page_ratio
  + 0.30 * printable_ratio
  + 0.25 * density_component
  - min(replacement_char_ratio * 5.0, 0.30)
  - min(control_char_ratio * 2.0, 0.20)
~~~

The result is clamped to 0..1.

Do not interpret this score as:

- legal correctness;
- text semantic correctness;
- OCR accuracy;
- metadata accuracy;
- answer confidence.

It is only a transparent routing heuristic.

Future changes to the weights should be benchmark-driven and documented.

---

## 16. Bangla encoding detection

Encoding detection lives in src/legal_ingest/encoding/detector.py.

The system distinguishes three practically important Bangla source representations.

### 16.1 Unicode Bangla

Characters in the Bengali Unicode block are counted directly.

Current character range:

~~~text
U+0980 .. U+09FF
~~~

### 16.2 Standard Bijoy-like text

The detector uses conservative line-level heuristics based on known markers and patterns.

Current marker set includes:

~~~text
† ‡ ¨ © ¯ ¶ Î ï š Œ ‰ ‹ Š
~~~

Current known patterns include forms such as:

~~~text
Avgvi
Av‡
‡K
Zvwi
Kwi
wQ
gvbyl
ivÎ
UvKv
FY
AvBb
Av`vjZ
Avwg
n‡q
e‡j
~~~

A line is considered a standard-Bijoy conversion candidate when:

- marker count reaches the configured threshold; or
- at least one marker and one known pattern are present; or
- at least two known patterns are present.

Legacy-font lines are explicitly excluded from standard-Bijoy conversion candidacy.

### 16.3 Legacy PDF-font Bangla

Real Supreme Court PDFs exposed another representation: old PDF-font glyph text using extended
Latin/glyph code points.

A line is currently considered a legacy-font candidate when:

- it contains at least four characters in U+00A1..U+024F; and
- those glyphs represent at least 6 percent of visible characters.

This heuristic is intentionally separate from the Bijoy converter path.

### 16.4 Encoding classification

Current classification rules:

- Unicode + any legacy representation -> mixed;
- convertible Bijoy + legacy-font glyphs -> mixed;
- legacy-font only -> legacy_font_bangla;
- convertible Bijoy only -> bijoy;
- Unicode only -> unicode_bangla;
- otherwise -> none.

Unknown exists in the schema as a defensive/default enum value.

---

## 17. Bangla normalization policy

Normalization lives in src/legal_ingest/encoding/normalizer.py.

### Safe standard-Bijoy conversion

The optional bijoy2unicode converter is loaded only when a candidate line actually needs it.

Candidate lines are converted independently.

If conversion fails for a line:

- the original line is preserved;
- conversion failure count increases;
- a warning is emitted.

Non-candidate lines are preserved unchanged.

### Legacy-font safety rule

Legacy PDF-font Bangla is not passed to bijoy2unicode.

When legacy-font candidates are detected and conversion is enabled:

- the source text is preserved;
- a warning explains why conversion was skipped.

This rule was introduced after real public Supreme Court PDF testing showed that converting old
font-glyph strings through a normal Bijoy converter could produce plausible-looking but incorrect
Unicode Bangla.

Do not remove this safety boundary without a validated font-specific decoding strategy.

### Page preservation

When page content exists, normalization runs page by page.

The normalized combined text is rebuilt from normalized pages.

EncodingInfo continues to describe the original extracted representation, while normalization
fields describe what conversion was applied.

---

## 18. Legal metadata parsing

Metadata parsing is deterministic and composed in src/legal_ingest/parsing/metadata.py.

The parser currently runs after encoding handling so supported converted text is what downstream
metadata parsing sees.

The orchestrator calls focused parsers for:

- case identity;
- court;
- district;
- judges;
- parties;
- hearing dates;
- judgment date;
- citations.

Evidence spans are attached by field when available.

---

## 19. Case identity parsing

Implementation: src/legal_ingest/parsing/case.py

Current supported case types:

- Death Reference;
- Criminal Appeal;
- Civil Appeal;
- Criminal Revision;
- Civil Revision;
- Writ Petition;
- Jail Appeal;
- Sessions Case.

The primary pattern expects forms equivalent to:

~~~text
<Case Type> No. <number> of <four-digit year>
~~~

The parser searches the first three pages and returns the first supported caption-level identity.

If a full case number is unavailable, a separate case-type-only parser may still identify the case
type.

Connected appeals may contain multiple case numbers. The canonical case_number field currently
stores the first supported caption-level match.

---

## 20. Court and district parsing

Implementation: src/legal_ingest/parsing/court.py

Court parsing supports Supreme Court of Bangladesh captions with optional:

- High Court Division;
- Appellate Division;
- parenthesized jurisdiction.

Whitespace in the heading may span lines because the pattern uses flexible whitespace.

District parsing currently expects an English form equivalent to:

~~~text
District: Brahmanbaria.
~~~

Both parsers search the first three pages.

Bangla-language court/district captions are not yet a broad supported baseline.

---

## 21. Judge parsing

Implementation: src/legal_ingest/parsing/judges.py

Judge parsing is deliberately constrained to the first-page caption.

Important safeguards:

- only the first page is parsed for judges;
- the candidate caption is truncated before the first recognized case identity or Versus marker;
- if no such boundary is found, the parser limits itself to the first 1500 characters;
- duplicate judge names are removed;
- at most eight names are returned.

This restriction was strengthened after real-PDF testing exposed a false-positive risk where prose
containing the word justice could be mistaken for a judge.

Future changes should preserve the principle that bench extraction is a caption parser, not a
document-wide name search.

---

## 22. Party parsing

Implementation: src/legal_ingest/parsing/parties.py

The party parser is caption-oriented and searches the first three pages.

Recognized separators include:

- Versus;
- Vs.;
- V.

The parser looks for plausible party text immediately around the separator and can search nearby
lines when the separator appears on its own line.

Safeguards reject:

- empty/punctuation-only values;
- role-only labels;
- text containing another Versus marker;
- judge/advocate/attorney-general context;
- district/hearing/judgment labels;
- obvious case-number lines.

Explicit dashed roles may be captured when present.

Important rule:

Do not map parties to plaintiff/defendant/appellant/respondent unless the source supports that role.
The parser should not infer procedural roles from position alone.

The current design replaced an older broad regex that could capture malformed values such as
punctuation and surrounding line breaks.

---

## 23. Date parsing

Implementation: src/legal_ingest/parsing/dates.py

Supported date forms include numeric formats such as:

~~~text
28.01.2026
28/01/2026
28-01-2026
~~~

and textual forms such as:

~~~text
22nd April -2024
~~~

Hearing parsing recognizes Heard On with optional colon.

The parser examines a bounded window after the hearing prefix and stops before a judgment heading or
blank paragraph where possible.

Judgment parsing supports forms equivalent to:

~~~text
Judgment On: 22.04.2024
Judgment Delivered On: 17.07.2025
~~~

Date parsing currently looks only at the first five pages.

---

## 24. Citation parsing

Implementation: src/legal_ingest/parsing/citations.py

Current citation extraction is intentionally narrow.

### Reported-case citations

Supported report abbreviations currently include:

- DLR;
- BLC;
- BLD;
- MLR;
- ADC.

### Statute/section patterns

Current statute patterns include:

- Code of Criminal Procedure;
- CrPC;
- Penal Code;
- Evidence Act;
- Constitution / Constitution of Bangladesh;
- Code of Civil Procedure.

The parser scans all pages.

Do not describe citation extraction as comprehensive legal citation parsing.

---

## 25. Metadata evidence

LegalMetadata.evidence maps field names to EvidenceSpan lists.

Current evidence keys may include:

- case_number;
- case_type;
- court;
- district;
- judges;
- parties;
- hearing_dates;
- judgment_date;
- citations.

Evidence includes source page and, where available, page-relative character offsets.

This evidence is part of the project’s source-grounding strategy and should be preserved when
metadata parsers evolve.

---

## 26. Document identity

The pipeline computes SHA-256 over the source PDF bytes.

That digest is used as:

- source_sha256;
- document_id.

This makes document identity deterministic for identical source bytes.

Do not switch to filename-based identity.

If identity semantics ever change, consider whether schema_version must also change.

---

## 27. Exporters

Exporters are explicit adapters. The ingestion pipeline itself does not write output files unless a
caller or CLI explicitly asks an exporter to do so.

### 27.1 JSON

Functions:

- to_json;
- write_json.

JSON serialization uses the canonical Pydantic IngestionResult schema.

### 27.2 Markdown

Functions:

- to_markdown;
- write_markdown.

The Markdown export includes:

- source filename;
- supported metadata;
- parties;
- citations;
- selected extraction information;
- source pages when retained;
- normalized full text when pages were intentionally omitted.

### 27.3 Retrieval chunks

Functions:

- to_retrieval_chunks;
- chunks_to_jsonl;
- write_chunks_jsonl.

Current defaults:

- chunk_size = 1000 characters;
- overlap = 150 characters.

Validation rules:

- chunk_size must be greater than zero;
- overlap cannot be negative;
- overlap must be smaller than chunk_size;
- document.pages must be present.

Current chunks are page-local and never cross page boundaries.

Boundary preference inside a page:

1. paragraph break;
2. sentence-like period-space;
3. Bangla danda-space;
4. whitespace;
5. hard character boundary when no suitable break occurs after 60 percent of the target size.

Whitespace is trimmed from final chunk spans.

Chunk ID format:

~~~text
<document_id>:p<page_number>:c<chunk_index>
~~~

Character offsets are relative to the page text.

---

## 28. Why chunks are page-local

The first stable retrieval contract prioritizes exact source tracing.

Cross-page chunks can improve context continuity, but they complicate provenance and citation
semantics.

Future work may add an optional cross-page strategy, but the current page-local baseline should
remain available for compatibility.

---

## 29. Public Python API

The main public imports come from legal_ingest.

Typical usage:

~~~python
from legal_ingest import (
    LegalDocumentPipeline,
    PipelineConfig,
    to_json,
    to_markdown,
    to_retrieval_chunks,
)
~~~

Other exported helpers include:

- detect_encoding;
- is_bijoy_line;
- parse_legal_metadata;
- write_json;
- write_markdown;
- write_chunks_jsonl;
- chunks_to_jsonl;
- benchmark runners;
- canonical schema models.

Legacy-font detection is available from legal_ingest.encoding.

Downstream applications should prefer public package exports over importing internal parser modules
directly unless they intentionally depend on internal behavior.

---

## 30. CLI contract

Primary command:

~~~bash
bangla-legal-ingest
~~~

Compatibility alias:

~~~bash
legal-ingest
~~~

### Version

~~~bash
bangla-legal-ingest --version
~~~

### Schema

~~~bash
bangla-legal-ingest schema --model result
bangla-legal-ingest schema --model document
~~~

### Ingest

~~~bash
bangla-legal-ingest ingest judgment.pdf
~~~

Relevant options:

~~~text
--extractor auto|pdfplumber|pypdf|docling
--min-chars INTEGER
--min-quality FLOAT
--auto-docling
--no-convert-bijoy
--no-metadata
--format json|markdown|chunks
--output PATH
--chunk-size INTEGER
--chunk-overlap INTEGER
--compact
~~~

### Benchmark

~~~bash
bangla-legal-ingest benchmark
~~~

Custom benchmark manifests may be supplied with:

~~~text
--repo-root
--metadata
--encoding
--output
~~~

---

## 31. Benchmark framework

Benchmark code lives in src/legal_ingest/benchmarking.

The committed benchmark is intentionally a regression harness, not a representative population
study.

### 31.1 Metadata benchmark

Manifest:

~~~text
benchmarks/gold/metadata_seed.jsonl
~~~

The runner:

- loads page-marked text;
- runs deterministic metadata parsing;
- evaluates only fields explicitly present in expected;
- uses normalized exact matching;
- records field-level correctness;
- computes macro field accuracy;
- computes exact-case rate;
- computes evidence coverage.

Current supported benchmark metadata fields:

- case_number;
- case_type;
- court;
- district;
- judges;
- hearing_dates;
- judgment_date;
- citations.

### 31.2 Encoding benchmark

Manifest:

~~~text
benchmarks/gold/encoding_seed.jsonl
~~~

The runner compares expected encoding class to detect_encoding output.

### 31.3 Benchmark limitations

The committed metadata seed contains one manually verified repository sample judgment.

The committed encoding seed contains five characterization examples.

These are useful regression checks but are too small for general accuracy claims.

---

## 32. Real public-PDF smoke validation

A separate workflow exercises the actual package against public Bangladesh Supreme Court PDFs.

Workflow:

~~~text
.github/workflows/public-pdf-smoke.yml
~~~

Runner:

~~~text
scripts/public_pdf_smoke.py
~~~

The workflow is manual because it depends on an external government website and should not make
ordinary CI depend on external availability.

The completed smoke validation used four public judgments:

1. Death Reference No 106 of 2018;
2. Death Reference No.117 OF 2017;
3. Civil Revision No.205 of 2021;
4. Criminal Appeal No. 3346 of 2022.

The recorded run:

- ingested all four documents;
- generated retrieval chunks for every document;
- passed 31 of 31 explicit metadata/safety checks;
- produced no smoke-test failures.

The checks cover selected metadata and source-safety behavior. They do not establish representative
accuracy for all Bangladesh legal PDFs.

Real-document testing exposed issues that were then converted into fixes and regression tests,
including:

- multi-line court headings;
- Vs. captions;
- flexible hearing date forms;
- textual judgment dates;
- false-positive judge extraction;
- role-only party labels;
- old PDF-font Bangla glyph text.

Two death-reference PDFs contained legacy-font Bangla sections. The smoke run detected 33 candidate
legacy-font lines in one and 87 in the other. Automatic conversion was not applied to those lines.

---

## 33. Current validation snapshot

As of 2026-09-29:

### CI

- Python 3.11: passing;
- Python 3.12: passing;
- Ruff: passing;
- package build: passing;
- Twine package validation: passing;
- latest observed unit/integration test count: 52 passing.

### Committed metadata seed

Current measured seed:

- cases: 1;
- scored fields: 7;
- macro field accuracy: 1.000;
- exact-case rate: 1.000;
- evidence coverage: 1.000.

### Committed encoding seed

Current measured seed:

- cases: 5;
- classification accuracy: 1.000.

### Public-PDF smoke validation

Current recorded result:

- documents: 4;
- explicit checks: 31;
- checks passed: 31.

These values belong to their stated sample sizes only.

Do not convert them into broader claims such as 100 percent legal-document accuracy.

---

## 34. CI workflows

### Required CI

Workflow:

~~~text
.github/workflows/ci.yml
~~~

Current jobs include:

- test on Python 3.11;
- test on Python 3.12;
- Ruff;
- pytest;
- seed benchmark validation;
- package build;
- Twine distribution validation.

### Public PDF smoke workflow

Workflow:

~~~text
.github/workflows/public-pdf-smoke.yml
~~~

This is intentionally separate/manual because it requires live external downloads.

Do not make normal pull-request correctness depend on an external government server.

---

## 35. Test strategy

The tests directory should protect behavior at several layers.

### Unit tests

Examples:

- encoding detection;
- conversion behavior;
- quality metrics;
- parser-specific behavior;
- exporter behavior.

### Pipeline tests

Protect:

- document hashing;
- extraction integration;
- metadata integration;
- page retention;
- configuration flags;
- auto fallback behavior.

### Regression tests

When a real document exposes a bug:

1. reduce the problem to the smallest safe fixture;
2. add a failing test;
3. fix the implementation;
4. keep the test permanently.

This is how the real-PDF discoveries should continue to improve the package.

### Packaging tests

The repository includes tests for:

- distribution name;
- runtime version consistency;
- current repository URLs;
- both CLI entry points.

---

## 36. Error-handling philosophy

The package defines project-specific exceptions in src/legal_ingest/exceptions.py.

General expectations:

- missing optional dependencies should produce actionable configuration errors;
- extractor backend failures should be wrapped as extraction errors;
- unsupported source types should fail explicitly;
- unsafe text conversion should preserve source text and warn;
- malformed benchmark JSONL should report file and line context;
- invalid chunk parameters should fail immediately.

Do not suppress errors in ways that make downstream systems believe ingestion succeeded when it did
not.

---

## 37. Warnings are part of the operational contract

Warnings are not cosmetic.

They may communicate:

- blank/non-extractable pages;
- extractor fallback;
- quality-threshold misses;
- missing optional converter;
- conversion failures;
- legacy-font text preservation.

Downstream systems should retain or log warnings.

Future code should avoid deleting useful warnings merely to make output look cleaner.

---

## 38. Law Buddy integration boundary

BanglaLegalIngest is intentionally independent of Law Buddy.

Expected flow:

~~~text
PDF
 |
 v
BanglaLegalIngest
 |
 v
LegalDocument
 |
 v
RetrievalChunk[]
 |
 v
Law Buddy
 |-- BM25
 |-- dense/vector retrieval
 |-- reranking
 |-- answer generation
 |-- citation verification
~~~

BanglaLegalIngest should own:

- extraction;
- normalization;
- metadata;
- provenance;
- diagnostics;
- retrieval-chunk creation.

Law Buddy should own:

- indexes;
- embeddings;
- retrieval/ranking;
- query understanding;
- answer generation;
- answer-level citation verification;
- UI/application behavior.

BanglaLegalIngest must not import Law Buddy.

---

## 39. Public release model

The project is currently pre-1.0.

Current distribution identity:

~~~text
bangla-legal-ingest
~~~

Current runtime version:

~~~text
0.7.0a1
~~~

Before a release, synchronize:

- pyproject.toml version;
- src/legal_ingest/__init__.py version;
- CHANGELOG.md;
- CITATION.cff;
- this PROJECT_REFERENCE.md snapshot;
- README validation claims;
- benchmark results when changed.

Release checks:

~~~bash
python -m pip install -e ".[manual,bangla,dev,release]"

ruff check src tests examples
pytest
bangla-legal-ingest benchmark

rm -rf build dist
python -m build
twine check dist/*
~~~

The first PyPI publishing workflow should prefer Trusted Publishing / GitHub OIDC.

Do not commit long-lived PyPI credentials.

---

## 40. Historical development milestones

The current architecture was reached through a deliberate staged refactor rather than a full
rewrite.

### Stage 1 — package foundation

Introduced:

- installable src-layout package;
- Pydantic schemas;
- pipeline configuration;
- CLI foundation;
- CI;
- license and architecture documentation.

### Stage 2 — unified extraction

Introduced:

- common DocumentExtractor contract;
- pdfplumber backend;
- pypdf backend;
- optional Docling backend;
- page-aware ExtractedContent;
- SHA-256 document identity;
- explicit fallback behavior.

### Stage 3 — Bangla encoding layer

Introduced:

- Unicode Bangla detection;
- conservative Bijoy-like detection;
- optional lazy conversion;
- page-preserving normalization;
- encoding diagnostics.

### Stage 4 — legal metadata and provenance

Introduced focused parsers for:

- case identity;
- court/district;
- judges;
- parties;
- dates;
- citations;
- field-level evidence.

### Stage 5 — routing and exporters

Introduced:

- transparent extraction-usability score;
- quality-aware auto routing;
- optional Docling fallback;
- JSON/Markdown exporters;
- RetrievalChunk contract;
- JSONL retrieval export;
- Law Buddy integration boundary.

### Stage 6 — validation

Introduced:

- metadata benchmark harness;
- encoding benchmark harness;
- committed seed data;
- real public-PDF smoke workflow;
- real-document parser fixes;
- safe legacy-font handling.

### Public repository maturation

Added:

- README/public documentation;
- contribution/security/conduct files;
- issue and pull-request templates;
- release documentation;
- citation metadata;
- package-build validation.

### Rename to BanglaLegalIngest

Changed public identity to:

- repository: BanglaLegalIngest;
- distribution: bangla-legal-ingest;
- primary CLI: bangla-legal-ingest.

Kept:

- import namespace: legal_ingest;
- compatibility CLI alias: legal-ingest.

---

## 41. Known limitations

The following are known, intentional limitations of the current alpha.

### Input

- PDF only;
- no OCR baseline for scanned/image-only PDFs.

### Bangla

- standard Bijoy-like conversion is heuristic;
- legacy PDF-font Bangla is detected and preserved but not decoded to Unicode;
- not every historical Bangla font/encoding is supported.

### Metadata

- strongest coverage is for common English-language Bangladesh court captions;
- Bangla-language caption metadata needs broader patterns;
- complex multi-party captions may be partially extracted;
- connected cases are simplified to one primary case_number;
- citation parsing is intentionally narrow.

### Routing

- quality weights are heuristic;
- threshold 0.65 is not corpus-calibrated;
- high usability score does not prove semantic correctness.

### Retrieval chunks

- chunks are page-local;
- no token-aware or model-specific strategy is currently built in;
- no cross-page chunking baseline is currently exposed.

### Evaluation

- metadata gold set is very small;
- encoding gold set is characterization-oriented;
- public-PDF smoke documents are useful but not representative;
- no general extraction-fidelity percentage is claimed.

---

## 42. Areas that should not be casually changed

Future maintainers should treat the following as high-risk interfaces.

### Canonical schemas

Changing field names or semantics can break downstream systems.

Consider compatibility and schema_version.

### Character offsets

RetrievalChunk and EvidenceSpan offsets are provenance data.

Do not alter trimming/combining logic without testing offset correctness.

### Legacy-font safety

Do not route legacy-font glyph text through standard Bijoy conversion without validated evidence.

### Automatic routing

Do not label the routing score as accuracy/confidence.

### document_id

The current identity is based on SHA-256 source bytes.

Changing this can break deduplication or downstream references.

### CLI aliases

legal-ingest currently exists for compatibility.

Removing it should be a documented compatibility change.

### Import namespace

legal_ingest is the stable Python import.

A repository rename is not sufficient reason to change it.

---

## 43. How to add a new extractor

A new extractor should:

1. implement DocumentExtractor;
2. define a stable name;
3. lazily import optional dependencies;
4. preserve page numbering;
5. return ExtractedContent;
6. record blank-page warnings;
7. wrap backend failures in project exceptions;
8. avoid writing files implicitly;
9. avoid losing provenance;
10. add unit tests;
11. add pipeline/routing tests;
12. update create_extractor;
13. update configuration/CLI choices when public;
14. update docs and this reference;
15. add optional dependency metadata when needed.

If page provenance cannot be preserved, fail clearly or design an explicit alternative contract.
Do not silently flatten.

---

## 44. How to add or change an encoding strategy

Any encoding change should:

1. include positive examples;
2. include negative examples;
3. preserve source text on uncertainty;
4. distinguish detection from conversion;
5. expose diagnostics;
6. avoid changing EncodingInfo semantics accidentally;
7. add regression tests;
8. test mixed English/Bangla documents;
9. test legacy-font false positives;
10. update docs/encoding.md and this reference.

If a font-specific decoder is introduced, it should probably be an explicit strategy rather than
silently replacing the current conservative policy.

---

## 45. How to add or change metadata parsing

Any metadata parser change should:

1. identify the source layout being supported;
2. use the smallest practical page/caption scope;
3. return empty output when unsupported;
4. attach EvidenceSpan records;
5. avoid procedural-role inference unless explicit;
6. deduplicate carefully;
7. add a positive regression test;
8. add at least one negative/false-positive test when relevant;
9. run existing real-PDF smoke checks where possible;
10. update docs/metadata.md and this reference.

Prefer focused parser modules over a new monolithic regex file.

---

## 46. How to add a new schema field

Before adding a public field:

1. decide whether the field belongs in ingestion or downstream retrieval/answering;
2. define exact semantics;
3. define default behavior;
4. define provenance expectations;
5. update Pydantic schema;
6. update JSON schema tests;
7. update exporters if needed;
8. update benchmark support if applicable;
9. update public-api.md;
10. update this reference;
11. consider schema_version impact.

Do not add fields only because one downstream UI wants them if they do not belong to document
ingestion.

---

## 47. How to change retrieval chunking

Chunking changes must preserve:

- deterministic behavior;
- source document identity;
- exact source page;
- offset correctness;
- stable metadata attachment.

If adding token-based, semantic, or cross-page chunking:

- make the strategy explicit;
- keep the current page-local strategy available;
- define chunk ID semantics;
- add provenance tests;
- benchmark retrieval impact separately from ingestion correctness.

---

## 48. How to expand benchmarks

A representative benchmark is the most important remaining maturity task.

A stronger corpus should include:

- multiple Bangladesh courts;
- multiple legal case types;
- English-only PDFs;
- Unicode Bangla PDFs;
- standard Bijoy-like text;
- legacy PDF-font Bangla;
- mixed documents;
- clean text PDFs;
- difficult layouts;
- blank pages;
- fully annotated parties;
- fully annotated citations;
- real raw PDFs where redistribution is allowed.

Suggested extraction metrics:

- extraction success rate;
- page coverage;
- text fidelity;
- blank-page behavior;
- extractor-selection decisions.

Suggested metadata metrics:

- normalized exact match;
- field-level precision/recall/F1 where appropriate;
- exact-case rate;
- provenance/evidence coverage.

Do not publish aggregate performance without clearly defining the population and sample size.

---

## 49. Future roadmap

The current repository does not need another broad architectural rewrite.

Higher-value future work is:

### Priority A — broader validation

Build a larger manually reviewed legal-document benchmark.

### Priority B — legacy-font decoding

Research safe font-specific legacy Bangla decoding using labeled source/output examples.

### Priority C — OCR baseline

Add explicit scanned-PDF handling, ideally behind an optional dependency and separate benchmark.

### Priority D — metadata coverage

Expand Bangladesh court-layout support, especially Bangla-language captions and more procedural
formats.

### Priority E — retrieval experiments

Evaluate alternative chunk strategies without breaking the current provenance-preserving baseline.

### Priority F — public distribution

Publish a tested pre-release to PyPI using Trusted Publishing when desired.

---

## 50. Change-management matrix

Use this table when planning a future update.

| Change type | Must inspect/update |
| --- | --- |
| package version | pyproject.toml, src/legal_ingest/__init__.py, CHANGELOG.md, CITATION.cff, this snapshot |
| repository/distribution naming | README, pyproject.toml, docs/naming.md, CITATION.cff, CHANGELOG.md, tests |
| PipelineConfig | config.py, CLI, public-api.md, getting-started.md, tests, this file |
| public schema | schemas.py, exporters, schema CLI/tests, public-api.md, this file, possibly schema_version |
| extractor | extractors/, factory, optional deps, routing tests, docs/extractors.md, this file |
| routing score | quality/, pipeline, tests, docs/quality-routing.md, benchmark rationale, this file |
| encoding detection | encoding/, tests, docs/encoding.md, smoke tests, this file |
| metadata parser | parsing/, tests, docs/metadata.md, benchmarks, smoke tests, this file |
| retrieval chunking | exporters/chunks.py, tests, docs/exporters.md, Law Buddy contract, this file |
| benchmark | benchmarking/, benchmarks/, RESULTS.md, README claims, this file |
| CLI | cli.py, pyproject scripts, README, getting-started.md, tests, this file |
| release process | pyproject, releasing.md, CHANGELOG, CITATION, CI, this file |
| Law Buddy boundary | docs/law_buddy_integration.md, schemas/chunks if needed, this file |

---

## 51. Update protocol for this source-of-truth file

For any substantial future PR, ask:

1. Does the change alter project purpose or scope?
2. Does it change the pipeline order?
3. Does it change public configuration?
4. Does it change schema fields or semantics?
5. Does it change extractor behavior?
6. Does it change routing behavior?
7. Does it change encoding classification or conversion?
8. Does it change metadata coverage?
9. Does it change provenance?
10. Does it change chunk semantics?
11. Does it change the CLI?
12. Does it change validation claims?
13. Does it change packaging or release behavior?
14. Does it change a known limitation?
15. Does it change the Law Buddy boundary?

If yes to any of these, update the relevant section in this file in the same PR.

The snapshot table at the top should be synchronized at each public release or major architectural
change.

---

## 52. Pull-request definition of done

A behavior-changing PR should normally satisfy all applicable items below:

- code is scoped to one coherent change;
- Ruff passes;
- pytest passes;
- new behavior has regression coverage;
- public schema changes are explicit;
- provenance remains correct;
- unsafe encoding conversion is not introduced;
- user-facing errors/warnings remain actionable;
- benchmark claims are not inflated;
- README is updated when public usage changes;
- specialized docs are updated;
- CHANGELOG is updated when release-facing behavior changes;
- this PROJECT_REFERENCE.md is updated when architecture/contracts change;
- package build still succeeds when packaging metadata changes.

---

## 53. Troubleshooting guide

### PDF extracts almost no text

Inspect:

- diagnostics.attempted_extractors;
- diagnostics.quality;
- diagnostics.warnings;
- whether the PDF is scanned/image-only.

Try:

~~~bash
bangla-legal-ingest ingest judgment.pdf --extractor pypdf
~~~

or install Docling and explicitly test it.

### Bangla looks corrupted

Inspect:

- document.encoding.kind;
- convertible_bijoy_lines;
- legacy_font_candidate_lines;
- normalization_applied;
- warnings.

If kind is legacy_font_bangla, unchanged glyph-like text is expected under the current safety
policy.

### Metadata is missing

Inspect:

- the first pages;
- whether the source uses an unsupported caption style;
- document.metadata.evidence.

Do not fix missing metadata by adding a document-wide greedy regex.

Add a bounded parser fixture and regression test.

### Retrieval chunk generation fails

Check that:

- preserve_page_text is true;
- chunk_size is positive;
- overlap is non-negative and smaller than chunk_size;
- document.pages is not empty.

### Automatic routing selected an unexpected extractor

Inspect attempted_extractors and each recorded quality score.

Remember that the score measures extraction usability, not legal correctness.

---

## 54. Fast orientation for a future maintainer or AI assistant

When beginning work on this repository:

1. read README.md for the public-facing overview;
2. read this PROJECT_REFERENCE.md for full technical context;
3. inspect pyproject.toml for packaging/version state;
4. inspect src/legal_ingest/schemas.py before changing data contracts;
5. inspect src/legal_ingest/pipeline.py before changing orchestration;
6. inspect the focused module relevant to the task;
7. inspect tests covering that behavior;
8. inspect benchmarks/RESULTS.md before repeating performance claims;
9. preserve the conservative legacy-font rule;
10. use a feature branch and focused PR;
11. do not merge a behavior-changing PR without green CI;
12. do not invent benchmark results.

For current project direction, prefer validation/data expansion and downstream integration over
another broad rewrite.

---

## 55. Important invariants checklist

The following should remain true unless deliberately redesigned:

- one-based page numbering;
- page provenance survives extraction;
- PDF input validation is explicit;
- document identity is SHA-256 of source bytes;
- encoding is detected before normalization;
- legacy-font text is not blindly passed to bijoy2unicode;
- failed conversion preserves original text;
- metadata parsing is deterministic;
- unsupported metadata remains empty;
- metadata evidence points back to source pages;
- automatic routing diagnostics expose attempted extractors;
- usability score is not marketed as accuracy;
- retrieval chunks are deterministic;
- retrieval chunks preserve page-relative offsets;
- page-local chunking remains available;
- core pipeline makes no external network call;
- heavy extractors remain optional;
- Law Buddy is downstream, not imported by BanglaLegalIngest;
- benchmark claims state their sample size and limitations.

---

## 56. Useful commands

### Development setup

~~~bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[manual,bangla,dev]"
~~~

### Lint

~~~bash
ruff check src tests examples
~~~

### Tests

~~~bash
pytest
~~~

### Seed benchmark

~~~bash
bangla-legal-ingest benchmark
~~~

### Print schema

~~~bash
bangla-legal-ingest schema --model result
~~~

### Ingest to JSON

~~~bash
bangla-legal-ingest ingest judgment.pdf
~~~

### Ingest to Markdown

~~~bash
bangla-legal-ingest ingest judgment.pdf --format markdown
~~~

### Export retrieval chunks

~~~bash
bangla-legal-ingest ingest judgment.pdf   --format chunks   --output chunks.jsonl
~~~

### Build package

~~~bash
python -m pip install ".[release]"
rm -rf build dist
python -m build
twine check dist/*
~~~

---

## 57. Related documentation

Use the specialized files for shorter topic-specific guidance:

- README.md — public landing page;
- docs/README.md — documentation index;
- docs/getting-started.md — installation and basic use;
- docs/naming.md — naming and compatibility;
- docs/public-api.md — public API summary;
- docs/architecture.md — architecture overview;
- docs/extractors.md — extractor behavior;
- docs/encoding.md — encoding and normalization;
- docs/metadata.md — metadata parser scope;
- docs/quality-routing.md — quality/routing behavior;
- docs/exporters.md — JSON/Markdown/chunk outputs;
- docs/benchmarking.md — benchmark framework;
- docs/public-pdf-smoke.md — real public-PDF smoke validation;
- docs/law_buddy_integration.md — downstream boundary;
- docs/releasing.md — release process;
- benchmarks/RESULTS.md — measured validation results;
- CHANGELOG.md — release-facing history;
- CONTRIBUTING.md — contributor workflow;
- SECURITY.md — security reporting;
- CITATION.cff — citation metadata.

---

## 58. Final maintainer note

BanglaLegalIngest is now organized as an independent ingestion library rather than a collection of
experiments.

The highest-value future changes should improve evidence, coverage, validation, or safe
interoperability while preserving the core contract:

~~~text
source PDF
   -> page-aware extraction
   -> safe Bangla handling
   -> deterministic legal metadata
   -> provenance-preserving LegalDocument
   -> retrieval-ready chunks
~~~

If a proposed change makes that contract harder to understand, harder to validate, or less
traceable to the source document, it should be reconsidered before implementation.

# Getting Started

## Requirements

- Python 3.11 or newer;
- a text-based PDF for the current baseline;
- optional `bijoy2unicode` support for standard Bijoy-like text;
- optional Docling support if you want the heavier extractor.

## Install from source

```bash
git clone https://github.com/sifat371/legal-document-ingestion.git
cd legal-document-ingestion

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

python -m pip install --upgrade pip
python -m pip install ".[manual,bangla]"
```

## Minimal Python example

```python
from legal_ingest import LegalDocumentPipeline

pipeline = LegalDocumentPipeline()
result = pipeline.ingest("judgment.pdf")

document = result.document

print(document.document_id)
print(document.metadata.case_number)
print(document.metadata.court)
print(len(document.pages))
print(result.diagnostics.extractor)
print(result.diagnostics.warnings)
```

## Configure the pipeline

```python
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
```

## Export JSON

```python
from legal_ingest import to_json

payload = to_json(result)
print(payload)
```

## Export retrieval chunks

```python
from legal_ingest import to_retrieval_chunks, write_chunks_jsonl

chunks = to_retrieval_chunks(
    result.document,
    chunk_size=1000,
    overlap=150,
)

write_chunks_jsonl(chunks, "chunks.jsonl")
```

Retrieval chunking requires `preserve_page_text=True` because exact source-page provenance is part
of the chunk contract.

## CLI

```bash
legal-ingest ingest judgment.pdf
legal-ingest ingest judgment.pdf --format markdown
legal-ingest ingest judgment.pdf --format chunks --output chunks.jsonl
legal-ingest ingest judgment.pdf --extractor pypdf
legal-ingest benchmark
```

## What to inspect when something looks wrong

Start with:

```python
result.diagnostics.extractor
result.diagnostics.attempted_extractors
result.diagnostics.quality
result.diagnostics.warnings
result.document.encoding
result.document.metadata.evidence
```

The package intentionally exposes diagnostics instead of hiding fallback and normalization
decisions.

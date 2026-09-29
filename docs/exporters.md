# Exporters and Retrieval Chunks

Stage 5 defines explicit output adapters instead of letting the ingestion pipeline write files
implicitly.

## Canonical JSON

~~~python
from legal_ingest import to_json, write_json

payload = to_json(result)
write_json(result, "output/result.json")
~~~

JSON uses the canonical Pydantic ingestion schema.

## Markdown

~~~python
from legal_ingest import to_markdown, write_markdown

markdown = to_markdown(result)
write_markdown(result, "output/judgment.md")
~~~

The Markdown view includes supported metadata, extraction information, and page headings.

## Retrieval chunks

~~~python
from legal_ingest import to_retrieval_chunks

chunks = to_retrieval_chunks(
    result.document,
    chunk_size=1000,
    overlap=150,
)
~~~

Stage 5 chunks are intentionally page-local. A chunk never crosses a source-page boundary.
Every chunk contains exact page-relative character offsets plus selected legal metadata.

This provides a stable interface for systems such as Law Buddy:

~~~text
LegalDocument
   |
   v
to_retrieval_chunks()
   |
   +-- chunk_id
   +-- page_start / page_end
   +-- char_start / char_end
   +-- case metadata
   +-- source text
   |
   v
BM25 / vector index / reranker
~~~

JSONL export is available with write_chunks_jsonl.

## Why page-local first?

Cross-page chunking can improve context continuity, but it complicates provenance. The first stable
module contract prioritizes exact source tracing. Later retrieval experiments can add an optional
cross-page strategy without breaking the page-local baseline.

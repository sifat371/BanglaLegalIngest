# Law Buddy Integration Contract

The ingestion project remains independent of Law Buddy. Integration happens through the canonical
document and retrieval-chunk contracts.

~~~python
from legal_ingest import LegalDocumentPipeline, to_retrieval_chunks

result = LegalDocumentPipeline().ingest("judgment.pdf")

chunks = to_retrieval_chunks(
    result.document,
    chunk_size=1000,
    overlap=150,
)

for chunk in chunks:
    index.add(
        text=chunk.text,
        metadata={
            "chunk_id": chunk.chunk_id,
            "document_id": chunk.document_id,
            "page": chunk.page_start,
            "case_number": chunk.case_number,
            "court": chunk.court,
        },
    )
~~~

Law Buddy should own retrieval, ranking, embeddings, vector/BM25 indexes, answer generation, and
citation verification. BanglaLegalIngest should own source extraction, text normalization,
document structure, metadata parsing, and source provenance.

This boundary allows each repository to evolve independently while sharing a stable ingestion
contract.

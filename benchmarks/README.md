# Benchmarks

This directory contains the committed validation seed used for regression testing.

## Metadata seed

gold/metadata_seed.jsonl contains one manually verified record based on the repository's existing
samples/sample_output_pdfplumber.txt. Only fields that can be verified directly from that sample
are scored. Party and citation fields are intentionally excluded from the seed gold rather than
being partially annotated.

This single document is not a representative accuracy benchmark.

## Encoding seed

gold/encoding_seed.jsonl is a small synthetic characterization set covering English-only text,
Unicode Bangla, Bijoy-like text, mixed Unicode/Bijoy text, and a negative example containing one
isolated legacy-looking token.

It verifies detector behavior but does not establish real-world encoding accuracy.

## Run

~~~bash
legal-ingest benchmark
~~~

The command reports metadata field exact-match metrics, metadata evidence coverage, and encoding
classification accuracy.

## What is still needed for publishable performance claims

A broader benchmark should use separately collected and manually reviewed legal documents with
multiple courts and jurisdictions, multiple language/encoding conditions, difficult layouts,
fully annotated parties/citations, and real source PDFs so extraction backends can be compared
directly.

Until that exists, the committed seed should be described as regression validation only.

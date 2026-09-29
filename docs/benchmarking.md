# Benchmarking and Validation

Stage 6 adds an executable benchmark harness while separating regression validation from
representative performance claims.

## Metadata evaluation

The metadata runner reads JSONL records that identify a page-marked text source and an expected
object. Only fields included in expected are scored.

Current metrics are normalized exact accuracy per field, macro field accuracy, exact-case rate,
and provenance evidence coverage. Whitespace and case are normalized before exact comparison. The
benchmark does not silently score unannotated fields.

## Encoding evaluation

The encoding runner compares the detector's source-encoding class against labeled text snippets and
reports classification accuracy.

## Seed limitations

The committed metadata seed has one repository sample judgment. The encoding seed is synthetic.
These are useful CI regression checks, but they are not sufficient for claims about general
Bangladesh legal-document accuracy.

## Missing extraction benchmark

The repository does not currently contain the raw source PDFs needed to compare pdfplumber, pypdf,
and Docling against a manually reviewed extraction gold set. Stage 6 therefore does not fabricate
an extraction accuracy number.

A future private or redistributable PDF benchmark can use the same package and should report at
least successful extraction rate, page coverage, text fidelity, metadata accuracy, and routing
decisions.

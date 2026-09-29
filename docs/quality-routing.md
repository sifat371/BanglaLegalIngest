# Extraction Quality Routing

Stage 5 adds deterministic routing based on observable extraction-usability signals.

The routing score is not a legal accuracy score and does not claim that extracted text is
semantically correct. It only helps decide whether another extraction backend should be tried.

## Signals

For each extractor result the module records:

- non-empty-page ratio;
- printable-character ratio;
- replacement-character ratio;
- control-character ratio;
- average extracted characters per page;
- a bounded usability score derived from those signals.

The score is intentionally transparent and will remain a heuristic until Stage 6 benchmarking
provides evidence for better thresholds or weights.

## Auto mode

By default auto mode tries:

1. pdfplumber;
2. pypdf when the first result is below the configured text/quality threshold.

If neither reaches the threshold but one or more produced enough text, the highest-scoring
candidate is returned with a warning.

Docling can be allowed as a third automatic candidate explicitly:

~~~python
PipelineConfig(auto_docling_fallback=True)
~~~

or:

~~~bash
legal-ingest ingest judgment.pdf --auto-docling
~~~

It is opt-in because Docling is a heavier optional dependency and may be substantially slower than
the lightweight extractors.

## Diagnostics

The selected result records both the final quality report and every attempted extractor, including
failed attempts. This makes routing decisions reproducible and debuggable.

# Bangla Encoding Detection and Normalization

Stage 3 migrates the useful legacy Bijoy handling into a reusable, tested package layer.

## Goals

The encoding layer has two separate responsibilities:

1. classify extracted source text as Unicode Bangla, Bijoy-like, mixed, or neither;
2. optionally convert only conservative Bijoy candidate lines to Unicode.

Detection runs even when conversion is disabled.

## Public API

~~~python
from legal_ingest import detect_encoding

info = detect_encoding(text)
print(info.kind)
print(info.unicode_bangla_chars)
print(info.bijoy_candidate_lines)
~~~

The ingestion pipeline performs the same analysis automatically:

~~~python
result = LegalDocumentPipeline().ingest("judgment.pdf")

print(result.document.encoding.kind)
print(result.document.encoding.normalization_applied)
print(result.document.encoding.converted_lines)
~~~

## Conservative line detection

The legacy script already used marker characters to decide which lines were safe to convert. Stage
3 keeps that principle and makes it independently testable.

A line is a candidate when it has:

- at least two known Bijoy marker glyphs; or
- one marker plus a known legacy pattern; or
- at least two known legacy patterns.

A single ASCII-looking pattern is not enough to rewrite an otherwise English line.

This is deliberately heuristic. It is a baseline to benchmark later, not a claim of perfect
encoding identification.

## Conversion behavior

When conversion is enabled:

- non-candidate lines remain unchanged;
- candidate lines are passed to bijoy2unicode;
- a failed conversion preserves the original line;
- conversion failures are counted and surfaced as warnings;
- page numbers are preserved;
- document-level classification describes the source text before conversion.

If the optional converter is unavailable, detection still works and the original text is returned
with a warning.

Install conversion support with:

~~~bash
pip install -e ".[bangla]"
~~~

## Why no global text rewrite?

English and Unicode Bangla often coexist with legacy text in Bangladesh legal PDFs. Converting an
entire document as though every line were Bijoy risks corrupting already-correct content. Stage 3
therefore keeps line-level selection and records exactly how many lines were converted.

## Known limitations

- the detector is heuristic and still needs a manually labeled benchmark;
- some legacy text without known markers or patterns can be missed;
- unusual English typography can still resemble legacy glyphs;
- normalization currently targets Bijoy-to-Unicode only;
- OCR/scanned PDFs remain outside the current baseline.

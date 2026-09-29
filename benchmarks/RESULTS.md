# Validation Results

Measured in GitHub Actions for Stage 6 on 2026-09-29.

## CI and committed seed

- Python 3.11: lint, tests, and seed benchmark validation passed.
- Python 3.12: lint, tests, and seed benchmark validation passed.
- Test suite after real-PDF fixes: 49 tests passed.

| Metric | Result |
| --- | ---: |
| Metadata cases | 1 |
| Metadata scored fields | 7 |
| Metadata macro field accuracy | 1.000 |
| Metadata exact-case rate | 1.000 |
| Metadata evidence coverage | 1.000 |
| Encoding cases | 5 |
| Encoding classification accuracy | 1.000 |

The committed metadata result is for one manually verified repository sample judgment. The
encoding result is for five synthetic characterization cases. These are regression results only.

## Public Supreme Court PDF smoke validation

A separate smoke workflow downloaded four PDFs directly from the Bangladesh Supreme Court website
and ran the package end to end.

| Document | Pages | Retrieval chunks | Metadata/safety checks |
| --- | ---: | ---: | ---: |
| Death Reference No 106 of 2018 | 22 | 41 | passed |
| Death Reference No.117 OF 2017 | 39 | 75 | passed |
| Civil Revision No.205 of 2021 | 4 | 7 | passed |
| Criminal Appeal No. 3346 of 2022 | 7 | 12 | passed |

Across the four documents, 31 of 31 explicit smoke checks passed with no smoke-test failures.
Checks cover case number, court, judges, hearing/judgment dates, expected caption parties, retrieval
chunk creation, and legacy-font safety where applicable.

The real PDFs exposed issues that the original synthetic/unit fixtures did not: flexible date
phrasing, court headings split across lines, Vs. party captions, a false-positive judge extraction,
role-only party labels, and old PDF-font Bangla glyph text. Those cases were converted into
regression tests and parser/encoding fixes before this result was recorded.

Two death-reference PDFs contain legacy font-encoded Bangla sections. The current safe behavior is
to detect and preserve those glyph strings rather than send them to bijoy2unicode and risk
corrupting the source text. In this smoke run 33 candidate legacy-font lines were detected in Death
Reference No 106 and 87 in Death Reference No.117; automatic conversion was not applied.

## Interpretation

The public-PDF smoke test demonstrates that the pipeline can download, ingest, normalize safely,
parse selected caption metadata, preserve provenance, and create retrieval chunks for these four
real documents. It is still not a statistically representative accuracy benchmark.

No general extraction-fidelity or metadata-accuracy percentage is claimed for the wider population
of Bangladesh legal documents.

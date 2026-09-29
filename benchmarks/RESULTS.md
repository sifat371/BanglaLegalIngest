# Seed Validation Results

Measured in GitHub Actions for Stage 6 on 2026-09-29.

## CI

- Python 3.11: lint, tests, and seed benchmark validation passed.
- Python 3.12: lint, tests, and seed benchmark validation passed.
- Test suite: 45 tests passed.

## Committed seed

| Metric | Result |
| --- | ---: |
| Metadata cases | 1 |
| Metadata scored fields | 7 |
| Metadata macro field accuracy | 1.000 |
| Metadata exact-case rate | 1.000 |
| Metadata evidence coverage | 1.000 |
| Encoding cases | 5 |
| Encoding classification accuracy | 1.000 |

## Interpretation

The metadata result is for one manually verified repository sample judgment. The encoding result is
for five synthetic characterization cases. These numbers are regression-validation results only,
not estimates of performance on the wider population of Bangladesh legal documents.

No extraction-fidelity benchmark is reported because the repository does not include the raw source
PDF corpus needed for a manually reviewed extractor comparison.

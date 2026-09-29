# Contributing

Contributions are welcome, especially changes that improve real-document coverage without weakening
provenance or silently guessing legal content.

## Good contributions

Useful contributions include:

- reproducible bug reports with a minimal document/text fixture;
- additional Bangladesh court caption/layout fixtures;
- Unicode Bangla, Bijoy, or legacy-font examples;
- metadata parser improvements with regression tests;
- extractor adapters that return the canonical page-aware schema;
- benchmark annotations and evaluation tooling;
- documentation, examples, and packaging improvements.

Please do not commit private, confidential, copyrighted, or sensitive legal documents unless you
have the right to redistribute them.

## Development setup

```bash
git clone https://github.com/sifat371/BanglaLegalIngest.git
cd BanglaLegalIngest

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

python -m pip install --upgrade pip
python -m pip install -e ".[manual,bangla,dev]"
```

Run the local checks:

```bash
ruff check src tests examples
pytest
bangla-legal-ingest benchmark
```

## Pull requests

Keep pull requests focused. Each behavior change should include a regression test whenever practical.

For metadata parsing changes:

1. include the smallest text fixture that demonstrates the layout;
2. state the expected field values;
3. preserve page-relative evidence;
4. avoid filling unsupported fields with guesses.

For encoding changes:

1. preserve the original text when conversion safety is uncertain;
2. add positive and negative examples;
3. do not interpret plausible-looking Unicode output as proof that a conversion is correct.

For extraction/routing changes:

1. record observable diagnostics;
2. separate usability heuristics from semantic/legal accuracy;
3. avoid hidden filesystem writes or network calls in the core pipeline.

## Benchmarks and claims

Do not add broad accuracy claims from tiny fixtures. Benchmark documentation should state the
population and sample size clearly and distinguish regression checks from representative evaluation.

## Code style

- Python 3.11+;
- Ruff-clean code;
- typed public interfaces where practical;
- Pydantic models for public data contracts;
- deterministic behavior in the core pipeline;
- no LLM or network dependency for basic ingestion.

## Reporting issues

Use GitHub Issues for reproducible bugs and feature requests. For security vulnerabilities, use the
process in [SECURITY.md](SECURITY.md).

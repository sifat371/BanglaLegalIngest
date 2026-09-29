# Release Process

This project is prepared for source and package distribution, but publishing to PyPI should only be
done after the release artifact has been checked and the version is intentionally chosen.

## 1. Update release metadata

Before publishing:

- choose the version in `pyproject.toml`;
- update `src/legal_ingest/__init__.py` to the same version;
- update `CHANGELOG.md`;
- update `CITATION.cff`;
- ensure README validation claims match the latest measured results.

## 2. Run checks

```bash
python -m pip install -e ".[manual,bangla,dev,release]"

ruff check src tests examples
pytest
bangla-legal-ingest benchmark

rm -rf build dist
python -m build
twine check dist/*
```

## 3. Test the built wheel

Use a clean virtual environment:

```bash
python -m venv .release-test
source .release-test/bin/activate

python -m pip install dist/*.whl
bangla-legal-ingest --version
bangla-legal-ingest schema --model result
```

For PDF extraction tests, install the relevant optional dependencies as part of the release test.

## 4. Tag and GitHub release

Create a signed or normal Git tag matching the chosen version and publish release notes summarizing
the changelog.

## 5. PyPI

The intended distribution name is `bangla-legal-ingest`. The import namespace remains
`legal_ingest`; changing the distribution name does not require downstream Python import changes.


The repository is not configured to publish automatically yet. When a PyPI project is created,
prefer PyPI Trusted Publishing / GitHub OIDC over long-lived API tokens.

Do not create a release workflow that contains a PyPI password or token in the repository.

## Pre-1.0 policy

Until version 1.0, the package should remain explicit about API changes and benchmark limitations.
A stable 1.0 release should require a larger representative validation corpus and a clearly defined
compatibility policy.

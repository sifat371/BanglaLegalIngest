"""Packaging invariants for the public BanglaLegalIngest identity."""

import tomllib
from pathlib import Path

import legal_ingest

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_distribution_and_runtime_versions_match() -> None:
    pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert pyproject["project"]["name"] == "bangla-legal-ingest"
    assert pyproject["project"]["version"] == legal_ingest.__version__


def test_primary_and_compatibility_cli_names_are_published() -> None:
    pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    scripts = pyproject["project"]["scripts"]

    assert scripts["bangla-legal-ingest"] == "legal_ingest.cli:main"
    assert scripts["legal-ingest"] == "legal_ingest.cli:main"


def test_repository_urls_use_current_github_name() -> None:
    pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    urls = pyproject["project"]["urls"]

    assert all("sifat371/BanglaLegalIngest" in url for url in urls.values())

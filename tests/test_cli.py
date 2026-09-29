import json

from pypdf import PdfWriter

from legal_ingest.cli import main


def make_blank_pdf(path) -> None:
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    with path.open("wb") as handle:
        writer.write(handle)


def test_cli_prints_document_schema(capsys) -> None:
    exit_code = main(["schema", "--model", "document"])
    output = capsys.readouterr().out

    assert exit_code == 0
    assert '"LegalDocument"' in output
    assert '"source_filename"' in output


def test_cli_ingests_pdf_with_explicit_backend(tmp_path, capsys) -> None:
    path = tmp_path / "blank.pdf"
    make_blank_pdf(path)

    exit_code = main(
        [
            "ingest",
            str(path),
            "--extractor",
            "pypdf",
            "--min-chars",
            "0",
            "--compact",
        ]
    )
    output = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert output["document"]["source_filename"] == "blank.pdf"
    assert output["diagnostics"]["extractor"] == "pypdf"


def test_cli_help_without_subcommand(capsys) -> None:
    exit_code = main([])
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "legal-ingest" in output

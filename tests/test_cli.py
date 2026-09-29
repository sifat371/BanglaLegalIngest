from legal_ingest.cli import main


def test_cli_prints_document_schema(capsys) -> None:
    exit_code = main(["schema", "--model", "document"])
    output = capsys.readouterr().out

    assert exit_code == 0
    assert '"LegalDocument"' in output
    assert '"source_filename"' in output


def test_cli_help_without_subcommand(capsys) -> None:
    exit_code = main([])
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "legal-ingest" in output

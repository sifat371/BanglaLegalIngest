from legal_ingest.parsing import parse_legal_metadata
from legal_ingest.schemas import PageContent

PAGE_ONE = """District: Brahmanbaria.

In the Supreme Court of Bangladesh High Court Division (Criminal Appellate Jurisdiction) Present:

Mr. Justice Md. Zakir Hossain And Mr. Justice Md. Toufiq Inam Death Reference No. 127 of 2018.

The State.

-Versus- Md. Abdul Motin, ----- Condemned-Prisoner.

With Criminal Appeal No. 2184 of 2019.

(Arising out of Jail Appeal No. 330 of 2018.) Md. Abdul Motin, ----- Condemned-Prisoner-Appellant.

-Versus- The State.
"""

PAGE_TWO = """With Criminal Appeal No. 13461 of 2018.

Most. Sahana Khatun, ----- Informant-Appellant.

-Versus- 1. The State.

2. Humayun Mia, ----- Respondents.

Heard On: 28.01.2026 and 03.02.2026.

And Judgment Delivered On: 08.02.2026.

This Death Reference has been made under section 374 of the Code of Criminal Procedure, 1898.
Charges were framed under sections 302/34 of the Penal Code.
"""


def test_parses_sample_caption_fields_with_evidence() -> None:
    metadata = parse_legal_metadata(
        [
            PageContent(page_number=1, text=PAGE_ONE),
            PageContent(page_number=2, text=PAGE_TWO),
        ]
    )

    assert metadata.case_number == "Death Reference No. 127 of 2018"
    assert metadata.case_type == "Death Reference"
    assert metadata.district == "Brahmanbaria"
    assert metadata.court == (
        "Supreme Court of Bangladesh High Court Division "
        "(Criminal Appellate Jurisdiction)"
    )
    assert metadata.judges == ["Md. Zakir Hossain", "Md. Toufiq Inam"]
    assert metadata.hearing_dates == ["28.01.2026", "03.02.2026"]
    assert metadata.judgment_date == "08.02.2026"

    party_names = [party.name for party in metadata.parties]
    assert "The State" in party_names
    assert "Md. Abdul Motin" in party_names
    assert all("\n" not in name for name in party_names)

    assert "section 374 of the Code of Criminal Procedure, 1898" in metadata.citations
    assert "sections 302/34 of the Penal Code" in metadata.citations

    assert metadata.evidence["case_number"][0].page_number == 1
    assert metadata.evidence["judges"][0].page_number == 1
    assert metadata.evidence["hearing_dates"][0].page_number == 2
    assert metadata.evidence["judgment_date"][0].page_number == 2


def test_party_parser_does_not_repeat_legacy_broken_capture() -> None:
    metadata = parse_legal_metadata([PageContent(page_number=1, text=PAGE_ONE)])

    assert all(party.name != "." for party in metadata.parties)
    assert all("Versus" not in party.name for party in metadata.parties)
    assert any(
        party.name == "Md. Abdul Motin" and party.role == "Condemned-Prisoner"
        for party in metadata.parties
    )


def test_empty_pages_return_empty_metadata() -> None:
    metadata = parse_legal_metadata([])

    assert metadata.case_number is None
    assert metadata.parties == []
    assert metadata.evidence == {}

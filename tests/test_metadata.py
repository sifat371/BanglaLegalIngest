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


def test_real_caption_variants_for_court_parties_and_dates() -> None:
    text = """IN THE SUPREME COURT OF
BANGLADESH
HIGH COURT DIVISION
(CRIMINAL APPELLATE JURISDICTION)
Present:
Mr. Justice Md. Shohrowardi
Criminal Appeal No. 3346 of 2022
Nurunnahar
…….Convict appellant
-versus-
The State and another
…….respondents
Heard on 01.06.2025, 02.06.2025 and 22.06.2025
Judgment delivered on 17.07.2025
"""
    metadata = parse_legal_metadata([PageContent(page_number=1, text=text)])

    assert metadata.court == (
        "SUPREME COURT OF BANGLADESH HIGH COURT DIVISION "
        "(CRIMINAL APPELLATE JURISDICTION)"
    )
    assert metadata.judges == ["Md. Shohrowardi"]
    assert [party.name for party in metadata.parties] == [
        "Nurunnahar",
        "The State and another",
    ]
    assert metadata.hearing_dates == ["01.06.2025", "02.06.2025", "22.06.2025"]
    assert metadata.judgment_date == "17.07.2025"


def test_vs_caption_and_textual_judgment_date() -> None:
    text = """In the Supreme Court of Bangladesh
High Court Division
(Civil Revisional Jurisdiction)
Present:
Mr. Justice Md. Jahangir Hossain.
Civil Revision No.205 of 2021.
Sham Debnath and others
.........Petitioners.
Vs.
Shamol Debnath and others
....... Opposite-Parties.
Heard on 21.04.2024 and
Judgment on 22nd April -2024.

The principle of justice will be meet if the order of stay is maintained.
"""
    metadata = parse_legal_metadata([PageContent(page_number=1, text=text)])

    assert metadata.judges == ["Md. Jahangir Hossain"]
    assert [party.name for party in metadata.parties] == [
        "Sham Debnath and others",
        "Shamol Debnath and others",
    ]
    assert metadata.hearing_dates == ["21.04.2024"]
    assert metadata.judgment_date == "22nd April -2024"


def test_empty_pages_return_empty_metadata() -> None:
    metadata = parse_legal_metadata([])

    assert metadata.case_number is None
    assert metadata.parties == []
    assert metadata.evidence == {}

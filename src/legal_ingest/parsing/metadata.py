"""Compose focused parsers into the canonical LegalMetadata model."""

from legal_ingest.parsing.case import parse_case_identity, parse_case_type_only
from legal_ingest.parsing.citations import parse_citations
from legal_ingest.parsing.court import parse_court, parse_district
from legal_ingest.parsing.dates import parse_dates
from legal_ingest.parsing.judges import parse_judges
from legal_ingest.parsing.parties import parse_parties
from legal_ingest.schemas import EvidenceSpan, LegalMetadata, PageContent


def _add_evidence(
    evidence: dict[str, list[EvidenceSpan]],
    field: str,
    spans: list[EvidenceSpan],
) -> None:
    if spans:
        evidence[field] = spans


def parse_legal_metadata(pages: list[PageContent]) -> LegalMetadata:
    """Parse supported metadata deterministically from page-aware text."""

    if not pages:
        return LegalMetadata()

    evidence: dict[str, list[EvidenceSpan]] = {}

    case_number, case_type, case_evidence = parse_case_identity(pages)
    if case_type is None:
        case_type, type_evidence = parse_case_type_only(pages)
    else:
        type_evidence = case_evidence

    court, court_evidence = parse_court(pages)
    district, district_evidence = parse_district(pages)
    judges, judge_evidence = parse_judges(pages)
    parties, party_evidence = parse_parties(pages)
    hearing_dates, judgment_date, hearing_evidence, judgment_evidence = parse_dates(pages)
    citations, citation_evidence = parse_citations(pages)

    _add_evidence(evidence, "case_number", case_evidence)
    _add_evidence(evidence, "case_type", type_evidence)
    _add_evidence(evidence, "court", court_evidence)
    _add_evidence(evidence, "district", district_evidence)
    _add_evidence(evidence, "judges", judge_evidence)
    _add_evidence(evidence, "parties", party_evidence)
    _add_evidence(evidence, "hearing_dates", hearing_evidence)
    _add_evidence(evidence, "judgment_date", judgment_evidence)
    _add_evidence(evidence, "citations", citation_evidence)

    return LegalMetadata(
        case_number=case_number,
        case_type=case_type,
        court=court,
        district=district,
        judges=judges,
        parties=parties,
        hearing_dates=hearing_dates,
        judgment_date=judgment_date,
        citations=citations,
        evidence=evidence,
    )

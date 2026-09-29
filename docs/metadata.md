# Legal Metadata Parsing

Stage 4 migrates legal metadata extraction from the legacy monolithic script into focused,
page-aware deterministic parsers.

## Parsed fields

The canonical LegalMetadata model can now populate:

- case number;
- case type;
- court;
- district;
- judges;
- parties and explicit source roles when present;
- hearing dates;
- judgment date;
- reported-case and supported statute/section citations.

## Provenance

Each populated field can include one or more EvidenceSpan records with a page number and
page-relative character offsets. This makes parser output debuggable and gives downstream
retrieval systems a concrete source location.

## Party parsing

The legacy regex could capture punctuation and surrounding text as party names. Stage 4 instead
looks around caption-level Versus markers line by line. It does not invent
plaintiff/defendant or appellant/respondent labels. A role is populated only when an explicit
dashed role marker is present in the source, such as Condemned-Prisoner or Informant-Appellant.

## Deterministic baseline

No LLM is used for metadata extraction. Unsupported layouts remain empty rather than being filled
with guesses. This gives Stage 6 a reproducible baseline to benchmark field by field.

## Known limitations

- patterns focus on common English-language Bangladesh court captions;
- Bangla-language caption metadata needs dedicated patterns;
- connected appeals can contain several case numbers while the canonical primary case_number field
  currently records the first caption-level match;
- party parsing is conservative and may omit complex multi-party captions;
- citation parsing covers a defined set of common statute names/report abbreviations.

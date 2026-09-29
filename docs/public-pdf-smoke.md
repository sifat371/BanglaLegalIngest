# Public Supreme Court PDF Smoke Test

This repository includes an external smoke-test utility for exercising the full ingestion module on
real public judgments without committing the PDFs themselves.

## Documents

The workflow currently downloads four PDFs from the Bangladesh Supreme Court website:

1. Death Reference No 106 of 2018
   https://www.supremecourt.gov.bd/resources/documents/3425449_Death_Ref_106of2018.pdf
2. Death Reference No.117 OF 2017
   https://www.supremecourt.gov.bd/resources/documents/2335716_Death_Reference_No_117_of_20217.pdf
3. Civil Revision No.205 of 2021
   https://www.supremecourt.gov.bd/resources/documents/2102148_civil_revision_no_205_2021_dt_22_4_24.pdf
4. Criminal Appeal No. 3346 of 2022
   https://www.supremecourt.gov.bd/resources/documents/2027591_Cril_Rev_No_3346_of_2022.pdf

The PDFs are downloaded only for the workflow run and are not checked into the repository.

## What the smoke test exercises

The runner calls the same public package APIs intended for downstream consumers. It verifies:

- real PDF download and parsing;
- automatic extraction;
- page preservation;
- case identity, court and judge parsing;
- common hearing/judgment date formats;
- Versus and Vs. party-caption variants;
- safe legacy-font Bangla detection;
- retrieval chunk creation and provenance.

The current fixture expectations are explicit in scripts/public_pdf_smoke.py.

## Measured run

The 2026-09-29 run ingested all four PDFs, produced retrieval chunks for every document, and passed
31 of 31 explicit metadata/safety checks with no failures.

The run also identified real legacy-font Bangla in both death-reference judgments. Those lines are
preserved unchanged with a warning because bijoy2unicode is not a reliable decoder for that PDF
glyph representation.

## Run manually

Use the GitHub Actions workflow named Public PDF Smoke Test, or download the four PDFs locally and
run:

~~~bash
python scripts/public_pdf_smoke.py path/to/downloaded/pdfs --output smoke-report.json
~~~

This workflow depends on the external Supreme Court website, so it is intentionally separate from
the required unit-test CI.

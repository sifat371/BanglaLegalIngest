# Project Naming and Compatibility

The repository was renamed to **BanglaLegalIngest** to make its scope immediately clear to public
users.

The project intentionally uses different names at different integration layers:

| Layer | Name |
| --- | --- |
| GitHub repository / project | `BanglaLegalIngest` |
| Python distribution | `bangla-legal-ingest` |
| Python import package | `legal_ingest` |
| Primary CLI | `bangla-legal-ingest` |
| Compatibility CLI alias | `legal-ingest` |

## Why keep `legal_ingest`?

Changing the repository name does not require changing Python imports. Keeping `legal_ingest`
avoids unnecessary churn in downstream code and keeps imports concise:

~~~python
from legal_ingest import LegalDocumentPipeline
~~~

## CLI compatibility

New documentation uses:

~~~bash
bangla-legal-ingest ingest judgment.pdf
~~~

Existing scripts that call:

~~~bash
legal-ingest ingest judgment.pdf
~~~

continue to work because both console-script names point to the same CLI entry point.

## Git remotes after the GitHub rename

GitHub normally redirects the old repository URL, but existing clones should update their remote so
configuration and documentation remain explicit:

~~~bash
git remote set-url origin https://github.com/sifat371/BanglaLegalIngest.git
git remote -v
~~~

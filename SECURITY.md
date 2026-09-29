# Security Policy

## Supported versions

The project is currently in public alpha. Security fixes are applied to the latest code on the
`main` branch.

## Reporting a vulnerability

Please do not publish exploit details, malicious sample files, credentials, tokens, or private legal
documents in a public issue.

Use GitHub's private vulnerability reporting feature for this repository if it is available. If it
is not available, open a minimal public issue asking for a private contact channel without including
sensitive details.

Useful reports include:

- affected version or commit;
- the component involved;
- a minimal safe reproduction;
- expected and observed behavior;
- potential impact.

## Security scope

This package parses untrusted PDF content through optional third-party extraction libraries.
Applications that expose uploads to end users should additionally enforce file-size limits,
resource/time limits, sandboxing where appropriate, dependency updates, and normal malware/file
validation practices.

The project does not execute macros or embedded PDF scripts intentionally, but downstream
deployments remain responsible for their threat model.

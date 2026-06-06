# Security Policy

## Scope

This repository is a document-intelligence and extraction engine. It is not a hosted production service.

Security concerns still matter, especially around:

- unsafe dependency upgrades
- arbitrary file handling
- path traversal bugs
- accidental leakage of private documents
- misuse of extracted outputs as authoritative legal advice

## Reporting a vulnerability

Please do **not** open a public GitHub issue for a suspected security problem.

Instead, report it privately to the maintainer with:

- a short description
- affected files or commands
- reproduction steps
- impact assessment
- any proposed mitigation

## What counts as a security issue here

Examples:

- a script can write outside the repo unexpectedly
- unsafe handling of untrusted file paths
- secrets accidentally committed
- dependency behavior that creates a credible remote-code or data-exfiltration risk

## What does not count

Examples:

- extraction inaccuracy by itself
- stale insurer/product data by itself
- disagreements about product recommendations

Those are important quality/product issues, but not necessarily security issues.

## Responsible use note

Outputs from this repo should not be treated as legal advice, underwriting advice, or a substitute for insurer-approved current documents.

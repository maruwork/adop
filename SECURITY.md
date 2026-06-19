# Security Policy

## Supported Versions

| Version | Supported |
| --- | --- |
| latest | yes |

## Trust Model

ADOP is a local, single-operator CLI. Its inputs are treated as operator-trusted, and its boundaries are scoped accordingly:

- **Operator-controlled inputs are trusted.** `@file` JSON arguments (e.g. `--couplings-json @path`), `render-html --output`, and `init --overlay` / `--artifact-root` read or write wherever the operator points them, by design. Do not pass untrusted/attacker-supplied values to these flags.
- **The artifact-root boundary is opt-in.** It is enforced only when `--target-project-root` is given without `--allow-project-impact`, and it protects against *writing into the target project's tree during a trial*. Read commands (`list`, `show`, `couplings`, `scan`) intentionally read whatever root they are pointed at.
- **`adop_sync` requires a trusted canonical source.** It copies the files named in that source's `adop.json`. Manifest paths are validated to be project-relative (no `..`, no absolute/drive-relative roots) so a manifest cannot direct writes outside `--target`, but you should still only sync from a canonical repo you trust.
- **`scan` is bounded.** It skips files larger than 5 MB and does not follow symlinked directories.

Running ADOP against fully untrusted inputs (e.g. a CI job feeding attacker-controlled `@file` paths or a cloned repo whose `adop.json` you have not reviewed) is outside the supported model.

## Reporting a Vulnerability

Use [GitHub private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing/privately-reporting-a-security-vulnerability) to submit security issues.

Private disclosure is supported from day one.

Include the affected version, a description of the issue, and reproduction steps if available.

Response is best effort with no fixed SLA at this stage.

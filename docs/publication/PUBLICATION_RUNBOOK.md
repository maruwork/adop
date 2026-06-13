# ADOP Publication Runbook

Status: Active

## Purpose

Provide one ordered runbook that another operator can execute to publish `ADOP` without rediscovering shelf rules.

## Preconditions

- `OWNER_DECISION_PACKET.md` is fully resolved
- `PUBLIC_POLICY_PROMOTION_MATRIX.md` is accepted
- `PUBLIC_VERIFICATION_CONTRACT.md` is accepted
- no hidden common-shelf restructure work remains

## Runbook

1. Confirm every blocking decision in `OWNER_DECISION_PACKET.md` is filled.
2. Confirm exported/public files using `REPO_EXPORT_GUIDE.md` and `REPO_EXPORT_CHECKLIST.md`.
3. Prepare the standalone repo root with only the carried files listed in `REPO_EXPORT_GUIDE.md`.
4. Add the chosen license file.
5. Promote `docs/publication/CONTRIBUTING_DRAFT.md` and `docs/publication/SECURITY_DRAFT.md` only after owner-specific values replace draft placeholders.
6. Keep internal-only docs out of the first public repo unless the owner intentionally expands the surface.
7. Run the full command set in `PUBLIC_VERIFICATION_CONTRACT.md`.
8. If verification passes, apply the chosen CI scope.
9. Publish with the chosen host/owner/visibility settings.

## Stop Points

- a blocking owner decision is still open
- a draft policy still lacks owner-specific values
- exported files still depend on monorepo-only context
- verification fails under the documented shell assumptions

## Rollback Points

- before repository creation: stop with no external effects
- after export but before publication: revise the exported copy, then rerun verification
- after CI wiring but before publication: fix the verification surface, then rerun

## Not In This Document

- actual credentials
- live host configuration
- visibility toggles performed in real time

## Current Chosen Defaults

- license: `MIT`
- host/owner: `fumimaruwork`
- repository name: `adop`
- initial visibility: `private`
- public contributions: accepted from day one with maintainer review
- security intake: GitHub private vulnerability reporting if enabled
- CI posture: required at repo creation

## Draft Promotion Note

- `docs/publication/CONTRIBUTING_DRAFT.md` and `docs/publication/SECURITY_DRAFT.md` remain draft files in this monorepo shelf
- remove `Draft` status only in the exported/public repo copy when the chosen wording is promoted

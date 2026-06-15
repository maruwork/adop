# ADOP Public Policy Promotion Matrix

Status: Active

## Purpose

Define the fate of each draft/pre-public policy document before publication.

## Matrix

| File | Current Status | Publication Fate | Required Owner Input | Notes |
| --- | --- | --- | --- | --- |
| `docs/publication/CONTRIBUTING_DRAFT.md` | draft-only | promote with edits | issue/PR policy | must stop saying "draft" before publication |
| `docs/publication/SECURITY_DRAFT.md` | draft-only | promote with edits | security intake posture | must not imply a contact channel until owner chooses one |
| `RELEASE_BOOTSTRAP_NOTES.md` | internal prep | keep internal | none beyond go-live operator use | operational note, not public policy |
| `OWNER_DECISION_PACKET.md` | internal execution authority | keep internal | all blocking owner decisions | used to drive publication, not to publish directly |
| `PUBLISHABLE_HOLD_CHECKLIST.md` | internal gate | keep internal | none | proves readiness before go-live |

## Promotion Rule

- `promote with edits` means the file can become public only after owner-specific values replace placeholders and draft language.
- `keep internal` means the file remains a private execution aid and does not belong in the first public repository surface.

## Fail-Close Rule

If a file has no explicit fate in this matrix, do not proceed to publication.

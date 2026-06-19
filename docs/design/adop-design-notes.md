# ADOP Design Notes

Created: 2026-06-11
Updated: 2026-06-12

---

## Role of ADOP

A SSOT for recording and managing the full relationship lifecycle with external tools.

Covers the entire period from initial interest through retirement. The CLI is only an interface for writing and validating records correctly.

---

## Differences from Similar Tools

| Tool | Common ground | Difference from ADOP |
|---|---|---|
| ADR (adr-tools / MADR) | Recording tool adoption decisions | Records decisions after the fact only. No current-state or trial management. |
| Backstage | Software catalog and lifecycle management | Infrastructure-scale. Too heavy for individuals or small teams. |
| RFC process | Proposal → approval flow | Ends at approval. No trial management or structured artifacts. |

The closest analog to ADOP is ADR, but the decisive difference is state management ("where are we right now?") and enforced transitions that prevent adoption without a trial.

---

For the normative state machine, artifact type mappings, and base attribute field schema, see [`docs/design/adop-lifecycle-schema-design.md`](adop-lifecycle-schema-design.md).

---

## Cross-Project Value

Because artifacts are JSON, multiple artifact roots can be aggregated across projects.

- A rejection reason from Project A can inform a judgment in Project B
- Functions as a personal SSOT for tool adoption history
- "What is being used in which project right now" is visible in one place

---

## Confirmed Design Decisions

1. **`watch` lives inside ADOP** — Interest records belong in the SSOT too. `watch` is the entry point; transition to `proposed` starts formal evaluation.
2. **`migrating` is an independent state** — Distinct from `deprecated` (decision made, work not yet started). It is a standalone state representing active migration work in progress.
3. **`reject` is terminal for a scene lane** — Re-evaluation does not reopen a rejected lane; it must use a new `related_scene`. A candidate can be rejected before any trial (from `proposed` / `blocked`) or after a pause (from `hold`) via `adop reject`, in addition to a `reject` verdict at trial close.

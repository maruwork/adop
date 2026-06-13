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

## State Model

### State Transitions

```
watch ──→ proposed ──→ trial-ready ──→ in-trial
              │                           │
           blocked                  ┌─────┼─────┐
           │    │                promote  hold  reject
        (lift)  (permanent)         │      │
          ↓       ↓           deprecated  ──→ trial-ready (reopen)
       proposed  reject             │           └──→ reject
                                migrating
                                   │
                                archived
                         (direct from deprecated also valid)
```

Entry point: `watch`
Terminal states: `reject`, `archived`

### What Each State Answers

| State | Question it answers |
|---|---|
| watch | Things noticed but not yet at the evaluation stage |
| proposed | Things formally decided to evaluate |
| blocked | Things to trial but stopped by external constraints (legal, security, budget) |
| trial-ready | Things waiting to start a trial |
| in-trial | Things currently under evaluation |
| promote | Things adopted and in active use |
| hold | Things paused but not discarded |
| reject | Things decided not to use, and why |
| deprecated | Adopted things now moving toward retirement |
| migrating | Things with active migration work in progress |
| archived | Things previously used but now fully ended |

### Required Record Fields per State

| State | Required fields |
|---|---|
| watch | tool name, interest reason |
| proposed | use case, proposer, why now |
| blocked | block reason, unblock condition, owner |
| trial-ready | candidates compared, selection reason |
| in-trial | executor, evaluation criteria, scope, start date |
| promote | decision reason, approved uses, prohibited uses |
| hold | pause reason, resume condition |
| reject | rejection reason, confirmed failure conditions |
| deprecated | retirement reason, replacement candidates, timeline |
| migrating | migration target, migration plan |
| archived | end date, successor tool |

---

## Base Attribute Fields

Base attributes a tool registration should carry. These serve as axes for filtering and querying.

| Field | Purpose |
|---|---|
| `platform` | OS/environment compatibility (windows / mac / linux / any) |
| `license` | License type. Axis for determining commercial use eligibility. |
| `cost` | free / paid / freemium |
| `data_flow` | Data destination, types, and control. Entry point for security judgment. |
| `version` | Version at time of trial or adoption |
| `category` | Tool type (MCP Server / CLI / Library / API Service, etc.) |
| `ai_compatibility` | AI environments it runs in (claude / cursor / copilot / openai / any, etc.) |

### data_flow Structure

`data_flow` is held as a struct, not a scalar value.

```yaml
data_flow:
  destination: local | vendor-api | third-party | unknown
  data_types: [prompts, code, file-content, credentials, ...]
  opt_in: true | false   # whether it can be turned off by default
```

If `opt_in: false` and `data_types` includes `code` or `credentials`, the tool is an immediate candidate for a use prohibition review.

### Field Mutability

Some fields change over time. When a field changes, record the reason and date.

| Field | Example of change |
|---|---|
| `cost` | free → paid transition |
| `data_flow` | local-only → cloud sync added |
| `license` | license change in a new version |
| `version` | update to a new version after trial |

### Query Examples

- Which tools currently in use are Claude-specific? → `state=promote AND ai_compatibility=claude`
- What would stop working if we moved to Cursor? → `state=promote AND ai_compatibility=claude NOT cursor`
- List all tools that send data to the cloud → `data_flow.destination=vendor-api OR third-party`
- Find tools where data transmission cannot be disabled by default → `data_flow.opt_in=false`
- Find tools not licensed for commercial use → `license=NC`

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

## Open Design Questions

1. **Re-evaluation route for `reject`** — Keep it as a terminal state, or allow conditional transitions back to `watch` or `proposed`?

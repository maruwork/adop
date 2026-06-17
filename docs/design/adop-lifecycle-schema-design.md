# ADOP Lifecycle Schema Design

Status: Active

## Purpose

Define the state machine and artifact schema extensions for ADOP's full tool lifecycle.
This document is an extension plan on top of the existing Case B (scene-lane lifecycle with tool identity carried in artifacts) architecture.

---

## 1. Adoption Unit

The lifecycle tracking unit is the **scene lane** rooted at `related_scene`.
Tool identity and the narrower `adoption_unit` travel inside the lane artifacts.
State is inferred from the latest lifecycle-relevant artifacts for that scene lane, not stored as an explicit field.
All artifacts are append-only. There is no `updated_at`.

---

## 2. State Machine

### 2.1 State to Artifact Type Mapping

| State | Artifact type | Status |
|---|---|---|
| watch | `watch-note` | new |
| proposed | `candidate-intake-note` | existing |
| blocked | `blocked-note` | new |
| trial-ready | `comparison-note` | existing |
| in-trial | `trial-packet` | existing |
| promote | `promotion-note` | existing |
| hold | `hold-note` | new |
| reject | `reject-note` | existing |
| deprecated | `deprecation-note` | new |
| migrating | `migration-note` | new |
| archived | `archive-note` | new |

### 2.2 Transitions

```
watch ──→ proposed ──→ trial-ready ──→ in-trial
              │                           │
           blocked                  ┌─────┼─────┐
           │    │                promote  hold  reject
      (unblock)  (permanent)         │      │
          ↓          ↓          deprecated  ──→ trial-ready (resume)
       proposed    reject            │           └──→ reject
                               ┌────┴────┐
                           migrating   archived
                               │
                            archived
```

### 2.3 Entry and Terminal States

| Role | State | Artifact type |
|---|---|---|
| Entry | `watch` | `watch-note` |
| Terminal | `reject` | `reject-note` |
| Terminal | `archived` | `archive-note` |

### 2.4 Transition Table

| From | To | Trigger | Creates artifact |
|---|---|---|---|
| — | watch | tool noticed | `watch-note` |
| watch | proposed | use_case decided, formal evaluation started | `candidate-intake-note` |
| proposed | trial-ready | comparison complete, tool selected | `comparison-note` |
| proposed | blocked | external constraint discovered | `blocked-note` |
| proposed | reject | rejected before trial | `reject-note` |
| blocked | proposed | constraint lifted | `candidate-intake-note` |
| blocked | reject | constraint is permanent | `reject-note` |
| trial-ready | in-trial | trial started | `trial-packet` |
| in-trial | promote | trial succeeded | `promotion-note` |
| in-trial | hold | trial paused | `hold-note` |
| in-trial | reject | trial failed | `reject-note` |
| hold | trial-ready | trial resumed | `comparison-note` |
| hold | reject | tool discarded after pause | `reject-note` |
| promote | deprecated | retirement decision made | `deprecation-note` |
| deprecated | migrating | active migration started | `migration-note` |
| deprecated | archived | retired without migration | `archive-note` |
| migrating | archived | migration complete | `archive-note` |

`reject` is terminal for the scene lane. Re-evaluation is allowed only under a
new `related_scene`; the CLI does not reopen a rejected lane back into `watch`,
`proposed`, or `trial-ready`.

---

## 3. New Artifact Types

Required fields for each new artifact type.
All new artifacts also carry `schema_version`, `artifact_type`, `artifact_id`, `created_at`, `related_scene`, `candidate_or_tool`.

### watch-note

| Field | Required | Notes |
|---|---|---|
| `interest_reason` | yes | why this tool is on the radar |
| `related_scene` | no | use_case if already known; omit if not yet decided |

**Validation exception**: `watch-note` is the only artifact type where `related_scene` is optional. All other artifact types require `related_scene`. This exception must be handled explicitly in `adop_validation.py`.

### blocked-note

| Field | Required |
|---|---|
| `block_reason` | yes |
| `unblock_condition` | yes |
| `owner` | yes |

### deprecation-note

| Field | Required |
|---|---|
| `retirement_reason` | yes |
| `replacement_candidates` | yes |
| `timeline` | yes |

### migration-note

| Field | Required |
|---|---|
| `migration_target` | yes |
| `migration_plan` | yes |

### archive-note

| Field | Required |
|---|---|
| `end_date` | yes |
| `successor_tool` | no |

---

## 4. Basic Tool Attributes

Tool-level attributes added to `candidate-intake-note` at intake time.
Optional in `watch-note` (may not be known yet), required at `candidate-intake-note`.

| Field | Values |
|---|---|
| `platform` | `windows`, `mac`, `linux`, `any`, `unknown` |
| `license` | license identifier |
| `cost` | `free`, `paid`, `freemium`, `unknown` |
| `data_flow` | structured object — see below |
| `version` | version at time of intake |
| `category` | `mcp-server`, `cli`, `library`, `api-service`, etc. |
| `ai_compatibility` | `claude`, `cursor`, `copilot`, `openai`, `any`, `unknown`, etc. |

### data_flow structure

| Field | Values | Description |
|---|---|---|
| `destination` | `local`, `vendor-api`, `third-party`, `unknown` | where data is sent |
| `data_types` | list | `prompts`, `code`, `file-content`, `credentials`, etc. |
| `opt_in` | `true`, `false` | whether transmission can be disabled by default |

A record with `opt_in: false` and `data_types` containing `code` or `credentials` is an immediate candidate for prohibited use review.
`unknown` is allowed for guided intake when the team wants to open a bounded record before all attributes are collected, but the unknown itself must be written explicitly.

### Attribute changes

Attributes are set at intake and do not change in place (append-only).
If an attribute changes significantly (e.g., free → paid, local → cloud sync added), that is typically a trigger for a state transition to `deprecated`.

Promotion is blocked until the latest intake for the scene has no `unknown`
tool attributes remaining.

### Declared Usage Tracking

ADOP tracks adoption usage as declared metadata, not as observed hook/log
telemetry.

| Field | Values | Notes |
|---|---|---|
| `recording_mode` | `guided`, `explicit` | whether the operator used the guided path or the full explicit path |
| `recording_source` | `manual-cli`, `quick-intake`, `quick-compare`, `quick-trial`, `quick-close-trial`, `unblock` | which CLI surface created the record |

These fields are required on `candidate-intake-note`, `comparison-note`,
`trial-packet`, `trial-result`, `judgment-report`, `hold-note`, `reject-note`,
and `promotion-note`.

---

## 4b. Tool-to-File Coupling (Entanglement)

External tools must be recorded as external, AND their entanglement with project
files must be reportable — this is the core input for judging whether a tool can
be cleanly detached at `deprecated` / `migrating` / `archived`.

### coupling-note

`coupling-note` is an artifact type but **not a lifecycle state**: a tool can have
couplings in any state. It is therefore added to `ARTIFACT_TYPES` (prefix `cp`) but
NOT to `SUMMARY_STATES`.

Capture is **declared** (operator records it), consistent with ADOP's append-only,
declared-disposition model. Each `coupling-note` is a complete **snapshot** of the
current coupling set for one `(tool, use-case)`; the report uses the latest note per
pair (latest-wins). Detaching a file = record a new snapshot without it.

| Field | Required | Notes |
|---|---|---|
| `related_scene` | yes | the use-case |
| `candidate_or_tool` | yes | the external tool |
| `couplings` | yes | non-empty list of coupling entries |

Each coupling entry:

| Field | Required | Values |
|---|---|---|
| `path` | yes | project-relative file path |
| `coupling_type` | yes | `config`, `import`, `invocation`, `generated`, `data-write`, `reference` |
| `removal_cost` | yes | `clean`, `edit`, `entangled` |
| `note` | no | free text |

`coupling_type` answers *how* the tool is entangled; `removal_cost` is the
**癒着度** — how hard it is to detach. The report headline per tool is the worst
`removal_cost` across its files (`clean` < `edit` < `entangled`): one `entangled`
file means migration is heavy.

### Commands

- `couple` — record a coupling-note (snapshot). Couplings given as repeated
  `--couple 'PATH|TYPE|COST[|NOTE]'` or `--couplings-json` (`@path` reads a file).
- `couplings` — report latest coupling per `(tool, use-case)`, text or `--json`.
- `summary` — "Tool Entanglement" section shows file count + worst detachment cost.

## 5. Artifact ID Prefixes

Prefixes for new artifact types to be added to `ARTIFACT_ID_PREFIX` in `adop_types.py`.

| Artifact type | Prefix |
|---|---|
| `watch-note` | `wt` |
| `blocked-note` | `bl` |
| `deprecation-note` | `dp` |
| `migration-note` | `mg` |
| `archive-note` | `ar` |
| `coupling-note` | `cp` |

---

## 6. Fixed Decisions

| Topic | Decision |
|---|---|
| Usage tracking | Declared-only. Canonical artifacts carry `recording_mode` and `recording_source`; ADOP does not treat hook/log observation as canonical state input. |
| `reject` recyclability | `reject` is terminal for a scene lane. A materially new evaluation must use a new `related_scene`. |
| Coupling auto-scan (current contract) | `scan` is advisory only. Only `couple` writes canonical coupling history; observed-vs-declared drift detection is out of scope for the current generic contract. |

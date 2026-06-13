# ADOP Lifecycle Schema Design

Status: Active

## Purpose

Define the state machine and artifact schema extensions for ADOP's full tool lifecycle.
This document is an extension plan on top of the existing Case B (use-case/scene as adoption unit) architecture.

---

## 1. Adoption Unit

The adoption unit is **use-case + tool**. One adoption = one (tool, use-case) pair.
State is inferred from the latest artifact for that pair, not stored as an explicit field.
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
| hold | `reject-note` (verdict=hold) | existing |
| reject | `reject-note` (verdict=reject) | existing |
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
| in-trial | hold | trial paused | `reject-note` (verdict=hold) |
| in-trial | reject | trial failed | `reject-note` (verdict=reject) |
| hold | trial-ready | trial resumed | `comparison-note` |
| hold | reject | tool discarded after pause | `reject-note` |
| promote | deprecated | retirement decision made | `deprecation-note` |
| deprecated | migrating | active migration started | `migration-note` |
| deprecated | archived | retired without migration | `archive-note` |
| migrating | archived | migration complete | `archive-note` |

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
| `platform` | `windows`, `mac`, `linux`, `any` |
| `license` | license identifier |
| `cost` | `free`, `paid`, `freemium` |
| `data_flow` | structured object — see below |
| `version` | version at time of intake |
| `category` | `mcp-server`, `cli`, `library`, `api-service`, etc. |
| `ai_compatibility` | `claude`, `cursor`, `copilot`, `openai`, `any`, etc. |

### data_flow structure

| Field | Values | Description |
|---|---|---|
| `destination` | `local`, `vendor-api`, `third-party`, `unknown` | where data is sent |
| `data_types` | list | `prompts`, `code`, `file-content`, `credentials`, etc. |
| `opt_in` | `true`, `false` | whether transmission can be disabled by default |

A record with `opt_in: false` and `data_types` containing `code` or `credentials` is an immediate candidate for prohibited use review.

### Attribute changes

Attributes are set at intake and do not change in place (append-only).
If an attribute changes significantly (e.g., free → paid, local → cloud sync added), that is typically a trigger for a state transition to `deprecated`.

---

## 5. Artifact ID Prefixes

Prefixes for new artifact types to be added to `ARTIFACT_ID_PREFIX` in `adop_types.py`.

| Artifact type | Prefix |
|---|---|
| `watch-note` | `wt` |
| `blocked-note` | `bl` |
| `deprecation-note` | `dp` |
| `migration-note` | `mg` |
| `archive-note` | `ar` |

---

## 6. Open Items

| Item | Decision needed |
|---|---|
| Usage tracking | Declared (manual record) vs. observed (hook/log integration); what fields to carry |
| `reject` recyclability | Terminal state, or allow re-entry to `watch` or `proposed` under conditions |

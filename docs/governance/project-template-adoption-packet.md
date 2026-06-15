# ADOP Project Template Adoption Packet

Status: Active

## 1. Purpose

Fix the local rules for applying `pj-template` to `adop`.

## 2. Reading Route

See `README.md` for the full reading order.

### 2.1 Entry Split

- entry for overall understanding:
  - `README.md`
- entry for current work:
  - `none`
- entry for design:
  - `docs/design/`
- entry for execution surfaces:
  - `shared/python/`
  - `docs/checklists/`
  - `shared/templates/`

## 3. Governance Shelf

- governance shelf:
  - `docs/governance/`
- governance shelf entry:
  - `docs/governance/project-template-adoption-packet.md`
- common shelf:
  - `common/`
- common entry:
  - `common/README.md`

### 3.5 Template Branch Decisions

- current ownership:
  - `no-current-canonical`
- restart aid:
  - `restart-aid-none`
- publication mode:
  - `publication-planned`
- structure weight:
  - `standard`
- runtime placement:
  - `runtime-local`

### 3.6 Branch Consequence Record

- current ownership consequence:
  - `none`
- restart aid consequence:
  - `none`
- publication consequence:
  - `PUBLICATION_RUNBOOK.md`
- runtime consequence:
  - `shared/python/`
  - `docs/checklists/`
  - `shared/templates/`

### 3.7 Rule Ownership Split

- what the shared progression rule decides:
  - common principles for project progression / stop / writeback
- what template-side branches decide:
  - no-current-canonical
  - publication-planned
  - runtime-local
- what remains truly project-specific:
  - ADOP artifact schema and lifecycle surface
  - publication-readiness draft and execution docs
  - generic versus project-local overlay boundary

### 3.8 Bundle Adoption

- bundle declaration surface:
  - `none`
- continue check surface:
  - `none`
- close / residual split adoption:
  - `no`
- template version status:
  - `upgraded-template scaffold`

## 4. Read / Write / No-Touch

### Read

- `AGENTS.md`
- `CLAUDE.md`
- `README.md`
- `common/`
- `docs/`
- `shared/python/`
- `docs/checklists/`
- `shared/templates/`
- `docs/design/`
- `docs/publication/`

### Write

- `common/`
- `docs/governance/`
- `docs/`
- `docs/design/`
- `docs/publication/`

### No-Touch

- `__pycache__/` (any code shelf, e.g. `shared/python/`, `tests/`)
- `.pytest_cache/`

## 5. Current Shelf Classification

Authoritative shelf authority and class definitions: `docs/governance/project-boundary-register.md`.

- no-current-canonical: `yes` — this project does not currently keep a daily current board as its canonical route

## 6. Runtime And Caller-Sensitive Paths

- runtime-sensitive paths:
  - `shared/python/`
  - `docs/checklists/`
  - `shared/templates/`
- caller-sensitive rename / move:
  - `shared/python/`
  - `docs/checklists/`
  - `shared/templates/`

## 7. Expected Local Deliverables

- `common/README.md`
- `docs/governance/project-template-adoption-packet.md`
- `docs/governance/project-file-taxonomy.md`
- `docs/governance/project-boundary-register.md`
- `docs/governance/project-workspace-and-artifact-policy.md`

## 8. Output And Reporting

- generated / scratch work:
  - `workspace/`
- governance decision writeback:
  - `docs/governance/`
- generated residue is not canonical
- helper compression surfaces remain non-authoritative

## 8.5 Project-Specific Exception Register

| exception | reason template could not absorb it | related branches | owner decision | keep path |
|---|---|---|---|---|
| root publication and draft docs remain at repo root | publication-prep materials already use root placement as the public-facing surface | `publication-planned`, `runtime-local` | no | root markdown docs |

## 9. Owner-Only Decisions

- archive / restore / delete
- moving or renaming runtime-sensitive shelves
- reclassifying publication docs into historical or support
- final publication go / no-go decisions

## 10. Stop Conditions

- a new top-level shelf becomes necessary
- generated residue appears to become canonical without review
- runtime-sensitive paths would need rename or move
- root publication doc placement would need replacement rather than coexistence

## 11. Completion Rule

- governance route is explicit
- local common shelf is explicit
- no-current-canonical status is explicit
- runtime-sensitive paths are explicit
- generated residue is separated from canonical shelves
- owner-only decisions remain owner-only

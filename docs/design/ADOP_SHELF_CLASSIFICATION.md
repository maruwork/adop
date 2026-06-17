# ADOP Shelf Classification

Status: Active

## Purpose

Separate generic `ADOP` authority from project-local adoption execution and current-state tracking.

## Generic ADOP Authority

These shelves/files define reusable common ADOP behavior.

- `adop.json`
- `shared/python/`
- `docs/checklists/`
- `shared/templates/`
- `docs/design/`
- `README.md`
- `docs/ADOP_GENERIC_QUICKSTART.md`

## Project-Local Overlay

These belong outside ADOP generic authority.

- current trial boards
- current summary or canonical current state
- project-local operator flow
- project-local landing target authority
- project-local decision logs
- project-local hook / queue / runbook activation details

## Authority Contract

ADOP common owns — do not redefine on the project side:

| What | Owned by ADOP common |
|---|---|
| Artifact schema and field definitions | `adop_types.py`, `adop_validation.py` |
| Lifecycle states and valid transitions | `adop_state_machine.py`, `adop_types.py` |
| CLI commands and their behavior | `adop_cli.py` |
| Coupling vocabulary (`coupling_type`, `removal_cost`) | `adop_types.py` |
| Generic adoption checklist | `docs/checklists/` |
| Adoption note template | `shared/templates/external-tool-adoption-note-template.md` |

Project-local overlay owns — do not put in ADOP common:

| What | Owned by project |
|---|---|
| Artifact root (the actual artifact files) | project-local path |
| Runtime copy of `adop_*.py` + `common.py` | project-local path, synced from canonical |
| Current adoption register and summary | project-local |
| Operator flow (who runs what, when) | project-local |
| Landing target authority | project-local |
| Coupling records for project files | project-local artifact root |

## Project-Local Overlay Minimum Structure

A compliant project-local overlay must declare:

| Item | Purpose |
|---|---|
| Artifact root path | bounded directory where ADOP CLI reads and writes artifacts |
| Runtime copy path + sync date | local `adop_*.py` copy; must be verified against canonical |
| Active use cases table | current scene lanes and their lifecycle states |
| Operator flow | who drives each stage in this project |
| Landing target | where a promoted tool goes in this project's architecture |

Use `shared/templates/project-local-adop-overlay-template.md` as the starting form.

## Reading Rule

1. Read generic ADOP authority first.
2. Read project-local overlay only after the generic model is understood.
3. Do not treat project-local current state as if it were ADOP core authority.
4. Do not redefine what ADOP common owns on the project side.

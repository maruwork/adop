# ADOP Shelf Classification

Status: Active

## Purpose

Separate generic `ADOP` authority from project-local adoption execution and current-state tracking.

## Generic ADOP Authority

These shelves/files define reusable common ADOP behavior.

- `python/`
- `checklists/`
- `templates/`
- `roadmap/`
- `tasks/`
- `design/`
- `README.md`
- `ADOP_SHELF_CLASSIFICATION.md`
- `ADOP_GENERIC_QUICKSTART.md`

## Project-Local Overlay

These belong outside `common/adop`.

- current trial boards
- current summary or canonical current state
- project-local operator flow
- project-local landing target authority
- project-local decision logs
- project-local hook / queue / runbook activation details

## Reading Rule

1. Read generic ADOP authority first.
2. Read project-local overlay only after the generic model is understood.
3. Do not treat project-local current state as if it were ADOP core authority.


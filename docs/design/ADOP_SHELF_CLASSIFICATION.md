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

## Reading Rule

1. Read generic ADOP authority first.
2. Read project-local overlay only after the generic model is understood.
3. Do not treat project-local current state as if it were ADOP core authority.

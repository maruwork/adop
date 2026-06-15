# ADOP Generic Quickstart

Status: Active

## Purpose

Provide the shortest bounded path to understand and verify generic ADOP.

## Read Order

1. `README.md`
2. `docs/design/ADOP_SHELF_CLASSIFICATION.md`
3. `docs/checklists/external-tool-adoption-checklist.md`
4. `shared/templates/external-tool-adoption-note-template.md`
5. `shared/python/adop_types.py`
6. `shared/python/adop_cli.py`

## Fastest Verification

The authoritative command set is in `docs/publication/PUBLIC_VERIFICATION_CONTRACT.md`.

Set `CLI=shared/python/adop_cli.py; SRC=shared/python` and run the Mandatory Checks there.

## What This Proves

- CLI can start
- artifact schema and lifecycle can be exercised
- bounded no-impact trial flow can be recorded
- lint can validate the resulting artifact root

## What This Does Not Prove

- project-local landing target ownership
- project-local operator workflow
- project-local hook / runbook / queue integration

# ADOP governance entry point

**Last updated**: 2026-06-16

This file is the root stop-rule surface for delegated work inside this repository.

## Scope

- Applies to this repository.
- Root entry for delegated AI is this file, then the canonical ADOP route below.

## First Read

1. `README.md`
2. `docs/design/ADOP_SHELF_CLASSIFICATION.md`
3. `docs/ADOP_GENERIC_QUICKSTART.md`
4. `docs/checklists/external-tool-adoption-checklist.md`

## Current Authority

Current canonical shelves:

- `shared/python/`
- `docs/checklists/`
- `shared/templates/`

Current support shelves:

- `docs/design/`
- `docs/`

Current no-touch generated shelves:

- `shared/python/__pycache__/`
- `tests/__pycache__/`
- `.pytest_cache/`

## Stop Rule

Stop immediately if work would:

- treat `shared/python/__pycache__/` as canonical authority
- replace generic ADOP contracts with project-local trial state
- rename or move `shared/python/`, `docs/checklists/`, or `shared/templates/` without owner approval

## Current Live Restart Rule

- Use `README.md`, `docs/design/ADOP_SHELF_CLASSIFICATION.md`, `docs/ADOP_GENERIC_QUICKSTART.md`, and `docs/checklists/external-tool-adoption-checklist.md` as the bounded restart route for active understanding.

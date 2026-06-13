# ADOP governance entry point

**Last updated**: 2026-06-12

This file is the root stop-rule surface for delegated work inside this repository.

## Scope

- Applies only to `C:\Users\f_tan\project\adop`.
- Root entry for delegated AI is this file, then the canonical ADOP route below.

## First Read

1. `README.md`
2. `common/README.md`
3. `docs/governance/project-template-adoption-packet.md`
4. `docs/AI_AGENT_RUNTIME_TOKEN_OPTIMIZATION.md`
5. `docs/ADOP_GENERIC_QUICKSTART.md`
6. `docs/checklists/external-tool-adoption-checklist.md`

## Current Authority

Current canonical shelves:

- `shared/python/`
- `docs/checklists/`
- `shared/templates/`

Current support shelves:

- `common/` — local reusable common rule shelf (see `docs/governance/project-boundary-register.md`)
- `docs/design/`
- `docs/publication/`
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
- turn support shelves into current trial authority without explicit local rule

## Current Live Restart Rule

- Treat `docs/governance/project-template-adoption-packet.md` as the local governance route.
- Treat this project as `no-current-canonical` for daily bundle tracking at this time.
- Use `README.md`, `docs/ADOP_GENERIC_QUICKSTART.md`, and `docs/checklists/external-tool-adoption-checklist.md` as the bounded restart route for active understanding.

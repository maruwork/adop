# ADOP

**Purpose**: The shared canonical shelf for external tool adoption management.

This repository holds the shared code, checklists, and templates for ADOP.
It does not hold any specific project's current trial state or adoption register.

## What This Is

- `ADOP` is the shared shelf for external tool adoption judgment and trial lifecycle management
- common authority holds artifact schema, trial lifecycle states, checklists, and templates
- current trial board, operator flow, and landing target authority belong in project-local overlays

## What This Is Not

- not any specific project's current adoption board
- not any specific project's canonical operator flow
- not any specific project's landing target authority

## Shelves

- `shared/python/`: shared code for the generic adoption body
  - `adop_cli.py`: command entry
  - `adop_artifacts.py`: artifact IO / atomic write
  - `adop_validation.py`: schema / gate validation
  - `adop_summary.py`: summary projection
  - `adop_types.py`: SSOT constants / field names
  - `adop_ids.py`: id mint / parse
  - `adop_state_machine.py`: lifecycle transition helpers
  - `common.py`: bounded runtime helper
- `docs/checklists/`: checklist items to review before adopting an external tool
- `shared/templates/`: record templates for external tool adoption
- `docs/design/`: bounded design notes
- `docs/ADOP_GENERIC_QUICKSTART.md`: generic ADOP reading order and bounded verification path
- `SUPPORT.md`: pre-issue checklist and support contact routes

## Reading Order

1. `README.md`
2. `docs/design/ADOP_SHELF_CLASSIFICATION.md`
3. `docs/ADOP_GENERIC_QUICKSTART.md`
4. `docs/checklists/external-tool-adoption-checklist.md`
5. `shared/templates/external-tool-adoption-note-template.md`
6. `shared/python/adop_types.py`
7. `shared/python/adop_cli.py`
8. `docs/design/adop-lifecycle-schema-design.md`
9. `SUPPORT.md`

## How to Use

1. use the generic code and lifecycle as the baseline for a project-side runtime copy or overlay
2. read `docs/checklists/` before starting any adoption work
3. bring `shared/templates/` into the project side
4. write current trial state, promote / hold / reject decisions, operator procedures, and landing target authority on the project side

## Repository Community Files

- `LICENSE`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `CODE_OF_CONDUCT.md`
- `CHANGELOG.md`
- `SUPPORT.md`
- `.github/ISSUE_TEMPLATE/`
- `.github/PULL_REQUEST_TEMPLATE.md`
- `.github/CODEOWNERS`
- `.github/workflows/ci.yml`

## What Common Authority Owns

- artifact schema
- trial lifecycle states
- bounded adoption CLI
- generic checklist
- generic adoption note template

## What Project-Local Overlay Owns

- current trial board
- current summary
- operator flow
- hook / queue / runbook activation details
- landing target authority
- project-local decision log

## Do Not Put Here

- any specific project's current trial board
- any specific project's current summary
- any project-specific operator flow
- any project-specific judgment log
- any project-specific landing target authority

## Return Path

- return to the shelf entry: `README.md`
- when reading this as a standalone repo, start from this `README.md`

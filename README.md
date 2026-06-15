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

- `adop.json`: machine-readable canonical identity and runtime file manifest
- `shared/python/`: shared code for the generic adoption body
  - `adop_cli.py`: command entry
  - `adop_artifacts.py`: artifact IO / atomic write
  - `adop_validation.py`: schema / gate validation
  - `adop_summary.py`: summary projection
  - `adop_types.py`: SSOT constants / field names
  - `adop_ids.py`: id mint / parse
  - `adop_state_machine.py`: lifecycle transition helpers
  - `adop_sync.py`: drift detection and sync for project-local runtime copies
  - `common.py`: bounded runtime helper
- `docs/checklists/`: checklist items to review before adopting an external tool
- `shared/templates/`: record templates for external tool adoption
  - `external-tool-adoption-note-template.md`: adoption note record template
  - `project-local-adop-overlay-template.md`: project-local overlay minimum structure
- `docs/design/`: bounded design notes
- `docs/ADOP_GENERIC_QUICKSTART.md`: generic ADOP reading order and bounded verification path
- `SUPPORT.md`: pre-issue checklist and support contact routes

## Reading Order

1. `README.md`
2. `docs/design/ADOP_SHELF_CLASSIFICATION.md`
3. `docs/ADOP_GENERIC_QUICKSTART.md`
4. `docs/checklists/external-tool-adoption-checklist.md`
5. `shared/templates/external-tool-adoption-note-template.md`
6. `shared/templates/project-local-adop-overlay-template.md`
7. `shared/python/adop_types.py`
8. `shared/python/adop_cli.py`
9. `docs/design/adop-lifecycle-schema-design.md`
10. `SUPPORT.md`

## How to Use

```bash
# 1. In your project directory, scaffold the artifact root and overlay
adop init

# 2. Record the first candidate
adop quick-intake --candidate <tool> --use-case <scene> --why-now "<reason>"

# 3. Check progress at any time
adop status

# 4. See what to do next
adop next

# 5. Detect how deeply the tool is embedded
adop scan --target . --tool <tool>
```

Full flow: `quick-intake → quick-compare → quick-trial → quick-close-trial`

See `docs/checklists/` before starting adoption work.
Bring `shared/templates/` into the project side for operator procedures.

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

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

Use a bounded artifact root outside any target project.
All commands use `python shared/python/adop_cli.py` (works on any OS).

```
python shared/python/adop_cli.py --version

python shared/python/adop_cli.py quick-intake  --artifact-root adop-smoke --candidate ToolA --source doc --use-case review-lane --why-now "need bounded trial"
python shared/python/adop_cli.py quick-compare --artifact-root adop-smoke --use-case review-lane --candidate ToolA --candidate ToolB --selected ToolA
python shared/python/adop_cli.py quick-trial   --artifact-root adop-smoke --use-case review-lane --mode review-assist --executor self --decision-owner self --landing-target docs/review-lane
python shared/python/adop_cli.py quick-close-trial --artifact-root adop-smoke --trial-id tr-001 --verdict hold --observed-effect "useful but needs narrowing"
python shared/python/adop_cli.py lint --artifact-root adop-smoke
```

Or use `adop init` if you have ADOP installed as a command:

```
adop init
adop quick-intake --candidate ToolA --source doc --use-case review-lane --why-now "need bounded trial"
adop status
adop next
```

## What This Proves

- CLI can start
- artifact schema and lifecycle can be exercised
- bounded no-impact trial flow can be recorded
- guided intake can make unknown tool attributes explicit instead of omitting them
- promote remains blocked until every tool attribute is known; `unknown` is only a bounded intake placeholder
- lint can validate the resulting artifact root

## What This Does Not Prove

- project-local landing target ownership
- project-local operator workflow
- project-local hook / runbook / queue integration

## Setting Up a Project-Local Overlay

Copy the overlay template into the project and fill in project specifics.

**Linux/macOS:**
```
cp shared/templates/project-local-adop-overlay-template.md <project>/adop-overlay.md
```

**Windows (PowerShell):**
```
Copy-Item shared\templates\project-local-adop-overlay-template.md <project>\adop-overlay.md
```

Or use `adop init` which creates both the artifact root and overlay in one step:
```
adop init
```

The template defines the minimum structure: artifact root, runtime copy path and sync date,
active use cases, operator flow, landing target authority.

Common ADOP authority stays in this repo. The overlay holds only project-specific truth.
Authority boundary: `docs/design/ADOP_SHELF_CLASSIFICATION.md`

## Using ADOP as a Runtime Copy in Another Project

Projects that maintain a local copy of the ADOP Python runtime (`adop_*.py`, `common.py`)
must track drift against the canonical. ADOP provides `shared/python/adop_sync.py` for this.

`--target` points to the **project root**; runtime files are placed under
`<target>/shared/python/` (preserving the canonical relative path).

```
# from the ADOP canonical root:

# check drift in a project's copy
python shared/python/adop_sync.py check --target path/to/project/

# register a project (stored in sync-registry.json, gitignored)
python shared/python/adop_sync.py register --target path/to/project/

# apply updates to all registered projects
python shared/python/adop_sync.py push

# show registered projects and their status
python shared/python/adop_sync.py list
```

The canonical ADOP repo is `https://github.com/maruwork/adop`.
Runtime files are declared in `adop.json` at the repo root.

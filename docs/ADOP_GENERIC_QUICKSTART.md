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

```bash
CLI=shared/python/adop_cli.py
SRC=shared/python
ARTIFACT_ROOT=/tmp/adop-smoke

python "$CLI" --version
python -m py_compile "$SRC"/*.py
python "$CLI" quick-intake  --artifact-root $ARTIFACT_ROOT --candidate ToolA --source doc --use-case review-lane --why-now "need bounded trial"
python "$CLI" quick-compare --artifact-root $ARTIFACT_ROOT --use-case review-lane --candidate ToolA --candidate ToolB --selected ToolA
python "$CLI" quick-trial   --artifact-root $ARTIFACT_ROOT --use-case review-lane --mode review-assist --executor self
python "$CLI" quick-close-trial --artifact-root $ARTIFACT_ROOT --trial-id tr-001 --verdict hold --observed-effect "useful but needs narrowing"
python "$CLI" lint --artifact-root $ARTIFACT_ROOT
```

## What This Proves

- CLI can start
- artifact schema and lifecycle can be exercised
- bounded no-impact trial flow can be recorded
- lint can validate the resulting artifact root

## What This Does Not Prove

- project-local landing target ownership
- project-local operator workflow
- project-local hook / runbook / queue integration

## Using ADOP as a Runtime Copy in Another Project

Projects that maintain a local copy of the ADOP Python runtime (`adop_*.py`, `common.py`)
must track drift against the canonical. ADOP provides `shared/python/adop_sync.py` for this.

```bash
# from the ADOP canonical root:

# check drift in a project's copy
python shared/python/adop_sync.py check --target /path/to/project/copy/

# register a project copy (stored in sync-registry.json, gitignored)
python shared/python/adop_sync.py register --target /path/to/project/copy/

# apply updates to all registered copies
python shared/python/adop_sync.py push

# show registered copies and their status
python shared/python/adop_sync.py list
```

The canonical ADOP repo is `https://github.com/maruwork/adop`.
Runtime files are declared in `adop.json` at the repo root.

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
# set ARTIFACT_ROOT to any writable directory outside the project
python shared/python/adop_cli.py --version
python shared/python/adop_cli.py quick-intake --artifact-root $ARTIFACT_ROOT --candidate ToolA --source doc --use-case review-lane --why-now "need bounded trial"
python shared/python/adop_cli.py quick-compare --artifact-root $ARTIFACT_ROOT --use-case review-lane --candidate ToolA --candidate ToolB --selected ToolA
python shared/python/adop_cli.py quick-trial --artifact-root $ARTIFACT_ROOT --use-case review-lane --mode review-assist --executor codex
python shared/python/adop_cli.py quick-close-trial --artifact-root $ARTIFACT_ROOT --trial-id tr-001 --verdict hold --observed-effect "useful but needs narrowing"
python shared/python/adop_cli.py lint --artifact-root $ARTIFACT_ROOT
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

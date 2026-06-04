# ADOP Generic Quickstart

Status: Active

## Purpose

Provide the shortest bounded path to understand and verify generic ADOP.

## Read Order

1. `README.md`
2. `ADOP_SHELF_CLASSIFICATION.md`
3. `checklists/external-tool-adoption-checklist.md`
4. `templates/external-tool-adoption-note-template.md`
5. `python/adop_types.py`
6. `python/adop_cli.py`

## Fastest Verification

Use a bounded artifact root outside any target project.
Because this workspace uses Git Bash, the examples below use `/c/tmp/adop-smoke`:

```bash
python python/adop_cli.py --version
python python/adop_cli.py quick-intake --artifact-root /c/tmp/adop-smoke --candidate ToolA --source doc --use-case review-lane --why-now "need bounded trial"
python python/adop_cli.py quick-compare --artifact-root /c/tmp/adop-smoke --use-case review-lane --candidate ToolA --candidate ToolB --selected ToolA
python python/adop_cli.py quick-trial --artifact-root /c/tmp/adop-smoke --use-case review-lane --mode review-assist --executor codex
python python/adop_cli.py quick-close-trial --artifact-root /c/tmp/adop-smoke --trial-id tr-001 --verdict hold --observed-effect "useful but needs narrowing"
python python/adop_cli.py lint --artifact-root /c/tmp/adop-smoke
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

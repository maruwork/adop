# ADOP Public Verification Contract

Status: Active

## Purpose

Define the minimum verification surface that must pass before `ADOP` is published.

## Mandatory Checks

Run these from this monorepo root, or from the standalone repository root / an
equivalent extracted copy. Set `CLI` and `SRC` for your context first:

```bash
# This monorepo:
CLI=shared/python/adop_cli.py; SRC=shared/python
# Standalone repo (after export, where shared/python/ becomes python/):
# CLI=python/adop_cli.py; SRC=python

python "$CLI" --version
python -m py_compile "$SRC"/*.py
python "$CLI" quick-intake --artifact-root /c/tmp/adop-smoke --candidate ToolA --source doc --use-case review-lane --why-now "need bounded trial"
python "$CLI" quick-compare --artifact-root /c/tmp/adop-smoke --use-case review-lane --candidate ToolA --candidate ToolB --selected ToolA
python "$CLI" quick-trial --artifact-root /c/tmp/adop-smoke --use-case review-lane --mode review-assist --executor codex
python "$CLI" quick-close-trial --artifact-root /c/tmp/adop-smoke --trial-id tr-001 --verdict hold --observed-effect "useful but needs narrowing"
python "$CLI" lint --artifact-root /c/tmp/adop-smoke
```

## Pass Criteria

- every command exits successfully
- no command depends on monorepo-only paths
- bounded artifact output stays outside any target project
- the resulting artifact root can be linted successfully

## Fail Criteria

- a documented command fails under the documented shell assumptions
- publication docs require monorepo-only context
- verification requires undocumented local setup

## Shell Assumption

- this workspace uses Git Bash style paths
- if another shell is used publicly, quickstart examples must be translated before release

## Chosen Verification Defaults

The current chosen default is:

- use this contract as the minimum required public verification scope
- require CI at repo creation

## Current Verification Decision Record

- minimum public verification surface:
  - CLI version, `py_compile`, and the bounded quick flow in this contract
- CI required at repo creation or allowed immediately after:
  - required at repo creation

These choices are reflected in `OWNER_DECISION_PACKET.md` and `PUBLICATION_RUNBOOK.md`.

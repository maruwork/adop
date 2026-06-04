# ADOP Repo Export Guide

Status: Active

## Purpose

Describe how to read and extract `ADOP` as a standalone repository even while it currently lives under `common/adop/` in the monorepo.

## Reading Rule

- public-facing commands in this shelf are repo-relative
- public-facing file paths in this shelf are repo-relative
- monorepo host paths must not be required to understand generic ADOP

## Expected Standalone Root

```text
./
├── README.md
├── ADOP_SHELF_CLASSIFICATION.md
├── ADOP_GENERIC_QUICKSTART.md
├── PUBLIC_VERIFICATION_CONTRACT.md
├── PUBLIC_POLICY_PROMOTION_MATRIX.md
├── PUBLICATION_RUNBOOK.md
├── PRIVATE_HOST_BOOTSTRAP_RUNBOOK.md
├── PRIVATE_RELEASE_HOLD_LINE.md
├── REPO_EXPORT_GUIDE.md
├── REPO_EXPORT_CHECKLIST.md
├── checklists/
├── templates/
├── python/
└── LICENSE
```

## Must Stay Repo-Relative

- quickstart commands
- quickstart file references
- public-facing shelf classification examples

## Carry Into The Standalone Repository

- `README.md`
- `ADOP_SHELF_CLASSIFICATION.md`
- `ADOP_GENERIC_QUICKSTART.md`
- `PUBLIC_VERIFICATION_CONTRACT.md`
- `PUBLIC_POLICY_PROMOTION_MATRIX.md`
- `PUBLICATION_RUNBOOK.md`
- `PRIVATE_HOST_BOOTSTRAP_RUNBOOK.md`
- `PRIVATE_RELEASE_HOLD_LINE.md`
- `REPO_EXPORT_GUIDE.md`
- `REPO_EXPORT_CHECKLIST.md`
- `checklists/`
- `templates/`
- `python/`

## Keep Internal Unless Explicitly Needed

- `roadmap/`
- `tasks/`
- `design/`
- working-mirror notes under `common/refernce`
- draft-only owner-decision notes that are not meant for the public repo

## May Stay Monorepo-Aware

- working-mirror notes under `common/refernce`
- local bounded verification roots such as `/c/tmp/adop-smoke` when using Git Bash

## Export Blockers

- repository creation in the chosen host
- private repository setup actions in the chosen host
- CI wiring in the chosen host

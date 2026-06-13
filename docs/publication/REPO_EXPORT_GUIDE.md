# ADOP Repo Export Guide

Status: Active

## Purpose

Describe the standalone repository shape for `ADOP`.

## Reading Rule

- public-facing commands in this shelf are repo-relative
- public-facing file paths in this shelf are repo-relative
- monorepo host paths must not be required to understand generic ADOP

## Expected Standalone Root

```text
./
├── README.md
├── ADOP_SHELF_CLASSIFICATION.md
├── docs/ADOP_GENERIC_QUICKSTART.md
├── PUBLIC_VERIFICATION_CONTRACT.md
├── PUBLIC_POLICY_PROMOTION_MATRIX.md
├── PUBLICATION_RUNBOOK.md
├── PRIVATE_HOST_BOOTSTRAP_RUNBOOK.md
├── PRIVATE_RELEASE_HOLD_LINE.md
├── SUPPORT.md
├── .github/
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

Paths are standalone repo destinations. Monorepo source paths are noted where they differ.

- `README.md`
- `ADOP_SHELF_CLASSIFICATION.md` — from `docs/design/ADOP_SHELF_CLASSIFICATION.md`
- `docs/ADOP_GENERIC_QUICKSTART.md`
- `PUBLIC_VERIFICATION_CONTRACT.md` — from `docs/publication/`
- `PUBLIC_POLICY_PROMOTION_MATRIX.md` — from `docs/publication/`
- `PUBLICATION_RUNBOOK.md` — from `docs/publication/`
- `PRIVATE_HOST_BOOTSTRAP_RUNBOOK.md` — from `docs/publication/`
- `PRIVATE_RELEASE_HOLD_LINE.md` — from `docs/publication/`
- `SUPPORT.md`
- `.github/`
- `REPO_EXPORT_GUIDE.md` — from `docs/publication/`
- `REPO_EXPORT_CHECKLIST.md` — from `docs/publication/`
- `checklists/` — from `docs/checklists/`
- `templates/` — from `shared/templates/`
- `python/` — from `shared/python/`

## Keep Internal Unless Explicitly Needed

- `archive/` — completed wave materials
- `docs/design/` — internal design and architecture notes
- `docs/governance/` — monorepo governance docs
- `docs/publication/` — stays in monorepo; only its carried files go to standalone root
- `common/` — monorepo-local rule shelf
- `workspace/` — scratch

## May Stay Monorepo-Aware

- working-mirror notes under `common/reference`
- local bounded verification roots such as `/c/tmp/adop-smoke` when using Git Bash

## Export Blockers

- repository creation in the chosen host
- private repository setup actions in the chosen host
- CI wiring in the chosen host

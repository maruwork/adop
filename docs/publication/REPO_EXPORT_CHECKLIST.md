# ADOP Repo Export Checklist

Status: Active

## Purpose

List the minimum repository-facing conditions for lifting this shelf into a standalone public repository.

## Checklist

- public-facing commands are repo-relative
- public-facing file paths are repo-relative
- `README.md` explains current monorepo placement and standalone-repo view
- `REPO_EXPORT_GUIDE.md` defines the expected standalone root
- `ADOP_SHELF_CLASSIFICATION.md` can be read without host-specific absolute paths
- generic quickstart is usable as a standalone repo guide
- carried files vs internal-only files are explicit
- publication verification contract exists
- publication runbook exists

## Out Of Scope

- license selection
- repository host/owner decision
- CI/CD outside this shelf

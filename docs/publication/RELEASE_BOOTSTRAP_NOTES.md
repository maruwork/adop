# ADOP Release Bootstrap Notes

Status: Draft

## Purpose

Give the owner a bounded checklist for the moment just before a standalone public repository is created.

## Bootstrap Notes

1. Copy the shelf using `REPO_EXPORT_GUIDE.md`.
2. Add the chosen license file only after owner decision.
3. Decide whether `docs/publication/CONTRIBUTING_DRAFT.md` and `docs/publication/SECURITY_DRAFT.md` become live documents as-is or require owner-specific policy text.
4. Decide the minimum public CI scope for CLI/version, bounded quickstart, and validation.
5. Re-run the bounded verification path in the standalone repo before publication.

## Must Not Be Skipped

- verify repo-relative commands still work after extraction
- verify public docs do not require monorepo-only context
- verify draft docs still read as draft until go-live


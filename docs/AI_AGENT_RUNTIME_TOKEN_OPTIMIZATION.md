# AI Agent Runtime Token Optimization

## Purpose

Reduce token waste during ADOP checklist review, CLI validation, and publication-readiness work without weakening canonical authority.

## Adopt Now

- RTK for repetitive CLI output reduction
- thin entrypoint reading from `AGENTS.md` / `CLAUDE.md`
- bounded reads in `docs/governance/`, `shared/python/`, `docs/checklists/`, and the exact publication or template file under change
- compact / plan discipline for longer publication-prep sessions
- avoid loading `shared/python/__pycache__/` or unrelated support docs unless the task explicitly targets them

## Deferred

- distill
- local RAG
- proxy / budget-kill layers
- heavier context-mode automation

## Scale Profile

ADOP should currently use the medium-scale profile.

## Operator Rules

1. Read the smallest authority route first.
2. Prefer targeted reads of the exact checklist, template, or CLI file under change.
3. Do not load generated residue by default.
4. Use RTK-filtered command execution for repetitive validation output.
5. Compression helpers do not decide lifecycle truth, artifact truth, or publication truth.

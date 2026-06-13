# ADOP Project Workspace And Artifact Policy

Status: Active

## 1. Purpose

Fix the handling of scratch work, generated residue, and the archive shelf in ADOP.

## 2. Active Workspace

- active workspace root:
  - `workspace/`
- allowed contents:
  - scratch notes
  - one-off review outputs
  - temporary validation artifacts
- prohibited uses:
  - placing canonical lifecycle docs or reusable templates without explicit promotion

## 3. Generated Output Shelf

- machine-readable output:
  - `workspace/`
- human-readable report output:
  - `workspace/`
- retention:
  - keep only while the artifact is still referenced by active review work
- promotion rule:
  - generated artifact is not canonical until explicitly reviewed and promoted

## 4. Archive Shelf

- archive root:
  - `archive/`
- what belongs here:
  - completed wave roadmap, task board, and design docs
- archive note rule:
  - record why the file left active topology in `archive/README.md`

## 5. Legacy Compatibility Shelf

- legacy shelf:
  - `none`
- why it still exists:
  - `not applicable`
- rule:
  - `not applicable`

## 5a. Hidden Active Asset Rule

- hidden / ignored active shelf:
  - `none`
- rule:
  - hidden active asset must not stay unannounced

## 5b. Runtime / Agent Residue Rule

- residue shelf:
  - `__pycache__/` (any code shelf, e.g. `shared/python/`, `tests/`)
  - `.pytest_cache/`
- class:
  - `generated`
- cleanup trigger:
  - when runtime verification no longer needs the residue
- owner:
  - repository owner or the maintainer explicitly handling residue cleanup

## 6. Promotion Rule

1. decide the artifact role
2. choose the canonical shelf using taxonomy
3. confirm caller / reader impact
4. update governance docs if the artifact is promoted

## 7. Cleanup Rule

- residue cleanup must not silently remove canonical evidence
- cleanup must not write from generated shelves back into canonical shelves without review

## 8. Completion Rule

- active workspace is explicit
- generated residue shelves are explicit
- archive shelf is explicit
- hidden active assets are not assumed

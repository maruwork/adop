# Project Workspace and Artifact Policy Template

**When to use**: Use this when deciding placement and handling for workspace, generated output, and archive material.  
**Replace**: paths, retention rules, generated-output handling, archive policy.  
**Do not write**: implementation-task detail, the current-state canonical source, or project-specific current operations.

> **Use**:
> Reusable template for fixing workspace, generated-output, and archive operations early so the repository does not turn into a scratch dump later.

> **Reading note**: This file is a fill-in policy form. Read the actual workspace / cleanup / archive rule body in the cleanup-procedure section of [`project-structure-governance-starter-pack.md`](./project-structure-governance-starter-pack.md).

**project_id**: `project_xxx`
**status**: Draft / Approved
**rulebook**: `project-structure-governance-starter-pack.md`

---

## 1. Purpose

- route temporary work into one active workspace
- keep generated output separate from canonical shelves
- separate archive material from active work

This template decides only the handling of `workspace / generated / archive`.
It does not decide by itself:

- placement for every file type
- shelf class or current canonical status for each shelf
- the full project entry route or reading order

## 2. Active Workspace

- active workspace root:
  - `{path}`
- allowed contents:
  - `{scratch, temporary exports, one-off analysis, generated review files}`
- prohibited uses:
  - `{placing canonical docs without explicit promotion}`

## 3. Generated Output Shelf

- machine-readable output:
  - `{path}`
- human-readable report output:
  - `{path}`
- retention:
  - `{policy}`
- promotion rule:
  - generated artifacts are not canonical until they are explicitly reviewed and promoted

## 4. Archive Shelf

- archive root:
  - `{path}`
- what belongs here:
  - `{historical docs, retired tools, obsolete exports, one-off completed artifacts}`
- archive note rule:
  - record why the file left the active topology

## 5. Legacy Compatibility Shelf

- legacy shelf:
  - `{path or none}`
- why it still exists:
  - `{caller / hardcoded path / migration bridge}`
- rule:
  - do not use it as a new write target

## 5a. Hidden Active Asset Rule

- hidden / ignored active shelf:
  - `{path or none}`
- if active assets live here:
  - `{manifest path}`
  - `{entry-file reference}`
- rule:
  - do not operate hidden active assets as invisible active state

## 5b. Runtime / Agent Residue Rule

- residue shelf:
  - `{path or none}`
- class:
  - `generated` / `support`
- cleanup trigger:
  - `{when to delete or rotate}`
- owner:
  - `{who decides retention}`

## 6. Promotion Rule

When promoting scratch or generated files into canonical material, pass at least these checks:

1. decide the role
2. decide the shelf against the taxonomy
3. check caller and reader impact
4. update the boundary register if needed

## 7. Cleanup Rule

For the cleanup rule body, see the cleanup-procedure section of [`project-structure-governance-starter-pack.md`](./project-structure-governance-starter-pack.md).

## 8. Completion Rule

- one active workspace is defined
- a generated-output shelf is defined
- an archive shelf is defined
- if a compatibility lane exists, it is explicitly marked as not being a new write target
- if hidden active assets exist, a visibility rule exists
- runtime or agent residue has a retention or cleanup rule
- if a visible support document exists, it does not blur with the front current surface
# Project Structure Governance Starter Pack

**Purpose**: the minimum pack for organizing a project's file, folder, and shelf structure without breaking its rules or current authority.  
**Use When**: you need to organize the whole project structure, shelf responsibilities, or the handling of workspace, generated output, and archive.  
**Prerequisite**: the project's current canonical source, entry route, and owner-only decisions are already visible.

> **Note**:
> this pack exists to align structure.
> It does not contain the final judgment for archive, delete, or hidden-asset disposition.

## 0. Inspect First

1. the project's entry route and current canonical source
2. the existing taxonomy, boundary register, and workspace rule
3. whether hidden active assets, generated callers, or runtime residue exist
4. whether any owner-only decision is still unresolved

## 1. Role Of This Pack

- separate the responsibilities of files, shelves, generated output, archive, and support
- cut a clean line between current canonical authority and visible support
- expose hidden active assets, placeholder shelves, and runtime residue

## 2. Included Materials

- [project-file-taxonomy-template.md](./project-file-taxonomy-template.md)
- [project-boundary-register-template.md](./project-boundary-register-template.md)
- [project-workspace-and-artifact-policy-template.md](./project-workspace-and-artifact-policy-template.md)

Support rules to read as needed:

- `../policies/file-operation-policy.md`
- `../policies/naming-and-shelf-policy.md`

## 3. Completion Conditions

1. the entry file can explain the current route
2. the taxonomy can explain the responsibility of each file and shelf
3. the boundary register can explain read, write, and no-touch
4. workspace, generated output, and archive handling are fixed
5. hidden active assets and residue handling are recorded

## 4. What Remains Project-Specific

- project-specific paths
- project-specific commands, runtime surfaces, DB facts, and callers
- real evidence for hidden active assets
- issues that still need owner judgment for cleanup

## 5. What The AI May Draft First

- taxonomy draft
- boundary-register draft
- workspace / generated / archive organization proposal
- rename or move candidate list
- inventory of hidden active assets, residue, and placeholders

## 6. What The AI Must Not Decide

- final archive, restore, or delete judgment
- final reclassification between canonical and historical
- keep / expose / retire for hidden active assets
- caller-sensitive rename, move, or delete

## 7. Root Design Shelf Option

- root-level `design/` is allowed when declared as the project's design shelf
- declare the same `design/` path in the taxonomy and boundary register
- keep `design/` separate from front current surfaces, generated shelves, and workspace shelves

## 8. AI Stop Line

Stop when any of the following appears:

- the caller relationship of a hidden active asset is still uncertain
- archive, delete, or restore judgment is needed
- canonical versus historical reclassification is needed
- a rename would affect root entry, runtime, DB, or caller surfaces

## 9. Cleanup Procedure

1. confirm root misplaced artifacts
2. confirm the boundary between current canonical authority and visible support
3. confirm the shelves for generated output, archive, and workspace
4. expose assets under hidden or ignored paths through a manifest
5. record the handling of runtime residue and AI worktree residue

## 10. Completion Checklist

- no root misplaced artifact remains
- docs, generated output, and archive are separated
- hidden active assets have a manifest or entry record
- visible support documents are not serving as a substitute for current authority

## 11. Shortest Procedure

1. read the entry and current route
2. create the taxonomy
3. create the boundary register
4. create the workspace / generated / archive policy
5. take a cleanup inventory
6. separate only the points that require owner judgment

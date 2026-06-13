# Naming and Shelf Policy

**Purpose**: Define portable naming and shelf rules to use before a project-specific placement table is applied.

> **Canonical relationship**: This file is the canonical shared policy in `pj-template`. Project-specific naming exceptions and shelf-placement exceptions should be added as local rules under this baseline.

This policy covers naming and the conditions for introducing a new shelf.

- For file moves, archiving, and disposal rules, see `file-operation-policy.md`
- For separation between entry, guide, and reference reading surfaces, see `entry-guide-reference-separation-policy.md`

## Naming

- Do not add dates to active canonical document names.
- Generated outputs, logs, snapshots, exports, reports, and archived items may use date suffixes.
- Use lowercase kebab-case for new portable document names unless a stronger convention exists.
- Let code and config filenames follow the norms of their language or toolchain.
- Keep project-specific names in project shelves, not in shared shelves.
- Imported or legacy filenames may stay as-is until there is a formal normalization pass.
- Before renaming an existing exception, check callers, records, manuals, generated outputs, and other downstream references first.

## Folder Naming

- Use lowercase kebab-case for new shared shelf folders.
- Archive, intake, or legacy folder groups may keep their original names when that preserves traceability.
- Numbered sequences may use zero-padded prefixes such as `01-...`, but do not create meaningless serial numbering.

## Entry Files

- Use `README.md` as the default shelf entry file.
- Allow `INDEX.md` only for imported, legacy, or compatibility-driven cases where that filename is required.

## Prefixes and Mixed Language

- Use prefixes such as `PT-`, `SE-`, or `ADR-` only when the numbering system itself has meaning in that shelf.
- Do not add uppercase ID prefixes to new shared documents unless they are required.
- Mixed-language filenames are acceptable for imported, legacy, or project-specific guidance, but avoid them for new shared reusable assets.

## Rename Decisions

- Prioritize impact on callers, records, manuals, outputs, hooks, tests, and databases over visual neatness.
- Rename immediately only when the impact is small.
- When the impact is large, record the item as a rename candidate for later discussion.

## Shelf Rules

- Place reusable assets that can serve any project in shared shelves.
- Place project-specific governance and enforcement rules in that project's governance shelves.
- Do not create duplicate intake destinations inside a project for external research input before formal promotion.
- Before adding a new shelf, check whether an existing shelf README, guide, or register already covers that role.
- Add a shelf only when it has a reader role or authority role that differs from existing shelves.
- When adding a shelf, document its entry point, return route, and handling of current / generated / historical material in one README or register.
- If two or more shelves serve the same reader role, treat them as merge, rename, or archive candidates instead of adding another one.

## Archive and Deletion

- Prefer archiving over deletion.
- Archive files that still have historical value even if they no longer have an active role.
- Delete only generated artifacts, local state, duplicates without historical value, or items with explicit approval to remove.

## Generalization

When a project-specific file contains reusable principles, extract a portable version into a shared shelf without moving the original file. Keep the original as the project-specific canonical source until a separate migration explicitly changes that status.

## Anti-Bloat Rule

- When adding files or folders, also check for removable duplicates, stale explanations, and unnecessary route notes.
- Before creating something new, classify it against an existing shelf role such as `entry / guide / reference / canonical / evidence / archive`.
- If it cannot be classified, do not place it in a canonical shelf; treat it as temporary, workspace, or draft material.
- Keep every long-lived shelf readable enough that a reader can tell from the README alone what belongs there and what does not.
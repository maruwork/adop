# Entry / Guide / Reference Separation Policy

**Purpose**: Define a portable rule that keeps project entry documents, reading-order guides, and reference shelves from blending together, so first-time readers and downstream agents can choose the next step without confusion.

This policy does not replace a project-local current canonical source or governance SSOT.
Each project should define its canonical paths through local rules and then apply this policy to navigation design.

- For shelf and filename naming, see `naming-and-shelf-policy.md`
- For file creation, movement, archiving, and disposal, see `file-operation-policy.md`

## 1. Role Separation

Split the project's navigation surface into at least these three roles:

- `entry`
  - the first surface to open once
  - tells the reader what the project is, where current state lives, and which guide comes next
- `guide`
  - shows reading order by purpose only
  - may separate paths such as current work, runtime, or first read
- `reference`
  - holds inventory, generated indexes, backlog catalogs, and historical lookup
  - must not act as a substitute for the current authoritative source

When these roles are packed into one file, the entry surface gets bloated and inventory starts to look like the current source.
The goal is not to increase file count. The goal is to prevent role collision.

## 2. Entry Rule

- Keep exactly one entry file.
- Use `README.md` as the standard shelf entry name.
- Keep the entry thin and make sure it answers at least these four questions:
  - What is this project?
  - Where should I look for current state?
  - Where is the canonical rule or governance source?
  - Where do runtime, DB, or tool surfaces begin?
- Do not remove links from the entry file to the guide and canonical surfaces.
- Do not overload the entry file with inventory tables, generated snapshots, long anti-misread essays, or detailed route descriptions.
- When updating the entry file, check that old routes are not left behind as duplicates.
- If the entry file starts carrying two or more different current or route frames, merge it back to one.

## 3. Guide Rule

- Keep guide files to three by default.
- The recommended minimum set is:
  - `guide-first-read.md`
  - `guide-current-work.md`
  - `guide-runtime.md`
- A guide shows reading order; it is not an inventory or current-status board.
- Before adding a new guide, check whether the role can be absorbed into an existing guide.
- Allow a fourth or later guide only when role conflict cannot be avoided with the existing three.
- If one guide starts to carry multiple journeys, consider section compression or relocation into an existing guide.

## 4. Reference Rule

- Put inventory, generated indexes, backlog catalogs, and historical lookup in the reference shelf.
- Near the top of every reference file, state at least:
  - this is not the entry surface
  - this is not the current authoritative source
  - where to return if the reader wants the current source
- If a reference file starts summarizing current progress or the active branch on its own, treat that as role drift.
- Move easily misread backlog catalogs or pending lists off the front surface and lock them into the reference role.

## 5. Split Gate

- Decide README splitting by role conflict, not by line count.
- Consider separating entry / guide / reference when:
  - entry, reading order, inventory, and anti-misread notes are mixed in one file
  - a first-time reader must read a long explanation before choosing the next step
  - a backlog catalog or generated index looks like the current source
- Do not split mechanically just because a file is long.
- When splitting, move content into a destination role instead of merely deleting it.

## 6. Link Preservation Rule

- You may delete duplicate explanation, but do not delete the route.
- Keep at least these link classes in the entry file:
  - project overview / concept
  - current canonical
  - governance / rule SSOT
  - runtime / DB / tool surface
- If content moved into a guide can no longer be reached from the entry file, the separation is incomplete.

## 7. Follow-Through Updates

When the role of entry, guide, or reference changes, update at least:

- taxonomy or placement map
- navigation or index
- boundary or disposition register
- generator, script, or caller references

If a reference shelf is newly created or renamed, check existing generated paths and links first.

## 8. Success Criteria

This separation counts as successful only when:

- a first-time reader can choose the next step from the entry file alone
- a reader following current work can land on the current-work guide without hesitation
- the runtime / DB / tool starting point does not mix with the current-work guide
- reference files are unlikely to be mistaken for the current authoritative source
- a new document can be placed by judging whether it belongs to entry, guide, reference, or canonical

## 9. Anti-Bloat Rule

Entry / guide / reference cleanup exists to shorten the reader journey, not to grow file count.

- Before creating a new entry, guide, or reference file, check whether compression, replacement, or pointerization of an existing file is enough.
- Before creating a new shelf, check whether an existing shelf already serves the same role.
- When creating new reference material, explicitly state whether it is generated, inventory, historical lookup, or a current companion.
- Do not create ambiguous new documents; keep them as workspace memos or drafts until canonicalization is justified.
- If a change makes the README, guide, or reference layer heavier, remove stale route notes or duplicate cautions in the same change.

## 10. Orientation / Readability Rule

- Keep the `Markdown` readable both for linear human reading and for search / link jumps.
- Bias the file opening toward a short role statement plus the minimum return links.
- Do not stack repeated warnings such as `this is entry` or `this is not current` in the same file.
- Keep direct-open warnings short and limited to role, authority, or next-step risks that are easy to misread.
- Place cross-role explanation in the single file whose responsibility is closest, and let other files point there.
- Avoid long caution lists, repeated current values, and repeated explanations of another file's navigation.
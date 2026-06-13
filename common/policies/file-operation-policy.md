# File Operation Policy

**Purpose**: Define portable rules for file creation, movement, archiving, and modification. Project-specific placement and protected targets should be defined by each project.

> **Canonical relationship**: This file is the canonical shared policy in `pj-template`. Project-specific placement and protected targets should be added as local rules under this baseline.

This policy covers the operating boundary for `create / move / archive / dispose`.

- For naming and shelf naming rules, see `naming-and-shelf-policy.md`
- For separation of entry, guide, and reference surfaces, see `entry-guide-reference-separation-policy.md`

## 1. Decide Placement First

- Choose the shelf before creating a file.
- Prefer an existing shelf over a new folder.
- Create a new folder only when the file's role cannot be explained by an existing shelf.
- A new folder should support repeated work or multiple files, not just a single isolated file.

## 2. Conditions for Creating a Folder

- Its role is clearly different from existing folders.
- Its contents are coherent and expected to recur.
- The placement can be explained in a taxonomy, guide, or register.
- It will not become an unstructured dumping ground.

## 3. Move and Archive Rules

- Check references and callers before moving anything.
- Prefer archiving over deletion when historical value exists.
- Record why an archived file left active service.
- Do not mix active files with archived or one-off material in the same shelf.

## 4. Temporary Work

- Use a declared workspace or scratch area for temporary output.
- Do not treat temporary output as a formal document.
- Promotion out of temporary work requires review and placement judgment.
- When multiple temporary areas exist, route new temporary output into one active workspace.

## 5. Follow-Through After Changes

When a file's role or location changes, update the nearest applicable surface:

- taxonomy or placement map
- guide or index
- boundary or disposal record
- caller or config references

If no follow-through document exists, create a small durable note instead of relying on memory.

## 6. Disposal Model

The default rule is **archive first, delete last**.

Before moving or deleting a file, check:

- whether the current runtime still uses it
- whether anything actually references it
- whether there is still intent to maintain it
- whether misreads or accidental edits would have large impact
- whether it still has historical or re-verification value

Use only these five categories:

- `current keep`
- `exception keep`
- `isolated keep`
- `archive keep`
- `delete candidate`

Do not leave items in active shelves while still unclassified. Do not treat archives as current state.

## 7. Naming, Paths, and Protection

- Use stable names for active canonical files.
- Do not add dates to active canonical filenames.
- Logs, snapshots, exports, reports, and archived material may include dates.
- Do not hard-code user-specific absolute paths into reusable code.
- Use temporary directories for tests and scratch output.
- Do not write outside the project without explicit approval.

Treat the following as high-risk protected files:

- governance and policy
- schema and migration history
- append-only audit records
- production config
- root entry instructions

Do not place secrets in tracked files or logs. Avoid storing large generated artifacts or binaries in source control unless they are truly required.
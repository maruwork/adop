# External Tool Placement Policy

**Purpose**: Keep external tools from mixing with project truth, public files, or local-only state.

## Core Rule

Use these default locations unless the project already has an approved equivalent:

- external tools:
  - `{approved local tool path}`
  - do not treat this as a repository reading surface
- local state, cache, auth, logs, or machine-only settings for those tools:
  - `{approved ignored local state path}`
  - keep this ignored

Put controllable generated output in the approved ignored local state path.
Do not create or normalize generated residue inside the tool checkout.
If a toolchain still creates residue inside the tool checkout, treat it as residue only and never as canonical authority.

Do not invent a more complex structure unless the project actually needs one.

## Public Boundary

- public guidance belongs in `README.md`, `docs/`, or `.github/`
- `AGENTS.md` and `CLAUDE.md` stay at project root as agent entry files
- developer-only control files do not become public guidance

## Writeback Rule

External tools are support surfaces.
They do not become project truth by themselves.

If a tool produces something worth keeping, write the accepted result back into the project's canonical docs, runtime files, or approved public files.

## Stop Rule

Stop and decide explicitly if any of these is true:

- the tool might be shared, but is being placed in one project only
- the tool location is undefined or mixed into canonical shelves without an approved exception
- the tool creates local state, but no ignored location is defined
- a public file would end up depending on developer-only local state

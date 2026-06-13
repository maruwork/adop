# Project Template Adoption Completion Policy

## 1. Purpose

Define when `pj-template` is ready enough for delegated use and when a project-local adoption packet is complete enough to operate from.

## 2. Shared Template Completion

Treat the shared template set as complete enough when it includes at least:

1. entry guidance
2. file placement guidance
3. boundary guidance
4. workspace guidance
5. an adoption-packet template
6. stop conditions and owner-only boundaries

It must also provide root agent-entry starters for both Codex and Claude Code.

## 3. Project-Local Packet Completion

Treat the project-local adoption packet as complete enough when all of the following are explicit:

1. reading route
2. read / write / no-touch boundary
3. current, support, generated, and archive handling
4. runtime-sensitive paths
5. output / reporting path
6. owner-only decisions remain owner-only
7. root `AGENTS.md` and `CLAUDE.md` are installed or mapped to existing equivalents

If the project uses external tools or token optimization, record only the actual local paths in use.

## 4. Non-Goals

The following are not required for shared-template completion:

- project-specific final close verdict
- project-specific archive or delete decisions
- project-specific hidden-asset disposition
- proof that every target project has already been updated

## 5. Fail-Close Rule

If a required shared rule or required packet section is unclear, missing, or contradictory, delegated adoption is not ready.

## 6. Stop and Owner Boundary

Stop and return control to the owner when any of these is true:

1. the current route is unclear
2. archive and active work are mixed without a clear local rule
3. hidden active assets are suspected
4. generated artifacts may have active callers but the relationship is unclear
5. rename / move / delete / archive / restore would require owner judgment
6. a new shelf or folder would be required without a placement rule

## 7. Safe Outputs

Delegated AI may still return:

- inventory
- placement suggestions
- boundary or taxonomy updates in allowed paths
- route observations
- unresolved points for owner judgment

Delegated AI must not decide final canonical, archive, restore, delete, or caller-sensitive rename questions.

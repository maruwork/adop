# PJ Template

Purpose: the canonical shared template shelf for structuring projects.

This shelf does not store any one project's current state or operating results.
It stores only the reusable structure for how a project is organized, guided, decomposed, and advanced.

## Shelves

- `frameworks/`
  - live frameworks for design, decomposition, progression, and decision-making
- `policies/`
  - reusable operating rules
- `templates/`
  - reusable document starters
- `checklists/`
  - reusable verification checklists
- `examples/`
  - small portable examples

## Read First

1. `frameworks/project-progression-rule.md`
2. `frameworks/project-progression-rule-integration-audit.md`
   - read only the integration map and shelf-role alignment first
3. `frameworks/goal-path-checkpoint-task-design-framework.md`
4. `policies/execution-readiness-gate-policy.md`

For additional materials by use case, open only the needed README in each shelf.
Do not start with `ps-suite` or `RISEN` unless they are directly relevant.

## Canonical Terms

Use these labels consistently throughout the template:

- `progression rule`
- `template-side rule`
- `project-specific rule`
- `completion definition`
- `current location`
- `stop reason`
- `writeback destination`

Do not rename the same idea in different places.
When adapting the template into a project, align to these labels first and add local wording only after that.
Write simply.
Do not spend time making a simple rule look more complex than it is.

## Three-Layer Split

This template separates work into three layers:

1. `progression rule`
   - the highest shared authority
   - defines the subject, progression, stop conditions, and re-grounding
2. `template-side rule`
   - reusable concretization for applying the higher rule inside projects
   - includes gates, templates, checklists, structure work, and entry organization
3. `project-specific rule`
   - holds only that project's purpose, current state, runtime facts, and owner judgment

Lower layers must not conflict with higher layers.

## Replace Per Project

- entry-file paths
- file names for viewing the current state
- command names
- shelf names
- root `design/` adoption and exact design-shelf path
- project-local rule names

## Default Root Agent Files

For the current shared scope, `pj-template` assumes both Codex and Claude Code are first-class targets.

- keep root `AGENTS.md` for the Codex entry route
- keep root `CLAUDE.md` for the Claude Code entry route
- if either file is absent during `pj-template` adoption, install it rather than leaving the route implicit
- if token optimization is adopted, install the local runtime token note first, then fill missing `AGENTS.md` and `CLAUDE.md`, and only then consider optional memory or continuation support

## Keep On The Template Side

- progression method
- the overall path to completion
- how entry surfaces are built
- how `current / support / historical / generated` are separated
- how external tools are classified and where they may be placed
- how restart and handoff are handled
- how publication responsibility is handled
- how heavy structure cleanup should be
- whether runtime-sensitive surfaces live locally or downstream

Keep method and branching conditions on the template side.

## Keep On The Project-Specific Side

- that project's completion definition
- that project's current canonical surface
- that project's runtime, DB, and caller facts
- owner-only decisions
- that project's paths, shelf names, commands, and operating constraints

Keep content and final judgment on the project-specific side.

## Do Not Put Here

- any specific project's current state
- any specific project's task state
- any specific project's operating log
- any specific project's register body

## Return Path

If in doubt, go back to `../README.md`.

## Boundary With Reference

You may read discussion logs under `../reference/` as history and failure analysis.
Current authority still lives under `pj-template`.

For time-bound judgment calls and audit-wave notes split out of `project-progression-rule-integration-audit.md`, read:

- `../reference/pj-template-progression-rule-audit-history-20260608.md`

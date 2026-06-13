# Specification, Review, and Skill Policy

**Purpose**: Define portable rules for specification-first work, independent review, and reusable agent-skill extraction.

This policy concretizes the specification / review / skill side of `../frameworks/project-progression-rule.md`, especially:

- `derive task and design from the definition of completion`
- `make completion conditions explicit before implementation`
- `advance in a reviewable form`

Framework-family selection belongs to `../frameworks/framework-selection-guide.md`.
Mismatch classification after review belongs to `../frameworks/decision-to-implementation-consistency-review.md`.

## 1. Write Specifications Before Complex Implementation

For complex or high-risk work, write a specification before implementation.

When useful, split it into:

1. Requirements
2. Design
3. Task breakdown

Small tasks may use a short inline spec, but success criteria must still be explicit.

If a design spec is treated as completion-level, use:

- policy: `spec-review-and-skill-policy.md`
- checklist: `../checklists/design-spec-completion-checklist.md`

### 1.1 Minimum Design Trace When Implementation Comes First

For work that becomes hard to explain afterward, record at least:

1. `purpose`
2. `impact`
3. `execution order`
4. `rollback`
5. `postcheck`

## 2. Convert Ambiguous Goals

Before implementation, convert an ambiguous goal into a measurable outcome.

Examples:

- `clean it up` -> concrete criteria for naming, placement, and complexity
- `fix the bug` -> expected behavior and regression check
- `organize the files` -> inventory, classification, accepted actions

## 3. Independent Review

For important design or risky change, the reviewer should be able to judge from:

- the artifact or diff
- stated requirements
- verification evidence
- known risks

The reviewer must not need the full conversation history.

For security-sensitive changes, a threat model or equivalent boundary note may be prepared before review.
If a portable baseline is needed, use:

- `../checklists/security-review-checklist.md`

## 4. Skill Extraction

When the same instruction, workflow, or reference material repeats across tasks, consider extracting it into a reusable skill, template, checklist, or policy.

A good skill defines:

- when to use it
- input and output
- key constraints
- completion criteria
- fallback behavior

## 4.5 Adopting External Workflow Patterns

When a useful pattern is found in an external repo, skill, or workflow:

1. check conflict with existing rules
2. adopt only the useful part
3. state what is not being adopted

Do not import whole workflows if they replace the repo's core rules.

## 4.6 External Tools

Before adopting an external tool, decide only these points:

1. where it will live
2. what it helps with
3. what it is not authoritative for
4. where accepted results must be written back

Use:

- `external-tool-placement-policy.md`
- the target project's local operator guide or adoption note

Do not leave recurring tool usage as session-only habit.
If it repeats, promote it into a clear project rule or support tool.

## 5. Keep Reusable Assets Portable

Unless something is an explicit example, avoid project-specific paths, credentials, role names, and database assumptions in reusable assets.

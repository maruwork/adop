# Shared Policies

This shelf stores reusable operating rules that can be applied across projects.

The documents here are shared concretizations under `project-progression-rule.md`.
Their strength order is:

1. `project-progression-rule.md`
2. each shared rule under `policies/`
3. project-specific rules

Project-specific rules may concretize these shared rules, but must not contradict higher authority.

Keep prose in clear shared English.
File names, status values, classification codes, schema keys, and CLI options should stay in the exact English form needed by tooling.

## Shelf Position

Treat this shelf as the shared concretization layer under `project-progression-rule.md`.
Follow the first-read order in `../README.md`.

### Highest-Priority Pre-Start Gate

The following file is not optional support material.
Treat it as the highest-priority gate before starting work:

- [execution-readiness-gate-policy.md](./execution-readiness-gate-policy.md)

Do not claim `ready to proceed`, `ready to execute`, `ready to handoff`, or `planning/spec complete` before that gate is passed.

For the top-level explanation of the five-layer model, read the framework side first:

- [../frameworks/goal-path-checkpoint-task-design-framework.md](../frameworks/goal-path-checkpoint-task-design-framework.md)

## Baseline For Reuse

- use the five-layer body from the framework shelf directly
- use this shelf for pre-start checks and required work-design rules
- replace paths, file names, and command names per project
- return to `../README.md` if unsure

This is not a shelf for accumulating project-specific rules.
Add only shared concretizations that help projects apply the higher rule.

## Open These Policies First

- execution and stopping
  - [execution-readiness-gate-policy.md](./execution-readiness-gate-policy.md)
  - [verification-and-retry-policy.md](./verification-and-retry-policy.md)
- entry and reading split
  - [entry-guide-reference-separation-policy.md](./entry-guide-reference-separation-policy.md)
- file and shelf structure
  - [file-operation-policy.md](./file-operation-policy.md)
  - [naming-and-shelf-policy.md](./naming-and-shelf-policy.md)
  - [external-tool-placement-policy.md](./external-tool-placement-policy.md)
  - [project-template-installation-gate-policy.md](./project-template-installation-gate-policy.md)
  - [project-publication-responsibility-policy.md](./project-publication-responsibility-policy.md)
- agent work
  - [context-management-policy.md](./context-management-policy.md)

## Detailed Policies

- open agent detail, task detail, and project-template adoption detail only when needed
- open [external-tool-placement-policy.md](./external-tool-placement-policy.md) before introducing a new external helper, adapter, memory tool, or AI-facing local file
- treat overlapping policies as later consolidation candidates

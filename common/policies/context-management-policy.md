# Context Management Policy

**Role**: Prevent context rot and context pollution during long sessions, resume flows, handoffs, and multi-turn design work, so later AI runs can recover the same meaning.

This policy concretizes the context side of `../frameworks/project-progression-rule.md`, especially:

- `re-ground in the canonical source`
- `do not keep current state only in your head`
- `do not mix entry surfaces`
- `do not stop after listing incomplete items`

## 1. Read Context Source-First

Read context from sources, not from memory.

Preferred order:

1. search
2. minimum required file or range reads
3. generated inventory or projections
4. transcript summary
5. current diff

Do not assume a full reread. Recover only the needed slices in a source-first way.

## 2. Separate Canonical State from Generated Context

Decision, inventory, plan, classification, summary, and report are not the same thing.

- canonical state
  - current rule / current path / current truth
- generated context
  - inventory / projection / summary / report / continuation artifact

Do not mistake generated context for canonical state.

## 2.5 Keep One Canonical Home for Each Rule

Do not scatter the same reusable rule across multiple documents.

When adding or strengthening a rule, decide first:

1. which file is the canonical source for that rule
2. which files should only reference it
3. where current-case application belongs
4. where fail-close enforcement lives: validator, healthcheck, or gate

Outside the canonical rule file, only the following are normally allowed:

- a pointer to the canonical rule
- application to the current case
- entry, route, or file mapping specific to that document

Do not redefine judgment conditions, required fields, stop-reason schema, or completion conditions in different wording outside the canonical source.

For the top-level judgments, stop conditions, and re-grounding conditions related to `project-progression-rule.md`, treat that file as canonical first. This policy only explains the context-specific side.

If the same point must be explained repeatedly in different documents, the weakness is in the canonical source, the entry route, or the current-case application surface. Fix the structure instead of adding duplicated prose.

## 3. Close Drift-Prone Work with a Continuation Note

Long tasks, resume-oriented tasks, and handoff-oriented tasks should leave a continuation note.

At minimum include:

- goal
- completed work
- known canonical facts
- already_paid_explanations
- incomplete items
- touched files
- verification
- next safe action

For long-running tasks or tasks with repeated explanations, the continuation note should state what is already fixed and does not need to be re-explained.
Move that context back into a repo-native artifact instead of keeping it only in session memory.

## 4. Avoid Context Pollution

Do not confuse the following with project knowledge:

- logs
- caches
- generated outputs
- historical sessions
- user-global tool state
- repo-external runtime state

They may be read when needed, but they are not canonical.

## 4.5 Boundary for Global Settings

- Rules that decide project structure, placement, verification, workflow, or governance belong inside the project or in an explicitly declared shared canonical source.
- User-global areas should hold only truly global items such as credentials, installed tools, plugins, skills, caches, runtime logs, and session state.
- Do not use a global area as the canonical home for project-specific governance.
- Do not create a project that requires reading a user's private global settings just to understand the project.
- If a global setting affects project execution, write the requirement on the project side rather than relying on a private global file.

## 5. Clean Review

Design and review should target artifacts, not the mood of the active session.

When needed, insert a clean-context review pass that reevaluates the work using only the minimum source set.

The purpose of clean review here is to regularize what should be reread as canonical source.
Detailed procedures for mismatch classification and false-complete judgment belong to `../frameworks/decision-to-implementation-consistency-review.md`.

## 6. Capture Recurring Shorthand and Comparison Targets

When proper nouns, comparison targets, metaphors, or shorthand appear repeatedly and literal meaning alone is not enough to resolve design, review, or tasking intent, treat the term as a **context object with attached expectations**.

Rules:

- do not stop at a glossary entry
- store the following in a project-local register:
  - what it refers to
  - which expectations it carries
  - what it does not mean
  - which canonical or intake source supports it
  - when it should be updated
- later AI runs should read that register first when the term appears
- do not assume the user must re-explain a term whose meaning already exists in the repository

This rule is not about increasing literal definitions.
It is about preserving what the term is expected to imply so later AI runs do not drift in interpretation.

The target project may currently use a project-local comparison-target or shorthand register for this purpose.

## 7. English Label Interpretation Rule

Treat English labels by their **label type**, not just their meaning.

What confuses later AI runs or operators is often not the English word itself, but whether it is:

- descriptive prose
- a fixed value
- a variable or field name
- a command, option, or policy name

Rules:

1. If it is just descriptive wording, write the meaning plainly in the local language used by the project.
2. If it is a fixed value, attach the label type, such as `status value`, `verdict value`, or `field value`.
3. If it is a variable or field name, wrap it in backticks and say that it is a variable or field name.
4. If it is a command, option, or policy name, label it as such.
5. Write the meaning first in prose, then append the original label only if needed.

Good examples:

- `currently active (status value: "ACTIVE")`
- `the parent task remains in continue state (parent_verdict value: "continue")`
- ``active_branch`` as a field name
- `the --strict option of governance_healthcheck.py`

Bad examples:

- `active`
- `continue`
- `flowing`
- `reroute`

This rule is not about translation.
It exists so a reader can tell at a glance what kind of label they are looking at.
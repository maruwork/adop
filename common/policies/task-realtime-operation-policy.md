# Task Realtime Operation Policy

## Purpose

Define reproducible operational rules so task-state changes are written back into the project's canonical task surface in the same turn.

## 1. Core Rule

- do not separate task-state mutation from canonical task updates
- whenever task state changes, update the canonical task state in the same turn
- do not keep current state only in the AI's head

## 2. Canonical Task Surface

Each project should have one in-repo canonical surface for current task state.

If the project also has overview boards, execution boards, or external mirrors:

- treat them as projections or mirrors
- update them only after canonical task state is updated
- do not let them replace the canonical task surface

## 3. What Counts as a Mutation

Treat these as task-state mutations:

- creating or promoting a current task
- creating or closing a branch task
- creating or resolving a human decision
- changing current status
- changing `next action` or equivalent current-routing fields

Do not treat typo-only cleanup or report-only wording cleanup as mutations.

## 4. Operation Order

Use this order:

1. confirm the current scope and preconditions
2. update the task item or canonical task surface
3. update any local projections that depend on it
4. verify consistency
5. sync mirrors only if the project uses them

## 5. Verification Rule

At minimum confirm:

- the canonical task surface reflects the new state
- no stale current item remains visible as current
- parent / branch / decision relationships are still intact
- any projection or mirror still matches the canonical state

## 6. Handoff Rule

When handing work to another AI, leave at least:

- active bundle id if the project uses one
- current task surface
- changed item files
- next action
- unresolved decisions or blockers

## 7. Route Rule

If the project distinguishes routes such as repo, DB, replica, or planning-only, record one primary route for each active task.

Do not let route labels replace the underlying canonical task state.

## 8. Keep / Avoid

Keep:

- same-turn task writeback
- one canonical current task surface
- projections following canonical updates

Avoid:

- postponing task updates
- using an external tracker as the only current source
- operating current state from memory alone

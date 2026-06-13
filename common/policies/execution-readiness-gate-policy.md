# Pre-Start Check And Execution Rule

Purpose: one shared gate for confirming whether work may really proceed, whether design is sufficient, and where work must stop.

This policy mainly concretizes these parts of `../frameworks/project-progression-rule.md`:

- conditions for proceeding
- pre-start checks
- stop conditions
- checks before claiming checkpoint advancement

If even one item is ambiguous, unchecked, or unmet, work must not proceed.
For every major section, the reader must be able to answer not only what was checked, but how it was checked.

- what was inspected
- which file, rule, command, or output was used as evidence
- where that evidence will be recorded

## 1. Goal

- completed state
- scope for this wave
- out-of-scope area
- unmet conditions
- what this work finishes
- what this work does not finish
- subject of the completion report

## 2. Path

- the order of progression
- where work stops
- dependencies before and after

## 3. Checkpoints

- which checkpoints exist
- in what order they are passed
- what drift each checkpoint prevents
- what must be true before and after each checkpoint

## 4. Tasks

- whether every checkpoint has the tasks it needs
- whether anything is missing
- whether work from another checkpoint has been mixed in
- whether the order is correct

## 5. Design

For each task, confirm that the following exist:

- start conditions
- where to read
- where to write
- where not to touch
- what will be done
- output
- pass conditions
- failure conditions
- stop conditions
- evidence
- result destination

Each task design must contain at least:

1. `Task ID`
2. `Parent Theme`
3. `Parent Checkpoint`
4. `active bundle id`
5. `active bundle type`
6. `success subject`
7. `scope for this turn`
8. `out-of-scope for this turn`
9. `purpose`
10. `why this task is needed`
11. `start conditions`
12. `inputs`
13. `allowed read locations`
14. `allowed write locations`
15. `must-not-touch locations`
16. `actions`
17. `expected output`
18. `pass conditions`
19. `failure conditions`
20. `stop conditions`
21. `send-back conditions`
22. `conditions that escalate to human judgment`
23. `evidence`
24. `result record destination`
25. `final judge`

## 6. Execution Surface

- where the actual work will happen
- where the result will be left
- where records and evidence will be left

## 7. Test, Tool, And Command

- required tests
- required tools or scripts
- commands that will be used

## 8. Preconditions

- environment variables
- DB connection
- services
- permissions
- fixtures or data

Anything missing must be written as a named blocker.

## 9. Connectivity Across Layers

- `goal -> path`
- `path -> checkpoint`
- `checkpoint -> task`
- `task -> design`

## 10. Completion Boundary

- all tasks completed means all checkpoints passed
- all checkpoints passed means the path is complete
- a complete path means the goal is achieved
- the boundary between this wave and later work is clean
- the subject of the completion report does not change midway

## 11. Ownership And Scope

- owner
- scope for this wave
- out-of-scope for this wave
- execution order

## 12. Failure Handling

- under what conditions work stops
- under what conditions it becomes blocked
- under what conditions it is sent back
- under what conditions it may resume
- what is recorded on failure

The following always require a stop before proceeding:

- moving, deleting, renaming, or archiving canonical files
- changing the meaning of root entry, rule, taxonomy, boundary, or disposition
- DB writes or writes into persistent external systems
- use of credentials, secrets, paid APIs, or private remote services
- changes to branch, merge, release, or deployment policy
- changes to ownership boundaries
- promotion of temporary output or external input into canonical authority
- selection of a future operating model that is not backward compatible

The following may proceed without stopping:

- read-only investigation
- local lint, test, or consistency checks
- additive changes that do not redefine existing rules
- reversible branch-local fixes
- reports, classifications, and execution plans

When stopping, write at least:

- stop reason
- required judgment
- options
- recommendation
- basis for judgment
- restart conditions
- whether any work may still continue while stopped
- if so, what that bounded scope is
- the next file that must be touched
- the minimum scope that should still be filled this turn
- the next action after judgment

## 13. Result Confirmation And Reflection

- what will be inspected to confirm the result
- where the result will be recorded
- where the current state will be reflected
- how `current` and `historical` are separated

## 14. Whether The Later Stages Are Visible

- how far this wave will go
- what comes next
- whether later work already has the prerequisites it needs
- whether this is a premature start that will only stop later

## 15. Required Approval And Rollback Means

- required approvals
- required permissions
- rollback means if the work fails

## 16. Pass Condition

Work may proceed only when all of the following are true:

- `goal, path, checkpoint, task, and design` are connected
- `active bundle id` and `active bundle type` are fixed
- `success subject`, `scope for this turn`, and `out-of-scope for this turn` are fixed
- the subject of the completion report is fixed
- the execution surface and result-storage surface exist
- required tests, tools, and commands exist
- prerequisites are confirmed or explicitly written as blockers
- ownership, scope, order, and failure handling are clear
- an evidence source can be answered for each major section
- `closed bundles` are not mixed with `post-close residual work`

## 17. References

- [../frameworks/goal-path-checkpoint-task-design-framework.md](../frameworks/goal-path-checkpoint-task-design-framework.md)
- [../frameworks/project-progression-rule.md](../frameworks/project-progression-rule.md)
- [./verification-and-retry-policy.md](./verification-and-retry-policy.md)
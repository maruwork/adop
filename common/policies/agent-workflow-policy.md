# Agent Workflow Policy

**Purpose**: Define a portable workflow for agent-assisted development that carries work consistently from investigation through implementation, verification, and handoff. This policy also defines the boundary between the designer and the executor, rerouting after branch completion, and how stop situations are handled.

This policy concretizes the day-to-day agent-operation side of `../frameworks/project-progression-rule.md`, especially:

- `choose the next bounded move`
- `execute within limits`
- `stop conditions`
- `decide whether to continue or close`
- `do not end with status-only reporting when incompletion is visible`

## 1. Work Phases

Use the following seven stages as the default flow:

1. `Investigate`
   - read related files, inputs, data, and dependencies
2. `Diagnose`
   - identify the problem, scope, impact, and unresolved points
3. `Propose`
   - state the implementation direction, verification method, and next action
4. `Implement`
   - change only the agreed scope
5. `Verify`
   - run lint, tests, inventory, and read-only checks
6. `Report`
   - summarize changes, verification results, residual issues, and next action
7. `Close`
   - close only when acceptance criteria are met; otherwise reroute into the next task

For small typo fixes or inventory-only work, it is acceptable to pass through only the necessary stages in a shorter form.

## 1.5 Standard Pre-Start Judgment Order

When a new instruction arrives, decide only these points before starting:

1. what kind of work this is
2. where the current source of truth is
3. whether the work should be split into `investigate / judge / reflect`
4. whether any planning surface or helper investigation is actually needed
5. what the next bounded action is

Do not start by widening into extra structure unless the task clearly needs it.

### 1.5.1 Basic Three-Way Split

1. `investigate`
   - read the source
   - collect references and impact scope
   - do not make the final judgment here
2. `judge`
   - decide keep / archive / remove / reroute
   - decide SSOT updates, task-state judgment, and shelf judgment only here
3. `reflect`
   - update registers, tasks, policies, checklists, or file moves

Rules:

- do not `judge` before `investigate` finishes
- do not `reflect` before `judge` finishes
- helper agents should normally be delegated only the `investigate` part
- the owner of final judgment owns `judge` and `reflect`

### 1.6 User-Facing Declaration Before Starting

State the use of a helper planning surface and any helper-agent investigation delegation to the user in one sentence before starting.

- `I will use an additional planning surface. <reason>` or `An additional planning surface is unnecessary. <reason>`
- `I will delegate investigation to a helper agent. <reason>` or `Investigation delegation to a helper agent is unnecessary. <reason>`

If delegating, continue by stating the request text or dispatch conditions in a form that can be passed through directly.

## 2. Branch Completion Is Not Task Completion

Do not treat completion of a `branch`, `PR`, or `patch` alone as `no task left`.

If any of the following remains, reroute to the parent task:

- incomplete items in the parent task
- the next branch-local task under the same goal
- the next action under the same dispatch
- inventory, verification, or classification that can continue read-only

At branch completion, always state:

- the completed branch-local scope
- the remaining items on the parent task
- the next branch-local or read-only action that can proceed

## 3. Gates and Stop Judgments

Follow [execution-readiness-gate-policy.md](./execution-readiness-gate-policy.md) when human judgment is needed or when stop reasons must be organized.

Important points:

- if a gate sits between propose and implement, check whether any branch-local work can still proceed before the judgment
- reversible preflight, read-only inventory, and local additive documentation may proceed while waiting for human judgment
- if an owner-owned dirty area exists, follow [diff-ownership-and-wave-close-policy.md](./diff-ownership-and-wave-close-policy.md) for the continuation route

Additional rules:

- if `owner judgment required = no`, do not stop by asking the user whether work may continue
- in that case, write `what to fill next` and `how far continuation is allowed` onto the current surface and continue
- also write `the next file that must be edited` and `the minimum fill required in this turn`

## 3.5 Prefer Code Harness Assets

Prefer increasing **code harness assets** over relying on natural-language effort.

Priority order:

1. check whether repeated instructions can be turned into scripts, hooks, tests, or checklists
2. check whether recurring assumptions or prohibitions can be fixed in policy or explicit project rules
3. check whether agent-to-agent handoff can be left in files, diffs, logs, or queues instead of chat alone
4. if the same problem repeats, suspect missing harness assets before making prompts longer

## 4. Boundary Between Designer and Executor

- `designer`
  - fixes scope, source of truth, output, and completion condition
- `executor`
  - reads, edits, and verifies inside that boundary

Do not hand work to an executor when the source of truth, rename / archive judgment, or output contract is still unsettled.

## 5. Economic Rule for Delegation

Decide not by `can this be delegated`, but by `is delegation faster`.

Compare:

- `preparation cost`
  - explaining preconditions
  - organizing prohibitions
  - listing references
  - specifying output format
  - review and rollback cost
- `recovery value`
  - work volume
  - repeat volume
  - mechanical nature
  - reusability of the returned artifact

Rules:

- if `preparation cost >= recovery value`, do not delegate
- delegate only when `preparation cost < recovery value`

### 5.1 Conditions for Parallel Dispatch

- there are two or more issues and their cause regions are independent
- there is no shared state, overlapping write set, or strong order dependency
- each work unit can be explained as self-contained
- the root owner can perform an integration review at collection time

### 5.2 Bite-Sized Execution Units

- 1 unit = 1 clear action
- when possible, keep each unit small enough to verify within minutes
- always include the exact file path, expected outcome, and verification method

## 6. Prefer Additive and Reversible Work

Prefer:

- read-only inventory
- classification tables
- verification
- additive portable copies
- generalization that keeps the source in place
- added notes, registers, and packets

Handle carefully:

- in-place rename
- archive moves
- role changes for canonical files
- DB writes
- meaning changes to the root entry

## 7. Do Not Hide the Root Cause

When a problem is structural, look at the root cause instead of stopping at a patch.
At the same time, avoid an all-at-once rewrite. Start with inventory, scope splitting, reversible unblocking, and next-PR design.

## 8. Reporting Format

During progress or at completion, state briefly:

- what is being examined now
- what is fixed
- what remains unfixed
- the next action that can proceed

## 9. Relationship to Project Rules

Keep the project entry file and local runbook thin.
Put reusable workflow rules in the common policy shelf.
Keep project-specific enforcement details, protected paths, database gates, and approval roles in project governance files.

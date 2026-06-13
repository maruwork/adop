# Decision-to-Implementation Consistency Review

Portable baseline framework for checking whether design decisions, requirements, implementation, and operating procedures still align.

This framework concretizes the consistency-review side of `project-progression-rule.md`, especially:

- `do not count local movement as forward progress`
- `separate written completion from actual completion`
- `detect drift`
- `identify the correction surface`

The `truth-boundary drift` handled here does not redefine the canonical source for context surfaces themselves.
The normative boundaries for `current / history / artifact / cache` belong to `../policies/context-management-policy.md`.
This framework only classifies:

- whether those boundaries are broken at review time
- what should be fixed first to recover alignment

## 1. Purpose

- check whether design decisions and implementation reality still match
- detect the gap between `marked complete` and `actually complete` early
- surface explanation / implementation / operation misalignment before adding more implementation

## 2. Minimum Inputs

- decision record or design spec
- current implementation surface
- current operational route or runbook
- current validation or test surface

## 3. Review Questions

1. Does each claim in the decision or design exist in the implementation?
2. If the implementation exists, are the explanation or runbook surfaces stale?
3. Are current truth and history / artifact / cache getting mixed?
4. Do owner, trigger, input, output, and completion condition still match?
5. Even if something is marked `complete`, are residue or hidden blockers still present?

## 4. Output Contract

Produce at least:

- aligned items
- misaligned items
- mismatch type
  - missing implementation
  - stale documentation
  - stale operation note
  - truth-boundary drift
  - false-complete claim
- correction target
  - code
  - design/spec
  - runbook/manual
  - register/canonical

## 5. Classification

| result | meaning |
|---|---|
| `aligned` | decision / design / implementation / operation still match |
| `doc-drift` | implementation exists but explanation surfaces are stale |
| `implementation-gap` | implementation is missing against the written claim |
| `truth-boundary-drift` | the `current / history / artifact / cache` boundary is broken |
| `false-complete` | the work is still incomplete but is being treated as complete |

## 6. Handoff Rule

- When you find a mismatch, decide first what must be fixed to restore current truth.
- Separate items that can be repaired by explanation surfaces alone from items that require implementation changes.
- Revoke a close verdict if needed to fix a false-complete state.

## 7. Completion Condition

This review counts as complete only when:

- mismatches are classified in the current canonical surface
- the correction surface is unique
- no false-complete claim remains
- downstream readers can tell without hesitation what needs to be fixed to recover alignment

<a id="flow-integrity-review-framework"></a>
## 8. Flow Integrity Review

For multi-step flows, review `broken linkage` separately even when each individual file exists.

Minimum checks:

- Is one end-to-end flow defined from start to finish?
- Is the owner / input / output contract clear for each step?
- Is the boundary between human judgment and auto-continue explicit?
- Do notification, recording, approval, and updates carry into the next step?
- Has the flow degraded into `reference only`, `spec only`, or `implementation only`?

Review sequence:

1. fix the flow boundary
2. record the contract of each step
3. confirm linkage
4. confirm abnormal branches
5. classify findings into `alignment repair / new implementation` and `root fix / surface fix`

Minimum evidence to leave behind:

- execution timestamp
- `PASS / WARNING / FAIL`
- the checked file / command / screen / DB result
- observations
- next action
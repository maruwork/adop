# Task Specification Template

**When to use**: Use this when fixing what one task should create, change, and verify.  
**Replace**: task ID format, target component names, verification style, side-effect handling.  
**Do not write**: project-wide requirements, the current-state canonical source, or the final verdict body.

**Task ID**:
**Task Name**:
**Type**: mock / production / research / maintenance / poc
**Owner**:
**Dependencies**:
**Preconditions**:
**Postconditions**:
**References**:

## 1. Scope

Describe what will be implemented.
Follow the rule `1 task = 1 clear outcome`. If one task carries multiple outcomes, consider splitting it.
If the task introduces a different subject or outcome from the requirements or basic design, treat it as a split gate.

**Out of scope**:

- TBD

## 2. Target Files or Components

Make sure create / modify / delete coverage matches the task outcome with no gaps or excess.

| Path / Component | Operation | Role |
|---|---|---|
|  | create / modify / delete |  |

## 3. Implementation Requirements

### Requirement 1

Write the behavior, constraints, and interface expectation.
Do not leave only implementation steps; write behavior that can flow into acceptance.
If only procedure remains and behavior is still unclear, stop instead of calling it complete.

### DB Test Data Requirements

If a database is involved, specify NOT NULL, CHECK, foreign-key, and seed prerequisites.

## 4. Interface Contract

| Kind | Name | Definition | Notes |
|---|---|---|---|
| Function / API / DB / File |  |  |  |

If no interface is specified, write: `No interface specified; implementation may choose the internal shape.`
Do not start implementation while the contract is still undefined.

## 5. Acceptance Criteria

Write observable conditions that let a third party judge pass / fail.

| ID | Criterion | Verification |
|---|---|---|
| C1 |  |  |

If acceptance loses the upstream requirement or a third party still cannot start verification, do not call the task complete.

## 6. Idempotency and Side Effects

- Idempotency type:
- File writes:
- DB writes:
- External calls:
- Re-run behavior:

Do not leave approval-dependent writes or re-run handling implicit.

## 7. Implementation Order

Write steps in dependency order.

1. TBD
2. TBD
3. TBD

If this order differs from the requirements or basic-design path, explain why or consider splitting the task.

## 8. Downstream Impact and Review Notes

- Downstream impact:
- Material change review needed:
- Human decision gate:

Do not leave the human decision gate hidden. If needed, state it here as a stop condition.
Treat approval boundaries, external writes, and policy changes as stop gates instead of passing them hidden into execution readiness.
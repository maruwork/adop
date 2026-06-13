# Requirements Template

**When to use**: Use this when structuring requirements for a project or feature.  
**Replace**: project name, stakeholders, requirement ID scheme, success conditions, reference materials.  
**Do not write**: implementation detail, current-state management, or project-specific operating procedures.

**Project**:
**Author**:
**Date**:
**Approver**:

## 1. Overview

### Purpose

State what this project must achieve.
Keep the completion state, the subject of completion reporting, and the closure scope for this requirement stable and explicit.

### Background

State why this is needed now.
Do not overload it with operating context or future plans that are not directly tied to the current scope.

### Reference Cases / Materials

- Similar cases:
- Reference specification:
- Related ADR / decision:

### Stakeholders

| Stakeholder | Role | Expected Benefit |
|---|---|---|
|  |  |  |

If the subject of completion reporting spans multiple projects or multiple capabilities, stop and consider splitting by goal or checkpoint.

## 2. Scope

### In Scope

- TBD

If multiple capabilities are mixed together, do not force them through one requirement; consider splitting by goal or checkpoint.

### Out of Scope

- TBD

### Assumptions and Constraints

- TBD

### Success Criteria

- What must be true to count as complete:
- What state must be verified before handing off to the next phase:
- Whether the requirement is ready to hand off into basic design:

As a completion gate, do not proceed to basic design if any of those three points remain hidden.

### Primary User Workflow

1. User:
2. Start condition:
3. Main actions:
4. Expected result:

If the start condition or expected result cannot be stated, do not proceed until the workflow is strengthened.

## 3. Functional Requirements

### Requirement Structuring Notes

- Write each requirement so the subject, trigger, and expected result are clear.
- Do not mix mandatory and optional conditions.
- Lead with required behavior, not implementation method.
- If one requirement mixes multiple capabilities or multiple states, consider splitting it.
- Do not pass through a requirement whose acceptance cannot be verified.

| ID | Requirement | Acceptance Criteria | Priority |
|---|---|---|---|
| FR-1 |  |  | must / should / could |

### Edge Cases and Failure Conditions

Write the stop and failure surface that should be handed down into task design.

| Case | Condition | Expected Behavior |
|---|---|---|
| EC-1 |  |  |

## 4. Non-Functional Requirements

| ID | Category | Requirement | Target |
|---|---|---|---|
| NFR-1 | Performance |  |  |
| NFR-2 | Security |  |  |
| NFR-3 | Reliability |  |  |

If multiple subsystems or actors have independent lanes, consider splitting them as a split gate instead of overloading this template.

## 5. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
|  | low / medium / high | low / medium / high |  |

If approval boundaries, external writes, or unresolved owners are visible, mark them explicitly as stop gates instead of passing them hidden into basic design.

## 6. Requirement Quality Check

- [ ] The subject of completion reporting is fixed.
- [ ] In Scope and Out of Scope do not conflict.
- [ ] Success Criteria are written as handoff conditions for the next phase.
- [ ] The start condition and expected result of the Primary User Workflow are explicit.
- [ ] Acceptance Criteria can be checked for each requirement.
- [ ] Non-functional requirements include target values.
- [ ] Major edge cases are covered.
- [ ] Assumptions, constraints, and completion conditions are explicit.
- [ ] No unresolved point remains hidden.

## 7. Glossary

| Term | Definition |
|---|---|
|  |  |
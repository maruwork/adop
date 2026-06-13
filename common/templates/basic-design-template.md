# Basic Design Template

**When to use**: Use this after requirements are fixed and you need to decide structure and technology choices.  
**Replace**: layer names, diagrams, interface names, related decision-tracking method.  
**Do not write**: task-level breakdown, current-state management, or project-specific current operations.

**Project**:
**Author**:
**Date**:
**Status**: Draft / Review / Approved

## 1. Architecture

Describe the system boundary, major components, and runtime flow.
Write it at a level where the boundary and flow can be handed down to task design.
If this creates a different subject or order from the requirements workflow, stop and review it as a split gate.

```text
[client] -> [service] -> [storage]
```

### Option Comparison

| Option | Pros | Cons | Fit |
|---|---|---|---|
| A |  |  | high / medium / low |
| B |  |  | high / medium / low |

### Recommended Direction

- recommendation:
- reason for adoption:
- rejected alternatives:

Keep the line between the adopted option and rejected options explicit so downstream tasks work from the same assumptions.
If this document changes the boundary or completion subject from the requirements, treat that as a stop gate.

## 2. Technology Choices

Document choices so they can flow into task-spec preconditions and out-of-scope boundaries.

| Layer | Choice | Reason | Constraints |
|---|---|---|---|
| Frontend |  |  |  |
| Backend |  |  |  |
| Data |  |  |  |
| Infrastructure |  |  |  |

## 3. Data Design

Document the entities, fields, and constraints that should flow into task specs or DB specs.

| Entity/Table | Purpose | Key Fields | Constraints |
|---|---|---|---|
|  |  |  |  |

## 4. Interface Design

Document input, output, and error behavior that can be handed down to task-spec interface contracts.

| Interface | Input | Output | Error Behavior |
|---|---|---|---|
|  |  |  |  |

If any of input, output, or error behavior remains hidden at handoff time, do not call this complete.

### Related Decisions

| Decision | Status | Note |
|---|---|---|
| ADR / design note | draft / proposed / accepted |  |

## 5. Security and Operations

- Authentication / authorization:
- Secret handling:
- Logging and monitoring:
- Backup / recovery:
- Performance target:

## 6. Open Issues

Any open issue without an owner or due date is a stop gate.
Treat mismatched owners or boundaries between requirements and task specs as stop gates too.

| Question | Owner | Due |
|---|---|---|
|  |  |  |
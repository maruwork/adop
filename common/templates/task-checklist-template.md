# Task Specification Checklist

**Use When**: reviewing whether a task specification is clear enough for implementation and verification.  
**Replace Per Project**: Task-ID format, approval handling, and project-specific evidence names.  
**Do Not Put Here**: the task specification body itself, current-state management, or detailed project-specific workflow rules.

## 1. Basic Information

- [ ] Task ID and title are clear.
- [ ] The owner or role is identified.
- [ ] Dependencies are explicit, or `none` is stated.
- [ ] Preconditions and postconditions are concrete.
- [ ] Referenced documents or issues exist.

## 2. Scope

- [ ] In-scope work is concrete.
- [ ] Out-of-scope work is explicit.
- [ ] Affected files or components are listed to the extent they are known.
- [ ] Changing an unlisted file requires approval or a task update.

## 3. Implementation Guidance

- [ ] Required interfaces, APIs, schemas, and contracts are specified.
- [ ] Constraints are measurable.
- [ ] External dependencies are identified.
- [ ] When sequencing matters, the order of work is defined.

## 4. Acceptance Criteria

- [ ] Each criterion has an ID.
- [ ] Each criterion is measurable.
- [ ] Each criterion maps to a test, command, or review evidence.
- [ ] If security, performance, or data integrity matter, they are included in the criteria.

## 5. Side Effects And Idempotency

- [ ] Writes are enumerated.
- [ ] External calls are enumerated.
- [ ] Re-run behavior is defined.
- [ ] When needed, the rollback or cleanup path is explained.

## 6. Final Decision

```text
Ready for implementation: yes / no
Blocking issues:
Reviewer:
Date:
```
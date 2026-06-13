# Implementation Audit Checklist

**Use When**: checking design alignment, completion conditions, and side effects after implementation.  
**Replace Per Project**: verdict names, handling of the test-data contract, and names of related design records.  
**Do Not Put Here**: the body of the implementation plan, the live current-state authority, or a project-specific current board.

This checklist concretizes the following parts of `../frameworks/project-progression-rule.md` on the post-implementation verification surface:

- `verification`
- `definition of advancement`
- `completion-condition confirmation`

It is a reusable checklist for checking design alignment, completion conditions, side effects, and test-data alignment when relevant.

## 1. Checklist

- [ ] design record exists
- [ ] approval record exists
- [ ] completion conditions are explicit
- [ ] implemented items match the design
- [ ] non-target areas remain unchanged
- [ ] completion conditions are checked one by one
- [ ] no unexpected side effects or regressions exist
- [ ] the test-data contract is checked when applicable

## 2. Verdict

- PASS
- REQUIRES_REVISION
- RE_DESIGN

## 3. Completion Rule

- the result can be recorded with a reason
- the revision or redesign path can be stated clearly
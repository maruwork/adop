# AI Agent Runtime Bootstrap Checklist

**When to use**: Use this when defining the entry surface and boundaries for AI work in a new project.  
**Replace**: tool names, compression methods, context operations, rollback conditions.  
**Do not write**: the project's formal local rules themselves or day-to-day current operations.

This checklist concretizes the new-project bootstrap side of `../frameworks/project-progression-rule.md`, especially:

- `define the entry surface`
- `separate canonical and helper surfaces`
- `do not keep current only in your head`
- `make the AI re-ground somewhere explicit`

Use it as the first checklist for bootstrap decisions in a new AI agent runtime.

## 1. Entry / Boundary

- [ ] We decided to keep the root entry file thin.
- [ ] If examples are needed, we keep them to one representative note.
- [ ] We decided to push detail down into policies, manuals, checklists, or frameworks.
- [ ] We decided the boundary between repo-local and user-global surfaces.
- [ ] We decided not to treat external runtime config as the project SSOT.

## 2. Token Optimization Profile

- [ ] We decided to adopt token optimization selectively, not as an all-or-nothing bundle.
- [ ] We decided whether to use standard CLI compression.
- [ ] We decided whether broad context compression is in scope now or deferred.
- [ ] We decided whether external knowledge helpers or repo-wide compression are in scope now or deferred.
- [ ] We decided whether a proxy or budget-control layer is in scope now or deferred.
- [ ] We recorded the reason for every deferred item.

## 3. Search / Context Discipline

- [ ] We decided to prefer boundary-first and source-first reading over broad rereads.
- [ ] We decided to make targeted search and narrow reads the default.
- [ ] We defined how to use compact / clear / plan.
- [ ] We decided whether to treat 1 task / 1 session as the default work unit.

## 4. Authority / Safety

- [ ] We stated that token-optimization tools are not authority surfaces.
- [ ] We stated that compression tools do not decide truth, state, verdict, owner, or canonical placement.
- [ ] We defined rollback conditions if adoption increases misreads later.

## 5. Minimal Measurement

- [ ] Measure output reduction on key CLI commands.
- [ ] Measure whether explanation repayment decreases.
- [ ] Check that current facts are not lost before and after compact.
- [ ] Check that important errors do not get hidden.

## 6. Bootstrap Verdict

- [ ] We can describe the adopted setup in one line.
- [ ] Deferred items are split into later waves.
- [ ] We confirmed that the authority boundary still holds.
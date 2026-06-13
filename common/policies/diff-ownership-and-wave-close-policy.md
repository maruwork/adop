# Diff Ownership and Wave Close Policy

**Purpose**: Define a portable rule that prevents diffs from accumulating without ownership, instead of cleaning a dirty working tree in an ad hoc way.

This policy concretizes the diff-ownership and wave-close side of `../frameworks/project-progression-rule.md`, especially:

- `advance only the next bounded move`
- `do not count local movement as forward progress`
- `stop when it should stop`
- `do not move on while unknown diffs remain`

Use this policy when opening a new wave from a clean decision point to fix:

- what will land on the mainline in this wave
- which diffs become residual, monitor work, or generated follow-up
- when the wave can be closed before the next one starts

## 1. Terms

- `wave`
  - one execution unit that can be completed inside the repository
- `finish line`
  - the close condition that wave must reach
- `mainline`
  - what this wave actually closes
- `monitor residual`
  - a monitored residual that stays closed until its trigger appears
- `repo-external residual`
  - residual work that cannot be completed inside this repository because it depends on outside operators or dependencies
- `generated follow-up`
  - the bundle that updates indexes, inventories, or other generated artifacts after canonical sources change
- `scratch`
  - preliminary reading, experiments, candidates, first-pass output
- `unknown diff`
  - any diff that belongs to none of the categories above

## 2. Principles

### 2.1 One Wave, One Finish Line

- One wave should carry only a bundle that can be completed inside the repository.
- Dependencies on outside operators, human judgment, external callers, or deployment work should be split out as `repo-external residual` from the start.
- Do not open a wave if you cannot state its finish line.

### 2.2 Register First, Action Second

- Archive, reroute, restore, or shelf moves must be rowed or registered before execution.
- At minimum, fix these first:
  - `caller / reference reality`
  - `reroute destination`
  - `blast radius`
- Do not finalize archive keep, restore, or reroute until impact scope is understood.

### 2.3 Unknown Diff = 0

- Every diff must belong to one of:
  - `mainline`
  - `monitor residual`
  - `repo-external residual`
  - `generated follow-up`
  - `scratch`
- Do not open a new wave while `unknown diff` remains.

### 2.4 Close the Current Wave Before the Next

- Before opening the next large wave, close the prior one up to:
  - canonical reflection complete
  - residual separation complete
  - `unknown diff = 0`
- Do not stack the next wave on top of an unclosed one.

### 2.5 Generated Follows Canonical

- `index`, inventory, mirror, and generated notes should not be mixed into the canonical change bundle.
- Close the canonical source first, then handle follow-up as `generated follow-up`.
- If a generated file must be edited by hand instead of regenerated, record the exception reason explicitly.

### 2.6 Workspace Quarantine

- Put provisional reading, experiments, and scratch output in `workspace/`.
- Do not place undecided material directly into a canonical shelf.
- When promoting scratch, pass placement judgment and current reflection first.

### 2.7 Archive Is Not Disposal

- Archive is a historical holding shelf, not a disguised delete sink.
- Neither archive keep nor restore should be treated as final until it can be re-explained row by row.
- Do not create nested archive paths such as `archive/archive/...`.

## 3. Required Checks Before Opening a Wave

Before opening a new wave, confirm at least:

1. `finish line`
   - can it be completed inside the repository?
2. `scope`
   - can it close at the cluster, task, or register-row level?
3. `residual split`
   - are repo-external dependencies already separated from mainline?
4. `diff ownership`
   - are there no `unknown diff` items in existing changes?
5. `generated impact`
   - are index, inventory, or mirror follow-ups split as their own bundle?

If any one of these is unclear, cut the wave smaller.

## 4. Wave Close Criteria

A wave can be treated as closed only when:

- every row, cluster, or task inside the finish line is complete
- canonical docs, tasks, registers, and handoff agree
- any reopen condition is explicit as monitor residual
- anything that can only progress outside the repo is separated as repo-external residual
- `unknown diff = 0`

## 5. When to Stop and Split

If any of the following appears, split it instead of absorbing it broadly:

- repo-external operator action is required
  - send it to `repo-external residual`
- a restore requires code, runtime, or projection changes
  - reflect only the reopen decision in current canon and split implementation into another wave
- a cluster is too large for one row
  - split it into subcluster rows and continue
- generated follow-up is required
  - split it into a follow-up wave after canonical close

## 6. Prohibitions

- opening the next wave while `unknown diff` remains
- mixing repo-external residual into mainline
- progressing archive, reroute, or restore without a row or register
- mixing generated follow-up with canonical diffs when judging close
- placing provisional material in canonical shelves when it belongs in `workspace/`
- performing unowned diff cleanup just to make the worktree look clean

## 7. Required Report Items

When closing a wave, report at least:

- the finish line for this wave
- completed mainline
- monitor residual
- repo-external residual
- whether generated follow-up exists
- whether `unknown diff = 0` was achieved

## 8. Handling Owner-Owned Dirty Areas

- Do not let AI treat a still-owned unfinished area as something it can clean or overwrite on its own.
- Priority order:
  1. protect the owner's unfinished changes
  2. continue any work that can proceed independently
  3. if unavoidable, identify the target file and return the decision for owner intake
- First check whether work can continue in read-only mode.
- If there are files independent from the dirty area, continue there only.
- Even when continuing on a clean path around the dirty area, do not overwrite the owner's uncommitted work invisibly.
- Do not stop read-only or independent work merely because a dirty owner-owned area exists.

## 9. Related

- [agent-workflow-policy.md](./agent-workflow-policy.md)
- [file-operation-policy.md](./file-operation-policy.md)
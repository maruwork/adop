# Business Workflow Spine

**Purpose**: Define a portable functional spine for business workflows that still holds when the domain changes.  
**Positioning**: This is not a project-local role model or status model. It is a shared spine for `how work flows`.

## 1. What to Fix

Even when the domain changes, the core of a business workflow usually stays close to these four stages:

1. `design`
2. `pre-execution audit`
3. `execution`
4. `post-execution audit`

The content of the task may change between product development, quality control, or legal review, but this functional axis is usually stable.

## 2. Meaning of the Four Stages

### 2.1 Design

Fix:

- what will be done
- where completion ends
- target
- scope
- prohibited actions
- required evidence
- handoff conditions to the next stage

The role of design is not to maximize executor freedom without limits.
Its role is to turn work into an executable unit that later stages can audit.

### 2.2 Pre-Execution Audit

Fix:

- whether the task may proceed as written
- whether design is sufficient
- whether required approval exists
- whether risk classification is appropriate
- whether the work is safe to hand to an executor
- whether a human gate is required

Pre-execution audit is not post hoc criticism.
It prevents the accident of executing the wrong task correctly.

### 2.3 Execution

Fix:

- actual work
- intermediate artifacts
- self-checks
- tests or measurements
- bundled evidence

Execution does not close with `I did it`.
It becomes valid work only when it leaves artifacts that later stages can verify.

### 2.4 Post-Execution Audit

Fix:

- whether completion conditions were truly met
- whether required evidence is present
- whether the work should be sent back
- whether redesign is needed
- whether a close claim is valid

Post-execution audit is not just quality checking.
It is the final judgment surface for `close / reroute / reopen / human judgment`.

## 3. Why Use Four Stages

This four-stage split is durable because it does not depend on role labels or industry vocabulary.

- software development:
  - design -> design review -> implementation -> implementation audit
- quality control:
  - inspection design -> inspection plan review -> inspection execution -> result audit
- business improvement:
  - improvement design -> execution approval -> execution -> outcome audit

What changes is the task content.
What stays stable is the spine of designing, auditing before execution, executing, and auditing the result again.

## 4. Minimum Packet Contract

To operationalize this spine, at minimum use:

| packet | role |
|---|---|
| `design packet` | hands off what to do and what completion means |
| `pre-execution audit packet` | returns whether execution may proceed and what the gate is |
| `execution evidence packet` | bundles execution results and evidence |
| `post-execution verdict packet` | returns close / revision / redesign / escalation |
| `resume packet` | returns next action, next actor, and resume condition when work stops |

## 5. Stop Principle

Stopping is not the default in this spine.

- the default is `move forward`
- stop only when a gate exists
- when stopping, return who resumes, what resumes, and under which condition

Workflow quality is therefore judged by:

- whether it stops correctly
- whether it avoids unnecessary stops
- whether it can resume naturally after a stop

## 6. Separation from Role Names

This framework does not fix role names.

Roles may be mapped locally per project or domain.

| spine role | typical local role |
|---|---|
| `design` | designer / planner / analyst |
| `pre-execution audit` | reviewer / approver / gate owner |
| `execution` | implementer / operator / examiner |
| `post-execution audit` | auditor / verifier / quality owner |

The key is to read by functional responsibility, not by the local role label.

## 7. Project-Local Adaptation Rule

Each project may map this spine onto its own local role model.

Do not confuse:

1. generic spine
2. local role names
3. local status model
4. local packet schema

The generic spine fixes how many stages the work moves through.
Local rules add who does the work, what the roles are called, and which statuses are used.

## 8. Definition of Done

On this spine, work counts as `Done` only when at least:

1. design exists
2. a pre-execution audit verdict exists
3. execution evidence exists
4. a post-execution audit verdict exists
5. reroute or resume exists when close is not possible

If any one is missing, the work may have been executed, but it is not closed.

<a id="agent-workflow-navigation-baseline"></a>
## 9. Agent Workflow Navigation Baseline

To keep agents from hesitating about `when to read what`, maintain this read order alongside the workflow spine:

1. repo or project entrypoint
2. current task surface
3. workflow navigation guide
4. governance or audit rule
5. role guide
6. execution board only when execution detail is needed
7. local runbook, lessons, or archive only when those are needed

For each event, fix:

- who reads
- why they read
- which files are required
- what is optional
- what completion or handoff looks like

This section does not fix project-specific role names, step names, or paths.

<a id="idea-triad-workflow"></a>
## 10. Idea Triad Workflow

Split idea generation into `diverge -> converge -> sharpen`.

| phase | purpose | output |
|---|---|---|
| `diverge` | expand ideas | broad candidate set |
| `converge` | compare and compress candidates | shortlist |
| `sharpen` | make feasibility, value, and risk concrete | go / no-go ready candidate |

Minimum handoff between phases:

- diverge -> converge
  - theme
  - candidate count
  - top candidates
  - short reason notes
- converge -> sharpen
  - shortlisted ideas
  - ranking
  - selection reason
  - key constraints

Principles:

- `diverge` prioritizes volume
- `converge` fixes the comparison axes and narrows
- `sharpen` makes feasibility, value, risk, and decision conditions concrete

<a id="decision-boundary-baseline"></a>
## 11. Data-Driven Decision Boundary

Separate:

- the rule source humans update as current truth
- runtime-derived DB, cache, or generated artifacts
- escalation points that require human judgment

Minimum cycle:

1. a new situation appears
2. check the existing rule
3. if it matches, return the decision
4. if it does not match and matters, escalate to a human
5. write the reviewed decision back into the source rule set
6. reload or regenerate the runtime store

Completion requires at least:

- the source rule set is visibly the current truth
- escalation conditions exist
- writeback is defined
- runtime reload or projection is defined
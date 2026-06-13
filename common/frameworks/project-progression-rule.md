# Project Progression Rule

Purpose: define the highest-level rule that keeps an AI from drifting the subject, losing the current location, advancing on a false basis, or failing to stop and return to the canonical source before resuming.

Treat this document as the core canonical authority of `pj-template`.

## 1. Position

The strength order is:

1. `progression rule`
2. `template-side rule`
3. `project-specific rule`

Lower rules must not contradict higher rules.

## 2. Why This Document Is Needed

Even within a few turns, an AI can drift the subject, the `current` surface, or the basis for calling something progress.
Progress cannot be maintained from memory alone.

So the following must be fixed as external canonical authority and used for re-grounding every time:

- what counts as correct
- what counts as progress
- where work must stop
- where work must return

## 3. Core Principle

The core of this rule is:

`Fix the correct understanding as external canonical authority, re-ground to it every time, and allow only correct progression.`

Progression is defined as repeating:

`canonical source -> judgment -> execution -> verification -> record reflection -> re-grounding`

## 4. Three-Part Structure

### 4.1 Completion Skeleton

This layer defines what closes the project.

- completion definition
- goals required for completion
- completion conditions for each goal or surface
- unresolved items
- work items

### 4.2 Progression Rule

This layer defines how the AI progresses along the completion skeleton.

- which entry it reads from
- where it is now
- what the next action is
- what counts as checkpoint advancement
- what must remain in `current`

### 4.3 Recognition And Correction Discipline

This layer defines how the AI detects drift, stops, returns, corrects, and resumes.

- drift detection
- automatic stop
- re-grounding to the canonical source
- corrected restart

## 5. Start Order

The AI must not start from tasks.

It must proceed in at least this order:

1. confirm what the project is about
2. define what counts as completion
3. enumerate the goals required for that completion
4. make the completion conditions explicit and fixed
5. decide which entry route should be read
6. organize the path
7. place checkpoints
8. enumerate tasks
9. turn tasks into design
10. execute
11. verify
12. reflect the result into the canonical record

## 6. Handling Completion Conditions

Completion conditions are not something the AI may invent without basis.
The AI must take the following, turn implicit conditions into explicit conditions, and fix them in a canonical source:

- user requirements
- existing documents
- the nature of the project
- publication responsibility
- operating responsibility
- real-world constraints

The AI's role is not to decide arbitrarily.
Its role is to derive, define, and fix the conditions from evidence.

## 7. Definition Of Entry

An `entry` is not merely the first file opened.
An entry is the type of canonical source that lets the reader begin correct understanding for the current purpose.

### 7.1 Whole-Project Entry

- what this project is
- what completion means
- what scope is in or out

### 7.2 Current-Work Entry

- where work is now
- what the current surface is
- what the next action is

### 7.3 Design Entry

- which design documents to read
- in what order
- what the `current authoritative source` is

### 7.4 Execution Entry

- what will be run
- how it will be checked
- where the result will be recorded

Do not mix entry types.

## 8. What The AI Must Always Confirm

### 8.1 Success Subject

- what must become true for this work to count as success
- what the subject of the completion report is
- whether a means has been mistaken for the subject

### 8.2 Reading Route

- which files must be read to understand the target as a whole
- what becomes clear in that order
- what is still unresolved

### 8.3 Conditions For Proceeding

- what must be in place before work may proceed
- what missing condition requires a stop
- whether that condition is truly a stop condition rather than only a viewpoint

### 8.4 Current Location

- which goal branch the work is under
- which checkpoint it is before or after
- which task is active now

### 8.5 Next Action

- whether that action directly advances the higher-level subject
- whether it advances a checkpoint
- whether it avoids ending as local cleanup only

## 9. Progression Loop

Every turn, the AI must proceed in at least this order:

1. `re-ground`
   - re-read from canonical authority:
     - success subject
     - `current`
     - unresolved items
     - next checkpoint
2. `choose the next action`
   - judge whether the next action directly advances the higher-level subject
3. `pre-start check`
   - confirm:
     - prerequisites
     - blockers
     - the entry that should be read
     - whether means have become the goal
4. `bounded execution`
   - move only the current work bundle
   - do not widen sideways
5. `verification`
   - confirm whether the checkpoint truly advanced
   - do not count local progress alone as advancement
6. `writeback`
   - write back to canonical authority:
     - `current`
     - evidence
     - next action
     - stop reason
7. `next-action judgment / close / stop`
   - choose one:
     - continue
     - close
     - stop as blocked

### 9.1 Supervisory Output Contract

Every turn's result must be representable outside the conversation with at least:

- `success subject`
- `current location`
- `this turn's single action`
- `completion condition`
- `strong evidence`
- `stop reason`
- `next action`
- `writeback destination`

Explaining it only in conversation does not count as having recorded it.

### 9.2 Active Bundle Rule

Do not start work unless the active work bundle is clear.

At minimum, the project must be able to tell:

- what bundle is active now
- what it is trying to complete
- what the next action is
- what would make work stop

If residual work continues after close, separate it from the closed bundle instead of mixing them.

### 9.3 Continue Versus Stop

An ordinary stage change is not a stop reason.

Continue as long as:

1. the next action is identifiable
2. the next action still advances the higher-level subject
3. no new owner judgment is required
4. no new blocker appears around permission, destructive action, or external dependency

Stop only when:

1. owner judgment is required
2. canonical sources conflict and must be resolved first
3. the next action cannot be identified
4. the next action no longer connects to the higher-level subject

## 10. Drift Correction

The AI must not assume it will not drift.
It must assume that if drift appears, it must stop, return, correct, and only then resume.

### 10.0 Forced Check Timing

1. before work starts
2. when choosing the next action
3. immediately after a work bundle finishes
4. when the user points out a recognition mismatch
5. when the conversation turns to whole-project understanding, entry, current, canonical authority, or project-specific rules

### 10.1 Drift Detection

- does the current work directly advance the success subject
- is the current reading surface correct
- is local progress being counted as advancement before the higher-level question is answered
- is work trying to continue while unresolved items remain only enumerated

### 10.2 Automatic Stop

- do not continue
- do not count it as progress
- do not widen into another workstream

### 10.3 Re-Ground To Canonical Authority

- success subject
- reading route
- `current`
- unmet conditions
- next action

### 10.4 Corrected Resume

- corrected success subject
- corrected `current`
- corrected next action
- corrected stop condition

## 11. Discipline When Unfinished Work Is Found

When unfinished work is found, the AI must not stop at enumeration alone.
It must at least:

1. choose the highest-priority unfinished item
2. treat it as something that should be closed here and now
3. advance it to the level of definition or judgment

It must not hand responsibility back in the form of `this could be done later if needed`.

## 12. Definition Of Advancement

The following do not count as advancement:

- only adding files
- only aligning section shape
- only cleaning a register
- only polishing appearance
- local improvements while the higher-level question still cannot be answered
- advancing only an entry README or support organization without increasing the main yes/no judgment surface
- adding a project-specific rule for a difference that the template could have absorbed

The following do count as advancement:

- a higher-level question can now be answered with yes or no
- it is now possible to judge whether an unmet item is a stop condition or a continue condition
- the reading route has become unambiguous
- a checkpoint has been passed
- one deficiency directly attached to the subject has been closed

## 13. What Must Be Visible To Human Supervision

- the success subject for this work
- the current location
- the one action being advanced now
- its completion condition
- strong evidence
- stop reason
- next action
- writeback destination

## 14. Relationship With Other `pj-template` Rules

- five-layer concretization:
  - `goal-path-checkpoint-task-design-framework.md`
- pre-start check and stop-condition concretization:
  - `execution-readiness-gate-policy.md`
- task state and `current` canonical operation concretization:
  - `task-realtime-operation-policy.md`
- whole-workflow concretization:
  - `business-workflow-spine.md`

## 14.5 Template-Side Default Branches

Before turning project differences into project-specific rules, absorb them on the template side where possible.

Typical branch values include:

- current-work ownership
- resume support
- publication mode
- structure weight
- runtime placement

What still remains project-specific:

- that project's completion definition
- that project's current canonical surface
- that project's runtime, DB, and caller facts
- owner-only decisions
- that project's paths, shelf names, commands, and external dependencies

## 15. How To Use This When Adopting The Template

1. read this document
2. create the completion definition
3. fill the template-side branch conditions
4. map goal, path, checkpoint, task, and design into the project
5. decide the `current` canonical surface and record destinations
6. return to this loop every turn during progression

## 16. Minimum Rules

- do not start from tasks
- do not fix goals before the completion definition
- do not create the path before the goals
- do not proceed without completion conditions
- do not mix entry types
- do not stop at enumerating unfinished work
- do not count local progress as advancement
- do not keep `current` only in memory
- do not continue after detecting drift without stopping

## 17. Read Next

1. [project-progression-rule-integration-audit.md](project-progression-rule-integration-audit.md)
2. [goal-path-checkpoint-task-design-framework.md](goal-path-checkpoint-task-design-framework.md)
3. [business-workflow-spine.md](business-workflow-spine.md)
4. [execution-readiness-gate-policy.md](../policies/execution-readiness-gate-policy.md)
5. [task-realtime-operation-policy.md](../policies/task-realtime-operation-policy.md)

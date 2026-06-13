# Goal, Path, Checkpoint, Task, And Design

Purpose: one shared document that tells the reader what must be decided, and in what order, before work begins.

## 1. How To Use This

Read in this order:

1. `goal`
2. `path`
3. `checkpoint`
4. `task`
5. `design`

Do not start from `design`.

## 2. Meaning Of The Five Parts

### 2.1 Goal

Define the goal of the work that is about to be done.

At minimum, be able to say:

- what the completed state is
- what is in scope this time
- what is out of scope this time
- what remaining item would still mean not achieved
- what this work does finish
- what this work does not finish
- what the subject of the completion report is

### 2.2 Path

Make the route to the goal explicit.

At minimum, be able to say:

- in what order work proceeds from the current state
- where it stops
- which stage depends on which prior stage

### 2.3 Checkpoint

Make clear which checkpoints must be passed on the path to the goal.

At minimum, be able to say:

- which checkpoints exist
- in what order they are passed
- what kind of drift each checkpoint prevents
- what must be true before passing it
- what becomes true after passing it

### 2.4 Task

Break each checkpoint down into units of work required to pass it.

At minimum, be able to say:

- which tasks belong to which checkpoints
- whether each task is truly necessary
- whether anything is missing
- whether the order is correct

### 2.5 Design

Before executing each task, decide what will be read, what will be written, and what completion means.

At minimum, be able to say:

- start conditions
- what to read
- what to write
- what must not be touched
- what to do
- completion conditions
- failure conditions
- stop conditions
- evidence
- record destination
- final judge

For the full mandatory field list, read:

- `../policies/execution-readiness-gate-policy.md`

## 3. Connectivity

The five parts connect in this order:

- `goal` is fixed
- `path` is fixed
- `checkpoint` is fixed
- `task` is fixed
- `design` is fixed

If even one link is broken, the work is incomplete.

## 4. What Must Be Fixed Before Execution

At minimum, decide these first:

- how far this wave will advance
- where completion will be cut for this wave
- what this wave will not do
- whether missing items are named explicitly as blockers

## 5. What The Entry Document Must Say

Any document family using this model must let the entry document state:

- which file is the `goal`
- which file is the `path`
- which file is the `checkpoint`
- which file is the `task`
- which file is the `design`
- that they must be read in that order

## 6. Read Next

- pre-start verification:
  - [../policies/execution-readiness-gate-policy.md](../policies/execution-readiness-gate-policy.md)

<a id="requirements-to-design-workflow"></a>
## 7. Flow From Requirements To Design

When turning a request into implementation-ready work, proceed in at least this order:

```text
request
  -> requirements
  -> basic design
  -> detailed design
  -> task breakdown
  -> traceability matrix
  -> quality gate
  -> implementation cycle
```

Minimum checks at each stage:

- requirements
  - purpose, scope, functional items, non-functional items, assumptions, and risks are explicit
- basic design
  - boundary, major components, data, interfaces, and rejected choices are explicit
- detailed design
  - contracts, validation, errors, state, and test conditions are concrete
- task breakdown
  - one clear outcome
  - target files
  - dependency
  - acceptance criteria
  - verification method
- traceability
  - requirements, design, tasks, and evidence connect to one another

<a id="task-splitting-methodology"></a>
## 8. Task Splitting Method

Do not physically split design documents into as many pieces as there are tasks.
Keep design as one coherent body and give tasks precise references back into it.

Principles:

- use vertical slices whenever possible
- use horizontal slices only for shared foundations, migrations, infrastructure work, or explicit refactors
- when size is still unreadable, create a short spike first

Review triggers:

| signal | suggested limit | when exceeded |
|---|---:|---|
| referenced design docs | 3 | split or clarify scope |
| implementation files | 5 | split by capability or component |
| estimated single-file size | 200 lines | split by component or helper |
| dependencies | 3 blockers | revisit sequencing |

Each task should contain at least:

- referenced design sections
- dependencies and blockers
- target files or components
- acceptance criteria
- test or evidence mapping
- explicit out-of-scope items
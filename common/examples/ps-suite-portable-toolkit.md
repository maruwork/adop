# PS Suite Portable Toolkit Example

Minimal example of how to split a portable PS Suite pack for use in another project or external AI environment.

This document is not the canonical source for the current runtime or current task.  
It is a reusable example that shows how to divide a portable prompt or toolkit pack.

## 1. Recommended Split

Split the portable toolkit into at least these three packs:

| Pack | Purpose | Typical use |
|---|---|---|
| `standard` | everyday questions, comparisons, evaluations | general consultation, review, comparison |
| `dev-flow` | development support from requirements through quality gates | design, implementation, testing, acceptance setup |
| `business-view supplement` | business value, ROI, decision support | add a business lens to technical answers |

## 2. Why Split It

- a single giant prompt is heavy to reuse
- each use case can select only the pack it needs
- business support can be added only when needed
- adopting projects can add role, workflow, and governance locally without mixing them into the portable pack

## 3. Minimum Contract

Each pack should define at least:

| Field | Meaning |
|---|---|
| `purpose` | when to use it |
| `input expectation` | what kind of request or context it expects |
| `output expectation` | what it should return |
| `non-goal` | what it should not do |
| `combination rule` | how to combine it with other packs, if needed |

## 4. Adoption Rule

- `standard` should be usable on its own
- `dev-flow` should include the sequence from design to implementation to quality gates
- `business-view supplement` should not be used alone; add it to `standard` or `dev-flow`
- do not embed project-specific workflow or path information directly into pack bodies

## 5. Completion Rule

A portable toolkit pack is ready only when:

- the three pack roles are clearly separated
- standalone and combination rules are explicit
- no project-specific current truth is embedded
- an adopting project can attach its own workflow afterward
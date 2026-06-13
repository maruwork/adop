# Design Spec Completion Checklist

**When to use**: Use this during review to quickly check whether a design spec reaches completion-level quality.  
**Related**: `../policies/spec-review-and-skill-policy.md`  
**Replace**: owner name, completion wording, related policy name.  
**Do not write**: the design spec itself, current-state management, or project-specific current operations.

This checklist concretizes the design-spec completion side of `../frameworks/project-progression-rule.md`, especially:

- `definition of completion`
- `explicit completion conditions`
- `required design granularity after entry judgment`

## 1. Problem / Scope

- [ ] The purpose, problem, and intended use are clear from the document itself.
- [ ] In-scope boundaries are written.
- [ ] Out-of-scope boundaries are written.
- [ ] The handling of excluded areas is not ambiguous.

## 2. Runtime / Trigger / IO

- [ ] The usage situation is written.
- [ ] The trigger or start timing is written.
- [ ] Inputs are written.
- [ ] Outputs are written.
- [ ] The output destination is written.

## 3. Branching / Owners

- [ ] Branches for detection, judgment, notification, recording, correction, auto-correction, and human intervention exist.
- [ ] Automated execution and human judgment are separated.
- [ ] The trigger owner is written.
- [ ] The execution owner is written.
- [ ] The decision owner is written.
- [ ] The storage owner is written.

## 4. Truth / Boundary

- [ ] Current truth and history are separated.
- [ ] Artifact, evidence, and cache handling are separated.
- [ ] The boundary against existing mechanisms is written.
- [ ] Non-conflict conditions against existing truth, owners, and workflows are written.
- [ ] It is clear which surface has authority and which does not.

## 5. Contract / Phase

- [ ] The minimum contract for standalone use is written.
- [ ] The extended contract for embedded use is written.
- [ ] MVP scope is separated.
- [ ] Phased implementation is separated.
- [ ] Future expansion is separated.
- [ ] Final completion is separated.

## 6. Operation / Verification

- [ ] Installation order is written.
- [ ] First-run order is written.
- [ ] Verification order is written.
- [ ] Daily-operation reading order is written.
- [ ] Test viewpoints exist.
- [ ] Regression-check viewpoints exist.
- [ ] Non-pollution-check viewpoints exist.
- [ ] Failure behavior is written.
- [ ] Retry conditions exist.
- [ ] Hold conditions exist.
- [ ] Stop conditions exist.

## 7. Completion Judgment

- [ ] Completion conditions are written.
- [ ] Non-completion conditions are written.
- [ ] Superficial resolution and root resolution are distinguished.
- [ ] Adoption reasons are written.
- [ ] Rejected options are written.
- [ ] Rework risk is written.

## 8. Final Verdict

- [ ] This document alone lets a context-lost implementer or AI understand the whole picture, install it, run first use, and judge completion.
- [ ] If it does not meet that bar, do not call it a completion-level design spec.
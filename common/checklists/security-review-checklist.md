# Security Review Checklist

**When to use**: Use this when reviewing security-sensitive changes.  
**Replace**: asset names, boundaries, control names, follow-up task handling.  
**Do not write**: the threat model itself, the current-state canonical source, or project-specific current operations.

Portable checklist for reviewing security-sensitive design changes, runtime paths, database paths, external integrations, and permission changes.

This checklist concretizes the security side of `../frameworks/project-progression-rule.md`, especially:

- `pre-start checks`
- `verification`
- `do not count local movement as forward progress`
- `make stop conditions explicit`

This checklist is not the place for current truth or security progress logs.
Write results back into the project's current surface, review artifact, or follow-up task.

## 0. Scope

- [ ] The target change can be described in one sentence.
- [ ] In scope and out of scope are separated.
- [ ] The work is classified as `foundation work`, `daily operations`, or `non-mainline`.

## 1. Assets

- [ ] Protected data assets are listed.
- [ ] Protected control assets are listed.
- [ ] Audit or evidence assets are listed.

## 2. Boundary

- [ ] The trust boundary is written down.
- [ ] Actors, systems, and external services are separated.
- [ ] Allowed actions and denied actions are separated.

## 3. Attack / Misuse

- [ ] At least one abuse case exists.
- [ ] At least one accidental misuse case exists.
- [ ] We checked whether wrong-target, stale-context, or privilege drift is relevant.

## 4. Controls

- [ ] A preventive control exists.
- [ ] A detective control exists.
- [ ] A corrective or recovery path exists.
- [ ] The document explains fail-soft or fail-close behavior instead of fail-open behavior.

## 5. Evidence

- [ ] A read-only verification path exists.
- [ ] Dry-run or simulation availability is explicit.
- [ ] Security claims are not justified by a single tool output alone.

## 6. Residual Risk

- [ ] Unresolved risk is documented.
- [ ] Human-decision points are separated out.
- [ ] Follow-up tasks are explicit when needed.

## Summary

```text
Decision: block / fix soon / accept with note
Primary risk: ___
Required follow-up: ___
Writeback destination: current / review artifact / follow-up task
```
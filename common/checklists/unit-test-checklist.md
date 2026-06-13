# Unit Test Checklist

**When to use**: Use this when checking whether code is testable, covered, isolated, and maintainable at the unit-test level.  
**Replace**: test framework names, mock policy, summary decision wording.  
**Do not write**: the implementation plan itself, integration-test concerns, or project-specific current-state management.

Use this before refactoring, before PR merge, or before accepting generated code.

This checklist concretizes the unit-test side of `../frameworks/project-progression-rule.md`, especially:

- `pre-start checks`
- `verification`
- `fix completion against evidence`
- `do not count local movement as forward progress`

This checklist itself is not the canonical place for the test plan or the current verdict.
Write results back into the project's verification record, current surface, or follow-up task.

| Severity | Meaning |
|---|---|
| A | structural issue that makes testing impossible or unstable |
| B | quality or maintainability risk |
| C | improvement opportunity |

## 1. Testability

| Severity | Check | Result |
|---|---|---|
| A | A hidden external dependency cannot be mocked at the unit level. | [ ] |
| A | Uncontrolled side effects change the result for the same input. | [ ] |
| A | Global state leaks between tests. | [ ] |
| A | The unit is too coupled to instantiate or call in isolation. | [ ] |
| B | Important logic is hidden behind private methods or oversized functions. | [ ] |
| B | One function or class carries multiple responsibilities. | [ ] |

## 2. Coverage Quality

| Severity | Check | Result |
|---|---|---|
| A | Only the happy path is tested. | [ ] |
| A | Error paths are untested. | [ ] |
| A | Boundary values are untested. | [ ] |
| B | Assertions are too weak to prove behavior. | [ ] |
| B | Regression risk is not covered by focused tests. | [ ] |
| C | Scenario variety is limited. | [ ] |

## 3. Isolation

| Severity | Check | Result |
|---|---|---|
| A | Test results depend on execution order. | [ ] |
| A | A test unintentionally calls a real network or external service. | [ ] |
| A | Randomness, time, locale, or timezone is uncontrolled. | [ ] |
| A | Setup or teardown does not restore state. | [ ] |
| B | Shared fixtures are hard to understand or reset. | [ ] |
| B | Temporary files or test DB rows are not cleaned up. | [ ] |

## 4. Test Correctness

| Severity | Check | Result |
|---|---|---|
| A | Async errors or rejected promises are not captured. | [ ] |
| B | The test depends on implementation detail instead of behavior. | [ ] |
| B | One test contains too many unrelated assertions. | [ ] |
| B | Exceptions are checked only by type and ignore useful detail. | [ ] |
| B | Floating-point comparison ignores tolerance. | [ ] |
| B | The mock is more complex than the behavior under test. | [ ] |

## 5. Maintainability

| Severity | Check | Result |
|---|---|---|
| B | Test names do not explain the condition and expected behavior. | [ ] |
| B | Failing tests do not show the failing behavior clearly. | [ ] |
| B | The reason for chosen test values is unclear. | [ ] |
| C | Test structure is inconsistent across files. | [ ] |
| C | Comments do not explain non-obvious setup. | [ ] |

## 6. Generated Code Checks

| Severity | Check | Result |
|---|---|---|
| A | Existing tests were not run after generated code was added. | [ ] |
| A | Errors can be swallowed in ways tests will not detect. | [ ] |
| B | Generated code duplicates existing behavior instead of reusing it. | [ ] |
| B | Generated code was accepted without focused tests. | [ ] |
| C | Generated naming lowers test readability. | [ ] |

## Summary

```text
A checks: ___
B checks: ___
C checks: ___
Decision: block / fix soon / accept with note
Required follow-up: ___
Writeback destination: verification record / current / follow-up task
```
# Integration Test Checklist

**When to use**: Use this when checking whether module boundaries, state transitions, external dependencies, and operational behavior work as one integrated system.  
**Replace**: target environment names, external dependency names, summary decision wording.  
**Do not write**: unit-test detail, the implementation plan itself, or project-specific current-state management.

Use this before release, before merging cross-module changes, or when adding a new integration point. Unit tests are assumed to have passed already.

This checklist concretizes the integration-side of `../frameworks/project-progression-rule.md`, especially:

- `advance one checkpoint at a time`
- `verification`
- `make stop conditions explicit`
- `writeback`

This checklist is not the current canonical source for the integration flow itself.
Write results back into the project's verification record, runbook, or follow-up task.

| Severity | Meaning |
|---|---|
| A | risk of data loss, security failure, outage, or invalid state |
| B | reliability or maintainability risk |
| C | improvement opportunity |

## 1. Interface and Data Transfer

| Severity | Check | Result |
|---|---|---|
| A | Data shape, type, and required fields match across module boundaries. | [ ] |
| A | Null, empty, and malformed values are handled safely across boundaries. | [ ] |
| A | Error object format matches caller expectations. | [ ] |
| B | Request and response contracts match the documented interface. | [ ] |
| B | Encoding, timezone, and date format are consistent. | [ ] |

## 2. State Propagation

| Severity | Check | Result |
|---|---|---|
| A | Cross-module transactions roll back or compensate correctly. | [ ] |
| A | Async operations do not race ahead of the required completion point. | [ ] |
| B | State from one step is handed to the next step correctly. | [ ] |
| B | Event or queue ordering assumptions are verified. | [ ] |

## 3. External Boundaries

| Severity | Check | Result |
|---|---|---|
| A | External outage or timeout has a safe fallback or a clear failure path. | [ ] |
| A | Retry behavior has limits and does not duplicate writes. | [ ] |
| B | DB, API, file, and queue connectivity works in the target environment. | [ ] |
| B | Timeout settings are exercised in practice. | [ ] |
| B | Slow external responses are handled correctly. | [ ] |

## 4. Authorization and Security

| Severity | Check | Result |
|---|---|---|
| A | Authentication tokens or credentials propagate safely. | [ ] |
| A | Authorization checks still hold across layers. | [ ] |
| A | Expired or revoked sessions are handled correctly. | [ ] |
| B | Logs and errors do not expose secrets or personal data. | [ ] |

## 5. Data Integrity

| Severity | Check | Result |
|---|---|---|
| A | Concurrent updates do not corrupt shared data. | [ ] |
| A | Delete or update effects propagate to dependent modules. | [ ] |
| B | Cache and persistent storage do not drift silently. | [ ] |
| B | Derived records can be regenerated or reconciled. | [ ] |

## 6. Error Propagation

| Severity | Check | Result |
|---|---|---|
| A | Downstream errors reach the caller or alerting path. | [ ] |
| A | Broad catch blocks do not swallow errors. | [ ] |
| B | Useful context survives across error boundaries. | [ ] |

## 7. Idempotency and Retry

| Severity | Check | Result |
|---|---|---|
| A | Re-running the same request does not change the intended result. | [ ] |
| A | Retry does not create duplicate side effects. | [ ] |
| A | Duplicate input is detected or handled safely. | [ ] |

## 8. Configuration and Environment

| Severity | Check | Result |
|---|---|---|
| A | Production, staging, and test configuration are separated. | [ ] |
| B | Required environment variables are validated early. | [ ] |
| B | Configuration changes propagate to every related module. | [ ] |
| B | Startup and shutdown order has been verified. | [ ] |

## 9. Performance and Observability

| Severity | Check | Result |
|---|---|---|
| A | Concurrent usage does not cause deadlock or resource exhaustion. | [ ] |
| B | Cross-module calls avoid obvious N+1 or polling explosions. | [ ] |
| B | Response time stays within the expected range. | [ ] |
| B | Logs contain enough context for failure diagnosis. | [ ] |
| C | Start, end, and duration are traceable. | [ ] |

## Summary

```text
A checks: ___
B checks: ___
C checks: ___
Decision: block / fix soon / accept with note
Required follow-up: ___
Writeback destination: verification record / runbook / follow-up task
```
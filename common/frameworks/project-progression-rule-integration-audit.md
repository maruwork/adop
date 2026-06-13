# Project Progression Rule Integration Audit

This table centers `project-progression-rule.md` and summarizes what role each framework, policy, and checklist plays.
Its purpose is to let a reader explain the existing placement before adding any new rule.

## 0. Read First

1. [project-progression-rule.md](./project-progression-rule.md)
2. [project-progression-rule-integration-audit.md](./project-progression-rule-integration-audit.md)
3. [goal-path-checkpoint-task-design-framework.md](./goal-path-checkpoint-task-design-framework.md)
4. [../policies/execution-readiness-gate-policy.md](../policies/execution-readiness-gate-policy.md)

## 1. Verdict Classes

- `KEEP`
  - the role is clear and the file stays live
- `INTEGRATED`
  - the role has been absorbed into another live rule
- `LATER`
  - keep it for now as reference or support

## 2. Framework Roles

| file | primary role | verdict | notes |
|---|---|---|---|
| `project-progression-rule.md` | top progression rule | `KEEP` | canonical authority for progression, stopping, and re-grounding |
| `goal-path-checkpoint-task-design-framework.md` | five-layer breakdown | `KEEP` | skeleton for task design |
| `business-workflow-spine.md` | progression spine | `KEEP` | flow from design through execution |
| `ps-suite-guide.md` | support toolkit guide | `LATER` | support only, not core |
| `framework-selection-guide.md` | framework selection support | `INTEGRATED` | kept as a support guide |
| `prompt-quality-improvement-cycle.md` | prompt-improvement support | `INTEGRATED` | support treatment |
| `decision-to-implementation-consistency-review.md` | consistency review | `INTEGRATED` | support review angle |

## 3. Policy Roles

| file | primary role | verdict | notes |
|---|---|---|---|
| `execution-readiness-gate-policy.md` | pre-start check | `KEEP` | concretizes the conditions for proceeding |
| `agent-workflow-policy.md` | day-to-day operating flow | `KEEP` | next action, continuation, delegation |
| `task-realtime-operation-policy.md` | `current` and task-state operation | `KEEP` | current-canonical operation |
| `entry-guide-reference-separation-policy.md` | entry / guide / reference split | `KEEP` | prevents route mixing |
| `verification-and-retry-policy.md` | verify / retry | `KEEP` | how to proceed after failure |
| `file-operation-policy.md` | file and shelf operations | `KEEP` | placement, move, archive |
| `naming-and-shelf-policy.md` | naming and shelf responsibility | `KEEP` | naming and shelf semantics |
| `project-template-installation-gate-policy.md` | template-installation gate | `KEEP` | stop conditions before installation |
| `project-template-adoption-completion-policy.md` | adoption completion | `KEEP` | completion condition for adoption |

## 4. Checklist Roles

- `implementation-audit-checklist.md`
  - post-implementation audit
- `design-spec-completion-checklist.md`
  - design-spec completion check
- `ai-agent-runtime-bootstrap-checklist.md`
  - AI runtime bootstrap
- `unit-test-checklist.md`
  - unit-test viewpoints
- `integration-test-checklist.md`
  - integration-test viewpoints
- `security-review-checklist.md`
  - security-review viewpoints

## 5. Conclusion

- replacement targets are limited; most files are either `KEEP` or `INTEGRATED`
- absorb project differences into template-side branch decisions before adding a new type
- move time-dependent deliberation records down into `../../reference/`
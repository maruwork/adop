# Project Publication Responsibility Policy

## 1. Purpose

This policy defines who prepares, who reviews, who executes public release, and who maintains the repository after release when a project is published on GitHub.

The goal is to prevent the project-side owner and the shared-governance side from assuming different responsibility splits.

## 2. Core Rule

Do not leave GitHub publication responsibility implicit.

Before a repository is made public, the project must explicitly define:

1. who prepares the repository-local surface
2. who reviews shared-surface quality
3. who executes the public release step
4. who owns repository-local maintenance after release
5. who owns shared-surface maintenance after release

If any one of these is unclear, public release is not ready.

## 3. Recommended Default Split

### Project-side owner

Owns:

- repository-local structure and placement
- project-specific README and docs
- repository-local evidence gathering
- repository-local fixes after release

### Shared-governance side

Owns:

- shared tool-application review
- shared publication-gate review
- cross-project release consistency
- shared-surface maintenance after release

## 4. Recommended Default Publication Route

Use this default unless the project explicitly chooses another route.

- preparation: `project-side owner`
- review: `shared-governance side`
- public release execution: `shared-governance side`

Reason:

- public release is the highest-risk irreversible step
- the project-side owner has stronger repository-local context
- the shared-governance side has stronger cross-project publication discipline

## 5. Allowed Alternative Route

The project may explicitly choose:

- preparation: `project-side owner`
- review: `shared-governance side`
- public release execution: `project-side owner`

Allow this only if:

1. review approval is already explicit
2. the project records the execution owner before release
3. post-release repository-local maintenance ownership remains explicit

## 6. What Must Not Happen

Do not allow any of the following:

1. the project-side owner publishes without shared review when shared tools affect the release surface
2. the shared-governance side rewrites repository-local structure without project shelf rules
3. both sides assume the other side owns post-release maintenance
4. public release execution is decided ad hoc in chat only

## 7. Minimum Decision Record

Before public release, record:

- preparation owner
- review owner
- public release execution owner
- repository-local post-release owner
- shared-surface post-release owner

This record may live in the project-local adoption packet, the public-release packet, or another explicit governance document for the project.

## 8. Fail-Close Rule

If a project can be prepared for release but the responsibility split is still unclear, stop before public release and return the missing decision points.
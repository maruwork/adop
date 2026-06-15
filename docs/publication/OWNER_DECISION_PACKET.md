# ADOP Owner Decision Packet

Status: Active

## Purpose

Collect the minimum owner decisions required to move from publishable hold to actual publication, in one execution-grade authority surface.

## Blocking Decisions

Each decision must be filled before actual publication.

## Owner Answer Format

Every blocking decision must be recorded with the following fields:

- `state`: `open` / `chosen`
- `owner answer`: the chosen value
- `owner rationale`: why that value was chosen
- `downstream action target`: which publication step/doc must change because of the answer
- `blocking`: whether publication must stop until this answer exists

### 1. License

- state: chosen
- blocking: yes
- owner answer:
  - chosen license: `MIT`
- owner rationale:
  - why this license matches ADOP reuse posture: permissive reuse is appropriate for a generic adoption-management tool and lowers friction for first public evaluation
- downstream action target:
  - `LICENSE` file in the standalone repo
  - contribution/publication wording that depends on the chosen license
- owner must decide:
  - chosen license
  - confirmation that ADOP reuse posture matches that license
- downstream effect:
  - license file added during export/go-live
  - contribution expectations must remain compatible with the chosen license

### 2. Repository Host

- state: chosen
- blocking: yes
- owner answer:
  - GitHub owner/org: `fumimaruwork`
  - repository name: `adop`
  - initial visibility: `private`
- owner rationale:
  - why this host/owner/visibility combination is appropriate: private-first creation preserves a final verification window before public release while keeping the target public owner fixed
- downstream action target:
  - standalone repository creation target
  - publication runbook host/visibility steps
- owner must decide:
  - GitHub owner/org
  - repository name
  - initial visibility
- downstream effect:
  - standalone repository creation target is fixed
  - go-live sequence can name the real host

### 3. Public Contribution Policy

- state: chosen
- blocking: yes
- owner answer:
  - issue policy: issues may be opened from day one for bugs, docs, and bounded enhancement requests
  - pull request policy: pull requests are accepted from day one and require maintainer review before merge
  - accept public contributions from day one: `yes`
- owner rationale:
  - why this contribution posture fits the first public release: open issue intake supports evaluation while maintainer-reviewed PRs keep early-surface changes bounded
- downstream action target:
  - `docs/publication/CONTRIBUTING_DRAFT.md`
  - public-facing repo guidance
- source notes:
  - `docs/publication/CONTRIBUTING_DRAFT.md`
  - `PUBLIC_POLICY_PROMOTION_MATRIX.md`
- owner must decide:
  - issue policy
  - pull request policy
  - whether public community contributions are accepted from day one
- downstream effect:
  - `docs/publication/CONTRIBUTING_DRAFT.md` can be promoted or intentionally held

### 4. Public Security Intake Policy

- state: chosen
- blocking: yes
- owner answer:
  - security-report intake posture: use GitHub private vulnerability reporting if enabled
  - private disclosure from day one: `yes`
  - promised response posture: best effort, no fixed SLA at first publication
- owner rationale:
  - why this security posture is supportable at first publication: it provides a standard intake path without committing to an unsupported response guarantee
- downstream action target:
  - `docs/publication/SECURITY_DRAFT.md`
  - public security policy wording
- source notes:
  - `docs/publication/SECURITY_DRAFT.md`
  - `PUBLIC_POLICY_PROMOTION_MATRIX.md`
- owner must decide:
  - security-report intake posture
  - whether private disclosure is supported from day one
  - any promised response posture
- downstream effect:
  - `docs/publication/SECURITY_DRAFT.md` can be promoted or intentionally held

### 5. Public Verification / CI Scope

- state: chosen
- blocking: yes
- owner answer:
  - minimum public verification surface: `python shared/python/adop_cli.py --version`, `python -m py_compile shared/python/*.py` (in the exported standalone repo: `python/`), and the full bounded quick flow from `PUBLIC_VERIFICATION_CONTRACT.md`
  - CI required at repo creation or allowed immediately after: required at repo creation
- owner rationale:
  - why this verification posture is sufficient for first publication: it validates CLI entry, schema/runtime integrity, and the end-to-end bounded artifact lifecycle before public exposure
- downstream action target:
  - `PUBLIC_VERIFICATION_CONTRACT.md`
  - `PUBLICATION_RUNBOOK.md`
  - public CI wiring step
- source notes:
  - `PUBLIC_VERIFICATION_CONTRACT.md`
  - `RELEASE_BOOTSTRAP_NOTES.md`
  - `REPO_EXPORT_CHECKLIST.md`
- owner must decide:
  - minimum public verification surface
  - whether CI is required at repo creation or may follow immediately after
- downstream effect:
  - go-live sequence can declare what must pass before publication

## Settled Inside The Shelf

- public-facing commands can be repo-relative
- public-facing paths can be repo-relative
- bounded verification works locally
- generic/common vs project-local overlay boundary is explicit
- pre-public docs and publishable-hold docs already exist

## Decision Closure Rule

Publication execution is ready only when every blocking decision above has:

- a chosen value
- an owner-confirmed rationale
- a downstream action target in the runbook
- `state: chosen`

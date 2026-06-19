# ADOP Completion Contract

Status: Active

## Purpose

Define the evidence required before saying common `ADOP` is complete enough to close a major implementation pass.

This contract is broader than `docs/publication/PUBLIC_VERIFICATION_CONTRACT.md`.
The publication contract is the minimum public release check.
This completion contract is the broader "do not call it done yet" gate.

## Scope Boundary

This contract covers common `ADOP` authority:

- CLI behavior
- artifact schema and lifecycle rules
- canonical HTML rendering and operator guidance
- project-local overlay scaffold contract
- black-box consumer proof
- GitHub CI proof

This contract does not replace project-local authority:

- a consumer project's live overlay contents
- a consumer project's current adoption records
- owner-specific release, legal, or hosting decisions

Repo hygiene is required before this monorepo closes a completion pass, but it is a local closure condition, not exported common ADOP authority.

## Stop Rule

Do not say `ADOP` is complete if any gate below is missing evidence.
Do not treat a happy-path smoke run as sufficient if fallback or installed-command paths remain unproven.
Do not mix project-local overlay policy into generic ADOP contract text.

## Completion Gates

### 1. CLI Contract

Pass only if all of the following are true:

- `python shared/python/adop_cli.py --version` works from the source tree.
- installed-command invocation works as `adop ...` in a clean consumer project outside the source tree.
- `init`, `render-html`, `lint`, `scan`, `scan --record`, `quick-close-trial --verdict promote`, `quick-close-trial --verdict hold`, `block`, and `unblock` all execute under their documented contract.
- advisory and writing behavior stay distinct: `scan` alone does not write a canonical artifact, while `scan --record` does.
- failure behavior is bounded and explicit: invalid roots, invalid promote inputs, and missing required arguments fail with contract-aligned errors.

### 2. Schema And Lifecycle Contract

Pass only if all of the following are true:

- CLI behavior, lifecycle rules, and validation rules agree on the same artifact schema.
- `unknown` may appear only as an explicit bounded intake placeholder and cannot survive into promote.
- hold and reopen preserve provenance correctly, returning the lane to the compare/trial path instead of inventing a new contract.
- block and unblock preserve provenance correctly, returning the lane to the documented pre-trial path.
- coupling records written by `scan --record` conform to the canonical coupling-note schema.

### 3. HTML And Operator Contract

Pass only if all of the following are true:

- one canonical renderer/template is used; completion is not based on adding report-specific HTML forks.
- the empty state tells a first-time operator how to begin, including `adop init`.
- reader-facing explanation and operator-facing action guidance are both present and do not compete with each other.
- rendered output exposes the source artifact root so operators can tell what data they are looking at.
- sample or preview content is clearly subordinate to real artifact data and cannot be mistaken for production evidence.
- next-command guidance in HTML matches the CLI contract for hold, reopen, block, unblock, and promotion paths.

### 4. Overlay Contract

Pass only if all of the following are true:

- `adop init` creates a project-local overlay that matches the minimum structure defined in `docs/design/ADOP_SHELF_CLASSIFICATION.md`.
- the initialized overlay references common ADOP authority instead of copying schema, lifecycle, or CLI definitions into project-local text.
- the `init` fallback path still produces an overlay with the same required sections when the template file cannot be located.
- common ADOP docs do not store live project-specific trial boards as if they were generic authority.

### 5. Black-Box Consumer Proof

Pass only if all of the following are true:

- a clean consumer project can run `install -> init -> intake -> compare -> trial -> hold/reopen -> promote -> render-html -> lint` using the installed `adop` command.
- the same consumer proof also exercises `block -> unblock` without relying on monorepo-only paths or hidden local setup.
- the proof is newcomer-usable: no manual editing of generated HTML, no source-tree-relative imports, and no undocumented bootstrap steps.
- the proof covers both Linux and Windows.

When one scene cannot simultaneously prove every branch, use multiple scenes in the same clean consumer project so that hold/reopen, block/unblock, and final promotion are all evidenced in one black-box run.

### 6. GitHub CI Proof

Pass only if all of the following are true:

- the repository contains workflow coverage for source-tree validation and installed-command consumer black-box checks.
- the latest relevant GitHub Actions runs are green on GitHub-hosted runners; a local-only pass is not enough after workflow changes.
- CI proves the installed-command path on both Linux and Windows.
- CI proves the HTML/operator surface, coupling recording, hold/reopen guidance, block/unblock guidance, and final lint surface rather than only unit tests.

## Local Repo Closure Gate For This Monorepo

The following conditions are required before this monorepo itself can claim closure on a completion pass, but they are not part of exported common ADOP authority:

- `workspace/` top level contains only intentional human-meaningful shelves.
- disposable verification residue lives under `workspace/tmp/`.
- local pytest guidance keeps `--basetemp` under `workspace/tmp/...`.
- quarantined stale residue is fully purged before final closure if it is the only known cleanliness gap.

## Required Evidence Bundle Before A Completion Claim

Before saying "complete", collect and review all of the following:

- the exact commands or tests that proved the CLI and schema gates
- the exact black-box run that proved installed-command newcomer usability
- the exact GitHub Actions run links or identifiers that proved hosted CI success
- the exact HTML checks that proved operator guidance and sample/data separation
- the exact local repo-cleanliness check for this monorepo, if local hygiene is still part of the remaining closure work

If any item is still phrased as expectation instead of evidence, the completion claim is still open.

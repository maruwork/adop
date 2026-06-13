# ADOP Private Host Bootstrap Runbook

Status: Active

## Purpose

Define the exact execution order for preparing `fumimaruwork/adop` as a private repository without crossing into any public-release action.

## Private Boundary

Allowed in this runbook:

- create `fumimaruwork/adop` as a private repository
- place the carried files listed in `REPO_EXPORT_GUIDE.md`
- add the chosen `LICENSE`
- promote the chosen wording from draft documents into the private repository copy
- run the documented verification sequence
- wire the chosen CI scope in the private repository

Forbidden in this runbook:

- change repository visibility to public
- announce or share the repository as public
- run public go-live actions

## Carry Set For Private Repository

Carry all files listed in `REPO_EXPORT_GUIDE.md` § "Carry Into The Standalone Repository", plus `LICENSE`.

Do not carry by default:

- `archive/` — completed wave materials
- `docs/design/` — internal design notes (except `ADOP_SHELF_CLASSIFICATION.md`, carried per export guide)
- `docs/governance/` — monorepo governance docs
- `common/` — monorepo-local rule shelf
- `workspace/` — scratch
- internal decision notes not needed in the private repository copy

## Private Repository Setup Order

1. Create `fumimaruwork/adop` with `private` visibility.
2. Prepare the repository root with the carried files and directories.
3. Add `LICENSE` using the chosen MIT text.
4. Promote `docs/publication/CONTRIBUTING_DRAFT.md` and `docs/publication/SECURITY_DRAFT.md` into the private repository copy after replacing draft-only wording as intended.
5. Keep internal-only files out unless they are intentionally needed for the private repository.
6. Configure the chosen CI scope in the private repository.

## Private Verification Order

Run the same verification sequence described in `PUBLIC_VERIFICATION_CONTRACT.md` after the private repository candidate is assembled.

## Hold Rule

Stop after private verification and private CI wiring. Do not continue into public release from this runbook.

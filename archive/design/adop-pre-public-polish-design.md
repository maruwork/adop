# ADOP Pre-Public Polish Design

Status: Complete

## ADPPP-T1

- Start Conditions: `ADOP` private bootstrap is already closed.
- Read: `README.md`, `REPO_EXPORT_GUIDE.md`
- Write: `.github/`, `SUPPORT.md`
- Do: add issue templates, pull request template, `CODEOWNERS`, and support guidance.
- Acceptance: a third party can see where to report bugs, ask questions, and open reviewable pull requests.

## ADPPP-T2

- Start Conditions: `ADPPP-T1` is complete.
- Read: `common/refernce/prepare_private_repo_candidates.sh`
- Write: `README.md`, `REPO_EXPORT_GUIDE.md`, candidate-generation script
- Do: make export and candidate flow carry the new repository-facing files.
- Acceptance: candidate regeneration does not require ad hoc copy steps.

## ADPPP-T3

- Start Conditions: `ADPPP-T2` is complete.
- Read: candidate-generation script, private candidate directory
- Write: `common/refernce/adop-private-repo-candidate-20260605`
- Do: regenerate candidate and run CLI/compile verification.
- Acceptance: candidate contains the new files and existing verification still passes.

## ADPPP-T4

- Start Conditions: `ADPPP-T3` is complete.
- Read: candidate directory, GitHub repository state
- Write: `fumimaruwork/adop` private repository contents and metadata
- Do: commit/push the polished candidate and set description/topics while keeping the repository private.
- Acceptance: repository metadata and files match the prepared candidate.

## ADPPP-T5

- Start Conditions: `ADPPP-T4` is complete.
- Read: common shelf and summary notes
- Write: summary note in `common/refernce`
- Do: remove generated cache directories, record the latest result, and stop before public release.
- Acceptance: no generated cache directories remain in `epo root`, and the summary explains what changed.

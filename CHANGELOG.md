# Changelog

All notable changes to this project are documented in this file.

## Unreleased

### Added

- `adop reject`: reject a candidate from `proposed` / `blocked` / `hold` without running a trial (terminal for the scene)
- `adop aggregate`: read-only cross-project portfolio (scene / tool / state) across multiple `--root` artifact roots
- `adop render-html`: render the canonical HTML governance dashboard from an artifact root
- Schema-version tolerance: `MIN_READABLE_SCHEMA_VERSION` keeps older artifacts valid after an upgrade; a too-new `schema_version` reports "written by a newer adop; upgrade adop" instead of a generic invalid
- HTML dashboard: a "Back to top" button
- HTML dashboard: the decision detail now shows the `decision_owner` for lanes that record one (was only in the raw JSON)
- `examples/`: a minimal, self-contained worked example (`examples/walkthrough/.adop/`)
- Secret-commit guard: `.gitignore` patterns plus pre-commit `detect-private-key`, `check-added-large-files`, and a local `forbid-secret-files` hook
- Coverage gate: `pytest-cov` dev dependency and a `fail_under` threshold (~84% measured)

### Fixed

- Distribution: `adop.json` now lists `adop_html.py` and the HTML template, so a manifest-synced runtime can start and render (previously crashed with `ModuleNotFoundError`)
- Dashboard now surfaces the trial-packet allow/deny envelope, block reason, intake "why now", watch interest, reject reason, and deprecated/migrating/archived/hold reasoning (were blank or showed the stale promote judgment)
- Dashboard "Latest update" column now shows the genuinely most-recent artifact and its date (previously picked an earlier-stage note by id number — e.g. the intake over a later trial packet — and showed only a cryptic artifact id)
- Write-trial guard: `task-scoped` and `phase-scoped` trials now also require an isolated write sandbox
- Windows: artifact-write lock maps `PermissionError` like `FileExistsError` so concurrent id minting retries instead of crashing; stale locks are reclaimed
- Performance: `summary` / state resolution read judgments from a single in-memory load instead of re-reading the artifact root per trial
- `adop init`: creates a nested `--overlay` parent directory instead of crashing with `FileNotFoundError`
- `adop summary`: no longer prints a comparison-time structural gap once a scene has advanced to `in-trial` or later
- CI: repaired `ci.yml` (a Windows PowerShell here-string broke the workflow YAML, startup-failing every run since 0.1.1); de-flaked the concurrent id-mint test on loaded runners
- CLI no longer leaks a raw `KeyError` / traceback when a parent artifact is missing a field a handler reads (e.g. a hand-edited or schema-drifted trial packet); it returns a JSON error envelope with exit 11

### Changed

- Clean tool-only repository: removed the self-dogfooding `.adop/` records and the tool-surface demo files; moved `SECURITY` / `CONTRIBUTING` / `CODE_OF_CONDUCT` / `SUPPORT` into `.github/`
- Lint: ignore `E501` (long help/template strings) while keeping `line-length` for `ruff format`; dropped the dead relative-import branch so `mypy` passes

### Tests

- Suite grew from 105 to 202 tests

## 0.1.1 - 2026-06-17

### Added

- `pyproject.toml`: pip install support — `pip install git+https://github.com/maruwork/adop.git` now works; installs `adop` and `adop-sync` as console commands
- CI: `pip-install` job verifies the installed package on each push
- CI: `windows-latest` added to OS matrix; smoke test uses `shell: bash` for cross-platform compatibility

### Fixed

- README Setup section: code fence was not closed on a separate line (markdown rendering broken)
- README: added Python 3.11/3.12 requirement and alias setup instructions for Linux/macOS and Windows
- CHANGELOG: artifact type count corrected from 13 to 14

## 0.1.0 - 2026-06-15

### Added

- 11-state tool adoption lifecycle: watch → proposed → blocked → trial-ready → in-trial → promote / hold / reject → deprecated → migrating → archived
- 24 CLI commands covering the full lifecycle plus tool-to-file coupling recording
- `adop init`: scaffold `.adop/` artifact root and project-local overlay in one command
- `adop status`: present state per (tool, use-case) scene with next-step guidance
- `adop next`: single recommended next command for the most active pending scene
- `adop scan`: static analysis to detect tool-to-file couplings (import, config, invocation, reference)
- `adop lint`: artifact root validation with exit-code contract (exit 0 ok, exit 10 error)
- Default artifact root `.adop/`: `--artifact-root` is optional on every command
- `adop_sync.py`: drift detection and sync for project-local runtime copies (`check`, `apply`, `register`, `push`, `list`)
- `adop.json`: machine-readable canonical identity and runtime file manifest
- Artifact schema validation for all 14 artifact types including hold-note and reject-note
- Tool entanglement (coupling-note) recording and reporting
- Append-only atomic artifact writes with boundary and IO error handling (exit 11, 14)
- 105 tests covering lifecycle, validation, coupling, artifact root errors, sync, status, and scan

### Changed

- `adop_sync.py`: `--target` points to the project root; runtime files preserved at `<target>/shared/python/`
- `adop lint`: outputs human-readable text by default; exit 10 on missing or empty root

### Fixed

- `adop scan`: Node ecosystem files and Windows scripts now classified correctly
- `adop_sync apply`: creates parent directories automatically
- `adop close-trial`: hold verdict generates hold-note; reject verdict generates reject-note (previously both used reject-note)
- `adop lint`: open trials (no trial-result yet) are not flagged for missing judgment-report

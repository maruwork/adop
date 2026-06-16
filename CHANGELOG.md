# Changelog

All notable changes to this project are documented in this file.

## Unreleased

### Added

- `adop.json`: machine-readable canonical identity and runtime file manifest
- `adop_sync.py`: drift detection and sync for project-local runtime copies (`check`, `apply`, `register`, `push`, `list`)
- `tests/test_sync.py`: 12 tests covering sync check/apply/register/push/list
- `shared/templates/project-local-adop-overlay-template.md`: minimum structure template for project-local overlays
- `ADOP_SHELF_CLASSIFICATION.md`: authority contract — formal table of what ADOP common owns vs. project-local overlay
- `adop init`: scaffold `.adop/` artifact root and overlay file in one command
- `adop status`: show current lifecycle state per scene with next steps and coupling summary
- `adop scan`: static analysis of a directory to detect tool-to-file couplings (import, config, invocation, reference)
- `adop next`: print the single recommended next CLI command for the most active pending scene
- Default artifact root `.adop/`: `--artifact-root` is no longer required on any command; omitting it uses `.adop/` with a helpful error if missing
- `tests/test_usability_commands.py`: 18 tests covering init, status, scan, next, and default artifact root

### Changed

- `adop_summary.py`: added public `get_scene_states()` function for CLI status/next commands
- CLI epilog updated to guide first-time users to `adop init`
- `adop_sync.py`: `--target` now points to the project root; runtime files preserved at `<target>/shared/python/` (Option B — full relative path, not basename-only flat layout)
- `docs/ADOP_GENERIC_QUICKSTART.md`: unified entry point to `python shared/python/adop_cli.py`, OS-agnostic examples (no `/tmp`, bash glob, or `cp`), `adop init` shortcut documented
- `shared/templates/project-local-adop-overlay-template.md`: unified command examples to `python shared/python/adop_cli.py` / `adop_sync.py`

### Fixed

- `adop scan`: Node ecosystem files (`package.json`, lock files) and Windows scripts (`.ps1`, `.bat`, `.cmd`) now classified correctly instead of falling through to `reference/clean`
- `adop_sync`: structured layout (`shared/python/` mirroring canonical) now works; `apply` creates parent directories automatically

## 0.1.0 - 2026-06-15

### Added

- 11-state tool adoption lifecycle: watch, proposed, blocked, trial-ready, in-trial, promote, hold, reject, deprecated, migrating, archived
- 24 CLI commands covering the full lifecycle plus tool-to-file coupling recording
- Artifact schema validation with lint command
- Tool entanglement (coupling-note) recording and reporting
- Summary command with Current State by Scene, Lifecycle Notes, and Tool Entanglement sections
- 101 tests covering lifecycle, validation, coupling, artifact root error handling, sync, status, and scan

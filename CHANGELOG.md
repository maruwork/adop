# Changelog

All notable changes to this project are documented in this file.

## Unreleased

_Nothing yet._

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

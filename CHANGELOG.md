# Changelog

All notable changes to this project are documented in this file.

## Unreleased

### Added

- `adop.json`: machine-readable canonical identity and runtime file manifest
- `adop_sync.py`: drift detection and sync for project-local runtime copies (`check`, `apply`, `register`, `push`, `list`)

### Changed

### Fixed

## 0.1.0 - 2026-06-15

### Added

- 11-state tool adoption lifecycle: watch, proposed, blocked, trial-ready, in-trial, promote, hold, reject, deprecated, migrating, archived
- 20 CLI commands covering the full lifecycle plus tool-to-file coupling recording
- Artifact schema validation with lint command
- Tool entanglement (coupling-note) recording and reporting
- Summary command with Current State by Scene, Lifecycle Notes, and Tool Entanglement sections
- 64 tests covering lifecycle, validation, coupling, and artifact root error handling

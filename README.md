# ADOP

When a team evaluates a new library, linter, or service, the reasoning ends up scattered across Slack threads, issue comments, and wikis. Six months later, nobody remembers why the tool was accepted or rejected — or what the trial conditions were. The next team member starts the evaluation over.

ADOP is a CLI that gives each tool evaluation a structured, append-only record. Every decision — from "we noticed this tool" through "we ran a bounded trial" to "we promoted it" or "we rejected it" — is written as a timestamped artifact in your project's `.adop/` directory. The record outlasts the discussion.

## Who Needs This

Teams that:
- evaluate multiple tools or libraries per quarter and need to trace why each was accepted or rejected
- run bounded trials and want to record the trial conditions and outcome, not just the verdict
- need to show auditors or future teammates that adoption decisions were deliberate and documented
- want to know how deeply a tool is embedded before deciding to replace it

## How It Works

Each evaluation is tracked as a **scene lane** rooted at `related_scene`, with the chosen tool and adoption unit carried by the artifacts inside that lane. Evaluating `ruff` as a linter is therefore a separate lane from evaluating `ruff` as a formatter. Each lane moves through up to 11 states:

```
watch → proposed → blocked → trial-ready → in-trial
  → promote / hold / reject → deprecated → migrating → archived
```

State is always derived from what is written on disk. There is no daemon, no database, no central server.

## What It Looks Like

```
$ adop status

ADOP  (.adop/)

  lint-pipeline   in-trial

Next steps:
  [lint-pipeline]
    adop quick-close-trial --trial-id tr-001 --verdict <promote|hold|reject> --observed-effect "<what you saw>" # promote also requires explicit judgment fields

$ adop next
[lint-pipeline] (in-trial)
  adop quick-close-trial --trial-id tr-001 --verdict <promote|hold|reject> --observed-effect "<what you saw>" # promote also requires explicit judgment fields
```

Artifacts are plain JSON files in `.adop/`. They are append-only — nothing is deleted or overwritten. `adop lint` validates the full record.

## Setup

**Requires Python 3.11, 3.12, or 3.13.**

**Option A — pip install (recommended)**

```bash
pip install git+https://github.com/maruwork/adop.git
adop --version   # adop 0.1.1
```

**Option B — clone and run**

```bash
git clone https://github.com/maruwork/adop.git
cd adop
python shared/python/adop_cli.py --version   # adop 0.1.1
```

With Option B, all commands run as `python shared/python/adop_cli.py <command>`.
For convenience, alias it once per shell session:

```bash
# Linux / macOS
alias adop="python $(pwd)/shared/python/adop_cli.py"

# Windows (PowerShell)
function adop { python "$PWD\shared\python\adop_cli.py" @args }
```

## Quickstart

```bash
# 1. In your project directory, scaffold the record store and overlay
adop init

# 2. Record the first candidate
adop quick-intake --candidate ruff --source doc --scene lint-pipeline --why-now "evaluating faster linter"

# 3. Compare candidates and select one
adop quick-compare --scene lint-pipeline --candidate ruff --candidate pylint --selected ruff

# 4. Start a bounded trial
adop quick-trial --scene lint-pipeline --mode read-only-comparison --executor ci --decision-owner eng-lead --landing-target ci/lint

# 5. Check present state at any time
adop status

# 6. Close the trial with a verdict
adop quick-close-trial --trial-id tr-001 --verdict hold --observed-effect "30% faster, but approval scope still needs narrowing"

# 7. Validate the full record
adop lint

# 8. Render one dashboard HTML from the canonical template
adop render-html --artifact-root .adop --output workspace/html-preview/adop_dashboard.html
```

Full command reference: `adop --help`

Guided `quick-close-trial --verdict promote` is intentionally stricter: it requires explicit `--judgment-reason`, `--next-action`, `--recurring-control-decision`, `--root-cause-hypothesis`, `--preventive-action`, and `--why-this-problem-recurred` so that promotion evidence is not silently auto-filled.
Promotion is also blocked if the latest intake still carries `unknown` tool attributes; placeholders are allowed during guided intake, but they must be resolved before a tool is promoted.
`reject` is terminal for a scene lane. If a materially new evaluation is needed later, open a new scene name instead of reopening the rejected lane.

See `docs/checklists/` before starting adoption work.

## Where Records Are Saved

All artifacts write to `.adop/` in the present working directory by default.
The `--artifact-root` flag is optional on every command.
`adop init` creates the directory and a project-local overlay file in one step.

## Detecting Tool Coupling

Before replacing or removing a tool, check how deeply it is embedded:

```bash
adop scan --target . --tool ruff
```

Reports every file that imports, configures, or references the tool, along with an estimated removal cost.
Detected entries also carry a machine-readable detection source and confidence so that
strong config surfaces can be distinguished from low-confidence text references.
High-confidence hits are derived from structured surfaces such as `pyproject.toml`,
`package.json`, `.pre-commit-config.yaml`, workflow `uses:` / `run:` commands, and
tool-owned config filenames.
For larger repos, exclude noisy shelves and write the snapshot directly:

```bash
adop scan --target . --tool ruff --scene lint-ci --exclude archive --exclude common --exclude workspace --record
```

## Rendering One Dashboard HTML

Use the canonical template under `shared/templates/` and render exactly one dashboard output per target path:

```bash
adop render-html --artifact-root .adop --output workspace/html-preview/adop_dashboard.html
```

The rendered dashboard is intended to stand on its own for first-time readers:
- it explains what ADOP records
- it shows the artifact root that produced the page
- it separates recorded lanes from preview sample lanes
- it shows zero-record startup commands when the artifact root is still empty
- it keeps promoted lanes on `No required next command` and moves retirement into a separate command box
- it supports search, state filtering, sorting, and `Show more` for larger lane portfolios

For layout testing, you can stress the board without adding real artifacts:

```bash
adop render-html --artifact-root .adop --output workspace/html-preview/adop_dashboard.html --sample-board-count 10
```

When preview lanes are injected this way, the page warns that those rows are samples and must not be treated as project decisions.

## File Map

- `adop.json`: machine-readable canonical identity and runtime file manifest
- `shared/python/`: CLI and supporting modules
  - `adop_cli.py`: command entry point
  - `adop_html.py`: canonical HTML dashboard renderer
  - `adop_artifacts.py`: artifact IO / atomic write
  - `adop_validation.py`: schema and gate validation
  - `adop_summary.py`: summary projection
  - `adop_types.py`: constants and field names
  - `adop_ids.py`: id generation and parsing
  - `adop_state_machine.py`: lifecycle transition rules
  - `adop_sync.py`: drift detection and sync for project-local runtime copies
  - `common.py`: bounded runtime helper
- `docs/checklists/`: review checklist before starting an evaluation
- `shared/templates/`: record templates for adoption notes and project-local overlays
  - `adop-governance-dashboard-template.html`: canonical HTML dashboard template
- `docs/design/`: design notes and schema reference
- `docs/ADOP_GENERIC_QUICKSTART.md`: fastest path to understand and verify ADOP
- `SUPPORT.md`: pre-issue checklist and support contact routes

## Full Reading Order

1. `README.md`
2. `docs/design/ADOP_SHELF_CLASSIFICATION.md`
3. `docs/ADOP_GENERIC_QUICKSTART.md`
4. `docs/checklists/external-tool-adoption-checklist.md`
5. `shared/templates/external-tool-adoption-note-template.md`
6. `shared/templates/project-local-adop-overlay-template.md`
7. `shared/python/adop_types.py`
8. `shared/python/adop_cli.py`
9. `docs/design/adop-lifecycle-schema-design.md`
10. `SUPPORT.md`

## Authority Boundary

This repository holds the shared authority: artifact schema, lifecycle states, CLI, generic checklist, and templates.

Each project maintains its own overlay file (scaffolded by `adop init`) that holds the project-specific trial board, operator flow, and landing target authority. The boundary is defined in `docs/design/ADOP_SHELF_CLASSIFICATION.md`.

## Repository Community Files

- `LICENSE`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `CODE_OF_CONDUCT.md`
- `CHANGELOG.md`
- `SUPPORT.md`
- `.github/ISSUE_TEMPLATE/`
- `.github/PULL_REQUEST_TEMPLATE.md`
- `.github/CODEOWNERS`
- `.github/workflows/ci.yml`

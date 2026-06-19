# Project-Local ADOP Overlay

**Status**: Active
**Common authority**: https://github.com/maruwork/adop
**ADOP version synced**: 0.1.1 (canonical repo itself)

---

## Artifact Root

Adoption artifacts for this project live at:

```
.adop/
```

Validate: `python shared/python/adop_cli.py lint --artifact-root .adop`

---

## Runtime Copy

ADOP runtime files (`adop_*.py`, `common.py`) are at:

```
shared/python/
```

Last verified against canonical: 2026-06-18
Check drift: not applicable here because this repository is the canonical source

---

## Active Scene Lanes

| Scene Lane | Tool | Current State | Last Activity |
|---|---|---|---|
| `lint-python` | `ruff` | `in-trial` | 2026-06-18 |
| `commit-gates` | `pre-commit` | `in-trial` | 2026-06-18 |
| `repo-hygiene-hooks` | `pre-commit-hooks` | `in-trial` | 2026-06-18 |
| `workflow-schema-check` | `check-jsonschema` | `in-trial` | 2026-06-18 |
| `type-check-python` | `mypy` | `in-trial` | 2026-06-18 |
| `parallel-pytest` | `pytest-xdist` | `in-trial` | 2026-06-18 |
| `js-lint` | `eslint` | `in-trial` | 2026-06-18 |
| `js-format` | `prettier` | `in-trial` | 2026-06-18 |
| `workflow-action-check` | `actionlint` | `in-trial` | 2026-06-18 |
| `shell-script-lint` | `shellcheck` | `in-trial` | 2026-06-18 |
| `repo-security-scan` | `trivy` | `in-trial` | 2026-06-18 |
| `dependency-refresh-bot` | `renovate` | `in-trial` | 2026-06-18 |
| `dockerfile-lint` | `hadolint` | `in-trial` | 2026-06-18 |
| `markdown-lint` | `markdownlint-cli2` | `in-trial` | 2026-06-18 |
| `editor-eslint-integration` | `vscode-eslint` | `in-trial` | 2026-06-18 |
| `dependency-bot-alt` | `dependabot` | `in-trial` | 2026-06-18 |

Live view: `python shared/python/adop_cli.py summary --artifact-root .adop`

---

## Operator Flow

| Stage | Who | How |
|---|---|---|
| Raise a candidate | repo maintainer | edit repo config, note intended tool, then create ADOP intake |
| Run comparison | repo maintainer | compare against status quo or lighter alternative in the matching scene lane |
| Open trial | repo maintainer + CI | wire config into `pyproject.toml`, `.pre-commit-config.yaml`, or `.github/workflows/ci.yml` |
| Close trial | repo maintainer | use CI evidence plus coupling review before `promote` / `hold` / `reject` |
| Define landing target | repo maintainer | fix the exact owning file or workflow location before promotion |

---

## Current Judgment Memo

| Item | Current project answer |
|---|---|
| Adoption class | mixed: this repo records both recurring operations integration examples and creation-assistance governance behavior |
| Layer to strengthen | mechanism |
| Phase | self-improvement loop |
| What serves as authority | `.adop/` artifacts, repo-tracked config/workflow files, and human-reviewed promotion decisions |
| What does not serve as authority | preview sample rows, ad-hoc tool output, unrecorded scan output, or undocumented convenience use |
| Fail-close / escalation / verification | unresolved or unknown cases stay `hold` / `reject`; repo maintainer decides status changes; verify with `adop lint`, coupling review, and CI evidence before promote |

---

## Approved Use Scenes

| Scene | Tool | Allowed use | Landing target | Notes |
|---|---|---|---|---|
| none yet | none | no recurring tool use is promoted yet in this repository | n/a | every recorded scene is still `in-trial` as of 2026-06-18 |

---

## Prohibited Use Scenes

| Scene | Tool | Prohibited or blocked use | Reason | Reopen condition |
|---|---|---|---|---|
| all scenes until promoted | all recorded tools | treat any in-trial tool as approved recurring authority | no scene has been promoted yet | a recorded `promotion-note` plus updated landing target authority |
| preview sample rows | sample-only lanes | use layout-check sample rows as if they were project decisions | samples are not canonical records | render HTML without sample rows, or rely only on recorded lanes |
| unrecorded convenience use | any external tool | keep using a tool repeatedly without leaving ADOP artifacts | breaks the explicit adoption record and authority boundary | create the missing intake / compare / trial / coupling artifacts |

---

## Landing Target Authority

Promoted tools land at:

| Target | Owner | Notes |
|---|---|---|
| `pyproject.toml` | repo maintainer | dependency declarations plus `ruff` / `mypy` settings |
| `.pre-commit-config.yaml` | repo maintainer | `pre-commit`, `pre-commit-hooks`, `check-jsonschema`, local `ruff`, local `mypy` hooks |
| `.github/workflows/ci.yml` | repo maintainer | CI surface for `pre-commit` and `pytest -n auto` |
| `tool-surfaces/package.json` / `tool-surfaces/eslint.config.js` / `tool-surfaces/.prettierignore` | repo maintainer | Node-side examples for `eslint` and `prettier` |
| `.github/workflows/tool-surface-examples.yml` | repo maintainer | example workflow for `actionlint`, `shellcheck`, `trivy`, `eslint`, and `prettier` |
| `tool-surfaces/scripts/repo-smoke.sh` | repo maintainer | shell script surface used by `shellcheck` |
| `tool-surfaces/.trivyignore` | repo maintainer | repo-local security scan exception surface for `trivy` |
| `tool-surfaces/renovate.json` | repo maintainer | bot-style config surface for `renovate` |
| `tool-surfaces/Dockerfile.tooling-example` | repo maintainer | Dockerfile surface for `hadolint` |
| `tool-surfaces/.markdownlint-cli2.jsonc` | repo maintainer | Markdown lint config surface for `markdownlint-cli2` |
| `tool-surfaces/.vscode/extensions.json` / `tool-surfaces/.vscode/settings.json` | repo maintainer | editor integration surface for `vscode-eslint` |
| `.github/dependabot.yml` | repo maintainer | dependency bot config surface for `dependabot` |

---

## Pending Project Decisions

| Item | Status |
|---|---|
| Verify the new dev-tool surface on a networked GitHub runner | pending |
| Decide whether Node / bot / security scenes should be promoted or kept as audit-only examples | pending |
| Verify whether low-confidence `text-reference` hits are strict enough to keep for this repo, or should be filtered further | pending |
| Treat editor-local settings such as `tool-surfaces/.vscode/settings.json` as first-class coupling surfaces even when the tool id is implicit | fixed in generic scan on 2026-06-18 |

---

## Return Path

Common authority: https://github.com/maruwork/adop
Lifecycle and schema spec: `docs/design/adop-lifecycle-schema-design.md`
Adoption checklist: `docs/checklists/external-tool-adoption-checklist.md`

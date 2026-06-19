# Project-Local ADOP Overlay

**Status**: Active
**Common authority**: https://github.com/maruwork/adop
**ADOP version synced**: 0.1.1 (canonical repo itself)

This repository is the canonical ADOP source. It does not track its own tool-adoption
scenes here; consumer projects create their own `.adop/` and overlay via `adop init`.

---

## Artifact Root

Adoption artifacts for a consumer project live at:

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

Last verified against canonical: 2026-06-19
Check drift: not applicable here because this repository is the canonical source

---

## Active Scene Lanes

| Scene Lane | Tool | Current State | Last Activity |
|---|---|---|---|
| none | none | this canonical repo records no project-local adoption scenes | n/a |

Live view: `python shared/python/adop_cli.py summary --artifact-root .adop`

---

## Operator Flow

| Stage | Who | How |
|---|---|---|
| Raise a candidate | repo maintainer | open an issue / note the intended tool, then `adop quick-intake` |
| Run comparison | repo maintainer | `adop quick-compare` against the status quo or a lighter alternative |
| Open trial | repo maintainer | `adop quick-trial` with a bounded, no-write mode |
| Close trial | repo maintainer | `adop quick-close-trial` with observed evidence |
| Define landing target | repo maintainer | fix the exact owning file/workflow before promotion |

---

## Current Judgment Memo

| Item | Current project answer |
|---|---|
| Adoption class | n/a — canonical tool repository, not a consumer project |
| Layer to strengthen | mechanism (the ADOP CLI itself) |
| Phase | core build / self-improvement loop |
| What serves as authority | `shared/python/` runtime, repo-tracked config/workflow files, human-reviewed decisions |
| What does not serve as authority | ad-hoc tool output, unrecorded scan output, undocumented convenience use |
| Fail-close / escalation / verification | unresolved cases stay unadopted; maintainer decides; verify with `pytest`, `adop lint`, and CI |

---

## Approved Use Scenes

| Scene | Tool | Allowed use | Landing target | Notes |
|---|---|---|---|---|
| none yet | none | no recurring external-tool use is promoted in this repository | n/a | dev toolchain (ruff/mypy/pytest/pre-commit) is project tooling, not an ADOP-tracked scene |

---

## Prohibited Use Scenes

| Scene | Tool | Prohibited or blocked use | Reason | Reopen condition |
|---|---|---|---|---|
| unrecorded convenience use | any external tool | repeated use without leaving ADOP artifacts | breaks the explicit adoption record | create the missing intake / compare / trial artifacts |

---

## Landing Target Authority

| Target | Owner | Notes |
|---|---|---|
| `pyproject.toml` | repo maintainer | build metadata, dependencies, ruff / mypy / pytest / coverage config |
| `.pre-commit-config.yaml` | repo maintainer | ruff, ruff-format, mypy, and workflow-schema hooks |
| `.github/workflows/ci.yml` | repo maintainer | black-box install + source-tree test matrix |

---

## Return Path

Common authority: https://github.com/maruwork/adop
Lifecycle and schema spec: `docs/design/adop-lifecycle-schema-design.md`
Adoption checklist: `docs/checklists/external-tool-adoption-checklist.md`

# Project-Local ADOP Overlay

**Status**: Active
**Common authority**: https://github.com/maruwork/adop
**ADOP version synced**: [fill in from adop.json at sync time]

Copy this file into the project. Fill in each section.
Do not copy schema, lifecycle definitions, or CLI descriptions from ADOP — reference them.

---

## Artifact Root

Adoption artifacts for this project live at:

```
[path/to/artifact-root/]
```

Validate: `python shared/python/adop_cli.py lint --artifact-root [path]`

---

## Runtime Copy

ADOP runtime files (`adop_*.py`, `common.py`) are at:

```
[path/to/adop-runtime-copy/]
```

Last verified against canonical: [date]
Check drift: `python shared/python/adop_sync.py check --target [path/to/project-root/]`

---

## Active Scene Lanes

| Scene Lane | Tool | Current State | Last Activity |
|---|---|---|---|
| [scene] | [tool] | [state] | [date] |

Live view: `python shared/python/adop_cli.py summary --artifact-root [path]`

---

## Operator Flow

| Stage | Who | How |
|---|---|---|
| Raise a candidate | [who] | [how: issue, doc, meeting] |
| Run comparison | [who] | [time box, decision method] |
| Open trial | [who] | [executor, mode, scope] |
| Close trial | [who] | [judgment criteria, sign-off] |
| Define landing target | [who] | [authority, location] |

---

## Current Judgment Memo

State the current project-side judgment in the same language the shared checklist expects.
Fill these fields even when the answer is "none yet" or "not approved".

| Item | Current project answer |
|---|---|
| Adoption class | [operations integration / creation assistance / mixed] |
| Layer to strengthen | [interface / mechanism / scaling] |
| Phase | [core build / future extension / implementation / self-improvement loop] |
| What serves as authority | [repo files, human review gate, workflow, etc.] |
| What does not serve as authority | [tool output, preview HTML rows, ad-hoc chat notes, etc.] |
| Fail-close / escalation / verification | [how the project stops, who decides, and how to verify] |

---

## Approved Use Scenes

List the scenes that are currently approved for recurring use in this project.
If nothing is approved yet, say so explicitly.

| Scene | Tool | Allowed use | Landing target | Notes |
|---|---|---|---|---|
| [scene or "none yet"] | [tool] | [what is currently approved] | [target] | [scope or approval note] |

---

## Prohibited Use Scenes

List the scenes that are currently blocked or forbidden in this project.
Include both "not approved yet" and "explicitly prohibited" when relevant.

| Scene | Tool | Prohibited or blocked use | Reason | Reopen condition |
|---|---|---|---|---|
| [scene or "none recorded"] | [tool] | [what must not happen] | [why] | [what would change this] |

---

## Landing Target Authority

Promoted tools land at:

| Target | Owner | Notes |
|---|---|---|
| [target location] | [owner] | [scope] |

---

## Pending Project Decisions

| Item | Status |
|---|---|
| [pending project decision or gap] | [pending / in-progress] |

---

## Return Path

Common authority: https://github.com/maruwork/adop
Lifecycle and schema spec: `docs/design/adop-lifecycle-schema-design.md`
Adoption checklist: `docs/checklists/external-tool-adoption-checklist.md`

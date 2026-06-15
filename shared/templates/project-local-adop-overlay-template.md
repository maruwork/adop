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

## Active Use Cases

| Use Case | Tool | Current State | Last Activity |
|---|---|---|---|
| [use-case] | [tool] | [state] | [date] |

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

## Landing Target Authority

Promoted tools land at:

| Target | Owner | Notes |
|---|---|---|
| [target location] | [owner] | [scope] |

---

## Open Items

| Item | Status |
|---|---|
| [pending decision or gap] | [open / in-progress] |

---

## Return Path

Common authority: https://github.com/maruwork/adop
Lifecycle and schema spec: `docs/design/adop-lifecycle-schema-design.md`
Adoption checklist: `docs/checklists/external-tool-adoption-checklist.md`

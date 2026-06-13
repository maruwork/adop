# Project File Taxonomy Template

**Use When**: deciding where each file type belongs.  
**Replace Per Project**: shelf names, file-type labels, example paths, and exception handling.  
**Do Not Put Here**: day-to-day `current` management, implementation-task details, or a project-specific redefinition of the current canonical surface.

> **Purpose**:
> reusable template for fixing project-specific file and folder structure as a `file type -> shelf` matrix.
> Do not carry source-project shelf names into it. Keep it minimal enough that any project can decide its shelves from the start.

**role**: fill the placement matrix - `file type -> shelf`  
**project_id**: `project_xxx`  
**status**: Draft / Approved  
**companion rulebook**: [`project-structure-governance-starter-pack.md`](./project-structure-governance-starter-pack.md) - shelf-class definitions, workspace rules, cleanup procedure  
**companion policies**:
- `../policies/entry-guide-reference-separation-policy.md`
- `../policies/file-operation-policy.md`
- `../policies/naming-and-shelf-policy.md`

---

## 1. Purpose

- decide the shelf before creating the file
- keep `current canonical`, support, generated output, and archive from crossing wires
- avoid turning the repo into a dumping ground as it grows

## 2. Entry Rule

- choose one first entry for a first-time reader or agent
  - `{example only: README.md / index.md / docs/README.md}`
- keep the entry file thin
- state explicitly that the taxonomy is a placement matrix, not a current-work board

## 3. Placement Matrix

| file type | canonical shelf | examples | notes / enforcement |
|---|---|---|---|
| `current canonical docs` | `{path}` | `{files}` | `{notes}` |
| `governance / policy` | `{path}` | `{files}` | `{notes}` |
| `design / architecture` | `{path}` | `{design/*.md or local equivalent}` | `{root design/ allowed when declared}` |
| `task / work tracking` | `{path}` | `{files}` | `{notes}` |
| `runtime / tool code` | `{path}` | `{files}` | `{notes}` |
| `external tools` | `{approved local path or none}` | `{actual local path}` | `{do not treat this as a repository reading surface; controllable generated output goes to approved ignored local state; checkout residue stays non-authoritative}` |
| `library / shared code` | `{path}` | `{files}` | `{notes}` |
| `tests` | `{path}` | `{files}` | `{notes}` |
| `config / schema` | `{path}` | `{files}` | `{notes}` |
| `templates / reusable assets` | `{path}` | `{files}` | `{notes}` |
| `workspace / scratch` | `{path}` | `{files}` | `{includes ignored local tool state}` |
| `generated reports` | `{path}` | `{files}` | `{notes}` |
| `archive / historical` | `{path}` | `{files}` | `{notes}` |
| `entry / guide surface` | `{path}` | `{files}` | `{single entry / guide max 3}` |
| `agent root entry files` | `{root}` | `{AGENTS.md / CLAUDE.md}` | `{root-only}` |
| `root repo infrastructure files` | `{root}` | `{.gitignore / .gitattributes / .gitmodules / LICENSE}` | `{root-only}` |
| `github workflow and community files` | `{.github/}` | `{PULL_REQUEST_TEMPLATE.md / ISSUE_TEMPLATE_* / workflows/*}` | `{GitHub-owned surface}` |
| `reference shelf` | `{path}` | `{files}` | `{non-authority note / redirect to current canonical}` |

## 4. Placement Decision Order

1. check whether the existing matrix already has a matching row
2. if an existing shelf explains the role, do not create a new folder
3. fix the exact save location before creating or installing the file
4. add a new file type only when no row matches
5. if temporary placement is unavoidable, use the declared workspace

## 5. Canonical Separation Rule

This taxonomy must preserve at least these five classes:

- current canonical
- support
- generated
- historical
- external intake

Do not scatter files with the same meaning across multiple shelves.

## 6. Root Rule

- keep root exceptions explicit and minimal
- root-level `design/` is allowed only when it is the declared design / architecture shelf
- `AGENTS.md` and `CLAUDE.md` stay at root
- `.gitignore`, `.gitattributes`, and `.gitmodules` stay at root

## 7. Workspace Rule

- converge active workspace into one place
- do not mix generated output into canonical shelves
- keep local tool state in workspace or another ignored path

## 8. Archive Rule

- prefer archive over delete
- record why an archived file left the active topology
- do not mix active shelves and archive shelves

## 9. Follow-Through Surfaces

When a file role or location changes, update at least:

- the taxonomy
- the entry index or navigation
- the boundary or disposition register

## 10. Completion Rule

This taxonomy is complete only when at least the following are in place:

- entry file
- placement matrix
- workspace / archive rule
- root rule

## 11. Local Notes

- `{project-specific exceptions}`
- `{enforcement hooks or scripts}`
- `{known residual shelves}`

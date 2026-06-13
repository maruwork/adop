# ADOP Project File Taxonomy

Status: Active

## 1. Purpose

Fix the placement of each file type in ADOP to prevent generic authority from mixing with support materials or residue.

## 2. Entry Rule

- delegated AI entry:
  - `AGENTS.md`
- human entry:
  - `README.md`
- governance entry:
  - `docs/governance/project-template-adoption-packet.md`

## 3. Placement Matrix

| file type | canonical shelf | examples | notes / enforcement |
|---|---|---|---|
| `current canonical docs` | repo root, `docs/checklists/`, `shared/templates/`, `shared/python/` | `README.md`, lifecycle docs | public-facing docs may stay at root |
| `governance / policy` | `docs/governance/`, `common/policies/` | adoption packet, taxonomy, boundary register | project-local governance goes under `docs/governance/` |
| `design / architecture` | `docs/design/` | design docs, shelf classification | support, not daily current |
| `publication / release planning` | `docs/publication/` | runbooks, pre-release checklists, export guides | support, not canonical current |
| `runtime / tool code` | `shared/python/` | CLI, artifact IO, validation helpers | caller-sensitive |
| `config / schema` | repo root | entry and quickstart docs | keep public-facing docs visible |
| `templates / reusable assets` | `shared/templates/`, `common/templates/` | adoption note template | `common/` is shared local rule shelf |
| `workspace / scratch` | `workspace/` | one-off review files | not canonical |
| `generated reports or residue` | `workspace/`, `__pycache__/` (any), `.pytest_cache/` | scratch outputs, bytecode cache, test cache | not authoritative |
| `archive / historical` | `archive/` | completed wave roadmap, tasks, design docs | historical only; not canonical authority |
| `entry / guide surface` | repo root, `docs/` | `AGENTS.md`, `CLAUDE.md`, token optimization note | keep thin |

## 4. Root Rule

- root may keep public-facing lifecycle, publication, and support docs plus thin entry files
- new root support docs should be avoided when an existing shelf can explain the role
- governance-local additions should go to `docs/governance/`

## 5. Workspace Rule

- active workspace is `workspace/`
- generated residue under any `__pycache__/` or `.pytest_cache/` is not a canonical write target
- scratch files must not be promoted without updating governance docs

## 6. Archive Rule

- archive over delete when historical value exists
- `archive/` is the designated historical shelf; use it for completed wave materials
- do not leave retired files mixed with active shelves

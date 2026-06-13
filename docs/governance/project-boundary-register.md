# ADOP Project Boundary Register

Status: Active

## 1. Purpose

Fix the class and authority of each shelf in ADOP.

## 2. Register

| shelf | class | canonical now | role | notes |
|---|---|---|---|---|
| `README.md` | `front current surface` | `yes` | repo entry | human-readable primary route |
| `AGENTS.md` / `CLAUDE.md` | `front current surface` | `yes` | delegated AI entry | thin route only |
| `common/` | `support` | `no` | local reusable common rules | copied from `pj-template` |
| `docs/governance/` | `support` | `no` | local governance concretization | project-local adoption rules |
| `docs/AI_AGENT_RUNTIME_TOKEN_OPTIMIZATION.md` | `visible support` | `no` | token optimization local rule | redirects to canonical shelves |
| `shared/python/`, `docs/checklists/`, `shared/templates/` | `current canonical` | `yes` | generic ADOP runtime and reusable authority | caller-sensitive |
| `docs/design/` | `support` | `no` | design and architecture notes | not daily current |
| `docs/publication/` | `support` | `no` | publication planning and runbooks | not daily current |
| `archive/` | `historical` | `no` | completed wave materials | not canonical authority |
| `workspace/`, `__pycache__/` (any code shelf), `.pytest_cache/` | `generated` | `no` | scratch or residue | never treated as authority |
| `.github/` | `support` | `no` | community and repo ops metadata | not runtime authority |

## 3. Reading Rules

- read entry first, then governance route, then the exact checklist, template, or CLI file under change
- support shelves do not replace canonical lifecycle or template shelves
- generated shelves never define lifecycle truth or current topology

## 4. Minimum Required Shelves

- entry:
  - `AGENTS.md`
  - `CLAUDE.md`
  - `README.md`
- governance:
  - `docs/governance/`
- runtime:
  - `shared/python/`
  - `docs/checklists/`
  - `shared/templates/`
- support:
  - `common/`
  - `docs/design/`
  - `docs/publication/`
- historical:
  - `archive/`
- generated:
  - `workspace/`
  - `__pycache__/` (any code shelf, e.g. `shared/python/`, `tests/`)
  - `.pytest_cache/`

## 5. Boundary Questions

- public-facing lifecycle docs may remain at root but do not replace the governance route
- generated residue may exist under any `__pycache__/` or `.pytest_cache/` but must not receive new canonical writes
- completed wave materials belong in `archive/`; do not leave them in active shelves

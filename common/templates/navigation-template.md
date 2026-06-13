# Navigation Template

**Use When**: defining the project's entry files and reading order.  
**Replace Per Project**: file names, guide names, current-state paths, and downstream references.  
**Do Not Put Here**: project-specific current status, implementation detail, or archive decisions.

## 0. What This Template Decides

- the first entry a reader should open
- the minimum guide set
- where current state is read
- what counts as support versus current authority

## 1. Entry

- single entry:
  - `{README.md or equivalent}`
- role:
  - `{first project entry}`

Keep the entry thin.
It should only route the reader to the next correct surface.

## 2. Guides

Keep guides to three or fewer by default.

| Guide | Role | Open when |
|---|---|---|
| `{guide-first-read.md}` | first-time understanding order | when starting from the whole picture |
| `{guide-current-work.md}` | active-work route | when following current work |
| `{guide-runtime.md}` | runtime or implementation route | when inspecting implementation |

## 3. Canonical Documents

| Document | Role | Path |
|---|---|---|
| overview / concept |  |  |
| current state |  |  |
| governance / rule source |  |  |
| runtime / implementation |  |  |

## 4. Support Shelf

Route inventory, generated indexes, backlog catalogs, and historical lookup into a support or reference shelf.

Support documents must not double as the canonical source of current state.

## 5. Current-State Entry

Declare only the minimum surfaces that should be read first for current state.

| Order | Path | Role |
|---|---|---|
| 1 |  |  |
| 2 |  |  |
| 3 |  |  |

If the project has no local daily current surface, state that explicitly.

## 6. Entry Role Separation

Keep these roles separate:

| Entry type | Path | Role |
|---|---|---|
| whole-project entry |  |  |
| current-work entry |  |  |
| design entry |  |  |
| runtime entry |  |  |

## 7. Reading Order

| What the reader wants | Route |
|---|---|
| understand the whole project for the first time | `single entry` -> `whole-project entry` -> `overview / concept` -> `governance / rule source` |
| follow work that is active now | `single entry` -> `current-work entry` -> `current state` |
| inspect runtime / DB / tool reality | `single entry` -> `runtime entry` -> `runtime / implementation` |

## 8. Completion Check

- the entry file alone lets a reader choose the next step
- guides do not replace current authority
- support documents are unlikely to be mistaken for the canonical source of current state
- new documents can be placed without ambiguity

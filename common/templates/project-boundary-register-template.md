# Project Boundary Register Template

**Use When**: registering the class and disposition of each shelf.  
**Replace Per Project**: shelf names, class names, dispositions, and how supporting evidence is stored.  
**Do Not Put Here**: the body of an implementation plan, the live canonical source for the current state, or a project-specific current-operation log.

> **Purpose**:
> a reusable template for fixing the treatment of each shelf and making it readable in one way only whether that shelf is current authority.

> **Reading Rule**:
> this file is a fill-in register.
> Read shelf classes, workspace handling, and cleanup procedure in [`project-structure-governance-starter-pack.md`](./project-structure-governance-starter-pack.md).

**project_id**: `project_xxx`  
**status**: Draft / Approved  
**paired taxonomy**: `project-file-taxonomy-template.md`  
**rulebook**: `project-structure-governance-starter-pack.md`

---

## 1. Purpose

- fix the meaning of each shelf
- keep live canonical authority distinct from support, generated, and history
- prevent misreads such as `all docs are current authority`

This template registers `the class and current-authority status of each shelf`.
It does not, by itself, determine:

- file-type placement
- retention rules for workspace, generated, or archive
- whole-project entry surfaces or read order

## 2. Register

| shelf | class | current authority now | role | notes |
|---|---|---|---|---|
| `{path}` | `current canonical` / `support` / `generated` / `historical` / `external` / `reserved-empty` | `yes/no` | `{role}` | `{notes}` |
| `{path}` | `current canonical` / `support` / `generated` / `historical` / `external` / `reserved-empty` | `yes/no` | `{role}` | `{notes}` |
| `{path}` | `current canonical` / `support` / `generated` / `historical` / `external` / `reserved-empty` | `yes/no` | `{role}` | `{notes}` |

## 3. Reading Rules

For the definitions of shelf classes, read the cleanup-procedure section of:

- [`project-structure-governance-starter-pack.md`](./project-structure-governance-starter-pack.md)

Write each shelf class in the `class` column of Section 2.
Allowed class values:

- `current canonical`
- `front current surface`
- `support`
- `visible support`
- `generated`
- `historical`
- `external`
- `reserved-empty`

## 4. Minimum Required Shelves

Register at least the following:

- entry or index shelf
- current task or work shelf
- governance or policy shelf
- design shelf (`design/` at project root is allowed when explicitly declared)
- runtime or code shelf
- workspace or generated shelf
- archive or historical shelf
- front current surface
- hidden active or ignored shelf
- the shelf for post-execution or post-agent leftovers, if any
- any `reserved-empty` shelf that exists

## 5. Boundary Questions

For every shelf, answer at least:

- is this current authority now
- what is the shelf for
- what must not be placed here
- what reader or agent assumes this shelf exists
- whether it may appear on the front current surface
- if it remains only as visible support, which live entry surface it returns to

## 6. Completion Rule

- the taxonomy and the register describe the same shelf structure
- the entry file and the register do not contradict one another
- generated, archive, and support do not cross with live canonical authority
- the front current surface does not cross with support or visible support
- if a reserved-empty shelf exists, its notes contain `no ad hoc write`
- if a hidden active asset exists, its notes contain visibility or manifest guidance

## 7. Local Exceptions

- `{exception keep shelves}`
- `{old-reference shelves}`
- `{external authority shelves}`
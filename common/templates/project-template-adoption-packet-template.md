# Project Template Adoption Packet Template

**Use When**: adopting `pj-template` into an individual project and fixing how far the AI may safely proceed inside that project.  
**Replace Per Project**: project name, entry routes, governance document locations, read/write/no-touch boundaries, and the names of any existing local rules.  
**Do Not Put Here**: implementation-task detail, final archive/delete judgment, or project-specific day-to-day operating logs.

**project_id**: `project_xxx`  
**status**: Draft / Approved  
**shared_template_source**: `{shared template source path or identifier}`  
**owner**: `{owner}`

---

## 1. Purpose

- fix how `pj-template` is applied inside this project
- fix where the AI may read, where it may write, and where it must stop
- keep project-local authority separate from the shared template

This packet is not the first place to define project-specific rules.
Use it after `../frameworks/project-progression-rule.md` to map the entry route, writeback destination, and owner-only decisions into the project-local surface.

## 2. Reading Route

Fix the reading order for this project:

1. `{project entry path}`
2. `{current work source of truth path / none}`
3. `{governance or rule source path}`
4. `{runtime / code surface path / none}`
5. `{this packet path}`

### 2.1 Entry Split

- whole-project entry:
  - `{path}`
- active-work entry:
  - `{path}`
- design entry:
  - `{path}`
- execution-surface entry:
  - `{path}`

## 3. Governance And Design

- governance document location:
  - `{path}`
- governance entry:
  - `{README path or main rule path}`
- installed packet:
  - `{packet path}`
- design document location:
  - `{path or none}`
- root `design/` adopted:
  - `{yes/no}`

## 4. Core Adoption Decisions

- current-work ownership:
  - `{local-source / downstream-source / no-active-source}`
- resume support:
  - `{present / none}`
- publication mode:
  - `{planned / not-planned}`
- structure weight:
  - `{lightweight / standard / extended}`
- runtime placement:
  - `{local / downstream / none}`

### 4.1 Decision Consequences

- current-work consequence:
  - `{local source path / downstream source path / none}`
- resume support consequence:
  - `{resume support path / none}`
- publication consequence:
  - `{publication responsibility path / none}`
- runtime consequence:
  - `{local runtime-sensitive path / downstream runtime authority path / none}`

### 4.2 Scope Split

- what the shared progression rule decides:
  - `{paths or bullets}`
- what this packet decides:
  - `{paths or bullets}`
- what remains truly project-specific:
  - `{paths or bullets}`

## 5. Read / Write / No-Touch Boundary

### Read

- `{paths}`

### Write

- `{governance or approved writeback paths}`
- `{allowed companion paths if any}`

### No-Touch

- `{archive paths}`
- `{runtime-sensitive or generated-sensitive paths}`
- `{external or hidden paths}`

## 6. Project Material Classification

- current work source of truth:
  - `{paths or none}`
- support:
  - `{paths}`
- generated / workspace:
  - `{paths}`
- historical / archive:
  - `{paths}`
- hidden active or ignored assets:
  - `{paths or none}`

## 7. Local Tool Surfaces

- external tools:
  - `{actual local tool path or none}`
- ignored local tool state:
  - `{approved ignored local state path or none}`

If the tool checkout still emits residue, record it as non-authoritative residue, not as a canonical project shelf.

Keep this section short.
Only record the paths actually used by the project.

## 8. Expected Local Deliverables

- root entry document or equivalent
- root `AGENTS.md`
- root `CLAUDE.md`
- file taxonomy or placement rule document
- boundary / write-scope document
- workspace / artifact handling document
- design document location, including root `design/` if adopted

If an equivalent local surface already exists, state its path and relationship explicitly.

## 9. Output And Reporting

- summary output:
  - `{path}`
- unresolved points:
  - `{path}`
- latest result wording rule:
  - `{rule}`

At minimum, keep these reporting fields:

- `success subject`
- `current location`
- `this turn's single action`
- `completion condition`
- `strong evidence`
- `stop reason`
- `next action`
- `writeback destination`

## 10. Owner-Only Decisions

- final canonical versus historical classification
- archive / restore / delete
- hidden active asset keep versus expose versus retire
- rename / move / delete when an external caller may depend on the path
- project entry replacement when the current route is unclear

## 11. Stop Conditions

- the current work route is unclear
- archive and active work are mixed without a local rule
- a hidden active asset is suspected
- the caller relationship of a generated artifact is unclear
- a new folder is being created without a placement rule

## 12. Completion Rule

- the project reading route is explicit
- the governance document location and packet path are explicit
- the read / write / no-touch boundary is explicit
- current, support, generated, and archive handling is explicit
- runtime-sensitive paths are explicit
- owner-only decisions remain owner-only
- the shared / packet / project-specific split is explicit

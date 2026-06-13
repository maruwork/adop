# Project Template Installation Gate Policy

## 1. Purpose

Define the minimum gate before installing `pj-template` into a project.

## 2. Core Rule

Do not create new project-local files or folders for `pj-template` until the installation gate passes.

Until it passes, stay in review mode and return only findings, options, and owner decisions.

## 3. Installation Gate

Installation is allowed only when all of the following are true:

1. the target project's entry route is explicit
2. the target project's existing governance or equivalent has been checked
3. the placement rule for any new file or folder is explicit
4. read / write / no-touch boundaries are explicit
5. no owner-only decision is being hidden inside the installation step
6. existing shelves were checked before proposing new ones

If one of these is missing, installation is not ready.

## 4. Required Reading

Before proposing or creating installation artifacts, read:

1. `project-progression-rule.md`
2. `project-template-adoption-completion-policy.md`
3. `file-operation-policy.md`
4. `naming-and-shelf-policy.md`
5. the target project's current entry file
6. the target project's current governance shelf or closest equivalent

## 5. What Counts as Installation

These actions require the gate:

- creating a new shelf or folder for template adoption
- creating `project-template-adoption-packet.md`
- creating taxonomy, boundary, or workspace-policy files in the target project
- creating new route or governance files for template adoption

## 6. Stop Conditions

Stop and do not install when any of these is true:

1. the authority relationship of existing files is unclear
2. a new folder would be created without a placement rule
3. an existing file may already serve the same role
4. owner judgment would be required for canonical, archive, restore, delete, or caller-sensitive rename decisions
5. hidden active assets or generated-caller relationships remain unresolved

## 7. Allowed Output Before Installation

Before gate pass, delegated AI may still return:

- inventory
- route and authority observations
- placement suggestions
- conflict analysis
- a proposed installation plan

Do not create installation files at this stage.

## 8. Default Installation Rule

After the gate passes:

- prefer existing shelves over new shelves
- prefer existing entry files over replacement entry files
- prefer the minimum required files
- if root `AGENTS.md` is absent, install it
- if root `CLAUDE.md` is absent, install it

## 9. Follow-Up Rule

After safe installation, also update the local route or governance entry that points to the installed file.

If that follow-up update is not yet safe, stop before installation.

# ADOP Private Release Hold Line

Status: Active

## Purpose

Define the explicit stop point after private preparation and before any public release action.

## Last Allowed Private Step

The last allowed private step is reached when all of the following are true:

- the private repository exists
- the carried files are placed
- the chosen license is added
- the chosen wording for the private repository copy is promoted
- the private verification sequence passes
- the chosen CI scope is wired

## First Forbidden Public Step

The following actions are outside this private-preparation wave:

- changing repository visibility to public
- treating the repository as publicly available
- running any public announcement or go-live action

## Hold Rule

If private bootstrap is complete, stop here until the user explicitly asks to proceed beyond the private state.

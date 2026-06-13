# PS Suite Companion Setup Guide

Portable baseline setup guide for reusing PS Suite companion scripts in another project or external work environment.

This document is not the runtime canonical source for the current project.  
It is a reusable example that lets the adopting project specify script names, package names, credential sources, and execution paths locally.

## 1. Purpose

- align the prerequisites for the first companion-script run
- define the minimum runtime, package, credential, and verification setup
- avoid embedding project-specific paths or local credential stores in the baseline text

## 2. Minimum Setup Cohort

Define at least the following cohorts:

| cohort | purpose |
|---|---|
| language runtime | script execution environment |
| package manager | dependency installation |
| browser/runtime tooling | required when browser validation exists |
| API credential | required when external APIs are called |
| script inventory | list of available scripts |
| verification step | what to check after setup |

## 3. Baseline Setup Pattern

### Runtime

- Python 3.10+
- Node.js 18+
- npm

### Dependencies

- install Python packages from `requirements.txt` or an explicit package list
- if browser automation exists, separate browser package installation from browser binary installation

### Credentials

- prefer environment variables for API keys
- if a local credential-store fallback exists, document the source and the fallback rule separately
- do not hard-code project-specific credential paths into the baseline

### Script Inventory

List at least the following for each script:

- script name
- purpose
- execution example
- required dependency

## 4. Verification Rule

Setup counts as complete only when:

- runtime versions can be checked
- dependency installation steps exist
- credential sources are explicit
- a script inventory exists
- a first verification command exists

## 5. Non-Goals

- this is not a production rollout manual for a specific project
- do not embed machine-specific paths or secret locations
- leave the adopting project's runtime boundary rules to separate documents
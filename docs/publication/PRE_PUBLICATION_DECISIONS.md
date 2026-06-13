# ADOP Pre-Publication Decisions

Status: Complete

## Purpose

Record the decisions that must be made before `ADOP` is published, without pretending they are already resolved.

## Resolved Decisions

### 1. License

Status: chosen

- chosen license: `MIT`

### 2. Repository Host And Owner

Status: chosen

- GitHub owner/org: `fumimaruwork`
- repository name: `adop`
- initial visibility: `private`

### 3. Public Contribution Surface

Status: chosen

- issue policy: issues open from day one
- pull request policy: PRs accepted from day one with maintainer review
- public community contributions from day one: `yes`

### 4. Public Security Intake

Status: chosen

- security-report intake posture: GitHub private vulnerability reporting if enabled
- private disclosure from day one: `yes`
- response posture: best effort, no fixed SLA

### 5. Public CI Scope

Status: chosen

- minimum public verification surface: public verification contract command set
- CI at repo creation: required

## Already Settled Inside The Shelf

- public-facing commands can be repo-relative
- public-facing file paths can be repo-relative
- bounded CLI verification works locally
- generic/common vs project-local overlay boundary is explicit

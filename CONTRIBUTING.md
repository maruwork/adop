# Contributing to ADOP

Thank you for considering a contribution.

## Before You Start

- read `README.md`
- read `SECURITY.md` if the change may involve credentials, local files, or vulnerability behavior
- check whether the issue already exists

## What This Project Accepts

- artifact schema and validation improvements
- CLI usability and bounded verification improvements
- generic checklist and template improvements
- public docs and export guidance

## What This Project Does Not Accept as Core Contributions

- project-local current trial boards
- project-local operator flows
- project-local landing target authority
- project-local adoption decision logs

## Preferred Contribution Flow

1. open or confirm an issue — issues may be opened from day one for bugs, docs, and bounded enhancement requests
2. prepare a focused branch
3. keep the change small enough to review
4. update docs when behavior or usage changes

## Pull Request Expectations

- explain what changed and why
- list the checks you ran (`python -m pytest tests/ -q --basetemp workspace/tmp/pytest-local`)
- mention any remaining limitations or follow-up work
- pull requests are accepted from day one and require maintainer review before merge

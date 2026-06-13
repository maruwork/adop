# ADOP Error Hardening Task Board

Status: Complete

- fix CLI import/runtime blockers
- remove non-generic checklist drift
- verify py_compile and CLI entry
- record blocker/residual status

## Execution Notes

- added `python/common.py` so `adop_cli.py` can import `fix_stdout_encoding`
- removed the `Beads`-specific current memo from the common checklist
- updated `README.md` to reflect roadmap/tasks/design shelves
- verified `adop_cli.py --version`
- verified `py_compile`

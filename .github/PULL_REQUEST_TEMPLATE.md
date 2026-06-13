## Summary

- what changed
- why it changed

## Verification

- [ ] `python shared/python/adop_cli.py --version` (standalone repo: `python/adop_cli.py`)
- [ ] `python -m py_compile shared/python/*.py` (standalone repo: `python/*.py`)
- [ ] `python -m pytest`

## Boundary Check

- [ ] generic ADOP and project-local overlay boundaries still hold
- [ ] public-facing docs remain repo-relative
- [ ] no generated cache directories are included

## Notes

List any remaining risks or follow-up work.

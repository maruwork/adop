# ADOP Genericization Task Board

Status: Complete

- map module responsibilities across:
  - `adop_cli.py`
  - `adop_artifacts.py`
  - `adop_validation.py`
  - `adop_summary.py`
  - `adop_types.py`
  - `adop_ids.py`
  - `adop_state_machine.py`
- define common authority vs project-local overlay boundary
- define what checklists own vs what templates own vs what project notes own
- audit python/checklist/template/readme surfaces for generic purity
- add explicit ADOP reading order and usage order
- add explicit verification path for generic ADOP
- record residual status

## Execution Notes

- added `ADOP_SHELF_CLASSIFICATION.md`
- added `docs/ADOP_GENERIC_QUICKSTART.md`
- expanded `README.md` with module responsibility map, boundary, and reading order
- updated checklist/template with explicit common-vs-project notes
- verified `adop_cli.py --version`
- verified `py_compile`
- verified bounded `lint` against `C:\tmp\adop-smoke`

# ADOP Genericization Design

Status: Complete

## Theme

`ADOP genericization`

## Scope

- generic authority surfaces
- project-local boundary clarification
- bounded verification

## Start Conditions

- `ADOP error hardening` is complete
- `ADOP ACI manual review` findings are recorded

## Shared Execution Rules

- readable locations:
  - `epo root`
  - `common/aci`
  - `common/refernce`
- writable locations:
  - `epo root`
  - `common/refernce`
- must not touch:
  - downstream project-local ADOP copies
  - current trial boards
  - project-local adoption registers
- required tools/commands:
  - `python -m py_compile python/*.py`
  - `python python/adop_cli.py --version`
  - bounded `quick-*` smoke flow against `C:\tmp\adop-smoke`

## AG-T1 Surface Responsibility Map

1. Task ID
   - `AG-T1`
2. Parent Theme
   - `ADOP genericization`
3. Parent Checkpoint
   - `AG-CP1 Surface Map Fixed`
4. Purpose
   - define the owner boundary of each ADOP shelf/module
5. Why This Task Is Needed
   - avoid hidden overlap between CLI, IO, validation, and summary ownership
6. Start Conditions
   - review findings are available
7. Input
   - current `python/*.py`, `README.md`, checklist/template files
8. Readable Locations
   - `python`
   - `checklists`
   - `templates`
   - `README.md`
9. Writable Locations
   - `README.md`
   - genericization records
10. Must Not Touch
   - project-local ADOP docs or runtime copies
11. Actions
   - map each module to one primary role
   - record checklist/template/README roles
12. Expected Output
   - explicit surface responsibility map
13. Acceptance Criteria
   - every file in `python/` has one primary role
   - checklist/template/README ownership is explicit
14. Failure Conditions
   - a file still implicitly owns multiple unrelated policy surfaces
15. Stop Conditions
   - responsibility split requires disruptive renames or moves
16. Send-Back Conditions
   - required ownership cannot be expressed without reopening boundary assumptions
17. Human Decision Gate
   - escalate only if a non-reversible rename/split becomes required
18. Evidence
   - updated docs
19. Record Destination
   - genericization records and README
20. Final Decider
   - `Codex B`

## AG-T2 Common-vs-Project Boundary Rule

1. Task ID
   - `AG-T2`
2. Parent Theme
   - `ADOP genericization`
3. Parent Checkpoint
   - `AG-CP2 Boundary Rules Fixed`
4. Purpose
   - define what common ADOP owns and what must remain project-local
5. Why This Task Is Needed
   - genericization fails if current-state or operator-flow authority stays in common
6. Start Conditions
   - `AG-T1` responsibility map exists
7. Input
   - review findings and current docs
8. Readable Locations
   - `README.md`
   - checklist/template files
   - `common/aci` examples when needed
9. Writable Locations
   - `README.md`
   - genericization records
10. Must Not Touch
   - project-local trial state docs
11. Actions
   - write explicit inclusion list for common authority
   - write explicit exclusion list for project-local overlay
   - reflect the rule in shelf docs
12. Expected Output
   - common-vs-project boundary rule
13. Acceptance Criteria
   - a new reader can tell where trial boards, operator flows, and landing targets belong
14. Failure Conditions
   - project-local authority still appears valid from common docs alone
15. Stop Conditions
   - clarification requires changing artifact schema semantics
16. Send-Back Conditions
   - compatibility risk cannot be resolved locally
17. Human Decision Gate
   - escalate only if ADOP’s product scope changes
18. Evidence
   - boundary wording in docs
19. Record Destination
   - genericization records and README
20. Final Decider
   - `Codex B`

## AG-T3 Generic Shelf Audit

1. Task ID
   - `AG-T3`
2. Parent Theme
   - `ADOP genericization`
3. Parent Checkpoint
   - `AG-CP3 Generic Shelf Audit Executed`
4. Purpose
   - inspect each surface for hidden project drift, wording drift, or ownership ambiguity
5. Why This Task Is Needed
   - latent non-generic content can survive if every surface is not explicitly reviewed
6. Start Conditions
   - `AG-T2` boundary rule exists
7. Input
   - all `epo root` files
8. Readable Locations
   - full `epo root`
9. Writable Locations
   - genericization records
10. Must Not Touch
   - downstream artifacts outside `epo root`
11. Actions
   - inspect python modules for hidden project assumptions
   - inspect checklist/template wording
   - inspect README for missing read/use order
12. Expected Output
   - per-surface audit findings or clearance
13. Acceptance Criteria
   - each shelf surface has an explicit audit judgment
14. Failure Conditions
   - any shelf remains unreviewed
15. Stop Conditions
   - audit requires reading outside approved common shelves
16. Send-Back Conditions
   - newly found blocker requires reopening error-hardening
17. Human Decision Gate
   - escalate only if a file is acting as project SSOT while appearing generic
18. Evidence
   - findings notes and changed docs
19. Record Destination
   - genericization records
20. Final Decider
   - `Codex B`

## AG-T4 Structure And Guidance Fix

1. Task ID
   - `AG-T4`
2. Parent Theme
   - `ADOP genericization`
3. Parent Checkpoint
   - `AG-CP4 Structure And Guidance Fixed`
4. Purpose
   - correct shelf guidance so another reader can use ADOP generically
5. Why This Task Is Needed
   - audited drift must be removed from the shelf, not just recorded
6. Start Conditions
   - `AG-T3` findings exist
7. Input
   - audit findings
8. Readable Locations
   - affected common ADOP docs/code
9. Writable Locations
   - affected common ADOP docs/code
10. Must Not Touch
   - external/public host settings
11. Actions
   - update README
   - update checklist/template wording
   - add missing boundary/read-order notes
12. Expected Output
   - corrected structure and guidance files
13. Acceptance Criteria
   - generic reader can identify purpose, ownership, and next read target
14. Failure Conditions
   - fixes still rely on operator memory
15. Stop Conditions
   - fix requires taxonomy rewrite beyond this wave
16. Send-Back Conditions
   - missing checkpoint/task coverage is discovered
17. Human Decision Gate
   - escalate only if a shelf move/rename becomes necessary
18. Evidence
   - updated files and verification output
19. Record Destination
   - common ADOP files and genericization records
20. Final Decider
   - `Codex B`

## AG-T5 Generic Read/Use/Verify Flow

1. Task ID
   - `AG-T5`
2. Parent Theme
   - `ADOP genericization`
3. Parent Checkpoint
   - `AG-CP5 Verification Recorded`
4. Purpose
   - make the generic read path, use path, and verification path executable by another reader
5. Why This Task Is Needed
   - a generic shelf is incomplete if use order exists only in the author’s head
6. Start Conditions
   - `AG-T4` fixes are applied
7. Input
   - current README/checklist/template/python surfaces
8. Readable Locations
   - `epo root`
9. Writable Locations
   - `README.md`
   - genericization records
10. Must Not Touch
   - downstream project copies
11. Actions
   - define read order
   - define usage order
   - define bounded verification path and commands
12. Expected Output
   - explicit read/use/verify flow
13. Acceptance Criteria
   - another reader can follow the documented flow to verify the shelf
14. Failure Conditions
   - verification still depends on unwritten assumptions
15. Stop Conditions
   - bounded verification requires unavailable external services
16. Send-Back Conditions
   - verification uncovers a new blocker
17. Human Decision Gate
   - escalate only if intended verification surface changes product scope
18. Evidence
   - command outputs and updated docs
19. Record Destination
   - genericization records and README
20. Final Decider
   - `Codex B`

## Result

- `README.md`, `ADOP_SHELF_CLASSIFICATION.md`, and `docs/ADOP_GENERIC_QUICKSTART.md` now carry the generic reading/use/verify surface
- checklist/template wording now points project-local execution details outward instead of keeping them in common authority
- residual status is `none`

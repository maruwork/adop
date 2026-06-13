# ADOP Private Host Bootstrap Design

Status: Complete

## Theme

`ADOP private host bootstrap`

## Scope

- private repository bootstrap only
- carried files and private-repository setup order
- pre-public verification order
- explicit hold line before public release

## Start Conditions

- `ADOP publication execution` is complete with repository-side preparation remaining
- host target is fixed as `fumimaruwork/adop`
- initial visibility is fixed as `private`

## Shared Execution Rules

- readable locations:
  - `epo root`
  - `common/refernce`
- writable locations:
  - `epo root`
  - `common/refernce`
- must not touch:
  - live public visibility
  - public announcement surfaces
  - downstream project-local overlays

## APHB-T1 Private Boundary

1. Task ID
   - `APHB-T1`
2. Parent Theme
   - `ADOP private host bootstrap`
3. Parent Checkpoint
   - `APHB-CP1 Private Boundary Fixed`
4. Purpose
   - separate private bootstrap from public-release actions
5. Why This Task Is Needed
   - the user explicitly does not want publication yet
6. Start Conditions
   - publication execution packet exists
7. Input
   - `PUBLICATION_RUNBOOK.md`
   - `REPO_EXPORT_GUIDE.md`
   - `OWNER_DECISION_PACKET.md`
8. Readable Locations
   - `epo root`
9. Writable Locations
   - bootstrap records
10. Must Not Touch
   - live repo visibility
11. Actions
   - identify private-only actions
   - identify public-release actions to exclude
12. Expected Output
   - private boundary rule
13. Acceptance Criteria
   - another operator can tell where private prep stops
14. Failure Conditions
   - public-release actions remain mixed into private bootstrap
15. Stop Conditions
   - private boundary depends on host operations already performed
16. Send-Back Conditions
   - publication execution docs are missing required host detail
17. Human Decision Gate
   - escalate only if visibility policy changes
18. Evidence
   - updated bootstrap docs
19. Record Destination
   - bootstrap records
20. Final Decider
   - `Codex B`

## APHB-T2 Private Carry Set

1. Task ID
   - `APHB-T2`
2. Parent Theme
   - `ADOP private host bootstrap`
3. Parent Checkpoint
   - `APHB-CP2 Carry Set Fixed`
4. Purpose
   - define the carried file set for the private repo
5. Why This Task Is Needed
   - host execution fails if carried files are ambiguous
6. Start Conditions
   - `APHB-T1` boundary rule exists
7. Input
   - `REPO_EXPORT_GUIDE.md`
   - `REPO_EXPORT_CHECKLIST.md`
8. Readable Locations
   - `epo root`
9. Writable Locations
   - export/bootstrap docs
10. Must Not Touch
   - live remote repo contents
11. Actions
   - define carried files for private repo
   - define internal-only files that stay behind
12. Expected Output
   - private carry set
13. Acceptance Criteria
   - another operator can prepare the private repo contents without guessing
14. Failure Conditions
   - carry set still conflicts with exclusions
15. Stop Conditions
   - carry set requires changing generic ADOP shelf structure
16. Send-Back Conditions
   - a public-only file is still required by private bootstrap
17. Human Decision Gate
   - escalate only if private repo scope expands beyond the current packet
18. Evidence
   - updated export/bootstrap docs
19. Record Destination
   - bootstrap records
20. Final Decider
   - `Codex B`

## APHB-T3 Private Repository Setup

1. Task ID
   - `APHB-T3`
2. Parent Theme
   - `ADOP private host bootstrap`
3. Parent Checkpoint
   - `APHB-CP3 Private Repository Setup Order Fixed`
4. Purpose
   - define the order of private repo creation and preparation
5. Why This Task Is Needed
   - host preparation should be executable without rediscovery
6. Start Conditions
   - `APHB-T2` carry set exists
7. Input
   - `PUBLICATION_RUNBOOK.md`
   - `OWNER_DECISION_PACKET.md`
8. Readable Locations
   - `epo root`
9. Writable Locations
   - runbook/bootstrap docs
10. Must Not Touch
   - live public release actions
11. Actions
   - define repo creation order
   - define file placement and license placement order
   - define draft promotion order for the private repo copy
12. Expected Output
   - private repository setup order
13. Acceptance Criteria
   - another operator can create the private repo and prepare it in order
14. Failure Conditions
   - setup order still depends on hidden host knowledge
15. Stop Conditions
   - setup order requires public release actions
16. Send-Back Conditions
   - required host step is missing from the packet
17. Human Decision Gate
   - escalate only if host target changes
18. Evidence
   - updated runbook/bootstrap docs
19. Record Destination
   - bootstrap records
20. Final Decider
   - `Codex B`

## APHB-T4 Private Verification

1. Task ID
   - `APHB-T4`
2. Parent Theme
   - `ADOP private host bootstrap`
3. Parent Checkpoint
   - `APHB-CP4 Private Verification Fixed`
4. Purpose
   - define the verification sequence before any public action
5. Why This Task Is Needed
   - the private repo still needs a reproducible acceptance path
6. Start Conditions
   - `APHB-T3` setup order exists
7. Input
   - `PUBLIC_VERIFICATION_CONTRACT.md`
   - `docs/ADOP_GENERIC_QUICKSTART.md`
8. Readable Locations
   - `epo root`
9. Writable Locations
   - verification/bootstrap docs
10. Must Not Touch
   - live CI systems
11. Actions
   - define the private verification order
   - define the pass condition before any public action
12. Expected Output
   - private verification order
13. Acceptance Criteria
   - another operator can verify the private repo candidate without guessing
14. Failure Conditions
   - verification still depends on monorepo-only assumptions
15. Stop Conditions
   - verification requires public repo state
16. Send-Back Conditions
   - host setup order and verification order disagree
17. Human Decision Gate
   - escalate only if private verification scope changes the chosen CI posture
18. Evidence
   - updated verification/bootstrap docs
19. Record Destination
   - bootstrap records
20. Final Decider
   - `Codex B`

## APHB-T5 Hold Line

1. Task ID
   - `APHB-T5`
2. Parent Theme
   - `ADOP private host bootstrap`
3. Parent Checkpoint
   - `APHB-CP5 Hold Point Fixed`
4. Purpose
   - define the explicit stop line before public release
5. Why This Task Is Needed
   - private prep must not accidentally roll into publication
6. Start Conditions
   - `APHB-T4` verification order exists
7. Input
   - all bootstrap outputs
8. Readable Locations
   - `epo root`
   - bootstrap records
9. Writable Locations
   - hold/bootstrap docs
10. Must Not Touch
   - public visibility
11. Actions
   - state the last allowed private step
   - state the first forbidden public step
12. Expected Output
   - explicit hold line
13. Acceptance Criteria
   - another operator can stop cleanly before publication
14. Failure Conditions
   - hold line still allows ambiguous public action
15. Stop Conditions
   - hold line requires actual repo creation to define
16. Send-Back Conditions
   - earlier bootstrap tasks are incomplete
17. Human Decision Gate
   - escalate only if the user changes the no-public rule
18. Evidence
   - updated hold/bootstrap docs
19. Record Destination
   - bootstrap records
20. Final Decider
   - `Codex B`

## Latest Result

- complete
- the design is sufficient for another operator to prepare `fumimaruwork/adop` in a private state and stop before public release

# ADOP Pre-Public Readiness Design

Status: Complete

## Theme

`ADOP pre-public readiness`

## Scope

- repository-facing public docs
- pre-public draft assets
- publishable-hold packet

## Start Conditions

- `ADOP genericization` is complete

## Shared Execution Rules

- readable locations:
  - `epo root`
  - `common/refernce`
- writable locations:
  - `epo root`
  - `common/refernce`
- must not touch:
  - downstream project-local ADOP copies
  - actual public repository settings
  - external hosting state
- required tools/commands:
  - bounded ADOP CLI verification
  - repo-relative wording checks inside `epo root`

## APR-T1 Public Surface Map

1. Task ID
   - `APR-T1`
2. Parent Theme
   - `ADOP pre-public readiness`
3. Parent Checkpoint
   - `APR-CP1 Public Surface Map Fixed`
4. Purpose
   - decide which docs are public-facing and which remain draft-only
5. Why This Task Is Needed
   - pre-public work drifts if public docs and draft docs are mixed
6. Start Conditions
   - genericization is complete
7. Input
   - current ADOP shelf structure
8. Readable Locations
   - `epo root`
9. Writable Locations
   - readiness records and `README.md`
10. Must Not Touch
   - external hosting state
11. Actions
   - define public-facing docs
   - define draft-only docs
   - define publishable-hold packet members
12. Expected Output
   - public surface map
13. Acceptance Criteria
   - every pre-public asset category is explicit
14. Failure Conditions
   - one doc remains ambiguous between public and draft
15. Stop Conditions
   - scope requires actual repo creation
16. Send-Back Conditions
   - genericization still leaves unresolved structure work
17. Human Decision Gate
   - escalate only if public scope changes ADOP’s intended audience
18. Evidence
   - mapped asset list
19. Record Destination
   - readiness records and README
20. Final Decider
   - `Codex B`

## APR-T2 Public Docs Pack

1. Task ID
   - `APR-T2`
2. Parent Theme
   - `ADOP pre-public readiness`
3. Parent Checkpoint
   - `APR-CP2 Public Docs Added`
4. Purpose
   - add repo-facing docs a third party would need before publication
5. Why This Task Is Needed
   - public-ready status is impossible if public docs do not exist
6. Start Conditions
   - `APR-T1` public surface map exists
7. Input
   - current README and genericization outputs
8. Readable Locations
   - `epo root`
9. Writable Locations
   - public-facing ADOP docs
10. Must Not Touch
   - actual remote repo settings
11. Actions
   - expand README/public guidance
   - add quickstart/evaluation/export docs as needed
   - ensure public commands and paths are repo-relative
12. Expected Output
   - public docs pack
13. Acceptance Criteria
   - a reader can understand purpose, trial, verification, and extraction path without monorepo-only context
14. Failure Conditions
   - docs still require implicit local knowledge
15. Stop Conditions
   - public docs require a live remote repo to make sense
16. Send-Back Conditions
   - docs reveal unresolved genericization work
17. Human Decision Gate
   - escalate only if public docs require product-scope change
18. Evidence
   - updated docs and repo-relative checks
19. Record Destination
   - readiness records and ADOP docs
20. Final Decider
   - `Codex B`

## APR-T3 Draft Asset Pack

1. Task ID
   - `APR-T3`
2. Parent Theme
   - `ADOP pre-public readiness`
3. Parent Checkpoint
   - `APR-CP3 Draft Assets Added`
4. Purpose
   - add draft-only decision/policy assets without implying publication has happened
5. Why This Task Is Needed
   - owner decisions should be prepared before go-live, but not silently assumed
6. Start Conditions
   - `APR-T1` public surface map exists
7. Input
   - current readiness docs
8. Readable Locations
   - `epo root`
9. Writable Locations
   - draft-only ADOP docs
10. Must Not Touch
   - live public policy or security intake
11. Actions
   - add pre-public decisions draft
   - add contributing/security/release drafts
   - mark them clearly as draft/pre-public
12. Expected Output
   - draft asset pack
13. Acceptance Criteria
   - no draft doc implies ADOP is already public
14. Failure Conditions
   - draft docs read as live public policy
15. Stop Conditions
   - draft asset requires real public contact details or remote setup
16. Send-Back Conditions
   - a missing public surface dependency is discovered
17. Human Decision Gate
   - escalate only if a draft asset would commit the owner to a public policy
18. Evidence
   - draft docs with explicit status
19. Record Destination
   - readiness records and ADOP docs
20. Final Decider
   - `Codex B`

## APR-T4 Publishable Hold Packet

1. Task ID
   - `APR-T4`
2. Parent Theme
   - `ADOP pre-public readiness`
3. Parent Checkpoint
   - `APR-CP4 Publishable Hold Fixed`
4. Purpose
   - collect owner-decision and hold-state artifacts in one place
5. Why This Task Is Needed
   - “ready to publish later” must be inspectable without rereading the whole shelf
6. Start Conditions
   - `APR-T2` and `APR-T3` are in place
7. Input
   - public docs and draft docs
8. Readable Locations
   - `epo root`
9. Writable Locations
   - publishable-hold packet docs
10. Must Not Touch
   - public repo settings
11. Actions
   - add owner decision packet
   - add publishable-hold checklist
   - add go-live sequence draft
12. Expected Output
   - publishable-hold packet
13. Acceptance Criteria
   - another reader can see exactly what remains before publication
14. Failure Conditions
   - owner decisions remain scattered
15. Stop Conditions
   - packet requires actual hosting operations
16. Send-Back Conditions
   - packet reveals missing public docs or draft docs
17. Human Decision Gate
   - escalate only if the remaining-decision set cannot be bounded
18. Evidence
   - packet docs
19. Record Destination
   - readiness records and ADOP docs
20. Final Decider
   - `Codex B`

## APR-T5 Decision-Only Residual Verification

1. Task ID
   - `APR-T5`
2. Parent Theme
   - `ADOP pre-public readiness`
3. Parent Checkpoint
   - `APR-CP5 Decision-Only Residual Confirmed`
4. Purpose
   - prove the shelf no longer needs structural refactor before publication
5. Why This Task Is Needed
   - pre-public readiness is invalid if hidden shelf work still remains
6. Start Conditions
   - `APR-T4` publishable-hold packet exists
7. Input
   - all readiness outputs
8. Readable Locations
   - `epo root`
   - readiness records
9. Writable Locations
   - readiness records
10. Must Not Touch
   - live public repo state
11. Actions
   - verify repo-relative public docs
   - verify draft docs remain draft
   - verify remaining work list is decision-only or repository-setup-only
12. Expected Output
   - residual judgment
13. Acceptance Criteria
   - no structural refactor remains
   - only owner/hosting work remains
14. Failure Conditions
   - a remaining item still requires shelf restructuring
15. Stop Conditions
   - verification requires a live public remote
16. Send-Back Conditions
   - public/draft assets are still incomplete
17. Human Decision Gate
   - escalate only if a remaining item cannot be classified as decision-only or repository-setup-only
18. Evidence
   - checklist result and summary
19. Record Destination
   - readiness summary
20. Final Decider
   - `Codex B`

## Result

- public-facing docs exist
- draft assets exist
- remaining work is limited to owner decision and host actions

# ADOP Publication Execution Design

Status: Complete

## Theme

`ADOP publication execution`

## Scope

- owner decision completion
- standalone repo export packet
- draft-to-public policy promotion rule
- public verification contract
- final publication runbook

## Start Conditions

- `ADOP pre-public readiness` is complete
- `OWNER_DECISION_PACKET.md`, `PUBLISHABLE_HOLD_CHECKLIST.md`, and `PUBLIC_GO_LIVE_SEQUENCE_DRAFT.md` exist

## Shared Execution Rules

- readable locations:
  - `epo root`
  - `common/refernce`
- writable locations:
  - `epo root`
  - `common/refernce`
- must not touch:
  - downstream project-local ADOP overlays
  - external repository host state
  - live remote configuration
- required evidence:
  - updated publication packet docs
  - verification notes
  - residual judgment

## APE-T1 Owner Decision Consolidation

1. Task ID
   - `APE-T1`
2. Parent Theme
   - `ADOP publication execution`
3. Parent Checkpoint
   - `APE-CP1 Owner Decision Set Fixed`
4. Purpose
   - gather every owner decision into one complete execution authority set
5. Why This Task Is Needed
   - publication fails if license, host, visibility, policy posture, or CI scope stay scattered
6. Start Conditions
   - pre-public readiness outputs exist
7. Input
   - `PRE_PUBLICATION_DECISIONS.md`
   - `OWNER_DECISION_PACKET.md`
   - `PUBLISHABLE_HOLD_CHECKLIST.md`
8. Readable Locations
   - `epo root`
9. Writable Locations
   - `OWNER_DECISION_PACKET.md`
   - `common/refernce/adop-publication-execution-*`
10. Must Not Touch
   - actual remote host settings
11. Actions
   - normalize every required owner decision into one packet
   - remove duplicated or drifting decision wording
   - mark which decisions are blocking and which are optional
12. Expected Output
   - complete owner decision set
13. Acceptance Criteria
   - another operator can see every required decision in one place
14. Failure Conditions
   - one required decision still lives only in a side document
15. Stop Conditions
   - a required decision cannot be expressed without changing ADOP product scope
16. Send-Back Conditions
   - missing pre-public docs are discovered
17. Human Decision Gate
   - escalate if owner decisions materially change intended audience or licensing posture
18. Evidence
   - updated owner decision packet
19. Record Destination
   - publication execution records
20. Final Decider
   - `Codex B`

## APE-T2 Standalone Export Packet

1. Task ID
   - `APE-T2`
2. Parent Theme
   - `ADOP publication execution`
3. Parent Checkpoint
   - `APE-CP2 Export Packet Fixed`
4. Purpose
   - define exactly what is carried into the standalone repo and what stays behind
5. Why This Task Is Needed
   - repo creation is error-prone if carried files, exclusions, and bootstrap order are implicit
6. Start Conditions
   - `APE-T1` owner decision set exists
7. Input
   - `REPO_EXPORT_GUIDE.md`
   - `REPO_EXPORT_CHECKLIST.md`
   - `README.md`
8. Readable Locations
   - `epo root`
9. Writable Locations
   - `REPO_EXPORT_GUIDE.md`
   - `REPO_EXPORT_CHECKLIST.md`
   - publication execution records
10. Must Not Touch
   - actual filesystem export outside `epo root`
11. Actions
   - define carried files
   - define excluded internal/process files
   - define bootstrap order and root layout
12. Expected Output
   - standalone export packet
13. Acceptance Criteria
   - another operator can export the repo without guessing what belongs
14. Failure Conditions
   - export still relies on monorepo-only implicit context
15. Stop Conditions
   - export packet requires creating the live repo to make sense
16. Send-Back Conditions
   - hidden genericization debt is found
17. Human Decision Gate
   - escalate if export boundaries conflict with owner decisions
18. Evidence
   - updated export docs
19. Record Destination
   - publication execution records
20. Final Decider
   - `Codex B`

## APE-T3 Policy Promotion Matrix

1. Task ID
   - `APE-T3`
2. Parent Theme
   - `ADOP publication execution`
3. Parent Checkpoint
   - `APE-CP3 Policy Promotion Rule Fixed`
4. Purpose
   - decide the public fate of each draft policy/process document
5. Why This Task Is Needed
   - publication is ambiguous if draft docs have no explicit promotion path
6. Start Conditions
   - `APE-T2` export packet exists
7. Input
   - `docs/publication/CONTRIBUTING_DRAFT.md`
   - `docs/publication/SECURITY_DRAFT.md`
   - `RELEASE_BOOTSTRAP_NOTES.md`
   - `PUBLIC_GO_LIVE_SEQUENCE_DRAFT.md`
8. Readable Locations
   - `epo root`
9. Writable Locations
   - draft policy docs
   - publication execution records
10. Must Not Touch
   - live public policy endpoints or contacts
11. Actions
   - mark each draft as promote-as-is, promote-with-edit, or keep-internal
   - record missing public-safe details
   - remove wording that would confuse another operator about publication state
12. Expected Output
   - policy promotion matrix
13. Acceptance Criteria
   - another operator can tell what to publish and what to keep internal
14. Failure Conditions
   - a draft doc still looks half-public and half-internal
15. Stop Conditions
   - promotion requires real host configuration
16. Send-Back Conditions
   - export packet lacks files needed for policy publication
17. Human Decision Gate
   - escalate if policy choice implies new legal or support obligations
18. Evidence
   - updated draft docs and matrix notes
19. Record Destination
   - publication execution records
20. Final Decider
   - `Codex B`

## APE-T4 Public Verification Contract

1. Task ID
   - `APE-T4`
2. Parent Theme
   - `ADOP publication execution`
3. Parent Checkpoint
   - `APE-CP4 Public Verification Scope Fixed`
4. Purpose
   - define the exact verification surface required before public release
5. Why This Task Is Needed
   - go-live is risky if verification commands and pass criteria depend on memory
6. Start Conditions
   - `APE-T3` policy promotion matrix exists
7. Input
   - quickstart docs
   - bounded smoke commands
   - repo export docs
8. Readable Locations
   - `epo root`
9. Writable Locations
   - public verification docs
   - publication execution records
10. Must Not Touch
   - external CI systems
11. Actions
   - fix the minimum verification command set
   - define pass/fail interpretation
   - define which checks are mandatory before publication
12. Expected Output
   - public verification contract
13. Acceptance Criteria
   - another operator can verify the publication candidate without asking the author
14. Failure Conditions
   - verification depends on unrecorded shell/environment assumptions
15. Stop Conditions
   - verification requires live remote resources
16. Send-Back Conditions
   - a required verification step exposes shelf inconsistency
17. Human Decision Gate
   - escalate if verification scope exceeds the agreed public CI posture
18. Evidence
   - updated verification docs
19. Record Destination
   - publication execution records
20. Final Decider
   - `Codex B`

## APE-T5 Publication Runbook

1. Task ID
   - `APE-T5`
2. Parent Theme
   - `ADOP publication execution`
3. Parent Checkpoint
   - `APE-CP5 Final Publication Runbook Fixed`
4. Purpose
   - assemble one ordered runbook that another operator can execute end to end
5. Why This Task Is Needed
   - the wave only succeeds if publication can happen without rediscovery
6. Start Conditions
   - `APE-T1` through `APE-T4` are complete
7. Input
   - owner decision set
   - export packet
   - policy promotion matrix
   - public verification contract
8. Readable Locations
   - `epo root`
   - publication execution records
9. Writable Locations
   - runbook docs
   - publication execution records
10. Must Not Touch
   - real remote repo or host
11. Actions
   - define exact action order
   - define stop points and rollback points
   - define handoff expectations
12. Expected Output
   - final publication runbook
13. Acceptance Criteria
   - another operator can execute publication in order from docs alone
14. Failure Conditions
   - runbook still requires unwritten judgment at key steps
15. Stop Conditions
   - runbook requires immediate real-world host operations
16. Send-Back Conditions
   - a prerequisite from earlier tasks is still ambiguous
17. Human Decision Gate
   - escalate if runbook reveals unresolved owner decisions
18. Evidence
   - final runbook
19. Record Destination
   - publication execution records
20. Final Decider
   - `Codex B`

## APE-T6 Closure Verification

1. Task ID
   - `APE-T6`
2. Parent Theme
   - `ADOP publication execution`
3. Parent Checkpoint
   - `APE-CP6 Execution-Ready Residual Confirmed`
4. Purpose
   - prove the wave ends with execution-ready residual only
5. Why This Task Is Needed
   - the wave is incomplete if hidden shelf work is still embedded in publication docs
6. Start Conditions
   - `APE-T5` runbook exists
7. Input
   - all publication execution outputs
8. Readable Locations
   - `epo root`
   - publication execution records
9. Writable Locations
   - publication execution summary
10. Must Not Touch
   - live public host state
11. Actions
   - review every remaining item
   - classify each item as execution-only, repository-setup-only, or owner-decision-only
   - confirm no shelf restructure remains
12. Expected Output
   - closure judgment
13. Acceptance Criteria
   - remaining work is explicit and external to shelf structure
14. Failure Conditions
   - a remaining item still needs common-shelf redesign
15. Stop Conditions
   - closure requires performing real-world publication
16. Send-Back Conditions
   - another task is shown incomplete
17. Human Decision Gate
   - escalate if any residual cannot be bounded clearly
18. Evidence
   - closure summary and residual list
19. Record Destination
   - publication execution summary
20. Final Decider
   - `Codex B`

## Closure

- publication execution packet is complete
- remaining work is bounded to owner decisions and real host execution

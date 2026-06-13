# Verification and Retry Policy

**Purpose**: Define how completion is proven and how repeated failure should be handled.

You only need to remember three things first:

1. use the strongest available evidence
2. when work can show change, prefer `negative proof -> positive proof`
3. after the same failure three times, stop using the same approach

## 1. Completion Requires Evidence

Do not claim completion without verification.

Use the strongest evidence that is reasonable for the task:

- tests for behavior
- lint or static checks for structure
- type checks or schema validation for contracts
- generated inventory for file topology
- screenshots or rendered output for visual work
- dry-run output for risky automation

Do not declare something correct based only on a single score, one benchmark run, an LLM judge, or one detector output.

When evaluation signals are used, separate at least:

- benchmark / judge / detector results
- read-only verification results on the live project
- hypotheses that remain unverified in production

When comparability matters, record tool name, version, dataset or gold set, threshold, and run count.

If the signal is unstable, probabilistic, or judge-dependent, prefer repeated runs to see a trend. Do not treat one good run as proof of success.

If no verification path exists, state that it is unverified and why.

When a benchmark, judge, or detector is used for decision-making, evidence may be recorded either through:

- `../templates/evaluation-verdict-template.md` when a reusable verdict artifact is needed
- direct writeback into a current / report / register surface using:
  - `strongest_evidence`
  - `verification_result`
  - `unresolved_risk`
  - `retry_change`
  - `writeback_destination`

## 2. Verification-First

For work such as behavior changes, bug fixes, or gate hardening, where before-and-after change can be shown, prefer **negative proof -> positive proof** when possible.

Examples:

- failing test -> passing test
- dry-run mismatch -> fixed dry-run
- lint violation -> clean result
- broken-reference report -> clean report

Do not force that pattern uniformly for:

- docs-only work
- config-only work
- regenerated projections
- read-heavy work such as inventory, classification, or archive preflight

This policy does not adopt test-first absolutism.  
It adopts **verification-first** and asks for the most reasonable negative proof that fits the work type.

## 3. Change Approach After Three Failures

Do not repeat the same failed move indefinitely.

After the same command, path, tool, or approach fails three times, stop and report:

- what was tried
- what failed
- what changed between attempts
- the best alternative
- whether human judgment is required

## 4. Change the Hypothesis

After failure, change at least one of the following:

- the diagnostic question
- the file or data source being investigated
- the tool or command
- the environment assumption
- the proposed fix

Repeating the same operation without a new hypothesis is not progress.

## 5. Roll Back When Needed

If the work path has accumulated too much confusion, return to the last known-good point and choose a cleaner approach.

Use version control, branch-local changes, logs, and generated reports to identify the rollback point concretely. Do not erase user changes or unrelated work.

## 6. Report Residual Risk

Results produced under this policy must leave at least these five items:

- `strongest_evidence`
  - what was the strongest verification evidence this time
- `verification_result`
  - whether the work passed, partially passed, or still failed
- `unresolved_risk`
  - what remains unverified or operationally uncertain
- `retry_change`
  - what changed after three failures, or what will change next
- `writeback_destination`
  - which task, current surface, packet, or register received the result

If those five items are missing, the work did not complete verification; it stopped at observation.

Verification does not mean zero risk. If coverage only proves part of the behavior, state the unverified area explicitly.
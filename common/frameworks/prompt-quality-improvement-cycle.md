# Prompt Quality Improvement Cycle

Shared improvement cycle for refining prompts and agent instructions through `investigate -> hypothesize -> revise -> remeasure` using failure logs and return patterns.

This framework supports the prompt and instruction improvement side of `project-progression-rule.md`, especially:

- `detect drift`
- `do not repeat the same failure`
- `return to stronger discipline after correction`

This framework is about the improvement cycle itself. It does not decide:

- which framework family to choose
- where the project's overall starting point lives
- how to read the PS-family frameworks as a whole

Framework-family selection belongs to `framework-selection-guide.md`.
PS-family framework navigation belongs to `ps-suite-guide.md`.

## 1. Purpose

- improve prompt quality from failure data rather than intuition
- keep `prompt improvement` separate from `process improvement`
- prioritize revisions and close the loop with measurement

## 2. Inputs

- review or audit return records
- failure taxonomy
- representative bad examples
- current prompt / instruction / checklist / workflow spec
- success metric

## 3. Core Loop

1. aggregate current failures
   - failure rate
   - concentrated step
   - recurring pattern
2. classify root causes
   - issue fixable by prompt structure
   - process-design issue
   - current-truth inconsistency
   - missing handoff contract
3. compare with external knowledge
   - reusable pattern
   - anti-pattern
   - alternative structure
4. prioritize revision candidates
   - expected effect
   - implementation cost
   - regression risk
5. apply revisions
   - wording
   - structure
   - gate
   - expectation contract
6. remeasure
   - failure rate
   - revision count
   - repeated explanation count
   - handoff loss

## 4. Decision Questions

- Is this a prompt problem or a workflow problem?
- Does the current output contract hand off cleanly to the next step?
- Should you add a gate, or improve the questions and expectation contract instead?
- Is a local fix enough, or does the framework itself need redesign?

## 5. Output Contract

Minimum output:

- baseline_failure_pattern
- root_causes
- adopted_changes
- rejected_changes
- expected_effect
- measurement_method
- success_threshold

## 6. Completion

One cycle may close when:

- revision reasons are recorded
- adopted and rejected changes are separated
- an effect-measurement method exists
- post-remeasurement improvement or non-improvement can be read

## 7. Portable Boundary

This document covers only the skeleton of the prompt-quality improvement cycle.  
Keep framework names, product names, and repo-specific event names in local sources unless they are intentionally portable.

<a id="automated-discovery-prompt-design"></a>
## 8. Discovery Prompt Design

Portable baseline framework for running discovery work in a way that both humans and AI can reproduce.

### 8.1 Purpose

- design discovery as a repeatable loop instead of a one-off brainstorm
- separate divergence, integration, verification, and rediscovery so each stage knows what to check

### 8.2 Core Loop

1. diverge
2. integrate
3. verify
4. rediscover

### 8.3 Prompt Guidance

- In divergence, fix the instruction to maximize volume without worrying about duplicates.
- In integration, ask for categories, parent concepts, and surviving differences.
- In verification, ask not only what is missing but also why it was missed.
- In rediscovery, avoid re-listing existing content and fill only the missing part.

### 8.4 Escalation Options

- tighten constraints
- change abstraction level
- force combinations

### 8.5 Completion Signal

- new categories almost stop appearing
- the integrated structure stabilizes
- additional viewpoints in verification shrink toward zero

<a id="prompt-question-set-design-framework"></a>
## 9. Prompt Question-Set Design

Shared framework for decomposing a complex investigation, design, or comparison task into an ordered question set.

### 9.1 Purpose

- avoid asking for the final answer all at once when the scope is large
- design the question structure before investigation starts
- make earlier answers feed later steps

### 9.2 Use Cases

- multi-option comparison
- root-cause investigation
- discovery of improvement options
- introduction plans or migration design
- revision of prompts or frameworks themselves

### 9.3 Design Rules

- split into roughly 3 to 7 questions
- make each answer usable by the next question
- do not mix `what do we want to know` with `what do we want to decide`
- make the last question return a recommendation, rationale, and remaining uncertainty

### 9.4 Recommended Question Order

1. what is the problem
2. what failures, gaps, or constraints exist
3. what external knowledge or alternatives exist
4. what should be adopted
5. how should it be measured and closed

### 9.5 Output Contract

- question_set
- intermediate_findings
- comparison_axes
- recommended_option
- why_recommended
- remaining_risks

<a id="token-optimization-baseline"></a>
## 10. Token Optimization Baseline

In AI-agent token optimization, do not confuse volume reduction with authority boundaries.

Priority order:

1. thin standard CLI output
2. avoid inflating the entry file
3. read boundary-first
4. use compact / plan discipline
5. do not let tools take over authority sources

Easy to adopt early:

- standard CLI output compression
- thin entry documents
- boundary discipline for search and reading
- compact / clear / plan operations

Easy to defer:

- items that add repo-external runtime or proxy layers
- items that create new authority surfaces
- items whose rollback is heavy

When judging completion, check:

- whether token reduction slowed current-canonical reading
- whether important error causes were hidden
- whether any tool started deciding authority, truth, state, or owner
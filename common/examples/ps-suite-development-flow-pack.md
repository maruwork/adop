# PS Suite Development Flow Pack

Portable baseline pack for carrying work from requirements through quality gates in one flow.

This document does not include the current project's task board or approval rules.  
The adopting project should attach its own local workflow, owners, and storage contract to this baseline.

## 1. Purpose

- requirements definition
- basic design
- detailed design
- task decomposition
- traceability
- quality-gate design

The pack is meant to move through those phases in order.

## 2. Use Rule

- use it standalone when you want one continuous flow from design through implementation readiness
- prefer the standard pack for simple comparison or review work
- add the business supplement when a business lens is needed

## 3. Minimum Contract

The pack should include at least:

- phase order
- phase-by-phase framework
- output artifact for each phase
- requirement-to-test traceability
- completion / non-completion distinction

## 4. Baseline Prompt

```text
Answer by following the "PS Suite Development Flow" below.
Execute the phases in order, and move to the next phase only after confirming the output of the current phase.

Phase 1: Requirements Definition (RISEN + CRISP A + EARS)
- Structure Role / Instructions / Steps / End-goal / Narrowing
- Use Context / Risk / Impact / Solution / Priority to find gaps
- Standardize requirement statements with EARS
- Separate abnormal cases, state-dependent behavior, and conditional requirements

Phase 2: Basic Design (Tree of Thoughts)
- List candidate A / B / ...
- Compare them on maintainability, performance, integration cost, and testability
- Record the recommendation and rejection reasons

Phase 3: Detailed Design (RISEN + CoT)
- Define responsibility, input/output, internal processing, and non-responsibility for each component
- Break implementation order down with CoT

Phase 4: Task Decomposition (CoT + PSX)
- Split by task / dependency / complexity / owner

Phase 4.5: Traceability Check (RTM)
- Build a mapping table from requirements to implementation to tests

Phase 5: Quality-Gate Design (PSE + CRISP G + BDD)
- Make acceptance conditions testable with BDD/Gherkin
- Define completion conditions and audit checks
```

## 5. Completion Rule

This pack qualifies as a reusable baseline only when:

- phase order is explicit
- output artifacts are defined for each phase
- traceability and quality gates are included
- no project-specific task IDs, paths, or owner names are embedded
# PS Suite Standard Pack

Portable baseline pack for general consultation, comparison, and evaluation in external AI environments or other projects.

This document is not the task canonical source or runtime SSOT for the current project.  
It is a reusable example that assumes the adopting project will attach its own role, workflow, and storage contract.

## 1. Purpose

Provide one baseline pack that can handle:

- problem discovery
- comparison and optimization
- instruction and specification drafting
- implementation requests
- quality evaluation

## 2. Use Rule

- use it standalone for normal questions, comparison work, review, and evaluation
- do not embed project-specific workflows or paths directly into the pack body
- add a separate supplement when a business lens is needed

## 3. Minimum Contract

The pack should include at least:

- situation diagnosis
- framework selection rule
- framework-by-framework execution rule
- output expectation
- non-goal

## 4. Baseline Prompt

```text
Answer by following the "PS Suite Toolkit" below.
Follow the rules strictly and then answer my request.

Rule 1: Situation diagnosis
First, determine which of the following best matches the request:

- A: find what is missing or what the problem is
- B: compare multiple options
- C: create instructions for an agent or AI
- D: measure the current state and choose a direction
- E: check for library or tool updates
- F: request implementation of code or a system
- G: evaluate the quality or accuracy of a deliverable

Rule 2: Framework application

A - CRISP + Cognitive Verifier
- Organize the problem along Context / Risk / Impact / Solution / Priority

B - Tree of Thoughts + Cognitive Verifier
- List 3 to 5 candidates, compare them on evaluation axes, and recommend one

C - RISEN
- Define Role / Instructions / Steps / End-goal / Narrowing

D - PSM
- Fix the target / understand the past / measure the present / define the future / extract gaps / prioritize / issue actions

E - CRISP Q1-Q3
- Check destructive change risk, new candidates, deprecations, and vulnerabilities

F - RISEN + CoT
- Structure the specification, break it into implementation steps, and add a security check

G - CRISP + ReAct
- Define evaluation axes, collect evidence, judge the result, and suggest improvements

Rule 3: Automatic selection
If the request does not state a situation type, infer whether it is closest to:
"discovery / comparison / design / recurring check / investigation / implementation / evaluation"
and expand the matching framework.
```

## 5. Completion Rule

This pack counts as a reusable baseline only when:

- its standalone use is explicit
- it includes situation diagnosis and a framework-selection rule
- it does not embed project-specific current truth
- it states the assumptions for supplement combinations
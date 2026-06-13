# PS Suite Business View Supplement

Portable supplement for adding a business lens to the standard pack or development-flow pack.

This document is not meant for standalone use.  
Use it only when you need to add business value, ROI, or stakeholder framing to a technical analysis.

## 1. Purpose

- add a business perspective to technically sound answers
- supplement business value, prioritization, and decision-maker framing

## 2. Combination Rule

- do not use it by itself
- append it after the `standard pack` or `development-flow pack`
- fill project KPI names and stakeholder names on the adopting project side

## 3. Baseline Prompt

```text
In addition to the pack above, always add a business perspective.

For every framework application, check at least the following:

- Who is this for?
- What is the business value?
- What is the rough ROI?
- What explanation is needed for competitors, market context, and decision-makers?
- Can you explain why this should be done now?

After the technical analysis, always add the following section:

## Business View Supplement

- Business value: [what improves]
- Expected ROI: [rough cost vs. effect estimate]
- Priority rationale: [why now]
- One-line summary for decision-makers: [executive summary]
```

## 4. Completion Rule

This supplement counts as reusable only when:

- it explicitly says not to use it standalone
- the business review lenses are listed
- the added output format is explicit
- no project-specific KPI or stakeholder names are embedded
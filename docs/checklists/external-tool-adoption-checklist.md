# External Tool Adoption Checklist

**When to use**: before trialing a new external tool, or when deciding whether to integrate an existing one into operations.
**What to replace**: tool name, adoption class, decision owner, trial procedure.
**Do not include**: the adoption note body, the current canonical state, or any project-specific current operations.

**Purpose**: a shared checklist for safely adopting external tools, trackers, memory helpers, or workflow assistants — as formal operations integration or creation assistance, not ad-hoc convenience use.

**What the shared shelf holds**: generic judgment criteria only.
**What goes on the project side**: current state, landing target authority, operator flow, project-specific trigger details.

## Supplement

Use this checklist when:
- trialing a new external tool for the first time
- beginning to use an existing external tool repeatedly
- deciding whether to promote from `creation assistance` to `operations integration`

## 1. Classify First

- decided whether this is `operations integration` or `creation assistance`
- can describe which harness layer to strengthen: `interface / mechanism / scaling`
- can describe which phase this belongs to: `core build / future extension / implementation / self-improvement loop`

## 2. For Operations Integration

- decided where it fits: trigger / hook / runbook / healthcheck / queue
- decided what will serve as authority
- explicitly stated what will not serve as authority
- decided fail-close / escalation / verification
- can trace from the current canonical surface to "in which scene this is used automatically or semi-automatically"

## 3. For Creation Assistance

- decided when to use it
- decided what it is used for
- explicitly stated that the tool's output itself is not SSOT
- decided what to write back into the repo canonical
- decided whether this is one-off or recurring use

## 4. Promotion on Recurring Use

- if recurring, decided which of the following to promote to: `workflow / checklist / skill / hook / runbook`
- if not promoting, can explain why stopping at one-off assistance
- has not left a state of "using it every time because it's convenient"

## 5. Current Judgment Memo

When leaving a current candidate reading, explicitly state the target project's current state and date.

- explicitly stated the current state of `operations integration` / `creation assistance`
- selected the layer to strengthen from `interface / mechanism / scaling`
- can write the current approved use scenes specific to the target project
- can write the current prohibited scenes specific to the target project
- has not written project-specific current canonical surfaces directly into the shared checklist body

## 6. Completion Artifact

When adopting an external tool, leave at least one of the following in the repo:

- adoption note
- trial board row
- workflow / runbook update
- checklist / template
- hook / healthcheck / queue integration

If no artifact is left, adoption is not considered complete.

## 7. Trial Lifecycle

- recorded which state the tool is in: `proposed / trial-ready / in-trial / promote / hold / reject`
- fixed `landing_target` as machine-readable and decided the writeback destination before starting the trial
- held executor / trigger / evaluation gate / decision owner / current state as machine-readable
- fixed the scene and evaluation criteria at trial start
- left artifact / observed effect / next action at trial close

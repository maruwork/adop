# Framework Selection Guide

This guide supports the helper-selection side of `project-progression-rule.md`, especially:

- `which entry surface to read from`
- `which reasoning model to apply to the next bounded move`

The responsibility of this guide ends at `choosing the framework family`.
The chosen framework's internals, execution order, handoff contract, and evidence rules belong to that framework's canonical source.

- For the PS-family framework overview and starting point, see `ps-suite-guide.md`
- For the prompt / instruction improvement loop, see `prompt-quality-improvement-cycle.md`

## Purpose

This guide helps a reader choose the right reasoning or prompting framework from the situation they are in.

It turns framework choice into a push-style classification step:

- first classify the situation
- then select the framework family
- then expand the actual prompt or workflow

## Situation Type Mapping

| Situation type | Typical use | Recommended framework |
|---|---|---|
| Discovery | finding missing pieces, root causes, gaps, or hidden problems | CRISP + Cognitive Verifier |
| Comparison | choosing among multiple options, tools, or architectures | Tree of Thoughts + Cognitive Verifier |
| Design | defining instructions, prompts, system behavior, or contracts | RISEN |
| Periodic review | measuring current state, checking direction, reviewing milestones | PSM |
| Research | checking recent information, trends, or external updates | CRISP (Q1-Q3) |
| Implementation | asking an agent to write code or produce implementation output | RISEN + CoT |
| Evaluation | checking quality, completeness, or output fitness | CRISP + ReAct |

## How To Use

1. Describe what you want to do.
2. Classify it into one of the situation types above.
3. Pick the corresponding framework.
4. Expand the actual question, prompt, or workflow using that framework.

If a project uses local names or local wrappers around these frameworks, map those names after classification. The classification step itself should stay portable.

## Output Contract

Record at least:

- selected_framework_family
- selected_framework
- selection_reason
- rejected_alternatives
- next_expansion_target

## Meta Prompt

```text
I am trying to do "{what I want to do or understand}".

First classify this into one of the following situation types:
A. Discovery (find what is missing or what is wrong)
B. Comparison (choose the best option among multiple options)
C. Design (decide how to build or instruct)
D. Periodic review (measure the current state and decide direction)
E. Research (learn recent information or technical trends)
F. Implementation (ask for code or implementation output)
G. Evaluation (measure quality, completeness, or fitness)

After classifying it, choose the matching framework and then structure the request with that framework before answering.
```

<a id="ui-framework-selection-baseline"></a>
## UI Framework Selection Baseline

When choosing a UI family, answer at least these questions first:

1. Is it a prototype, operator dashboard, embedded product UI, or standalone chat product?
2. Do you prioritize Python-first speed, React customization, no-code flow editing, or local-LLM hosting?
3. Is the primary value simple interaction, workflow orchestration, model comparison, or in-app task assistance?
4. Is the deployment local-only, self-hosted web, or product-embedded?

Selection baseline:

- if you want to ship the first shape fastest with Python only
  - Streamlit
- if you prioritize visual workflow orchestration
  - Dify / Flowise
- if you want to embed AI into an existing React surface
  - assistant-ui / CopilotKit
- if you want a standalone chat console
  - Lobe Chat
- if you want self-hosting with a local-model-first posture
  - Open WebUI / Text Generation WebUI

If a UI family is selected, record these in addition to the output contract above:

- selected_ui_family
- whether it is prototype-only or intended for long-term operation
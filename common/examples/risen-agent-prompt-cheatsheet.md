# RISEN Agent Prompt Cheatsheet

Minimal cheatsheet for building agent instructions with RISEN.

## RISEN

- `Role`
- `Instructions`
- `Steps`
- `Expectation`
- `Narrowing`

## Minimal Template

```text
# Role
You are [role name]. [Write the responsibility in one or two lines.]

# Instructions
[Write the core task this agent must complete in one or two sentences.]

# Steps
1. [Step 1]: [What to do]
2. [Step 2]: [Precondition: quote the output of Step 1 before starting] [What to do]
3. [Step 3]: [Precondition: quote the output of Step 2 before starting] [What to do]

# Expectation
- Required field 1: [description]
- Required field 2: [description]

# Narrowing
- [Prohibited item 1]
- [Prohibited item 2]
- Each step must start by quoting the prior step's output.
```

## Quick Rules

- write `Expectation` as the input contract for the next agent
- keep `Steps` between 3 and 7 items
- require citation of the previous step output so steps are not skipped
- make `Narrowing` objective and verifiable
- ban vague phrases such as `be careful`

## Good Output Example

- recommended_option
- evidence
- unresolved_risks
- next_action

## Use Boundary

This cheatsheet is a generic example for agent instructions. Do not include repository-specific task IDs or paths.
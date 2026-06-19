# ADOP Examples

A small, self-contained worked example so you can see what ADOP records look like
without scaffolding your own. It is **read-only sample data** — not this
repository's own adoption decisions.

## `walkthrough/`

One scene lane (`lint-ci`) evaluating `ruff`, driven through a full bounded cycle
and left on `hold`, plus one coupling snapshot. Seven artifacts under
`walkthrough/.adop/`:

| Artifact | Meaning |
|---|---|
| `candidate-intake-note` (ci-001) | the tool was proposed for one use case |
| `comparison-note` (cmp-001) | `ruff` selected over `pylint` for a bounded trial |
| `trial-packet` (tr-001) | the trial's scope, executor, and no-write boundary |
| `trial-result` + `judgment-report` (tr-001) | observed effect and the close decision |
| `hold-note` (hl-001) | trial paused (verdict: hold) with a reopen condition |
| `coupling-note` (cp-001) | where `ruff` is entangled in project files |

### View it

```bash
adop summary    --artifact-root examples/walkthrough/.adop
adop status     --artifact-root examples/walkthrough/.adop
adop couplings  --artifact-root examples/walkthrough/.adop
adop lint       --artifact-root examples/walkthrough/.adop
adop render-html --artifact-root examples/walkthrough/.adop --output workspace/html-preview/example.html
```

(Run from the repo root, or use `python shared/python/adop_cli.py …` if `adop`
is not installed as a command.)

To explore your own project instead, run `adop init` there — it creates a fresh
`.adop/` and overlay.

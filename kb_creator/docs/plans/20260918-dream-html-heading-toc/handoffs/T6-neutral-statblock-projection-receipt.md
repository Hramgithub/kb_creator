# T6 neutral statblock projection receipt

- Goal id: `20260918-dream-html-heading-toc`
- Step id: `T6-neutral-statblock-projection`
- Role: engineering assistance
- Repository-policy role / effort: `gpt-5.6-terra`, medium
- Orchestrator policy owner: main-chat `gpt-5.6-sol`, medium; ownership was not transferred
- Assignment state: completed; platform model/effort unverified
- Scoped override: user-directed removal of quote transport from reconstructed statblocks
- Timestamp: `2026-09-18T12:41:00+03:00`
- Elapsed time: approximately 32 minutes
- Token use: unavailable

## Scope and result

Implemented a scenario-neutral Stage-40 neutral statblock span transport. The
adapter now selects only sealed `kind=statblock` units, verifies each exact
sidecar line range, page containment, identity hash, and non-overlap, then
inserts paired plain Markdown markers:

`<!-- semantic-span-start: statblock; id: ... -->` / `<!-- semantic-span-end: statblock; id: ... -->`.

The renderer consumes only a matching marker pair and emits
`<section class="statblock-card" data-semantic-kind="statblock"
data-semantic-id="...">`. The statblock title and body stay ordinary Markdown
inside that range. Ordinary blockquotes remain quote/callout rendering; the
former quoted `semantic-kind` transport now fails closed. Adapter post-render
QA rejects quote/callout statblocks and requires the sealed semantic ID.

## Files changed

- `kb_creator/pipeline/publication_adapters.py`
- `kb_creator/tests/test_publication_html_adapter.py`
- `translator/translator.py`
- `translator/tests/test_recovery_support.py`
- this receipt

## Verification / evidence

- `compileall` passed for all four changed Python files.
- Two focused renderer unit tests passed through `unittest`: neutral plain-span
  rendering and missing/mismatched marker rejection.
- Adapter positive smoke passed using its authority fixture: sealed plain
  Markdown span produces the expected paired transport and neutral semantic
  container evidence.
- `git diff --check` passed.

## Blockers and next action

- Full pytest suite remains unavailable in this Python environment because
  pytest is not installed. No broader acceptance is claimed.
- The upstream reconstruction successor still has to author statblock title and
  body spans in its sealed semantic sidecar before a real Dream candidate can
  use this Stage-40 path. This task did not alter that authority.
- Next: run focused pytest/renderer and adapter suites in the project test
  environment, then let the orchestrator integrate only verified results.

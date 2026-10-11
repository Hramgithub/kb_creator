# T4 adapter engineering receipt

- Goal id: `20260918-dream-html-heading-toc`
- Step id: `T4-adapter-engineering`
- Role: engineering assistance
- Repository-policy role / effort: `gpt-5.6-terra`, medium
- Orchestrator policy owner: main-chat `gpt-5.6-sol`, medium; ownership was not transferred
- Assignment state: completed; platform model/effort unverified
- Scoped override: none
- Timestamp: `2026-09-18T12:18:00+03:00`
- Elapsed time: approximately 56 minutes
- Token use: unavailable

## Scope

Implemented only the KB Creator HTML adapter/config readiness boundary, contract
author/preflight lifecycle recognition, and focused adapter tests. Did not edit
the Translator renderer, scenario data, generated output, accepted authority,
canonical plan/status, or Git history.

## Result

- Added closed `kb_creator.html_publication_policy.v1` lifecycle handling:
  `deferred` is a legal closed source state but is rejected by Stage 40;
  `stage40_ready` requires declared page roles, cover, credits, TOC
  origin/source page/explicit entry-to-target mappings, body start, and flow.
- Stage 40 compares all declared role pages to exact accepted-MASTER page
  markers; it does not infer authority from localized titles.
- The adapter emits one resolved top-level `frontmatter_policy` with page map,
  TOC mappings, credits, order, body start, and expected flow, then derives
  legacy renderer fields from it for compatibility.
- Added manifest/DOM closure gates for TOC origin, source page, entry count,
  visible-entry conservation, exact link order, unique real target IDs,
  credits, body start, and frontmatter flow.
- Changed semantic statblock projection to `> <!-- semantic-kind: statblock -->`.
  Adapter QA now requires neutral `section`/`div.statblock-card` with
  `data-semantic-kind="statblock"` and rejects quote/callout statblock DOM.

## Files changed

- `kb_creator/pipeline/publication.py`
- `kb_creator/pipeline/publication_adapters.py`
- `kb_creator/tests/test_publication_html_adapter.py`
- this receipt

## Files checked

- Active plan/context and R1/R2/R3 receipts under this goal.
- `AGENTS.md`, existing publication contract author/preflight paths, adapter,
  adapter tests, current renderer frontmatter resolver, and current dirty-tree
  boundaries.

## Verification / evidence

- Python `compileall` passed for the three changed Python files.
- Focused direct smoke passed: a production-shaped four-page policy normalized
  to the resolved policy and accepted a matching source-TOC manifest/DOM.
- `git diff --check` passed.
- Added positive source-TOC closure coverage and negatives for missing,
  deferred, and unmapped source-TOC policy plus obsolete quote-styled
  statblocks.

## Blockers / risks

- Focused pytest suite could not run because both available Python launchers
  lack pytest (`python` absent; bundled Python reports `No module named pytest`).
- Renderer integration remains owned by the renderer contributor: it must
  consume the exact resolved `frontmatter_policy` extension and render the
  agreed `semantic-kind: statblock` directive as a neutral container. Until
  that lands, an end-to-end Stage-40 run is intentionally not claimed.
- Existing source configs must receive an explicit successor configuration;
  their old identity-bound placeholders correctly fail Stage 40.

## Next action

Renderer owner integrates the agreed resolved-policy and typed-statblock
transport, then rerun `kb_creator/tests/test_publication_html_adapter.py` and
the directly dependent renderer/control-plane suites in an environment with
pytest. Orchestrator integrates results without treating this implementation as
HTML acceptance, release, or a commit authorization.

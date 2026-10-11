# Engineer receipt: HTML stage asset locality fix

- Goal id: `20260914-dissociation-publication`
- Step id: `html_stage_asset_locality_fix`
- Role: engineering contributor
- Model: `gpt-5.6-sol`
- Effort: `high`
- Orchestrator policy owner: `gpt-5.6-sol` at `medium`
- Assignment state: `user-overridden`
- Scoped override: engineering contributor uses `gpt-5.6-sol` at `high` for this bounded fix
- Timestamp: `2026-09-15T20:50:13+03:00`
- Elapsed time: unavailable
- Token use: unavailable

## Scope

Diagnose and fix the generic publication HTML adapter so a renderer cannot leave
local asset references escaping the HTML stage. Preserve the accepted
`MASTER_RU` plus accepted ArtView gate. Do not run live publication or MinerU,
and do not edit canonical plan, context, or project status.

## Result

Pass. The renderer previously received the accepted Stage 21 `MASTER_RU.md`
directly. Its existing image renderer correctly resolved Markdown image paths
relative to that file, then emitted paths from the Stage 40 HTML back to Stage
21. Copying Stage 31 assets into Stage 40 did not change those references.

The adapter now validates the sealed ArtView application and its exact accepted
decision, acceptance, candidate-manifest, `MASTER_RU`, asset-manifest,
reader-projection, effective-config, and projected-asset identity graph before
writing. It maps each accepted current ArtView row to the `MASTER_RU` asset
manifest by exact byte count and SHA-256, rejects ambiguous identity mappings,
and renders from a derived stage-local Markdown projection. Included assets are
copied only from the application-bound Stage 31 inventory and references are
rebased to Stage 40; accepted exclusions remove their image line. Unsafe,
missing, stale, colliding, escaping, and reparse paths fail closed.

## Files changed

- `kb_creator/pipeline/publication_adapters.py`
- `kb_creator/tests/test_publication_html_adapter.py`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_html_stage_asset_locality_fix_20260915.md`

Existing concurrent changes in `publication_adapters.py`, including Stage 30
asset-graph materialization, were preserved.

## Files checked

- `translator/translator.py`
- Run 07 accepted `MASTER_RU.md` and `ASSET_MANIFEST.json`
- Run 07 ArtView `candidate_manifest.json`, accepted decisions,
  `ARTVIEW_APPLIED.json`, `reader_projection.json`, and
  `effective_visual_config.json`
- Publication registry/control-plane tests

## Verification

- `test_publication_html_adapter.py`, `test_publication_registry_e2e.py`, and
  `test_publication_control_plane.py`: `51 passed in 94.32s`
- Python bytecode compile for the adapter and focused test: pass
- Repository `git diff --check`: pass
- Read-only Run 07 authority probe with temporary output: two references
  rebased, two exact assets materialized, no Stage 21 escape in the derived
  Markdown
- Live publication and MinerU: not run

## Blockers and next action

- Blockers: none
- Next action: orchestrator integrates the change, obtains independent
  implementation review, then performs the governed HTML-stage recovery or
  rebuild for Run 07.

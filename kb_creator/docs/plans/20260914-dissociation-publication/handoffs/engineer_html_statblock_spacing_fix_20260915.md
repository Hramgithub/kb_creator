# Engineer receipt: HTML stat-block heading and spacing fix

- Goal id: `20260914-dissociation-publication`
- Step id: `html_statblock_spacing_fix`
- Role: engineering contributor
- Model: `gpt-5.6-sol`
- Effort: `high`
- Orchestrator policy owner: `gpt-5.6-sol` at `medium`
- Assignment state: `user-overridden`
- Scoped override: engineering contributor uses `gpt-5.6-sol` at `high` for this bounded fix
- Timestamp: `2026-09-15T22:00:36+03:00`
- Elapsed time: unavailable
- Token use: unavailable

## Scope

Diagnose and fix the scenario-neutral HTML pipeline defect exposed by the
Dissociation run11 terminal stat block. Change only reusable adapter, renderer,
tests, and this receipt. Do not edit run11 artifacts, create or resume a
publication run, record acceptance, or edit canonical plan/context/status.

## Result

Pass. Run11's accepted derived Markdown preserves a compact terminal stat block
as one heading followed immediately by eleven lines, ten of which use Markdown
hard breaks. The Stage 40 report records `statblock_cards: 0`; the renderer
therefore emitted the heading both in the generated TOC and in the body, then
collapsed the hard-broken lines into an ordinary body paragraph.

The HTML adapter now detects only structurally terminal, numeric, densely
hard-broken heading sections. It derives the exact renderer heading id without
scenario vocabulary, merges it into the existing `statblock_section_policy`,
and records the detected ids in the adapter receipt. The existing renderer then
excludes that heading from the generated TOC and wraps the body occurrence once
in `statblock-card`. The renderer now preserves Markdown hard breaks as `<br>`
and applies compact stat-block line height and paragraph margins. A hard-broken
ordinary section followed by more prose is explicitly left unclassified.

## Files changed

- `kb_creator/pipeline/publication_adapters.py`
  - SHA-256: `C21EBC8918CF32646D0BC7EB76D0C9B4D0C304C7549846C16E6AE768427812EB`
- `translator/translator.py`
  - SHA-256: `9CF57E4CE194E05B7CA64488DD3AB5AA60A9F57A96BDEE80D96F6C93C71BF8D8`
- `kb_creator/tests/test_publication_html_adapter.py`
  - SHA-256: `A9D11A8E366F5CC35FAB8EF8DA7D94174C6621578DBB3978053FF5B738A852C2`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_html_statblock_spacing_fix_20260915.md`
  - This immutable receipt is not self-hashed.

The adapter and focused test already contained concurrent Stage 30/40 asset
locality changes when this task started. Those edits were preserved and not
reverted.

## Verification

- Read-only run11 detector probe:
  `['soprotivlenie-lyudei-politseiskie-ispytuemye-zhiteli-aniaka']`
- Generic integration fixture renders exactly one visible Cyrillic stat-block
  heading, one `statblock-card`, preserved `<br>` elements, `line-height: 1.12`,
  compact paragraph margins, and two occurrences of the ordinary Notes heading
  (TOC plus body), proving the non-statblock control remains unchanged.
- `test_publication_html_adapter.py`, `test_publication_registry_e2e.py`, and
  `test_publication_control_plane.py`: `52 passed in 93.08s`.
- Focused post-adjustment rerun of `test_publication_html_adapter.py`:
  `10 passed in 1.82s`.
- Python bytecode compile for adapter, renderer, and focused test: pass.
- Repository `git diff --check` for changed code/tests: pass.
- Publication runs, acceptance recording, browser, and generated run11 writes:
  not performed.

## Blockers and next action

- Blockers: none.
- Next action: orchestrator obtains independent implementation review, then
  performs the governed recovery/rebuild of the HTML stage and visual review of
  the new candidate.

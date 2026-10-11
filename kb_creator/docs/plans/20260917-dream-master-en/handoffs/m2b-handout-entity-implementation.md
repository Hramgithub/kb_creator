# M2b numbered-handout entity implementation receipt

- Goal: `20260917-dream-master-en`; milestone: `M2b`.
- Scope: generic, structural-mode-only caption evidence for the existing
  `numbered_player_handouts` closure check.
- Result: `IMPLEMENTED_AND_VERIFIED`.
- Orchestrator policy owner: `gpt-5.6-sol`, medium.
- Assignment: engineering implementation, `gpt-5.6-terra`, medium; assignment
  state `completed`; orchestration ownership remains with the main chat.
- Scoped override: none.
- Timestamp: `2026-09-18T00:00:00+03:00`.
- Elapsed time: approximately 25 minutes.
- Token use: approximately 11k tokens.

## Changed files and result

- `kb_creator/pipeline/reconstruction_promotion.py`
  - preserves the legacy heading and explicit handout-asset evidence paths;
  - adds a strict visible-caption extractor that operates only after structural
    v2/v4 authority and sidecar validation, on `kind: handout` Markdown spans;
  - applies the shared `semantic_structure.apply_block_boundaries` transform
    before interpreting the reviewed one-based coordinates;
  - supports only the closed caption grammar (optional Figure/Fig. prefix,
    optional Player, Handout number, and closed suffix); and
  - fails closed for invalid spans and multiple distinct captions in one
    handout span, retaining the contract's exact range comparison.
- `kb_creator/tests/test_reconstruction_promotion.py`
  - adds span-bound caption, figure-number disambiguation, nested quote/ATX,
    duplicate, prose/metadata rejection, ambiguity, and compact-boundary
    coordinate regression coverage.

No Dream literal, source/candidate edit, `working/**` write, materialization,
or reconstruction acceptance record was made.

## Verification/evidence

- Bundled Python `py_compile` passed for both changed Python files.
- Targeted promotion suite with the repository test dependencies passed:
  `19 passed, 1 skipped`; two known stale live Dissociation fixture tests were
  excluded as directed because their producer closure has drifted.
- `git diff --check` passed for both implementation/test files.
- Read-only Dream replay-16 preflight passed:
  `promotion_preflight_passed`, replay-v2 run identity
  `D80F35D17285D77E319A5E4B16A4F1207CE5415608ED95D56CE050B729A1BA98`,
  candidate inventory
  `609657AA11554918A67A9955C7D5DCD3554A5E4B65A4E2305C556F3851D4D9A3`.

## Next action

The generic promotion boundary is now ready for the orchestrator's materialize
and explicit-acceptance sequence. Preserve this reusable implementation/test
pair in the future commit scope; continue excluding generated `working/**`
artifacts.

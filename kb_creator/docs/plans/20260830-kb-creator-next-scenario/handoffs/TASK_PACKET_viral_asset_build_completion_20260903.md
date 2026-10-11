# Finish canonical v2 asset materialization

- Goal 20260830-kb-creator-next-scenario; nri-engineer Terra/medium.
- Exclusive scope: build_scenario_master_en.py, verify_scenario_master_en.py
  and their two tests. Root owns orchestration/build; author owned separately
  by merge_metadata_guards, review UI by typed_renderer_fidelity.
- Concrete implementation: admit canonical asset placement/anchor fields in
  closed schema while validating immutable provenance fields independently;
  replace unconditional canonical-reader rejection with actual placement/event
  validation. Author owner will provide placement/anchor and asset events.
- Materialize 9 canonical binary:null full-page recipes using existing Poppler
  renderer into private staging before serializing resolved asset paths. Keep
  config immutable; exact output binary identities belong in candidate manifest.
  Independent verifier checks generated binaries/recipe/page/dimensions and
  all placements. Preserve legacy fixture/v1 behavior and negative tests.
- Fix real integration errors in owned serializers discovered with new author,
  preserving source content and no bypasses. Coordinate schema directly with
  the author and QA engineers. No author edits, new design, baseline-only report,
  source/frozen mutation, manual asset ledger, canonical candidate build or Git.
- Read PDF skill before rendering. You are not alone; preserve others' edits.
- Run two owned test modules with captured result. Receipt:
  terra_viral_asset_build_completion_20260903.md, including changes, tests,
  exact remaining errors, elapsed/tokens or unavailable.

# Viral remediation v2 candidate materializer continuation

- Goal: `20260830-kb-creator-next-scenario`
- Step: `7-user-review-remediation-v2-materializer`
- Owner: same `nri-engineer`, `gpt-5.6-terra` / `medium`
- Prior receipt: `terra_engineering_viral_user_review_remediation_slice3_20260902.md`
- Completion token: `READY_FOR_V2_OUTPUT_VERIFIER`

## Objective

Complete the v2 candidate-producing route in the builder. The existing v2
schema/preflight seam must become an absent-root atomic materializer for a
synthetic but fully representative v2 fixture. This continuation does not edit
the verifier or real Viral policy/evidence.

You are not alone in the worktree. Preserve all prior changes and do not revert
or clean any path.

## Exclusive ownership

- `kb_creator/scripts/build_scenario_master_en.py`
- `kb_creator/tests/test_build_scenario_master_en.py`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_user_review_remediation_v2_materializer_20260903.md`

No other file may be modified.

## Required behavior

Implement the architecture receipt's complete v2 materialization side:

- `build_candidate()` routes v2 without weakening the sealed v1 route;
- absent target, private staging and atomic rename semantics;
- typed source-ordered graph materializes reader Markdown, provenance,
  inventory and declared topology without owner-end dumping;
- exact source fragment/range identity is retained in provenance;
- parent heading opens at the first descendant and anchor-only/run-in entries
  never enter outline;
- canonical serializers cover tables, callouts, ordered-list callouts,
  equipment cards, creature statblocks, full-page maps and physical page pairs;
- asset copies/placements obey exact event bindings, reader-value suppression,
  duplication resolution and quality stage;
- `source_backed_recovery` and generated-navigation provenance are explicit;
- audit=124/reader=122/excluded=2 remains declarative and pages 123--124 leak
  no reader content/assets;
- metrics/inventory are recomputed from output, not Viral constants;
- no acceptance sidecar is produced.

Create comprehensive synthetic tests covering successful output and mutations
for order, container termination, title drift, table rows/cells, anchor-only
outline pollution, asset placement/suppression, fragment identity, excluded
page leakage, determinism and atomic absent-root behavior. Retain all v1 tests.

## Forbidden

Do not edit verifier files, configs/evidence/source/reconstruction/candidates,
build the real Viral target, extract XObjects, run Step 8A, stage/commit/push or
touch unrelated dirty paths.

## Evidence

Run the builder test module and `py_compile`; include all counts/results and an
exact changed-path list in the immutable receipt. Return the completion token
only when a representative v2 candidate can be built and its output assertions
pass. Otherwise identify the remaining builder-only gap.

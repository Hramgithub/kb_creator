# Viral v2 typed-chunk ledger fresh-engineer retry

- Goal: `20260830-kb-creator-next-scenario`
- Step: `7-user-review-remediation-builder-typed-chunk-ledger-retry`
- Owner: fresh `nri-engineer`, repository profile `gpt-5.6-terra` / `medium`
- Superseded incomplete receipt: `terra_engineering_viral_user_review_remediation_builder_typed_chunk_ledger_20260903.md`
- Authoritative algorithm packet: `sol_orchestrator_viral_user_review_remediation_builder_typed_chunk_ledger_20260903.md`
- Completion token: `READY_TO_RESUME_V2_VERIFIER_SEMANTIC_GATES`

## Objective

Implement, not merely restate, the complete typed-chunk composition and final
event ledger specified in the authoritative algorithm packet. Start from the
current shared worktree, which already contains all preceding v2 builder and
verifier work.

You are not alone in the worktree. The prior engineer is finished and must not
touch these paths. Preserve every existing edit; never revert or clean.

## Exclusive ownership

- `kb_creator/scripts/build_scenario_master_en.py`
- `kb_creator/tests/test_build_scenario_master_en.py`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_user_review_remediation_builder_typed_chunk_ledger_retry_20260903.md`

## Requirements

Read the full authoritative algorithm packet and architecture receipt. Replace
the string-first v2 materializer with typed top-level/nested chunks, asset
relocation by chunk/list operation, one final join, join-time char/UTF-8 byte
range accumulation, and provenance generated only from that ledger. Cover
plain/repeated text, structured `contains`, before/after/inside reader assets,
suppressed assets, exact slice hashes, overlap rules, two-root determinism,
blank-run and literal preservation.

Do not use first-occurrence search over finished Markdown. Do not touch verifier,
configs, evidence, source/reconstruction, real candidates, Git or Step 8A.

Run the full builder test module and `py_compile`. Write the new immutable retry
receipt with exact changed paths, results and any concrete blocker. Return the
completion token only when the ledger is actually implemented and tested.

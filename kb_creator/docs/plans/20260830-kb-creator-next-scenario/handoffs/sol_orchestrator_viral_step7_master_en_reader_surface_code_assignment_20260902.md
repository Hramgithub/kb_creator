# Viral Step 7 — reader-surface code assignment

## Ownership

- Contributor: `nri-engineer`, `gpt-5.6-terra`, medium.
- Orchestrator remains the main chat; this packet does not transfer integration or release authority.
- Other work may be present in the checkout. Do not revert, rewrite, stage, commit, or clean unrelated changes.

## Frozen inputs

- Worktree: `D:\NRI\.worktrees\kb-creator-viral`.
- Publication config: `kb_creator/working/viral/master_en/publication_config_v1.json`, SHA-256 `852101DCA3D64A1D510CCC96A5BB2806B5BE21C9D5674E7729164E85C265B8E4`, 706382 bytes.
- Accepted reconstruction: `kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4`, inventory SHA-256 `68C17FB765A89C6146398868E61F1F6EB7B2FE4EAFBA8C2C2C8F42260BBDBA83`.
- Architecture: `sol_architect_viral_step7_master_en_reader_surface_remediation_20260902.md`, corrected by the asset-count, reader-alt-ordinal, and suppression errata in the same handoff directory.
- Config audit: 25 semantic fragments, 22 suppressions, all stored hashes/owners valid; p55 structure/note bindings are already closed. Do not modify config.

## Write scope

Only:

1. `kb_creator/scripts/build_scenario_master_en.py`
2. `kb_creator/scripts/verify_scenario_master_en.py`
3. `kb_creator/tests/test_build_scenario_master_en.py`
4. `kb_creator/tests/test_verify_scenario_master_en.py`
5. One receipt: `terra_engineering_viral_step7_master_en_reader_surface_code_20260902.md`

Everything else is read-only. In particular: source PDF, accepted reconstruction, publication config, Candidate A/B, plan/context/status files, candidate C, Git index/history, MASTER_RU and downstream outputs.

## Required implementation

Implement the architecture's closed `reader_surface` contract in production code, using reusable deterministic functions rather than Viral-only output patches.

- Extend top-level and nested closed-schema validation. Unknown keys must fail at every new nesting level. Validate exact production counts 25/22/107 and all selector field combinations.
- Resolve semantic ranges from immutable LF-normalized page bodies. Prove once-only selector resolution, raw SHA-256, owner, order, non-overlap and exact relationship to the normal binding claims before rendering.
- Apply only the 22 exact authorized suppressions. Zero/multiple/partial/overlapping matches, wrong owner/hash/replacement, or `authorial_text_affected:true` must fail. Preserve suppression text/hash evidence in sidecars and conservation accounting.
- Replace the global source-heading increment with the declared owner-local algorithm: generated owner level stays declared; retained source subtrees preserve relative depth beginning at owner+1; overflow and exact generated-label duplicates become deterministic strong labels; no source H1/H2 or source level <= owner remains.
- Enforce the 107 reader-alt contract and policy before emission; evidence-only assets are not reader ordinals.
- Add reader-surface fragment/suppression/heading/alt outcomes to provenance/QA sidecars so the verifier can independently recompute them from config, accepted pages and candidate output.
- The verifier must not import builder internals. It must independently reject semantic owner/order/hash failures, unauthorized or incomplete suppressions, heading violations, bad/empty/provenance alts, sidecar mismatches and reader-description leakage.
- Preserve the accepted reconstruction, asset bytes, public link targets, existing structured/xref semantics and candidate topology.

## Focused tests

Amend only the two existing test modules. Keep the suite compact and behavior-oriented; do not create a large mutation matrix.

- Small generic page fixtures for prefix/suffix semantic splits and exact suppression.
- Closed-schema/selector failures, wrong/missing/duplicate/overlap/order/owner/hash cases.
- Alt-policy positive and negative cases.
- Owner levels L2–L5, preserved relative depth, duplicate label, H6 boundary and strong-label overflow.
- Content-aware regressions for p8, p55, p68, p46, one provenance alt, and representative map/pregen/merchandise/back-cover heading cases.
- Full-config assertions for 168/25/22/107 and declared dependency bindings.
- Verifier-side independent rejection tests.

Run only the two focused test files plus `py_compile` and `git diff --check` for owned files. Do not run MinerU or the historical 371/119/490 suites. Do not build Candidate C or any production candidate.

## Receipt

Record exact changed files and SHA-256 values, commands/results, compact coverage mapping, unresolved risks, and one of `PASS_IMPLEMENTATION` or `BLOCKED_IMPLEMENTATION`. A passing receipt does not authorize a candidate build; independent GPT-5.5/high implementation review follows.

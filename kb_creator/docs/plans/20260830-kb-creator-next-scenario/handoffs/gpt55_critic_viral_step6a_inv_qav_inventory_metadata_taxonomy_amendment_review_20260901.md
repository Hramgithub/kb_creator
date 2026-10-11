# Independent critic review: Viral Step 6A INV/QAV inventory-metadata taxonomy amendment

- Goal: `20260830-kb-creator-next-scenario`
- Step: `6A-INV-QAV-inventory-metadata-taxonomy-amendment`
- Review kind: `architecture`
- Candidate status: immutable architecture amendment, not a frozen release candidate.
- Verdict: `ACCEPT`
- Recommendation: implementation-ready for the bounded Terra QAV-D2 batch after the orchestrator binds this receipt hash.
- Critic role policy: `gpt-5.5` / `high`
- Actual platform model / effort: `unavailable`; repository policy does not prove platform selection.
- Implemented or materially designed by this critic: no.
- QA ownership by this critic: none.
- Orchestrator policy owner: main chat `gpt-5.6-sol` / `medium`; this review does not transfer orchestration, canonical-state, integration, stop/ask, release, or user-facing synthesis ownership.
- Assignment state: `platform-unverified`
- Scoped override: user assigned this independent critic review at `gpt-5.5` / `high`; this matches repository critic policy and waives no safety, ownership, QA, release, implementation, or scope boundary.
- Timestamp: `2026-09-01T09:04:57.3373231+03:00`
- Elapsed time at receipt creation: approximately `260 seconds`
- Token use at receipt creation: `135449` tokens in the local goal tracker immediately before receipt drafting; final post-hash token use unavailable.

## Scope

I reviewed the immutable architecture amendment:

`kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_viral_step6a_inv_qav_inventory_metadata_taxonomy_amendment_20260901.md`

This is not an implementation review, QA review, semantic acceptance, release review, publication review, staging review, commit review, or push review. I did not run live build/remediate/preflight/verify, did not inspect a frozen release candidate, did not verify release freeze evidence, did not verify release QA references, and did not validate release exclusions or mutation invalidation. Release remains a separate later gate. Any byte mutation of the amendment or this receipt invalidates the corresponding hash-bound review identity and requires a fresh review.

## Files checked read-only

- `AGENTS.md`
- `docs/governance/nri_goal_governance.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/plan.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/context.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_viral_step6a_executable_enforcement_remediation_packet_20260901.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_step6a_executable_enforcement_remediation_packet_review_20260901.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_viral_step6a_sch_qav_shape_error_taxonomy_amendment_20260901.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_step6a_sch_qav_shape_error_taxonomy_amendment_review_20260901.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_viral_step6a_inv_qav_inventory_metadata_taxonomy_amendment_20260901.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_step6a_mutation_batch_inv_20260901.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_step6a_mutation_batch_qav_a_20260901.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_step6a_mutation_batch_qav_b_20260901.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_step6a_mutation_batch_qav_c_20260901.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_step6a_mutation_batch_qav_d1_20260901.md`
- `kb_creator/scripts/scenario_source_reconstruction.py`
- `kb_creator/tests/test_scenario_source_reconstruction.py`
- `kb_creator/working/viral/source_reconstruction/20260831_step6a_reconstruction_from_salvaged_engine_candidate/RECONSTRUCTED_EN.qa.json`

## Evidence

- Parent packet SHA-256 verified: `32D5A63657C5157B77B3A40ABB0CD5B0CDD00473A2846F28B1586B97C997257A`.
- Parent packet independent review SHA-256 verified: `B45198A548309258D08DE3CFBD4B0FA18F65580CBD94192E03044507E688E279`.
- SCH/QAV amendment SHA-256 verified: `0A692CD1A8F3067E551ACFB1581840BF9748FD2C308C6BBE79FD4B174FC75D2A`.
- SCH/QAV amendment review SHA-256 verified: `102383E2CD10EFE91DFBAD13A905DDCFB63DFE8ADF6BCC9B1D7937E40ADAA5DB`.
- INV/QAV amendment SHA-256 verified: `779B641EBD2DC55F3A4725AA0345D5286CB41CE608A4465B8B5AE43DC9156606`.
- Current code/test baseline verified: `kb_creator/scripts/scenario_source_reconstruction.py` = `FCAE2693C03A35382CADF35B6474E7A173670D65FD6D428726E56E71FF4BDA46`; `kb_creator/tests/test_scenario_source_reconstruction.py` = `3A7DB49164A11DF5C7EB5663639914668ACE1AAA22F72AEC2F69F66B0E474357`.
- INV receipt SHA-256 verified: `A559B08DFF5A4EB75F41AD075ECB91E74797956502A210B08B62C78FCFE78518`.
- QAV receipts verified: A `5A08C25D42FCCAE87C154FCBC505125F4D71BEF9196FECA1BEC8D2CE9FFEE5EC`; B `652DEEDC0DD415853FB7193148DBABC5041C06909DAE0AC83C1C0295E01B8DEA`; C `346AEB9D11EB6749471DDB9218F4CB6AC86C5F8B1982F8ACED5EE6E79D61D0C6`; D1 `12A38CB2267EDF6E85184BC8728A4BCCC8B1E14424F14D4BB8BE984FD37DA4E7`.
- The assigned D2 implementation receipt path was absent before this review: `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_step6a_mutation_batch_qav_d2_20260901.md`.
- This review receipt path was absent before creation.
- Live QA metadata read-only values: `output_inventory_rule` is exactly `every regular file recursively present under candidate root except root-level RECONSTRUCTED_EN.qa.json`; `output_inventory_count` is `501`; `state` is `candidate_needs_review`.
- Current writer still emits short `all_regular_except_qa`, and current verifier still contains later `E_QA_INVENTORY_ARRAY`, `E_QA_INVENTORY_COUNT`, and `E_QA_INVENTORY_DIGEST` branches after `_verify_inventory_authority`. Current focused registry still expects those three late QAV codes. These are the implementation gaps the amendment scopes for Terra, not accepted current behavior.
- Git status was pre-existing dirty/untracked across governance and `kb_creator` paths. I preserved that state and changed no implementation, candidate, protected, plan, context, status, release, Git, cache, or cleanup surface.

## Assessment

The root cause is real and implementation-relevant. The shared verifier loads the QA document, closes QA root shape, then calls `_verify_inventory_authority(candidate_root, qa)` before later COMMANDS/QAV semantic checks. The current late QAV array/count/digest checks therefore cannot be authoritative for physical states already consumed by phase-6 inventory authority.

The exact four D2 rows in the amendment are coherent and ordered correctly:

1. `QAV-inventory-rule-wrong`, selector `candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_rule`, mutation to exact legacy short string `all_regular_except_qa`, expected `E_QA_INVENTORY_RULE`, reseal `()`.
2. `QAV-inventory-count-wrong`, selector `candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_count`, mutation to integer `500`, expected `E_INV_CARDINALITY`, reseal `()`.
3. `QAV-inventory-digest-wrong`, selector `candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256`, mutation to string `"0" * 64`, expected `E_INV_DIGEST`, reseal `()`.
4. `QAV-inventory-array-wrong`, selector `candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/RECONSTRUCTED_EN.md`, mutation removing only the row whose path is `RECONSTRUCTED_EN.md`, expected `E_INV_ORDINARY_ROW_MISSING`, reseal `()`.

The INV receipt independently proves the three aliased phase-6 outcomes with the same selectors/mutations, `strict_verify_calls=1`, `outside_fixture_reads=0`, empty reseals, empty residue, expected equals observed, and `PASS`. Preserving phase-6 INV as the earliest authority is therefore required. Making QAV-D2 count/digest/array into cross-family audit aliases is cleaner than hiding family routing or weakening the inventory verifier.

`output_inventory_rule` is different and remains independently reachable after phase 6, because inventory authority does not consume that declarative string. The amendment correctly requires one exact long production literal to be emitted by both TEST and production-shaped writers and checked later as `E_QA_INVENTORY_RULE`, with no alias or normalization for the short form.

Removing the three late `E_QA_INVENTORY_ARRAY`, `E_QA_INVENTORY_COUNT`, and `E_QA_INVENTORY_DIGEST` branches does not weaken coverage. After phase 6, the verifier has already checked the enumerated non-QA regular-file set, row shape, row order, count, digest, path form, hashes, and live bytes. Retaining shadowed late branches would create misleading unreachable taxonomy rather than defense in depth.

The global identical-state alias ceiling is precise: the two accepted SCH/QAV pairs plus three new INV/QAV pairs make exactly five pairs and ten members. The amendment preserves physical identity of selector/mutation/reseal/code while requiring distinct case ids, distinct callables, distinct callable names, fresh fixtures, and distinct audit rows. It also states that the alias table is test/audit evidence only and cannot be passed to `_strict_verify`, which blocks production case routing.

The count proof is internally consistent: INV remains `18`; QAV remains `90` as `24 root-shape + 1 state + 4 authority-hash + 9 scalar + 28 count-map + 20 gate/boolean D1 + 4 D2`; selector-specific negatives remain `368`; focused tests remain `371` including three BLD nodes. Selector non-uniqueness is explicitly not used as a count proxy.

Prior receipt validity is stated truthfully. INV and QAV-A/B/C/D1 receipts remain historical engineering evidence for their bounded cases, not current final QA, live, protected-119, combined-490, candidate acceptance, release, Git, promotion, or publication proof. The amendment also correctly requires post-D2 rerun of all ten alias members plus the D2 rule case, and downstream Luna/final-critic gates remain open.

Terra's three-path scope is sufficient and appropriately narrow: only the reconstruction library, the focused test file, and the absent D2 receipt may change. The required pre-write checks, exact four D2 audits, five-pair callable identity table, retired-code search, representative regressions, BLD run, collect-only `371`, zero residue, and stop conditions are enough to gate the intended implementation without substituting QA or live release work.

No QA substitution, live command, release claim, semantic promotion, publication, staging, commit, push, cache cleanup, protected test mutation, canonical plan/context/status edit, or orchestration transfer is authorized by the amendment.

## Severity findings

- P0: none.
- P1: none.
- P2: none.

## Blockers

No architecture blocker remains for implementing the INV/QAV inventory-metadata taxonomy amendment.

Procedural gates still open:

- The orchestrator must bind this receipt hash before Terra starts.
- Terra must implement only the D2 batch within the exact three-path allowlist and write `terra_engineering_viral_step6a_mutation_batch_qav_d2_20260901.md`.
- Terra must rerun all ten members of the five alias pairs and `QAV-inventory-rule-wrong` on the post-D2 baseline.
- Luna bounded QA must later inspect actual code and run the required full focused/protected/combined/live checks.
- A fresh independent final implementation/process critic must review the implemented result with no implementation/material-design/QA participation and no unresolved P0/P1/P2.
- Release remains pending and separate; this receipt is not a release decision.

## Changed path

Created only:

- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_step6a_inv_qav_inventory_metadata_taxonomy_amendment_review_20260901.md`

No code, tests, live candidate, source, sidecar, contract, recovery, COMMANDS, protected CLI/tests, canonical plan, context, project status, release file, Git index/ref, cache, cleanup, staging, commit, push, promotion, publication, semantic review, or QA artifact was edited.

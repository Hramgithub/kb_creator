# Independent critic review: Viral Step 6A REG synthetic-redefinition taxonomy alias amendment

- Goal: `20260830-kb-creator-next-scenario`
- Step: `6A-REG-synthetic-redefinition-taxonomy-alias-amendment`
- Review kind: `architecture`
- Candidate status: immutable architecture amendment, not an implementation, QA, or release candidate.
- Verdict: `ACCEPT`
- Recommendation: implementation-ready for the bounded Terra REG batch after the orchestrator binds this receipt hash.
- Critic role policy: `gpt-5.5` / `high`
- Actual platform model / effort: `unavailable`; repository policy does not prove platform selection.
- Implemented or materially designed by this critic: no.
- QA ownership by this critic: none.
- Orchestrator policy owner: main chat `gpt-5.6-sol` / `medium`; this review does not transfer orchestration, canonical-state, integration, stop/ask, release, or user-facing synthesis ownership.
- Assignment state: `platform-unverified`
- Scoped override: user clarified on `2026-09-01` that Luna may execute only prepared bounded QA scripts/commands and capture evidence; Terra remains the engineering owner for reusable code, tests, fixtures, mutation audit construction, and implementation. Any downstream wording about Luna inspection is constrained to prepared read-only QA command execution and evidence capture.
- Timestamp: `2026-09-01T09:51:36.3538928+03:00`
- Elapsed time at receipt creation: approximately `8 minutes`
- Token use at receipt creation: `unavailable`

## Scope

I reviewed the immutable architecture amendment:

`kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_viral_step6a_reg_synthetic_redefinition_taxonomy_alias_amendment_20260901.md`

This is not an implementation review, QA review, semantic acceptance, release review, publication review, staging review, commit review, or push review. I did not run live build/remediate/preflight/verify, did not inspect a frozen release candidate, did not verify release freeze evidence, did not verify release QA references, and did not validate release exclusions or mutation invalidation. Release remains a separate later gate. Any byte mutation of the amendment or this receipt invalidates the corresponding hash-bound review identity and requires a fresh review.

## Files checked read-only

- `AGENTS.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_viral_step6a_reg_synthetic_redefinition_taxonomy_alias_amendment_20260901.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_viral_step6a_reg_historical_specimen_clarification_20260901.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_viral_step6a_executable_enforcement_remediation_packet_20260901.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_step6a_executable_enforcement_remediation_packet_review_20260901.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_viral_step6a_sch_qav_shape_error_taxonomy_amendment_20260901.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_step6a_sch_qav_shape_error_taxonomy_amendment_review_20260901.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_viral_step6a_inv_qav_inventory_metadata_taxonomy_amendment_20260901.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_step6a_inv_qav_inventory_metadata_taxonomy_amendment_review_20260901.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_step6a_mutation_batch_qav_d2_evidence_correction_20260901.md`
- `kb_creator/scripts/scenario_source_reconstruction.py`
- `kb_creator/tests/test_scenario_source_reconstruction.py`

## Evidence

- Target amendment SHA-256 verified: `6E0C6280D7930D6994E461E32363C1FA15B0BBC39AFAE34CAF9EE8D84737341D`.
- Historical clarification SHA-256 verified by assignment binding: `F713704F12293AFA15BB0856D9680EA73755C9C85E03EC8D57C90CAA6928604D`.
- Accepted parent packet SHA-256 verified: `32D5A63657C5157B77B3A40ABB0CD5B0CDD00473A2846F28B1586B97C997257A`.
- Accepted parent independent review SHA-256 verified: `B45198A548309258D08DE3CFBD4B0FA18F65580CBD94192E03044507E688E279`.
- SCH/QAV amendment SHA-256 verified: `0A692CD1A8F3067E551ACFB1581840BF9748FD2C308C6BBE79FD4B174FC75D2A`.
- SCH/QAV independent review SHA-256 verified: `102383E2CD10EFE91DFBAD13A905DDCFB63DFE8ADF6BCC9B1D7937E40ADAA5DB`.
- INV/QAV amendment SHA-256 verified: `779B641EBD2DC55F3A4725AA0345D5286CB41CE608A4465B8B5AE43DC9156606`.
- QAV-D2 correction SHA-256 verified: `32A714D453F4A895866267A8F47879DE554A53581E272A7908C3F92D695FC268`.
- Frozen current library verified: `kb_creator/scripts/scenario_source_reconstruction.py` = `34943D5E0008A01A1F3AFC3AF2D49091F06049187AE9D0CB7DA02654663862D4`.
- Frozen current focused tests verified: `kb_creator/tests/test_scenario_source_reconstruction.py` = `D3FA871BBA3DED04ECD216544B7A9A7EEECB95D4769DDF45612B412990F9D192`.
- This review receipt path was absent before creation.
- Current `_verify_qa_root_shape` is shape-first: closed top-level key set mismatch returns `E_SHAPE_QA`; only a shape-complete wrong schema reaches `E_SCHEMA_QA`.
- Current `_strict_verify` accepts production/test route from context and has no family, case id, pytest id, audit id, or alias-table input for verifier selection.
- Current inventory authority runs before later QA semantic checks and enforces row shape, path form, live file set, 501 cardinality, ordinal order, live byte/hash agreement, and manifest digest.
- Current focused registry still contains the pre-amendment `REG-P1-stale-metadata -> E_QA_SCHEMA` expectation. The amendment explicitly names this as invalid current behavior to replace after this review, so that is an implementation gap, not accepted current evidence.
- Git status was already dirty/untracked across governance and `kb_creator` paths before this receipt. I preserved that state and changed no implementation, candidate, protected, plan, context, status, release, Git, cache, cleanup, or live path.

## Assessment

The amendment correctly resolves the blocker identified by the historical clarification. It does not claim that the unavailable historical QA-v2 bytes were recovered, and it does not reuse the historical raw hash `FE142A...` as identity. Instead, it explicitly redefines `REG-P1-stale-metadata` as a synthetic deterministic regression cluster derived from a fresh valid fixture. That is a truthful replacement branch, not a fabricated historical specimen.

The synthetic transform is specific enough to implement and audit without hidden authority: start from a fresh valid 501-row fixture, set schema to `kb_creator.reconstructed_en_qa.v2`, set the stale recovery manifest hash, remove exactly `recovery_evidence_sha256`, align `open_blocker_count` and `counts.open_blockers` to `3`, remove exactly contact sheets `sheet-001.png` through `sheet-031.png`, retain and ordinally order the remaining 470 current records, recompute `output_inventory_sha256`, preserve the canonical rule literal, preserve `state=candidate_needs_review`, and preserve all other fields. The amendment also correctly states that failed derivation assertions are fixture-construction stops, not verifier successes.

The expected `REG-P1-stale-metadata` outcome `E_SHAPE_QA` is coherent with the current shared phase-5 predicate. Removing `recovery_evidence_sha256` produces a top-level QA shape mismatch before schema comparison, inventory authority, or later QA semantic checks. Retiring `E_QA_SCHEMA` is necessary; retaining it would require a nonexistent code or forbidden REG-specific routing.

The 38-selector audit exception is explicit and bounded. It lists five scalar/root-field changes, thirty-one stable contact-sheet row selectors, and two inventory metadata selectors. It deliberately excludes `state` and `output_inventory_rule` because their values are preserved. This is a legitimate exception to the ordinary one-selector audit row because the case is a single parent-authorized synthetic document transaction, and the exact selector list prevents a root-only audit from hiding the material changes.

`REG-P1-missing-enforcement` is bound physically and narrowly: `COMMANDS.counts.pages` changes from integer `124` to integer `125`, reseals are exactly `(INVENTORY, QA)`, and the expected earliest code is `E_COMMAND_COUNTS_PAGES`. The amendment correctly requires this REG case to stay distinct from `CMD-count-pages-wrong` by case id, callable object/name, fixture, and audit row while admitting their identical final physical state.

The alias ceiling supersession is correct. The existing two SCH/QAV pairs plus three INV/QAV pairs are already accepted; adding exactly `CMD-count-pages-wrong <-> REG-P1-missing-enforcement` creates exactly six cross-family identical-state pairs and twelve members. The synthetic REG stale cluster is not an alias member because its 38-selector final state is unique. No seventh alias, shared callable, or verifier routing by test identity is authorized.

The count arithmetic is internally consistent: `REG=2`, selector-specific negatives `368`, distinct case ids `368`, distinct callable objects/names `368`, `BLD=3`, and focused total `371`. No node is added or removed; two already-counted REG identities are made executable under corrected taxonomy.

Terra's implementation boundary is sufficient and narrow: only the reconstruction library, focused test file, and absent REG engineering receipt may change. The required commands cover the two REG nodes, taxonomy cross-checks, twelve alias members, BLD, collect-only `371`, and retired-code search for `E_QA_SCHEMA`. The required receipt evidence includes complete REG audit objects, stale 38-selector delta, 470-record digest recomputation, six-pair alias table, full 368-row audit digest, hashes, path delta, and zero residue.

The downstream role boundary is acceptable only under the scoped override above: Luna may execute prepared bounded QA scripts/commands and capture evidence after Terra, but may not construct fixtures, write tests, build mutation-audit machinery, perform remediation, or act as the engineering owner. That constraint is compatible with the amendment's architecture because all construction and implementation authority is assigned to Terra.

No QA substitution, live command, release claim, semantic promotion, publication, staging, commit, push, cache cleanup, protected test mutation, canonical plan/context/status edit, or orchestration transfer is authorized by this amendment.

## Severity findings

- P0: none.
- P1: none.
- P2: none.

## Blockers

No architecture blocker remains for the bounded Terra REG implementation batch.

Procedural gates still open:

- The orchestrator must bind this receipt hash before Terra starts.
- Terra must implement only within the exact three-path allowlist and write `terra_engineering_viral_step6a_mutation_batch_reg_20260901.md`.
- Terra must prove the two REG rows, four taxonomy rows, all twelve alias members, BLD `3`, collect-only `371`, retired `E_QA_SCHEMA`, full audit digest, exact path delta, and zero residue.
- Luna must later be limited to prepared bounded QA command execution and evidence capture.
- A fresh independent GPT-5.5/high implementation/process critic must review the implemented result with no implementation/material-design/QA participation and no unresolved P0/P1/P2.
- Release remains pending and separate; this receipt is not a release decision.

## Changed path

Created only:

- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_step6a_reg_synthetic_redefinition_taxonomy_alias_amendment_review_20260901.md`

No code, tests, live candidate, source, sidecar, contract, recovery, COMMANDS, protected CLI/tests, canonical plan, context, project status, release file, Git index/ref, cache, cleanup, staging, commit, push, promotion, publication, semantic review, or QA artifact was edited.

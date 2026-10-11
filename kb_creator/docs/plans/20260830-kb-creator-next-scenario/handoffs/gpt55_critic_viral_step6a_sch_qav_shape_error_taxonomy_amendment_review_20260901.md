# Independent critic review: Viral Step 6A SCH/QAV shape-error taxonomy amendment

- Goal: `20260830-kb-creator-next-scenario`
- Step: `6A-SCH-QAV-shape-error-taxonomy-amendment`
- Review kind: `architecture`
- Verdict: `ACCEPT`
- Recommendation: implementation-ready for the held QAV-A Terra batch, after the orchestrator binds this receipt hash.
- Critic role policy: `gpt-5.5` / `high`
- Actual platform model / effort: `unavailable`; repository policy does not prove platform selection.
- Implemented or materially designed by this critic: no.
- QA ownership by this critic: none.
- Orchestrator policy owner: main chat `gpt-5.6-sol` / `medium`; this review does not transfer orchestration, canonical-state, integration, release, or user-facing synthesis ownership.
- Assignment state: `platform-unverified`
- Scoped override: user assigned this independent critic review at `gpt-5.5` / `high`; no safety, ownership, QA, release, or implementation boundary is waived.
- Timestamp: `2026-09-01T08:02:47.9827891+03:00`
- Elapsed time at receipt creation: approximately `172 seconds`
- Token use at receipt creation: `139242` orchestrator/runtime tokens reported by local goal tracker; subagent split unavailable.

## Scope

I reviewed the immutable architecture amendment:

`kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_viral_step6a_sch_qav_shape_error_taxonomy_amendment_20260901.md`

This is not a release review. I did not verify a frozen release candidate, release manifest, freeze evidence, QA release references, declared release exclusions, or publication invalidation. The release gate remains separate. Any byte mutation of the amendment or this receipt invalidates the corresponding review identity and requires a fresh review.

## Files checked read-only

- `AGENTS.md`
- `docs/governance/nri_goal_governance.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/plan.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/context.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_viral_step6a_executable_enforcement_remediation_packet_20260901.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_step6a_executable_enforcement_remediation_packet_review_20260901.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_viral_step6a_sch_qav_shape_error_taxonomy_amendment_20260901.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_orchestrator_viral_step6a_terra_mutation_batch_qav_a_20260901.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_step6a_mutation_batch_sch_20260901.md`
- `kb_creator/scripts/scenario_source_reconstruction.py`
- `kb_creator/tests/test_scenario_source_reconstruction.py`

## Evidence

- Parent packet SHA-256 verified: `32D5A63657C5157B77B3A40ABB0CD5B0CDD00473A2846F28B1586B97C997257A`.
- Amendment SHA-256 verified: `0A692CD1A8F3067E551ACFB1581840BF9748FD2C308C6BBE79FD4B174FC75D2A`.
- Prior independent parent-packet design review SHA-256 verified: `B45198A548309258D08DE3CFBD4B0FA18F65580CBD94192E03044507E688E279`.
- Held QAV-A assignment SHA-256 verified: `5582B039B2B8D8E88B92821D1AAAF537AEBBDEA6CE5D6CD8EFF191BC06908144`.
- Completed SCH receipt SHA-256 verified: `274444A4EC1F843E2883E2299736B2A009A41EB92F02F4CFC7B8F37D0EBE25F4`.
- Frozen code/test baseline verified: `kb_creator/scripts/scenario_source_reconstruction.py` = `2309CD5015B89908A5B751916F46B4C601AFB8E121EB338FC6450B7BAAE49FAC`; `kb_creator/tests/test_scenario_source_reconstruction.py` = `7B9AEC1EF0BA2870E2021544912538FE3234DAF92D0E38E34F16285118649DCF`.
- The assigned review receipt path was absent before creation.
- The QAV-A implementation receipt path `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_step6a_mutation_batch_qav_a_20260901.md` was absent.
- Current worktree is dirty with pre-existing governance/config and `kb_creator` changes; I preserved that state and made no implementation/protected/candidate/Git edits.

## Assessment

The root cause is real. The accepted parent packet required `SCH-QA-required-top-member-missing -> E_SHAPE_QA` and `SCH-qa-unexpected-top-member -> E_SHAPE_QA`, while QAV-A required the identical physical invalid QA documents at `#/asset_count` and `#/unexpected` to return `E_QA_SHAPE`. A shared deterministic verifier cannot return different codes for the same admitted bytes without forbidden case-id, family, pytest, mutation-history, provider-prefix, or environment routing.

The amendment's taxonomy is deterministic and consistent with the parent phase order. Parent phase 5 closes schemas, required top-level shapes, unexpected members, and row shapes before phase 6 inventory transport, phase 7 graph checks, phase 8 COMMANDS/QA semantics, and phase 9 no-fabricated-closure state. Therefore all 24 QAV root missing/extra cases must stop at the same phase-5 QA shape predicate as SCH and emit `E_SHAPE_QA`.

`QAV-state-promoted -> E_QA_STATE` is correctly retained as a separate phase-9 state predicate. The current frozen source still collapses QA schema and state under `E_QA_SCHEMA`, so the amendment correctly identifies this as future Terra work and does not claim it is already fixed. The one-mutation valid fixture for promoted state is not shadowed by the phase-5 root-shape correction because the `state` member remains present and only its value changes.

The two cross-family identical-selector aliases are narrowly and explicitly allowed: `SCH-QA-required-top-member-missing` with `QAV-top-asset_count-missing`, and `SCH-qa-unexpected-top-member` with `QAV-top-extra`. The amendment preserves distinct case IDs, requires distinct callable object identities and names, requires separate fresh fixtures and audit rows, and does not reduce the 368 negative-row proof to selector uniqueness.

Literal reseals remain `()` for all 25 QAV-A rows. This is coherent with phase-5 QA root-shape closure and phase-9 QA state validation: no inventory or QA regeneration is allowed to mask the invalid document under review.

Prior SCH evidence remains compatible but not current-baseline sufficient. The SCH receipt already records the two overlap rows as `E_SHAPE_QA` with no reseal, one strict verify call, expected equals observed, and `PASS`. Its material hashes are older than the current frozen baseline, so the amendment correctly requires Terra to rerun the two SCH overlap nodes and Luna to later rerun the full 371.

Counts remain unchanged: SCH `33`, QAV `90`, selector-specific negatives `368`, BLD `3`, focused total `371`. The amendment changes expected-code literals only for the 24 existing QAV root missing/extra nodes and does not add, remove, or merge cases.

The held QAV-A assignment is superseded precisely: only its old `E_QA_SHAPE` root-shape literals and ambiguous schema/state wording are overridden. Its three-path write allowlist, no-live/no-protected/no-cache/no-Git boundaries, command structure, and receipt obligations remain binding.

Terra's resumed scope and stop conditions are sufficient. They require pre-write hash review binding, exact 25 QAV-A nodes in four chunks, SCH overlap rerun, representative completed-family regression, BLD 3, focused collect 371, distinct callable identity evidence, full closed audit objects, zero residue, exact changed paths, and a truthful blocked receipt on any mismatch.

No hidden routing, weakened check, QA substitution, live mutation, release claim, semantic promotion, publication, staging, commit, push, or orchestration transfer is authorized by the amendment.

## Severity findings

- P0: none.
- P1: none.
- P2: none.

## Blockers

No architecture blockers remain for implementing the amended QAV-A taxonomy.

Procedural blockers still open downstream:

- Terra must implement only the held QAV-A batch within the exact three-path allowlist and write its immutable QAV-A receipt.
- Luna independent QA must later inspect the actual implementation, rerun the required focused/protected/combined/live checks, and write its own bounded QA receipt.
- A fresh independent final implementation/process critic must review the implemented result with no implementation/material-design/QA participation and no unresolved P0/P1/P2.
- Release remains pending and separate; the candidate remains `candidate_needs_review`.

## Changed path

Created only:

- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_step6a_sch_qav_shape_error_taxonomy_amendment_review_20260901.md`

No code, tests, live candidate, source, sidecar, contract, recovery, QA, COMMANDS, protected CLI/tests, canonical plan, context, project status, release file, Git index/ref, cache, cleanup, staging, commit, push, promotion, or publication path was edited.

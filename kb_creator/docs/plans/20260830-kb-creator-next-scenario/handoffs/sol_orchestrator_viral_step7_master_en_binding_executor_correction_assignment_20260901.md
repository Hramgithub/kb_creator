# Viral Step 7 MASTER_EN C1 binding-executor correction assignment

## Boundary

- Owner: same `gpt-5.6-terra` engineering role, `medium`.
- Write only `kb_creator/scripts/build_scenario_master_en.py`, `kb_creator/tests/test_build_scenario_master_en.py`, and new immutable correction receipt `handoffs/terra_engineering_viral_step7_master_en_binding_executor_correction_20260901.md`.
- Preserve all other edits; config/source/verifier/plan/context/candidate/Git are read-only.
- Baseline builder SHA-256 `B862A9C0B10B54E77D46E2DF9EB7DE9D37DECDCC89507A7C8FEED270EB1049FC`; tests SHA-256 `8AAB587EA54D30DAEB47D9B0081F6CAE0A133CA7337CFE47A2FF5B176012A3B9`.

## Findings to correct

The first C1 receipt is historical but not accepted as conservation proof:

1. `conservation_ledger` classifies every unclaimed line as structural merely because every page has a `source_disposition` row. The reported 474 structural blocks therefore hide missing ownership instead of proving an explicit policy.
2. `resolve_bindings` excludes `consume_continuation_label` locators from page starts and does not create claims for declared continuation pages. Continuation content can therefore remain unclaimed.
3. `binding_declarations` uses a broad union for `unit_ref`; require `physical_unit -> handout anchor` and `owned_page_unit -> visual_review.review_id`.
4. Enforce the exact four shared-prefix rows and owners: 04->04, 05->04, 06->06, 07->06; all other rows null.
5. Require locator occurrence semantics explicitly (`occurrence == 1` under the exact-once contract), and close continuation membership/overlap against each row's source pages.
6. Fix the reader-noise value check indentation so every row is validated, not only the final row.

## Required result

- Build real non-overlapping claims for explicit continuation labels and continuation page starts, ending at the next declared start or EOF.
- A nonblank accepted-v4 line/block may be counted only when owned by exactly one binding/owned-page unit or matched by a concrete, explicit technical/evidence-only rule. Generic page disposition is not authorization.
- Fail closed on any unowned, duplicate, or unauthorized-suppression block. Do not hard-code a count to make the current package green.
- Re-run the real amended config resolver. A PASS requires an evidence-backed ledger with zero unowned/duplicate/unauthorized-suppression; report any newly exposed config gap truthfully instead of weakening the rule.
- Add only representative regression nodes for the six findings above; keep total builder+verifier tests compact (roughly 20-26). Preserve Phase B asset tests and normal CLI fail-closed behavior. No candidate/sidecar output.

Run the same C1 compile, builder+verifier focused pytest and scoped diff-check commands. Do not run MinerU or 371/119/490.

The correction receipt returns `PASS_CORRECTED_BINDING_EXECUTOR`, `FAIL`, or `BLOCKED`, with changed hashes, exact conservation categories/counts and rule evidence, test count, forbidden-output absence, elapsed time and token use if available. It must explicitly supersede only the conservation claim in the first C1 receipt; historical files remain unchanged.

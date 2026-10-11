# Terra assignment: Viral Step 6A audit-capture recovery

**Owner:** `gpt-5.6-terra`, engineering at medium effort.  **Status:** dispatched.

## Bound inputs

- Accepted architecture packet: `sol_architect_viral_step6a_executable_enforcement_remediation_packet_20260901.md`, SHA-256 `32D5A63657C5157B77B3A40ABB0CD5B0CDD00473A2846F28B1586B97C997257A`.
- BLD/full-integration assignment: `sol_orchestrator_viral_step6a_terra_bld_full_integration_assignment_20260901.md`, SHA-256 `110F89D632C4FDA710BC76C7E9A05A552B121B777552247DAE1A27859B187A56`.
- Truthful incomplete receipt: `terra_engineering_viral_step6a_bld_full_integration_20260901.md`, SHA-256 `82C3A77FCDD7F884676A783B806AC4671838133194F455B5D6A1C4E039810A3D`.
- Frozen implementation identities:
  - library `0A1B84C9CAD20E56F272B9311925A13926A487DFCB21F4C2570B0A7F9CCD2EAD`;
  - focused tests `FA70BBAE285EAAA10E1F6BAF90119008342A18552E580E4E8530D9462997D5F9`.
- Confirmed engineering run: `371 passed in 1033.74s (0:17:13)`; the prior run did not preserve complete streams.

## Role boundary

This is engineering evidence construction and therefore belongs only to Terra. Luna must not design or implement capture, construct fixtures or audit rows, alter tests/code, interpret failures, or complete the receipt. A later Luna/high task may only execute an already prepared immutable QA command packet and capture raw results.

## Allowed writes

Only replace the existing incomplete receipt:

`kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_step6a_bld_full_integration_20260901.md`

The library and focused test module are read-only for this recovery. If either identity differs or a code/test edit appears necessary, stop with a truthful blocker.

## Required recovery execution

1. Import the frozen focused test module and use its actual ordered `CASES`, `make_valid_bundle`, and `apply_case` entry points. Execute all 368 cases in fresh subroots owned by one automatically cleaned `TemporaryDirectory`. Do not reconstruct from labels or expected-code tables.
2. Retain all returned actual `MutationAudit.as_dict()` values in registry order. Validate the exact closed 16-field key set, `strict_verify_calls == 1`, `outside_fixture_reads == 0`, empty undeclared changes/residue, exact expected/observed equality, and `result == "PASS"` before writing the receipt.
3. Derive the canonical UTF-8/LF stream only from those actual returned objects using the accepted formula:

   `case_id<TAB>semantic_selector<TAB>comma_joined_reseals<TAB>expected_code<TAB>observed_code<TAB>PASS<LF>`

   Record all 368 literal rows, exact byte length, and recomputed uppercase SHA-256. Record both complete REG objects and the exact 38-selector `REG-P1-stale-metadata` delta from the returned audit.
4. Record the complete registry evidence: canonical profile serialization/seal, provider ids, public/test signatures, route table, all 368 case ids, family counts, callable names and non-secret one-based within-process ordinals, 368 distinct callable objects/names, and exactly six declared alias pairs/twelve distinct members.
5. Preserve the existing three-row BLD state-transition evidence with admitted/final/temp/marker states, non-secret file-id tokens, manifest identities, verifier phases, and results.
6. Run one explicit cache-disabled focused pytest capture through a subprocess with stdout and stderr retained separately in memory: `python -B -m pytest -p no:cacheprovider kb_creator/tests/test_scenario_source_reconstruction.py -q`. Record the literal command, native exit, collected/passed counts, elapsed time, complete stdout byte count and SHA-256, complete stderr byte count and SHA-256, and the terminal summary. Do not create a durable raw log.
7. Record material/cache/scope pre/post identities and exact changed-path proof. The only intended path delta is the assigned receipt. The automatically cleaned OS temporary roots are not worktree cleanup and must leave no residue.
8. Mechanically regenerate the large receipt from the validated in-memory evidence, then independently parse the embedded JSON array and canonical-row block back from the receipt and recompute counts, byte length, and hashes before claiming `COMPLETE`.

## Forbidden

- no protected 119 or combined 490 run;
- no live preflight/build/remediate/verify;
- no candidate/source/recovery/CLI/contract-test/visual/QA/COMMANDS mutation;
- no code/test/config/governance/Git changes;
- no manual or broad cleanup;
- no claim that the uncaptured earlier pytest stream was recovered;
- no Luna participation in this recovery.

Return the regenerated receipt SHA-256 and literal residual gaps. `COMPLETE` is permitted only if every requirement above is embedded and self-verified; otherwise preserve a truthful `BLOCKED` state.

Timestamp: 2026-09-01 Europe/Moscow

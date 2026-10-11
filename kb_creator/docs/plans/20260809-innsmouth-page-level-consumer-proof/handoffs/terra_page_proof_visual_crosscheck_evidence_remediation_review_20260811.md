# Independent Terra Implementation Review Receipt — Packet 4b.6-r exact evidence

- Goal id: `20260809-innsmouth-page-level-consumer-proof`.
- Step id: `4b.6-r-independent-implementation-review`.
- Review kind: `implementation` (non-release, non-frozen fixture-only candidate).
- Role/effort: independent Terra critic, `high`; actual platform model/effort: `platform-unverified`.
- Implemented or materially designed the candidate: **no**.
- Orchestrator policy owner: `gpt-5.5` at `medium` (`platform-unverified`).
- Assignment state: `platform-unverified`.
- Scoped override: independent fixture-only implementation review and this new immutable receipt only. No code, tests, previous receipts, plan, context, status, contracts, release files, Git, live PDF/source/output/Keeper/HTML/PDF, browser, network, parser, renderer, build, Packet 4b.7, registry activation, or orchestration transfer.

## Recommendation

**Reject.** The production baseline is unchanged and the prescribed seven-suite regression passes, but P1.1, P1.2, P1.3, and P1.5 remain open in the test evidence. Passing tests do not demonstrate Sol section 7 closure. Packet 4b.7, production activation, and release remain blocked.

## Evidence and checklist result

1. Read `AGENTS.md`, `docs/governance/nri_goal_governance.md`, the assigned `plan.md`/`context.md`, Sol's original binding remediation specification, Sol's exact-evidence packet, the rejecting Terra re-review, and the executor receipt.
2. `kb_creator/pdf_raw/page_proof.py` SHA-256 is exactly `A6E5E647A6B973772D6690775EC78F30FBDA909CBB19F95D6A88A4BA9702870B`; no production delta was found.
3. Within the packet evidence (not a Git/worktree audit), the executor receipt declares only `_page_proof_fixture_leaves.py`, `test_page_proof_visual_crosscheck.py`, and that receipt changed. This review did not run Git.
4. The seven fourth-case leaf names are direct primitive/literal assignments and the AST test rejects names, calls, attributes, subscripts, comprehensions, and binary operators in their right-hand trees. No import-time leaf builder/hash/JSON/production call was found.
5. The fourth row is an explicit `_FixtureAdmission` constructor; it reuses the exact two-column W/render leaves, uses a distinct literal V, retains two-column P, has literal V/F anchors, and is absent from inactive production registries. Its P oracle/canonical-root proof is nevertheless missing from the mandatory complete pre-normalizer contract (P1.1).
6. The fourth flow is syntactically literal and does not read `_case_rows()` or normalized flow. Its literal V contains the two required ordered boundary rows. This does not cure the failed structural mutation/recovery evidence in P1.2.
7. No `copy` or `deepcopy` remains. The mandated missing/duplicate/reorder closure is not met: the new duplicate case appends a copy of boundary row 0, whereas Sol requires an appended copy of final row 1; moreover legacy fourth-case normalizer paths remain outside the full contract (P1.1/P1.2).
8. Failed. `_assert_pre_normalizer_contract` is not the specified keyword-only typed helper, permits `expected_vector=None`, and receives dynamically generated `_expected_vector(...)` mappings rather than a full literal mapping at each call. More decisively, `_assert_reaches_internal_visual_predicate` and direct normalizer calls remain in `test_root_binding_and_reviewer_contract_predicates_fail_after_valid_admission_then_repair`, `test_private_two_boundary_admission_variant_has_real_boundary_reorder_recovery`, and the legacy test families at lines 746-911. These calls are not immediately preceded by the required full contract with the exact row/W/render/V/mechanics/flow and literal 15-key vector.
9. Failed. The new matrix names root/reviewer/boundary targets, but its vectors are generated rather than per-call literals; its aggregate-like substitute duplicates the first boundary rather than representing the required two valid-shape `f0 -> f2` aggregate rows. Required evidence is therefore not the exact exhaustive target/vector matrix.
10. Failed. Earlier legacy block/transcription/decision/inventory/mask paths still use the old helper and baseline-success shortcut rather than full-vector, target-only repair evidence. In particular the legacy inventory mutation has no target-only inverse repair; the new matrix does not replace all required inventory list/order/count/stale cases.
11. Failed. The AST test checks some direct edges, private names, payload runtime keys, domains, and V2 root non-edges, but it does not derive and assert the exact transitive F field set from source nor reject reflective/dynamic/whole-row/loop/comprehension/dictionary-expansion constructs in the binding helpers. It is a weaker subset than Sol section 5.
12. Passed. Production registries are inactive (`_PRODUCTION_FIXTURE_ADMISSION = ()` and expected primitives empty); public exports/signatures/errors are unchanged by the verified production SHA, coverage remains first, and no proof/output/4b.7 path was introduced.
13. Passed; exact command and post-run hashes are below.
14. Failed acceptance gate: the listed omissions are P1 under Sol's explicit reject rule.

## Findings

### P0

None.

### P1

1. **P1.1 — mandatory pre-normalizer evidence is not applied to every internal call.**
   - Evidence: `test_page_proof_visual_crosscheck.py:366-489` retains `_assert_reaches_internal_visual_predicate`; lines 582-658 and 746-911 contain normalizer calls governed by it or by no full helper. The new helper at lines 419-489 accepts a nonliteral/default vector and does not enforce the exact required signature/root canonicality/closed-key/schema assertions.
   - Exact repair scope: only `kb_creator/tests/test_page_proof_visual_crosscheck.py`. Remove the legacy helper/calls or migrate every positive, internal-negative, and repaired normalizer call to the exact keyword-only `_assert_pre_normalizer_contract` with the exact objects and a written 15-key literal mapping immediately before each call. Make it assert the complete Sol 2.1 contract, including P/F independent-oracle anchors, exact W/render metadata, canonical closed V root and schema.

2. **P1.2 — fourth two-boundary structural evidence is not the mandated target-only proof.**
   - Evidence: the literal fourth leaf, explicit row, literal flow, and two boundaries exist, but `boundary_duplicate` appends `boundary_checks[0]`, not the required final row 1; the separate legacy fourth-case test has unguarded normalizer calls and returns directly to the admitted baseline rather than proving each inverse repair under the full contract.
   - Exact repair scope: only `kb_creator/tests/test_page_proof_visual_crosscheck.py`. Retain one literal fourth baseline. For missing/duplicate/reorder, parse that literal baseline freshly, mutate only the specified target (duplicate exact row 1), reseal only its closure, assert the one-false literal vector, invoke the normalizer, inverse-repair the same mutated object, then assert all-true literal vector and byte-identical normalized fourth baseline.

3. **P1.3 — exhaustive target matrix and earlier target-only repairs are incomplete as evidence.**
   - Evidence: matrix expectations are generated by `_expected_vector`, not literal at each call; its aggregate-like case is `[row0, row0]` instead of two valid-shape aggregate `f0 -> f2` rows; legacy inventory and other retained cases do not provide full-vector target-only repair proof.
   - Exact repair scope: only `kb_creator/tests/test_page_proof_visual_crosscheck.py`. Use explicit literal vectors per target; implement the specified aggregate substitute; migrate all earlier block/transcription/decision/inventory/mask cases and add every required inventory list/order/count/stale target with target-only inverse repair. Preserve the two outer-envelope cases as separate, non-internal evidence.

4. **P1.5 — AST containment is weaker than the required exact graph contract.**
   - Evidence: `test_binding_helper_ast_containment_and_closed_roots_exclude_final_binding` validates selected direct edges/name sets and runtime payload keys, but lacks source-derived transitive P/F field sets and the mandatory rejection of reflection, dynamic lookup/import, whole-row serialization, loops, comprehensions, and dictionary expansion.
   - Exact repair scope: only `kb_creator/tests/test_page_proof_visual_crosscheck.py`. Extend the source-derived AST assertion to encode every Sol 5.1–5.3 edge, primitive call set, exact private-name set, transitive P/F field set, bytes domains, prohibited construct set, and V2 F non-edges.

### P2

None.

### P3

None.

## Exact bounded regression

Interpreter: `D:\NRI\.tools\python-3.13.14\python.exe` — `Python 3.13.14`.

```powershell
& 'D:\NRI\.tools\python-3.13.14\python.exe' -B -m pytest -q -p no:cacheprovider kb_creator/tests/test_page_proof_coverage_guard.py kb_creator/tests/test_page_proof_stage_a_topology_inventory.py kb_creator/tests/test_page_proof_fixture_admission.py kb_creator/tests/test_page_proof_closed_schemas.py kb_creator/tests/test_page_proof_witness_render_components.py kb_creator/tests/test_page_proof_flow_adjacency.py kb_creator/tests/test_page_proof_visual_crosscheck.py
```

Result: **`87 passed in 0.33s`**.

Post-review SHA-256:

- `kb_creator/pdf_raw/page_proof.py`: `A6E5E647A6B973772D6690775EC78F30FBDA909CBB19F95D6A88A4BA9702870B`
- `kb_creator/tests/_page_proof_fixture_leaves.py`: `EC6E5FBC5252F4BD094A6ED263668D002C413364057D360819217D530296B3AA`
- `kb_creator/tests/test_page_proof_visual_crosscheck.py`: `7FE49A905B77A384A4EFD3638F7149CC95D47DB17665A9A8AB5EE3826C1C0917`

## Files checked

- `AGENTS.md`
- `docs/governance/nri_goal_governance.md`
- `kb_creator/docs/plans/20260809-innsmouth-page-level-consumer-proof/plan.md`
- `kb_creator/docs/plans/20260809-innsmouth-page-level-consumer-proof/context.md`
- `kb_creator/docs/plans/20260809-innsmouth-page-level-consumer-proof/handoffs/sol_page_proof_visual_crosscheck_binding_remediation_spec_20260811.md`
- `kb_creator/docs/plans/20260809-innsmouth-page-level-consumer-proof/handoffs/sol_page_proof_visual_crosscheck_evidence_remediation_packet_20260811.md`
- `kb_creator/docs/plans/20260809-innsmouth-page-level-consumer-proof/handoffs/terra_page_proof_visual_crosscheck_binding_remediation_rereview_20260811.md`
- `kb_creator/docs/plans/20260809-innsmouth-page-level-consumer-proof/handoffs/executor_page_proof_visual_crosscheck_evidence_remediation_20260811.md`
- `kb_creator/pdf_raw/page_proof.py`
- `kb_creator/tests/_page_proof_fixture_leaves.py`
- `kb_creator/tests/test_page_proof_visual_crosscheck.py`

## Blockers and next action

- Blockers: P1.1, P1.2, P1.3, and P1.5. The candidate is not accepted; Packet 4b.7 and all production/release activation remain blocked.
- Next action: orchestrator may assign only the four exact test-file repair scopes above, then request a fresh independent Terra implementation review. No production change or scope expansion is authorized by this receipt.

- Elapsed time: approximately 18 minutes active review.
- Token use: unavailable.
- Timestamp: `2026-08-11T15:12:33.2974128+03:00`.

This immutable receipt does not transfer orchestration ownership. It is a non-release implementation rejection; any candidate mutation requires a new independent review receipt.

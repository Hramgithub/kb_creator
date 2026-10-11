# Independent Terra Implementation Re-review Receipt — Packet 4b.6-r

- Goal id: `20260809-innsmouth-page-level-consumer-proof`.
- Step id: `4b.6-r-implementation-rereview`.
- Review kind: `implementation`; this is not a release review.
- Role/effort: independent Terra critic, `high`; actual platform model/effort: `platform-unverified`.
- Implemented or materially designed candidate: **no**.
- Orchestrator policy owner: `gpt-5.5` at `medium` (`platform-unverified`).
- Assignment state: `platform-unverified`.
- Scoped override: fresh independent Packet 4b.6-r implementation re-review and this immutable receipt only. No code, tests, plan, context, status, contracts, output, Git, live/PDF/source/EN/RU/Keeper/HTML work, browser, network, parser, renderer, or release work.

## Recommendation

**Reject.** The production P/W/E/V/F dependency graph is acyclic and the exact bounded regression passes, but the post-P1 test evidence does not meet the required valid-admission and target-only predicate-vector contract. Open P1 findings block Packet 4b.7 and production activation. This is not a release acceptance.

## Evidence checked

- Read canonical `docs/governance/nri_goal_governance.md` and the assigned Sol specification, prior Terra rejection, and Terra engineering/recovery receipts.
- Inspected only the eight allowed candidate paths listed below. No Git command, live material, PDF/source/EN/RU/Keeper/HTML/output, browser, network, external parser, or renderer was used.
- Production `P` is computed from fixture/Stage-A/topology/render identity plus literal WitnessV2/CrossCheckV2 schema names. It excludes W, V, F, and expected-output fields. Final `F` includes P plus exact W/render/V length/SHA pairs; it excludes F and expected-output hashes.
- WitnessV2 and CrossCheckV2 closed roots use `pre_visual_binding_sha256`; neither root key set contains final `binding_sha256`. Candidate and review wrappers still use final `fixture_binding_sha256` and compare it with `row.binding_sha256`.
- `_fixture_admission_is_valid` recomputes P and F; `_fixture_admission_row_matches_derive_leaves` checks the exact W/render/V tuple. The production admission registry and expected primitive registry are both empty, and the bounded suites retain coverage-first public fail-close behavior.
- The literal-leaf helper has no imports/builders. The visual mutation helper calculates mutated F through the test-side stdlib-only `_oracle_final_admission_binding_sha256`, not production F code.
- Scope verification is limited to the allowed candidate contents, their current hashes, and the assigned receipts. A whole-worktree mutation audit was not performed because the packet forbids Git.

## Bounded regression

Confirmed interpreter: `D:\NRI\.tools\python-3.13.14\python.exe` (`Python 3.13.14`).

```powershell
& 'D:\NRI\.tools\python-3.13.14\python.exe' -B -m pytest -q -p no:cacheprovider kb_creator/tests/test_page_proof_coverage_guard.py kb_creator/tests/test_page_proof_stage_a_topology_inventory.py kb_creator/tests/test_page_proof_fixture_admission.py kb_creator/tests/test_page_proof_closed_schemas.py kb_creator/tests/test_page_proof_witness_render_components.py kb_creator/tests/test_page_proof_flow_adjacency.py kb_creator/tests/test_page_proof_visual_crosscheck.py
```

Result: **`85 passed in 0.27s`**.

## Findings

### P0

None. The actual P -> W/E -> V -> F graph contains no final-binding back-edge; F is absent from WitnessV2 and CrossCheckV2 roots; inactive production registries remain empty.

### P1

1. **P1.1 is not fully fixed: pre-normalizer and predicate-vector evidence remains incomplete.** `_assert_reaches_internal_visual_predicate` (`test_page_proof_visual_crosscheck.py:367-383`) receives only V. It asserts valid P/F and the V leaf pair, but cannot and does not call `_fixture_admission_row_matches_derive_leaves(row, W, render, V)`. The three-positive test (`:386-400`) likewise omits direct P/admission/exact-tuple assertions. The helper checks only selected root/reviewer/content predicates; it does not assert that every applicable non-target named predicate is true. Most negative cases then rely on generic error assertions, and end-of-test baseline normalizations do not repeat the required pre-normalizer proof for a target-only repair.
2. **P1.2 is only partially fixed.** The new two-boundary case (`:437-479`) does create two real ordered adjacency rows, an admitted row, and direct missing/duplicate/reorder rejection evidence. However, its fourth case is constructed by deep-copying/mutating the canonical flow and parsed canonical crosscheck rather than using the required literal fourth flow/crosscheck expectation; it also restores by returning to a separately retained baseline rather than proving each target-only repair and its pre-normalizer contract. This does not close the specified fourth-matrix/recovery requirement.
3. **P1.3 is only partially fixed.** Root-P and one reviewer-independence mutation now directly exercise their respective predicates, and the two-boundary case directly exercises cardinality/reorder. Required root-context and the other reviewer-contract targets (empty identity and wrong scope), plus direct target predicates for the ordinary boundary replay/decision mutations, remain absent. Generic normalizer errors are not a replacement for the required named-predicate vectors.
4. **P1.4 is fixed.** Mutated rows use `_oracle_final_admission_binding_sha256` (`:28-40`, `:351-353`), and the helper asserts the row's final F equals that independent oracle before the normalizer call. No production F helper is used for the visual mutation reseal.
5. **P1.5 is only partially fixed.** The new AST test (`:403-413`) verifies forbidden field-name constants are absent from `_fixture_pre_visual_binding_payload` and verifies W/V root key sets exclude F. It does not contain the mandated AST containment of the binding helpers themselves (allowed references only) or an AST-derived dependency check for the P/F helper chain. Static source inspection supports the desired current graph, but the required durable assertion remains weaker than the specification.

### P2

None.

## Files checked and SHA-256

- `kb_creator/pdf_raw/page_proof.py` — `A6E5E647A6B973772D6690775EC78F30FBDA909CBB19F95D6A88A4BA9702870B`
- `kb_creator/tests/_page_proof_fixture_leaves.py` — `7BBE5D9110A65D47C94D588758753C95D1436C9BA49AA9018307CE32EBA79EA8`
- `kb_creator/tests/test_page_proof_fixture_admission.py` — `276D2D4D89B283B601E58BE443808D8793518A159602C1FA4BD9976B8F9E441A`
- `kb_creator/tests/test_page_proof_closed_schemas.py` — `F4F33B0505275D436EFD16A622EECEF943F5C8CFB40BA3BE55148677F31DBA2C`
- `kb_creator/tests/test_page_proof_witness_render_components.py` — `8FD9D8E4AD034A667F793F0F6005C84787E9F478FFFC3ECD658EB813BE66BEA1`
- `kb_creator/tests/test_page_proof_flow_adjacency.py` — `1CDEFD250A271D59DF4C1AFE1283E573076E4066779DAC0FEB7B2FAE81A623E4`
- `kb_creator/tests/test_page_proof_visual_crosscheck.py` — `6C77671B4E62C75A19D476050ABE26C014DC69CAAC1EE108796D46EF63667AE3`
- `kb_creator/tests/test_page_proof_stage_a_topology_inventory.py` — `E9752542CA1574437AA24B8097CA5D30A4A7A7B434ED0146D72C66EF83165203`

## Blockers and next action

- Blockers: P1.1, P1.2, P1.3, and P1.5 above. Standing inactive topology/registry and public-boundary restrictions remain unchanged.
- Next action: a bounded executor must provide literal fourth-case flow/crosscheck expectations; a reusable pre-normalizer assertion that accepts the exact W/render/V triplet; direct P/admission/tuple and complete named-predicate vectors before every positive, negative, and repaired normalizer call; all required root/reviewer/boundary targets; target-only repair proofs; and complete AST containment of P/F binding helpers. Then rerun the exact seven-suite command and request a new independent Terra implementation review.

- Timestamp: `2026-08-11T14:37:28.8255720+03:00`.
- Elapsed time: approximately 8 minutes active review time.
- Token use: unavailable.

This immutable receipt does not transfer orchestration ownership, does not approve release or production activation, and is invalidated for acceptance purposes by any candidate mutation; a new independent implementation review is required after remediation.

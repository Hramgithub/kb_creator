# Sol architecture clarification — Packet 4b.6-r P1 evidence layout

## Immutable receipt and decision

- Goal id: `20260809-innsmouth-page-level-consumer-proof`.
- Step id: `4b.6-r-P1-evidence-layout-clarification`.
- Role/effort: Sol architect, requested `high`; actual platform model/effort `platform-unverified`.
- Orchestrator policy owner: `gpt-5.5` at `medium` (`platform-unverified`).
- Assignment state: `platform-unverified`.
- Scoped override: this architecture clarification and this immutable handoff only. It does not transfer orchestration ownership and grants no implementation, criticism, acceptance, release, live-input, browser, network, build, output, or Git authority.
- Result: **canonical option (a), with a precise qualification.** Delete the legacy normalizer families and the generated-vector matrix. Replace them with four named, non-parameterized, one-normalizer-call positive pytest fixtures and one explicitly named test per internal semantic target. Each internal target test contains exactly two written normalizer call sites: one negative and one inverse-repaired call. No macro, parameterized template, loop, callback, lambda table, or helper may contain or emit a normalizer call or an expected predicate vector.

Option (b) is rejected. A macro/template cannot satisfy “a written 15-key literal mapping at each call” when the normalizer call is hidden in reusable code or its vector arrives through a name, function result, parameter, expansion, or generated case table. This is P1 noncompliance, not an allowed implementation alternative. No different production structure is required.

This clarification supersedes only the **test evidence layout** in sections 2, 4, 5, 7, and 8 of `sol_page_proof_visual_crosscheck_evidence_remediation_packet_20260811.md`. It does not supersede or relax that receipt's P/W/E/V/F semantics, literal fourth-case facts, target-only mutation/reseal rules, independent oracles, public fail-close boundary, production SHA requirement, or independent-critic gate.

## Evidence, assumptions, and conflict classification

The following current facts were inspected read-only:

- `kb_creator/pdf_raw/page_proof.py` SHA-256 is `A6E5E647A6B973772D6690775EC78F30FBDA909CBB19F95D6A88A4BA9702870B`, the frozen accepted production baseline.
- `kb_creator/tests/_page_proof_fixture_leaves.py` SHA-256 is `EC6E5FBC5252F4BD094A6ED263668D002C413364057D360819217D530296B3AA`; all seven required fourth-case literal families already exist. It is frozen for the next executor.
- The current `kb_creator/tests/test_page_proof_visual_crosscheck.py` SHA-256 is `FF9227AFC600D56643241B853D750F8E36008D144AD4F4852784813C06502C89`. This differs from the restart receipt's `323453E3...` value and is therefore an unaccepted working candidate, not review evidence. A fresh executor must record this exact before hash (or stop if it has changed again) and its own after hash in a new receipt.
- The current file still has `_assert_reaches_internal_visual_predicate`, `_expected_vector`, a loop-driven target matrix, a loop-driven positive family, and four legacy normalizer families. The present source has normalizer calls not guarded by a literal full contract.

There is **no genuine impossible P0/P1 contract conflict**. The literal-per-call rule is implementable in one test file because all production predicates, test-side P/F oracles, fourth literal bytes, mutation resealers, mechanics, and flow setup already exist. The cost is deliberate source expansion. The following conditions would instead be P1 blockers:

1. retaining any generated/parameterized vector or hidden normalizer call;
2. needing to change `_page_proof_fixture_leaves.py` or production to complete the layout;
3. being unable to build one of the 46 isolated target vectors with valid admission and only the named predicate false;
4. assigning the implementation author as the independent Terra critic.

No P0 is identified. If condition 2 or 3 is encountered, the executor must stop and report P1 rather than improvise a broader rewrite.

## 1. Exact one-file replacement boundary

The future executor may modify only:

1. `kb_creator/tests/test_page_proof_visual_crosscheck.py`;
2. one new immutable executor receipt under this goal's `handoffs/` directory.

It must not modify `_page_proof_fixture_leaves.py`, `page_proof.py`, any other test, plan, context, project status, contract, prior receipt, release file, configuration, source, output, or Git state.

### 1.1 Delete these current helpers

Delete completely:

- `_assert_reaches_internal_visual_predicate`;
- `_expected_vector`;
- `_resealed_crosscheck_case`;
- `_rebind_crosscheck_root` (currently unused and not part of the canonical evidence path).

Retain `_assert_pre_normalizer_contract` with the exact keyword-only typed signature and complete assertions from Sol section 2.1. Retain only normalizer-free setup/oracle primitives such as `_case_rows`, `_normalized_case`, `_two_boundary_case`, `_parse_crosscheck`, `_seal_crosscheck`, `_reseal_admission_row_for_crosscheck`, the P/F oracles, and block/boundary/inventory seal primitives. They may prepare data but may not call `_normalize_fixture_visual_crosscheck`, select an expected false key, return an expected vector, or perform semantic mutation/repair on behalf of a target test.

### 1.2 Delete or rewrite these current tests

Delete these functions in full; their coverage is replaced by the explicit inventory in section 2:

- `test_private_two_boundary_admission_variant_has_real_boundary_reorder_recovery`;
- `test_literal_two_boundary_p1_root_reviewer_and_boundary_matrix_has_exact_vectors_and_repairs`;
- `test_missing_duplicate_reordered_rows_and_rejected_aggregate_substitutes_fail_closed`;
- `test_pixels_masks_bboxes_and_block_decision_digest_target_only_failures_repair`;
- `test_previsual_transcription_hash_status_order_and_inventory_mutations_fail_closed_then_repair`;
- `test_boundary_geometry_decision_reason_neighbors_column_and_digest_mutations_fail_closed_then_repair`.

Rewrite `test_positive_literal_crosscheck_leaves_have_independent_metadata_and_normalize`: its loop is removed and its positive work moves to the four fixtures below. Keep separate assertion-only positive tests if useful, but they must consume the fixture result and add no normalizer call.

Rewrite `test_binding_helper_ast_containment_and_closed_roots_exclude_final_binding` exactly as section 5 specifies. Retain `test_two_boundary_leaf_assignments_are_direct_literals`. Add `test_visual_crosscheck_normalizer_call_layout_is_literal_and_complete` as section 4 specifies.

## 2. Canonical explicit test topology and exact target inventory

### 2.1 Four named one-call positive fixtures

Add these exact non-parameterized module-scoped pytest fixtures:

```text
positive_two_column_normalized_case
positive_nested_form_normalized_case
positive_visual_only_normalized_case
positive_two_boundary_normalized_case
```

Each fixture constructs only its named case, calls `_assert_pre_normalizer_contract` with an inline all-true 15-key literal dictionary, immediately calls `_normalize_fixture_visual_crosscheck` exactly once, and returns immutable/raw setup plus canonical normalized baseline bytes. No fixture may loop, accept a case parameter, call another positive fixture, or call a target mutation helper. The fourth fixture must also prove the literal P, F, W/render/V metadata, exact pre-visual core, two ordered boundary triples, and normalized content facts required by Sol section 3.2.

All negative/repair tests below consume `positive_two_boundary_normalized_case`. Each reparses fresh literal fourth V bytes for its own mutable tree; no test shares a mutated object.

### 2.2 Exact 46 internal target tests

Create exactly one function for every row below. Every function has exactly two normalizer calls: negative then repaired. The “false key” is the sole `False` entry in the negative call's written vector; the repaired call's written vector has all 15 entries `True`.

| Exact test function | Sole false key |
| --- | --- |
| `test_visual_crosscheck_root_pre_visual_binding_target_only_repair` | `visual_crosscheck_root_binding_matches` |
| `test_visual_crosscheck_root_topology_target_only_repair` | `visual_crosscheck_root_context_matches` |
| `test_visual_crosscheck_root_pre_visual_core_target_only_repair` | `visual_crosscheck_root_context_matches` |
| `test_visual_crosscheck_reviewer_identity_target_only_repair` | `visual_crosscheck_reviewer_matches_contract` |
| `test_visual_crosscheck_reviewer_scope_target_only_repair` | `visual_crosscheck_reviewer_matches_contract` |
| `test_visual_crosscheck_reviewer_independence_target_only_repair` | `visual_crosscheck_reviewer_matches_contract` |
| `test_visual_crosscheck_root_content_seal_target_only_repair` | `visual_crosscheck_content_seal_matches` |
| `test_visual_crosscheck_boundary_missing_final_row_target_only_repair` | `visual_crosscheck_cardinality_matches` |
| `test_visual_crosscheck_boundary_duplicate_final_row_target_only_repair` | `visual_crosscheck_cardinality_matches` |
| `test_visual_crosscheck_boundary_reordered_rows_target_only_repair` | `visual_crosscheck_boundary_region_matches` |
| `test_visual_crosscheck_boundary_aggregate_f0_f2_target_only_repair` | `visual_crosscheck_boundary_region_matches` |
| `test_visual_crosscheck_boundary_source_fragment_target_only_repair` | `visual_crosscheck_boundary_region_matches` |
| `test_visual_crosscheck_boundary_target_fragment_target_only_repair` | `visual_crosscheck_boundary_region_matches` |
| `test_visual_crosscheck_boundary_kind_target_only_repair` | `visual_crosscheck_boundary_region_matches` |
| `test_visual_crosscheck_boundary_source_block_target_only_repair` | `visual_crosscheck_boundary_region_matches` |
| `test_visual_crosscheck_boundary_target_block_target_only_repair` | `visual_crosscheck_boundary_region_matches` |
| `test_visual_crosscheck_boundary_source_column_target_only_repair` | `visual_crosscheck_boundary_region_matches` |
| `test_visual_crosscheck_boundary_target_column_target_only_repair` | `visual_crosscheck_boundary_region_matches` |
| `test_visual_crosscheck_boundary_bbox_target_only_repair` | `visual_crosscheck_boundary_region_matches` |
| `test_visual_crosscheck_boundary_nonconfirm_target_only_repair` | `visual_crosscheck_boundary_decision_matches` |
| `test_visual_crosscheck_boundary_wrong_reason_target_only_repair` | `visual_crosscheck_boundary_decision_matches` |
| `test_visual_crosscheck_boundary_stale_decision_sha_target_only_repair` | `visual_crosscheck_boundary_decision_matches` |
| `test_visual_crosscheck_block_missing_final_row_target_only_repair` | `visual_crosscheck_cardinality_matches` |
| `test_visual_crosscheck_block_duplicate_final_row_target_only_repair` | `visual_crosscheck_cardinality_matches` |
| `test_visual_crosscheck_block_reordered_rows_target_only_repair` | `visual_crosscheck_block_region_matches` |
| `test_visual_crosscheck_block_id_target_only_repair` | `visual_crosscheck_block_region_matches` |
| `test_visual_crosscheck_block_ordinal_target_only_repair` | `visual_crosscheck_block_region_matches` |
| `test_visual_crosscheck_block_disposition_target_only_repair` | `visual_crosscheck_block_region_matches` |
| `test_visual_crosscheck_block_reason_target_only_repair` | `visual_crosscheck_block_region_matches` |
| `test_visual_crosscheck_block_column_target_only_repair` | `visual_crosscheck_block_region_matches` |
| `test_visual_crosscheck_block_bbox_target_only_repair` | `visual_crosscheck_block_region_matches` |
| `test_visual_crosscheck_block_pixel_count_target_only_repair` | `visual_crosscheck_block_region_matches` |
| `test_visual_crosscheck_block_component_evidence_target_only_repair` | `visual_crosscheck_block_region_matches` |
| `test_visual_crosscheck_transcription_empty_bytes_target_only_repair` | `visual_crosscheck_block_transcription_matches` |
| `test_visual_crosscheck_transcription_changed_bytes_old_hash_target_only_repair` | `visual_crosscheck_block_transcription_matches` |
| `test_visual_crosscheck_transcription_wrong_hash_target_only_repair` | `visual_crosscheck_block_transcription_matches` |
| `test_visual_crosscheck_block_nonconfirm_target_only_repair` | `visual_crosscheck_block_decision_matches` |
| `test_visual_crosscheck_block_wrong_reason_target_only_repair` | `visual_crosscheck_block_decision_matches` |
| `test_visual_crosscheck_block_stale_decision_sha_target_only_repair` | `visual_crosscheck_block_decision_matches` |
| `test_visual_crosscheck_inventory_block_digest_value_target_only_repair` | `visual_crosscheck_inventory_matches` |
| `test_visual_crosscheck_inventory_block_digest_order_target_only_repair` | `visual_crosscheck_inventory_matches` |
| `test_visual_crosscheck_inventory_boundary_digest_value_target_only_repair` | `visual_crosscheck_inventory_matches` |
| `test_visual_crosscheck_inventory_boundary_digest_order_target_only_repair` | `visual_crosscheck_inventory_matches` |
| `test_visual_crosscheck_inventory_block_count_target_only_repair` | `visual_crosscheck_inventory_matches` |
| `test_visual_crosscheck_inventory_boundary_count_target_only_repair` | `visual_crosscheck_inventory_matches` |
| `test_visual_crosscheck_inventory_stale_sha_target_only_repair` | `visual_crosscheck_inventory_matches` |

“List/order/count/stale” is now closed mechanically: one wrong digest value and one order case for each of block and boundary lists, one case for each count, and one stale/wrong inventory SHA case, for seven inventory tests total.

### 2.3 Two exact outer-envelope tests

Retain the original Sol outer distinction as exactly two tests:

```text
test_visual_crosscheck_outer_changed_v_with_unchanged_valid_row_rejected
test_visual_crosscheck_outer_changed_row_v_metadata_without_recomputed_f_rejected
```

Each has exactly one normalizer call under the exact error assertion. The first directly proves `visual_crosscheck_leaf_matches_admission=False`; the second directly proves `fixture_admission_is_valid=False`. Neither calls `_assert_pre_normalizer_contract`, and neither is counted as internal predicate evidence.

### 2.4 Exact normalizer call count

The final source must contain exactly **98** AST call sites to `page_proof._normalize_fixture_visual_crosscheck`:

```text
4 positive fixtures x 1 call                    =  4
46 internal target tests x 2 calls              = 92
2 outer-envelope tests x 1 call                 =  2
                                                   --
total                                             = 98
```

There are no other normalizer calls. Because no normalizer call is under a loop, comprehension, parameterized fixture, callback, lambda, or helper, the AST count is also the declared executable evidence layout count.

## 3. Literal vector and mutation/repair policy

At every positive, internal-negative, and repaired call site, `expected_predicates=` is an inline `ast.Dict` with exactly the 15 keys from Sol section 2.2, in that exact order. Every key is an `ast.Constant(str)` and every value is an `ast.Constant(bool)`. Prohibited forms include a name such as `ALL_TRUE`, `_expected_vector(...)`, `dict(...)`, `**` expansion, union, comprehension, subscript, conditional expression, fixture parameter, or mutation of a previously declared mapping.

The helper call is the immediately preceding executable statement. For a negative call inside `with pytest.raises(...)`, the helper expression is the immediately preceding sibling of that `with`; the normalizer is the only executable statement in the `with` body. For a success call, the helper expression is the immediately preceding sibling of the assignment/assertion containing the normalizer. No reseal, rebind, mutation, assignment, callback, or assertion may intervene.

The helper and normalizer must use AST-identical expressions for `row`, `mechanics`, `flow`, and `crosscheck_raw`. The helper additionally receives the exact fixture W/render objects. Every internal negative has the first four admission/leaf predicates true and exactly the table's key false. Every repair mutates the already-mutated tree by only the inverse semantic operation, reseals its downstream closure, has all 15 predicates true, normalizes, and compares `_canonical_json(repaired_normalized)` byte-for-byte with the canonical normalized bytes returned by `positive_two_boundary_normalized_case`.

P is never recomputed during a visual mutation. V and F are each resealed once after the semantic mutation and once after the semantic inverse repair. Downstream hash maintenance is allowed; a second semantic change, baseline reparse as repair, whole-list baseline replacement, whole-row replacement, retry, fixed-point loop, or production hash helper is forbidden.

## 4. Fourth-case structure and exact shape rules

All fourth-case structural tests start with `_parse_crosscheck(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1)`. That parse is the sole mutable source. The positive baseline has exactly two ordered boundary rows:

1. `f0 -> f1`, `within_block`, `b0 -> b0`, columns `1 -> 1`, bbox `[0, 0, 1, 3]`;
2. `f1 -> f2`, `cross_column`, `b0 -> b1`, columns `1 -> 0`, bbox `[0, 0, 4, 3]`.

Both use decision `confirm`, reason `matches_expected_boundary`, the closed boundary schema, and their current decision SHA.

- Missing: remove only row index 1. The remaining row 0 is the aligned prefix. Reseal inventory/content/V/F. Only cardinality is false. Repair inserts the exact literal-baseline row 1 at index 1 into the same mutated tree.
- Duplicate: append a separately parsed exact copy of literal-baseline row 1 after `[row0, row1]`, producing `[row0, row1,row1]`. Do not duplicate row 0. Reseal inventory/content/V/F. Only cardinality is false. Repair pops only the appended final row from the same tree.
- Reorder: exchange the same two row objects to `[row1,row0]`. Cardinality, row decisions, inventory, content, V, and F are current; only boundary region is false. Repair exchanges those same objects back.
- Aggregate-like: preserve cardinality two. Both rows must independently have the exact closed boundary schema and the current digest of the same valid-shape aggregate replay: `f0 -> f2`, `cross_column`, `b0 -> b1`, columns `1 -> 0`, bbox `[0,0,4,3]`, decision `confirm`, reason `matches_expected_boundary`. Thus the list is two repeated valid-shape `f0 -> f2` rows, inventory count is 2, its two digest entries are current, and content/V/F are current. Only boundary region is false. Repair restores row 0 to the literal `f0 -> f1` row and row 1 to the literal `f1 -> f2` row in the same tree, then reseals.

For every repaired structural case, the repaired raw V must equal the literal fourth V bytes before normalization, and the repaired normalized canonical bytes must equal the positive fixture's normalized canonical bytes after normalization.

## 5. Exact AST containment implementation

### 5.1 Mechanical proof of all 98 normalizer calls

`test_visual_crosscheck_normalizer_call_layout_is_literal_and_complete` parses this test module's source with `ast`. It must:

1. collect only calls whose function AST is exactly `page_proof._normalize_fixture_visual_crosscheck`;
2. assert total count `98`;
3. assert an exact literal function-to-call-count map: each of the four named positive fixtures has `1`, each of the 46 named target tests has `2`, each outer test has `1`, and every other function has `0`;
4. assert no collected call has an ancestor `For`, `AsyncFor`, `While`, `ListComp`, `SetComp`, `DictComp`, `GeneratorExp`, `Lambda`, or nested function;
5. for every non-outer call, locate its carrier statement and assert the immediately preceding sibling is a direct `_assert_pre_normalizer_contract(...)` expression;
6. compare `ast.dump(..., include_attributes=False)` for normalizer positional arguments `(mechanics, flow, crosscheck_raw, row)` with the helper's named keywords of the same semantics;
7. assert the helper's `expected_predicates` is a direct 15-entry literal dictionary with the exact ordered keys and constant booleans;
8. assert each positive fixture's vector is all true; each target function's lexical call-vector sequence is exactly `(its_table_false_key, all_true)`; and each outer call has no helper predecessor;
9. assert each negative normalizer is the sole executable statement in an exact `pytest.raises(RawPdfError, match="^page_proof_visual_crosscheck_invalid$")` body;
10. assert no call to `_assert_pre_normalizer_contract` exists without exactly one immediately following internal normalizer carrier.

This meta-test must use a literal expected function map and literal false-key map. It must not derive the expected inventory from discovered test names.

### 5.2 Exact P/F source graph proof

The rewritten `test_binding_helper_ast_containment_and_closed_roots_exclude_final_binding` parses `inspect.getsource(page_proof)` and selects exactly these six top-level functions:

```text
_fixture_pre_visual_binding_payload
_fixture_pre_visual_binding_sha256
_fixture_pre_visual_binding_is_valid
_fixture_admission_payload
_fixture_admission_binding_sha256
_fixture_admission_is_valid
```

It asserts the exact six-helper direct edge set already specified by Sol 5.1. It also fingerprints direct calls, distinguishing `ast.Name` calls from attribute calls:

```text
_fixture_pre_visual_binding_payload:
  names {}; attributes {row.fixture_id.decode}
_fixture_pre_visual_binding_sha256:
  names {_sha256, _canonical_json, _fixture_pre_visual_binding_payload}; attributes {}
_fixture_pre_visual_binding_is_valid:
  names {type, bool, _fixture_pre_visual_binding_sha256}; attributes {_HEX.fullmatch}
_fixture_admission_payload:
  names {_fixture_pre_visual_binding_payload}; attributes {value.update}
_fixture_admission_binding_sha256:
  names {_sha256, _canonical_json, _fixture_admission_payload}; attributes {}
_fixture_admission_is_valid:
  names {type, len, all, _sha256, _fixture_pre_visual_binding_is_valid,
         _fixture_admission_binding_sha256};
  attributes {row.fixture_id.decode, _HEX.fullmatch}
```

Repeated occurrences do not alter these exact sets. The exact body-only module-private `ast.Name` sets remain the six sets in Sol section 5.2; annotations and argument nodes are excluded by walking an `ast.Module` made from `FunctionDef.body`.

For field containment, define a local direct field set per function from `row.<attribute>`. Define the **payload dependency closure**, not the validator-control closure:

```text
P closure root: _fixture_pre_visual_binding_payload
P payload edges: {}
F closure root: _fixture_admission_payload
F payload edges: {_fixture_admission_payload -> _fixture_pre_visual_binding_payload}
```

Union direct `row` fields over each closure. P must equal exactly the eight Sol fields. F must equal exactly those eight plus the five Sol F fields. Validator-only checks of `binding_sha256` and expected-output hashes are intentionally not payload dependencies and must not be folded into this closure. Runtime payload key sets must independently equal P's 10 keys and F's 15 keys from Sol 5.3.

The bytes-constant set in `_fixture_pre_visual_binding_sha256` must equal only `{b"page-proof.fixture-pre-visual-binding.v1\0"}`; the set in `_fixture_admission_binding_sha256` must equal only `{b"page-proof.fixture-admission.v2\0"}`.

Across the four payload/hash functions, reject `For`, `AsyncFor`, `While`, every comprehension/generator, `Lambda`, `ast.Starred`, `**` dictionary expansion (`ast.Dict` with a `None` key or `keyword.arg is None`), whole-row serialization, attribute enumeration, and dynamic field lookup. Passing bare `row` is allowed only in `_fixture_admission_payload -> _fixture_pre_visual_binding_payload`; P payload's `row.fixture_id.decode("ascii")` is the only direct field method call. Across all six functions, reject calls/names for normalizers, registries, visual decision/inventory/content helpers, filesystem/path/environment access, `getattr`, `setattr`, `vars`, `dir`, `globals`, `locals`, `eval`, `exec`, `__dict__`, `dataclasses.asdict`, `importlib`, and `__import__`.

Finally assert the exact runtime P/F payload keys, P and F excluded-field sets, exact two domains, and all four root non-edges:

```text
"binding_sha256" not in _WITNESS_ROOT_KEYS
"binding_sha256" not in _VISUAL_CROSSCHECK_ROOT_KEYS
"pre_visual_binding_sha256" in _WITNESS_ROOT_KEYS
"pre_visual_binding_sha256" in _VISUAL_CROSSCHECK_ROOT_KEYS
```

Any weaker subset assertion is P1.

## 6. Dependencies, branches, data contracts, and risks

Dependency order is fixed:

```text
frozen production P/F predicates and schemas
  -> frozen fourth literal W/render/V leaves
  -> named positive fixtures and canonical normalized baselines
  -> 46 isolated mutation/inverse-repair tests
  -> 98-call layout AST proof plus exact P/F AST proof
  -> bounded seven-suite regression
  -> fresh independent Terra implementation review
  -> orchestrator integration decision
```

Branch rules:

- If the before hashes match the assumptions, execute the one-file replacement.
- If only `test_page_proof_visual_crosscheck.py` drifted, stop and report the new hash to the orchestrator before overwriting or reconciling concurrent work.
- If leaves or production drifted, stop with P1; this packet cannot repair them.
- If an isolated case yields more than the named false predicate, stop with P1 and report the exact vector; do not weaken the vector or add a second expected false.
- If all implementation DoD items pass, request a new independent Terra implementation review. Do not advance 4b.7 directly.

Primary risks are accidental call hiding, vector aliasing, a baseline-as-repair shortcut, aggregate rows with invalid shape or stale seals, inventory mutations that create two failures, and AST checks that inspect selected examples rather than an exact graph. The explicit function inventory and source meta-tests are mandatory controls for those risks.

## 7. Executor Definition of Done

The bounded executor is done only when all are true:

1. Only `test_page_proof_visual_crosscheck.py` and one new executor receipt changed.
2. Production and fixture-leaf hashes remain exactly the values recorded above.
3. All deleted helpers/families are absent; no generated expected-vector facility remains.
4. The four named positive fixtures exist, are non-parameterized, and contain one guarded normalizer call each.
5. All 46 exact target functions exist; each has one isolated negative and one same-object inverse repair, with two explicit guarded normalizer calls.
6. The two exact outer tests exist and remain outside the internal helper contract.
7. AST mechanically proves exactly 98 normalizer call sites, exact per-function distribution, no loop/template/helper calls, exact immediate guards, and literal vectors.
8. Every negative vector has exactly its named false key; every repaired vector is all true.
9. Every repaired raw fourth V equals the literal fourth baseline and every repaired normalized canonical result equals the positive fourth normalized canonical result.
10. Missing, duplicate row 1, reorder, and two-valid-shape repeated `f0 -> f2` aggregate cases satisfy section 4 exactly.
11. The exact seven inventory targets and every root/reviewer/boundary/block/transcription/decision/mask target are present.
12. The P/F AST test implements the exact calls, edges, private names, payload closure fields, keys, domains, prohibited constructs, and root non-edges in section 5.2.
13. The previously mandated seven-suite command passes with the confirmed interpreter; no live input, browser, network, parser/render build, output, or Git operation is used.
14. The new receipt records before/after hashes, exact command/result, exact `98` call count, `46` target count, files changed, blockers, next action, elapsed time, token use, timestamp, policy owner, assignment state, and scoped override.

Passing tests without the AST/source-layout proof is not DoD.

## 8. Revised independent Terra implementation checklist

The reviewer must be a fresh independent Terra critic at `high` who neither implemented nor materially designed this candidate. This is an implementation review, not a release review.

1. Read governance, plan/context, the accepted P/F architecture, Sol's exact evidence packet, both executor receipts, the prior Terra rejection, this clarification, and the new executor receipt.
2. Confirm only `test_page_proof_visual_crosscheck.py` and the new receipt changed in this bounded packet; confirm production and fixture-leaf hashes exactly.
3. Confirm the old helper, generated vector function, loop matrix, loop positive family, and four legacy families are absent.
4. Independently enumerate AST calls to `_normalize_fixture_visual_crosscheck`; require exactly 98 and the exact `4 + 92 + 2` distribution.
5. Inspect the call-layout meta-test for self-fulfilling discovery: its expected function/count/false-key inventories must be literal and independent of discovered names.
6. Confirm every internal call has an immediately adjacent helper using AST-identical row/mechanics/flow/V expressions and a direct 15-key bool-literal dictionary; confirm no helper call is orphaned.
7. Confirm all four positive fixtures are named, non-parameterized, one-call fixtures and the fourth positive proves literal metadata/P/F/core/two-boundary facts.
8. Confirm all 46 named target tests exist and no target is covered only by alias, parametrization, loop, generic lambda, or retained legacy case.
9. For every target, confirm the negative has exactly the specified one-false vector and the repaired call is all true; independently sample at least one case from each of root, reviewer, boundary structure, boundary region, boundary decision, block structure, block region/mask, transcription, block decision, and inventory.
10. Confirm all target repairs operate on the mutated tree, restore only the target semantic value/list operation, reseal only its closure, and compare repaired raw and normalized canonical bytes to the fourth baseline. Any baseline reparse/replacement used as repair is P1.
11. Confirm fourth missing removes row 1, duplicate appends exact row 1, reorder swaps the same two rows, and aggregate consists of two current, closed, valid-shape repeated `f0 -> f2` rows at cardinality 2. Confirm their exact vectors and inverse repairs.
12. Confirm seven independent inventory cases: block value/order, boundary value/order, block count, boundary count, stale inventory SHA. Each must keep all non-inventory predicates true.
13. Reconstruct the six-function P/F graph from production source and compare it with the test's exact call fingerprints, direct edges, body-only private names, payload-closure field sets, payload keys, domains, prohibited constructs, and V2 root non-edges. A subset check is P1.
14. Confirm the two outer tests are exactly the stale V leaf and invalid F cases, have no internal helper, and are not credited as internal target evidence.
15. Run the exact bounded seven-suite command with a confirmed interpreter and record exact result and post-review hashes.
16. Issue `accept` only with no P0/P1. A passing suite, 98 count without exact distribution, generated vector, hidden call, missing target, multi-false vector, invalid aggregate, shortcut repair, weak AST graph, production/leaf delta, scope expansion, or critic-author overlap is P1 reject.

Packet 4b.7, production registry activation, live preflight, output/build work, and release remain blocked until the orchestrator integrates a fresh independent Terra acceptance. Final release still requires the separate Terra release gate.

## 9. Handoff metadata

- Scope: architecture clarification for a single future test-file replacement; no implementation or acceptance.
- Files checked: `AGENTS.md`; `docs/governance/nri_goal_governance.md`; assigned `plan.md` and complete `context.md`; `sol_page_proof_visual_crosscheck_binding_remediation_spec_20260811.md`; `sol_page_proof_visual_crosscheck_evidence_remediation_packet_20260811.md`; `executor_page_proof_visual_crosscheck_evidence_remediation_20260811.md`; `executor_page_proof_visual_crosscheck_evidence_restart_20260811.md`; `terra_page_proof_visual_crosscheck_evidence_remediation_review_20260811.md`; `kb_creator/pdf_raw/page_proof.py`; `kb_creator/tests/_page_proof_fixture_leaves.py`; `kb_creator/tests/test_page_proof_visual_crosscheck.py`.
- Files changed: this new immutable handoff only.
- Verification/evidence: read-only source, contract, receipt, hash, call-site, and function-layout inspection. No tests, live input, browser, network, parser, renderer, build, output, or Git operation was run.
- Blockers: bounded one-file implementation and a fresh independent Terra implementation acceptance remain required. The current test file is unaccepted working state.
- Next action: the orchestrator may assign one fresh bounded executor to sections 1–7, with only the test file and a new receipt writable; after completion it may assign a distinct independent Terra critic to section 8.
- Elapsed time: approximately 18 minutes active architecture inspection and specification.
- Token use: exact receipt-final usage unavailable; runtime goal reported `133574` tokens at the pre-write capture.
- Timestamp: `2026-08-11T15:37:30.7166250+03:00`.
- Orchestrator policy owner: `gpt-5.5` at `medium` (`platform-unverified`).
- Assignment state: `platform-unverified`.
- Scoped override: Sol architecture clarification and this receipt only; no orchestration transfer, implementation authority, critic authority, release authority, or scope expansion.

This receipt is immutable. Any correction must use a new handoff path and explicitly supersede this file; prior receipts must not be modified.

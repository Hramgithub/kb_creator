# Sol P1 remediation specification — Packet 4b.2 fixture admission

## Decision and scope

Remediate only Terra P1 findings in Packet `4b.2`: add a closed three-row literal admission registry validator, a separately typed literal expected tuple, literal helper metadata, and fully resealed target-only evidence. Preserve:

- `_PRODUCTION_FIXTURE_ADMISSION == ()`;
- a separate empty production expected tuple;
- topology coverage as the first public gate;
- exact public failure `page_proof_stage_a_fixture_coverage_incomplete` while topology coverage is incomplete;
- `page_proof_fixture_registry_invalid` as the next gate under a private complete topology inventory;
- no proof-like output or new public API/state.

Allowed changes are exactly:

- `kb_creator/pdf_raw/page_proof.py`;
- `kb_creator/tests/_page_proof_fixture_leaves.py`;
- `kb_creator/tests/test_page_proof_fixture_admission.py`;
- `kb_creator/tests/test_page_proof_coverage_guard.py` only if needed to preserve the existing next-gate assertion.

No other code, test, plan, context, status, live/source/output/configuration, Git, rebuild or release artifact is in scope.

## 1. Exact literal test metadata

`_page_proof_fixture_leaves.py` must retain the three raw `bytes` tuples and add frozen, closed metadata whose values are written literally. No `len()`, `hashlib`, comprehension, row constructor, registry view or mutable container may produce the expected metadata.

Leaf order is exactly `fixture_id`, `witness`, `render_png`, `independent_visual_crosscheck`:

| fixture | literal lengths | literal SHA-256 values in the same order |
|---|---|---|
| `page-proof.positive-two-column.v1` | `(33, 18, 14, 17)` | `e40137c0f1597d0a7b4aac30969a521e40c28d8019f02be2c10e21593dc127c9`; `55e46169779e6024da782ee095e31cad352e2a95bf83ba55ee999c5944fb8bf1`; `7c07119bb74fc885f24e67004db46d2a36521c3b7b20ed21fda400f4e1a7a0ab`; `a919bec03c64e62fb396ca2b8f8e83b03833a13035bad6db78eae8539601935f` |
| `page-proof.positive-nested-form.v1` | `(34, 19, 15, 18)` | `a3b7a43716c68188aade57ef01da907d582b63fb4d478cb6fe01f6c0bbfdf558`; `e2b0def2f8b443bdc2675f1a5fb723054c181fb70193a9abe1d3807dc5dcac98`; `87f4e1ee14cbd163a1fab81d5684b1e767cf73717bf08764ef6072dbd786a939`; `c71e0866d337610fa633c3515ad01ce3659a0a2e0c844c0f62586ba9e2b20291` |
| `page-proof.positive-visual-only.v1` | `(34, 19, 15, 18)` | `0de3f42cefdd92ad05303f3cc39043f98a990468c220ed3c1ebd01867d2ea998`; `a49c9817757aefa02b82d309e704857c100f24bd58b4f0de658ca4896062dbfe`; `b9378a7ac8489f4552554255f13df626502e1bef9dadd71da16b1b15b9959eb4`; `37bdfa306688b8c242317bc4e951eff1823a48a86225410237bf20554c604059` |

For the private validator proof only, use the already accepted Packet 4b.1 private complete-inventory digest:

```text
d0891ce46fc9cb3aeee366cf78610996b3e2a34e94d85c47e9d212599a438ac6
```

This is test-only and must never populate production admission. The three private rows bind respectively:

| page-proof fixture | Stage A fixture | Stage A authority content | binding | expected candidate test seal | expected reviewed test seal |
|---|---|---|---|---|---|
| two-column | `stage-a.positive-two-column.v1` | `890a9cef3ce995e7cb7881c035baa3e1e5a4c782f1827847b640c93fb28eafef` | `e1066a21aa2e00338232719cdfbbb7bc431f3f21077c330fe03e3270a5f0da0b` | `9bc92192ee0e03282585b83d6902b9367b1960b897c20da0c0c7240725c73e21` | `91ceaadb97a611699e648ca865be60951709f09b1c5cf555ceb1f3c94cf427c0` |
| nested Form | `stage-a.positive-nested-form.v1` | `8726e5d36b7acba9d96eacdcd62a57da00d7f4cfdd4df79cd6c63106d2e353e7` | `443d48c0b05aa0737209176c7398f1acab048cd0b9826bede578c63de668decc` | `c91d828ac9d5225df07efa76d0f854717ae67c5fb193d427f1992ab51631e929` | `a3382a5a0c432967419b6266156d1b132e22ef7f44ecc8ea8043b75da7d93d7b` |
| visual-only | `stage-a.identity-single-use.v1` | `e10859438e4ccef9ea6fdff9c8e3c923e71f39c4ae1b2c6a420d4319a1c468ed` | `a0d6e226d6db1ebf5914e59a1194219f1f42c8eb2c032bb391815ba888ce8769` | `98f9ccd0bf6d8c02a977472fcad6ac9feed628fd6a2943464307b9f4860d744a` | `696cac67d638d93b51d4d475e34205cf5b4f432fcc517c21bdab6c51a9e8ccd3` |

The expected-output values above are explicit non-proof structural test seals. They are not provisional Packet 4b.7 outputs and cannot enter production.

## 2. Independent expected tuple

Add `_fixture_admission_primitives(row)` with this exact field order:

```text
fixture_id
fixture_id_byte_length
fixture_id_sha256
stage_a_fixture_id
stage_a_authority_content_sha256
required_topology_inventory_content_sha256
witness_byte_length
witness_sha256
render_png_byte_length
render_png_sha256
independent_visual_crosscheck_byte_length
independent_visual_crosscheck_sha256
binding_sha256
expected_candidate_sha256
expected_reviewed_ledger_sha256
```

Tests must define:

- `_PRIVATE_FIXTURE_ADMISSIONS`: three literal `_FixtureAdmission` instances in the exact two-column, nested-Form, visual-only order;
- `_PRIVATE_EXPECTED_FIXTURE_ADMISSION_PRIMITIVES`: a separately written `tuple[tuple[object, ...], ...]` containing every primitive above in the same order.

The expected tuple must not call `_fixture_admission_primitives`, read the rows, unpack helper metadata, hash bytes, or use a comprehension. Assert that its type is exactly `tuple`, each child type is exactly `tuple`, and it is a distinct object graph from the dataclass rows.

Production remains explicitly inactive:

```python
_PRODUCTION_FIXTURE_ADMISSION: tuple[_FixtureAdmission, ...] = ()
_PRODUCTION_EXPECTED_FIXTURE_ADMISSION_PRIMITIVES: tuple[tuple[object, ...], ...] = ()
```

Empty production literals are not a valid registry and must cause the next-gate registry error after complete topology coverage.

## 3. Registry validator and exact order

Add `_fixture_admission_registry_is_valid(rows, expected_primitives, required_topology_content_sha256) -> bool`. It performs these checks in order and returns only `True`/`False`:

1. Exact container types: all three arguments are exact expected primitive types; no subclass, list, iterator or coercion.
2. Required topology digest is lower-case 64-hex.
3. Rows and expected tuple each contain exactly three entries; empty, partial or extra registries fail.
4. Every row type is exactly `_FixtureAdmission`; every expected child type is exactly `tuple` of length 15.
5. Ordered fixture ids equal exactly `(b"page-proof.positive-two-column.v1", b"page-proof.positive-nested-form.v1", b"page-proof.positive-visual-only.v1")`; duplicates, aliases and reorder fail.
6. Ordered Stage A `(fixture_id, authority_content_sha256)` pairs equal exactly the three pairs in section 1.
7. Every row repeats the exact supplied topology digest.
8. Compare `tuple(_fixture_admission_primitives(row) for row in rows)` to the independently supplied expected tuple. Any fully resealed substitution or changed expected-output hash fails here.
9. Run `_fixture_admission_is_valid` on every row. Tighten it to require all four byte lengths to be exact positive integers (`> 0`), exact ASCII fixture bytes, exact string/int field types, lower-case 64-hex hashes, exact fixture-id hash and exact binding recomputation.
10. Require uniqueness of fixture ids, binding hashes and each complete `(witness length/hash, render length/hash, cross-check length/hash)` leaf tuple.

The validator does not decode JSON/PNG, inspect authority objects, access files, or return rows.

After topology coverage succeeds, `_require_complete_stage_a_fixture_coverage()` must call this validator with both empty production tuples. Invalid/empty production admission raises exactly `RawPdfError("page_proof_fixture_registry_invalid")`. While topology coverage is incomplete, it must still raise the coverage error before this call and before caller access.

## 4. Fully resealed target-only matrix

Every semantic negative starts from the same valid three-row private registry, leaves the independent expected tuple unchanged, changes one declared target, and recomputes all dependent self-seals. Before asserting registry rejection, assert the changed row still passes `_fixture_admission_is_valid` whenever the target is not the binding seal itself.

Required cases:

| target | mutation and resealing |
|---|---|
| fixture identity | replace fixture bytes with an ASCII alias; recompute byte length, fixture hash and binding |
| fixture length | change bytes so the new literal length is valid; recompute fixture hash and binding |
| Stage A fixture | substitute another valid Stage A fixture id; recompute binding |
| Stage A content | substitute another valid authority content hash; recompute binding |
| topology digest | substitute another lower-case 64-hex digest; recompute binding |
| witness leaf | replace witness length/hash with another row's valid pair; recompute binding |
| render leaf | replace PNG length/hash with another row's valid pair; recompute binding |
| visual cross-check leaf | replace cross-check length/hash with another row's valid pair; recompute binding |
| complete cross-pair | replace all three leaf length/hash pairs with another row's valid leaves; recompute binding |
| expected candidate | replace only with a different lower-case 64-hex value; binding remains unchanged by contract |
| expected reviewed | replace only with a different lower-case 64-hex value; binding remains unchanged by contract |
| binding seal | replace only the binding with another 64-hex value; row self-check must fail |
| duplicate | repeat one otherwise valid row; registry fails uniqueness/order |
| reorder | swap two otherwise valid rows |
| missing/extra | remove one row or append one otherwise valid row |
| expected tuple independence | mutate/reorder one expected child while rows remain valid; list/comprehension-derived or wrong-shaped expected input fails exact type/shape/value checks |

Also retain closed malformed checks for wrong field types, non-ASCII fixture id, zero/negative/bool lengths, non-lower-case/non-64-hex hashes and stale fixture/binding seals. These are schema negatives, not substitutes for the fully resealed semantic matrix.

For every matrix row, the repaired positive is mandatory: restore only the declared target (and its necessary dependent seals), then assert all three of:

```text
_fixture_admission_is_valid(repaired_row) is True
_fixture_admission_registry_is_valid(repaired_rows, literal_expected_tuple, private_topology_digest) is True
the untouched canonical three-row registry still passes after the negative
```

No test may construct canonical rows with `len()`, `hashlib.sha256()`, `_fixture_admission_binding_sha256()`, or `replace()` from helper bytes. Those operations are permitted only to reseal a deliberately mutated private negative. The canonical positive rows and expected tuple must be literal.

## 5. Definition of done and evidence

- Terra's resealed witness cross-pair, resealed topology-digest mutation and changed expected-candidate hash all pass row self-validation where applicable but fail registry validation.
- All fields, every leaf cross-pair, duplicate/reorder/missing/extra and expected-tuple attacks have target-only rejection plus repaired-positive evidence.
- The production admission and production expected tuple remain empty.
- Existing poison arguments remain untouched and all public calls still emit the coverage error under current incomplete topology inventory.
- A private complete topology inventory reaches only `page_proof_fixture_registry_invalid` because production admission is empty.
- No decoder, authority access, fixture selection, candidate, ledger, review or replay output is added.
- Run exactly:

```text
python -B -m pytest -q -p no:cacheprovider \
  kb_creator/tests/test_page_proof_coverage_guard.py \
  kb_creator/tests/test_page_proof_stage_a_topology_inventory.py \
  kb_creator/tests/test_page_proof_fixture_admission.py
```

Packet 4b.2 is eligible for a new independent Terra implementation review only after the focused suite passes and the review confirms the registry rejects fully resealed substitutions rather than merely stale bindings.

## Receipt metadata

- Goal id: `20260809-innsmouth-page-level-consumer-proof`.
- Step id: `4b.2-P1-spec`.
- Scope/result: implementation-ready remediation for Terra's two Packet 4b.2 P1 findings only; no implementation or acceptance performed.
- Files checked: goal `plan.md`; Packet 4b.2 section of `sol_page_proof_implementation_packetization_20260809.md`; `terra_page_proof_fixture_admission_implementation_review_20260809.md`; current `pdf_raw/page_proof.py`; current fixture helper and fixture-admission test; Stage A literal rows.
- Files changed: this handoff only.
- Verification/evidence: read-only source inspection and independent recomputation of literal leaf lengths/hashes and private binding values; no test suite run.
- Candidate hashes checked: `page_proof.py=2764C2C064C9E152688DCA131024598AE07970BCB67ABAA2D639E4406B8FB77E`; fixture helper `C2334C48D3DAA46110A5CCEB3B01B24CE2FAC88D591FB8AFFA993CE771208A2D`; admission test `7435C4F91BD5CDB442E8022C7D2DD81381B5018556FC4880C412DC0CBE6873EF`.
- Blockers: none for bounded remediation; topology acceptance remains separately incomplete and therefore public coverage must remain closed.
- Next action: bounded executor edits only the four allowed files, runs the exact focused suite, and requests a fresh independent Terra review.
- Elapsed active time: approximately `7 minutes`.
- Token use: `unavailable`.
- Timestamp: `2026-08-09T23:05:54.1888407+03:00`.
- Role/model/effort: Sol architect / platform-unverified / high.
- Orchestrator policy owner: `gpt-5.5` medium (platform-unverified).
- Assignment state: `platform-unverified`.
- Scoped override: this fixture-only P1 remediation handoff path only; no code/tests/plans/context/status/live files/Git.

This immutable receipt does not transfer orchestration ownership and is not a release review.

# Sol architecture handoff — Packet 4b.6-r binding remediation specification

## Receipt and decision

- Goal id: `20260809-innsmouth-page-level-consumer-proof`.
- Step id: `4b.6-r-architecture`.
- Role: Sol architecture/root-cause/remediation specification; requested effort `high`.
- Actual model/effort: `platform-unverified`.
- Orchestrator policy owner: `gpt-5.5` at `medium` (`platform-unverified`).
- Assignment state: `platform-unverified`.
- Scoped override: user-authorized architecture handoff at this path only; no code, test, plan, context, status, output, Git, browser, network, parser, renderer, or release work.
- Result: **production binding-boundary remediation is required; a test-only fixed-point or stale/interim-row projection is forbidden.**

The narrow accepted design is a two-seal production contract:

1. an immutable `pre_visual_binding_sha256`, computed before either witness or independent visual-crosscheck bytes exist and embedded by those two artifacts; and
2. the final `binding_sha256`, computed after the witness/render/crosscheck leaves are sealed and used by later candidate/review/ledger artifacts.

An immutable pre-visual projection is therefore permitted only as an explicit production field and validator boundary. It is not permitted as a test-only substitute for the existing full admission binding. `PageProofFixtureAdmission.v1` and the current Witness/CrossCheck root binding semantics are superseded narrowly by this section; all unrelated Packet 4b.1–4b.6 contracts remain in force.

## 1. Root cause and rejected constructions

The current graph is cyclic:

```text
crosscheck raw
  -> independent_visual_crosscheck length/SHA
  -> _FixtureAdmission.binding_sha256
  -> crosscheck root.fixture_binding_sha256
  -> crosscheck raw
```

The same full-binding back-reference exists in the current witness root. It is hidden in the present private tests because the admission row can retain earlier placeholder witness metadata while a different full witness literal is passed directly to the mechanics normalizer. That layering cannot become a valid activated admission row in Packet 4b.7 and must not be preserved as evidence.

Terra's two rejections establish both failure modes:

- the first candidate never passed the stale outer crosscheck length/SHA and therefore did not reach the intended visual predicates;
- the remediation passed superficial outer comparisons by computing an interim binding, rebinding the root, changing the crosscheck leaf hash, and then leaving the final row binding stale. The row was not valid under `_fixture_admission_is_valid`.

The following are forbidden:

- fixed-point search, repeated hashing until stable, a bounded retry loop, or acceptance of a coincidental digest;
- an interim/stale row whose `binding_sha256` does not recompute from its final fields;
- omitting `_fixture_admission_is_valid` or the exact leaf-tuple match from pre-normalizer evidence;
- changing only tests while production still compares a witness/crosscheck back-reference to the full final admission binding;
- silently redefining the existing `fixture_binding_sha256` field to mean two different hashes in different packets;
- leaving witness metadata pinned to placeholder bytes while normalizing different witness bytes;
- using the normalizer or production seal helpers as the oracle that constructs its own expected inputs.

## 2. Corrected production schemas and exact hash graph

### 2.1 Admission row

The private frozen admission representation becomes the conceptual `PageProofFixtureAdmission.v2` and contains exactly, in contract order:

```text
fixture_id: ASCII bytes
fixture_id_byte_length
fixture_id_sha256
stage_a_fixture_id
stage_a_authority_content_sha256
required_topology_inventory_content_sha256
render_png_byte_length
render_png_sha256
pre_visual_binding_sha256
witness_byte_length
witness_sha256
independent_visual_crosscheck_byte_length
independent_visual_crosscheck_sha256
binding_sha256
expected_candidate_sha256
expected_reviewed_ledger_sha256
```

Moving the render pair before the witness pair is a contract clarification only; canonical payload keys, not dataclass position, determine hashes. Expected output hashes remain after and outside both bindings.

Define the immutable pre-visual payload exactly as:

```text
{
  fixture_id,
  fixture_id_byte_length,
  fixture_id_sha256,
  stage_a_fixture_id,
  stage_a_authority_content_sha256,
  required_topology_inventory_content_sha256,
  render_png_byte_length,
  render_png_sha256,
  witness_schema: "kb_creator.pdf_raw.PageProofWitnessV2",
  visual_crosscheck_schema: "kb_creator.pdf_raw.IndependentPageVisualCrossCheckV2"
}
```

and:

```text
pre_visual_binding_sha256 = sha256(
  b"page-proof.fixture-pre-visual-binding.v1\0" +
  canonical_json(pre_visual_payload)
)
```

Define the final admission payload as every admission field from `fixture_id` through `independent_visual_crosscheck_sha256`, including the stored `pre_visual_binding_sha256`, but excluding `binding_sha256` and both expected output hashes. Then:

```text
binding_sha256 = sha256(
  b"page-proof.fixture-admission.v2\0" +
  canonical_json(final_admission_payload)
)
```

`_fixture_admission_is_valid(row)` must independently recompute and require both hashes. The primitive expected tuple grows to sixteen fields and remains an independently written literal; it must include both bindings and all leaf metadata. The inactive production admission registry remains empty in this remediation.

### 2.2 Witness and visual-crosscheck roots

The witness root becomes `kb_creator.pdf_raw.PageProofWitnessV2`. Its closed key set replaces `fixture_binding_sha256` with `pre_visual_binding_sha256`. The witness normalizer compares that field only to the row's recomputed valid pre-visual binding.

The independent visual root becomes `kb_creator.pdf_raw.IndependentPageVisualCrossCheckV2`. Its closed key set likewise replaces `fixture_binding_sha256` with `pre_visual_binding_sha256`. Its content seal, block/boundary decision seals, inventory seal, reviewer contract, topology digest, and `pre_visual_evidence_core_sha256` remain otherwise unchanged.

The full final `binding_sha256` is reserved for candidate/review/ledger admission projection and must not occur in either WitnessV2 or CrossCheckV2 bytes. Candidate/review schema names and public signatures do not change in this packet.

### 2.3 Acyclic dependency graph

```text
fixture/Stage-A/topology identity + literal render bytes
                         |
                         v
              pre_visual_binding_sha256 (P)
                    /                 \
                   v                   v
       WitnessV2 bytes (W)      pre-visual mechanics/flow (E)
                   |                   |
                   |                   v
                   |        CrossCheckV2 decisions + P + E
                   |                   |
                   v                   v
              W length/SHA       CrossCheckV2 bytes (V)
                    \                 /
                     v               v
                 final admission binding_sha256 (F)
                                 |
                                 v
                  candidate/review/ledger projection
```

Required non-edges are as important as the edges:

- `P` does not depend on W, V, F, candidate, review, or expected-output hashes.
- WitnessV2 and CrossCheckV2 do not contain F.
- `F` may depend on P and the final W/render/V leaf pairs, but does not feed back into any of them.
- expected candidate/reviewed hashes do not feed either P or F.
- no candidate/review/ledger byte is constructed or activated in 4b.6-r.

This graph has the single topological build order `render -> P -> witness -> mechanics/flow E -> crosscheck -> F`. No iterative step exists.

## 3. Exact future executor scope

### Allowed production/test files

- Modify `kb_creator/pdf_raw/page_proof.py` only for the two-seal row, V2 closed roots, pure named predicates, and corresponding private normalizer comparisons.
- Modify `kb_creator/tests/_page_proof_fixture_leaves.py` only to replace affected witness/crosscheck literal bytes and independently written P/F/length/SHA metadata; it must remain literal-only.
- Modify `kb_creator/tests/test_page_proof_fixture_admission.py` for the V2 row, independent two-seal oracle, primitive tuple width, registry, cross-pair, and repair evidence.
- Modify `kb_creator/tests/test_page_proof_closed_schemas.py` only for the two renamed closed-root fields/schema literals and V2 row shape.
- Modify `kb_creator/tests/test_page_proof_witness_render_components.py` only to use exact admitted WitnessV2/render leaf pairs and valid V2 rows.
- Modify `kb_creator/tests/test_page_proof_flow_adjacency.py` only for mechanical V2 row/literal adaptation; flow rules must not change.
- Modify `kb_creator/tests/test_page_proof_visual_crosscheck.py` for the valid-admission matrix in sections 5–7.
- Modify `kb_creator/tests/test_page_proof_stage_a_topology_inventory.py` only where mechanical construction of `_FixtureAdmission` is required for the unchanged next-gate assertion.
- Add one immutable executor receipt under this goal's `handoffs/` directory.

No other source, test, plan, context, status, manifest, output, or configuration file is authorized. If another file proves necessary, stop and return a blocker; do not widen scope silently.

### Explicitly forbidden

- Production registry activation, candidate/review/replay implementation, public terminal, public API/state/error change, or Packet 4b.7 work.
- Live Innsmouth, any PDF/source, EN/RU/Keeper material, HTML/PDF output, rebuild, parser, renderer, PIL, filesystem leaf loading, environment/config access, browser, network, subprocess, dynamic import/plugin, or Git.
- Edits to Stage A, `raw_authority_projection.py`, `raw_interpreter_authority.py`, `page_capable.py`, or any acceptance/status artifact.
- A test helper that opens files, derives its literal metadata at import time, mutates shared expected objects, or calls production hashing/normalization to create its baseline oracle.

## 4. Required named internal predicates

The executor must factor the binding and visual gates into the following private, pure predicates. They may accept only already type-checked immutable/private values, return `bool` or an exact normalized value, and perform no mutation or I/O. `_normalize_fixture_visual_crosscheck` remains the fail-closed orchestrator and maps any false predicate to the existing exact `page_proof_visual_crosscheck_invalid` error.

Binding/admission predicates:

```text
_fixture_pre_visual_binding_payload
_fixture_pre_visual_binding_sha256
_fixture_pre_visual_binding_is_valid
_fixture_admission_binding_sha256              # v2 final F
_fixture_admission_is_valid                    # requires valid P and F
_fixture_admission_row_matches_derive_leaves   # exact W/render/V len+SHA tuple
_visual_crosscheck_leaf_matches_admission
```

Visual predicates, in normalizer order after canonical closed-root decoding:

```text
_visual_crosscheck_root_binding_matches
_visual_crosscheck_root_context_matches        # topology + pre-visual core
_visual_crosscheck_reviewer_matches_contract
_visual_crosscheck_cardinality_matches
_visual_crosscheck_block_region_matches
_visual_crosscheck_block_transcription_matches
_visual_crosscheck_block_decision_matches
_visual_crosscheck_boundary_region_matches
_visual_crosscheck_boundary_decision_matches
_visual_crosscheck_inventory_matches
_visual_crosscheck_content_seal_matches
```

`_visual_crosscheck_root_binding_matches` compares only CrossCheckV2 `pre_visual_binding_sha256` to a row that has already passed `_fixture_admission_is_valid`. Region predicates cover ordered identity, ordinal, disposition/reason, column, replayed bbox, pixel count, component evidence, adjacency neighbor ids/kind/columns, and boundary union bbox. Decision predicates cover exact confirm/reason and the decision-specific digest. The inventory predicate covers ordered digest lists, exact counts, and inventory digest.

Tests must be able to name the intended false predicate directly. A generic `RawPdfError` alone is insufficient proof of target reachability.

## 5. Valid-admission construction before the normalizer

Every positive, internal adversarial, and repaired case must satisfy this pre-normalizer contract using the exact bytes passed to mechanics/visual normalization:

```text
1. independent oracle recomputes P from identity/topology/render only;
2. literal WitnessV2 contains P and its own content seal is current;
3. mechanics and flow are normalized from that exact witness/render pair;
4. literal or mutation-derived CrossCheckV2 contains P and the resulting E;
5. block/boundary digests, inventory, and root content are sealed in dependency order;
6. the row receives exact W/render/V lengths and SHA-256 values;
7. independent oracle computes final F exactly once;
8. assert _fixture_pre_visual_binding_is_valid(row);
9. assert _fixture_admission_is_valid(row);
10. assert _fixture_admission_row_matches_derive_leaves(row, W, render, V);
11. assert every non-target named visual predicate is true;
12. invoke _normalize_fixture_visual_crosscheck.
```

The existing placeholder `witness:*`, `png:*`, and `visual:*` leaf families may remain only for the isolated 4b.2 hash-first registry tests if still required there. They must not be mixed into a 4b.4–4b.6 row whose normalizers consume the full WitnessV2/render/CrossCheckV2 literals.

Three immutable positive cases are mandatory: two-column, nested Form, and visual-only. Each must have independently written literal W/render/V lengths, SHA-256 values, P, and F in `_page_proof_fixture_leaves.py`. The positive test must prove all pre-normalizer conditions and the expected normalized content/block/transcription/boundary/pre-visual-core values.

A fourth private valid-admission boundary-matrix variant is required if necessary to obtain at least two ordered adjacency rows. It may reuse the two-column witness/render identity but must use a literal flow/crosscheck expectation with, for example, two fragments in one included block followed by the cross-column fragment. This is needed to make boundary reordering a real mutation rather than a no-op. It is not a fourth production registry row.

## 6. Target-only adversarial and repair matrix

For every internal row below, mutate exactly the named semantic target, recompute only dependent seals, rebuild the exact V leaf pair and final F, and prove the row plus exact W/render/V tuple are valid before calling the normalizer. The target named predicate must be false and all earlier/non-target predicates true. The normalizer must raise the exact visual error. Restore only the target semantic value, recompute its dependent closure, and require byte-for-byte baseline normalized output.

| class | required targets | dependent reseal after mutation | intended named predicate |
|---|---|---|---|
| root binding/context | CrossCheckV2 P; topology digest; pre-visual core | root content -> V leaf -> F | root binding or root context |
| reviewer | empty identity; wrong scope; non-independent value | root content -> V leaf -> F | reviewer contract |
| block structure | missing, duplicate, reordered block row | affected decision list -> inventory -> root content -> V leaf -> F | cardinality or block region |
| boundary structure | missing, duplicate, reordered boundary row; aggregate-like substitute | affected decision list -> inventory -> root content -> V leaf -> F | cardinality or boundary region |
| block replay | block id/ordinal; disposition/reason; column; bbox; pixel count; component evidence | block decision -> inventory -> root content -> V leaf -> F | block region |
| transcription | empty bytes; changed bytes with old hash; changed hash | block decision when its committed payload changes -> inventory -> root content -> V leaf -> F | block transcription |
| block decision | reject/non-confirm; wrong reason; stale/wrong decision digest | inventory from the deliberately supplied decision digest -> root content -> V leaf -> F | block decision |
| boundary replay | neighbor fragment ids; source/target block ids; kind; columns; union bbox | boundary decision -> inventory -> root content -> V leaf -> F | boundary region |
| boundary decision | reject/non-confirm; wrong reason; stale/wrong decision digest | inventory from the deliberately supplied decision digest -> root content -> V leaf -> F | boundary decision |
| inventory | block digest order/list; boundary digest order/list; either count; stale inventory digest | root content -> V leaf -> F | inventory |
| root seal | stale/wrong root content digest | V leaf -> F; do not repair root content | content seal |

Masks are represented at this layer by the replayed `component_evidence_sha256` commitment over component id, bbox, mask SHA, and pixel count. A mask target must therefore alter the expected component evidence commitment while keeping the mechanics input fixed; it must not mutate the PNG or invoke a renderer.

Two outer-envelope tests remain separate and cannot substitute for the internal matrix:

- change V bytes while retaining a valid unchanged row: `_visual_crosscheck_leaf_matches_admission` is false and the normalizer stops before JSON/internal predicates;
- change only the row's V length or SHA without recomputing F: `_fixture_admission_is_valid` is false and the row must never be offered as internal-predicate evidence.

The second case belongs to admission-validator coverage, not the valid-admission internal matrix.

## 7. Non-circular oracle and target-only recovery

The test oracle must be structurally independent:

- `_page_proof_fixture_leaves.py` contains only literal bytes and literal primitive metadata; no `hashlib`, JSON serialization, production import, comprehension-derived expected tuple, or import-time builder.
- `test_page_proof_fixture_admission.py` and `test_page_proof_visual_crosscheck.py` may define test-side `_oracle_pre_visual_binding_sha256`, `_oracle_final_admission_binding_sha256`, and visual decision/inventory/content resealers using only stdlib `hashlib`/`json` and explicit field lists/domain separators.
- Those oracle builders must not call `_fixture_pre_visual_binding_sha256`, `_fixture_admission_binding_sha256`, `_visual_*_sha256`, `_normalize_fixture_visual_crosscheck`, or any production registry/normalizer to generate expected values.
- All three literal baseline P and F values must be compared both to the independent oracle and to production recomputation. A duplicated implementation alone is insufficient; the literal constants are the second anchor.
- Mutation construction computes P once from stable non-target identity/render fields. P must remain unchanged across every visual-only mutation. V and F are each recomputed once in topological order. Any loop, retry, convergence check, interim row, or post-root patch is a test failure.
- Before the negative call, assert the exact row validity and exact leaf-tuple match. Before repair success, repeat them. Repair must restore the target field only; recomputation of downstream hashes is dependency maintenance, not an additional semantic repair.
- For every matrix case, record an explicit predicate vector or equivalent direct assertions showing exactly the intended named predicate false and all applicable non-target predicates true. Do not infer target reachability from exception text or line coverage.

## 8. Containment and unchanged behavior

- Public coverage remains first and code-owned. Because the production topology/admission registries remain incomplete/inactive, derive/review/replay retain their current fail-closed errors and return no wrapper, ledger, plaintext, or proof-like object.
- No new public export, signature, state, or success/reject terminal is introduced.
- Only pure canonical JSON/hash/bytes operations and already present private fixture mechanics are used. No path, filesystem, PDF, external parser/renderer, PIL, browser, network, subprocess, environment, plugin, dynamic import, Stage A construction/replay, source reconstruction, or arbitrary caller PDF bytes become reachable.
- The exact authority type import remains the only Stage A symbol dependency. No new import from projection/replay modules is allowed.
- An AST containment assertion must show that the binding helpers reference only row fields, canonical JSON, SHA-256, and literal schema/domain strings, and that P's dependency set excludes witness/crosscheck/F/output fields.
- A static assertion must show that neither WitnessV2 nor CrossCheckV2 closed roots contain `binding_sha256`/the final F field.
- Existing flow, geometry, component, reviewer, decision, inventory, and content formulas remain unchanged except for their root schema/pre-visual field.
- Packet 4b.7 and final acceptance remain blocked until this remediation receives independent Terra implementation review. Passing tests are not release acceptance.

The bounded future regression command is:

```powershell
& '<confirmed bundled Python path>' -B -m pytest -q -p no:cacheprovider kb_creator/tests/test_page_proof_coverage_guard.py kb_creator/tests/test_page_proof_stage_a_topology_inventory.py kb_creator/tests/test_page_proof_fixture_admission.py kb_creator/tests/test_page_proof_closed_schemas.py kb_creator/tests/test_page_proof_witness_render_components.py kb_creator/tests/test_page_proof_flow_adjacency.py kb_creator/tests/test_page_proof_visual_crosscheck.py
```

The executor must discover/confirm the Python path under the then-current environment; this handoff does not authorize or perform the command.

## 9. Architecture Definition of Done

The remediation candidate is reviewable only when all are true:

1. P and F have the exact formulas and dependency sets in section 2.
2. WitnessV2 and CrossCheckV2 bind P and contain no F.
3. every positive/adversarial/repaired 4b.6 case uses an admission-valid row and exact matching W/render/V bytes;
4. the independent oracle and literal constants agree with production recomputation;
5. all required named predicates are exercised, with target reachability proven directly;
6. the complete target-only recovery matrix passes, including real multi-boundary reorder evidence;
7. prior coverage/admission/schema/mechanics/flow suites pass under the corrected row/root schemas;
8. production registries remain inactive and public behavior remains fail-closed;
9. static containment finds no prohibited dependency or final-binding back-edge;
10. only the allowed files and the executor receipt changed.

## 10. Self-critique

### P0

- **Integrity split risk:** if candidate/review/ledger later bind only P, leaf substitution would no longer be committed by the final admission identity. Mitigation is mandatory: F includes exact W/render/V leaf pairs plus P, and all later artifacts use F. Any F occurrence in WitnessV2/CrossCheckV2 or any later artifact using only P is a P0 rejection.
- **Partial schema migration risk:** updating CrossCheck alone while Witness continues to embed F preserves a second cycle. WitnessV2 and CrossCheckV2 must migrate atomically in this remediation. A partial migration is a P0 rejection.

### P1

- This narrow binding correction changes literals and the private row/root schemas already exercised by 4b.2–4b.5. Their prior implementation reviews do not prove the corrected candidate. The bounded seven-suite regression and a fresh independent 4b.6-r review are required; Packet 4b.7 must not start from the old receipts alone.
- Named predicates add private surface area. They must remain pure, unexported, and called by the normalizer itself; test-only duplicate predicates that production never uses would recreate an evidence gap.
- A three-positive set has only one boundary in its current two-column case. Without a real two-boundary valid case, boundary reorder evidence is vacuous. The fourth private matrix variant is required if the existing flow cannot provide two boundaries.
- The term `pre_visual` could be misread as excluding the render. The exact payload controls: it includes the immutable render leaf pair and excludes witness/crosscheck bytes. Tests and comments must use that exact meaning.

### P2

- V2 fixture literal churn is mechanically noisy. Keep it isolated in the one literal helper and do not regenerate unrelated leaves.
- The independent oracle duplicates small canonical-hash formulas and can drift. Literal P/F constants, explicit field lists, and cross-comparison with production are required to make drift visible.
- Generic public error text remains coarse. This is acceptable only because private named-predicate assertions provide the intended-predicate evidence without changing public errors.

## 11. Required independent Terra remediation review

Terra must review the resulting candidate independently at `high` effort and must not have implemented or materially designed it. This is an implementation-remediation review, not a release review. Acceptance requires:

- reconstructing the P/W/E/V/F dependency graph from actual payload/root keys and confirming no cycle or forbidden back-edge;
- checking both production recomputation functions against the independent oracle and literal constants;
- confirming `_fixture_admission_is_valid(row)` and the exact W/render/V tuple match before every internal adversarial and repair normalizer call;
- confirming each negative fails its named target predicate after all non-target predicates and seals are current;
- confirming repair restores only the semantic target and then passes the same valid-admission checks and baseline normalization;
- confirming real block and boundary cardinality/order coverage, including non-vacuous boundary reorder;
- checking the outer stale-leaf test remains distinct from the internal matrix;
- checking WitnessV2/CrossCheckV2 contain P, never F, while candidate/review projection remains F-bound;
- running only the bounded regression command, recording exact result and candidate hashes, and inspecting containment statically;
- confirming the production registry is still inactive, public coverage/error precedence is unchanged, no terminal was added, and only allowed files plus the receipt changed;
- issuing `accept` only with no open P0 or P1 finding. P2 notes may remain explicit. Test count alone, generic error assertions, or a valid-looking interim row are not acceptance evidence.

## 12. Handoff metadata

- Files checked: the two Terra 4b.6 review receipts; the 4b packetization handoff; `kb_creator/pdf_raw/page_proof.py`; `kb_creator/tests/test_page_proof_visual_crosscheck.py`; `kb_creator/tests/_page_proof_fixture_leaves.py`; canonical NRI goal governance.
- Files changed: this handoff only.
- Verification/evidence: read-only source and contract inspection; no tests, parser, renderer, live artifact, browser, network, output, or Git operation run.
- Blocker resolved by specification: circular full admission/crosscheck binding and invalid final test row.
- Remaining blocker: implementation plus independent Terra remediation acceptance; separate topology-acceptance/production-activation blockers remain unchanged.
- Next action: orchestrator may assign one bounded executor using section 3, then request the section 11 Terra review. Do not start Packet 4b.7 before acceptance.
- Timestamp: `2026-08-11T13:51:33.7332501+03:00`.
- Token use: `unavailable` at handoff authoring time.

This architecture receipt is immutable, does not transfer orchestration ownership, does not approve implementation or release, and does not authorize production activation.

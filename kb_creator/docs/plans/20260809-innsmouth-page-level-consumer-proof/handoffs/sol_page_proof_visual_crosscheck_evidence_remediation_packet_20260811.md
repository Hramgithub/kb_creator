# Sol architecture receipt — Packet 4b.6-r remaining P1 evidence remediation

## Receipt and scope decision

- Goal id: `20260809-innsmouth-page-level-consumer-proof`.
- Step id: `4b.6-r-evidence-architecture`.
- Role: Sol architecture/root-cause/remediation specification; requested effort `high`.
- Actual model/effort: `platform-unverified`.
- Orchestrator policy owner: `gpt-5.5` at `medium` (`platform-unverified`).
- Assignment state: `platform-unverified`.
- Scoped override: user-authorized Sol specification and this immutable handoff only. No code, tests, canonical plan, context, project status, contracts, output, Git, live/PDF/source/EN/RU/Keeper/HTML, parser, renderer, browser, network, release, or Packet 4b.7 work.
- Result: **an evidence-only remediation is specified for P1.1, P1.2, P1.3, and P1.5.** The current production P/W/E/V/F graph is not reopened. The executor is not authorized to change production code or architecture.

This receipt narrows and completes only the open evidence requirements left by `terra_page_proof_visual_crosscheck_binding_remediation_rereview_20260811.md`. All accepted requirements of `sol_page_proof_visual_crosscheck_binding_remediation_spec_20260811.md` remain in force. This is neither implementation acceptance nor release acceptance, and orchestration ownership does not transfer.

## 1. Baseline assumptions and invariants

The remediation may proceed only while all of these assumptions remain true in the candidate inspected by the executor:

1. `kb_creator/pdf_raw/page_proof.py` is byte-for-byte the reviewed baseline with SHA-256 `A6E5E647A6B973772D6690775EC78F30FBDA909CBB19F95D6A88A4BA9702870B`.
2. Production P is based only on fixture, Stage-A authority, topology inventory, render identity, and the two V2 schema names. Production F includes P plus exact W/render/V leaf metadata and excludes F and expected-output hashes.
3. WitnessV2 and CrossCheckV2 contain `pre_visual_binding_sha256` and do not contain final `binding_sha256`.
4. Production topology/admission registries remain inactive; public derive/review/replay remain coverage-first and fail closed without returning a wrapper, ledger, plaintext, proof-like object, or new terminal.
5. The public exports, signatures, errors, flow formulas, component formulas, geometry formulas, reviewer contract, decision seals, inventory seal, and content seal do not change.

If any assumption is false, the executor must stop and return a blocker. It must not repair production, alter architecture, or widen this packet.

## 2. P1.1 exact reusable pre-normalizer assertion contract

### 2.1 Required test helper signature

Replace the incomplete `_assert_reaches_internal_visual_predicate` with one reusable helper having this exact semantic signature in `test_page_proof_visual_crosscheck.py`:

```python
def _assert_pre_normalizer_contract(
    *,
    row: page_proof._FixtureAdmission,
    witness_raw: bytes,
    render_png_raw: bytes,
    crosscheck_raw: bytes,
    mechanics: dict[str, object],
    flow: dict[str, object],
    expected_predicates: dict[str, bool],
) -> None:
```

The helper must not normalize V or construct expected values. It consumes the exact row/W/render/V/mechanics/flow that the immediately following normalizer call will consume. It must assert all of the following before that call:

- `row.pre_visual_binding_sha256` equals the independent test-side P oracle;
- `row.binding_sha256` equals the independent test-side F oracle;
- `_fixture_pre_visual_binding_is_valid(row)` is true;
- `_fixture_admission_is_valid(row)` is true;
- `_fixture_admission_row_matches_derive_leaves(row, witness_raw, render_png_raw, crosscheck_raw)` is true;
- `_visual_crosscheck_leaf_matches_admission(crosscheck_raw, row)` is true;
- W and render metadata in the row equal the exact supplied W/render length and SHA pairs, not merely V metadata;
- the parsed V root is canonical, has the exact closed CrossCheckV2 root key set, and has the exact schema literal;
- the actual full named predicate vector below has exactly the same keys and values as `expected_predicates`.

`expected_predicates` must be a full literal mapping at each call site. A target name, an omitted-key default, exception text, line coverage, or a helper that assumes all unmentioned predicates true is insufficient.

### 2.2 Full predicate-vector key set

The exact vector key set is:

```text
fixture_pre_visual_binding_is_valid
fixture_admission_is_valid
fixture_admission_row_matches_derive_leaves
visual_crosscheck_leaf_matches_admission
visual_crosscheck_root_binding_matches
visual_crosscheck_root_context_matches
visual_crosscheck_reviewer_matches_contract
visual_crosscheck_cardinality_matches
visual_crosscheck_block_region_matches
visual_crosscheck_block_transcription_matches
visual_crosscheck_block_decision_matches
visual_crosscheck_boundary_region_matches
visual_crosscheck_boundary_decision_matches
visual_crosscheck_inventory_matches
visual_crosscheck_content_seal_matches
```

The first four keys call the named production predicates directly. The eleven visual keys call the named production predicates directly on the parsed root and the supplied mechanics/flow. The block and boundary entries are `all(...)` over every supplied row that has an aligned expected counterpart. Extra rows are intentionally excluded from those two aggregates and are detected by cardinality; missing rows leave only the present aligned prefix applicable. Inventory is evaluated against the decision-digest tuples in the supplied V rows. The helper must not call `_normalize_fixture_visual_crosscheck` to infer any vector value.

The helper must also assert that every block/boundary row and every mechanics/flow object needed by an applicable predicate has the expected private type/shape before calling that predicate. A predicate exception is not a boolean vector result and fails the test.

### 2.3 Required call discipline and truth rule

The helper is mandatory immediately before every positive, internal-negative, and repaired `_normalize_fixture_visual_crosscheck` call in this file. The exact row/W/render/V objects passed to the helper must be passed to the normalizer; no reseal, rebind, replacement, or mutation may occur between them.

- Positive baseline: all fifteen vector values are `True`.
- Internal negative: the first four admission/leaf values are always `True`; exactly the named target predicate in sections 3 and 4 is `False`; every other vector value is `True`.
- Repaired case: all fifteen values are `True`, normalization succeeds, and canonical JSON of the normalized result equals the literal baseline normalized result byte-for-byte.

The two outer-envelope tests remain separate and must not call this helper as internal evidence:

- changed V with the unchanged valid row proves only `visual_crosscheck_leaf_matches_admission=False`;
- changed row V metadata without recomputing F proves only `fixture_admission_is_valid=False`.

## 3. P1.2 literal fourth valid-admission case

### 3.1 Literal-only leaves

Add a private test-only two-boundary variant. It is not a production registry row and must not be appended to any production or expected primitive registry.

`_page_proof_fixture_leaves.py` may add only these new fourth-case data families, each as a direct literal assignment:

```text
INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1       canonical bytes literal
TWO_BOUNDARY_V1_LENGTHS                            direct 4-int tuple for fixture/W/render/V
TWO_BOUNDARY_V1_SHA256                             direct 4-string tuple for fixture/W/render/V
TWO_BOUNDARY_PRE_VISUAL_BINDING_SHA256              direct 64-hex string
TWO_BOUNDARY_FINAL_BINDING_SHA256                  direct 64-hex string
TWO_BOUNDARY_EXPECTED_CONTENT_SHA256               direct 64-hex string
TWO_BOUNDARY_EXPECTED_PRE_VISUAL_CORE_SHA256       direct 64-hex string
```

The fourth case reuses the exact literal two-column fixture id, WitnessV2 bytes, and render PNG bytes, so its first three length/SHA pairs and P equal the two-column literals. The fourth V bytes, V length/SHA, F, root content SHA, and pre-visual-core SHA are separately pasted literals. The `_FixtureAdmission` row in the visual test must be an explicit constructor with every field stated; it must not be created with `dataclasses.replace` from the canonical two-column row.

For every new fourth-case assignment, the right-hand AST may contain only constants and tuple/list literals, plus Python's implicit concatenation of adjacent bytes literals. It may not contain a name reference, call, attribute, subscript, comprehension, arithmetic expression, import-time hash/JSON operation, production import, or builder. Existing literal helper rules remain: no `hashlib`, JSON serialization, production normalizer, filesystem read, or generated expected tuple.

An AST assertion in the visual test must enforce the direct-literal rule for all seven new names. Values may be computed once in an uncommitted shell calculation using the independent stdlib oracle, but only the final primitive literals may enter the helper.

### 3.2 Exact two-boundary flow and V baseline

In `test_page_proof_visual_crosscheck.py`, add a function that returns a fresh syntactically literal flow-input dictionary. It must not read `_case_rows()`, a normalized flow, or another mutable object, and it must not use `copy`, `deepcopy`, a comprehension, or a production flow helper to construct expected input.

The literal flow is the two-column identity with:

```text
b0.fragment_ids = ["f0", "f1"]
b1.fragment_ids = ["f2"]
included_block_ids = ["b0", "b1"]
excluded_block_ids = []
adjacency_rows[0] = f0 -> f1, within_block, b0 -> b0
adjacency_rows[1] = f1 -> f2, cross_column, b0 -> b1
```

Every other block field is stated literally and equals the accepted two-column mechanics identity. There must be exactly two adjacency rows in that order.

The literal CrossCheckV2 baseline must contain the two accepted two-column block rows and exactly these boundary rows in this order:

```text
0: f0 -> f1, within_block, b0 -> b0, columns 1 -> 1,
   boundary_bbox_px [0, 0, 1, 3], decision confirm,
   reason matches_expected_boundary, literal decision SHA
1: f1 -> f2, cross_column, b0 -> b1, columns 1 -> 0,
   boundary_bbox_px [0, 0, 4, 3], decision confirm,
   reason matches_expected_boundary, literal decision SHA
```

Its decision inventory contains both literal boundary decision SHAs in the same order, boundary count `2`, the two existing block decision SHAs in order, block count `2`, and a literal inventory SHA. The root contains the unchanged literal two-column P/topology/reviewer values, the literal fourth-case pre-visual core, and a literal content SHA. The V must be canonical JSON bytes. The test must prove the literal V metadata, P, and F against both independent test-side oracles and production recomputation before treating it as a positive case.

The positive fourth case must call mechanics on the exact reused W/render bytes, call flow normalization only on the fresh literal flow input, assert the resulting pre-visual core equals the literal expected core, call the full pre-normalizer helper with all fifteen values true, normalize the literal V, and assert exact literal block ids/transcriptions plus the two ordered boundary triples.

### 3.3 Missing, duplicate, reorder, and target-only recovery

Each structural case starts by parsing a fresh copy from the literal fourth V bytes. Parsing the literal bytes is the only permitted way to obtain a mutable crosscheck tree. `copy` and `deepcopy` must be removed from this test file.

For each mutation, reseal only the dependency closure with the independent stdlib test helpers: changed boundary list -> ordered boundary digest list/count/inventory SHA -> root content SHA -> V length/SHA -> F exactly once. P, W, render, mechanics, flow, block rows, reviewer fields, topology digest, and pre-visual core remain unchanged.

Required constructions are:

| case | target-only mutation | negative vector | target-only repair |
|---|---|---|---|
| missing | remove boundary row index 1 | only `visual_crosscheck_cardinality_matches=False` | insert the exact literal row 1 back at index 1 |
| duplicate | append one additional literal copy of boundary row 1 after the complete two-row baseline | only `visual_crosscheck_cardinality_matches=False` | remove only the appended final row |
| reorder | replace `[row0, row1]` with `[row1, row0]` | only `visual_crosscheck_boundary_region_matches=False` | swap those same two rows back |

The missing and duplicate layouts preserve a canonical aligned prefix so all applicable boundary-region and boundary-decision predicates remain true. The reorder retains cardinality, valid per-row decisions, a current inventory, current root content, current V leaf metadata, and current F; only alignment with the ordered adjacency universe is false.

Repair must start from the mutated tree or mutated raw bytes, perform only the repair operation shown above, and reseal its dependency closure. Calling the separately retained baseline as the repair, discarding the mutation and reparsing the baseline as the repaired object, or replacing the whole boundary list from baseline is not evidence. Before each negative and repaired normalizer call, the full pre-normalizer helper is required. Every repaired normalized result must equal the positive fourth baseline in canonical bytes.

## 4. P1.3 exact target and vector matrix

### 4.1 Exhaustive root and reviewer targets

The following cases are all mandatory and independent. Mutation helpers reseal root content, V metadata, and F unless the row says otherwise. In every row, the named false predicate is the only false vector value; repair restores only the named semantic field and then yields an all-true vector.

| target | exact mutation | only false predicate | repair |
|---|---|---|---|
| root P | CrossCheckV2 `pre_visual_binding_sha256` to another valid 64-hex value; row P unchanged | `visual_crosscheck_root_binding_matches` | restore literal root P |
| root topology | root `required_topology_inventory_content_sha256` to another valid 64-hex value; row unchanged | `visual_crosscheck_root_context_matches` | restore literal topology digest |
| root pre-visual core | root `pre_visual_evidence_core_sha256` to another valid 64-hex value; flow unchanged | `visual_crosscheck_root_context_matches` | restore literal flow core |
| reviewer identity | `reviewer_identity=""` | `visual_crosscheck_reviewer_matches_contract` | restore literal non-empty identity |
| reviewer scope | `reviewer_scope` to a non-contract non-empty string | `visual_crosscheck_reviewer_matches_contract` | restore `page_block_and_boundary` |
| reviewer independence | `reviewer_independence` to a non-contract non-empty string | `visual_crosscheck_reviewer_matches_contract` | restore `independent` |
| root content seal | replace only `content_sha256` with another valid 64-hex value and do not recompute it; then update only V metadata/F | `visual_crosscheck_content_seal_matches` | restore/recompute only the content seal, then V metadata/F |

### 4.2 Exhaustive boundary targets

Use the literal fourth case for all structure/order targets and for ordinary boundary replay/decision targets unless a one-boundary case is explicitly sufficient. Every listed mutation is mandatory:

```text
structure: missing final row; appended duplicate final row; two-row reorder;
           aggregate-like substitute represented by two valid-shape repeated
           aggregate rows at unchanged cardinality
region:    source_fragment_id; target_fragment_id; boundary_kind;
           source_block_id; target_block_id; source_column_index;
           target_column_index; boundary_bbox_px
decision:  decision != confirm; wrong decision_reason; stale/wrong decision_sha256
```

The aggregate-like substitute must keep two rows so cardinality remains true. Each substitute row has the exact closed boundary schema and current decision digest; inventory/content/V/F are current. It attempts to summarize `f0 -> f2` instead of replaying the two literal adjacencies. Therefore only `visual_crosscheck_boundary_region_matches` is false.

For every region mutation, recompute that row's decision SHA and all downstream seals so only `visual_crosscheck_boundary_region_matches` is false. For non-confirm and wrong-reason mutations, recompute the decision SHA and downstream seals; the exact value/reason check keeps only `visual_crosscheck_boundary_decision_matches` false. For stale/wrong decision SHA, preserve the deliberately wrong row SHA, construct the inventory from that supplied wrong SHA, and reseal root/V/F; only `visual_crosscheck_boundary_decision_matches` is false.

All three structural repairs and every ordinary boundary repair follow section 3.3: restore only the mutated field/list operation, reseal dependencies, prove an all-true vector, normalize, and compare canonical normalized bytes with the literal baseline.

### 4.3 Existing block, transcription, decision, inventory, and outer targets

Existing required targets are not removed. Migrate every current case to the full helper and target-only repair discipline:

- block structure: missing final row and appended duplicate final row -> cardinality false only; reorder at unchanged cardinality -> block region false only;
- block region: id, ordinal, disposition, reason, column, bbox, pixel count, component evidence -> block region false only;
- transcription: empty decoded bytes, changed bytes with old hash, wrong hash -> transcription false only;
- block decision: non-confirm, wrong reason, stale/wrong decision SHA -> block decision false only;
- inventory: block digest list/order, boundary digest list/order, either count, stale/wrong inventory SHA -> inventory false only;
- content seal and the two outer-envelope cases remain as specified above.

For a stale decision or stale inventory target, downstream seals are computed from the deliberately supplied stale value; no second semantic mismatch is permitted. A mask case changes only `component_evidence_sha256`; W/render/mechanics remain fixed.

## 5. P1.5 AST containment contract for P/F

Replace the partial AST test with a durable source-derived graph assertion. It parses `inspect.getsource(page_proof)` and inspects these six functions:

```text
_fixture_pre_visual_binding_payload
_fixture_pre_visual_binding_sha256
_fixture_pre_visual_binding_is_valid
_fixture_admission_payload
_fixture_admission_binding_sha256
_fixture_admission_is_valid
```

### 5.1 Exact binding-helper call graph

After filtering calls to the six named binding helpers, the direct edge set must be exactly:

```text
_fixture_pre_visual_binding_payload -> {}
_fixture_pre_visual_binding_sha256 -> {_fixture_pre_visual_binding_payload}
_fixture_pre_visual_binding_is_valid -> {_fixture_pre_visual_binding_sha256}
_fixture_admission_payload -> {_fixture_pre_visual_binding_payload}
_fixture_admission_binding_sha256 -> {_fixture_admission_payload}
_fixture_admission_is_valid -> {
    _fixture_pre_visual_binding_is_valid,
    _fixture_admission_binding_sha256,
}
```

The hash functions must additionally have exact primitive call dependencies:

```text
_fixture_pre_visual_binding_sha256:
    {_sha256, _canonical_json, _fixture_pre_visual_binding_payload}
_fixture_admission_binding_sha256:
    {_sha256, _canonical_json, _fixture_admission_payload}
```

No binding helper may call a normalizer, registry, visual decision/inventory/content helper, filesystem/path/environment function, reflection helper (`getattr`, `vars`, `__dict__`, `dataclasses.asdict`), or dynamic import.

### 5.2 Exact module-private name dependencies

Collect `ast.Name` ids beginning with `_` in each function. The permitted sets are exact, not supersets:

```text
_fixture_pre_visual_binding_payload:
    {_WITNESS_SCHEMA, _VISUAL_CROSSCHECK_SCHEMA}
_fixture_pre_visual_binding_sha256:
    {_sha256, _canonical_json, _fixture_pre_visual_binding_payload}
_fixture_pre_visual_binding_is_valid:
    {_FixtureAdmission, _HEX, _fixture_pre_visual_binding_sha256}
_fixture_admission_payload:
    {_fixture_pre_visual_binding_payload}
_fixture_admission_binding_sha256:
    {_sha256, _canonical_json, _fixture_admission_payload}
_fixture_admission_is_valid:
    {_FixtureAdmission, _HEX, _sha256,
     _fixture_pre_visual_binding_is_valid,
     _fixture_admission_binding_sha256}
```

This check is source containment, not proof from runtime values. An unexpected private name fails even when tests otherwise pass.

### 5.3 Exact field dependency sets

Collect `row.<attribute>` references and compute transitive payload dependencies through the call graph.

P's exact field set is:

```text
fixture_id
fixture_id_byte_length
fixture_id_sha256
stage_a_fixture_id
stage_a_authority_content_sha256
required_topology_inventory_content_sha256
render_png_byte_length
render_png_sha256
```

P also depends on the exact runtime constants:

```text
_WITNESS_SCHEMA == "kb_creator.pdf_raw.PageProofWitnessV2"
_VISUAL_CROSSCHECK_SCHEMA == "kb_creator.pdf_raw.IndependentPageVisualCrossCheckV2"
```

F's exact transitive field set is P's eight fields plus:

```text
pre_visual_binding_sha256
witness_byte_length
witness_sha256
independent_visual_crosscheck_byte_length
independent_visual_crosscheck_sha256
```

The P payload key set must equal those eight field names plus `witness_schema` and `visual_crosscheck_schema`. The F payload must equal the P payload plus exactly the five additional fields above. P must exclude W, V, F, candidate, review, and expected-output fields. F must exclude `binding_sha256`, `expected_candidate_sha256`, and `expected_reviewed_ledger_sha256`.

The AST test must assert the exact bytes domains in their respective functions:

```text
b"page-proof.fixture-pre-visual-binding.v1\0"
b"page-proof.fixture-admission.v2\0"
```

It must reject loops, comprehensions, `**` dictionary expansion, whole-row serialization, attribute enumeration, and dynamic field lookup in the two payload/hash functions. Finally, runtime static assertions must retain:

```text
"binding_sha256" not in _WITNESS_ROOT_KEYS
"binding_sha256" not in _VISUAL_CROSSCHECK_ROOT_KEYS
"pre_visual_binding_sha256" in both V2 root key sets
```

## 6. Exact executor write scope and verification

The bounded executor may modify only:

1. `kb_creator/tests/_page_proof_fixture_leaves.py` — new direct fourth-case literals only;
2. `kb_creator/tests/test_page_proof_visual_crosscheck.py` — full pre-normalizer vector helper, fourth literal flow/case, target-only mutation/repair evidence, exhaustive targets, and AST containment;
3. `kb_creator/docs/plans/20260809-innsmouth-page-level-consumer-proof/handoffs/executor_page_proof_visual_crosscheck_evidence_remediation_20260811.md` — one new immutable executor receipt.

No production file, other test, canonical plan/context/status/release file, contract/spec, manifest, configuration, source, output, or existing handoff may change. No Git operation is authorized. If either test file cannot close the packet without another path or a production change, stop and report a blocker.

The executor must confirm the Python command in the then-current environment and run exactly the bounded regression:

```powershell
& '<confirmed bundled Python path>' -B -m pytest -q -p no:cacheprovider kb_creator/tests/test_page_proof_coverage_guard.py kb_creator/tests/test_page_proof_stage_a_topology_inventory.py kb_creator/tests/test_page_proof_fixture_admission.py kb_creator/tests/test_page_proof_closed_schemas.py kb_creator/tests/test_page_proof_witness_render_components.py kb_creator/tests/test_page_proof_flow_adjacency.py kb_creator/tests/test_page_proof_visual_crosscheck.py
```

The executor receipt must record exact changed paths, before/after SHA-256 for both changed test files, interpreter/version, exact command/result, literal fourth-case identifiers and hashes, matrix case count, confirmation that `page_proof.py` still has the baseline SHA above, blockers, next action, elapsed time, token use, timestamp, policy owner, assignment state, and scoped override.

## 7. Exact independent Terra reviewer checklist

The next reviewer is an independent Terra implementation critic at `high`; it must not have implemented or materially designed this remediation. It is not a release review. The reviewer must complete every item:

1. Read governance, the assigned plan/context, the original Sol binding specification, the rejecting Terra re-review, this receipt, and the executor receipt.
2. Confirm `page_proof.py` remains at SHA-256 `A6E5E647A6B973772D6690775EC78F30FBDA909CBB19F95D6A88A4BA9702870B`; any production delta is an automatic reject/blocker for this packet.
3. Confirm only the two authorized test files and the executor receipt changed within the packet evidence supplied by the orchestrator; do not treat this as a whole-worktree Git audit.
4. Inspect the new fourth constants and AST assertion: every new leaf/metadata value is direct literal-only; no import-time builder/hash/JSON/production call exists.
5. Confirm the fourth row is an explicit constructor, W/render are the exact two-column literal leaves, V is a distinct canonical literal, P is unchanged, V/F are independently anchored literals, and the fourth case is absent from production registries.
6. Confirm the fourth flow is syntactically literal and independent of `_case_rows()`/normalized flow; confirm the literal V has exactly two ordered boundary rows matching the two adjacency rows.
7. Confirm no `copy`/`deepcopy` remains and missing/duplicate/reorder each start from literal V, produce an admission-valid exact W/render/V tuple, have the specified single-false vector, fail the normalizer, repair the mutated object by only the specified inverse operation, return to an all-true vector, and normalize byte-for-byte to baseline.
8. Confirm `_assert_pre_normalizer_contract` receives exact row/W/render/V/mechanics/flow and a full fifteen-key literal vector before every positive, internal-negative, and repaired normalizer call. Sample every test family and mechanically search for any unguarded call.
9. Confirm all root targets (P, topology, pre-visual core, content seal), all reviewer targets (empty identity, wrong scope, non-independent), and every boundary structure/region/decision target in section 4 are present with exactly the specified false predicate and all other vector values true.
10. Confirm all earlier block/transcription/decision/inventory/mask targets remain and now include target-only repair evidence; outer stale-leaf and invalid-F tests remain separate from the internal matrix.
11. Reconstruct the P/F graph from the AST assertions. Confirm exact helper call edges, exact private-name sets, exact P/F transitive field sets, exact domains, no reflective/dynamic/whole-row dependency, and no F back-edge into WitnessV2/CrossCheckV2.
12. Confirm production registries remain inactive, `__all__` and public signatures/errors are unchanged, public coverage remains first, and no output/proof terminal or Packet 4b.7 path was introduced.
13. Run the exact seven-suite command and record interpreter/version, exact pass/fail count/time, and post-review SHA-256 values for the production file and two changed tests.
14. Issue `accept` only with no open P0 or P1. Any omitted vector key, unguarded normalizer call, baseline-as-repair shortcut, nonliteral fourth leaf/flow, missing target, weak AST subset check, production delta, or scope expansion is a P1 reject. P2 observations may remain explicit.

Passing tests alone are insufficient. Packet 4b.7 and production activation remain blocked until the orchestrator receives and integrates a fresh independent Terra implementation acceptance. Final release acceptance still requires the separate governance release gate.

## 8. Acceptance criteria

The executor candidate is reviewable only when all are true:

1. No production or architecture file changed; `page_proof.py` retains the stated SHA-256.
2. Every internal positive, negative, and repaired V call has the exact row/W/render/V pre-normalizer assertion and full fifteen-key vector.
3. Each negative has exactly its specified false predicate; each repair has an all-true vector and byte-identical normalized baseline.
4. The fourth private admission is literal, valid, non-registered, independently anchored, and contains two real ordered boundaries.
5. Missing, appended duplicate, and reorder each prove target-only mutation and inverse repair without baseline replacement or deep copy.
6. Root, reviewer, and boundary target lists are exhaustive as specified; all prior matrix targets remain covered.
7. AST assertions pin exact P/F call, private-name, domain, and field-dependency graphs and closed-root non-edges.
8. Public no-live/no-output/fail-close containment is unchanged.
9. The exact seven-suite regression passes.
10. Only the two authorized test files and new executor receipt are in the implementation packet.
11. Fresh independent Terra implementation review accepts with no P0/P1.

## 9. Handoff metadata

- Files checked: canonical `docs/governance/nri_goal_governance.md`; assigned goal `plan.md` and `context.md`; the original Sol binding-remediation specification; the Terra implementation re-review; `kb_creator/pdf_raw/page_proof.py`; `kb_creator/tests/_page_proof_fixture_leaves.py`; `kb_creator/tests/test_page_proof_visual_crosscheck.py`.
- Files changed: this immutable handoff only.
- Verification/evidence: read-only contract/source/test inspection and SHA-256 capture. No code/test execution, live artifact, parser, renderer, browser, network, output, or Git operation was performed.
- Resolved by specification: exact closure contract for P1.1, P1.2, P1.3, and P1.5.
- Blockers: bounded implementation and fresh independent Terra implementation acceptance remain required; production topology/admission activation and all Packet 4b.7/release gates remain unchanged.
- Next action: orchestrator may assign one bounded executor under section 6, then request the independent checklist in section 7. Do not start Packet 4b.7 before acceptance.
- Elapsed time: approximately 16 minutes active architecture inspection/specification.
- Token use: `unavailable` at handoff authoring time.
- Timestamp: `2026-08-11T14:43:04.4615064+03:00`.
- Orchestrator policy owner: `gpt-5.5` at `medium` (`platform-unverified`).
- Assignment state: `platform-unverified`.
- Scoped override: architecture specification and this receipt only; no orchestration transfer and no implementation/review/release authority.

This receipt is immutable. A correction must use a new handoff path and supersede this receipt explicitly; it must not rewrite this file.

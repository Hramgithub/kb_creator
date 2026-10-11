# Sol Architecture Specification — Packet 4b.7 Witness-Bound Composition

## Immutable receipt

- Goal id: `20260809-innsmouth-page-level-consumer-proof`.
- Step id: `4b.7-specification`.
- Role/effort: Sol architect / requested `high`; actual platform model and
  effort are `platform-unverified`.
- Orchestrator policy owner: `gpt-5.5` at `medium`
  (`platform-unverified`). Orchestration ownership remains in the main chat.
- Assignment state: `platform-unverified`.
- Scoped override: the user-authorized Packet `4b.7` architecture handoff and
  this path only. It authorizes no implementation, review, registry activation,
  live input, output, build, Git, release, or orchestration transfer.
- Result: **one bounded next packet is specified.** This is not implementation,
  implementation acceptance, registry activation, or release review.

## 1. Purpose and critical-path finding

Packet `4b.7` must add exactly one missing P0/P1 proof capability:

> deterministically compose the admitted fixture witness/render leaves into
> mechanics `M`, the accepted flow/adjacency normalization `E`, and the accepted
> independent visual cross-check `V`, using only the four existing public derive
> inputs and no hidden fixture authority.

Packets `4b.1`–`4b.6` separately prove admission, schemas, render mechanics,
flow, and visual checks. They do **not** yet prove their public composition.
The current public derive signature receives only
`(RawAtomProvenanceAuthorityV1, witness_raw, render_png_raw,
independent_visual_crosscheck_raw)`, while the accepted literal WitnessV2 root
contains geometry/render/component facts but no `flow_input`. Current `E` is
constructed only by test-side flow builders. It cannot be reproduced from the
admitted public leaves without inventing block membership, component ownership,
fragment ids, columns, exclusions, or adjacency from geometry or from `V`.

That is the smallest missing P1 on the critical path. Candidate-ledger
construction, aggregate review, exact replay, terminal states, expected-output
sealing, production topology/admission activation, and a full adversarial or
containment closure are outside this packet. The three public functions must
still return no proof-like object.

## 2. Frozen inputs and assumptions

Implementation may start only if these exact accepted baseline identities still
match before any edit:

| Path | Required SHA-256 |
| --- | --- |
| `kb_creator/pdf_raw/page_proof.py` | `A6E5E647A6B973772D6690775EC78F30FBDA909CBB19F95D6A88A4BA9702870B` |
| `kb_creator/tests/_page_proof_fixture_leaves.py` | `EC6E5FBC5252F4BD094A6ED263668D002C413364057D360819217D530296B3AA` |
| `kb_creator/tests/test_page_proof_visual_crosscheck.py` | `EE4C1B5B4E43E44F77ACD8A22715F4418A64CBB2CA94939CFD56A7C227899FBC` |
| final 4b.6 acceptance receipt | `6812DDE8F60F277CB2FE402904F28DCC39402384A2DF52D7869A7B662F04CA50` |

The unchanged regression baselines are:

```text
test_page_proof_coverage_guard.py                 0065DB7A34C45DC4FBD17719825C3AA1566A9CCC7B484BB7A0AC30041D9D964A
test_page_proof_stage_a_topology_inventory.py     E9752542CA1574437AA24B8097CA5D30A4A7A7B434ED0146D72C66EF83165203
test_page_proof_fixture_admission.py              276D2D4D89B283B601E58BE443808D8793518A159602C1FA4BD9976B8F9E441A
test_page_proof_closed_schemas.py                 F4F33B0505275D436EFD16A622EECEF943F5C8CFB40BA3BE55148677F31DBA2C
test_page_proof_witness_render_components.py      8FD9D8E4AD034A667F793F0F6005C84787E9F478FFFC3ECD658EB813BE66BEA1
test_page_proof_flow_adjacency.py                  1CDEFD250A271D59DF4C1AFE1283E573076E4066779DAC0FEB7B2FAE81A623E4
```

Normative contract inputs remain the original Sol specification, its accepted
P1 correction, the accepted packetization through `4b.6`, all immutable
`4b.1`–`4b.6` implementation/remediation/review receipts, the final
`terra_page_proof_visual_crosscheck_canonical_layout_p1_repair_review_20260811.md`,
and `page_level_consumer_proof_contract_status.md` as read on 2026-08-11.

Assumptions:

1. `d0891ce46fc9cb3aeee366cf78610996b3e2a34e94d85c47e9d212599a438ac6`
   remains a **private test-surrogate topology content digest**, not production
   acceptance evidence. Its test rows use non-authoritative review hashes and
   must never be copied into production roots.
2. Exact production `fixture_topology_acceptance` review-content hashes remain
   absent. This blocks production activation but does not block fixture-only
   composition evidence.
3. The accepted P/W/E/V/F architecture remains normative. Version migration is
   required because adding a closed root field without changing the witness
   schema id would be a schema-version violation.
4. P2/P3 observations, including `KB-DEBT-20260811-001`, remain debt-only. They
   neither expand this packet nor block P0/P1 acceptance.

If any frozen identity differs, the executor must stop and write a blocker
receipt; it must not regenerate literals from an unaccepted candidate.

## 3. Allowed and disallowed file scope

### Allowed implementation writes

1. `kb_creator/pdf_raw/page_proof.py`.
2. `kb_creator/tests/_page_proof_fixture_leaves.py`.
3. `kb_creator/tests/test_page_proof_fixture_admission.py`.
4. `kb_creator/tests/test_page_proof_closed_schemas.py`.
5. `kb_creator/tests/test_page_proof_witness_render_components.py`.
6. `kb_creator/tests/test_page_proof_flow_adjacency.py`.
7. `kb_creator/tests/test_page_proof_visual_crosscheck.py`.
8. New `kb_creator/tests/test_page_proof_composition.py`.
9. One new immutable executor receipt under this goal's `handoffs/` directory.

An allowed file may change only for the V3 witness migration, dependent P/F
literal resealing, composition evidence, or assertions needed to preserve the
accepted `4b.1`–`4b.6` invariants. No unrelated cleanup or refactor is allowed.

### Disallowed writes and actions

- `_PRODUCTION_REQUIRED_STAGE_A_TOPOLOGY_INVENTORY`,
  `_PRODUCTION_EXPECTED_TOPOLOGY_PRIMITIVES`,
  `_PRODUCTION_FIXTURE_ADMISSION`, and
  `_PRODUCTION_EXPECTED_FIXTURE_ADMISSION_PRIMITIVES` must remain at their
  currently inactive empty production state.
- No new public API, public argument, public export, candidate/review wrapper,
  ledger schema, terminal state, review attestation, replay success, expected
  candidate/reviewed seal, or source-use language.
- No plan, context, project status, contract status, debt, release, prior
  receipt, configuration, Stage A authority module, parser, source
  reconstruction, EN/RU/Keeper/HTML/PDF/output, or generated artifact change.
- No live PDF read, source reconstruction, renderer/parser/PIL invocation,
  filesystem leaf loading, browser, network, subprocess, environment/config
  selector, plugin/dynamic import, build, Git, registry activation, Packet
  `4b.8`, Step `5`, or release work.

## 4. Exact data and contract changes

### 4.1 Versioned witness migration

Change the witness schema literal from
`kb_creator.pdf_raw.PageProofWitnessV2` to
`kb_creator.pdf_raw.PageProofWitnessV3`.

WitnessV3 has exactly the WitnessV2 closed root keys plus one required root key
named `flow_input`, before `content_sha256`. `flow_input` is canonical JSON and
has exactly:

```text
blocks
included_block_ids
excluded_block_ids
adjacency_rows
```

Each `blocks[]` row has exactly the already accepted 4b.5 fields:

```text
block_id
block_ordinal
atom_row_ids
component_ids
fragment_ids
column_index
flow_flags
```

`flow_flags` has exactly `running_marginal`, `occluded`,
`text_layer_disagreement`, and `visual_only`, all exact booleans.
`included_block_ids`, `excluded_block_ids`, and `adjacency_rows` are witness
claims only. Production must pass the complete object through the existing
`_normalize_fixture_block_flow_adjacency`; that normalizer independently derives
disposition/reason and requires the exact partition, fragment universe, and
adjacency sequence. No x/y sort or V-derived reconstruction is permitted.

Each `adjacency_rows[]` row retains exactly:

```text
source_fragment_id
target_fragment_id
boundary_kind
source_block_id
target_block_id
```

No alias, optional field, implicit default, code-owned flow table, or test-only
builder may supply a missing `flow_input` at runtime.

### 4.2 Seal migration

The existing pre-visual formula and domain remain unchanged except that their
literal `witness_schema` payload value becomes WitnessV3. Therefore:

```text
identity + Stage-A/topology + render + WitnessV3/CrossCheckV2 schema ids -> P'
P' + WitnessV3 -> M/E
P' + E -> V'
P' + exact W'/render/V' leaf pairs -> F'
```

`IndependentPageVisualCrossCheckV2` stays V2; its semantics and closed keys do
not change, but every literal V leaf is resealed with `P'` and the unchanged
accepted `pre_visual_evidence_core_sha256`. Final admission V2 stays V2 and is
resealed once with the exact W'/render/V' pairs. Expected candidate and reviewed
hash fields remain outside P' and F' and gain no authority in this packet.

All three canonical fixture families and the private two-boundary visual case
must receive new literal W'/V'/P'/F' anchors. Render bytes, Stage A authority
bytes/identities, normalized mechanics, normalized flow, block/boundary
decisions, and semantic expected results must remain byte-for-byte or
value-for-value unchanged. Any semantic drift is P1 and must stop the packet.

The literal helper remains import-free and builder-free. It may contain only
direct literal bytes and direct primitive metadata. Test-side stdlib-only
oracles must independently recompute P', witness content, V content, and F';
production helpers may be compared against those values but must not generate
the expected literals at import time.

### 4.3 Single composition function

Add one private composition function with this conceptual contract (repository
typing style may adjust the private name only):

```text
_normalize_fixture_page_proof_composition(
    validated_stage_a_authority: RawAtomProvenanceAuthorityV1,
    witness_raw: bytes,
    render_png_raw: bytes,
    independent_visual_crosscheck_raw: bytes,
    admission_row: _FixtureAdmission,
) -> closed private composition value
```

Its order is mandatory:

1. exact authority and exact-byte types;
2. valid P'/F' admission row and exact W'/render/V' tuple match;
3. WitnessV3/render/component/geometry normalization to `M`;
4. extraction of the exact canonical `flow_input` from that same decoded W';
5. existing flow/adjacency normalization to `E`;
6. existing CrossCheckV2 normalization against exact `M`, `E`, and V';
7. return only the closed private normalized `M/E/V` composition.

The function must not accept a pre-normalized mechanics object, flow object,
fixture id, path, parser, callback, dict supplied separately from W', or a
mechanics/flow result made by test code. It must not infer flow from geometry,
V, paint order, component bboxes, or fixture identity.

The existing witness normalizer may be split into a shared canonical WitnessV3
decoder plus mechanics normalization, or may return the exact `flow_input`
alongside `M`. It must decode the witness canonically once per composition and
must not trust a separately decoded/mutable copy.

### 4.4 Public fail-closed behavior

`derive_fixture_page_block_ledger_v1` may call the private composition only
after all existing coverage, registry, ingress, row-match, and authority gates.
After a valid private test activation it must still raise exactly
`page_proof_public_boundary_incomplete` and return nothing. Under unchanged
production roots it must still fail first with
`page_proof_stage_a_fixture_coverage_incomplete` before caller access.

`review_fixture_page_block_ledger_v1` and
`replay_fixture_page_block_ledger_v1` remain boundary-only after their existing
ordered schema checks. No candidate, review, rejected result, accepted result,
or exact replay is implemented here.

## 5. Deterministic test contract

### 5.1 Positive composition evidence

For each canonical admitted fixture (two-column, nested Form, visual-only), the
new composition suite must:

1. use literal W'/render/V' leaves and a fully valid private admission row;
2. use the exact fixture-only Stage A authority already exercised by accepted
   tests, without opening any PDF or constructing new Stage A topology;
3. independently assert P', F', exact leaf lengths/hashes, and admission tuple;
4. invoke the composition function once;
5. compare its complete normalized `M`, `E`, and V result to separately declared
   literal primitive expectations, not expectations generated by the SUT;
6. prove two-column order, nested-frame paint placement, explicit exclusions,
   visual-only zero included fragments, and exact paragraph adjacency retain
   their accepted values.

### 5.2 Required P0/P1 negatives only

The suite must contain target-only negative/repair evidence for:

- old WitnessV2 schema under otherwise current leaves;
- missing, unknown, mistyped, or noncanonical `flow_input` root;
- duplicate/missing/reordered block ownership;
- included/excluded partition substitution;
- missing/extra/non-adjacent adjacency;
- a fully resealed W'/F' flow mutation whose stale V pre-visual core is rejected;
- cross-pairing W', render, or V' between canonical rows;
- an attempt to call composition with separately supplied/pre-normalized flow;
- an attempt to remove flow and derive it from V or geometry.

Each internal negative starts from a valid private row and exact W'/render/V'
tuple, mutates one semantic target, reseals only its dependent hashes in
topological order, demonstrates the intended first failing predicate/error, then
inverse-repairs the same target and reproduces the literal positive composition.
Do not add exhaustive P2/P3 variants or the later full adversarial matrix.

### 5.3 Static and public-boundary assertions

- Literal helper AST: no imports, calls, comprehensions, runtime hash/JSON
  builders, filesystem operations, or production references.
- Composition AST/call graph: exactly one path
  `W'/render -> M -> flow_input -> E -> V'`; no geometry-to-flow,
  V-to-flow, fixture-id-to-flow, code-owned flow table, parser, filesystem,
  network, subprocess, environment, dynamic import, or candidate/review call.
- Existing visual-crosscheck canonical layout remains exactly 98 direct
  normalizer calls with all 46 target names and complete P/F containment,
  updated only for the WitnessV3/P'/F' literal identities.
- Production roots are exactly unchanged and empty/incomplete; all three public
  APIs retain coverage-first poison/no-result behavior.
- With test-only private activation, derive reaches composition and then only
  `page_proof_public_boundary_incomplete`; review/replay expose no terminal.

### 5.4 Mandatory commands

The executor first discovers and confirms the current Python executable and
version. It then runs only:

```powershell
& '<confirmed Python>' -B -m py_compile `
  kb_creator/pdf_raw/page_proof.py `
  kb_creator/tests/test_page_proof_composition.py `
  kb_creator/tests/test_page_proof_visual_crosscheck.py

& '<confirmed Python>' -B -m pytest -q -p no:cacheprovider `
  kb_creator/tests/test_page_proof_coverage_guard.py `
  kb_creator/tests/test_page_proof_stage_a_topology_inventory.py `
  kb_creator/tests/test_page_proof_fixture_admission.py `
  kb_creator/tests/test_page_proof_closed_schemas.py `
  kb_creator/tests/test_page_proof_witness_render_components.py `
  kb_creator/tests/test_page_proof_flow_adjacency.py `
  kb_creator/tests/test_page_proof_visual_crosscheck.py `
  kb_creator/tests/test_page_proof_composition.py
```

The receipt records exact commands, interpreter/version, pass count/time, and
post-run SHA-256 for every allowed changed file. No broad suite is required.

## 6. Definition of Done

Packet `4b.7` is implementation-reviewable only when all are true:

1. WitnessV3 is closed, canonical, and carries exact literal `flow_input`.
2. P'/W'/M/E/V'/F' is acyclic and every dependent literal is independently
   pinned; no expected output hash enters P' or F'.
3. The three canonical admitted fixtures compose deterministically from the
   four existing public derive inputs with no hidden flow authority.
4. Existing 4b.4 mechanics, 4b.5 flow, and 4b.6 visual normalized semantics are
   unchanged and the exact 98-call visual evidence layout remains intact.
5. Required target-only negatives fail at their named layer and inverse repair
   reproduces the literal baseline.
6. Production topology/admission roots remain inactive; public derive/review/
   replay return no wrapper, ledger, plaintext, mutable dict, or terminal.
7. Only the allowed files and one new executor receipt changed.
8. `py_compile` and the exact eight-suite fixture-only command pass.
9. A fresh independent Terra implementation critic at `high`, who did not
   implement or materially design the candidate, reports no P0/P1.

Passing tests alone are not acceptance and this packet is not release evidence.

## 7. Acceptance evidence required from the independent critic

The critic must independently:

- verify all frozen before-hashes and all executor after-hashes without Git;
- reconstruct the P'/W'/M/E/V'/F' graph and reject any hidden flow source,
  schema alias, final-binding back-edge, or partial literal migration;
- inspect all three literal WitnessV3 `flow_input` values and compare their
  normalized M/E/V results to independent primitive expectations;
- verify target-only admission validity and dependent resealing before each
  internal negative and repair;
- re-establish the 98-call/46-target visual-crosscheck evidence and complete
  P/F AST containment against the migrated identities;
- confirm the four production roots are still inactive and every public route
  remains no-result and coverage-first;
- run only the mandated commands and record exact counts, times, and candidate
  hashes;
- issue `accept` only with no open P0/P1. P2/P3 observations are recorded as
  debt and do not gate this packet.

This is an implementation review, not a final release review.

## 8. Dependencies, risks, and fail-closed rollback

Dependencies:

- independently accepted Packet `4b.6` baseline at the hashes in section 2;
- existing fixture-only Stage A authority constructors already used by the
  accepted tests;
- no production topology-acceptance identity is required or permitted.

Primary risks and controls:

| Risk | P0/P1 control |
| --- | --- |
| Flow remains test-generated | flow is literal inside canonical W'; composition accepts no separate flow |
| Adding flow silently changes WitnessV2 | mandatory WitnessV3 schema id and closed-key rejection of V2 |
| P/F migration becomes cyclic | retain P/F formulas; recompute in strict P' -> W'/E -> V' -> F' order |
| V becomes the flow authority | V is consumed only after E; any V-to-flow edge is P1 |
| Production test surrogate is activated | all four production roots must remain unchanged/inactive |
| 4b.6 evidence is invalidated without replacement | exact seven-suite regression, 98-call proof, and fresh Terra review are mandatory |

Fail closed:

- Any partial V3/P'/V'/F' migration, old/new cross-pair, missing flow, hidden
  fallback, semantic baseline drift, changed production root, or candidate/
  terminal output is a P0/P1 rejection with no accepted packet result.
- No compatibility fallback to WitnessV2 is allowed.
- Because production roots remain inactive, a failed or abandoned candidate
  cannot expose a public proof route. The accepted pre-packet hashes in section
  2 are the recovery point; restoration or integration is orchestrator-owned,
  not contributor-owned, and must not use Git under this packet.

Remaining blocker after successful Packet `4b.7`: exact production topology
acceptance identities are still absent. This receipt does not design or
authorize how any later packet resolves that blocker.

## 9. Next owner

Next owner: a bounded **Terra engineering** contributor at `medium`, because the
packet couples a versioned literal-leaf migration with P/F resealing and the
accepted 98-call visual evidence. The contributor implements sections 3–6 only
and writes one immutable executor receipt. A different, fresh Terra critic at
`high` then performs section 7. Neither role inherits orchestration ownership.

## 10. Handoff accounting

- Scope: architecture/root-cause analysis and one P0/P1-only fixture Packet
  `4b.7`; no implementation or acceptance.
- Files checked: root `AGENTS.md`; canonical NRI goal governance; assigned
  `plan.md` and `context.md`; contract status; original Sol contract and P1
  correction; implementation packetization; all Packet `4b.1`–`4b.6`
  implementation, remediation, architecture, and independent-review receipts;
  especially the final 4b.6 acceptance; current `page_proof.py`, literal leaves,
  and the seven accepted fixture-only test modules.
- Files changed: this immutable handoff only.
- Verification/evidence: read-only schema, dependency, receipt, source, and
  SHA-256 inspection. No test, PDF, parser, renderer, browser, network, build,
  output, Git, registry, or implementation action was run.
- Blockers: none to the specified private fixture composition packet; production
  activation remains blocked by absent authoritative topology-review identities.
- Next action: orchestrator may assign the bounded Terra engineering packet in
  section 9; do not assign review/replay, registry activation, Packet `4b.8`,
  Step `5`, or release work from this receipt.
- Elapsed active time: approximately `34 minutes`.
- Token use: `unavailable`.
- Timestamp: `2026-08-11T16:39:16.2219412+03:00`.

This receipt is immutable. A correction must use a new handoff and explicitly
supersede this file. It does not transfer orchestration ownership and does not
act as the final release reviewer.

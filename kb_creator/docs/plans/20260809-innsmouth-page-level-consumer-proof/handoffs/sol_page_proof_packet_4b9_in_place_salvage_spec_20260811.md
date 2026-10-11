# Immutable Sol Handoff — Packet 4b.9 In-Place Fixture Re-Proof

## Receipt

- Goal id: `20260809-innsmouth-page-level-consumer-proof`.
- Step id: `4b.9-in-place-salvage-specification`.
- Role: Sol architect.
- Requested effort: `high`.
- Actual platform model/effort: `unavailable`; repository role assignment is
  platform-unverified.
- Orchestrator policy owner: main-chat `gpt-5.5` at `medium`
  (`platform-unverified`). Orchestration ownership remains with the main chat.
- Assignment state: `platform-unverified role policy`.
- Scoped override: `none`.
- Scope: architecture and remediation specification for a new, unaccepted,
  in-place fixture-only candidate consisting of the current seven page-proof
  test files. This receipt performs no implementation, acceptance, production
  activation, public terminal/result work, live preflight, release review, or
  release decision.
- Result: **specified**. The old byte-exact pre-4b.9 baseline is not a
  dependency and must not be requested, reconstructed, or partially restored.
  The current seven files may be accepted only after the complete fixture-only
  re-proof below and two fresh independent Terra/high reviews.

## 1. Architectural decision

The seven current files are one new candidate snapshot, `S0`. They are not the
accepted 4b.7 baseline, not a restored 4b.9 baseline, and not accepted merely
because their literals appear internally consistent. Prior 4b.6 through 4b.8
receipts remain authoritative for contract semantics and the two accepted
child identities, but their former seven-file hashes are not reused as current
candidate acceptance evidence.

The salvage packet has one purpose:

> Independently re-prove from current fixture bytes that the complete
> `4b.6 -> 4b.7 -> 4b.8 -> 4b.9` test-only graph is closed, non-circular,
> semantically unchanged, bound to exactly the two accepted child identities,
> and unable to activate production or return a public result.

There are only three branches:

```text
S0 hashes match this specification
  -> build the independent salvage oracle
    -> all exact invariants already hold
      -> preserve all seven S0 files byte-for-byte; add only oracle + receipt
    -> a named invariant fails but is repairable inside the exact allowed set
      -> target-only in-place repair; reseal dependent identity fields only
      -> rerun the complete oracle and fixture regression

S0 drift, authority drift, semantic drift, or repair needs forbidden scope
  -> stop without further mutation
  -> write a blocker receipt
  -> 4b.9 remains unaccepted
```

No branch may use the missing
`B471EB875410C09CDEF9ABA3F39082C3201F815D6C62ED9F3165A4ED58E1DF7E`
fixture-leaves file as a required input. No six-file or other partial rollback
is permitted. An inverse replacement toward old literals is not salvage.

## 2. Candidate snapshot and frozen read-only boundary

### 2.1 Unaccepted `S0` input snapshot

An executor must verify these current SHA-256 values before its first write.
They identify the candidate to which this specification applies; they do not
make it accepted.

| Current candidate file | Required `S0` SHA-256 |
| --- | --- |
| `kb_creator/tests/_page_proof_fixture_leaves.py` | `EAFA65CFB474C2150DBC3632BF4F67364533D3D1CB9CF92B4D01A326F535C0EA` |
| `kb_creator/tests/test_page_proof_fixture_admission.py` | `0E05C55FA59087E87D6CCB9A6EDC678EB527264DAA56230D892FB66558EA2561` |
| `kb_creator/tests/test_page_proof_closed_schemas.py` | `526CB1A10F50ADDBE8262CBE0DBDE52DEE01E961691222E825461E512F3A8318` |
| `kb_creator/tests/test_page_proof_witness_render_components.py` | `7491E9A3DE3A0A7D34C089CF30D3C25408FFF239A2416FEFD8B671CCAD0D86CD` |
| `kb_creator/tests/test_page_proof_flow_adjacency.py` | `4718AA5619AD7E29363E5AE698CC43D41959443581167ECBF701734A0EB7FC2D` |
| `kb_creator/tests/test_page_proof_visual_crosscheck.py` | `1D92240D165F61A9905F5442B78686EF3A555DDD7A015D00AB4E222DA8C244A5` |
| `kb_creator/tests/test_page_proof_composition.py` | `94203585B8A54B20C91B982FF85F8F6D8F8CF8D4CC0D0F6426FDDFD5EC38550D` |

`kb_creator/tests/test_page_proof_private_authoritative_inventory_reseal.py`
must be absent at executor start. Any `S0` mismatch or pre-existing target file
is a stale-packet blocker; do not normalize or silently adopt different bytes.

### 2.2 Frozen read-only implementation and regression inputs

The following hashes must match before and after implementation:

| Read-only file | Required SHA-256 |
| --- | --- |
| `kb_creator/pdf_raw/page_proof.py` | `269E244F15445DF8EE81D3FFF33297705197F1BDCD703369C1342A49698114C2` |
| `kb_creator/tests/test_page_proof_coverage_guard.py` | `0065DB7A34C45DC4FBD17719825C3AA1566A9CCC7B484BB7A0AC30041D9D964A` |
| `kb_creator/tests/test_page_proof_stage_a_topology_inventory.py` | `E9752542CA1574437AA24B8097CA5D30A4A7A7B434ED0146D72C66EF83165203` |

The accepted Stage A module and six Stage A test inputs retain the hashes
recorded by the 4b.8 aggregate acceptance receipt. Their mismatch is a blocker;
they are not repairable in this packet.

The production module must continue to expose only the existing three public
names, retain `PageProofWitnessV3`, and retain all four inactive roots:

```text
_PRODUCTION_REQUIRED_STAGE_A_TOPOLOGY_INVENTORY.entries == ()
_PRODUCTION_REQUIRED_STAGE_A_TOPOLOGY_INVENTORY.entry_count == 0
_PRODUCTION_EXPECTED_TOPOLOGY_PRIMITIVES[2] == ()
_PRODUCTION_EXPECTED_TOPOLOGY_PRIMITIVES[3] == 0
_PRODUCTION_FIXTURE_ADMISSION == ()
_PRODUCTION_EXPECTED_FIXTURE_ADMISSION_PRIMITIVES == ()
```

## 3. Exact allowed implementation write set

A later implementation may change only these exact paths:

1. `kb_creator/tests/_page_proof_fixture_leaves.py`
2. `kb_creator/tests/test_page_proof_fixture_admission.py`
3. `kb_creator/tests/test_page_proof_closed_schemas.py`
4. `kb_creator/tests/test_page_proof_witness_render_components.py`
5. `kb_creator/tests/test_page_proof_flow_adjacency.py`
6. `kb_creator/tests/test_page_proof_visual_crosscheck.py`
7. `kb_creator/tests/test_page_proof_composition.py`
8. `kb_creator/tests/test_page_proof_private_authoritative_inventory_reseal.py`
9. `kb_creator/docs/plans/20260809-innsmouth-page-level-consumer-proof/handoffs/executor_page_proof_packet_4b9_in_place_salvage_20260811.md`

The preferred successful write set is only paths 8 and 9. A path among 1–7
may change only when the independent oracle first demonstrates a named failed
invariant and the repair changes the target field plus its downstream seals,
without changing accepted mechanics, flow, visual, or public semantics. The
executor receipt must explain every changed byte-bearing identity and show why
each changed existing file was necessary.

No cleanup, deduplication of the layered fixture literals, refactor, helper
framework, formatting churn, test renaming, schema change, public change, or
P2/P3 expansion is allowed.

## 4. Authority and dependency contract

### 4.1 The only admissible 4b.8 child identities

The inventory must consume both rows atomically and in this order:

| Field | two-column | nested Form |
| --- | --- | --- |
| `topology_id` | `stage_a_positive_two_column.v1` | `stage_a_positive_nested_form.v1` |
| `stage_a_fixture_id` | `stage-a.positive-two-column.v1` | `stage-a.positive-nested-form.v1` |
| authority schema | `kb_creator.pdf_raw.RawAtomProvenanceAuthority.v1` | same |
| authority content | `890a9cef3ce995e7cb7881c035baa3e1e5a4c782f1827847b640c93fb28eafef` | `8726e5d36b7acba9d96eacdcd62a57da00d7f4cfdd4df79cd6c63106d2e353e7` |
| authority inventory | `3173d033fcf6228687388f020f0e5e6e7e9c1ce2a373bc1b2bca49823ab951c0` | `f296a28a72e509f47fe294217492cc463375c30144f8deab57fd7b4c85678b21` |
| fixture binding | `c41ec7ae9eea7d5fc2f654eb825bf1bb1af954d00c754fd6140f134985af8880` | `9b0f9f382e7926e3447072fa9340c38dd93531302e4294a14d8436eeacdf1d0a` |
| positive assertion facts | `e681b6ffbed2705283b915039e1d7a6ac145f4988765fd772a68eb63803831c8` | `a82adc738fd89394e80a607df46f7775a1967f874267f3b0289e7e64829d3d0f` |
| review kind / decision | `fixture_topology_acceptance` / `accept` | same |
| accepted child identity | `74ddca65755dbde190b57a5e82368895644ac6b605873913c20a32f2786d6526` | `136489ff1892bb27b8425806a1972809d03ce5e5e22f42b6a9f1bdfeca1cc503` |
| reviewed authority content | equals own authority content | equals own authority content |
| entry SHA-256 | `31a05f30ebd7919f27191f2986c679c32c6fb739724a5364bdaef1d3b8b04673` | `e7693b62761befda746fb405e1f6f5c89bca6ad91fea877110cd1e4a9d0844f6` |

The private root must recompute exactly to:

```text
schema = PageProofRequiredStageATopologyInventory.v1
required_topology_ids = (
  stage_a_positive_two_column.v1,
  stage_a_positive_nested_form.v1,
)
entry_count = 2
inventory_sha256 = 3d707193bfe883dbe510e1ccdc169ac21e28c7b3a8fda697446a126fae7cdfd6
content_sha256 = 4d3683f15ae64b4d03e51211755f2b3580e112e35bce4bf8c69efa29645dd3b4
```

The aggregate 4b.8 receipt hash, a prior review hash, the old surrogate
`d0891ce46fc9cb3aeee366cf78610996b3e2a34e94d85c47e9d212599a438ac6`,
one child alone, a duplicate child, swapped child mappings, or a freshly
self-consistent arbitrary record is never authority.

### 4.2 Acyclic identity and semantic graph

The complete graph is:

```text
C2C + CNF -> E2C + ENF -> I -> T
T + stable fixture/render/schema identity -> P
P + T + literal WitnessV3 flow_input -> W
W + render + Stage A authority -> M
M.flow_input -> E
P + T + identity-dependent pre-visual core(M,E) + visual facts -> V
P + exact W/render/V leaf identities -> F
valid row(P,W,render,V,F) -> private W -> M -> E -> V composition
```

`P` is the pre-visual seal and never depends on `W`, `V`, `F`, expected
candidate hashes, or expected reviewed-ledger hashes. `W` and `V` carry `P`,
never `F`. `F` is computed last and binds exact W/render/V identities. There
must be no cycle, fixed-point reseal, fallback, or retry-until-valid path.

### 4.3 Exact candidate leaf checkpoints to be independently proved

These values are expected consequences of section 4.1 plus the preserved
fixture semantics. They become acceptable only when recomputed by the
independent oracle; their current presence is not proof.

| Fixture | P | W content / bytes / raw SHA-256 | V content / bytes / raw SHA-256 | F |
| --- | --- | --- | --- | --- |
| two-column | `cdb993a29ef0b05229a9a9c5dfd65dd30977df9c3ec1c295a88a94b5ea1f9c1d` | `172ae571a4da210c0f8cdd5faf4e82bbf1fe9e718448a89369ce38250d9a6594` / `3050` / `d08e02060ccb8a602a445cc14f0e71fd16fbcf1616d826463e00c64f46948295` | `d38f51bba2b575528a32b572084b12ba2be33060e972ad7138a70eee9d580f73` / `2501` / `2c358a6feb63859fa2f4c10346bd64e26da13f1e6d64f7cce5a868f881cab2c5` | `0c45fd6b6440482b377fbcd3c6797701e622250dc0fdd496d18dbef81cd48838` |
| nested Form | `388f7cc61345dbbcb516a4090e0d35cabb308f37137bf9b6b86c691fbf6c122c` | `aa95cc4c1ec640b9644e4febfb3e1d6f729be64b4544849ae5a9ffd4fd2c63e0` / `2927` / `c488c0491139d27e696b5ab4ea4205b5ada0a9f577e3c3a23231868469eb85c3` | `f332b60fd1107f66ccff5e497a071f8438be9dc4d5e1e6c22734b9abbb6dbc97` / `2084` / `887aba071a09620cdc4789a5635ba57661eff0eec0792ad50db66af3a2d4f0d3` | `249d56182c4710e6392740703ed86d388b714498d1bbc9c60e403de0caf0fbf2` |
| visual-only | `7f9327e3dba8c5ad888efa3423115e779b0bb0502438e7ddd9c02cd2c43dbea2` | `0d9b5d5faf83844591daaf8b2b471c2c03564653e47769b45ea0abef0167fb39` / `2125` / `68d22df7ade83daa01348bcd25dc90ec69a9f0efe73b9f6f0bb0b9cfe379fb2e` | `7995e65505d53305ff53811e0221b64496d93bf8b8a29a753d9683d0c1ac2f1f` / `1461` / `1e47e656240499dcc6d2c1e25a64691fe99c02d9801b6f52b2f8cc80993f1c76` | `4d9c98331427c55f788ee2fc532365434054e6d300236120fc11946c7894aecd` |
| two-boundary evidence-only | `cdb993a29ef0b05229a9a9c5dfd65dd30977df9c3ec1c295a88a94b5ea1f9c1d` | `7d014e1cdb5ce542936a91b28615cc86f508208ec3a190dba84a990dd145e86d` / `3186` / `e468e847f15c602d80808b572332978da2cd87eaa0009d766ae484ada80d1677` | `9083762bc843dacf0937f809809a8c82a4eed96326a7eb2dfab9870bb8d4aef0` / `2928` / `761fc6aca16af4972d31081f4ad620f7f369c0c984c972f411ce196e4a95a2f4` | `afd101e900a5242cf0c7867102272997e719ea3f183c5e096d0e5c1c826c522e` |

The two-boundary case remains visual evidence only and is not a fourth
admission row.

## 5. Independent salvage oracle

The new
`test_page_proof_private_authoritative_inventory_reseal.py` must contain
exactly these twelve non-parameterized tests:

1. `test_authoritative_child_identities_materialize_exact_private_inventory_literals`
2. `test_private_inventory_expected_tuple_is_independent_and_complete`
3. `test_child_identity_missing_duplicate_swapped_and_wrong_source_hash_fail_closed`
4. `test_surrogate_and_non_child_hash_substitutes_never_complete`
5. `test_all_three_resealed_admission_rows_bind_exact_authoritative_inventory`
6. `test_all_three_resealed_compositions_preserve_literal_semantic_projection`
7. `test_two_boundary_visual_evidence_reseals_without_semantic_drift`
8. `test_stale_p_w_v_f_each_fail_at_the_named_layer_and_inverse_repair_recovers`
9. `test_mixed_old_new_and_cross_pair_rows_fail_closed`
10. `test_expected_output_hashes_remain_unconsumed_and_unreachable`
11. `test_production_roots_remain_inactive_and_public_poison_is_coverage_first`
12. `test_static_containment_reproves_4b6_through_4b9`

The oracle rules are mandatory:

- All authority rows, expected primitive tuples, semantic projections, P/W/V/F
  checkpoints, target names, and source-structure expectations are literal in
  this new test module. They may not be imported from another test module,
  copied from a parsed receipt at runtime, derived from current candidate
  output, or generated by production sealing helpers.
- Canonical JSON and SHA-256 are recomputed with stdlib-only oracle functions
  that are separately implemented from production helpers. Production helpers
  are the system under test and may only be compared against oracle results.
- The candidate's raw literal leaves may be imported from
  `_page_proof_fixture_leaves.py`; their expected lengths, hashes, content
  seals, flow facts, and semantic projections come from the independent
  literals in the new oracle.
- Fixed-path, read-only `ast` inspection is allowed only for the eight test
  modules and `page_proof.py` named in this specification. No globbing, path
  discovery, environment selection, receipt parsing, dynamic import, plugin,
  subprocess, network, source/output path, or public positive route is allowed.
- The old surrogate digest may occur as one literal negative control in the
  new oracle. It must occur zero times in the seven candidate files and on no
  positive route.

## 6. Required re-proof by packet

### 6.1 Packet 4b.6 — canonical visual-crosscheck containment

The oracle and retained visual suite must jointly prove all of the following:

1. Exactly four named positive fixtures each contain one direct
   `_normalize_fixture_visual_crosscheck` call.
2. The exact accepted 46 target-only test names each contain two direct calls:
   one negative and one inverse-repaired positive.
3. The two outer-envelope tests each contain one direct call.
4. Total direct normalizer call sites are exactly `98`; exactly `96` internal
   calls have the immediately adjacent full pre-normalizer contract.
5. Every internal call has an inline literal 15-key boolean predicate map;
   there is no generated vector, parameterized call, helper-hidden call, loop,
   comprehension, callback, lambda, retry, or whole-baseline replacement.
6. Each negative has valid admission and current non-target seals before the
   named internal predicate is reached. The repair is the inverse of the one
   semantic mutation, reseals only downstream identity fields, and reproduces
   the literal positive normalized bytes.
7. The two-boundary facts remain exactly `f0 -> f1` within `b0`, then
   `f1 -> f2` across `b0 -> b1`, with the accepted columns, boxes, decisions,
   and ordered decision inventory.
8. Independent AST closure proves the complete P/F field sets, dependency
   edges, domains `page-proof.fixture-pre-visual-binding.v1\0` and
   `page-proof.fixture-admission.v2\0`, and absence of final/output/visual
   predicate dependencies from P.

Missing, duplicate, reordered, aggregate-like boundary rows; block and
boundary region/decision fields; transcription; reviewer; inventory; root
content; P; V; and F must all retain named target-only failure and inverse
repair evidence. A stale outer admission rejection is not evidence for an
inner visual predicate.

### 6.2 Packet 4b.7 — WitnessV3-bound private composition

The three admitted witnesses and the two-boundary witness must be closed
canonical `PageProofWitnessV3` objects with one admitted `flow_input`. The
private composition must:

```text
validate exact row and W/render/V leaves
  -> decode the same W once into M
  -> pass only M.flow_input into E
  -> pass that M and E into V normalization
  -> return private normalized mechanics/flow/visual data only
```

The independent literal semantic projections must preserve:

- two-column: included blocks `b0,b1`, fragments `f0,f1`, and one
  `f0 -> f1` cross-column adjacency;
- nested Form: included `b0`, excluded `b1` with `running_marginal`, fragments
  `n0,n1`, and no adjacency;
- visual-only: included set empty, excluded `b0` with `visual_only`, fragment
  `v0`, and no adjacency;
- two-boundary: included `b0,b1`, fragments `f0,f1,f2`, and the exact two
  ordered adjacencies in section 6.1.

The composition AST must have exactly one witness/mechanics normalizer call,
one flow normalizer call, and one visual normalizer call, in that order, with
no separate flow parameter or entry point. Tests must retain target-only
rejection and inverse repair for WitnessV2, missing/unknown/mistyped/
noncanonical `flow_input`, ownership, partition, adjacency, stale V pre-visual
core, W/render/V cross-pairs, and attempted separately supplied or
pre-normalized flow. Geometry, V, fixture id, environment, or code-owned tables
may not infer or replace flow.

### 6.3 Packet 4b.8 — accepted topology identity closure

Both section 4.1 child identities must be present, distinct, mapped only to
their own topology/fixture/authority facts, and admitted atomically. Independent
oracles must recompute both entry seals and both root seals. Missing, duplicate,
reordered, swapped, wrong-source, aggregate-receipt, prior-review, surrogate,
and arbitrary-rehash variants must be fully resealed at every non-target field,
fail `_inventory_is_complete`, and inverse-repair to the exact literal root.

This proves only fixture topology identity closure. It does not promote Stage A
claims from `not_proved_stage_a`, activate production, or authorize a live
consumer.

### 6.4 Packet 4b.9 — authoritative inventory and P/W/V/F reseal

All three admission rows must be self-valid and match a separately written
sixteen-field expected primitive tuple. The registry must validate only against
the exact private inventory content digest in section 4.1. The two-boundary
row must remain evidence-only.

For each admitted fixture, independent oracles must establish the exact
section 4.3 chain in this order: `T -> P -> W -> M/E -> V -> F`. Isolated
negative cases must prove stale P, stale W, stale V, and stale F at their named
layer after every non-target dependency is current; each inverse repair must
reproduce the exact section 4.3 literal chain. Mixed old/new chains, cross-pair
rows, and a valid row paired with a wrong leaf must fail before composition is
accepted.

The retained `expected_candidate_sha256` and
`expected_reviewed_ledger_sha256` values are historical, unconsumed fields.
They are outside P and F, may not be validated as current output, may not
produce candidate/reviewed bytes, and may not be used to claim a ledger,
review, replay, terminal, or public result.

## 7. Public and production fail-closed contract

All three real public APIs must be called only with poison objects against the
unchanged real production roots. Each must raise exactly
`page_proof_stage_a_fixture_coverage_incomplete` before reading, coercing,
iterating, hashing, comparing, or otherwise touching any caller value.

No new 4b.9 test may monkeypatch a production root or use a public API as
positive proof. Existing unchanged scoped monkeypatch regression tests may
continue to prove later error precedence, but they do not constitute production
activation. No public function may return a wrapper, candidate, review, replay,
ledger, plaintext, mutable result, success state, or terminal result.

## 8. Deterministic verification commands

Run from `D:\NRI`. Discover and record the executable/version first. On the
currently verified workstation the interpreter is
`D:\NRI\.tools\python-3.13.14\python.exe` (`Python 3.13.14`). Use the confirmed
path, not an unverified alias.

Syntax verification:

```powershell
& 'D:\NRI\.tools\python-3.13.14\python.exe' -B -m py_compile `
  kb_creator\tests\_page_proof_fixture_leaves.py `
  kb_creator\tests\test_page_proof_fixture_admission.py `
  kb_creator\tests\test_page_proof_closed_schemas.py `
  kb_creator\tests\test_page_proof_witness_render_components.py `
  kb_creator\tests\test_page_proof_flow_adjacency.py `
  kb_creator\tests\test_page_proof_visual_crosscheck.py `
  kb_creator\tests\test_page_proof_composition.py `
  kb_creator\tests\test_page_proof_private_authoritative_inventory_reseal.py
```

Fixture-only collection shape:

```powershell
& 'D:\NRI\.tools\python-3.13.14\python.exe' -B -m pytest --collect-only -q -p no:cacheprovider `
  kb_creator\tests\test_page_proof_coverage_guard.py `
  kb_creator\tests\test_page_proof_stage_a_topology_inventory.py `
  kb_creator\tests\test_page_proof_fixture_admission.py `
  kb_creator\tests\test_page_proof_closed_schemas.py `
  kb_creator\tests\test_page_proof_witness_render_components.py `
  kb_creator\tests\test_page_proof_flow_adjacency.py `
  kb_creator\tests\test_page_proof_visual_crosscheck.py `
  kb_creator\tests\test_page_proof_composition.py `
  kb_creator\tests\test_page_proof_private_authoritative_inventory_reseal.py
```

Required collection result: exactly `159 tests collected` — the currently
observed `147` existing cases plus the exact twelve-test oracle.

Fixture-only execution:

```powershell
& 'D:\NRI\.tools\python-3.13.14\python.exe' -B -m pytest -q -p no:cacheprovider `
  kb_creator\tests\test_page_proof_coverage_guard.py `
  kb_creator\tests\test_page_proof_stage_a_topology_inventory.py `
  kb_creator\tests\test_page_proof_fixture_admission.py `
  kb_creator\tests\test_page_proof_closed_schemas.py `
  kb_creator\tests\test_page_proof_witness_render_components.py `
  kb_creator\tests\test_page_proof_flow_adjacency.py `
  kb_creator\tests\test_page_proof_visual_crosscheck.py `
  kb_creator\tests\test_page_proof_composition.py `
  kb_creator\tests\test_page_proof_private_authoritative_inventory_reseal.py
```

Required result: exactly `159 passed`.

Upstream fixture-topology recheck:

```powershell
& 'D:\NRI\.tools\python-3.13.14\python.exe' -B -m pytest -q -p no:cacheprovider `
  kb_creator\tests\test_raw_authority_projection_stage_a_topology_authorities.py

& 'D:\NRI\.tools\python-3.13.14\python.exe' -B -m pytest -q -p no:cacheprovider `
  kb_creator\tests\test_raw_authority_projection_stage_a_contract.py `
  kb_creator\tests\test_raw_authority_projection_stage_a_replay.py `
  kb_creator\tests\test_raw_authority_projection_stage_a_boundaries.py `
  kb_creator\tests\test_raw_authority_projection_stage_a_containment.py `
  kb_creator\tests\test_raw_authority_projection_stage_a_adversarial.py `
  kb_creator\tests\test_raw_authority_projection_stage_a_topology_authorities.py
```

Required results: exactly `15 passed` and `386 passed, 1 skipped`. The one skip
must retain the already accepted FlateDecode identity-offset justification.
Count drift, a new skip, or changed collection is a blocker and may not be
resolved by changing this contract during implementation.

## 9. Acceptance criteria

Packet 4b.9 in-place salvage is eligible for implementation acceptance only if
all criteria hold:

1. The seven `S0` hashes matched before the first write; no old baseline or
   partial rollback was used.
2. Every read-only hash and all four inactive production roots match before
   and after.
3. The independent oracle meets section 5 without circular expected values.
4. Both exact 4b.8 child identities form the exact private inventory and all
   four inventory seals in section 4.1 recompute independently.
5. Every positive fixture and the two-boundary evidence case independently
   reproduce the exact P/W/V/F checkpoints in section 4.3.
6. Every 4b.6 visual containment rule and every 4b.7 WitnessV3 composition
   rule in section 6 is re-established from current source and runtime
   behavior, including target-only mutation and inverse repair.
7. No positive route contains the old surrogate; expected output hashes remain
   unconsumed and unreachable.
8. Public poison calls fail coverage-first before caller access; production
   roots and public surfaces remain inactive and unchanged.
9. Only the exact section 3 paths changed. Every changed existing candidate
   file has a named necessity, before/after SHA-256, and identity-only repair
   explanation in the executor receipt.
10. All section 8 commands pass with exact counts.
11. A fresh independent Terra/high implementation critic who neither
    implemented nor materially designed the candidate verifies the after
    hashes and reports no P0/P1.

Passing tests alone do not accept the packet. Acceptance is fixture-only and
non-release; it does not authorize Packet 5, a live preflight, a candidate
ledger, reviewed ledger, replay terminal, production activation, or release.

## 10. Rejection triggers

Any one of the following rejects or blocks the candidate:

- `S0` or a frozen read-only hash differs before work.
- The missing old fixture-leaves bytes are treated as required, guessed, or
  reconstructed, or any partial rollback is attempted.
- A repair changes semantics rather than only a named target and downstream
  identity seals, or needs a file outside section 3.
- Expected values are generated from production helpers, candidate outputs,
  current leaves, another test's constants, or parsed receipts.
- A negative case fails at stale admission/leaf metadata before reaching its
  named inner predicate, or repair replaces the whole baseline instead of
  applying the semantic inverse.
- Either child identity is absent, duplicated, swapped, substituted, or used
  alone; the old surrogate survives a positive route; or any P/W/V/F chain is
  mixed.
- The visual layout is not exactly 98 calls / 46 targets / 96 adjacent
  contracts, P/F containment is incomplete, or WitnessV3 composition accepts
  a separate or inferred flow.
- A production root, public signature, `__all__`, schema, error precedence,
  expected output hash, Stage A input, or production module changes.
- A public path touches caller input before coverage or returns any successful
  object/result/terminal state.
- Any dynamic import, plugin, filesystem discovery, environment selector,
  network, browser, subprocess, Git, live PDF/source, EN, KeeperBook, HTML,
  PDF, output/build, production activation, release path, or canonical
  plan/context/status/contract/release edit occurs.
- Test counts differ, a required command fails, a new skip appears, or the
  independent implementation critic has an open P0/P1.

On rejection, stop. Do not auto-repair Stage A, regenerate from a different
candidate, widen scope, use Git restoration, or request release review.

## 11. Required independent Terra/high architecture review checklist

Before any implementation, a fresh Terra/high critic who did not write or
materially design this specification must write an immutable architecture
receipt and answer every item explicitly:

1. Independence declaration, review kind `architecture`, non-release state,
   policy orchestrator, assignment state, and scoped override `none`.
2. Confirms `S0` is an unaccepted current snapshot only; confirms the missing
   old baseline is not required and partial rollback is prohibited.
3. Confirms section 3 is the complete and minimal later write set and that
   `page_proof.py`, Stage A, canonical state, production, and release files are
   read-only.
4. Independently checks both 4b.8 child records and recomputes both entry seals,
   inventory seal, and content seal from literal values.
5. Audits the acyclic `C -> E -> I -> T -> P -> W -> M/E -> V -> F` graph and
   verifies P/F ownership and output-hash exclusion.
6. Maps every 4b.6, 4b.7, 4b.8, and 4b.9 invariant in section 6 to a concrete
   oracle assertion or retained exact regression assertion; no acceptance may
   rely only on historical file hashes.
7. Confirms the oracle is independent: literal expected primitives and semantic
   baselines, stdlib-only seals, production as SUT only, no receipt/runtime
   derivation, and named target-only mutation/inverse-repair controls.
8. Confirms exact visual 98/46/96 containment and same-WitnessV3 private
   `W -> M -> E -> V` composition remain mandatory.
9. Confirms production roots/public APIs stay inactive and coverage-first and
   that no candidate/review/replay/result/terminal or expected-output
   consumption is authorized.
10. Confirms the exact commands/counts, rejection triggers, hard prohibitions,
    and two-review sequence are deterministic and sufficient.
11. Records P0/P1 findings and recommends `accept` only with none open.

The expected architecture-review artifact is:

`kb_creator/docs/plans/20260809-innsmouth-page-level-consumer-proof/handoffs/terra_page_proof_packet_4b9_in_place_salvage_architecture_review_20260811.md`

Only after architecture acceptance may the main-chat orchestrator assign one
bounded executor. A different fresh Terra/high critic must then review the
implementation and evidence. Neither critic nor executor inherits
orchestration, and neither review is a release review.

## 12. Hard prohibitions

This packet authorizes no live Innsmouth PDF, no EN source, no KeeperBook, no
HTML, no PDF, no output or build path, no Git, no network, no browser, no
production activation, no public terminal/result, no candidate/reviewed
ledger, no replay terminal, no Step 5, no release path, and no partial rollback.
It authorizes no implementation until section 11 is independently accepted.

## 13. Evidence, blockers, and next action

- Files checked: `D:\NRI\AGENTS.md`; canonical NRI goal governance;
  `kb_creator/PROJECT_STATUS.md`; assigned new-chat handoff, `plan.md`,
  `context.md`, and contract status; the invalid 4b.9 executor receipt; the
  forensic baseline-recovery specification; the 4b.8 aggregate acceptance;
  the prior 4b.9 architecture review and inventory/reseal specification; the
  final 4b.6 and 4b.7 specifications/reviews; current `page_proof.py`; the
  seven current candidate tests; coverage/topology tests.
- Files changed: this immutable handoff only.
- Verification/evidence: read-only SHA-256 inspection established the exact
  `S0` and frozen hashes above. Read-only AST inspection found the current
  visual source still has `98` direct normalizer calls and `46` exact
  target-only tests; the seven current files contain zero old-surrogate
  occurrences. Fixed-literal inspection established the section 4.3 current
  leaf lengths/hashes without importing production helpers. A fixture-only
  `--collect-only` run from `D:\NRI` reported `147 tests collected in 0.22s`.
  An initial collection attempt from `D:\NRI\kb_creator` failed only because
  that directory is not the command's package root; it made no write and is
  superseded by the correct-root collection result. No implementation tests,
  public API, live/source/output/build, Git, network, production activation,
  terminal result, or release action was run.
- Blockers: none to independent architecture review. Implementation, all live
  or production paths, and acceptance remain blocked pending that review.
- Next action: the main-chat orchestrator assigns a fresh independent
  Terra/high architecture review using section 11. Do not assign implementation
  unless that review accepts with no P0/P1.
- Elapsed active time: approximately `32 minutes`.
- Token use: `unavailable` (not exposed to this contributor).
- Timestamp: `2026-08-11T21:27:20.1638066+03:00`.

This receipt is immutable. Any correction must be a new handoff that explicitly
supersedes this file. It does not edit canonical state, transfer orchestration
ownership, accept an implementation, or act as the final release reviewer.

# Sol handoff — Packet 4b.8 authoritative topology-acceptance identity closure

## Receipt identity and result

- Goal id: `20260809-innsmouth-page-level-consumer-proof`.
- Step id: `4b.8-specification`.
- Role/effort: Sol architect / requested `high`; actual platform model and
  effort: `platform-unverified`.
- Orchestrator policy owner: `gpt-5.5` at `medium`
  (`platform-unverified`). Orchestration ownership remains with the main chat.
- Assignment state: `platform-unverified`.
- Scoped override: `none`.
- Result: **specification complete** for exactly one minimal fixture-only P0/P1
  packet. No implementation, topology acceptance, production activation, live
  preflight, release decision, or canonical-state update is performed here.

## 1. Purpose and architectural decision

Packet `4b.8` must close the two missing authoritative Stage A
`fixture_topology_acceptance` identities and do nothing else.

This is the correct smallest next packet. No code, ledger, review/replay, or
adversarial-matrix prerequisite must precede it:

1. Packet `4b.7` is independently accepted and proves only private
   `P' -> W' -> M -> E -> V' -> F'` composition.
2. The current Stage A module and focused topology test still match the exact
   final nested-Form implementation-review hashes, so no repair or rebuild is
   required before an aggregate topology-acceptance review.
3. The two existing final topology reviews have `review_kind="implementation"`;
   the two-column receipt expressly says it is not topology acceptance, and the
   nested-Form receipt names aggregate topology acceptance as the next action.
4. The sibling topology plan says its aggregate acceptance step is completed,
   but no immutable receipt with
   `review_kind="fixture_topology_acceptance"` exists. A plan/status statement
   is not an acceptance identity under the accepted contract.
5. Candidate-ledger bytes, final fixture-admission output seals, aggregate
   review, and replay all ultimately bind
   `required_topology_inventory_content_sha256`. Building them against the
   private surrogate digest before the two real review-content hashes exist
   would require another identity migration and would not remove the public
   coverage blocker.

Therefore `4b.8` is an **evidence/value-supply packet**, not an implementation
or activation packet. It creates one immutable aggregate Terra receipt
containing two separately sealed per-topology acceptance records. It does not
populate either page-proof production registry. A later separately specified
packet may consume the two accepted record hashes.

## 2. Critical-path dependency and branch

```text
accepted Stage A two-column implementation
  + accepted Stage A nested-Form implementation
  + unchanged exact Stage A candidate
    -> Packet 4b.8 independent fixture_topology_acceptance records
      -> two authoritative review-content SHA-256 values
        -> later private final-inventory/reseal/ledger specification
          -> later review/replay and terminal work
```

Failure branch:

```text
any frozen hash/fact/test/independence mismatch
  -> one immutable 4b.8 reject/blocker receipt
  -> no accepted child record and no consumable review-content hash
  -> production coverage remains incomplete
```

No branch from this packet reaches a live PDF, source reconstruction,
publication artifacts, build, Git, production registry activation, Step `5`,
or release.

## 3. Frozen inputs and assumptions

The reviewer must stop before acceptance if any frozen identity differs.

### 3.1 Stage A candidate

| Input | Required SHA-256 |
| --- | --- |
| `kb_creator/pdf_raw/raw_authority_projection.py` | `3F7457D10518F3D2588633B47FC5F6E359224A04938C69DBA3B8AB89B241BB5A` |
| `kb_creator/tests/test_raw_authority_projection_stage_a_topology_authorities.py` | `35FB7651097AA552E5B5683C445CDAB62E9556CECC1C958B0D76B421D23BE1BC` |
| `test_raw_authority_projection_stage_a_adversarial.py` | `30401D844627938BB54BA800E241C1FBC8AB9FC408C569A546B636ABF6EA9E2A` |
| `test_raw_authority_projection_stage_a_boundaries.py` | `66E276DE1EF42024EF175E45688DD893DAED3676279D4646CFE09D367FAA3B47` |
| `test_raw_authority_projection_stage_a_containment.py` | `F069110043862C74AF074F246B6CBD82C3B76691B373E36EC7A715E10C9E036D` |
| `test_raw_authority_projection_stage_a_contract.py` | `18513D1707E658BA411ED8096D0E333A1C80EDE45FD7D0D96CB4CE9FE1459D88` |
| `test_raw_authority_projection_stage_a_replay.py` | `1710C74540A8571DEE89C66A43CB98421CF626F44098C2B3E58FCFC3374FD3AA` |

### 3.2 Accepted contracts and prior evidence

| Input | Required SHA-256 |
| --- | --- |
| Stage A topology specification | `23ECCF5ED32998D55EB0DBBCF73B2987FFA4D14DC0BEDD40361B7DE274EAB630` |
| Stage A architecture acceptance | `97E82053214A0F2AAC9063A5D29D40CF606C93255E6A8B798FB7434770025596` |
| two-column final implementation re-review | `FA24DA4B0E2311DF7C3914E7744F33330A30A4A8B50D9259C99C2DFF5EA6F271` |
| nested-Form final implementation re-review | `89E91EFE69994A95EFE86A9F4180DADDB1F60519FF1FB0C52435358B984B44B8` |
| Sol Packet 4b.7 specification | `7594DFFB88C9F9F1779443729EB1E636574C74EB1F56B2D17586A5A0E5B32176` |
| final 4b.7 implementation review | `19683FCEA2111624EAB350447F33B400ADC97BE9A643AB2E89337267B251B300` |
| final 4b.7 review correction | `2BB9B1D4DEFDC97AB2E945362D2B3808F7382BC8A2822D5C8F43BC512936B19D` |

The page-proof implementation is read-only and frozen at
`269E244F15445DF8EE81D3FFF33297705197F1BDCD703369C1342A49698114C2`.
Its four production roots must remain inactive exactly as accepted in `4b.7`.

Assumptions:

1. The current Stage A hashes above are the candidate to be accepted; no
   nearest-version or regenerated substitute is allowed.
2. Existing `implementation` receipts are evidence inputs, not values that may
   be relabelled, rehashed, or inserted into the page-proof inventory.
3. The private page-proof topology digest
   `d0891ce46fc9cb3aeee366cf78610996b3e2a34e94d85c47e9d212599a438ac6`
   remains a non-authoritative test surrogate.
4. P2/P3 observations remain debt-only. They do not weaken P0/P1 acceptance or
   expand this packet.

## 4. Allowed and disallowed scope

### Allowed

- Read only the frozen inputs above, governance, assigned plan/context/status,
  and the accepted Stage A topology specification.
- Discover and record the exact Python executable/version.
- Run only the deterministic fixture-only commands in section 7 with `-B` and
  `-p no:cacheprovider`.
- Perform read-only SHA-256, canonical-JSON, AST/import, literal-registry, and
  in-memory fixture replay inspection.
- Write exactly one new immutable aggregate Terra critic receipt at:
  `kb_creator/docs/plans/20260809-stage-a-page-proof-topology-authorities/handoffs/terra_stage_a_fixture_topology_acceptance_20260811.md`.
  On acceptance it contains both child records from section 5. On rejection it
  contains no accepted child record and no consumable review-content hash.

### Disallowed

- Any edit to code, tests, fixture leaves, prior receipts, plans, context,
  project/contract status, debt, release, configuration, or generated output.
- Any edit or monkeypatch of `_FIXTURES`, `_EXPECTED_FIXTURE_PAIR`, either
  page-proof production topology root, or either production fixture-admission
  root.
- Any use of the existing implementation-receipt file hash as an acceptance
  record hash; any self-review, alias, placeholder, zero hash, same-record
  substitution, or mutable/generated expected row.
- Any live PDF/path, Innsmouth source, EN/RU/Keeper/HTML/PDF/output read or
  processing; filesystem fixture loading; browser, network, OCR, alternate PDF
  parser, source reconstruction, environment/config selector, plugin/dynamic
  import, subprocess, build, Git, production activation, Step `5`, or release.

## 5. Exact data/contract change

There is **no code or test contract change**. The only new authoritative data
is two distinct canonical child records in the one aggregate receipt.

Each child is closed canonical JSON with schema
`kb_creator.pdf_raw.StageAFixtureTopologyAcceptanceV1` and exactly these root
keys, in semantic order (serialization remains sorted-key compact UTF-8):

```text
schema
goal_id
topology_id
stage_a_fixture_id
review_kind
decision
reviewer_role
reviewer_identity
assignment_state
implemented_candidate
materially_designed_candidate
source_use
stage_a_module_sha256
stage_a_topology_test_sha256
stage_a_authority_schema
stage_a_authority_terminal_state
stage_a_authority_content_sha256
stage_a_authority_inventory_sha256
stage_a_fixture_binding_sha256
positive_topology_assertion_raw_sha256
positive_topology_assertion_raw_byte_length
positive_topology_assertion_sha256
positive_topology_assertion_content_sha256
reviewed_authority_content_sha256
stage_a_claim_boundary
verification
reviewed_at
content_sha256
```

Fixed values common to both children:

```text
goal_id = "20260809-stage-a-page-proof-topology-authorities"
review_kind = "fixture_topology_acceptance"
decision = "accept"
reviewer_role = "independent_terra_critic"
implemented_candidate = false
materially_designed_candidate = false
source_use = "forbidden"
stage_a_module_sha256 = "3f7457d10518f3d2588633b47fc5f6e359224a04938c69dba3b8ab89b241bb5a"
stage_a_topology_test_sha256 = "35fb7651097aa552e5b5683c445cdab62e9556cecc1c958b0d76b421d23be1bc"
stage_a_authority_schema = "kb_creator.pdf_raw.RawAtomProvenanceAuthority.v1"
stage_a_authority_terminal_state = "provenance_complete_no_consumer"
stage_a_claim_boundary = {
  "geometry":"not_proved_stage_a",
  "reading_order":"not_proved_stage_a",
  "semantic_blocks":"not_proved_stage_a",
  "visibility":"not_proved_stage_a"
}
```

Exact topology values:

| Field | two-column | nested Form |
| --- | --- | --- |
| `topology_id` | `stage_a_positive_two_column.v1` | `stage_a_positive_nested_form.v1` |
| `stage_a_fixture_id` | `stage-a.positive-two-column.v1` | `stage-a.positive-nested-form.v1` |
| authority content | `890a9cef3ce995e7cb7881c035baa3e1e5a4c782f1827847b640c93fb28eafef` | `8726e5d36b7acba9d96eacdcd62a57da00d7f4cfdd4df79cd6c63106d2e353e7` |
| authority inventory | `3173d033fcf6228687388f020f0e5e6e7e9c1ce2a373bc1b2bca49823ab951c0` | `f296a28a72e509f47fe294217492cc463375c30144f8deab57fd7b4c85678b21` |
| fixture binding | `c41ec7ae9eea7d5fc2f654eb825bf1bb1af954d00c754fd6140f134985af8880` | `9b0f9f382e7926e3447072fa9340c38dd93531302e4294a14d8436eeacdf1d0a` |
| assertion raw SHA-256 | `5f81d370d69d6976fd0dcb5ab0e1b08ce3f1b73fe3830b9350b9f4a385561420` | `1feafef11d915c54b976199f17cb2ba65560d4183994fbf3ccf7c7c50a3c8612` |
| assertion raw length | `3691` | `8958` |
| assertion facts SHA-256 | `e681b6ffbed2705283b915039e1d7a6ac145f4988765fd772a68eb63803831c8` | `a82adc738fd89394e80a607df46f7775a1967f874267f3b0289e7e64829d3d0f` |
| assertion content SHA-256 | `841240303b22329d2c1f29a107a130b1a8c057f667b612d8a21abe1cb9071748` | `55be622dda946e5ea37ab144534d88c8739a4e604c4cfe21d1d24ad96d83a853` |

For each child,
`reviewed_authority_content_sha256 == stage_a_authority_content_sha256`.
`verification` is a closed object containing the exact two commands from
section 7, their exact result strings, and the six frozen test hashes.
`reviewed_at` is an RFC 3339 timestamp with offset. Reviewer identity must be a
non-empty stable label; assignment state must be the actually supportable value.

For each child:

```text
content_sha256 = sha256(
  canonical_json(child excluding content_sha256)
)
```

The aggregate receipt must print both complete canonical child byte strings and
their independently recomputed lower-case content hashes. The two child hashes
must differ. Those two child hashes, not the Markdown file hash and not either
prior implementation receipt hash, are the only Packet `4b.8` outputs that a
later page-proof inventory packet may consume as
`independent_stage_a_review_content_sha256`.

This packet does not compute or install the final page-proof topology inventory
root/content hashes, entry hashes, production rows, P/W/V/F reseals, candidate
bytes, or reviewed-ledger bytes.

## 6. Fail-closed behavior

- Any frozen hash drift, test failure/count drift, noncanonical child JSON,
  duplicate/unknown/missing/mistyped field, hash mismatch, reviewer-independence
  failure, topology fact mismatch, claim-boundary expansion, or one-topology-only
  success makes the aggregate decision `reject`.
- A rejected receipt must not contain `decision="accept"` in either child and
  must not publish a child `content_sha256` as consumable authority.
- Both child records are atomic for Packet `4b.8`; one accepted topology does
  not advance page-proof coverage.
- The reviewer must not repair, regenerate, or reseal the candidate. Drift is a
  blocker for a separately specified Stage A remediation, not permission to
  alter this packet.
- After successful acceptance, all page-proof public APIs must still fail first
  with `page_proof_stage_a_fixture_coverage_incomplete`; the receipt alone is
  data supply, not registry activation.

## 7. Deterministic verification and Definition of Done

The reviewer first confirms the interpreter and all frozen hashes, then runs
exactly:

```powershell
& '<confirmed Python>' -B -m pytest -q -p no:cacheprovider `
  kb_creator/tests/test_raw_authority_projection_stage_a_topology_authorities.py
```

Required result: exactly `15 passed`.

```powershell
& '<confirmed Python>' -B -m pytest -q -p no:cacheprovider `
  kb_creator/tests/test_raw_authority_projection_stage_a_contract.py `
  kb_creator/tests/test_raw_authority_projection_stage_a_replay.py `
  kb_creator/tests/test_raw_authority_projection_stage_a_boundaries.py `
  kb_creator/tests/test_raw_authority_projection_stage_a_containment.py `
  kb_creator/tests/test_raw_authority_projection_stage_a_adversarial.py `
  kb_creator/tests/test_raw_authority_projection_stage_a_topology_authorities.py
```

Required result: exactly `386 passed, 1 skipped`; the existing skip must be
identified and confirmed unchanged/justified.

Packet `4b.8` is done only when all are true:

1. All frozen hashes match before and after verification.
2. `_FIXTURES` and `_EXPECTED_FIXTURE_PAIR` remain separate literal four-row
   authorities and match exactly, including both topology rows.
3. Two-column evidence proves two distinct non-empty two-atom candidate slots
   and exact `B -> C` paint transition without geometry/reading-order claims.
4. Nested-Form evidence proves root/Outer/Inner frames, two exact invocation
   joins, event order `P,OuterDo,C,InnerDo,N,D,Q`, glyph order `P,C,N,D,Q`, and
   no accepted CTM/geometry/visibility/semantics/reading-order claim.
5. Target-only fully resealed mismatch and inverse-repair evidence reaches the
   named topology predicates rather than stale outer seals.
6. Containment proves literal bytes/in-memory parser only and no page-proof,
   source, output, filesystem, network, environment, plugin, or build edge.
7. Both canonical child records recompute, have distinct content hashes, and
   bind their own exact authority content hash.
8. The aggregate receipt reports no open P0/P1 and contains all governance
   receipt fields. P2/P3 are debt-only.
9. No file other than the one immutable Terra receipt was changed.

Passing tests without the two valid child records is not acceptance.

## 8. Independent-review checklist

The fresh Terra critic must independently answer yes to every item:

- Did the critic neither implement nor materially design either topology?
- Do all section 3 hashes match, including the current Stage A candidate and
  the final implementation reviews?
- Are the prior reviews used only as evidence and never relabelled as topology
  acceptance?
- Does each child use the exact `fixture_topology_acceptance` kind, `accept`
  decision, topology/fixture pair, authority hashes, assertion hashes/length,
  reviewed-authority equality, and non-promotion boundary?
- Are two-column slots described only as raw paint candidates, never geometric
  columns or accepted reading order?
- Does nested Form retain exact hierarchy/invocation/paint/glyph ownership and
  exclude effective CTM and all page-proof semantics?
- Do target-only negatives validate all non-target seals, and does inverse
  repair pass exact replay?
- Are the focused and six-suite result counts exact and the skip justified?
- Are both child JSON roots canonical, closed, independently rehashed, and
  distinct?
- Are the page-proof production roots still inactive and public APIs still
  coverage-first/no-result without executing those APIs on caller data?
- Was the only write the immutable aggregate receipt, with no Git or live path?

Any `no` is P1 and requires `reject`. This is fixture topology acceptance, not
a final release review.

## 9. Risks and controls

| Risk | P0/P1 control |
| --- | --- |
| Canonical plan falsely substitutes for missing evidence | Require the actual closed child records and recomputed hashes; status text is non-authoritative. |
| Implementation receipt is silently relabelled | New fresh critic records only; prior receipt/file hashes are forbidden as outputs. |
| One aggregate hash is reused for both entries | Two topology-specific canonical child records with distinct content hashes. |
| Candidate drift is repaired during review | Stop and reject; no source/test mutation is allowed. |
| Stage A paint facts are promoted to geometry/reading order | Exact four-field `not_proved_stage_a` boundary and topology-specific semantic checks. |
| Receipt is mistaken for production activation | Production roots stay inactive; no page-proof file/test changes or public execution success. |
| Candidate ledger is built on the private surrogate digest | Ledger/reseal/review work remains forbidden until a later specification consumes both authoritative child hashes. |
| P2/P3 debt delays or broadens the critical path | Record as debt only; acceptance is no-open-P0/P1. |

## 10. Next owner and completion boundary

Next owner: one fresh independent **Terra critic at high effort** who did not
implement or materially design the Stage A topology candidate. The critic
executes sections 3–8 and writes only the one aggregate immutable receipt.
There is no engineering owner in this packet because candidate mutation is
forbidden.

After a successful receipt, the main-chat orchestrator may integrate the two
child hashes into canonical state and request a new Sol specification for the
next bounded fixture-only packet: private final-authority inventory
materialization and dependent P/W/V/F/candidate-ledger resealing. This receipt
does not itself authorize that work, production activation, review/replay
terminals, full adversarial containment, Step `5`, or release.

## 11. Handoff accounting

- Scope: architecture/root-cause analysis and exact specification for one
  fixture-only Packet `4b.8`; no implementation or acceptance.
- Files checked: root `AGENTS.md`; canonical NRI goal governance; assigned
  page-proof plan/context/contract status; original page-proof contract and P1
  correction; packetization; all architecture/executor/critic receipts for
  `4b.1`–`4b.7`, especially final `4b.7` acceptance and correction; sibling
  Stage A topology plan/context/specification and both final implementation
  reviews; current `page_proof.py`, `raw_authority_projection.py`, fixture
  leaves, composition test, and Stage A topology test set.
- Files changed: this immutable handoff only.
- Verification/evidence: read-only dependency, schema, source, receipt, and
  SHA-256 inspection. Current Stage A module/test hashes exactly match the final
  accepted nested-Form candidate. No test, live PDF, browser, network, build,
  output, Git, production activation, or implementation action was run.
- Blockers: none to executing the bounded independent acceptance packet. The
  missing two authoritative child hashes remain the blocker until that packet
  succeeds.
- Next action: main-chat orchestrator assigns section 10; do not assign an
  executor or begin candidate-ledger/activation work from this specification.
- Elapsed active time: `457 seconds` at final accounting capture.
- Token use: `199,724` tokens at final accounting capture.
- Timestamp: `2026-08-11T17:25:37.0059300+03:00`.

This receipt is immutable. A correction must use a new handoff and explicitly
supersede this file. It does not transfer orchestration ownership and is not a
final release review.

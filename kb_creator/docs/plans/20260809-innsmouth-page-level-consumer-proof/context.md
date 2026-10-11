# Context: Innsmouth Page-Level Consumer/Proof

## Current Checkpoint

The accepted raw-PDF Stage A authority is fixture-only. Independent Terra
acceptance is recorded in:

`../20260808-innsmouth-systemic-todo-execution/handoffs/terra_raw_authority_projection_stage_a_p1_faithful_topology_final_review_20260809.md`

It proves raw-byte provenance/text-order authority inside sealed fixtures only:
`1057 passed, 1 justified skipped`. It does not authorize a live Innsmouth PDF,
EN reconstruction, source mutation, Keeper/HTML/PDF rebuild, or release.

## Why This Exists

The Innsmouth TODO contains page-order, column-order, paragraph-boundary,
heading/body, list/body, table/body and art-anchor failures. They cannot be
closed honestly until the pipeline can demonstrate which visible page blocks
exist, in which reading order, and whether their text layer is publishable.

## Active Step

Packet `4b.9` is independently accepted only as an in-place fixture-only
salvage. The byte-exact frozen baseline was not restored because the required
historical `tests/_page_proof_fixture_leaves.py` bytes were unavailable; the
seven affected test files were instead treated as new unaccepted `S0` bytes and
re-proved through a fresh Sol/high specification, Sol hash-preimage
clarification, independent Terra/high architecture re-review, bounded
orchestrator implementation takeover, and independent Terra/high
implementation re-review.

The active next boundary is Step 5, but it is not yet authorized. It must be a
separate read-only live page preflight packet with its own specification,
evidence, and independent review before any live PDF/source/output/build path
can be touched.

Current continuation authorizes only the Step 5 architecture gate: Sol/high may
write a read-only live preflight specification and Terra/high may review it.
No live PDF/source/output/build path may be read or processed until that
architecture is independently accepted and a separate bounded executor packet
is assigned.

Sol wrote
`handoffs/sol_page_proof_step5_read_only_live_preflight_spec_20260811.md`
(SHA-256 `12DF1D960B94FA573FD98558CC744A9D36C4BB82CD9791C12B1623F31310F8E9`).
Independent Terra reviewed it in
`handoffs/terra_page_proof_step5_read_only_live_preflight_architecture_review_20260811.md`
(SHA-256 `5D9716CD3BC2F144C9E71FB9E34E19439F67A84AA2AF7DF906225AB44BACE4D5`).
Result: remediation required. P0/P2: none. P1: closed control-record sandbox
authority is underspecified; prerequisite-QA evidence is not bound into the
authorization; deterministic selected-page queue identity is not independently
replayable. Sol's declared blockers for a live adapter and render/no-render
conflict remain valid but are insufficient for acceptance.

Sol clarified the three P1 gaps in
`handoffs/sol_page_proof_step5_read_only_live_preflight_p1_clarification_20260811.md`
(SHA-256 `2AD0E5FB0437C99E0BC2300EB93C1F9CF85EA76E432B84CEDCEC7C9686BFC33A`).
Fresh independent Terra accepted the combined base specification and
clarification in
`handoffs/terra_page_proof_step5_read_only_live_preflight_architecture_rereview_20260811.md`
(SHA-256 `5BD2934B94D17573CB160ED9647C1BC79EA64C3199ADEE930036A6144403B67E`),
with no P0/P1/P2.

Step 5 architecture is accepted only as architecture. It authorizes at most a
separately specified and independently reviewed non-live adapter packet or a
narrow blocker-remediation/contract packet. It does not authorize adapter
implementation by default, Step 5A identity capture, Step 5B live preflight,
renderer-branch selection, source/output/build/Git/release, production
activation, public terminal result, or any live read.

## Checkpoint: 4b.9 In-Place Salvage Architecture Review Requires Remediation — 2026-08-11

Fresh independent Terra reviewed the Sol in-place salvage contract in
`handoffs/terra_page_proof_packet_4b9_in_place_salvage_architecture_review_20260811.md`
(SHA-256 `0E277BD1792ACF1990A88D7EC64F527C8F6A0F12E77EB7861F01A31FF7663359`).
It found no P0 but rejected architecture acceptance on one P1: the private
inventory/root seal preimage is underspecified, so an independent oracle cannot
reproduce the root seals solely from the contract.

The next permitted action is a bounded Sol/high clarification that supplies
the exact canonical hash payloads/preimages without changing the no-live,
no-production, no-public-result, no-Git, no-output/build, no-release, and
no-partial-rollback boundaries. A fresh independent Terra/high architecture
re-review is required before any executor assignment.

Sol supplied the bounded clarification in
`handoffs/sol_page_proof_packet_4b9_in_place_salvage_hash_preimage_clarification_20260811.md`
(SHA-256 `73301C3BFF32C5E2EAECE88C7D81F811795A32C1EBBD582F605B429660955C5F`).
It states the exact canonical JSON settings, inventory domain/NUL preimage,
and closed-root content preimage for the accepted inventory/root hashes.
Fresh independent Terra/high architecture re-review is now active.

Fresh independent Terra accepted the combined Sol specification and
clarification in
`handoffs/terra_page_proof_packet_4b9_in_place_salvage_hash_preimage_architecture_rereview_20260811.md`
(SHA-256 `873BF17D2E14A4659046ECBE6B9FA7FA63B018895030B5312220233166A10409`),
with no P0/P1/P2. The prior P1 is closed. The active step is now exactly one
bounded fixture-only implementation under the accepted write set, followed by
a different fresh independent Terra/high implementation review. This still
does not accept `4b.9` and does not open live/source/output/build/Git,
production, public-result, Step 5, release, or partial-rollback paths.

The first bounded executor read the packet but stopped before hash
precondition verification, implementation, tests, or receipt due to executor
budget. It made no edits. Recovery remains the same narrow implementation
packet: first verify `S0`, read-only hashes, absent new oracle file, and Python
path/version; then either implement the accepted oracle and receipt or write
the required blocker receipt.

A second bounded executor restart also stopped before the first mandatory
precondition verification and made no edits or receipt. Under the NRI recovery
rule, the orchestrator may take over the same narrow implementation packet
without expanding scope. The takeover starts at the exact precondition gate:
verify `S0`, read-only hashes, absent new oracle file, and Python path/version;
then either implement the accepted oracle and receipt or write the required
blocker receipt.

The orchestrator takeover candidate is recorded in
`handoffs/executor_page_proof_packet_4b9_in_place_salvage_20260811.md`
(SHA-256 `BE55C5E2292804D6767E437B5A6EBA8A09F6A32DE32338DCCAB582F23C51B09C`).
It added the independent 12-test oracle and made one target-only repair in
`tests/test_page_proof_closed_schemas.py` so the private active-topology helper
uses the two accepted `4b.8` child identities instead of old placeholder
surrogate hashes. `page_proof.py` stayed unchanged at
`269E244F15445DF8EE81D3FFF33297705197F1BDCD703369C1342A49698114C2`.

Verification from `D:\NRI` with `D:\NRI\.tools\python-3.13.14\python.exe`
(`Python 3.13.14`): `py_compile` passed; page-proof collect-only reported
`159 tests collected`; page-proof execution reported `159 passed in 0.74s`;
Stage A checks reported `15 passed in 0.31s` and
`386 passed, 1 skipped in 10.89s`. This is still not `4b.9` acceptance:
fresh independent Terra/high implementation review is active next.

Independent Terra implementation review rejected this candidate in
`handoffs/terra_page_proof_packet_4b9_in_place_salvage_implementation_review_20260811.md`
(SHA-256 `8E4792CE4240E8D9E85168899F0081F6F631978C5E8E6F545AE61FE05202B591`).
P0/P2: none. P1: the new oracle was not literal-only/fixed-path enough for
visual containment because it inspected/imported `visual_tests` at runtime and
did not directly prove exact `98/46/96` plus the 46 literal target names and 96
pre-normalizer contracts. The permitted remediation is oracle-only within the
accepted fixture write set, followed by a fresh independent Terra/high
implementation review.

Oracle-only remediation is now recorded in
`handoffs/executor_page_proof_packet_4b9_in_place_salvage_20260811.md`
(updated SHA-256 `8C47F7085FF00C89AECE7DDA0F1E9916E89D5F7B352D266CD9EDE4355CCA5CDE`).
The new oracle file now has SHA-256
`627BD77326E39F2EB06B8CC83F0496B3BD5B0646A6496AB1B7E23B50F17C5502`.
Verification remains exact: `py_compile` passed, oracle-only `12 passed`,
page-proof collect-only `159 tests collected`, page-proof execution
`159 passed in 0.62s`, Stage A `15 passed in 0.28s`, and Stage A aggregate
`386 passed, 1 skipped in 9.82s`. The latest oracle-only repair maps the fixed
AST actual target set to the literal 46-name tuple and maps every positive and
target visual-normalizer call to its immediately preceding pre-normalizer
contract. Fresh independent Terra/high implementation
re-review is required before `4b.9` acceptance.

Fresh independent Terra/high second implementation re-review accepted the
oracle-only remediation in
`handoffs/terra_page_proof_packet_4b9_in_place_salvage_implementation_rereview_2_20260811.md`
(SHA-256 `26A776FF76E56C63B320999B09813D9255E00EAF944659F0301BD8026F1F12D8`),
with no P0/P1/P2. The accepted fixture-only evidence is: `py_compile` passed,
oracle-only `12 passed`, page-proof collect-only `159 tests collected`,
page-proof execution `159 passed`, Stage A topology authorities `15 passed`,
and Stage A aggregate `386 passed, 1 skipped`.

This accepts Packet `4b.9` only as fixture-only private inventory reseal
evidence. It does not open live Innsmouth PDF/source, KeeperBook, HTML, PDF,
output/build, Git, production activation, public terminal result, Step 5, or
release paths.

## Sol Specification Received

Sol delivered `handoffs/sol_page_level_consumer_proof_spec_20260809.md`,
SHA-256 `44EF02B7BDFBA240733BBEDF6F4018313C32F6E312E48CAAEAFCE7FFC2E6DD24`.
It proposes a two-authority join: sealed Stage A provenance/text-order evidence
plus a separately sealed fixture geometry/visibility witness. It also requires
an explicit reviewed reading-order permutation and a complete paragraph-boundary
adjacency chain, while preserving occluded/text-layer-only/decorative content
as non-publication evidence.

This is a proposal only. Independent Terra architecture review is in progress;
no fixture implementation, live preflight, EN change or rebuild is authorized.

## Terra Architecture Review: Remediation Required

Independent Terra rejected the first specification with three P1 contract gaps,
recorded in `handoffs/terra_page_level_consumer_proof_architecture_review_20260809.md`:

1. the closed block schema lacks a mechanically defined `in_reading_flow`
   disposition and therefore cannot determine the exact adjacency universe;
2. the required positive topology coverage (two columns and nested Form) does
   not yet fail closed before any public accepted-proof terminal state; and
3. the visual witness has no replayable, per-block/per-boundary independent
   visual cross-check bound to the decision-specific evidence.

The only authorized next action is a Sol specification correction for these
three issues, followed by a fresh independent Terra review. Implementation,
live preflight, source mutation and artifact rebuild remain prohibited.

## Sol P1 Correction Received

Sol delivered `handoffs/sol_page_level_consumer_proof_p1_correction_20260809.md`,
SHA-256 `5DC8DE4E51D653572C59FC8EBC62184725C5D7DB9FD3577CFFB2203FADAA131E`.
The amendment introduces a total reading-flow derivation and exact adjacency
universe; requires all three public proof operations to fail before witness
decoding until literal accepted two-column and nested-Form topologies exist;
and adds a replayable per-block/per-boundary independent visual cross-check
leaf. The original specification remains unchanged.

Independent Terra re-review is active. No implementation or live action is
authorized pending that review.

## Architecture Accepted; Coverage Guard Only

Terra accepted the corrected architecture in
`handoffs/terra_page_level_consumer_proof_p1_architecture_rereview_20260809.md`.
The only presently authorized code task is a fixture-only public coverage guard:
because no separately accepted Stage A two-column/nested-Form authority entries
exist, every public derive/review/replay API must stop with
`page_proof_stage_a_fixture_coverage_incomplete` before it decodes or accesses
any supplied witness, image, review, ledger, or authority.

This guard is not a proof implementation and cannot create a candidate or
accepted terminal state. Creating Stage A topology fixtures and implementing
the actual ledger are later, independently reviewed steps. Live inputs and all
publication artifacts remain frozen.

## Coverage Guard Implemented; Independent Review Pending

The fixture-only public guard is present in `kb_creator/pdf_raw/page_proof.py`
with tests in `kb_creator/tests/test_page_proof_coverage_guard.py`. A local
focused verification passed `13 passed in 0.03s`. All three public APIs reject
with `page_proof_stage_a_fixture_coverage_incomplete` before they touch any
caller-supplied object or byte payload.

This is implementation evidence, not acceptance. Terra must independently
verify that the guard is a valid non-bypassable precursor to a future literal
topology inventory, rather than a permanent error-only stub. No new authority,
live preflight, source mutation or rebuild is authorized while that review is
pending.

## Coverage Guard Review: Remediation Required

Terra confirmed that the guard fails before argument access for the signatures
it implements, but rejected it because the accepted P1 architecture added the
mandatory `independent_visual_crosscheck_raw` leaf to all three public APIs.
The module and tests still use pre-correction signatures, so they cannot prove
coverage failure precedes access to every normative input.

The single authorized remediation is to restore the corrected signatures in
the exact positions and extend poison-input tests. No inventory, ledger,
visual mechanism, live input, source mutation or rebuild is permitted.

## Corrected Guard Submitted For Re-review

The engineer restored `independent_visual_crosscheck_raw` in all three
normative public signatures and added exact-signature plus poison-input coverage
for every parameter. Local focused verification is `14 passed in 0.04s`.

Independent implementation re-review is active. The module remains an honest
temporary no-proof guard because the required two-column/nested-Form authority
inventory is still absent.

## Coverage Guard Accepted

Independent Terra accepted the corrected guard in
`handoffs/terra_page_proof_coverage_guard_signature_rereview_20260809.md`.
The focused fixture-only suite passed `14 passed`. The accepted state proves
only that public APIs refuse every supplied input before inspection while
topology authority is incomplete.

The next dependency is a separate Stage A fixture-authority bundle for
two-column and nested-Form positive topologies. The guard itself is not a proof
of those topologies and not permission for live use, source repair or rebuild.

## Completion Condition For This Bundle's Design Phase

An independent Terra architecture review accepts a contract that:

1. consumes only fixture input at implementation time;
2. yields a replayable page/block evidence ledger rather than reconstructed
   prose;
3. distinguishes visible, occluded, decorative and text-layer-only content;
4. requires explicit page-level reading-order acceptance before source use;
5. fails closed on missing geometry, source identity, mapping, or review;
6. defines a later, separately authorized, read-only live-page preflight.

Until then, all Innsmouth source and publication artifacts remain frozen.

## Packet 4b.1 Accepted: Literal Inventory Validator

Packet `4b.1` is independently accepted as a fixture-only safety checkpoint.
`pdf_raw/page_proof.py` now owns a closed required-topology inventory validator;
the production root intentionally contains no entries because the two exact
independent `fixture_topology_acceptance` review-content hashes do not exist in
the evidence set. Therefore all three public APIs still reject with
`page_proof_stage_a_fixture_coverage_incomplete` before they inspect caller
inputs.

The first implementation review found an incorrect empty-root `content_sha256`.
The bounded remediation corrected the literal and added an independent seal
regression. Terra re-review accepted it with no P0/P1/P2; focused fixture-only
evidence is `35 passed`. Receipts:

- `handoffs/terra_engineer_page_proof_topology_inventory_20260809.md`;
- `handoffs/terra_engineer_page_proof_topology_inventory_remediation_20260809.md`;
- `handoffs/terra_page_proof_topology_inventory_remediation_review_20260809.md`.

This does not admit a fixture, produce a ledger, inspect a source PDF, or
authorize an Innsmouth rebuild. The next bounded action is Packet `4b.2`:
private fixture-admission foundation only.

## Packet 4b.2 Submitted For Independent Review

Two bounded `gpt-5.4` attempts exhausted their platform budget before any
implementation evidence. The orchestrator therefore took over the same narrow
packet under the documented recovery rule. The result adds only private,
literal test leaves and a deterministic fixture-admission row validator.
Production admission is still empty and all public APIs still fail at coverage
before caller-value access. Focused fixture-only evidence: `37 passed`.

Independent Terra review is required before the next packet. Receipt:
`handoffs/orchestrator_page_proof_fixture_admission_takeover_20260809.md`.

## Pause Checkpoint — 2026-08-09

Packet `4b.2` was independently rejected once for a P1: the test-side registry
was not independent because key metadata was generated dynamically. Sol then
specified the narrow correction in
`handoffs/sol_page_proof_fixture_admission_p1_remediation_spec_20260809.md`.

Bounded executor Packet `4b.2-r` is now complete, with receipt
`handoffs/executor_page_proof_fixture_admission_remediation_20260809.md`:

- code/test scope: `pdf_raw/page_proof.py`, fixture leaves, fixture-admission
  tests only;
- focused evidence: `41 passed in 0.10s`;
- production topology and fixture-admission roots remain intentionally empty;
- all public APIs still fail coverage-first before caller input access.

This is not acceptance. The bundle is paused before fresh independent Terra
implementation review. The only allowed first action on resume is that review;
`4b.3`, live preflight, Innsmouth source work and any artifact rebuild remain
prohibited.

## Resume Checkpoint — 2026-08-11

Independent Terra re-review accepted Packet `4b.2-r` with no P0/P1/P2 in
`handoffs/terra_page_proof_fixture_admission_remediation_review_20260811.md`.
The mandated fixture-only suite passed `41 passed in 0.25s`.

The accepted result is deliberately narrow: private literal fixture-admission
validation only. Production topology and admission roots remain empty, and all
public APIs still reject coverage-first before caller input access. This does
not permit a live PDF, source reconstruction, EN/RU/Keeper/HTML/PDF mutation,
artifact rebuild, Git action or release decision.

The next active packet is `4b.3`: closed canonical schemas and public-boundary
capability wrappers only. It must not decode PNG, derive geometry, create a
proof-like object or activate any terminal state.

## Packet 4b.3 Accepted — 2026-08-11

Independent Terra accepted `4b.3` in
`handoffs/terra_page_proof_closed_schemas_review_20260811.md`. The focused
fixture-only suite passed `50` tests. It found no technical P0/P1; a disclosed
pre-reminder web-search attempt by the executor is recorded as P2 process
deviation. Terra found it unused as implementation/evidence and did not require
technical remediation, but this packet must not be described as network-free.

The next active packet is `4b.4`: pure literal witness/render/component replay
and deterministic PNG mechanics. It remains fixture-only and must not invoke a
PDF renderer, open a path, call `page_capable`, derive flow, accept visual
review, create a proof terminal, or reach live Innsmouth inputs.

## Packet 4b.4 Rejected; Narrow Remediation Required — 2026-08-11

The first `4b.4` implementation passed its assigned focused fixture suite
(`55 passed in 0.15s`) but was independently rejected by Terra in
`handoffs/terra_page_proof_witness_render_components_review_20260811.md`.
The rejection is technical, not a live-input or release decision:

1. the canonical-decimal validator rejects valid fractional values such as
   `0.5`; and
2. the PNG/zlib decoder accepts trailing data after `IEND` or the final
   deflate block.

Executor-local path/computation deviations are recorded as P2 in the review
receipt and are not the rejection basis. The only permitted next action is a
restart of this same narrow fixture-only packet to fix both P1s and add
adversarial tests. No live PDF, source reconstruction, EN/RU/Keeper/HTML/PDF
mutation, rebuild, Git action, or release is authorized.

## Packet 4b.4 Remediation Accepted — 2026-08-11

Independent Terra accepted the narrow remediation in
`handoffs/terra_page_proof_witness_render_components_remediation_review_20260811.md`.
The mandated fixture-only suite passed `56` tests. The accepted changes correct
canonical fractional decimal validation and reject trailing bytes after PNG
`IEND` and terminal zlib/deflate data. Accepted positive leaves remain literal
bytes; production coverage/admission roots remain empty and public proof APIs
remain coverage-first.

The review retains only the historical P2 process disclosure from the original
candidate; it found no new deviation. The next packet is `4b.5`, flow and
adjacency mechanics only. It is not permission to access a live PDF, alter
source/artifacts, rebuild, run Git, or make a release decision.

## Packet 4b.5 Rejected; Narrow Remediation Required — 2026-08-11

Terra rejected the first `4b.5` flow/adjacency candidate in
`handoffs/terra_page_proof_flow_adjacency_review_20260811.md`, notwithstanding
the focused `65 passed` result. Mandatory evidence has two P1 gaps: the test
matrix covers only five cumulative flag cases instead of all sixteen
combinations, and the positive/repair adjacency baseline is calculated by a
test helper that mirrors the SUT. The only authorized next action is the same
fixture-only packet remediated with a literal full precedence table and an
independent literal adjacency/boundary baseline. Live inputs and publication
work remain prohibited.

## Packet 4b.5 Remediation Accepted — 2026-08-11

Independent Terra accepted the narrowly remediated flow/adjacency packet in
`handoffs/terra_page_proof_flow_adjacency_remediation_review_20260811.md`.
The prior P1 evidence gaps are closed without changing `page_proof.py`:

- the test oracle is a literal table for all sixteen combinations of
  `visual_only`, `text_layer_disagreement`, `occlusion`, and
  `running_marginal`;
- positive and repair assertions use separately declared literal fragment and
  boundary sequences, rather than an adjacency helper derived from SUT inputs;
- target-only mutation/reseal returns to that independent baseline.

The mandated fixture-only suite passed `77` tests. This acceptance advances
only the fixture proof route to packet `4b.6`; it does not permit a live PDF,
source reconstruction, EN/RU/Keeper/HTML/PDF mutation, rebuild, Git action or
release decision.

## Packet 4b.6 Rejected; Narrow Test-Evidence Remediation Required — 2026-08-11

Terra rejected the first independent visual cross-check candidate in
`handoffs/terra_page_proof_visual_crosscheck_review_20260811.md`, despite the
mandated suite reporting `82 passed`. The P1 is precise: every mutated
cross-check is paired with its original admission row, so the private
normalizer fails at the stale outer leaf-SHA gate before it reaches the
intended internal pixel, region, transcription, or decision predicate.

The only authorized recovery is to reseal the test admission row and every
dependent root/internal binding for each target-only mutation, assert the
declared inner error, and prove target-only repair. This is test-evidence work;
do not alter public APIs or access a live PDF, source reconstruction,
EN/RU/Keeper/HTML/PDF artifacts, rebuild, Git or release paths.

## Packet 4b.6-r Architecture Accepted; Bounded Implementation Pending — 2026-08-11

Sol replaced the circular full-admission root reference with an explicit,
production-owned two-seal graph: immutable pre-visual binding `P` binds stable
identity, Stage-A/topology identity and render bytes; final admission binding
`F` binds `P` plus the final witness/render/cross-check leaf pairs. WitnessV2
and CrossCheckV2 carry `P`, never `F`; candidate/review/ledger projection will
later use `F`. The construction order is acyclic: `render -> P -> witness ->
mechanics/flow -> cross-check -> F`.

Independent Terra accepted this architecture with no P0/P1/P2 in
`handoffs/terra_page_proof_visual_crosscheck_binding_remediation_architecture_review_20260811.md`.
The authoritative bounded implementation specification is
`handoffs/sol_page_proof_visual_crosscheck_binding_remediation_spec_20260811.md`.

This advances only to implementation authorization for fixture-only packet
`4b.6-r`. It does not accept implementation, unlock `4b.7`, activate production
registries, permit a live PDF/source/output/rebuild, Git, or release work. The
next owner is a `gpt-5.4` bounded executor using Sol section 3 exactly; then a
fresh independent Terra implementation-remediation review is mandatory.

## Executor Recovery: Reassign to Terra Engineering — 2026-08-11

Two separately created `gpt-5.4` low UI executor tasks stopped at the platform
budget limit before any code/test/receipt write: `019ff07e-bb2a-7322-a3c5-e09c1cee3a5f`
and `019ff080-31d5-7e01-b48c-4c56f166c6fa`. The second confirmed the current
V1 cycle and allowed scope, but made no change. This repeated no-progress stop
means `4b.6-r` is not a suitable low-effort mechanical packet.

Following the NRI recovery rule, the same narrow implementation scope is
reassigned to a Terra engineering task at `medium`. A distinct Terra critic at
`high` must review the implementation and cannot be the implementing task. No
other scope or live/rebuild authorization changes.

## Packet 4b.6-r First Implementation Review Rejected — 2026-08-11

Independent Terra reviewed the actual two-seal implementation in
`handoffs/terra_page_proof_visual_crosscheck_binding_remediation_implementation_review_20260811.md`.
It confirms the P/W/E/V/F graph is acyclic, W/V roots contain `P` not `F`, the
three literal P/F anchors agree with independent oracles, public registries
remain inactive, and the prescribed bounded suite reports `82 passed`.

The packet is nevertheless rejected on five P1 evidence gaps: no direct
pre-normalizer `P`/admission/exact-tuple/predicate-vector assertions; no fourth
valid-admission V case with two ordered boundaries; missing root/reviewer and
boundary-structure target classes; mutation F built through production rather
than independent oracle; and no durable AST containment assertion. The recovery
is limited to these P1.1–P1.5 points in Sol's existing allowed files. No live
source, output, rebuild, Git, registry activation, `4b.7`, or release work is
authorized. A new independent Terra implementation receipt is mandatory after
any candidate mutation.

## Packet 4b.6-r Re-review Rejected; Evidence Specification Required — 2026-08-11

The recovery re-review is recorded in
`handoffs/terra_page_proof_visual_crosscheck_binding_remediation_rereview_20260811.md`.
It confirms that P1.4 (independent mutation-F oracle) is fixed, but keeps the
packet rejected on P1.1/P1.2/P1.3/P1.5. The remainder is precise: the shared
pre-normalizer helper lacks the exact W/render/V triplet and complete predicate
vector; the fourth boundary case is derived rather than literal and does not
prove target-only repair; target coverage is incomplete; and the AST assertion
does not prove the binding-helper dependency set.

Do not send a third open-ended engineering remediation. Sol must first publish a
literal, file-scoped evidence packet for these four P1s. Only then may Terra
engineering modify the existing narrow scope and request another independent
implementation review. All no-live/no-output/no-Git/no-4b.7 boundaries persist.

## Checkpoint: Sol Exact Evidence Contract — 2026-08-11

Sol produced `handoffs/sol_page_proof_visual_crosscheck_evidence_remediation_packet_20260811.md`
with SHA-256 `357CF146FC8E65A6DF7B4BCA249EB470BEA6BEB8F0E67B49F0E9FE42B1CA2C61`.
The receipt is a specification only: it changed no code or artifacts. It gives
the next Terra engineer a bounded task packet and the next independent Terra
critic a literal acceptance checklist. The single current step is implementation
of that packet; P2/P3 observations do not substitute for any P0/P1 closure and
will be recorded as debt only after the current P1 gate is resolved.

Allowed implementation writes: `kb_creator/tests/_page_proof_fixture_leaves.py`,
`kb_creator/tests/test_page_proof_visual_crosscheck.py`, and a new immutable
executor receipt. `kb_creator/pdf_raw/page_proof.py` must retain SHA-256
`A6E5E647A6B973772D6690775EC78F30FBDA909CBB19F95D6A88A4BA9702870B`.
No live PDF, source reconstruction, Keeper/HTML/PDF output, build, browser,
network, Git, registry activation, Packet 4b.7, or release action is allowed.

## Checkpoint: Exact-Evidence Implementation Rejected — 2026-08-11

Independent Terra reviewed the first implementation of Sol's exact evidence
packet in `handoffs/terra_page_proof_visual_crosscheck_evidence_remediation_review_20260811.md`.
It confirmed the frozen production SHA and the bounded `87 passed in 0.33s`
regression, but rejected the fixture evidence on P1.1/P1.2/P1.3/P1.5.

The repair remains test-only and exact: migrate every internal normalizer call
to the keyword-only full literal fifteen-predicate contract; use the mandated
fourth-case duplicate row 1 and inverse repair; replace generated vectors and
the weak aggregate case while migrating retained legacy target-only repairs;
and make AST containment prove Sol's full P/F field/dependency/prohibited-node
contract. The governance recovery step is to resume the same Terra engineering
task with this bounded critic receipt before any orchestrator takeover. All
P2/P3 work remains debt-only and cannot advance the gate.

## Checkpoint: Terra Recovery Restart Did Not Close P1 — 2026-08-11

The required same-task recovery restart was made in UI-visible Terra engineering
task `019ff082-cfaf-75d1-8f4f-7a5ebd82fc1f`. It stopped without acceptance:
the per-call literal migration remains incomplete after repeated continuation
attempts. Production SHA remains unchanged and no live/output/Git path was
opened. This is not grounds for a third open-ended implementation loop.

Next action is a narrow Sol architecture clarification: define one feasible,
canonical test-file layout that can satisfy the critic's literal-per-call
evidence rule without generated vectors, legacy helper bypasses, or an
unbounded rewrite. A later fresh Terra implementation task must follow that
clarification. P2/P3 remain debt-only.

## Checkpoint: Canonical Layout Not Started by Fresh Terra — 2026-08-11

Fresh Terra engineering receipt
`handoffs/executor_page_proof_visual_crosscheck_canonical_layout_20260811.md`
verified the frozen production and leaf hashes and a baseline `86 passed`, but
made no test-file mutation. It found the expected unaccepted starting state:
36 normalizer calls, zero of Sol's 46 explicit target tests, and all prohibited
legacy helpers. It correctly refused to leave an invalid partial replacement,
citing insufficient medium execution budget.

This is a repeated bounded-execution failure after the required recovery
restart, not a P0/P1 semantic impossibility. The next action requires an
explicit governance recovery decision: orchestrator takeover of the one test
file, or a user-recorded scoped Terra/high implementation override. No other
pipeline stage is authorized, and P2/P3 remain debt-only.

## Checkpoint: User-Authorised Terra/High Override — 2026-08-11

The user explicitly authorized a scoped `Terra / high` implementation override
for the canonical one-file Packet 4b.6 rewrite. It applies only to
`kb_creator/tests/test_page_proof_visual_crosscheck.py` and one new immutable
executor receipt under Sol's layout clarification. It does not authorize any
production/fixture-leaf/live/output/Git change, does not relax P1, and does not
replace the required fresh independent Terra implementation review.

## Checkpoint: Sol Canonical One-File P1 Layout — 2026-08-11

Sol's clarification receipt
`handoffs/sol_page_proof_visual_crosscheck_evidence_layout_clarification_20260811.md`
finds no genuine P0/P1 conflict. It supersedes only the former test-evidence
layout: legacy normalizer families and generated vectors must be replaced with
four named one-call fixtures, 46 explicit target tests, two outer-envelope
tests, and an AST proof of exactly 98 normalizer calls. The P/W/E/V/F semantics,
literal fourth-case facts, frozen production/leaf hashes, and no-live boundary
remain unchanged.

The next task must go to a fresh Terra engineer, with writes limited to
`test_page_proof_visual_crosscheck.py` and one new receipt. It is large but
finite; a fresh independent Terra critic must apply Sol section 8 before any
acceptance. P2/P3 remain debt-only.

## Checkpoint: Canonical Layout Review Found Two Narrow P1s — 2026-08-11

Fresh independent Terra confirmed the canonical replacement's major evidence:
frozen production/leaves, four positive fixtures, 46 two-call tests, two outer
tests, `98` direct normalizer calls, literal vectors, fourth-case repairs, and
`129 passed`. It nevertheless rejected exactly two P1s in
`handoffs/terra_page_proof_visual_crosscheck_canonical_layout_review_20260811.md`:
two target names include forbidden `_id` aliases, and the P/F AST test remains
a subset rather than Sol's complete graph proof.

The user-authorized Terra/high executor may repair only those names and the
one containment test in the same test file, then a fresh independent Terra
review is mandatory. No other scope is reopened.

## Checkpoint: Packet 4b.6 Accepted; 4b.7 Requires Separate Specification — 2026-08-11

Fresh independent Terra accepted the narrow P1 repair in
`handoffs/terra_page_proof_visual_crosscheck_canonical_layout_p1_repair_review_20260811.md`.
The repaired test-only candidate preserves frozen production and fixture-leaf
hashes, restores the two exact target names, and gives the complete Sol 5.2
P/F AST-containment proof. The critic found no P0/P1; `py_compile` passed and
the required seven-suite regression reported `129 passed in 0.44s`.

The one P2 process observation is an early read-only `git status`; it did not
change Git/candidate state and is now recorded as
`../../debt.md#KB-DEBT-20260811-001`. It is debt-only and does not delay this
P0/P1 acceptance. `4b.7` is still not authorized for implementation: Sol must
first publish a separate bounded fixture-only specification. The no-live,
no-source, no-output, no-build, no-Git, and no-production-registry boundaries
remain unchanged.

## Checkpoint: Packet 4b.7 Architecture Accepted; Bounded Implementation Pending — 2026-08-11

Sol specified `WitnessV3` composition in
`handoffs/sol_page_proof_packet_4b7_spec_20260811.md` (SHA-256
`7594DFFB88C9F9F1779443729EB1E636574C74EB1F56B2D17586A5A0E5B32176`).
Fresh independent Terra accepted that architecture without P0/P1 in
`handoffs/terra_page_proof_packet_4b7_architecture_review_20260811.md`.

The one authorized implementation is fixture-only: migrate the witness to a
closed `WitnessV3` that carries canonical `flow_input`, then compose the same
witness as `W -> M -> E -> V` without a separate flow builder, geometry/V
inference, production registry, or public proof result. This is not live input,
source reconstruction, output/build, Git, 4b.8, Step 5, or release permission.
The next owner is a bounded Terra engineer at `medium`; a fresh independent
Terra critic at `high` is mandatory after any mutation.

## Checkpoint: 4b.7 Medium Recovery Exhausted; Scoped Terra/High Implementation — 2026-08-11

The medium Terra engineer verified the frozen baseline twice but stopped before
changing code because the atomic WitnessV3/P'/W'/V'/F' reseal and eight-suite
verification cannot safely be split. The two immutable no-mutation receipts
are `handoffs/executor_page_proof_packet_4b7_20260811.md` and
`handoffs/executor_page_proof_packet_4b7_restart_checkpoint_20260811.md`.

Under the user's explicit Terra/high authorization and the restart-before-
takeover rule, one scoped high-effort Terra implementation is now authorized
for Sol sections 3-6 only. The permitted file set and all no-live/no-source/
no-output/no-build/no-Git/no-production-registry boundaries are unchanged. A
different fresh Terra critic remains mandatory after any candidate mutation.

## Checkpoint: Packet 4b.7 Accepted; Next Packet Requires Separate Specification — 2026-08-11

The scoped Terra/high recovery completed the atomic WitnessV3 migration and
composition, recorded in
`handoffs/executor_page_proof_packet_4b7_high_recovery_20260811.md`. Fresh
independent Terra accepted the implementation with no P0/P1 in
`handoffs/terra_page_proof_packet_4b7_high_recovery_review_20260811.md`;
`handoffs/terra_page_proof_packet_4b7_high_recovery_review_correction_20260811.md`
supersedes only one historical before-hash transcription. `py_compile` passed
and the exact eight-suite regression reported `147 passed in 0.51s`.

This accepts only private fixture composition. Production roots are still
inactive and exact authoritative production topology-acceptance identities are
still absent. No live PDF/source, reconstruction, output/build, Git, 4b.8,
Step 5, or release action is authorized. The only next action is a separately
specified fixture-only P0/P1 packet.

## Checkpoint: Packet 4b.8 Fixture Identities Accepted — 2026-08-11

Fresh independent Terra accepted the bounded aggregate review in
`handoffs/terra_page_proof_packet_4b8_aggregate_acceptance_review_20260811.md`
without P0/P1. The two authoritative fixture-only child identities are:

- two-column: `74ddca65755dbde190b57a5e82368895644ac6b605873913c20a32f2786d6526`;
- nested Form: `136489ff1892bb27b8425806a1972809d03ce5e5e22f42b6a9f1bdfeca1cc503`.

This is evidence closure only. Stage A checks passed (`15 passed`; `386 passed,
1 skipped`), but no production registry, ledger/replay terminal, live PDF,
source reconstruction, output/build, Git, or release path was opened. The
next required artifact is a separately specified private inventory/reseal
packet; it must consume these identities without activating production roots.

## Checkpoint: Packet 4b.9 Architecture Accepted; Private Implementation Pending — 2026-08-11

Sol's post-4b.8 specification,
`handoffs/sol_page_proof_post_4b8_inventory_reseal_spec_20260811.md`, defines
the smallest next P0/P1 step: construct a private test-only authoritative
inventory from exactly the two accepted child identities and reseal `P/W/V/F`.
Fresh independent Terra accepted that architecture with no P0/P1 in
`handoffs/terra_page_proof_packet_4b9_architecture_review_20260811.md`.

Only Sol sections 3-7 may now be assigned to bounded Terra engineering. The
packet must not create a candidate ledger, terminal/public result, production
activation, or a live/source/output/build/Git path. Fresh independent Terra
implementation review remains mandatory after a candidate mutation.

## Checkpoint: Packet 4b.9 Invalid Partial Candidate; Recovery Decision Required — 2026-08-11

The high-recovery executor detected its own boundary breach before test/compile
verification: transient dynamic-import tooling and a read-only `git status`
violated the packet's no-dynamic-import/no-Git rule. It also left an incomplete
literal reseal in seven allowed test files. The immutable blocker receipt is
`handoffs/executor_page_proof_packet_4b9_high_recovery_20260811.md`.

This state is not a candidate and must not receive independent implementation
review. No production root, live/source/output/build/network/release path was
opened. Recovery needs a user-authorized destructive action: restore the seven
listed test files to their recorded frozen 4b.9 hashes, then rerun the same
bounded packet under a new executor receipt. Until that decision, 4b.9 is
blocked and no later packet is authorized.

## Checkpoint: 4b.9 Exact Recovery Source Missing — 2026-08-11

Sol's forensic recovery prescription is
`handoffs/sol_page_proof_packet_4b9_baseline_recovery_spec_20260811.md`.
It proves deterministic inverse recovery for six changed files but cannot
recreate the byte-exact frozen
`tests/_page_proof_fixture_leaves.py` from a SHA-256 alone: repeated literals
make the inverse ambiguous. The required file hash is
`B471EB875410C09CDEF9ABA3F39082C3201F815D6C62ED9F3165A4ED58E1DF7E`.

Read-only searches of `D:\NRI` and `C:\Users\BogdanD\.codex` found no matching
copy. Do not apply a six-file partial rollback. The next action requires an
external byte-exact backup of that fixture-leaves file; after it is supplied,
restore all seven files atomically and verify Sol's SHA matrix before retrying
4b.9.

## Checkpoint: User Chose In-Place Salvage Without Frozen File — 2026-08-11

The user explicitly chose to proceed without the unavailable byte-exact
fixture-leaves backup. Therefore the old frozen 4b.9 baseline is abandoned as
a recovery target. The current seven-file partial reseal is still invalid and
unaccepted; it becomes a new candidate only after a Sol-defined salvage
contract re-proves every affected 4b.6-4b.9 invariant from current bytes.

No prior 4b.6/4b.7 acceptance is silently reused as a frozen-hash assertion.
Production roots, public terminal states, live PDF/source, output/build, Git,
and release remain prohibited. Next action: a new Sol fixture-only salvage
specification, then fresh independent Terra architecture and implementation
reviews.

## Superseding completion checkpoint — 2026-08-26

Later work on the dedicated Innsmouth branch completed the English
reconstruction chain. The user accepted the Packet 7 user-review successor,
and a fresh independent `gpt-5.5` release review returned
`ACCEPT_PACKET7_USER_REVIEW_SUCCESSOR_RELEASE_ADMISSION` with no P0/P1/P2.

The canonical repository copy is
`kb_creator/inputs/innsmouth/master_en/packet7_user_review_20260826/`.
Its `MASTER_EN.md` is `133032` bytes with SHA-256
`41E84FAA5A247434133D2A3B0A40245C4842C4F906E7D5D117B9353DE05C1D18`.
The complete package is 41 files, 38 assets and `10289376` bytes. This
checkpoint supersedes the old live-path prohibition only for the already
accepted English package; original sources remain immutable.

The next goal is separate:
`../20260826-innsmouth-direct-master-ru-publication/`. It permits only a fresh
direct translation from the accepted MASTER_EN. Historical RU v6, old cleaned
EN v6 and the old unit/source-hash bridge are excluded.

## Historical Checkpoint: Paused for New-Chat Resume — 2026-08-11

Work is deliberately paused after the user chose in-place salvage without the
unavailable frozen fixture-leaves backup. At this checkpoint, Packet 4b.9 was
unaccepted and all live Innsmouth and production paths remained closed. This
checkpoint is superseded by the later 4b.9 in-place fixture-only salvage
acceptance above; live Innsmouth and production paths remain closed until Step
5 is separately authorized and reviewed.

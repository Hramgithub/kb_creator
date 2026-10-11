# Sol P1 Correction — Page-Level Consumer/Proof Contract

- Goal id: `20260809-innsmouth-page-level-consumer-proof`
- Step id: `3a`
- Role: Sol architect, requested effort `high`.
- Contract status: immutable proposed correction; no implementation is authorized.
- Corrects only the three P1 findings in the independent Terra architecture
  review dated 2026-08-09.

## 1. Amendment authority and unchanged boundary

This document is a normative amendment to
`sol_page_level_consumer_proof_spec_20260809.md`, SHA-256
`44EF02B7BDFBA240733BBEDF6F4018313C32F6E312E48CAAEAFCE7FFC2E6DD24`.
If the two documents conflict, this correction controls only:

1. reading-flow membership, exclusions and paragraph adjacency;
2. Stage A positive-topology coverage admission and mechanics-only behavior;
3. independent per-block/per-boundary visual cross-check evidence and review
   binding.

All other original requirements remain mandatory. In particular, this
correction does not admit any path, file object, arbitrary/live PDF bytes,
configuration, environment switch, callback, parser, OCR, EN, Keeper, HTML,
PDF, output, rebuild, source reconstruction, repair or release operation.
`RawAtomProvenanceAuthorityV1` remains the sole Stage A authority type. The
consumer must not import or call `RawPdfDocument`,
`extract_raw_pdf_page_atoms`, `_raw_replay`, `derive_page043_relation`, or
`source_reconstruction.py`. No live consumer mode or switch is introduced.

## 2. P1-1 replacement: closed reading-flow disposition

### 2.1 Mandatory block fields

Every `proposed_blocks[]` witness row and every normalized output `blocks[]` row
must add these closed, row-hash-bound fields:

```text
reading_flow_disposition: "included" | "excluded"
reading_flow_reason:
    "included_eligible_visible_text" |
    "excluded_decorative" |
    "excluded_occluded" |
    "excluded_text_layer_only" |
    "excluded_text_layer_disagreement" |
    "excluded_visible_text_without_layer" |
    "excluded_visual_only" |
    "excluded_non_text_visual" |
    "excluded_not_rendered" |
    "excluded_unresolved_or_blocked"
reading_flow_derivation_sha256: sha256
```

`reading_flow_derivation_sha256` is domain-separated canonical SHA-256 over:

```text
block_id
mechanical_kind
visibility_status
decoration_status
text_layer_status
publication_status
line_fragment_ids in block order
derived reading_flow_disposition
derived reading_flow_reason
```

The witness must carry the expected fields, but the consumer must independently
derive them using section 2.2 and require exact equality. The witness cannot
choose or override membership. Missing fields, unknown reasons, mismatches or a
reason inconsistent with the status axes fail with
`page_proof_flow_disposition_invalid` before candidate construction.

### 2.2 Total normative derivation

The derivation uses the first matching row below, in this exact precedence.
Rows are mutually exclusive by precedence, not by an implicit heuristic.

| Priority | Mechanical/status condition | Disposition | Reason |
| --- | --- | --- | --- |
| 1 | Any of visibility, decoration, text-layer or publication status is `unresolved`/`blocked`, or required geometry/mapping is unresolved | `excluded` | `excluded_unresolved_or_blocked` |
| 2 | `decoration_status = decorative` and publication status is `non_publication_decorative` | `excluded` | `excluded_decorative` |
| 3 | `visibility_status` is `partially_occluded` or `fully_occluded` and publication status is `non_publication_occluded_recovery` | `excluded` | `excluded_occluded` |
| 4 | `text_layer_status = text_layer_only` and publication status is `non_publication_text_layer_only` | `excluded` | `excluded_text_layer_only` |
| 5 | `text_layer_status = disagrees` and publication status is `blocked` or a closed non-publication disagreement state | `excluded` | `excluded_text_layer_disagreement` |
| 6 | `text_layer_status = absent_for_visible_text` | `excluded` | `excluded_visible_text_without_layer` |
| 7 | `visibility_status = visual_only` or `mechanical_kind = visual_only`, with publication status `non_publication_visual_only` | `excluded` | `excluded_visual_only` |
| 8 | `mechanical_kind = image`, no line fragments/glyphs exist, and the block is neither decorative nor unresolved | `excluded` | `excluded_non_text_visual` |
| 9 | `visibility_status = not_rendered` | `excluded` | `excluded_not_rendered` |
| 10 | `mechanical_kind` is `text` or `mixed`; visibility is `visible`; decoration is `content`; text-layer is `agrees_visible`; publication is `eligible_for_order_boundary_proof`; at least one non-empty line fragment exists; all geometry/mapping/conservation checks pass | `included` | `included_eligible_visible_text` |

Any combination not matched by the table is invalid; it must not be coerced to
an exclusion. A block with `included` must match priority 10 exactly. A block
with `excluded` cannot use `included_eligible_visible_text`. No aliases, null,
`ignored`, `dropped`, free-text reason or plugin-defined reason are accepted.

The normalized ledger copies the independently derived values, not the witness
values. Its block `row_id`, `row_sha256`, block inventory digest and evidence
core all include the three new fields.

### 2.3 Bound exclusion rows

`proposed_reading_order.excluded_block_rows[]` is replaced by this closed row:

```text
block_id
reading_flow_disposition: "excluded"
reading_flow_reason: one exclusion enum from section 2.1
block_reading_flow_derivation_sha256
exclusion_ordinal: contiguous int from 0
row_id
row_sha256
```

The array must contain every and only excluded block exactly once, sorted by
`block_ordinal`. Each row must match the corresponding normalized block fields
and derivation digest exactly. An included block in this array, an excluded
block absent from it, duplicate/reordered rows, or a substituted reason fails
with `page_proof_reading_flow_partition_invalid`.

`proposed_reading_order.ordered_block_ids` must contain every and only included
block exactly once. Thus:

```text
set(ordered_block_ids) ∩ set(excluded block ids) = empty
set(ordered_block_ids) ∪ set(excluded block ids) = set(all block ids)
```

The two arrays are a complete, disjoint partition, and their content/order
digests are included in `reading_order.row_sha256`, `inventory_sha256` and the
pre-visual evidence core defined in section 4.4.

### 2.4 Deterministic fragment and adjacency universe

The consumer derives the only permitted paragraph fragment universe as follows:

1. Traverse `ordered_block_ids` in its exact proposed reading order.
2. For each block, require `reading_flow_disposition = included` and append its
   `line_fragments` in contiguous `fragment_ordinal` order.
3. Require every included fragment to contain at least one Stage A glyph, valid
   geometry and non-empty Stage A-derived text.
4. Excluded blocks contribute no fragment. A boundary that references an
   excluded block/fragment is invalid.
5. Let `F` be the resulting ordered fragment-id array. The adjacency universe is
   exactly `[(F[0],F[1]), ..., (F[n-2],F[n-1])]`; for `n < 2`, it is empty.

The ledger adds:

```text
reading_flow_block_ids: exact ordered included block ids
excluded_block_rows: exact bound rows from section 2.3
fragment_universe: exact F
fragment_universe_sha256: sha256(domain, F)
adjacency_universe: exact ordered adjacent pairs
adjacency_universe_sha256: sha256(domain, adjacency_universe)
```

`proposed_paragraph_boundaries[]` must be an exact one-to-one ordered mapping of
`adjacency_universe`: same count, same pair at each `boundary_ordinal`, no
additional pair and no omission. Every boundary id is derived from
`page_identity_sha256`, `adjacency_universe_sha256`, ordinal and the two fragment
ids. `paragraph_adjacencies_complete` is true only when this exact equality and
all per-boundary cross-checks in section 4 pass. This rule deterministically
fixes the adjacency universe; neither the witness nor reviewer may enlarge,
shrink or reorder it.

## 3. P1-2 replacement: non-bypassable topology coverage

### 3.1 Literal topology coverage inventory

The implementation must contain a code-owned, immutable
`PageProofRequiredStageATopologyInventory.v1` and a second independent literal
expected tuple. It is not loaded from a file, environment, test parameter,
callback or registry. Its required topology-id tuple is exactly:

```text
(
  "stage_a_positive_two_column.v1",
  "stage_a_positive_nested_form.v1",
)
```

Each literal inventory entry is closed and contains:

```text
topology_id: one required literal id
stage_a_fixture_id: exact accepted fixture id
stage_a_authority_schema: "kb_creator.pdf_raw.RawAtomProvenanceAuthority.v1"
stage_a_authority_content_sha256: sha256
stage_a_authority_inventory_sha256: sha256
stage_a_fixture_binding_sha256: sha256
positive_topology_assertion_sha256: sha256 over the topology facts required below
independent_stage_a_review_kind: "fixture_topology_acceptance"
independent_stage_a_review_decision: "accept"
independent_stage_a_review_content_sha256: sha256
reviewed_authority_content_sha256: same authority content sha256
entry_sha256: domain-separated sha256 over every preceding field
```

The two-column assertion pins at least two content blocks, explicit left/right
column membership and a non-trivial cross-column reading transition. The
nested-Form assertion pins at least one Form invocation, distinct parent and
child frames, child atoms/glyphs, invocation-token linkage and exact paint
placement. A minimal/single-atom fixture cannot satisfy either assertion.

An entry counts only if its exact Stage A authority and topology assertion have
an independent accepted Stage A review whose content hash and reviewed authority
hash are the literal values. A plan row, proposed fixture, self-review,
page-consumer review, aggregate test count or rehashed surrogate does not count.

The inventory root contains the exact required id tuple, the two entries in that
order, `entry_count = 2`, `inventory_sha256` and `content_sha256`. Any missing,
duplicate, reordered, aliased, rejected, unreviewed, hash-mismatched or
topology-insufficient entry makes coverage incomplete.

### 3.2 One normative public-path rule

After primitive ingress type checks and before decoding any witness, PNG,
candidate, review or expected ledger, every public operation named below must
recompute and validate the complete literal topology inventory:

- `derive_fixture_page_block_ledger_v1`;
- `review_fixture_page_block_ledger_v1`;
- `replay_fixture_page_block_ledger_v1`.

If either required accepted inventory entry is absent or invalid, **each call
must raise exactly**
`RawPdfError("page_proof_stage_a_fixture_coverage_incomplete")` and return no
candidate, reviewed ledger, rejected ledger, partial dict or other proof-like
object. Input validity, an existing minimal candidate, a supplied review marked
`accept`, and an expected replay ledger do not change this result. There is no
fixture-specific exemption and no success terminal state while coverage is
incomplete.

Every complete literal `PageProofFixtureAdmission.v1` row must additionally bind
`required_topology_inventory_content_sha256`. Every candidate, reviewed ledger,
visual cross-check and review attestation must repeat that digest; replay must
recompute and require exact equality. Cross-pair substitution between a fixture
row and topology inventory fails admission.

This section replaces every ambiguous allowance in original §§2.2, 8 and 12.
The current minimal Stage A fixture inventory cannot produce
`fixture_candidate_review_required`, `fixture_proof_accepted_no_source_use`, or
`fixture_proof_rejected_no_source_use` through any public derive/review/replay
path.

### 3.3 Optional mechanics harness is non-proof

An executor may omit a mechanics harness. If retained for test development, it
must be private to fixture tests and return only a separately capability-typed,
immutable `PageProofMechanicsHarnessResult.v1` with:

```text
terminal_state: "fixture_mechanics_only_nonproof_topology_incomplete"
proof_eligible: false
attestable: false
source_use: "forbidden"
review_eligible: false
```

It must have no `PageBlockEvidenceCandidateV1` type, no accepted-proof schema,
no review field, no evidence-core digest that is accepted by the proof API, and
no conversion/cast/serialization accepted by derive/review/replay. The public
review entrypoint still performs section 3.2 first and therefore emits
`page_proof_stage_a_fixture_coverage_incomplete` while inventory is incomplete.
After coverage becomes complete, attempting to attest a mechanics result fails
with `page_proof_mechanics_attestation_forbidden`. A mechanics result cannot be
listed as a reviewable artifact or satisfy any implementation acceptance row.

## 4. P1-3 replacement: independent visual cross-check artifact

### 4.1 Required independent input and public signatures

The admitted leaf set adds canonical bytes
`independent_visual_crosscheck_raw`. Every literal fixture admission row adds its
byte length, SHA-256 and binding contribution. The public conceptual signatures
are replaced by:

```text
derive_fixture_page_block_ledger_v1(
    validated_stage_a_authority,
    witness_raw: bytes,
    render_png_raw: bytes,
    independent_visual_crosscheck_raw: bytes,
) -> PageBlockEvidenceCandidateV1

review_fixture_page_block_ledger_v1(
    candidate_raw: bytes,
    independent_visual_crosscheck_raw: bytes,
    review_raw: bytes,
) -> ReviewedPageBlockEvidenceV1

replay_fixture_page_block_ledger_v1(
    validated_stage_a_authority,
    witness_raw: bytes,
    render_png_raw: bytes,
    independent_visual_crosscheck_raw: bytes,
    review_raw: bytes,
    expected_ledger_raw: bytes,
) -> ReviewedPageBlockEvidenceV1
```

The topology check in section 3.2 precedes cross-check decoding on every path.
After complete topology admission, each path independently validates the
cross-check against the exact admitted authority, witness, render, derived
components and pre-visual evidence core. Passing a cross-check only to derive,
only to review, or only to replay is impossible.

### 4.2 Closed root schema

`kb_creator.pdf_raw.IndependentPageVisualCrossCheck.v1` is immutable canonical
JSON with closed root fields:

```text
schema
profile
fixture_id
fixture_binding_sha256
required_topology_inventory_content_sha256
stage_a_authority_content_sha256
witness_content_sha256
render_png_sha256
page_identity_sha256
component_universe_sha256
pre_visual_evidence_core_sha256
reviewer
block_checks
boundary_checks
counts
decision_inventory_sha256
inventory_sha256
content_sha256
```

`reviewer` is closed and contains:

```text
reviewer_role: "independent_visual_checker"
reviewer_identity: non-empty stable label
assignment_state: "platform-unverified"
implemented_candidate: false
materially_designed_candidate: false
aggregate_only: false
checked_at: RFC 3339 timestamp with offset
```

The cross-check is a fixture evidence leaf, not the aggregate Terra architecture
or implementation review. Its reviewer must not be the implementer/material
designer of the fixture decisions under check. Independence failure makes every
row ineligible and fails `page_proof_visual_crosscheck_invalid`.

### 4.3 Per-block independent check

`block_checks[]` contains exactly one row for every normalized block, ordered by
`block_ordinal`. Each row has closed fields:

```text
block_id
block_ordinal
render_png_sha256
checked_region_bbox_px
checked_region_pixel_sha256
checked_component_refs: ordered rows of component_id, mask_sha256, bbox_px
witness_block_decision_sha256
stage_a_derived_text_utf8_b64
independent_visible_transcription_utf8_b64
independent_visible_transcription_sha256
independent_visibility_status
independent_decoration_status
independent_text_layer_status
independent_publication_status
independent_reading_flow_disposition
independent_reading_flow_reason
independent_reading_order_ordinal_or_null
independent_column_id_or_null
independent_predecessor_block_id_or_null
independent_successor_block_id_or_null
decision: "confirm" | "reject"
reason_code: one closed block reason
decision_specific_sha256
row_id
row_sha256
```

`checked_region_bbox_px` must contain the block bbox plus the profile's literal
context margin and remain in render bounds. The consumer re-extracts that exact
pixel region from `render_png_raw` and recomputes
`checked_region_pixel_sha256`. It re-derives every referenced component from the
render and requires exact id/mask/bbox equality. Components outside the block
may be referenced only when they intersect the context region and are required
to assess occlusion, column relation or decoration.

`witness_block_decision_sha256` is a domain-separated digest of the exact witness
block id, geometry, component ids, status axes, reading-flow derivation fields,
column/order relations and proposed text-layer comparison. It prevents a check
for one decision from being reused for a changed decision.

Both transcription byte fields are mandatory canonical base64, including empty
bytes for a confirmed non-text/visual-only block. The Stage A field is
re-derived from Stage A glyphs; the independent visible transcription is the
checker-recorded literal fixture transcription. Its digest is recomputed from
the decoded bytes. A hash without these bytes is invalid.

For an included block, `decision = confirm` is valid only when:

- independent statuses and reading-flow fields exactly equal the mechanically
  validated witness/ledger decisions;
- independent reading ordinal, column and predecessor/successor exactly equal
  the normalized reading order;
- independent visible transcription bytes equal Stage A-derived bytes exactly,
  without normalization, OCR fallback, case folding or whitespace repair;
- all render-region and component references replay exactly.

For an excluded block, `confirm` requires the independent statuses and exact
closed exclusion reason to match section 2.2 and the visual/component evidence.
Disagreement, occlusion, decoration, visual-only and non-text decisions each use
a distinct closed reason code. `reject`, unknown reason, unresolved independent
status, missing block, duplicate block or any mismatch fails candidate creation
with `page_proof_visual_block_crosscheck_failed`.

`decision_specific_sha256` is:

```text
sha256(
  "page-proof.visual-block-decision.v1\0" + canonical_json({
    fixture/page/authority/witness/render/component/pre-visual-core bindings,
    block id and ordinal,
    checked region and component refs,
    witness_block_decision_sha256,
    both decoded transcription byte values and their digests,
    all independent status/flow/order fields,
    decision,
    reason_code
  })
)
```

Changing any decision, reason, text byte, order relation or evidence reference
invalidates the digest.

### 4.4 Per-boundary independent check and hash order

First, the consumer computes `pre_visual_evidence_core_sha256` over the complete
normalized source/page/Stage A/render/component/block/coverage/paint-order/
reading-flow/fragment-universe/adjacency-universe/proposed-boundary/
text-layer/conservation data, excluding the cross-check, aggregate review,
terminal decision and final hashes. This digest is fixed before cross-check
validation and avoids a circular hash.

`boundary_checks[]` then contains exactly one row per derived adjacency pair in
section 2.4, in boundary ordinal order:

```text
boundary_id
boundary_ordinal
left_fragment_id
right_fragment_id
left_block_id
right_block_id
render_png_sha256
left_checked_region_bbox_px
right_checked_region_bbox_px
left_region_pixel_sha256
right_region_pixel_sha256
checked_component_refs
witness_boundary_decision_sha256
left_independent_visible_transcription_utf8_b64
right_independent_visible_transcription_utf8_b64
measured_line_gap_px: canonical decimal
measured_indent_delta_px: canonical decimal
measured_column_relation: "same_column" | "cross_column" | "section_transition"
independent_boundary_decision: "same_paragraph" | "paragraph_break" |
                               "column_break" | "section_break" |
                               "not_applicable"
decision: "confirm" | "reject"
reason_code: one closed boundary reason
decision_specific_sha256
row_id
row_sha256
```

The consumer re-extracts both render regions, recomputes pixel digests,
re-derives every component ref, and requires fragment/block ids to match the
exact adjacency universe. It decodes actual independent transcription bytes and
requires each to equal its corresponding Stage A-derived fragment bytes before
an eligible boundary can be confirmed. `witness_boundary_decision_sha256`
binds the exact witness boundary id/pair, geometry cues, text cues, decision and
reason codes.

`decision = confirm` requires the independent boundary decision to equal the
witness decision and its measured geometry/column relation to satisfy the
literal profile rule for that decision. `unresolved` is not an independent
decision. A missing/extra/reordered row, hash-only transcription, wrong pair,
changed witness decision, pixel/component mismatch, transcription mismatch,
decision mismatch, unknown reason or `reject` fails with
`page_proof_visual_boundary_crosscheck_failed`.

The boundary `decision_specific_sha256` uses domain
`page-proof.visual-boundary-decision.v1\0` and canonically hashes every field
above plus fixture/page/authority/witness/render/component/pre-visual-core
bindings. It cannot be reused across a pair, decision or reason.

After every block and boundary row passes, the cross-check root computes:

```text
decision_inventory_sha256 = sha256(domain, ordered block decision digests,
                                   ordered boundary decision digests, counts)
evidence_core_sha256 = sha256("page-proof.evidence-core.v1\0",
                              pre_visual_evidence_core_sha256,
                              crosscheck content_sha256,
                              decision_inventory_sha256)
```

The final ledger adds the complete immutable cross-check root,
`pre_visual_evidence_core_sha256`, `visual_crosscheck_content_sha256`,
`visual_decision_inventory_sha256` and final `evidence_core_sha256`. All are
included in inventory/content hashes and exact replay.

### 4.5 Aggregate review cannot substitute

`PageProofReviewAttestation.v1` is amended with mandatory fields:

```text
required_topology_inventory_content_sha256
pre_visual_evidence_core_sha256
visual_crosscheck_content_sha256
visual_decision_inventory_sha256
confirmed_block_decision_count
confirmed_boundary_decision_count
candidate_evidence_core_sha256
```

The counts must equal all blocks and all derived adjacency pairs respectively.
The aggregate reviewer must bind the exact recomputed digests. The review may
accept only after every row-specific visual decision is `confirm` and all
reverification passes. Aggregate `decision = accept`, evidence refs, test
counts, a global render hash, a global transcription hash or a general statement
of visual review cannot create, repair or replace a missing/rejected row.

No block receives `eligible_for_order_boundary_proof`, and no boundary
contributes to `paragraph_adjacencies_complete`, unless its own decision-specific
cross-check passes. `visible_transcription_sha256` in the witness is only a
claim: it must equal the digest of the independently recorded literal
transcription bytes and all render/component checks above. Hash-only
transcription is never proof evidence.

## 5. Corrected acceptance and fail-closed states

A public proof candidate can exist only when, in order:

1. primitive ingress types are valid;
2. the literal two-column and nested-Form Stage A coverage inventory is complete
   and independently accepted;
3. the exact fixture admission row binds that inventory, Stage A authority,
   witness, render and independent cross-check;
4. every block's flow disposition/reason is mechanically derived and the
   included/excluded partition is exact;
5. fragment and adjacency universes are mechanically derived exactly;
6. every per-block and per-boundary independent visual cross-check replays and
   confirms its exact decision/reason with actual transcription bytes;
7. all original conservation, geometry, order, visibility, text-layer and hash
   rules pass.

Only then may derive return `fixture_candidate_review_required`. Only a valid
aggregate review that binds all corrected digests may produce
`fixture_proof_accepted_no_source_use` or
`fixture_proof_rejected_no_source_use`. These states remain fixture-only and
authorize neither implementation acceptance by themselves nor live/source use.

The corrected required errors are:

- `page_proof_stage_a_fixture_coverage_incomplete` for every public
  derive/review/replay path while the literal required inventory is incomplete;
- `page_proof_flow_disposition_invalid` for block derivation mismatch;
- `page_proof_reading_flow_partition_invalid` for non-exact inclusion/exclusion;
- `page_proof_visual_crosscheck_invalid` for root/admission/independence/binding
  failures;
- `page_proof_visual_block_crosscheck_failed` for any block-row failure;
- `page_proof_visual_boundary_crosscheck_failed` for any boundary-row failure;
- `page_proof_mechanics_attestation_forbidden` only after topology coverage is
  complete and a mechanics result is incorrectly offered for attestation.

Failure returns no proof-like object, partial ledger, plaintext, mutable nested
dict or reconstructed prose. Exact replay must repeat all admission, coverage,
flow, universe and visual checks before constant-time byte comparison.

## 6. Correction-specific adversarial requirements

Implementation review must reject the candidate unless target-only malformed
surrogates and target-only repairs demonstrate all of:

- missing/unknown/mismatched block flow field or reason;
- status-axis combination not covered by the total derivation table;
- included block listed as excluded, excluded block omitted, duplicate block or
  substituted exclusion reason/digest;
- fragment from an excluded block, shuffled fragment universe, missing/extra/
  non-adjacent boundary or changed adjacency digest;
- missing two-column inventory entry, missing nested-Form entry, fake acceptance
  receipt, changed reviewed authority hash, swapped topology id, rehashed
  insufficient fixture and cross-pair inventory substitution; every public
  derive/review/replay call must produce the exact coverage error;
- mechanics result cast/serialized/reviewed as a proof candidate;
- missing/duplicate/reordered block or boundary visual-check row;
- region pixel, component mask/bbox, witness-decision, pre-visual-core,
  transcription bytes/hash, independent status/order/boundary decision,
  reason code or decision-specific digest changed one at a time;
- aggregate review marked `accept` with one row missing/rejected or only a global
  transcription/render hash.

Each malformed artifact must be valid in every non-target respect. Repairing
only the targeted defect, resealing and replaying must pass the full corrected
contract. No test may read a live Innsmouth path or invoke a PDF parser.

## 7. Preserved prohibitions and non-goals

- No live Innsmouth PDF/source/EN/Keeper/HTML/PDF/config/output read, processing,
  rendering, mutation or derived artifact generation.
- No code or test implementation in this step.
- No edit to the original Sol specification, canonical plan/context/status,
  project/release files or `source_reconstruction.py`.
- No generic/alternate PDF parser, OCR, source text reconstruction,
  normalization, translation, correction or semantic-role inference.
- No live preflight authorization, live consumer switch, source-repair
  admission, rebuild, publication, release acceptance, Git or network action.
- No substitution of aggregate review for independent row-level visual evidence.
- No relaxation of visibility/occlusion/decorative/text-layer non-publication
  states from the original specification.
- No orchestration transfer; this is a bounded Sol architecture correction.

## Immutable handoff receipt

- Result: completed a normative replacement for exactly the three rejected P1 contract areas: deterministic reading-flow/adjacency, non-bypassable Stage A topology coverage, and replayable independent per-block/per-boundary visual cross-check evidence; no implementation or live/source action authorized.
- Scope: step `3a` specification correction only; all original no-live/no-source/no-rebuild/no-parser boundaries preserved.
- Paths checked: `kb_creator/docs/plans/20260809-innsmouth-page-level-consumer-proof/plan.md`; `kb_creator/docs/plans/20260809-innsmouth-page-level-consumer-proof/handoffs/sol_page_level_consumer_proof_spec_20260809.md`; `kb_creator/docs/plans/20260809-innsmouth-page-level-consumer-proof/handoffs/terra_page_level_consumer_proof_architecture_review_20260809.md`.
- Files changed: `kb_creator/docs/plans/20260809-innsmouth-page-level-consumer-proof/handoffs/sol_page_level_consumer_proof_p1_correction_20260809.md` only.
- Evidence: current plan SHA-256 `DF75393007D94AB1EF5A0AFE91EBB09485BD88A17A9BC14F978EF4E64BBB4B8A`; original Sol specification SHA-256 `44EF02B7BDFBA240733BBEDF6F4018313C32F6E312E48CAAEAFCE7FFC2E6DD24`; Terra rejection SHA-256 `1E8EF003B7D58CB67B78CD365C0E2AF1E9042BEC0D1F07D1E77C5928B99BF7DB`; correction maps directly to Terra P1 findings 1-3 and the minimal correction packet.
- Verification/evidence: document-only static contract review against all four correction requirements; required flow fields/reasons, exact adjacency derivation, topology error on all three public paths, non-attestable mechanics state, row-level visual artifact schemas/digests/reverification and preserved prohibitions are explicitly stated; no tests run because implementation is forbidden.
- Blockers: no blocker to independent Terra re-review; fixture implementation remains prohibited pending acceptance, and all public proof paths remain normatively blocked until literal independently accepted Stage A two-column and nested-Form topology inventory entries exist.
- Next action: orchestrator requests an independent Terra architecture re-review of this immutable correction together with the unchanged original specification; only acceptance may permit a separately bounded implementation packet.
- Elapsed active time: approximately 8 minutes.
- Token use: unavailable.
- Timestamp: `2026-08-09T20:34:30.9234638+03:00`.
- Orchestrator policy owner: `gpt-5.5` medium (platform-unverified); orchestration ownership remains with the main-chat orchestrator.
- Role/model/effort: Sol architect / model platform-unverified / high.
- Assignment state: `platform-unverified`.
- Scoped override: `none`.

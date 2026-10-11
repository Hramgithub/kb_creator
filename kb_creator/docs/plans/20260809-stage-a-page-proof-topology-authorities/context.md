# Context: Stage A Page-Proof Topology Authorities

The accepted page-proof architecture requires two independently accepted raw
Stage A fixture authorities before its public derive/review/replay APIs may
progress beyond `page_proof_stage_a_fixture_coverage_incomplete`.

Required topology ids are exact:

1. `stage_a_positive_two_column.v1`: at least two content blocks with explicit
   left/right membership and a non-trivial cross-column reading transition.
2. `stage_a_positive_nested_form.v1`: an explicit parent/child Form invocation,
   child atoms and glyphs, correct invocation-token linkage and paint order.

This is a synthetic fixture-authority task. It does not open the source PDF or
validate real Innsmouth pages. Only after independent acceptance will the
separate page-proof consumer bundle be allowed to replace its coverage guard
with literal inventory validation.

## Sol Specification Received

Sol delivered the fixture-only authority specification at
`handoffs/sol_stage_a_page_proof_topology_authorities_spec_20260809.md`,
SHA-256 `23ECCF5ED32998D55EB0DBBCF73B2987FFA4D14DC0BEDD40361B7DE274EAB630`.
It explicitly limits Stage A to raw provenance, frame/invocation and paint
order. Candidate column slots and nested Form structure must not become claims
about geometry, visibility, semantic blocks or reading order.

Independent Terra architecture review is active. No fixture code is authorized
until that review accepts the contract.

## Architecture Accepted; Fixture Implementation Authorized

Independent Terra accepted the raw-provenance-only topology contract in
`handoffs/terra_stage_a_page_proof_topology_authorities_architecture_review_20260809.md`.
The only allowed implementation now adds exactly the two synthetic Stage A
fixtures/assertions and their target-only tests within `raw_authority_projection.py`
and the approved fixture-only test surface. `page_capable.py`, `page_proof.py`,
all live material and all publication paths remain forbidden.

## Implementation Recovery: Split the Scope

The first engineering pass returned only verified baseline evidence
(`369 passed, 1 skipped`) and made no permitted code/test changes. The four-row
registry plus two complete adversarial matrices was too broad for one bounded
implementation packet. Per recovery policy, the same fixture-only work is
restarted in smaller steps: first the two-column authority alone, then the
nested-Form authority after independent review of the first addition.

This changes no technical boundary: both steps remain synthetic Stage A work
and cannot read live Innsmouth material or change page-proof/publication paths.

## Two-Column Authority Submitted For Independent Review

The bounded two-column slice adds one synthetic fixture with two root streams
and raw `A,B,C,D` paint order. Its focused replay/contract suite is `12 passed`.
The new authority declares only fixture slots and the `B -> C` paint transition;
every Stage A atom retains `unavailable_stage_a` geometry, visibility and
semantic-role fields.

Independent Terra must still check literal-pinning fidelity and whether the
negative cases exercise their intended topology failures rather than stale
hashes. Nested Form remains pending and is not authorized by this submission.

## Two-Column Review: Remediation Required

Terra confirmed the actual `A,B,C,D` raw frame/paint topology, baseline
preservation and absence of geometry/reading claims. It rejected acceptance for
two P1 proof defects: the topology assertion is regenerated from the candidate
rather than retained as a literal canonical leaf, and the negative suite calls
a narrow validator rather than a fully resealed replay path.

The recovery is limited to those P1s. Nested Form, page-proof inventory and all
live/publication paths remain forbidden.

## Two-Column Authority Accepted

The P1 remediation now retains `_TWO_COLUMN_ASSERTION_RAW` as a literal
canonical authority leaf, with literal length, raw SHA-256, facts SHA-256 and
assertion-content SHA-256. The independent critic accepted the corrected
negative pattern: an otherwise valid artifact is checked through full replay
validation against a private, resealed but different expected assertion and is
rejected; restoring the accepted row passes the same validation path.

Evidence: `handoffs/terra_stage_a_two_column_authority_literal_rereview_20260809.md`.
Focused QA: `13 passed`; wider Stage A adversarial/containment/topology QA:
`372 passed, 1 skipped`. This accepts only the two-column synthetic raw
provenance fixture. The nested-Form authority is the sole remaining Stage A
topology fixture before the page-proof coverage guard may become a literal
inventory check.

## Nested-Form Recovery Takeover

The assigned Terra engineer returned twice without an implementation artifact:
first from an obsolete concurrency snapshot, then after checkpoint restart with
no code, tests or receipt. Per the NRI restart-before-takeover rule, the
orchestrator now owns only the shared-fixture recovery for step `3b`. The next
operation is a local inspection of the existing `page_capable` Form-record
contract before any code is changed. This remains fixture-only and cannot touch
live Innsmouth, page-proof, configuration or publication paths.

Sol then supplied the minimal nested-Form adapter clarification at
`handoffs/sol_nested_form_minimal_adapter_clarification_20260809.md`, SHA-256
`25C6803DBF377B71EF1EFB63C5DA4D1114C644DBB513B2EAAEC3A220747D0E29`.
It confirms that the existing bytes-only `page_capable` extractor already
emits the necessary Form source facts. The allowed change is therefore a
fixture-gated `font | form` source adapter and a nested-only validator in
`raw_authority_projection.py`; it must preserve all baseline/two-column
validators and never expose `effective_ctm` in Stage A output.

The first adapter slice is implemented and tested only in isolation. Its
canonical nested PDF has `1463` bytes and SHA-256
`1e6b3313c74fb3275e0a6413cbc5d5733b79cd0642a08069686e47d3cddbee1d`;
the existing bytes-only extractor reports `7/3/3/5/2/7/5` for
objects/streams/frames/resolutions/invocations/atoms/glyphs and exact raw
event order `P, OuterDo, C, InnerDo, N, D, Q`. The adapter strips CTM from all
nested atoms/invocations, sets root-stream ordinals `[0, null, null]`, and
normalizes Form resolutions/invocations into the closed existing wire keys.
Focused QA is `9 passed`; wider Stage A QA is `373 passed, 1 skipped`.
No nested fixture has been admitted to the registry yet: exact validator,
literal row/inventory/content seals and independent review remain required.

## Nested-Form Candidate Submitted For Independent Review

The bounded recovery now admits exactly
`stage-a.positive-nested-form.v1` as the fourth immutable registry row. Its
PDF, authority inventory/content and canonical topology assertion are pinned
by literal lengths and SHA-256 identities. The assertion verifies only Form
frame lineage, invocation-token/resource linkage, depth-first raw paint
sequence `P, OuterDo, C, InnerDo, N, D, Q`, and glyph continuity. It retains
the same explicit Stage A claim boundary: geometry, visibility, semantic
blocks and reading order are all unavailable.

Focused QA is `15 passed`; wider adversarial/containment/topology QA is
`379 passed, 1 skipped`. The new tests prove normal project/replay,
target-only nested topology rejections, a private fully resealed but different
assertion rejection, and successful replay after restoring the accepted row.
This is a candidate only. It must receive a new independent Terra review
before step 3b or Stage A may be accepted.

## Nested-Form Review: P1 Remediated, Re-review Pending

Terra rejected the first candidate receipt
`handoffs/terra_stage_a_nested_form_implementation_review_20260809.md`:
the four named nested topology negatives changed artifact fields but did not
reseal their changed rows, so a stale seal could fail before the intended
hierarchy/invocation/paint/glyph predicate.

The correction now starts each case from a valid nested artifact, changes one
declared topology fact, reseals the changed frame/invocation/atom/glyph rows,
updates any dependent glyph atom reference, recomputes inventory/content, and
uses the private matching expected row through
`_validate_artifact(..., replay=True)`. Restoring the accepted artifact/row
passes the same full path. Focused `15 passed`; wider `379 passed, 1 skipped`.
The correction is submitted for fresh independent review; neither Stage A nor
the consumer/page-proof boundary is accepted yet.

## Stage A Authority Bundle Accepted

Independent Terra accepted the nested-Form correction in
handoffs/terra_stage_a_nested_form_implementation_review_20260809.md.
Together with the earlier two-column acceptance, Stage A now has both required
synthetic, raw-only authority topologies:

1. stage-a.positive-two-column.v1;
2. stage-a.positive-nested-form.v1.

Their fixture bytes, bindings, inventories, content identities and topology
assertion leaves are pinned in the four-row registry. The accepted scope remains
strictly raw provenance, frame/invocation/resource linkage and paint evidence:
it neither proves nor consumes geometry, visual visibility, semantic blocks or
reading order. This acceptance authorizes only the separate page-proof bundle's
bounded fixture-only consumer implementation; it does not authorize live
Innsmouth input, source reconstruction, output generation or a rebuild.

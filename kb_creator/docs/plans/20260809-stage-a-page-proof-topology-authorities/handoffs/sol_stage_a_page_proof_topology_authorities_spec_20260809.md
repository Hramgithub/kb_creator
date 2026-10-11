# Sol Architecture Specification — Stage A Page-Proof Topology Authorities

- Goal id: `20260809-stage-a-page-proof-topology-authorities`
- Step id: `1`
- Role/effort: Sol architect / high
- Contract status: implementation-ready fixture-only specification; it does not implement or accept either authority.
- Orchestrator policy owner: `gpt-5.5` medium (platform-unverified). Orchestration ownership remains in the main chat.

## 1. Result and controlling invariant

Implement exactly two additional synthetic `RawAtomProvenanceAuthorityV1`
fixtures, with topology ids in this exact order:

```text
(
  "stage_a_positive_two_column.v1",
  "stage_a_positive_nested_form.v1",
)
```

Their authority schema and terminal state remain exactly:

```text
kb_creator.pdf_raw.RawAtomProvenanceAuthority.v1
provenance_complete_no_consumer
```

Stage A may prove only admitted raw-byte identity, object/stream/token spans and
digests, frame and invocation identity, resource linkage, atom/glyph identity,
and exact interpreter execution/paint-event order. It must continue to emit
`geometry = visibility = semantic_role = "unavailable_stage_a"` for every
atom. It may not infer or claim page geometry, rendered visibility, semantic
blocks, actual left/right placement, paragraph structure or reading order.

For the two-column fixture, `left_fixture_slot` and `right_fixture_slot` are
literal construction roles attached to two distinct root content streams. They
are Stage A column *candidates*, not geometric columns. The accepted Stage A
assertion proves a non-trivial transition in raw paint order from the last atom
of the first slot to the first atom of the second slot. A later page witness and
independent visual review must establish that the candidates are actually
visible left/right columns and that this transition is the intended reading
transition.

For the nested-Form fixture, Stage A proves the depth-first invocation and
paint-event topology, including parent text before and after the child
invocation, nested child continuity and exact glyph ownership. It does not
prove where any glyph appears or whether it is visible.

## 2. Dependencies, branches and current remediation point

The allowed dependency chain is:

```text
literal synthetic PDF/profile/selector/id leaves
  -> existing bytes-only RawPdfDocument/page_capable fixture replay
  -> Stage A fixture-scoped normalization
  -> sealed RawAtomProvenanceAuthorityV1
  -> literal positive-topology assertion
  -> independent Terra fixture_topology_acceptance receipt
  -> later literal page-proof topology inventory entry
```

No edge may lead to `page_proof.py`, a page witness, a render, source
reconstruction, live Innsmouth material, configuration or output.

Current evidence identifies four implementation blockers inside Stage A, not
inside the raw extractor:

1. `_registry_check()` requires exactly two fixtures.
2. `_validate_artifact()` pins one stream/frame/resolution/atom/glyph and zero
   invocations.
3. `_validate_rows()` accepts only `text_show`/`Tj`, literal glyph `A`, font ref
   `[8,0]` and `code_index = 0`.
4. the extractor's Form records use `frame_id`, `form_ref`,
   `operator_token_ordinal` and `operator_token_id`, while the Stage A wire row
   expects `target_frame_id`, `token_id` and the existing font-shaped
   resolution keys.

The bounded remediation belongs in `raw_authority_projection.py`: preserve the
two already accepted authority bytes exactly, add two literal rows, normalize
the extractor's existing Form facts into the existing Stage A row vocabulary,
and validate each fixture against its literal expected topology. No change to
`page_capable.py` is required by this specification.

## 3. Literal admission registry and independent expected tuple

### 3.1 Registry shape

`_FIXTURES` remains a code-owned immutable tuple and becomes exactly four rows:

```text
stage-a.identity-single-use.v1
stage-a.flate-single-use.v1
stage-a.positive-two-column.v1
stage-a.positive-nested-form.v1
```

The first two rows, their leaves, existing bindings and expected authority
hashes must remain byte-for-byte unchanged.

Each `_FixtureRow` must carry literal values for:

```text
fixture_id, pdf, profile, selector
fixture_id_length, pdf_length, profile_length, selector_length
fixture_id_sha256, pdf_sha256, profile_sha256, selector_sha256
binding_sha256
topology_id_or_none
positive_topology_assertion_raw
positive_topology_assertion_length
positive_topology_assertion_raw_sha256
positive_topology_assertion_sha256
expected_counts_tuple
expected_row_seal_tuple
expected_inventory_sha256
expected_content_sha256
```

For the two old rows, topology id is `None`, assertion bytes are `b""`, length
is zero, assertion raw hash is SHA-256 of empty bytes, topology assertion hash
is the all-zero sentinel, and their existing authority seals remain unchanged.
For each new row, every field is a literal. No value may be read from disk,
environment, configuration, test parameters or a callback.

`binding_sha256` remains the existing four-leaf binding. The separately sealed
topology assertion binds that leaf binding and the projected authority hashes;
including the assertion hash in the four-leaf binding would create a cycle and
is forbidden.

### 3.2 Second independent expected tuple

Add one primitive `_EXPECTED_FIXTURE_SET` tuple that duplicates all four rows,
all leaf bytes, all lengths/hashes/bindings, all assertion bytes/hashes and all
expected row/inventory/content seals literally. It must not be produced by
`_fixture_tuple`, `_FIXTURES`, a comprehension, `dataclasses.fields`, a helper,
JSON decoding or import-time projection.

`_registry_check()` must require exact type, count, order and primitive equality
between `_FIXTURES` and `_EXPECTED_FIXTURE_SET` before admission or any PDF
operation. It must then independently recompute every leaf length/hash and
binding, canonical assertion encoding and assertion hashes. Duplicate fixture
ids or duplicate non-null topology ids fail with
`raw_interpreter_fixture_registry_invalid`.

This is the anti-mutable-registry control. A fully rehashed row substitution,
row reversal, cross-pairing a PDF with another assertion, or monkeypatching both
derived expectations must still fail before `RawPdfDocument.open` or
`extract_raw_pdf_page_atoms`.

## 4. Exact synthetic fixture leaves

All dictionaries and streams below are literal test-only PDF bytes. The xref,
object offsets, `/Length`, `startxref` and trailer are exact parts of each
committed byte literal, not built at runtime. Both use the current literal
`_PROFILE` and `_SELECTOR`; selector remains page `3 0 R`, route
`[[2,0],[3,0]]`. Font object `8 0 R` remains the current Type1 WinAnsi font with
`FirstChar 32`, `LastChar 128` and 97 literal width entries of `500`.

### 4.1 `stage_a_positive_two_column.v1`

Fixture id: `stage-a.positive-two-column.v1`.

Object topology:

```text
1 0 Catalog -> Pages 2 0 R
2 0 Pages   -> Kids [3 0 R]
3 0 Page    -> Resources /Font /F 8 0 R
               Contents [5 0 R 6 0 R] in this exact lexical order
5 0 identity stream -> left_fixture_slot
6 0 identity stream -> right_fixture_slot
8 0 Type1 WinAnsi font
```

Exact decoded stream payloads:

```text
5 0: BT /F 10 Tf (A) Tj (B) Tj ET\n
6 0: BT /F 10 Tf (C) Tj (D) Tj ET\n
```

No `Tm`, `Td`, `cm`, BBox, coordinate, block or reading-order claim is part of
this fixture. This is intentional: the two slot labels come only from the
literal root-stream identities and assertion, not from interpreted geometry.

Expected authority cardinality is exact:

```text
object_count=6, stream_count=2, token_count=18, frame_count=2,
resolution_count=2, invocation_count=0, atom_count=4, glyph_count=4
```

The exact atom/glyph execution order is `A, B, C, D`. The left slot owns the
first two text atoms/glyphs in frame/root stream `5:0`; the right slot owns the
last two in frame/root stream `6:0`. The required non-trivial transition is
`B -> C`, atom ordinals `1 -> 2`. Both sides have two non-empty text atoms, so a
single-atom fixture cannot satisfy this assertion.

What Stage A proves: distinct admitted root streams, distinct root frames,
their literal slot assignment, exact token/atom/glyph provenance and the
`B -> C` raw paint transition. What later page proof must witness/review:
actual left/right geometry, visibility/content eligibility, block membership,
column direction and the semantic reading transition.

### 4.2 `stage_a_positive_nested_form.v1`

Fixture id: `stage-a.positive-nested-form.v1`.

Object topology:

```text
1 0 Catalog -> Pages 2 0 R
2 0 Pages   -> Kids [3 0 R]
3 0 Page    -> Resources: Font /F 8 0 R, XObject /Outer 7 0 R
               Contents 5 0 R
5 0 identity parent-page stream
7 0 Form /Outer -> explicit Resources: Font /F 8 0 R,
                   XObject /Inner 9 0 R
8 0 Type1 WinAnsi font
9 0 Form /Inner -> explicit Resources: Font /F 8 0 R
```

Exact decoded payloads:

```text
5 0: BT /F 10 Tf (P) Tj ET /Outer Do BT (Q) Tj ET\n
7 0: BT /F 10 Tf (C) Tj ET /Inner Do BT (D) Tj ET\n
9 0: BT /F 10 Tf (N) Tj ET\n
```

The second `BT` in parent and outer streams deliberately reuses the already
resolved frame-local font, avoiding duplicate font-resolution ids.

Expected authority cardinality is exact:

```text
object_count=7, stream_count=3, token_count=33, frame_count=3,
resolution_count=5, invocation_count=2, atom_count=7, glyph_count=5
```

The exact depth-first atom paint-event order is:

```text
0 parent text P
1 parent form_do Outer
2 outer child text C
3 outer child form_do Inner
4 inner child text N
5 outer child text D
6 parent text Q
```

The exact glyph order is `P, C, N, D, Q`. The root frame has no incoming
invocation; Outer has exactly one incoming invocation from the root; Inner has
exactly one incoming invocation from Outer. Parent continuity is `P` before the
Outer invocation and `Q` after all Outer descendants. Outer continuity is `C`
before the Inner invocation and `D` after all Inner descendants.

What Stage A proves: raw invocation tokens, resource target refs, distinct
frame ids and owners, parent/child edges, child atom/glyph ownership and exact
depth-first execution order. What later page proof must witness/review: effective
page geometry, visibility/occlusion and whether any event contributes to a
semantic/reading block.

## 5. Stage A normalization and validation contract

The public functions and wrapper remain unchanged:

```text
project_stage_a_raw_authority(fixture_id_raw, pdf_raw, profile_raw, selector_raw)
replay_stage_a_raw_authority(fixture_id_raw, pdf_raw, profile_raw, selector_raw,
                             artifact_raw)
RawAtomProvenanceAuthorityV1
```

No new public state, accessor, parser, topology consumer or page-proof entrypoint
is permitted.

### 5.1 Streams and frames

For root `/Contents`, `root_contents_ordinal` is the zero-based lexical index
in the page's `/Contents` array. For Form streams it is `null`. Existing single
root-stream authorities retain integer `0` and therefore retain exact bytes.

Frames are ordered when first entered by depth-first replay. Exactly one frame
is root for each root content stream; a Form frame must have one earlier parent
frame and exactly one incoming invocation. Multiple root frames are valid for
the two-column fixture. Thus the current global rule “exactly one null parent”
must become a literal per-fixture expected-root-frame count, not a relaxed
open-ended count.

### 5.2 Resolution closed union without changing existing rows

Keep the current resolution row key set. Validate two closed arms:

```text
font arm:
  font_size, first_char, last_char, widths_span are non-null current values;
  token_id is the Tf operator token; target is the admitted font.

form arm:
  font_size=null, first_char=null, last_char=null, widths_span=null;
  token_id is the Do operator token; target_ref is the invoked Form owner ref.
```

The projection adapter maps extractor `operator_token_id` to Stage A `token_id`
for the form arm. A form resolution must be owned by the parent frame, be used
by exactly one `form_do` atom, and match exactly one invocation. Existing font
rows and their seals must not change.

### 5.3 Invocation normalization

For each extractor invocation, normalize:

```text
invocation_id       = extractor invocation_id
parent_frame_id     = extractor parent_frame_id
target_frame_id     = extractor frame_id
token_id            = [parent frame owner stream_id,
                       extractor operator_token_ordinal]
```

Before sealing, require extractor `form_ref` equals the target frame
`owner_ref`; the matching form resolution has the same target ref and token;
and the matching parent `form_do` atom has the same operator token and
resolution id. Extractor `effective_ctm` is deliberately discarded and cannot
enter Stage A rows or topology assertions.

### 5.4 Atoms, glyphs and exact paint order

Permit only the fixture-needed atom arms:

```text
text_show: operator token raw bytes Tj; one or more glyph ids; font arm only
form_do:   operator token raw bytes Do; zero glyph ids; one form arm;
           exactly one matching invocation
```

Atom ordinal is the exact depth-first interpreter execution/paint-event ordinal
and must be contiguous. A child atom occurs immediately after its invoking
`form_do` event and before the parent's next event. Glyph rows remain globally
ordered by their owning atom ordinal and then contiguous `code_index`. A glyph's
code bytes must equal the indexed bytes of its literal/hex operand; decoded
UTF-8 must contain exactly one scalar equal to `unicode_scalar`; font ownership,
width span and width remain exact. Do not retain the current literal-`A`,
`code_index=0`, single-glyph or fixed-count assumptions.

Every atom, including `form_do`, retains:

```text
geometry="unavailable_stage_a"
visibility="unavailable_stage_a"
semantic_role="unavailable_stage_a"
```

## 6. Required row, inventory and content seals

Row sealing remains byte-for-byte compatible:

```text
row_id = sha256(
  b"stage-a.row-id.v1\0" + kind_ascii + b"\0" + canonical_json(unsigned_row)
)
row_sha256 = sha256(
  b"stage-a.row.v1\0" + kind_ascii + b"\0" +
  canonical_json(unsigned_row plus row_id)
)
```

`expected_row_seal_tuple` is literal and ordered exactly by group order
`objects, streams, tokens, frames, resolutions, invocations, atoms, glyphs`.
Each group entry contains the literal group name and an ordered tuple of
`(row_id, row_sha256)`. Validation requires exact count, ordinal and equality;
it may not rebuild the expected tuple from the artifact or registry.

The inventory is unchanged:

```text
{
  "counts": exact counts object,
  "objects_row_sha256": [...],
  "streams_row_sha256": [...],
  "tokens_row_sha256": [...],
  "frames_row_sha256": [...],
  "resolutions_row_sha256": [...],
  "invocations_row_sha256": [...],
  "atoms_row_sha256": [...],
  "glyphs_row_sha256": [...]
}
inventory_sha256 = sha256(canonical_json(inventory))
content_sha256 = sha256(canonical_json(authority root excluding content_sha256))
```

The implementation receipt must report the actual 64-lowercase-hex values for
every new leaf, every group row-seal tuple digest, both authority inventory and
content hashes, both topology assertion hashes and both assertion content
hashes. Placeholder hashes, import-time generated pins or values copied from a
mutable artifact are not admissible.

## 7. Positive topology assertion and eventual inventory contract

### 7.1 Closed assertion root

Each new registry row contains canonical UTF-8 JSON bytes with this exact root:

```text
schema: "kb_creator.pdf_raw.PositiveStageATopologyAssertion.v1"
topology_id
stage_a_fixture_id
stage_a_fixture_binding_sha256
stage_a_authority_schema
stage_a_authority_terminal_state
stage_a_authority_inventory_sha256
stage_a_authority_content_sha256
facts
positive_topology_assertion_sha256
content_sha256
```

`positive_topology_assertion_sha256` is exactly:

```text
sha256(
  b"stage-a.positive-topology-facts.v1\0" + canonical_json(facts)
)
```

`content_sha256` is SHA-256 of the canonical complete root excluding only
`content_sha256`. `positive_topology_assertion_raw_sha256` in the registry is
SHA-256 of the complete canonical assertion bytes. These three hashes are
distinct and all literal.

### 7.2 Two-column facts schema

`facts` has exactly:

```text
fact_kind: "two_column_candidate_paint_topology"
slot_rows: exactly two rows in left, right order
paint_order_atom_row_ids
paint_order_glyph_row_ids
cross_slot_transition
stage_a_claim_boundary
```

Each slot row has exactly:

```text
slot: "left_fixture_slot" | "right_fixture_slot"
root_contents_ordinal
stream_id, stream_row_id, stream_row_sha256
frame_id, frame_row_id, frame_row_sha256
atom_row_ids: exactly two text_show atom row ids
glyph_row_ids: exactly two owned glyph row ids
```

`cross_slot_transition` has exactly `from_slot`, `to_slot`,
`from_atom_row_id`, `from_glyph_row_id`, `to_atom_row_id`, `to_glyph_row_id`,
`from_atom_ordinal=1`, `to_atom_ordinal=2`,
`minimum_text_atoms_per_slot=2`, and
`transition_kind="raw_paint_transition_requires_page_witness"`.

`stage_a_claim_boundary` is exactly:

```text
{
  "geometry":"not_proved_stage_a",
  "visibility":"not_proved_stage_a",
  "semantic_blocks":"not_proved_stage_a",
  "reading_order":"not_proved_stage_a"
}
```

### 7.3 Nested-Form facts schema

`facts` has exactly:

```text
fact_kind: "nested_form_invocation_paint_topology"
frame_rows: root, outer, inner in depth-first entry order
invocation_rows: outer, inner in invocation order
paint_event_rows: seven exact rows
glyph_continuity_rows: five exact rows
continuity_constraints
stage_a_claim_boundary
```

Each frame row binds frame id/row id/row hash, owner ref/stream id, parent frame
id or null and incoming invocation id or null. Each invocation row binds
invocation id/row id/row hash, parent/target frame ids, token id and token row
id/hash, matching form-resolution id/row id/hash and target ref.

Each paint-event row binds contiguous `paint_ordinal`, atom id/row id/row hash,
frame id, `operator_kind`, operator token id and the exact ordered glyph row ids.
The literal event labels/order are `parent_P`, `outer_Do`, `outer_C`,
`inner_Do`, `inner_N`, `outer_D`, `parent_Q`. Glyph continuity rows bind
`P,C,N,D,Q` to event ordinals `0,2,4,5,6`, including glyph id/row id/hash,
atom row id, code token id/index and scalar UTF-8 bytes.

`continuity_constraints` is exactly:

```text
{
  "root_incoming_invocation_count":0,
  "outer_incoming_invocation_count":1,
  "inner_incoming_invocation_count":1,
  "outer_descendant_interval":[2,5],
  "inner_descendant_interval":[4,4],
  "parent_before_after_event_ordinals":[0,6],
  "outer_before_after_event_ordinals":[2,5],
  "depth_first_paint_order_required":true
}
```

`stage_a_claim_boundary` is the same exact four-field object as section 7.2.

### 7.4 Exact eventual page-proof inventory mapping

After independent acceptance, and only in a later bundle, each assertion maps
one-for-one to the already accepted
`PageProofRequiredStageATopologyInventory.v1` entry:

```text
topology_id
stage_a_fixture_id
stage_a_authority_schema
stage_a_authority_content_sha256
stage_a_authority_inventory_sha256
stage_a_fixture_binding_sha256
positive_topology_assertion_sha256
independent_stage_a_review_kind="fixture_topology_acceptance"
independent_stage_a_review_decision="accept"
independent_stage_a_review_content_sha256
reviewed_authority_content_sha256
entry_sha256
```

`positive_topology_assertion_sha256` is the facts hash from section 7.1, not the
assertion raw hash or assertion content hash.

```text
entry_sha256 = sha256(
  b"page-proof.stage-a-topology-entry.v1\0" +
  canonical_json(entry excluding entry_sha256)
)
```

The eventual inventory root contains the exact required topology-id tuple, the
two entries in that order, `entry_count=2`, `inventory_sha256` over the ordered
entry hashes/count/id tuple, and `content_sha256` over the root excluding only
itself. This specification defines the future literal values but does not edit
or unblock `page_proof.py`.

## 8. Minimal positive proof and target-only adversarial matrix

Every negative must be valid in all non-target invariants. Tests must use a
private surrogate expected-seal row so final literal pins do not mask the
semantic failure. Repairing only the named target, resealing rows/inventory/root
and rebuilding the literal surrogate expectation must pass full internal
validation. Public replay of the malformed artifact must still fail before
open/extract with `raw_interpreter_authority_blocked`.

### 8.1 Positive proof

For each new fixture prove:

1. exact four-leaf admission and registry/independent-tuple equality precede
   every raw operation;
2. projection and replay produce byte-identical canonical authority bytes;
3. exact counts, all row seal tuples, inventory/content hashes and topology
   assertion hashes match literals;
4. the assertion independently joins literal rows rather than restating a
   derived registry;
5. all atom Stage A claim fields remain unavailable;
6. filesystem/network/subprocess/config/page-proof/source APIs remain
   unreachable.

### 8.2 Two-column target matrix

| Target-only case | Otherwise-valid malformed fixture/artifact | Only repair |
| --- | --- | --- |
| insufficient left slot | valid PDF with only `(A) Tj` in stream 5 and two right atoms | restore `(B) Tj` and expected seals |
| insufficient right slot | valid PDF with one right atom | restore `(D) Tj` |
| reversed slot transition | valid PDF `/Contents [6 0 R 5 0 R]` with both streams intact | restore lexical contents order |
| same stream/frame in both slots | fully sealed assertion points both slot rows to one valid stream/frame | restore right ids only |
| dropped/duplicated membership | fully sealed assertion omits or duplicates one atom/glyph while authority remains valid | restore exact one-to-one membership |
| wrong transition endpoint | transition is `A -> C`, `B -> D` or `C -> B` | restore exact `B -> C` endpoints/ordinals |
| paint order substitution | fully resealed valid authority swaps two text atom rows and dependent glyph ownership | restore exact raw execution order |
| geometry/reading-order smuggling | assertion adds a bbox, x/y fact, visibility, block or `reading_order=accepted` field | remove the extra claim and restore exact closed boundary |

The first three are malformed for this topology but otherwise valid raw PDFs.
They demonstrate that parser success is not topology acceptance.

### 8.3 Nested-Form target matrix

| Target-only case | Otherwise-valid malformed fixture/artifact | Only repair |
| --- | --- | --- |
| only one Form level | valid parent->Outer PDF with Inner removed and remaining rows consistent | restore Inner invocation/stream/frame/event |
| child has no text/glyph | valid nested Form whose Inner payload is empty | restore `(N) Tj` |
| invocation token mismatch | invocation points to another existing parent token | restore exact Do token id |
| target owner mismatch | target frame owner ref differs from matching form resolution target ref | restore owner ref |
| parent edge mismatch | child frame parent differs from invocation parent | restore parent id |
| duplicate incoming edge | two valid-looking invocations target the same child frame | remove only duplicate edge |
| missing/extra `form_do` pairing | invocation exists without its event, or event without invocation | restore one-to-one pair |
| flattened paint order | child events moved after `parent_Q`, with all row/root seals refreshed | restore depth-first event order |
| child atom drop/duplicate | one child atom is omitted or owned twice | restore exact ownership once |
| glyph continuity break | `P,C,N,D,Q` glyph row is dropped, duplicated, reordered or attached to another child atom | restore exact glyph sequence/owner |
| recursive/cyclic Form | otherwise valid Form resource points back to an active ancestor | restore acyclic target; extractor must emit `raw_pdf_page_form_cycle_blocked` with no partial result |
| CTM/geometry smuggling | assertion includes extractor `effective_ctm`, polygon or bbox | remove it; Stage A assertion remains topology-only |

At least the one-level, empty-child and cycle cases use malformed-for-target but
otherwise valid synthetic PDFs. Link/order cases use fully resealed canonical
surrogates and target-only repair so rejection is not attributable merely to a
stale hash.

### 8.4 Registry/seal attacks required for both

Cover omission, insertion, duplicate id, row reversal, cross-paired assertion,
cross-paired authority hashes, altered expected row-seal tuple, fully rehashed
PDF leaf substitution, assertion unknown/missing field, facts reorder, assertion
raw/content/facts hash substitution and import-time derived expectation. Each
must fail at the earliest registry/assertion/semantic boundary; poison
`RawPdfDocument.open` and `extract_raw_pdf_page_atoms` to prove pre-operation
failure where applicable.

## 9. Test surface and containment

Implementation scope is limited to:

- `kb_creator/pdf_raw/raw_authority_projection.py`;
- a new focused fixture-only test such as
  `kb_creator/tests/test_raw_authority_projection_stage_a_topology_authorities.py`;
- only the minimal compatibility edits required in the existing assigned
  `test_raw_authority_projection_stage_a_*.py` tests.

`page_capable.py` is an inspected dependency, not an expected change. Its
existing bytes-only parser is sufficient for ordered multiple contents and
nested Form replay. The legacy `raw_interpreter_authority` registry remains
exactly two rows; update the current test that equates legacy and Stage A counts
to compare the legacy rows only with the two exact baseline Stage A ids. Do not
silently add the new positive fixtures to legacy authority.

The existing 176-case/349-collection adversarial matrix assumes the two
single-atom baseline fixtures. Keep that matrix explicitly bound to those two
literal ids; do not broaden it mechanically to the topology fixtures. Add the
focused target-only matrix in section 8 for the new fixtures. The ordinary
projection/replay contract test should cover all four Stage A rows.

Containment tests must prove:

- only exact `bytes` leaves enter the existing public API;
- no path, file-like object, glob, URL, arbitrary PDF, environment/config
  selector, callback, plugin or dynamic import is accepted;
- no filesystem read/write, network, subprocess, browser, OCR, PDF library,
  live parser or alternate parser is reached;
- no import/call edge to `page_proof.py`, `source_reconstruction.py`, live
  Innsmouth, EN, Keeper, HTML, PDF, config, reports or output;
- malformed replay is validated and rejected before projection/open/extract;
- `-B` and `-p no:cacheprovider` are used for focused QA so tests leave no
  bytecode or pytest cache artifact.

The allowed parser boundary is only the existing in-memory
`RawPdfDocument.open(literal_pdf_bytes)` plus
`extract_raw_pdf_page_atoms(literal_pdf_bytes, literal_selector,
literal_profile)` already used by Stage A. There is no filesystem/live/parser
escape beyond that machinery.

## 10. Independent Terra acceptance contract

Terra acts as an independent critic at high effort and must not have implemented
or materially designed the candidate. Terra accepts each topology only if the
receipt records `review_kind="fixture_topology_acceptance"`,
`decision="accept"`, and independently verifies:

1. the exact fixture id/topology id mapping and all literal leaf hashes;
2. the independent expected tuple is genuinely literal and rejects fully
   resealed cross-pair/reversal attacks before raw operations;
3. both old accepted Stage A authority bytes/hashes are unchanged;
4. the exact new row seal tuples, authority inventory/content hashes,
   assertion raw/facts/content hashes and cardinalities;
5. the two-column fixture has two distinct non-empty two-atom candidate slots
   and exact `B -> C` paint transition, while making no geometry or reading
   claim;
6. the nested fixture has root/Outer/Inner frames, two exact invocation-token/
   resolution joins, event order `P,OuterDo,C,InnerDo,N,D,Q` and glyph order
   `P,C,N,D,Q`;
7. every negative is target-only, its non-target invariants validate, and its
   target-only repair passes exact replay;
8. containment and no-live/no-consumer boundaries pass;
9. focused and aggregate Stage A test commands and exact results are recorded.

The acceptance receipt must list, for each topology, the accepted authority
content/inventory hash, fixture binding, positive topology assertion hash and
the receipt `content_sha256`. A general statement, plan row, self-review,
aggregate pass count, page-proof review, mutable hash dump or a weaker
single-atom/single-level fixture is not acceptance.

Terra must reject if either assertion calls candidate slots actual geometric
columns, treats paint order as semantic reading order, includes effective CTM or
coordinates, accepts a child without owned glyph evidence, derives expected
pins from the candidate under review, or changes any page-proof API/public
state. This is implementation acceptance, not a release review.

## 11. Assumptions, risks and controls

| Assumption/risk | Required control |
| --- | --- |
| Current raw extractor behavior remains the dependency | Pin checked code hash in the implementation receipt and rerun focused multi-content/nested-Form tests |
| Literal slot names could be mistaken for geometry | Use `fixture_slot` terminology and the exact four-field `not_proved_stage_a` boundary |
| Supporting Forms could weaken old single-atom validation | Use fixture-specific exact counts/topology assertions; preserve old authority bytes and baseline adversarial matrix |
| Form extractor/wire field mismatch could lead to invented data | Normalize only fields already present and require token/frame/resource joins before sealing; discard CTM |
| A topology assertion could merely echo the artifact | Store canonical literal assertion bytes plus independent literal expected tuple; use fully resealed target-only surrogates |
| A valid raw PDF could be topology-insufficient | Require topology assertion validation after raw structural validity; test one-atom, one-level and empty-child valid PDFs |
| Registry growth could mutate legacy authority | Keep legacy registry at two explicit ids and test exact separation |
| Event order could be promoted to reading order | Name it execution/paint-event order everywhere; page proof remains responsible for reading order |

## 12. Explicit non-proofs and prohibited scope

This work does **not** prove real page geometry, actual left/right placement,
rendered visibility, occlusion, semantic blocks, paragraph boundaries,
publication eligibility or reading order. It does not prove anything about a
real Innsmouth page.

It must not:

- read or write live source files, EN, Keeper, HTML, PDF, config, output,
  reports or generated artifacts;
- render, OCR, rebuild, publish, repair source, construct a page-proof candidate
  or alter a page-proof ledger/review;
- edit `page_proof.py`, its tests, public signatures or public proof states;
- edit `page_capable.py` unless a later separately reviewed blocker proves the
  proposed literal fixtures cannot use the already tested machinery;
- add a filesystem/live/generic/alternate parser route;
- edit canonical plan, context, project status or release files;
- make a release decision, commit, push or transfer orchestration ownership.

## 13. Implementation acceptance criteria

The bounded implementation is complete only when all are true:

1. exactly the two new fixture/topology ids exist in the exact registry order;
2. the second expected tuple is literal and independent, and all admission
   attacks fail before raw operations;
3. both exact synthetic leaves project and replay byte-for-byte;
4. authority counts and the `A,B,C,D` / `P,C,N,D,Q` facts match sections 4.1
   and 4.2;
5. all row, inventory, authority-content and assertion seals are literal,
   reported and independently recomputed;
6. two-column candidate slots and `B -> C` transition pass without any geometry
   or reading-order claim;
7. nested frame/invocation/token/resource joins, child continuity and exact
   paint-event order pass;
8. every section 8 negative fails for only its target and target-only repair
   passes;
9. old Stage A authorities are byte/hash stable, legacy remains two rows, and
   assigned focused/aggregate tests pass under no-cache/no-bytecode execution;
10. Terra independently accepts both exact authorities and assertion hashes;
11. no forbidden file, API, state or live/output path changed or was accessed.

Independent acceptance supplies identities for a later inventory update only.
It does not itself remove the current page-proof coverage guard.

## Immutable handoff receipt

- Scope: architecture/remediation specification for exactly two synthetic Stage A positive topology authorities; fixture-only, no implementation or acceptance performed.
- Result: complete implementation contract for literal leaves, Stage A normalization, exact topology assertions/hashes, row/inventory/content seals, adversarial QA, containment and independent acceptance.
- Files checked: `AGENTS.md`; `docs/governance/nri_goal_governance.md`; assigned `plan.md` and `context.md`; `sol_page_level_consumer_proof_spec_20260809.md`; `sol_page_level_consumer_proof_p1_correction_20260809.md`; `terra_page_proof_coverage_guard_signature_rereview_20260809.md`; `kb_creator/pdf_raw/raw_authority_projection.py`; `kb_creator/pdf_raw/page_capable.py`; all assigned `test_raw_authority_projection_stage_a_*.py`; `test_page_capable_raw_pdf_authority.py`.
- Files changed: `kb_creator/docs/plans/20260809-stage-a-page-proof-topology-authorities/handoffs/sol_stage_a_page_proof_topology_authorities_spec_20260809.md` only.
- Verification/evidence: static dependency/data-contract review; checked hashes `raw_authority_projection.py=8CE1CCF172C60CE63675E287061E688D2A0C39A80DE511263E851925A96B30A3`, `page_capable.py=15C8604F5293E1336F169CDB28EEC140404EC2612712B4A45E7E52756163A95E`; focused existing bytes-only parser evidence `3 passed in 0.04s` for ordered multi-Contents, nested Form inheritance and Form-frame replay. No live files or output were accessed.
- Blockers: none to independent Terra architecture review; implementation and eventual page-proof inventory admission remain pending independent acceptance.
- Next action: orchestrator assigns an independent Terra architecture review of this immutable specification; after acceptance, dispatch a bounded Stage A-only implementation packet.
- Elapsed active time: approximately 10 minutes.
- Token use: unavailable.
- Timestamp: `2026-08-09T21:03:32.1180257+03:00`.
- Orchestrator policy owner: `gpt-5.5` medium (platform-unverified); ownership remains with the main-chat orchestrator.
- Role/model/effort: Sol architect / model platform-unverified / high.
- Assignment state: `platform-unverified`.
- Scoped override: `none`.

This receipt does not transfer orchestration ownership.

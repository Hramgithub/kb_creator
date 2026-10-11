# Sol Architecture Specification — Fixture-Only Page-Level Consumer/Proof

- Goal id: `20260809-innsmouth-page-level-consumer-proof`
- Step id: `2`
- Contract status: proposed specification; implementation is not authorized by this receipt.
- Scope: a separately gated, fixture-only proof route that consumes the accepted
  Stage A raw authority and produces replayable page/block evidence. It cannot
  reconstruct source text, admit a live PDF, or promote evidence into source use.

## 1. Result and governing invariant

The required design is feasible only as a two-authority join:

1. the accepted `RawAtomProvenanceAuthorityV1` supplies sealed raw-byte,
   object/stream/token/frame/atom/glyph provenance and execution order; and
2. a separately sealed fixture page witness supplies the geometry, raster
   component, visibility, occlusion, decorative-status and text-layer comparison
   facts that Stage A deliberately does not claim.

The join must be conservative: every Stage A atom/glyph and every fixture raster
component is accounted for exactly once, reading order is an explicit reviewed
permutation rather than an implicit sort, and every paragraph adjacency has one
explicit boundary decision. Missing, duplicated, contradictory or unreviewed
evidence produces no usable proof object.

Stage A currently seals atom fields as `geometry = unavailable_stage_a`,
`visibility = unavailable_stage_a`, and `semantic_role = unavailable_stage_a`.
Consequently, a consumer that inferred page blocks from Stage A alone would make
an unsupported promotion. A consumer that reopened `pdf_raw` would become a new
PDF parser. Both are prohibited.

## 2. Dependencies and gates

The dependency chain is one-way:

`literal Stage A fixture leaves`
→ `RawAtomProvenanceAuthorityV1 (provenance_complete_no_consumer)`
→ `literal page-witness fixture + literal render fixture`
→ `candidate page/block ledger (review required)`
→ `independent review attestation`
→ `fixture proof accepted, no source use`.

There is no edge from this route to `source_reconstruction.py`, EN, KeeperBook,
HTML, PDF, configuration or output directories. A later live preflight and a
later source-repair admission are two additional gates described in sections 10
and 11; neither is implemented or authorized here.

### 2.1 Authoritative input

The only raw-content authority accepted by this contract is an opaque instance
of `RawAtomProvenanceAuthorityV1` returned by the Stage A projection/replay API.
The legacy `ValidatedRawInterpreterAuthority` and `PageCapableAuthority` are not
substitutable input types. The consumer may read the accepted authority's
canonical bytes only after checking its exact runtime type, fixture id, content
hash and terminal state against a literal consumer allowlist row.

### 2.2 Required prerequisite branch

The currently accepted Stage A fixtures prove only a minimal single-page,
single-text-atom topology; the accepted projection currently requires zero Form
invocations and marks geometry/visibility unavailable. Therefore:

- the first implementation may prove its mechanics against the current minimal
  fixtures, but it may not claim the complete adversarial matrix;
- complete implementation admission requires separately accepted Stage A
  fixture authorities for every positive topology needed by section 9,
  including nested Form and multi-block/two-column cases;
- if those authorities are absent, implementation must stop with
  `page_proof_stage_a_fixture_coverage_incomplete`;
- expanding Stage A fixtures mutates the previously reviewed authority boundary,
  invalidates its point-in-time review, and requires its own bounded review. It
  must not be hidden inside the page-consumer implementation.

## 3. Public API boundary

The future fixture-only module may expose exactly these conceptual operations
(names are normative; signatures may use repository typing conventions):

```text
derive_fixture_page_block_ledger_v1(
    validated_stage_a_authority,
    witness_raw: bytes,
    render_png_raw: bytes,
) -> PageBlockEvidenceCandidateV1

review_fixture_page_block_ledger_v1(
    candidate_raw: bytes,
    review_raw: bytes,
) -> ReviewedPageBlockEvidenceV1

replay_fixture_page_block_ledger_v1(
    validated_stage_a_authority,
    witness_raw: bytes,
    render_png_raw: bytes,
    review_raw: bytes,
    expected_ledger_raw: bytes,
) -> ReviewedPageBlockEvidenceV1
```

All byte inputs must be exact `bytes`, canonical UTF-8 JSON where applicable,
and admitted by an immutable literal tuple containing byte lengths, SHA-256
digests and a domain-separated binding digest. Admission must complete before
JSON decoding, PNG decoding, authority canonical-byte access, or any parser
call. Replay must recompute the ledger and use constant-time exact byte
comparison with `expected_ledger_raw`.

The module must not accept a path, file-like object, arbitrary PDF bytes,
configuration, environment selector, URL, page number by itself, callback,
plugin, or parser object. It must not import or call `RawPdfDocument`,
`extract_raw_pdf_page_atoms`, `_raw_replay`, `derive_page043_relation`, or any
source reconstruction API. No API may return reconstructed prose.

## 4. Input schemas

All schemas are closed: unknown, missing, duplicate or mistyped fields fail.
Decimal PDF coordinates are canonical decimal strings; pixel coordinates are
integers. Every JSON root is serialized with UTF-8, sorted keys and compact
separators. Every row has a deterministic domain-separated `row_id` and
`row_sha256`. Every root has `inventory_sha256` and `content_sha256`.

### 4.1 Literal admission row

`kb_creator.pdf_raw.PageProofFixtureAdmission.v1` is code-owned literal data,
not a runtime file or registry:

```text
fixture_id: ASCII bytes
fixture_id_byte_length: int > 0
fixture_id_sha256: sha256
stage_a_fixture_id: string
stage_a_authority_content_sha256: sha256
witness_byte_length: int > 0
witness_sha256: sha256
render_png_byte_length: int > 0
render_png_sha256: sha256
binding_sha256: sha256(domain, all preceding identities and lengths)
expected_candidate_sha256: sha256
expected_reviewed_ledger_sha256: sha256
```

The code must contain a second, independent literal expected tuple. Deriving the
expected tuple from a mutable registry is forbidden. Rehashing an unlisted row,
cross-pair substitution, duplicate fixture ids and partial leaf substitution
must fail before any authority or image operation.

### 4.2 `PageProofFixtureWitness.v1`

Closed root keys:

```text
schema
profile
fixture
source_identity
page_identity
render_identity
visual_components
atom_geometry
proposed_blocks
proposed_reading_order
proposed_paragraph_boundaries
text_layer_comparisons
inventory_sha256
content_sha256
```

`profile` must equal a single literal profile id and version. The profile pins
the PDF coordinate system, pixel coordinate system, affine-transform direction,
half-open bbox convention, polygon convention, PNG decoder, component
connectivity, alpha/background rules, overlap thresholds and all enums used by
this specification. No configurable thresholds are allowed at runtime.

`fixture` contains the admission schema/id/binding hash.

`source_identity`:

```text
identity_kind: "sealed_fixture"
stage_a_fixture_id: string
stage_a_authority_schema: "kb_creator.pdf_raw.RawAtomProvenanceAuthority.v1"
stage_a_authority_content_sha256: sha256
pdf_byte_length: int > 0
pdf_raw_sha256: sha256
fixture_binding_sha256: sha256
```

The PDF length/hash are copied from the validated authority binding. No PDF
bytes or path occur in the witness.

`page_identity`:

```text
page_index: int >= 0
page_ref: [object_number >= 0, generation >= 0]
page_tree_route: non-empty list of refs ending at page_ref
media_box_pdf: [x0, y0, x1, y1] canonical decimals with x0 < x1, y0 < y1
crop_box_pdf: same form and contained by media_box_pdf
rotation_degrees: one of 0, 90, 180, 270
coordinate_system: literal "pdf_user_y_up_rational.v1"
page_identity_sha256: sha256 over all preceding page fields
```

The index/ref/route must equal the Stage A authority page identity.

`render_identity`:

```text
render_png_byte_length: int > 0
render_png_sha256: sha256
renderer_id: non-empty fixed string
renderer_version: non-empty fixed string
png_width: int > 0
png_height: int > 0
pdf_to_px_affine: six canonical decimals
pixel_rule: literal half-open/pixel-center rule
component_profile_sha256: sha256
```

The supplied PNG must match length/hash exactly and decode under the literal
fixture profile. The affine must map crop-box corners into the declared pixel
bounds within the profile's exact rational tolerance; NaN, infinity, float
rounding and an uninvertible affine fail admission.

`visual_components[]`:

```text
component_id: deterministic id from render hash, mask hash and bbox
component_ordinal: contiguous int from 0
bbox_px: [left, top, right, bottom], half-open and in image bounds
pixel_count: int > 0
mask_rle_b64: canonical RLE bytes
mask_sha256: sha256
member_pixel_sha256: sha256
witness_class: "text_like" | "image_like" | "decorative_like" | "unknown"
row_id, row_sha256
```

The consumer re-derives connected components from the admitted PNG and requires
exact identity, order, mask and pixel conservation. `witness_class` is not a
publication decision.

`atom_geometry[]` has exactly one row per Stage A atom:

```text
atom_row_id: Stage A atom row id
stage_a_atom_ordinal: contiguous Stage A ordinal
frame_row_id: Stage A frame row id
paint_ordinal: contiguous page execution/paint ordinal
polygon_pdf: at least four canonical points, closed by convention
bbox_pdf: exact polygon envelope, within crop/media policy
projected_polygon_px: canonical projected points
bbox_px: exact projected envelope
geometry_status: "measured_fixture_witness" | "missing" | "malformed"
geometry_evidence_sha256: sha256
row_id, row_sha256
```

Only `measured_fixture_witness` is candidate-admissible. Geometry is witness
evidence joined to Stage A, never represented as Stage A-derived geometry.

`proposed_blocks[]` groups geometry, Stage A content and visual components:

```text
block_id: deterministic id
block_ordinal: contiguous inventory ordinal
mechanical_kind: "text" | "image" | "mixed" | "decoration" | "visual_only"
atom_row_ids: unique ordered Stage A atom ids
glyph_row_ids: unique ordered Stage A glyph ids
component_ids: unique ordered visual component ids
bbox_pdf: envelope of member atom geometry, or explicit visual-only projection
bbox_px: envelope of member components/geometry
line_fragments: ordered fragment rows
visibility_status: "visible" | "partially_occluded" | "fully_occluded" |
                   "not_rendered" | "visual_only" | "unresolved"
decoration_status: "content" | "decorative" | "unresolved"
text_layer_status: "agrees_visible" | "absent_for_visible_text" |
                   "text_layer_only" | "disagrees" | "not_applicable" |
                   "unresolved"
publication_status: "eligible_for_order_boundary_proof" |
                    "non_publication_occluded_recovery" |
                    "non_publication_text_layer_only" |
                    "non_publication_decorative" |
                    "non_publication_visual_only" | "blocked"
occlusion_evidence: null or closed object containing occluder atom/component ids,
                    overlap mask hash, covered pixel count, coverage ratio and
                    relative paint order
row_id, row_sha256
```

Each `line_fragment` contains `fragment_id`, ordered atom/glyph ids, derived
`text_utf8_b64`, `text_sha256`, `bbox_pdf`, `bbox_px`, `baseline_or_null`,
`fragment_ordinal`, `row_id` and `row_sha256`. Text is derived only by joining
Stage A glyphs in their sealed order; witness text is never copied into it.

`proposed_reading_order`:

```text
ordered_block_ids: all and only blocks with in_reading_flow=true
excluded_block_rows: every other block exactly once with block_id and reason
order_edges: exactly len(ordered_block_ids)-1 predecessor/successor rows
column_rows: column_id, ordered member block ids, bbox and direction
page_direction: literal supported direction (initially "ltr_top_to_bottom")
decision_basis: "fixture_geometry_plus_explicit_review"
```

No x/y sort is authoritative by itself. Columns, cross-column transitions and
exceptions are explicit evidence. Paint order and reading order remain distinct.

`proposed_paragraph_boundaries[]` has one row for every adjacent pair of
text-bearing fragments in accepted reading order:

```text
left_fragment_id, right_fragment_id
boundary_ordinal: contiguous int
decision: "same_paragraph" | "paragraph_break" | "column_break" |
          "section_break" | "not_applicable" | "unresolved"
geometry_cues: exact line gap, indent delta and column relation
text_cues: terminal punctuation/hyphenation flags derived from Stage A text
witness_reason_codes: non-empty closed enum list
row_id, row_sha256
```

`unresolved` is never proof-complete. The boundary rows must form the exact
adjacency chain; non-adjacent, missing or duplicate pairs fail.

`text_layer_comparisons[]` has exactly one row per text or visible-text-like
block and records `block_id`, `stage_a_text_sha256`, `visible_transcription_sha256`
(hash only), `comparison_state`, `evidence_component_ids`, `reason_codes`,
`row_id`, and `row_sha256`. A disagreement may be preserved as evidence but
cannot receive `eligible_for_order_boundary_proof`.

### 4.3 `PageProofReviewAttestation.v1`

Closed fields:

```text
schema
review_kind: "architecture" | "fixture_implementation"
reviewer_role: "independent_terra_critic"
reviewer_identity: non-empty stable label
assignment_state: "platform-unverified"
implemented_candidate: false
materially_designed_candidate: false
release_review: false
candidate_evidence_core_sha256: sha256
fixture_matrix_sha256: sha256
decision: "accept" | "reject"
reason_codes: non-empty list from closed enum
evidence_refs: non-empty list of fixture/test receipt hashes or repo-relative refs
reviewed_at: RFC 3339 timestamp with offset
review_sha256: sha256 over all preceding fields
content_sha256: sha256 over the complete canonical review root excluding itself
```

The review binds the evidence core, not a mutable display rendering and not the
final root hash, avoiding a circular hash. A missing, self-reviewing, mismatched
or non-independent attestation can only produce review-required/rejected state.

## 5. Output schema: replayable page/block evidence ledger

`kb_creator.pdf_raw.PageBlockEvidenceLedger.v1` has these closed root keys:

```text
schema
profile
terminal_state
admission
source_identity
page_identity
stage_a_authority
render_identity
counts
blocks
atom_coverage
glyph_coverage
component_coverage
paint_order
reading_order
paragraph_boundaries
text_layer_comparisons
conservation
decision
review
evidence_core_sha256
inventory_sha256
content_sha256
```

`stage_a_authority` records schema, fixture id, terminal state, content hash,
inventory hash and the ordered Stage A row hashes used by the ledger. It does
not relabel any Stage A field as geometry, visibility or semantics.

`blocks` are normalized versions of section 4.2 block rows. Every block also
records `reading_order_ordinal_or_null`, `paint_ordinal_min_or_null`,
`paint_ordinal_max_or_null` and its derived text hash. A block is eligible for
order/boundary proof only when geometry is valid, visibility is `visible`,
decoration is `content`, text-layer state is `agrees_visible`, all mappings are
conserved, and all relevant boundaries are resolved.

Coverage arrays contain one row per source atom, glyph or render component:

```text
source_row_or_component_id
owner_block_id
coverage_disposition: "content" | "occluded" | "decorative" |
                      "text_layer_only" | "visual_only"
row_id, row_sha256
```

There is no `ignored`, `dropped`, catch-all or null disposition.

`paint_order` is the complete Stage A atom sequence by sealed ordinal/frame
invocation order. `reading_order` is the complete reviewed block permutation plus
explicit exclusions. Neither may overwrite the other.

`conservation` records exact counts and digests plus booleans:

```text
all_stage_a_atoms_accounted_once
all_stage_a_glyphs_accounted_once
all_visual_components_accounted_once
glyph_text_conserved
within_fragment_glyph_order_conserved
paint_order_conserved
reading_order_is_exact_permutation
reading_order_edges_complete
paragraph_adjacencies_complete
geometry_complete_and_in_bounds
occlusion_edges_respect_paint_order
text_layer_disagreements_non_publication_only
proof_status: "pass" | "fail"
```

Every boolean must be `true` and `proof_status` must be `pass` before a candidate
object exists. The corresponding count/hash details must be recomputed, not
trusted from the witness.

`decision` contains `scope = fixture_only`, `source_use = forbidden`,
`repair_admission = none`, `review_decision`, and closed reason codes.
`review` is null in a candidate and the exact attestation in a reviewed ledger.

The only public terminal states are:

- `fixture_candidate_review_required`;
- `fixture_proof_accepted_no_source_use`;
- `fixture_proof_rejected_no_source_use`.

No state may contain `ready`, `promoted`, `reconstructed`, `publishable`,
`source_repair_authorized` or an equivalent alias.

## 6. Fail-closed behavior

Ingress or validation failure raises `RawPdfError` with one stable code and
returns no candidate, partial ledger, plaintext, mutable dict or authority-like
object. Required codes include:

- `page_proof_ingress_forbidden`;
- `page_proof_fixture_registry_invalid`;
- `page_proof_fixture_admission_forbidden`;
- `page_proof_authority_type_forbidden`;
- `page_proof_authority_binding_invalid`;
- `page_proof_source_identity_invalid`;
- `page_proof_page_identity_invalid`;
- `page_proof_render_invalid`;
- `page_proof_geometry_missing_or_malformed`;
- `page_proof_mapping_invalid`;
- `page_proof_conservation_failed`;
- `page_proof_reading_order_incomplete`;
- `page_proof_paragraph_boundary_incomplete`;
- `page_proof_visibility_unresolved`;
- `page_proof_review_invalid`;
- `page_proof_replay_mismatch`;
- `page_proof_stage_a_fixture_coverage_incomplete`.

Text-layer disagreement and occlusion are evidence states, not parse errors. An
attempt to mark either ordinary visible source text must fail with
`page_proof_nonpublication_promotion_forbidden`.

Candidate/reviewed wrapper objects must be capability-constructed, immutable,
non-copyable, non-deep-copyable and non-pickleable. Accessors expose canonical
bytes, hashes, counts and terminal state only. They expose no arbitrary nested
dict and no reconstructed text.

## 7. Conservation and order acceptance rules

A fixture candidate exists only if all of the following hold:

1. Source/page identities match the Stage A authority exactly.
2. Stage A is in `provenance_complete_no_consumer` and matches one literal
   admission row.
3. Every Stage A atom is mapped to exactly one block and coverage row.
4. Every Stage A glyph is mapped to exactly one atom, fragment, block and
   coverage row; its Unicode bytes and order match Stage A exactly.
5. Every admitted raster component is mapped to exactly one block and coverage
   row, including decoration and visual-only content.
6. Every atom geometry row exists, is finite/in-bounds, projects consistently
   under the frozen affine, and has an exact bbox envelope.
7. Paint order is the exact Stage A atom order, including nested frame
   invocation placement. It is never inferred from geometry.
8. Reading order is an exact permutation of all in-flow blocks; every excluded
   block has one explicit non-content disposition; all predecessor/successor and
   column transitions are complete.
9. Within each fragment, atom/glyph order is conserved. Cross-block reordering
   is allowed only through the explicit reviewed reading-order sequence.
10. Every adjacent text fragment has exactly one resolved paragraph boundary.
11. Visible/text-layer comparisons agree for every eligible text block.
    Occluded, decorative, text-layer-only, disagreement and visual-only blocks
    remain explicitly non-publication.
12. Recomputed inventory/content hashes and exact replay bytes match.

Independent review acceptance is additionally required to reach
`fixture_proof_accepted_no_source_use`. Mechanical pass without review remains
`fixture_candidate_review_required`.

## 8. Fixture-only implementation admission

Implementation may begin only after an independent Terra architecture review
accepts this specification. The bounded implementation is admitted only if its
task packet enforces all of these conditions:

- code changes are confined to a new page-proof module under
  `kb_creator/pdf_raw/` and fixture-only tests/assets under the test tree;
- no changes to `source_reconstruction.py`, canonical plan/context/status,
  project configuration, live sources or outputs;
- literal fixture leaves contain no live Innsmouth bytes, hashes, paths, page
  text or derived output;
- all required positive topologies are first available as independently
  accepted Stage A fixture authorities; otherwise the implementation reports
  the coverage blocker described in section 2.2;
- AST/import containment proves the consumer cannot reach filesystem APIs, PDF
  parsers, source reconstruction, network, subprocess, environment/config,
  dynamic import or plugin loading;
- tests monkeypatch `RawPdfDocument.open`, `extract_raw_pdf_page_atoms` and all
  filesystem write/open paths to fail, and still demonstrate admission,
  validation and rejection before any forbidden call;
- all public successes replay byte-for-byte; all malformed matrix cases fail
  with the first intended error; a target-only repair makes each surrogate pass;
- direct reversal, fully rehashed cross-pair substitution, duplicate insertion,
  omission, swap, ordinal shift, hash reseal and unknown-key attacks are covered;
- a separate independent implementation review accepts the exact candidate
  hashes and test evidence.

Passing this gate authorizes only fixture implementation. It does not authorize
a live preflight, source repair or a consumer switch.

## 9. Required adversarial QA matrix

Each case needs a valid positive fixture, one-defect malformed surrogates, exact
first-failure evidence, target-only repair, reseal and successful replay.

| Case | Required proof | Mandatory rejection |
| --- | --- | --- |
| Two columns | Explicit column membership; top-to-bottom order within each column; reviewed cross-column transition; complete permutation | x/y zig-zag, paint-order-as-reading-order, swapped columns, duplicate/drop, or unresolved transition |
| Nested Form | Parent/child frame and invocation placement retained; effective geometry witness bound to the correct frame; child atoms/glyphs conserved once | flattened frame identity, lost/duplicated child atom, recursive/cyclic invocation, parent-token mismatch, or wrong paint placement |
| Running headers/footers | Components and atoms conserved; `decorative` disposition; explicit exclusion from reading flow | silent drop, ordinary body inclusion, or reuse as paragraph content |
| Text under image/occlusion | Text atom/glyph retained; occluder id, overlap mask/ratio and later paint order proven; state `non_publication_occluded_recovery` | promotion to ordinary body, missing occluder, reversed paint relation, or overlap below the frozen rule |
| Visual-only page | All visual components mapped; zero eligible text is valid; terminal remains evidence-only | invented text, empty component inventory, source-repair eligibility, or visual page treated as parse failure |
| Malformed/missing geometry | No candidate is created | missing atom row, NaN/infinite/degenerate/out-of-bounds bbox, inconsistent polygon envelope, invalid affine, pixel/PDF mismatch |
| PDF text layer disagreement | Both Stage A hash and visible transcription hash recorded; explicit disagreement/non-publication state | silent choice of either text, ordinary source-body status, or omitted comparison |
| Paragraph boundaries | Exact adjacency chain including column/section transitions; all decisions resolved | missing/extra/non-adjacent edge, unresolved decision, glyph reorder, implicit hyphen repair, or text mutation |

The matrix is incomplete if a negative case is tested only with an invalid Stage
A surrogate in unrelated respects. Each malformed row must be valid in every
non-target invariant, and its target-only repair must pass full replay.

## 10. Later separate live-page preflight

This section defines a future gate, not a live consumer switch and not authority
to run it.

### 10.1 Selection and freeze

A new goal/step must select exactly one page from a named unresolved repair
class before any live file is opened. The orchestrator records a closed
`LivePagePreflightAuthorization.v1` with:

- goal/step id and repair-class hypothesis;
- one source repo-relative path, byte length and SHA-256;
- one zero-based page index plus page object ref and page-tree route when known;
- read-only input allowlist (the one PDF only) and explicit denylist for EN,
  Keeper, HTML, PDF, config and output trees;
- exact hashes of the reviewed preflight adapter, Stage A boundary and fixture
  proof implementation;
- execution command, write-denied sandbox policy, network-disabled policy and
  stdout-only result policy;
- independent Terra preflight-plan acceptance and timestamp.

The authorization is frozen before execution. A source hash/length, page
identity, code hash, command or policy mismatch invalidates it; no automatic
refresh or nearest-page fallback is allowed.

### 10.2 Read-only execution

The future live adapter must be a separate, independently specified capability,
not a mode flag in the fixture consumer. It may open only the selected PDF in
binary read-only mode and only after the outer controller verifies the frozen
identity. It must run with filesystem writes denied, network/subprocess/config
access denied, and EN/output paths inaccessible. It must not render, rebuild,
copy, normalize, rename, touch timestamps, create cache/bytecode/test artifacts,
or persist a ledger.

Its sole result is canonical evidence bytes returned in memory/stdout with
terminal state `live_preflight_evidence_only_no_source_use`; stderr may contain
only a stable failure code. The controller verifies the source hash again after
the read and verifies the scoped filesystem was unchanged. Persisting those
bytes, if ever desired, requires a separate explicit artifact-writing task.

The preflight must stop on unsupported PDF features; it cannot fall back to a
generic library, OCR, existing EN, or a different page. A successful preflight
is evidence for review only and cannot invoke `source_reconstruction.py`.

## 11. Exact downstream source-repair admission/rejection

No fixture ledger, including `fixture_proof_accepted_no_source_use`, authorizes
any live source repair. After a separately authorized live preflight, a repair
class is authorized only by a new, immutable `SourceRepairClassAdmission.v1`
accepted by the orchestrator after independent Terra criticism. Common required
criteria are all of:

1. the exact repair class has accepted positive and adversarial fixture coverage;
2. the frozen live page identity and all implementation hashes match the
   preflight authorization;
3. the live evidence ledger passes every conservation/order invariant and exact
   replay, with no unresolved status in the proposed repair scope;
4. the independent reviewer accepts the evidence core and names the exact page,
   block/fragment ids and allowed transformation;
5. the admission states a minimal transformation grammar, rollback/input hash,
   target source file and prohibition on every unmentioned edit;
6. source execution remains a later bounded task; this proof route never applies
   the repair itself.

Class-specific decisions:

| Repair class | Authorize only when | Reject when |
| --- | --- | --- |
| `block_order_only` | Every eligible block is visible/content/text-layer-agreeing; reading order is accepted and complete; operation is a permutation of intact blocks with byte-equivalent text | Any missing geometry/mapping/review, disagreement/occlusion in scope, text edit, partial block, or ambiguous column transition |
| `paragraph_boundary_only` | Complete accepted fragment adjacency; glyph/text sequence conserved exactly; operation only inserts/removes paragraph separators at enumerated boundaries | Any unresolved boundary, hyphen/spelling/content change, non-adjacent join, reordered glyph, or disagreement/occlusion in scope |
| `heading_body`, `list_body`, `table_body` | Never from this contract alone; requires a separate semantic-role/classification specification and proof bound to this ledger | Always reject if page order/geometry or Stage A `semantic_role=unavailable_stage_a` is the only evidence |
| `art_anchor` | Never from this contract alone; requires a separate anchor semantics and target-link proof | Always reject from overlap/proximity or block order alone |
| `occluded_text_recovery` | Never as ordinary source body; only a separately named non-publication recovery workflow may inspect it | Any direct insertion into source, Keeper, HTML or PDF, or any silent preference for the PDF text layer |
| `visual_only_page_text_repair` | Not authorized | Always; this proof contains no text authority for a visual-only page |

If any common or class-specific criterion fails, the admission decision is
`rejected_no_source_change` with reason codes. There is no partial authorization,
best-effort fallback, class alias, range authorization or transitive promotion to
neighboring pages.

## 12. Risks and controls

| Risk | Control |
| --- | --- |
| Fixture witness merely repeats an expected answer | Re-derive raster components, bind all leaves, conserve Stage A rows, require target-only adversarial repairs and independent visual/architecture review |
| Existing `page_capable.py` appears reusable but accepts PDF bytes and replays a parser | Reuse only its conceptual canonical-hash/component-conservation lessons; prohibit its PDF entry points and hard-coded page relation from this consumer |
| Duplicate Stage A wrappers drift | Name `RawAtomProvenanceAuthorityV1` as the sole input and reject legacy/duck-typed alternatives |
| Geometry/coordinate drift | Canonical decimals, frozen affine and bbox conventions, exact projection/envelope checks, no floats |
| Reading-order heuristic silently promotes a guess | Explicit columns, edges, exclusions and independent review; no authoritative implicit sort |
| Occluded/text-layer-only content leaks into source | Separate status axes, mandatory non-publication disposition and promotion-specific failure code |
| Running decoration disappears and defeats conservation | Require explicit ownership/exclusion rather than ignore/drop semantics |
| Overfitting to minimal fixtures | Block completion until required Stage A positive topologies and the full adversarial matrix are independently accepted |
| Live source drifts during later preflight | Pre/post hash checks, one frozen page/source, no fallback, read-only sandbox and invalidation on any mismatch |

## 13. Non-goals and prohibited scope

- No live Innsmouth PDF/source/EN/Keeper/HTML/PDF/config/output read, render,
  processing or mutation.
- No generic or alternate PDF parser, OCR, image transcription, semantic role
  inference, text correction, translation, normalization or reconstruction.
- No live consumer mode/switch, feature flag, environment escape hatch, plugin,
  callback or allowlist loaded from disk.
- No invocation or edit of `source_reconstruction.py`; its unconditional
  fail-closed behavior remains required.
- No repair execution, source mutation, rebuild, publication, release decision,
  Git operation or production acceptance.
- No claim that geometry/visibility came from Stage A.
- No use of page proximity alone to infer headings, lists, tables, paragraphs,
  art anchors or publication eligibility.
- No range/page-family authorization and no transitive use of one page's proof.
- No edit to canonical plan, context, project status or release artifacts.

## 14. Specification acceptance criteria

An independent architecture reviewer should accept this specification only if
they confirm that:

1. all input/output roots and row identities are closed, canonical and replayable;
2. source/page/block/bbox/order/status/decision/reviewer fields are mandatory as
   defined, with no silent omission path;
3. the consumer accepts only a literal-fixture-bound Stage A authority object
   and cannot open or parse a PDF;
4. geometry and visual truth are explicitly separate witness evidence, not
   promoted Stage A facts;
5. atom/glyph/component/text/order/paragraph conservation is exact;
6. all required negative cases have valid positive topology and target-only
   first-failure/repair proofs;
7. every successful public state says fixture/evidence only and no source use;
8. the later live preflight is separately selected, frozen, write-denied,
   stdout-only and incapable of reading EN or generating artifacts;
9. source-repair authorization remains a later class-specific immutable gate;
10. implementation cannot modify canonical/project/release state or transfer
    orchestration ownership.

## Immutable handoff receipt

- Result: complete architecture/remediation specification for a separately gated fixture-only page-level consumer/proof; no implementation or live/source authorization granted.
- Paths checked: `kb_creator/docs/plans/20260809-innsmouth-page-level-consumer-proof/plan.md`; `kb_creator/docs/plans/20260809-innsmouth-page-level-consumer-proof/context.md`; `kb_creator/docs/plans/20260808-innsmouth-systemic-todo-execution/handoffs/terra_raw_authority_projection_stage_a_p1_faithful_topology_final_review_20260809.md`; `kb_creator/pdf_raw/page_capable.py`; `kb_creator/pdf_raw/raw_authority_projection.py`; `kb_creator/pdf_raw/raw_interpreter_authority.py`; `kb_creator/pdf_raw/source_reconstruction.py`.
- Files changed: `kb_creator/docs/plans/20260809-innsmouth-page-level-consumer-proof/handoffs/sol_page_level_consumer_proof_spec_20260809.md` only.
- Evidence: assigned plan/context boundaries; Stage A Terra acceptance `369 passed, 1 skipped` focused and `1057 passed, 1 justified skipped` aggregate as recorded, explicitly fixture-only/no-consumer; checked hashes `page_capable.py=15C8604F5293E1336F169CDB28EEC140404EC2612712B4A45E7E52756163A95E`, `raw_authority_projection.py=8CE1CCF172C60CE63675E287061E688D2A0C39A80DE511263E851925A96B30A3`, `raw_interpreter_authority.py=D1B02F5EEA5C26851AF2DA5F309392D3D963AD4AE3ABFCF4D7EA008F2B860870`, `source_reconstruction.py=799EBC6DE4D0EB44BB9B266760877D9506E967A30C699C8A60F65F862F4145DD`; code evidence shows Stage A geometry/visibility/semantic role unavailable and source reconstruction unconditionally blocked.
- Verification/evidence: specification checked against all seven user acceptance criteria and all eight mandated negative cases; no tests run because this assignment is specification-only.
- Blockers: no blocker to independent architecture review; complete fixture implementation is blocked until independently accepted Stage A fixture authorities cover the required multi-block, two-column and nested-Form positive topologies.
- Next action: orchestrator requests an independent Terra architecture review of this immutable specification; only an accepted review may authorize a bounded fixture-only implementation packet.
- Elapsed active time: approximately 20 minutes.
- Timestamp: `2026-08-09T20:19:00.9662036+03:00`.
- Token use: unavailable.
- Orchestrator policy owner: `gpt-5.5` medium (platform-unverified); ownership remains with the main-chat orchestrator.
- Role/model/effort: Sol architect / model platform-unverified / high.
- Assignment state: `platform-unverified`.
- Scoped override: `none`.

# Sol Architecture Clarification — Minimal Nested-Form Stage A Adapter

- Goal id: `20260809-stage-a-page-proof-topology-authorities`
- Step: `3b`, architecture clarification only
- Role/effort: Sol architect / high
- Scope: the smallest fixture-only implementation route for
  `stage-a.positive-nested-form.v1` in the current
  `kb_creator/pdf_raw/raw_authority_projection.py`.
- Status: implementation recipe; no code or acceptance decision is contained in
  this handoff.

## Outcome

Do not generalize the accepted baseline or two-column validators. Add one
fixture-gated extractor adapter and one exact nested-Form validator, while
keeping the current Stage A wire row keys and public APIs unchanged.

The adapter is required because current `page_capable` emits:

```text
Form resolution:
  resolution_id, frame_id, operator_token_id, resource_name_b64, target_ref

Invocation:
  invocation_id, frame_id, parent_frame_id, form_ref,
  operator_token_ordinal, effective_ctm

form_do atom:
  atom_id, operator_kind, frame_id, effective_ctm,
  operator_evidence, resource_resolution_ids
```

while Stage A expects fixed resolution/invocation/atom row keys. The missing
fields must be normalized only for the exact nested fixture. `effective_ctm`
must be checked for source-shape validity and discarded; it must not enter the
Stage A artifact or topology assertion.

## 1. Exact branch identity

Introduce literal constants or equivalent exact comparisons:

```text
fixture_id = b"stage-a.positive-nested-form.v1"
topology_id = "stage_a_positive_nested_form.v1"
```

Registry order becomes exactly:

```text
baseline identity
baseline flate
accepted two-column
nested Form
```

Update the independent primitive expected tuple and registry cardinality to
four. Preserve every existing baseline/two-column leaf, expected hash and
assertion byte unchanged. The exact topology-id sequence is:

```text
[None, None,
 "stage_a_positive_two_column.v1",
 "stage_a_positive_nested_form.v1"]
```

No branch may be selected merely by `topology_id is not None`.

## 2. Minimal pre-projection adapter

Add a private helper conceptually equivalent to:

```text
_adapt_nested_form_replay(row, replay) -> normalized replay
```

Call it in `_project` only when both exact nested fixture and topology ids
match. For all other rows, retain the current replay object and projection path.
If a non-nested row contains any invocation or `form_do` atom, fail closed with
`raw_interpreter_authority_profile_unsupported`; do not silently adapt it.

The helper must first require the exact nested source topology described below,
then return new normalized lists. It must not mutate extractor-owned rows in
place and must not pass through unknown keys.

### 2.1 Closed resolution source union

Accept exactly two source key sets in the nested helper:

```text
font source arm = {
  resolution_id, frame_id, resource_name_b64, target_ref,
  font_size, token_id, first_char, last_char, widths_span
}

Form source arm = {
  resolution_id, frame_id, operator_token_id,
  resource_name_b64, target_ref
}
```

Unknown, missing or mixed keys fail. A Form source arm is forbidden for every
non-nested fixture.

Normalize the Form arm into the existing Stage A resolution row key set:

```text
resolution_id       = source resolution_id
frame_id            = source frame_id
token_id            = source operator_token_id
target_ref          = source target_ref
resource_name_b64   = source resource_name_b64
font_size           = None
first_char           = None
last_char            = None
widths_span          = None
```

The font arm is copied through the current explicit projection unchanged. This
is a closed union represented with existing keys; do not add `resolution_kind`
or change `_ROW_KEYS`.

Change only the resolution projection expression needed to permit
`widths_span=None`:

```text
raw span when non-null; otherwise None
```

No other nullable span is authorized by this change.

### 2.2 Closed invocation source adapter

Accept the exact current extractor invocation key set:

```text
{
  invocation_id, frame_id, parent_frame_id, form_ref,
  operator_token_ordinal, effective_ctm
}
```

Require `effective_ctm` to be a six-item list of finite canonical numeric
strings, then discard it. Normalize:

```text
invocation_id   = source invocation_id
parent_frame_id = source parent_frame_id
target_frame_id = source frame_id
token_id        = [parent-frame owner stream id,
                   source operator_token_ordinal]
```

Before sealing, require all of these joins:

1. parent and target frames exist and are distinct;
2. target frame `parent_frame_id` equals the invocation parent;
3. target frame `owner_ref` equals source `form_ref`;
4. the normalized token exists in the parent frame's stream and is raw `Do`;
5. exactly one Form-resolution source row has the same parent frame, operator
   token and target ref;
6. exactly one parent `form_do` source atom has that operator token and exactly
   that resolution id.

Do not add `form_ref` or CTM to the Stage A invocation row. The existing
invocation `_ROW_KEYS` remain unchanged.

### 2.3 `form_do` atom adapter

For a nested source atom with `operator_kind="form_do"`, require the exact
extractor key set:

```text
{
  atom_id, operator_kind, frame_id, effective_ctm,
  operator_evidence, resource_resolution_ids
}
```

Require a six-item finite CTM shape and discard it. Add only
`glyph_ids=[]` to the normalized source row so the existing Stage A atom
projection can seal it. A `form_do` atom with glyphs, zero/multiple resolution
ids, no matching invocation, or a font-arm resolution fails.

Text atoms continue through the existing text projection. Do not relax their
required fields or glyph ownership.

### 2.4 Root-content ordinal

The nested stream order is exactly `5:0`, `7:0`, `9:0`. Only `5:0` is a page
root content stream. The Stage A rows must contain:

```text
root_contents_ordinal = [0, None, None]
```

The smallest safe change is an optional explicit `root_contents_ordinal`
argument to `_row` for stream projection. `_project` supplies `0,None,None`
only in the nested branch; other fixtures retain the current `ordinal` value
and therefore retain existing bytes.

Do not reinterpret global stream ordinal as root-content ordinal for Forms.

## 3. Exact validator branching

Replace the current broad `topology_id is None / else two-column` decision with
this closed dispatch:

```text
if fixture id is one of the two exact baseline ids and topology_id is None:
    _validate_rows(...)                    # unchanged baseline validator
    require current exact 5/1/10/1/1/0/1/1 counts

elif fixture id == accepted two-column id and
     topology_id == stage_a_positive_two_column.v1:
    _validate_two_column_rows(...)         # unchanged

elif fixture id == nested id and
     topology_id == stage_a_positive_nested_form.v1:
    _validate_nested_form_rows(...)

else:
    fail(code)
```

Do not route nested rows through `_validate_rows`: that function intentionally
contains baseline object refs, one-root-frame, font-only, no-invocation,
`text_show/Tj/A` assumptions. Do not route nested rows through the two-column
validator either.

Assertion dispatch is equally exact and computes the selected assertion once:

```text
baseline:   no topology assertion
two-column: _two_column_assertion(...)     # unchanged
nested:     _nested_form_assertion(...)
unknown:    fail(code)
```

For each positive fixture, compare the computed canonical assertion bytes and
raw SHA-256 to that fixture's literal assertion leaf. Never select an assertion
builder through a generic topology callback or registry function.

## 4. Exact nested validator

`_validate_nested_form_rows` is fixture-specific. It should use a small private
row-envelope check for this branch only; do not refactor or replace accepted
baseline/two-column validation during this step.

### 4.1 Generic wire envelope required inside the nested branch

For every nested object/stream/token/frame/resolution/invocation/atom/glyph row,
require:

- exact current `_ROW_KEYS[kind]`, kind and contiguous ordinal;
- exact recomputed `row_id` and `row_sha256` under current domains;
- globally unique row ids and unique semantic ids;
- valid refs and every non-null physical/raw span within the admitted literal
  PDF with matching SHA-256;
- exact token canonical base64, decoded span/order/hash and identity-stream
  physical offset relation;
- stream nested token copies equal their corresponding global token rows.

This check adds validation for nested rows only. Existing validators remain
byte- and behavior-stable.

### 4.2 Exact fixture inventory

Require exactly:

```text
objects=7, streams=3, tokens=33, frames=3,
resolutions=5, invocations=2, atoms=7, glyphs=5

object refs: [1:0, 2:0, 3:0, 5:0, 7:0, 8:0, 9:0]
stream ids:  [5:0, 7:0, 9:0]
frame ids:   [page-3-0-0, form-7-0-1, form-9-0-2]
frame owners:[[5,0], [7,0], [9,0]]
parents:     [None, page-3-0-0, form-7-0-1]
```

All three streams are literal identity streams. Object spans remain ordered and
non-overlapping. No additional root frame, stream, Form, image or resolution is
allowed.

### 4.3 Resolution arms and order

Require the exact resolution-arm sequence:

```text
0 parent font /F   -> [8,0]
1 parent Form /Outer -> [7,0]
2 outer font /F    -> [8,0]
3 outer Form /Inner  -> [9,0]
4 inner font /F    -> [8,0]
```

Font arm validation remains the existing strict font validation: non-null
font fields, `font_size="10"`, valid char range and width span contained in
font object `8 0 R`.

Form arm validation is exact:

```text
font_size is first_char is last_char is widths_span is None
resource names decode exactly to Outer, Inner
targets are exactly [7,0], [9,0]
token is in the owning parent-frame stream and raw bytes are Do
target object exists and equals the matched target-frame owner
```

Any mixed-null resolution fails; there is no third arm or fallback.

### 4.4 Invocation graph

Require invocation ids `"1","2"` in order and exact edges:

```text
1: page-3-0-0 -> form-7-0-1, token equals parent /Outer Do
2: form-7-0-1 -> form-9-0-2, token equals outer /Inner Do
```

Each non-root frame has exactly one incoming invocation; root has zero. Each
invocation joins exactly one Form-arm resolution and one `form_do` atom through
the same parent frame and token. Reject self-edge, cycle, duplicate incoming
edge, missing target, wrong owner, wrong token or unpaired event.

### 4.5 Atom/glyph paint continuity

Require exact atom operator/frame order:

```text
ordinal  operator    frame
0        text_show  page-3-0-0   # P
1        form_do    page-3-0-0   # Outer
2        text_show  form-7-0-1   # C
3        form_do    form-7-0-1   # Inner
4        text_show  form-9-0-2   # N
5        text_show  form-7-0-1   # D
6        text_show  page-3-0-0   # Q
```

For every atom, operator evidence must bind the owning frame's stream, exact
operator token/span/hash and preceding operands. `text_show` requires raw `Tj`
and its font-arm resolution. `form_do` requires raw `Do`, empty glyph ids and
its Form-arm resolution/invocation pair.

Require exact glyph byte/owner order:

```text
bytes:       P, C, N, D, Q
atom ordinals:0, 2, 4, 5, 6
font arms:   0, 2, 4, 2, 0
code_index:  0, 0, 0, 0, 0
```

Each glyph must retain current code/scalar/base64/width/font-span checks.
Every atom's `glyph_ids` must equal exactly the ordered glyph rows it owns.
This exact sequence proves depth-first raw paint continuity; it is not reading
order.

Every nested atom, including both `form_do` rows, must still contain:

```text
geometry="unavailable_stage_a"
visibility="unavailable_stage_a"
semantic_role="unavailable_stage_a"
```

## 5. Literal nested assertion

Add `_NESTED_FORM_ASSERTION_RAW` using the already accepted
`PositiveStageATopologyAssertion.v1` root. `_nested_form_assertion` may build the
candidate bytes from the exact validated artifact, but validation must compare
them to this literal canonical leaf and its literal length, raw SHA-256, facts
SHA-256 and content SHA-256 in both `_FIXTURES` and the independent expected
tuple.

The facts remain fixture-specific and bind:

- exact root/outer/inner frame rows;
- both invocation rows, token rows, Form-resolution rows and target refs;
- all seven paint-event rows in the order above;
- glyph continuity `P,C,N,D,Q`;
- exact incoming-edge counts and descendant intervals;
- the unchanged `not_proved_stage_a` boundary for geometry, visibility,
  semantic blocks and reading order.

Do not create a generic assertion schema dispatch, mutable expected registry or
derived literal leaf.

## 6. Required containment and focused proof

Implementation/test scope remains only `raw_authority_projection.py` and the
approved Stage A fixture tests. `page_capable.py`, `page_proof.py`, public proof
states and APIs remain unchanged.

Minimum evidence:

1. baseline identity/flate canonical bytes and expected hashes unchanged;
2. accepted two-column authority and literal assertion bytes/hashes unchanged;
3. nested projection and replay byte-identical with exact counts and literal
   assertion seals;
4. fully resealed nested surrogates reject wrong invocation token, target owner,
   duplicate incoming edge, missing `form_do`, flattened child order and broken
   glyph ownership through full replay validation;
5. repairing only the targeted nested defect and resealing passes;
6. Form source rows supplied to baseline/two-column fail rather than entering
   the adapter;
7. no filesystem, live input, alternate parser, config, source reconstruction,
   page-proof, output or Git route is added.

## 7. What must remain fixture-specific

The following must not become generic configuration or permissive validation:

- nested fixture/topology ids and registry position;
- object/stream/frame refs and ids;
- exact counts and root-content ordinals;
- resolution arm order, names and targets;
- invocation ids/edges and one-incoming-edge rule;
- atom/frame/operator sequence and glyph sequence/owners;
- nested topology assertion builder and literal assertion leaf;
- accepted failure codes and target-only adversarial repairs.

Only the mechanical conversion from the exact extractor Form source shape to
the existing Stage A wire keys is reusable inside the nested branch. It is not
authorization for arbitrary Forms or PDFs.

## 8. Implementation blocker

No architecture blocker remains. Completion is still blocked on materializing
the exact nested PDF literal, authority row/inventory/content hashes and literal
assertion bytes/hashes, then independently reviewing those exact identities.
Those values must be generated once from the accepted synthetic fixture and
pasted as literals; they must not be generated at import or validation time.

## Immutable handoff receipt

- Scope: minimal nested-Form adapter/validator clarification for the current accepted baseline plus two-column Stage A implementation; no code changes.
- Result: exact closed-union source adapter, fixture-specific validation dispatch, nested graph/paint/glyph invariants and containment recipe supplied.
- Files checked: root `AGENTS.md`; `docs/governance/nri_goal_governance.md`; assigned goal `plan.md` and `context.md`; prior Sol topology specification; current `kb_creator/pdf_raw/raw_authority_projection.py`; current Form record construction in `kb_creator/pdf_raw/page_capable.py`; current Stage A topology test surface.
- Files changed: `kb_creator/docs/plans/20260809-stage-a-page-proof-topology-authorities/handoffs/sol_nested_form_minimal_adapter_clarification_20260809.md` only.
- Verification/evidence: static current-code contract trace; confirmed registry has baselines plus accepted two-column only; current `_row` expects font-shaped resolutions and normalized invocations; current broad topology branch routes every positive topology to two-column; current `page_capable` Form rows include the source fields described above and `effective_ctm`, which this contract discards.
- Blockers: no architecture blocker; exact nested literal bytes and seals remain implementation/review work.
- Next action: orchestrator applies this recipe in the bounded step `3b`, runs focused target-only replay QA, then requests independent Terra implementation review.
- Elapsed active time: approximately 4 minutes.
- Token use: unavailable.
- Timestamp: `2026-08-09T21:48:04.5879115+03:00`.
- Orchestrator policy owner: `gpt-5.5` medium (platform-unverified); orchestration ownership remains in the main chat.
- Role/model/effort: Sol architect / model platform-unverified / high.
- Assignment state: `platform-unverified`.
- Scoped override: `none`.

This receipt does not transfer orchestration ownership.

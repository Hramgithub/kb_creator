# A5 architecture receipt: structural decision contract and fail-closed gates

## Governance receipt

- Goal id: `20260917-dream-structural-fidelity-audit`
- Step id: `A5`
- Role: architecture / root-cause analysis; requested effort `high`
- Model: unavailable (runtime identity is not independently exposed)
- Orchestrator policy owner: `gpt-5.6-sol`, medium
- Assignment state: `platform-unverified`
- Scoped override: none
- Scope: diagnose the generic Stage03-06 structural-fidelity gap and specify a
  scenario-neutral remediation. No production code, candidate, decision set,
  canonical plan, context, project status, acceptance, or release artifact was
  changed.
- Result: root cause confirmed and the implementation contract below specified.
- Files changed: this immutable receipt only.
- Blockers: none for implementation. A new immutable replay run and successor
  decision root are required because the current replay run, Stage05/06 outputs,
  and v12 decisions are sealed evidence.
- Next action: A6 implements the shared contract and synthetic tests; the
  orchestrator then creates a fresh Stage01-04 replay successor, authors a
  structurally complete successor decision set, and runs Stages05-06.
- Elapsed time: approximately 45 minutes.
- Token use: unavailable.
- Timestamp: 2026-09-17T15:35:00+03:00.

## Scope and assumptions

1. Source inputs, `20260917-cpu-replay-05`, its Stage05/06 outputs, and
   `20260917-cpu-replay-05-decisions-v12` remain immutable.
2. Human visual review is the authority for the complete inventory of visible
   semantic structures. MinerU signals are evidence, not sufficient authority.
3. The typed structure is applied before and during Stage06 materialization. It
   is **not** inferred or repaired later by MASTER_EN. MASTER_EN and promotion
   remain outside this goal.
4. The existing sealed Stage04 bundle is sufficient visual and block evidence;
   the repair does not require changing source text or regenerating MinerU.
5. A page may legitimately have zero declared structures, but only under an
   explicit, page-complete review bound to the exact Stage04 visual.

## Evidence and root cause

### Actual normalization boundary

MinerU data is normalized in Stage03, not Stage04:

- `kb_creator/scripts/compare_mineru_three_views.py::inspect_view` loads
  `_content_list.json`, `_content_list_v2.json`, `_middle.json`, and MinerU
  Markdown.
- `normalize_content` creates the canonical comparison block. It takes the
  block `type`, text, bbox, and assets from `_content_list.json`; from v2/middle
  it retains only title evidence through `_title_evidence` and
  `_is_unambiguous_title`.
- `kb_creator/scripts/build_mineru_visual_merge_bundle.py::_page_view` and
  `build_packets` merely page-slice and copy those Stage03 blocks into Stage04
  merge packets. They do not read or normalize v2/middle artifacts.

Therefore the earliest shared information-loss layer is Stage03 comparison
normalization. The decision/audit enforcement gap is then exposed at Stages
04-06: the reviewer can see a boundary, but no typed declaration is required,
Stage05 normalizes away Markdown punctuation, and Stage06 checks headings plus
text/asset identity rather than container survival.

### What the live MinerU metadata contains

All three Dream CPU views were inspected in the current replay. Their
`content_list_v2` and `middle.pdf_info[].para_blocks` do preserve some model
types: `title`, `paragraph`/`text`, `list`, `table`, `image`, `index`, page
furniture, and title levels in middle records. They do **not** expose typed
`quote`, `callout`, `handout`, or `statblock` records.

The signals are materially incomplete for this defect class:

- the three views agree on only three model `list` blocks: one on page 16 and
  two on page 18;
- the visually confirmed lists on pages 4-5, 11, 14, and 19 are not typed as
  lists in v2/middle;
- page 18 carries ten `table` blocks, but the normalized packet contains them
  as ten asset-backed, empty-text table blocks, with no character-card or
  statblock membership/boundary;
- pages 7, 9, 10, 14, and 19 contain visible handout boundaries but no handout
  type; page 15's Keeper's Note and page 17's quote blocks likewise have no
  corresponding typed metadata.

MinerU metadata should therefore remain advisory. Merely copying its v2/middle
types forward would still miss confirmed structures and cannot be the gate.

### Why current gates pass flattened output

- Page decision v1 has `selected_blocks`, free-form `markdown`, assets, and a
  boolean visual-review receipt, but no closed semantic-structure inventory.
- `audit_mineru_ai_merge_fidelity.py::_normalized` reduces text to an
  alphanumeric stream. `audit_v3_content` proves full-unit textual/spatial
  accounting and monotonic order, but Markdown blockquote, list, table, and
  heading-level punctuation does not participate in completeness.
- `materialize_mineru_ai_merge.py::_validate_decision` enforces selected-block
  identity and one title-to-ATX-heading rule. It does not require list syntax,
  container wrappers, card membership, or heading parentage.
- Page 18 demonstrates the gap: all ten image-backed table blocks are selected
  as assets and the text is present, so lexical/asset closure passes while the
  seven source statblocks are not represented as seven semantic containers.

## Remediation specification

### 1. Versioned opt-in without invalidating sealed evidence

Add `kb_creator.reconstruction_decision_set.v2`. It keeps every v1 authority
field and adds exactly:

```json
"semantic_structure_profile": "visually_reviewed_semantic_containers_v1"
```

The sealed review queue may continue to require page-decision schema
`kb_creator.mineru_ai_page_decision.v1`; changing that queue would invalidate
the replay prefix. Under decision-set v2, every page decision must additionally
contain `semantic_structure`. Decision-set v1 and page decisions without this
field remain valid only on the legacy path and produce the existing v3 audit.
Mixed coverage is invalid: one missing page, an unknown profile, or a profile
on decision-set v1 fails before the validated-submission snapshot is published.

This is the narrow compatibility bridge for a Stage05-06 successor replay. It
does not mutate the meaning of old decisions and does not permit an old v3
audit to satisfy a v2 structural submission.

### 2. Minimal per-page typed contract

Add this exact field to each successor page decision:

```json
"semantic_structure": {
  "schema": "kb_creator.page_semantic_structure.v1",
  "review": {
    "state": "complete",
    "visual": {"path": "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-014.png", "bytes": 0, "sha256": "..."}
  },
  "units": []
}
```

`bytes` above is illustrative and must be the non-zero observed identity. The
visual path must match the decision source page and an exact file identity in
the sealed Stage04 visual manifest. The source-view name is a configured
required view, not a scenario name.

Each closed `units` row has these exact fields:

| Field | Contract |
|---|---|
| `id` | globally unique stable identifier, safe token |
| `kind` | `blockquote`, `callout`, `handout`, `list`, `statblock`, or `heading` |
| `representation` | `blockquote`, `unordered_list`, `ordered_list`, `table`, or `atx_heading` |
| `source_blocks` | non-empty exact `{view, raw_index}` references to selected Stage04 packet blocks |
| `markdown_span` | 1-based inclusive `{start_line, end_line, sha256}` over effective LF Markdown |
| `container_parent` | same-page containing unit id or `null` |
| `semantic_parent` | parent heading unit id, including an earlier page, or `null` |
| `continuation_of` | previous same-kind unit id for a cross-page continuation, or `null` |
| `heading_level` | integer 1-6 only for `heading`, otherwise `null` |
| `item_count` | positive integer only for `list`, otherwise `null` |

Allowed representation pairs are closed: blockquote/callout/handout use
`blockquote`; list uses one list representation; heading uses `atx_heading`;
statblock uses `blockquote` or `table`. A typed sidecar preserves the semantic
difference between, for example, a quotation and a handout even though both
use portable Markdown blockquote syntax.

`markdown_span.sha256` is SHA-256 of the exact UTF-8 bytes formed by joining the
inclusive lines with LF and no added terminal LF. Spans are evaluated after
the existing `block_boundaries` transform and before asset-path substitution.
Move `_apply_block_boundaries` into a shared helper so Stage05 and Stage06 use
the same effective Markdown bytes.

### 3. Shared fail-closed validator

Add `kb_creator/pipeline/semantic_structure.py` and use it from both Stage05 and
Stage06. It must perform all checks below without scenario names, page numbers,
titles, or English-language heuristics:

1. closed shapes, supported profile/schema/kind/representation, complete page
   coverage, exact page-matched Stage04 visual identity, globally unique ids;
2. every `source_blocks` reference exists in that page packet and is selected
   in the decision; text refs occur inside the declared span in selected order,
   while asset refs have their exact decision placeholder inside the span;
3. exact line bounds and span hash; sibling spans are disjoint, nesting is
   explicit and strictly contained, and crossing/implicit overlap is rejected;
4. every line of a blockquote representation is explicitly quoted (including
   quoted blank separators), list marker style and top-level item count match,
   table representation has a valid header/delimiter pair, and an ATX heading
   span contains exactly one heading at the declared level;
5. `container_parent` resolves on the same page with strict span containment;
   `semantic_parent` resolves to a preceding heading and the child level is the
   parent level plus one; `continuation_of` resolves to a preceding same-kind,
   same-representation unit; all relation graphs are acyclic;
6. declared source-block order and Markdown unit order are monotonic. Nested
   source reuse is allowed only between an explicit ancestor and descendant;
7. `review.state=complete` with `units: []` is valid, but absence of the page
   contract under the v2 profile is not.

The validator cannot discover an omitted visible box algorithmically. Its
fail-closed guarantee begins at the complete visual-review declaration: after
a reviewer declares the page inventory, no declared boundary, type, nesting,
continuation, list count, statblock grouping, or heading relationship may be
flattened or moved and still pass.

### 4. Stage05 evidence

Add `kb_creator.ai-merge-fidelity-audit/v4`. Retain the v3 content ledger and
add the profile plus a closed per-page `semantic_structure` result containing
the reviewed visual identity, declared/validated counts, and compact rows of
`id`, `kind`, `representation`, and span hash. `passed=true` requires both v3
content closure and all structural checks. A decision-set v2 submission must
produce v4; v3 is never accepted for it.

`build_replay_audit` reads the snapshotted decision-set schema/profile and
dispatches v3 or v4 explicitly. It must not infer structural mode merely from
one page file.

### 5. Stage06 materialization, not MASTER_EN repair

Stage06 re-runs the shared validator against the exact snapshotted decisions
and effective Markdown, requires the exact passing v4 audit and submission
identity, then writes:

- page Markdown and `RECONSTRUCTED_EN.md` with the reviewed native Markdown
  representation already present;
- copied immutable page decisions;
- `SEMANTIC_STRUCTURE.json` using new schema
  `kb_creator.reconstruction_semantic_structure.v1`, sealed and bound to the
  submission SHA, fidelity-audit identity, page decision hashes, reviewed
  visuals, units, and a top-level structure SHA;
- the existing v3 merge provenance, with the sidecar included through the
  Stage06 deterministic inventory. No acceptance is inferred.

Thus typed metadata exists in the Stage06 candidate and semantic Markdown, not
only in a later MASTER_EN config. MASTER_EN may consume the sidecar in a future
accepted workflow, but it is not allowed to invent or repair these structures.

## Exact implementation surface

Required changes for A6:

- New `kb_creator/pipeline/semantic_structure.py`: closed parsing, effective
  Markdown calculation, cross-page registry, syntax/span/source-ref checks,
  deterministic report/sidecar projection.
- `kb_creator/pipeline/reconstruction.py`: add decision-set v2 constant and
  extend `validate_decision_set` with explicit v1/v2 dispatch, full-page
  structural coverage, and no mixed mode.
- `kb_creator/pipeline/reconstruction_replay_resume.py`:
  `materialize_replay_submission_snapshot`, `build_replay_audit`,
  `replay_downstream_adapters`, and `replay_resume_engine` dispatch v3/v4 by
  snapshotted decision-set schema; extend `DOWNSTREAM_IMPLEMENTATION` with the
  helper and new schemas.
- `kb_creator/scripts/audit_mineru_ai_merge_fidelity.py`: keep
  `audit_v3_content` unchanged for legacy evidence; add `audit_v4_content` that
  composes the v3 ledger with the shared structural validator and emits v4.
- `kb_creator/scripts/materialize_mineru_ai_merge.py`: allow the exact legacy
  key sets or the exact v2-profile page key set; move/reuse
  `_apply_block_boundaries`; extend `_validate_decision`; accept v4 only for a
  v2 structural submission; write and re-open-verify `SEMANTIC_STRUCTURE.json`.
- New contracts:
  `reconstruction_decision_set.v2.schema.json`,
  `page_semantic_structure.v1.schema.json`,
  `ai_merge_fidelity_audit.v4.schema.json`, and
  `reconstruction_semantic_structure.v1.schema.json`.
- `kb_creator/tests/test_semantic_structure.py` (new), plus focused extensions
  to `test_audit_mineru_ai_merge_fidelity.py`,
  `test_materialize_mineru_ai_merge.py`, and
  `test_reconstruction_replay_resume.py`.

No change is required in `build_mineru_visual_merge_bundle.py` for this replay:
the Stage04 packets and sealed visual inventory already provide the required
block and visual authorities. No change to `compare_mineru_three_views.py` is
required to close this goal; retaining additional v2/middle container hints in
a future comparison schema may improve review ergonomics, but those incomplete
signals must never replace the visual-review contract.

Promotion/acceptance is intentionally excluded. Before a later promotion of a
structural-profile candidate, `reconstruction_promotion.py` and package schemas
must be taught to require and verify the new sidecar and v4 audit. Until then,
promotion must remain pending rather than silently treating the candidate as a
legacy v3 one.

## Tests and acceptance criteria

Synthetic tests must cover one passing case for every kind/representation and
the following independent failures:

- missing page contract, mixed v1/v2 mode, stale or wrong-page visual identity;
- unknown/unselected/duplicated source block, source text or asset outside span;
- wrong line hash or bounds, crossing spans, undeclared nesting, relation cycle;
- flattened blockquote/callout/handout/statblock, wrong list style/count,
  malformed table, wrong heading level/parent, broken cross-page continuation;
- v3 audit offered to a v2 submission, v4 audit bound to another submission,
  missing/tampered Stage06 sidecar;
- legacy decision-set v1 fixtures remain byte-compatible and continue through
  the existing v3 audit/materializer path.

Focused suite:

```text
pytest -q kb_creator/tests/test_semantic_structure.py
pytest -q kb_creator/tests/test_audit_mineru_ai_merge_fidelity.py
pytest -q kb_creator/tests/test_materialize_mineru_ai_merge.py
pytest -q kb_creator/tests/test_reconstruction_replay_resume.py
pytest -q kb_creator/tests/test_reconstruction_replay.py
```

Implementation acceptance requires all of the following:

1. no scenario-title, Dream page-number, English-label, or MASTER_EN heuristic
   appears in reusable code or synthetic tests;
2. all 26 successor decisions carry a page-complete reviewed structure contract;
3. all A1-A3 confirmed units are declared, including seven separate page-18
   statblocks and cross-page/list/heading relationships where applicable;
4. removing one `>`, list marker, table delimiter, ATX level, unit relation, or
   statblock boundary makes Stage05 fail; bypassing Stage05 makes Stage06 fail;
5. Stage06 emits readable Markdown plus a hash-bound typed sidecar, and both are
   reproduced deterministically from the same successor submission;
6. existing v12 decisions, replay-05 artifacts, and legacy v1 tests remain
   unchanged; no acceptance or MASTER_EN promotion is inferred.

## Immutable replay path

Do not resume into the occupied `20260917-cpu-replay-05` Stage05/06 paths and do
not edit v12. Use the CLI's existing replay boundary:

1. create a fresh absent successor run root (for example
   `20260917-cpu-replay-06`) with `reconstruction-replay run --through-stage
   04-visual-merge-bundle`, rebasing the verified Stage01-04 prefix;
2. author a fresh successor decisions root bound to that run's new
   `review/review_queue.json`, Stage04 visual identities, source hash, and
   contract hash; use decision-set v2 and never copy old hashes blindly;
3. validate the new decision inventory and run `reconstruction-replay resume
   --run-root ... --decisions ... --decisions-root ...` once into absent
   Stage05/06 outputs;
4. verify v4 audit, Stage06 `SEMANTIC_STRUCTURE.json`, per-page Markdown, full
   visual QA, deterministic inventories, and that `acceptance_inferred=false`.

## Risks and controls

- **Human omission:** no deterministic parser can infer every visible box.
  Control: page-complete review bound to exact visual plus full-scope A1-A3
  inventory and independent implementation review.
- **Line-span brittleness:** intentional; immutable decisions must be rehashed
  after edits, preventing silent drift. Use a small authoring helper if needed,
  but do not weaken runtime validation.
- **Markdown parser divergence:** define and test the restricted native syntax
  above instead of accepting arbitrary extensions.
- **Transform divergence:** Stage05 and Stage06 must share effective-Markdown
  calculation; do not duplicate `_apply_block_boundaries` logic.
- **Legacy ambiguity:** dispatch by decision-set schema/profile, never by field
  sniffing. Old artifacts remain valid but cannot claim the new gate.
- **Downstream loss:** the Stage06 sidecar is authoritative typed metadata;
  future consumers must preserve or explicitly transform it. MASTER_EN is not
  a recovery layer.

## Files checked and verification evidence

Checked governance and goal state:

- `docs/governance/nri_goal_governance.md`
- `NRI_OCR_LAYOUT_RULES.md`
- `.agents/skills/kb-creator-scenario-reconstruction/SKILL.md`
- this goal's `plan.md`, `context.md`, and A1/A2/A3 receipts
- `kb_creator/README.md`, `kb_creator/PROJECT_STATUS.md`

Checked implementation/contracts/tests:

- `kb_creator/contracts/number-7-dream.reconstruction.json`
- `compare_mineru_three_views.py`, `build_mineru_visual_merge_bundle.py`,
  `audit_mineru_ai_merge_fidelity.py`, `materialize_mineru_ai_merge.py`
- `pipeline/reconstruction.py`, `reconstruction_replay.py`,
  `reconstruction_replay_resume.py`, and relevant promotion validators
- comparison, bundle, decision-set, audit, provenance, review-queue schemas
- MinerU, audit, materializer, replay, control-plane, and promotion tests
- live replay-05 v2/middle artifacts, Stage04 packets, all v12 decision shapes,
  and the page-18 decision/block inventory.

Verification was read-only. No automated test was run because this step defines
the remediation and does not alter executable code. The live artifact queries
confirmed the metadata type counts, missing semantic kinds, Stage03
normalization behavior, Stage04 projection behavior, page-18 asset-only table
blocks, and the absence of a typed structure field in all v12 page decisions.

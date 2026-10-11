# Number 7 Dream OCR-equivalence remediation architecture

## Receipt

- Timestamp: `2026-09-17T01:39:48+03:00`.
- Goal: `20260916-dream-reconstruction`.
- Role / scoped override: architecture, root-cause analysis, dependency trace,
  and remediation specification; assigned `gpt-5.6-sol` at `high`. No
  implementation, source mutation, acceptance, publication, release decision,
  or Git action was authorized.
- Orchestrator policy owner: main-chat `gpt-5.6-sol` at `medium`; ownership was
  not transferred.
- Assignment state: complete.
- Scope: replay-v3 Stage 05 accounting for exact duplicate text and reviewed
  multi-character or multi-token OCR corruption while keeping selected
  `original_pipeline_txt` units as canonical reader text.
- Result: **GO for the bounded consumer/schema/test remediation below; NO-GO
  for globally relaxed OCR thresholds or blanket OCR exclusions.**
- Files changed: this immutable receipt only.
- Blockers: current Stage 05 cannot pass. The draft direct audit has 32 errors:
  28 lexical-bound failures plus four exact duplicate-text units on page 18.
  Two page-23 draft classes are not OCR corruption: their raster raw indices are
  swapped, while text and geometry identify the exact canonical counterparts.
  Page 19 raw 290 additionally contains visible source text absent from the
  current canonical Markdown and requires a positional visual assertion before
  it can be accounted as equivalent.
- Next action: implement the two consumer changes and schema branch, add the
  tests below, independently review the implementation, correct the page-19
  decision/allowlist, remove the unnecessary page-23 classes, then rerun only
  replay-v3 Stage 05 against the sealed Stage 01-04 prefix.
- Elapsed time: approximately 40 minutes.
- Token use: exact role token count unavailable.

## Evidence and root cause

The existing policy in `audit_mineru_ai_merge_fidelity.py` is intentionally
strict: an OCR class accepts equal token counts, exactly one differing token,
token Levenshtein at most 1, normalized-string Levenshtein at most 2,
similarity at least 0.92, IoU at least 0.50, and center distance at most 0.035.
Those defaults correctly reject gross OCR loss and must remain unchanged.

The draft `20260917-cpu-replay-03-decisions-v3` direct audit contains 37 OCR
classes, 75 reviewed furniture exclusions, and 32 errors. The 28 bounds
failures occur on pages 1, 3, 9, 14, 16, 19, and 23. They include the heavily
damaged page-3 table of contents, multi-token handwriting/handout OCR damage,
inline `sub`/`sup` extraction differences, and two page-23 raw-index swaps.
The remaining four errors are page-18 `original_pipeline_ocr` and
`raster_pipeline_ocr` raw 271/275. Their normalized text occurs twice in two
selected canonical blocks. `_exact_equivalent()` rejects before geometry
because it requires exactly one textual candidate, even though each alternate
has one unambiguous same-region candidate.

The initial exploratory count of divergent alternates is not a stable contract:
the exact inventory depends on whether exact cross-raw-index matches are removed
before OCR divergence classification. Acceptance must therefore be driven by
the complete unit ledger and zero unresolved units, never by a hard-coded
`61`, `62`, or `63` count.

## Dependency and branch contract

The Stage 05 disposition order must be:

1. selected unit;
2. explicit OCR class membership;
3. exact cross-view whole-unit equivalence, resolved by text **and geometry**;
4. existing exact subspan equivalence;
5. exact reviewed exclusion;
6. unaccounted failure.

The reviewed OCR class has two internal branches:

- the existing bounded lexical branch, unchanged;
- a new exact, human-reviewed full-unit branch used only when the bounded
  lexical test fails.

No caller-supplied tolerance, wildcard, regex, page range, free-form text
replacement, or `ocr_artifact` shortcut is permitted. Legacy/v2 behavior and
the existing seven-key v3 class remain unchanged.

## Code remediation

### A. Geometry-disambiguated exact equivalence

Change `_exact_equivalent()` only as follows:

1. Collect all selected, mapped, cross-view units on the same page whose
   normalized text is exactly equal.
2. Compute canonical Stage-04 source-page spatial metrics for every candidate.
3. Keep only candidates satisfying the existing whole-unit bounds:
   `iou >= 0.50` and `center_distance <= 0.035`.
4. Accept only when exactly one candidate remains. Record all computed metrics
   and policy `exact_unique_cross_view_geometry_v2` in the disposition.
5. Fail closed on zero or multiple geometry-qualified candidates. Do not use
   raw index equality as authority and do not choose nearest by sorting.

This fixes page-18 raw 271/275 and automatically maps page-23 raster raw 341 to
canonical raw 342 and raster raw 342 to canonical raw 341. The two page-23 OCR
classes must then be removed; retaining them would be an unnecessary reviewed
override and must fail as unused or redundant evidence.

### B. Exact reviewed full-unit OCR divergence

Add a second closed OCR-class shape. It retains the existing exact unit fields
and adds:

```json
{
  "equivalence_policy": "reviewed_visual_full_unit_v1",
  "source_visual": {"path": ".../visual/original_pipeline_txt/pages/page-NNN.png", "bytes": 1, "sha256": "..."},
  "canonical_proof": {
    "supporting_assertion_ids": [],
    "expected_normalized_sha256": "..."
  },
  "visual_verdict": "canonical_proof_complete_for_region_alternates_are_ocr_corruption"
}
```

The complete reviewed class still contains `class_id`, `source_page`, one exact
`canonical_unit`, one or two exact `alternate_units`, the existing exact
page-specific triptych `visual`, and a non-empty `rationale`.

Runtime predicates, all mandatory:

1. The canonical unit is selected once, mapped once, and belongs to
   `original_pipeline_txt`; each alternate is unselected, from a distinct
   required OCR view, exact-unit identity bound, and used by no other class or
   exclusion.
2. Existing bounded lexical evaluation is run first. A reviewed class is valid
   only for an alternate that fails those bounds; an unnecessary reviewed
   override is an error.
3. Canonical and alternate are same-page reader units with non-null bboxes.
   With no supporting assertion, existing geometry bounds remain mandatory.
   With a supporting assertion, the alternate may represent a fused region and
   must satisfy `smaller_box_coverage >= 0.80` and
   `center_distance <= 0.035`; this does not relax unrelated classes.
4. `source_visual` must resolve exactly through the sealed visual manifest to
   the page-matching `original_pipeline_txt/pages/page-NNN.png`.
   `visual` must resolve to the page-matching triptych. Both byte count and
   SHA-256 must match; arbitrary visual files are rejected.
5. `canonical_proof` is reconstructed from the selected canonical Markdown
   span plus the named, already validated positional assertions. Assertions
   must be on the same page, anchored to this canonical unit, occur immediately
   before it, be contiguous and non-overlapping, and already participate in the
   gapless proof stream. The SHA-256 of the concatenated normalized rendered
   span must equal `expected_normalized_sha256`.
6. The reviewed branch imposes no global edit-distance ceiling: the exact unit
   identities, exact proof hash, fixed geometry, two exact visual identities,
   closed verdict, and non-empty rationale are the authority. The audit report
   must still emit token counts, string distance, similarity, spatial metrics,
   proof span, assertion ids, and policy for inspection.
7. Duplicate class ids, duplicate alternate membership, stale hashes, a
   selected alternate, wrong-page visuals, absent/extra assertion ids, a proof
   gap, or a class whose canonical proof is not fully present in Markdown fails
   closed. Every row must be used.

This branch is appropriate for the page-3 TOC: the selected embedded-text unit
is complete in the source visual, while both OCR views are grossly fragmented.
It is also appropriate for exact handout regions where handwriting or inline
layout markup causes multi-token OCR damage, after full-resolution visual
review confirms that the canonical proof is complete and that no alternate-only
reader text exists.

It is **not** permission to accept page-19 raw 290 as currently authored. The
source visibly reads `THE ENLIGHTENED - where Bright Minds make Bright Futures.
Start your journey today.`, while the selected canonical unit contains only
`Bright Futures. Start your journey today.`. Add the missing prefix as an exact
`anchor_prefix` visual assertion immediately before canonical raw 290, include
that assertion id in `canonical_proof`, and update Markdown accordingly. Only
then may the raster fused unit be reviewed as equivalent. If visual review
cannot prove the prefix exactly, leave the unit unresolved.

## Schema remediation

In `ai_merge_fidelity_reviewed_allowlist.v3.schema.json`:

- keep the current OCR class shape as one `oneOf` branch;
- add the reviewed branch with `additionalProperties: false` and the exact new
  keys above;
- add a closed `canonical_proof` definition requiring a unique array of
  non-empty assertion ids and one uppercase SHA-256;
- require `equivalence_policy` and the new verdict constants exactly;
- retain one or two alternates and all current unit/visual definitions;
- do not add numeric tolerance properties to the schema.

The runtime closed-key check must mirror the schema's two exact shapes. The
top-level allowlist shape and schema id remain unchanged, preserving existing
bounded v3 allowlists. If audit-report schema validation rejects the additional
policy/proof fields, update only the corresponding disposition detail branch in
`ai_merge_fidelity_audit.v3.schema.json`; do not weaken required authorities.

## Required tests

1. Two identical selected canonical units plus two exact OCR alternates at
   distinct bboxes resolve one-to-one by geometry; reversed raw indices also
   resolve correctly.
2. Duplicate exact text with two geometry-qualified candidates fails; nearest
   candidate is never guessed.
3. Existing bounded OCR positive and every current attack test remain unchanged.
4. Reviewed gross TOC corruption passes only with exact canonical/alternate
   identities, selected canonical proof, page-matching source render and
   triptych identities, failed strict bounds, closed verdict, and rationale.
5. Reviewed-mode attacks fail for a strict-bounds alternate, wrong visual page,
   stale visual hash, wrong canonical view, selected alternate, missing bbox,
   geometry miss, duplicate membership, empty rationale, wrong verdict, stale
   proof hash, unvalidated assertion, proof gap, or unused row.
6. A fused alternate passes the containment geometry branch only when an exact
   supporting assertion and canonical mapping form one contiguous proof span.
   The same case without the assertion fails.
7. Page-19-shaped fixture proves the missing prefix cannot be hidden by a
   reviewed equivalence class; after adding the exact prefix assertion, the
   composite proof passes.
8. Page-23-shaped swapped raw indices pass automatic exact equivalence with no
   OCR class; retaining either reviewed class is rejected as redundant.
9. Full Number 7 Dream dry audit, after decision correction, reports every page
   `unaccounted_unit_count=0`, completeness `1.0`, complete proof streams, no
   errors, and global `passed=true`.
10. Expanded reconstruction/replay suites pass; no Stage 01-04 producer runs,
    no source file changes, and no Stage 06 output is allowed before the new
    Stage 05 report passes.

## Acceptance criteria and risks

- Existing automatic thresholds are byte-for-byte policy constants and all old
  adversarial tests still pass.
- Exact duplicate text is disambiguated only by fixed canonical geometry.
- Every reviewed divergence is bound to exact units, exact canonical proof,
  exact page visuals, fixed geometry, and an explicit human verdict.
- The page-3 TOC may pass without pretending its OCR fragments are lexically
  close; the canonical embedded-text reading remains the output.
- Handout OCR may pass only when the canonical proof includes every visible
  source word. Page-19 raw 290 remains a blocker until its prefix is asserted.
- The sealed replay Stage 01-04 prefix remains immutable and reusable because
  this change is downstream-only. The old failed/dry audit is not reusable.
- Materialization, user acceptance, promotion, publication, Git, and release
  remain outside this remediation.

Primary residual risk is human error in the visual verdict. The exact two-image
authority, page/region geometry, proof hash, no-redundant-override rule, and
independent implementation review minimize but cannot eliminate that risk.

## Files checked / verification

- `.agents/skills/kb-creator-scenario-reconstruction/SKILL.md`.
- `kb_creator/docs/plans/20260916-dream-reconstruction/plan.md` and
  `context.md`; `kb_creator/PROJECT_STATUS.md`.
- `kb_creator/contracts/number-7-dream.reconstruction.json`.
- `kb_creator/scripts/audit_mineru_ai_merge_fidelity.py`.
- `kb_creator/contracts/ai_merge_fidelity_reviewed_allowlist.v3.schema.json`.
- `kb_creator/tests/test_audit_mineru_ai_merge_fidelity.py`.
- Replay-03 comparison, geometry plan, visual manifest, all 26 merge packets,
  and the draft decisions/allowlist under
  `20260917-cpu-replay-03-decisions-v3`.
- Read-only direct audit reproduction: 37 classes, 75 exclusions, 32 errors;
  28 lexical-bound failures and four exact duplicate-text failures.
- Full-resolution source page-19 inspection confirmed the missing visible
  prefix described above.


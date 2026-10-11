# Architecture receipt: source-visible text completeness audit

- Scope: read-only root-cause analysis and reusable remediation specification for the MinerU AI-merge fidelity audit completeness gap exposed during review of Dissociation run `20260915-cpu-first-05`.
- Result: **GO for the bounded implementation specified below; NO-GO for any v2 Stage 05 resume, Stage 06 candidate, reconstruction promotion, or acceptance until that implementation is independently closed.**
- Priority: **P1 pipeline blocker**, not P2 deferred.
- Assignment state: complete.
- Timestamp: `2026-09-15T01:21:14.1223980+03:00`.
- Elapsed time: approximately 28 minutes.
- Token use: approximately 24k architect tokens; exact agent accounting unavailable.
- Orchestrator policy owner: the main `20260914-dissociation-publication` orchestrator under repository `AGENTS.md` and `docs/governance/nri_goal_governance.md`.
- Orchestration ownership: remains with the main orchestrator; this receipt does not transfer plan, context, status, integration, resume, or release authority.
- Scoped override: architecture/specification only; no run/resume, decision, source, production code, canonical plan/context/status, network, GPU, remote/API, or Git mutation. This receipt is the only changed artifact.

## Verdict and rationale

The current v1 audit is not a source-completeness gate. It computes recall from the blocks that a reviewer chose in `selected_blocks`; therefore an incomplete source block, or a source-visible block omitted from the selection altogether, is outside its denominator. It can return `passed: true` while reader-facing source text is absent. The `<20` selected-token exemption creates a second blind spot for short continuations.

That is P1 before candidate materialization because the reconstruction contract covers all source pages and Stage 05 is the only automated fail-closed fidelity gate before Stage 06. A known gate that can approve deleted narrative content cannot remain permissive merely because individual decision omissions are manually repaired. The critic classified the audit limitation as P2 relative to the then-immediate page-5 edit; this architecture review treats the reusable production gate as P1 because the same mechanism applies to every page, short fragment, and future scenario.

Run `20260915-cpu-first-05` must remain immutable evidence. Once the implementation changes, its sealed implementation identity is stale and it must not be resumed under the new code. The orchestrator should allocate a fresh run after independent implementation closure; decisions are not acceptance authority and may be reused only through the governance-approved revalidation/re-authoring workflow against exact fresh queue, packet, comparison, and visual identities.

## Exact observed evidence

- `audit_mineru_ai_merge_fidelity.py:113-158` builds the denominator only in `_selected_tokens`, applies recall only when at least 20 tokens are selected, and never enumerates unselected source text.
- Its only reviewed exception authority is a closed `{allowlist: [...]}` collection of repeated, local glyph substitutions. Rows are keyed by page and `from`/`to`, require an exact count, require evidence, and fail when unused or overbroad. These semantics are useful and must not be weakened or silently repurposed.
- The critic-era page-5 decision selected the truncated original block ending at `At its center is a mound`; the raster view contained `with an open mine tunnel, descending into the darkness.` The audit passed because the missing suffix was not selected.
- During this read-only assignment, the shared decision root was updated by another owner. The current page-5 decision now selects `raster_pipeline_ocr:75` and includes the full suffix. The current page-4 decision also selects `raster_pipeline_ocr:48` and restores the page-3/page-4 continuation `ability of the human body. The rest became vessels.` The decision-set identities currently match those files. This agent made none of those changes.
- Those repairs close two instances, not the gate defect. The page-3 source ends with `testing the malle-`; only the raster page-4 evidence exposes the continuation. This is the exact short, cross-page case that selected-only recall and the 20-token exemption can miss.
- The v2 review queue already seals the Stage03 comparison at `outputs/03-compare-views/comparison.json` and seals every Stage04 packet identity. The required view authority is the three CPU views: `original_pipeline_txt`, `original_pipeline_ocr`, and `raster_pipeline_ocr`. Optional GPU views must not change completeness semantics.
- Stage 05 currently receives only the decision pages, packet root, optional reviewed allowlist, and output path. Stage 06 receives the comparison authority for materialization, but its `MERGE_PROVENANCE.json` does not bind the exact passed fidelity report. Promotion accepts only the current v1 report shape.

## Required v2 authority

For a `kb_creator.run_spec.v2` run, Stage 05 must use one closed, run-local authority chain:

1. The validated review queue at the fixed run-local path, with its sealed `queue_sha256` and run/contract/source identities.
2. The exact queue-pinned Stage03 comparison path, byte count, and SHA-256.
3. The exact queue-pinned Stage04 merge packet path, byte count, and SHA-256 for every source page.
4. The validated submission snapshot: decision-set identity, every page-decision identity, and the optional reviewed-allowlist identity.
5. Only the comparison's required succeeded CPU views form the automatic text-evidence domain. Missing required views, a non-passing comparison, page-domain drift, packet/comparison disagreement, or an extra/missing packet is fatal.

The v2 adapter must pass the queue, comparison, decision set, packet root, and their recorded identities explicitly. The audit must independently reopen and verify those files; infer the run root only to enforce the fixed `review/`, `outputs/03-compare-views/`, and `outputs/04-visual-merge-bundle/merge_packets/` containment relationship. Reject absolute overrides, `..`, symlinks, junctions/reparse points, hash/byte drift, and packet rows that are not byte-for-byte the comparison projection for that page. No copy, symlink, or compatibility mirror is authority.

## Closed evidence-accounting algorithm

The smallest reliable change is to retain the current selected-block fidelity calculation as an accuracy sub-gate and add a v2 **source-text disposition and coverage sub-gate**.

### Evidence units

- Enumerate every non-empty textual block from every required view on every source page. `text`, title-like blocks, headers, footers, and page numbers enter the domain. Empty blocks and pure image blocks do not create text units.
- Give each unit an exact identity: source page, view id, raw index, block type, bbox (or explicit null), normalized text SHA-256, and original text SHA-256.
- Normalize with Unicode NFKC + casefold and an alphanumeric comparison stream. Ignore formatting punctuation, whitespace, smart/straight quote differences, and word-wrap hyphens for matching; retain the original text and hashes in evidence. This permits `mi-go`/`migo`, split/joined OCR words, and Markdown punctuation without permitting deletion of lexical characters.
- Safe automatic equivalence is limited to exact normalized equality/containment or a local one-for-one OCR substitution: equal token count, no source-only delete opcode, bounded local replacement, and at most three changed characters on each side of a word. Arbitrary phrase replacement, unequal-count replacement, or any unmatched source-only suffix/prefix is not equivalence.

### Dispositions

Every evidence unit must end in exactly one disposition:

1. `included_selected`: the exact block is selected and maps to one unique Markdown span.
2. `included_equivalent`: the full unit is safely equivalent to an included selected unit/Markdown span; the report records the selected unit and span it inherits.
3. `excluded_reviewed`: an exact, used v2 allowlist row classifies it with visual evidence.
4. `required_visual_assertion`: reviewer-authored visible text absent from all three extracted views, bound to a visual crop/bbox, is present in Markdown.

Anything else is `unaccounted` and fails. A unique reader-facing region typed into Markdown but not linked to a selected source unit or an explicit visual assertion also fails: provenance must identify why that text is authoritative. One disposition may not overlap another, and no evidence unit may be consumed twice.

This rule catches the page-5 defect: the longer raster unit has an unmatched reader-facing suffix when only the shorter original unit is selected. It also catches the page-3/page-4 defect: raster page-4 block 48 is a unique unit and cannot disappear merely because it is shorter than 20 tokens.

## Reviewed allowlist v2

Do not broaden the legacy substitution allowlist. Add a closed schema such as `kb_creator.ai_merge_fidelity_reviewed_allowlist.v2` in the existing identity-bound `reviewed_allowlist` file slot, with:

- authority: run identity, source SHA-256, contract SHA-256, review-queue SHA-256, and comparison SHA-256;
- `substitutions`: the existing exact page/pattern/max-count/evidence rows with unchanged unused/overbroad failure behavior;
- `source_text_exclusions`: exact unit references and text hashes, one of `visual_only`, `advertisement`, `decorative`, `non_reader`, or `ocr_artifact`, a non-empty rationale, and an exact run-local triptych/render identity;
- `visual_text_assertions`: page, normalized/original text hashes, text, bbox/crop coordinates, non-empty rationale, and exact visual identity for visibly readable text that no required view extracted.

No wildcard pages, regex text, raw-index ranges, type-wide suppression, threshold override, or `max_count` exclusion is permitted. Duplicate, stale, unused, selected-and-excluded, or visually unbound rows fail. `visual_only` additionally names a selected decision asset and fails unless that logical asset is materialized; this prevents discarding map/handout text without preserving its visual carrier. `ocr_artifact` requires the visual evidence to demonstrate absence from the raster, not merely disagreement between OCR strings.

Legacy `{allowlist: [...]}` files remain substitution-only. They can never exclude source text and can never satisfy v2 completeness closure.

## Thresholds, reading order, and page boundaries

- V2 completeness threshold is fixed at **1.000000 on every page with any reader-required unit or visual assertion**, with **zero unaccounted units and zero source-only deletions**. There is no low-text or `<20` exemption. Explicit reviewed exclusions are dispositions, not denominator manipulation.
- Keep the current selected-block recall threshold (`0.95`) as a separate accuracy signal so large OCR/rewrite drift still fails. It must not substitute for completeness.
- Map selected text/structure units to unique, non-overlapping Markdown spans in `selected_blocks` order. The spans must be monotonically increasing. Multiset equality alone is insufficient because reordered columns can preserve recall while corrupting reading order.
- Report each adjacent page boundary. Both the last reader unit on page N and the first reader unit on page N+1 must be independently covered before any boundary normalization.
- If page N visibly ends in a hyphen and page N+1 begins with a lower-case continuation, classify the boundary as `hyphenated_continuation`, preserve both source-page sides, and verify the joined normalized lexical stream only as an additional semantic check. Never consume or move the next-page fragment to make the join pass.
- A non-hyphenated sentence continuation, such as page 4 `end of the` to page 5 `same day...`, is checked as two covered units in monotonic page order. No cross-page fuzzy search may hide a missing page-start fragment.

## Report, provenance, cache, resume, and package binding

1. Add a closed `kb_creator.ai-merge-fidelity-audit/v2` report schema. It records all authority identities, policy constants, allowlist identity/schema, per-page evidence/disposition counts, required and covered character counts, completeness `1.0`, selected recall/precision, ordered span mappings, substitutions, exclusions, visual assertions, boundary records, errors, and overall pass. Promotion must validate the full closed shape, not only `passed: true`.
2. Add queue, comparison, and reviewed submission identities to the v2 Stage05 resume/cache inputs. Extend the stage-manifest input-kind enum as needed. Packet identity is carried by the sealed queue and independently verified by the audit. Decision, allowlist, queue, comparison, packet, policy, schema, or audit implementation drift must change the Stage05 cache key.
3. Stage06 must consume the exact passed Stage05 audit identity. For v2, add it to `MERGE_PROVENANCE` (schema bump) together with queue/comparison/allowlist authority identities. The materializer rejects a v1 report, non-passing report, authority mismatch, or hash drift.
4. Promotion must require audit v2 for run-spec v2, verify its authority against the queue/submission/stages, verify the candidate provenance binds the same audit, copy the audit and reviewed allowlist into the package, and bind them in reconstruction QA and the sealed upstream manifest.
5. A v2 report may not be regenerated after Stage06 and substituted by resealing package metadata. Stage06's upstream Stage05 manifest and provenance identity must agree with the packaged audit bytes.
6. Add all new schemas and implementation files to the reconstruction implementation inventory. This intentionally makes pre-fix v2 runs non-resumable after the change.

## Legacy compatibility

- Preserve an explicit `legacy-v1` audit mode with the current selected-block report and allowlist semantics for `kb_creator.run_spec.v1` only.
- Never infer legacy mode merely because v2 authority arguments are absent. The v1 adapter must request it explicitly; a v2 adapter must require queue/comparison authority and audit v2.
- Promotion may accept audit v1 only when the sealed run itself is run-spec v1. A run-spec v2 package with audit/provenance v1 is a downgrade and fails.
- Existing v1 tests and fixtures should remain byte/shape compatible where they model legacy runs. V2 fixtures must be upgraded rather than relaxed.

## Bounded implementation surface

- `kb_creator/scripts/audit_mineru_ai_merge_fidelity.py`
- `kb_creator/pipeline/reconstruction.py`
- `kb_creator/scripts/materialize_mineru_ai_merge.py`
- `kb_creator/pipeline/reconstruction_promotion.py`
- new closed audit-v2 and reviewed-allowlist-v2 JSON schemas; the stage-manifest schema/input enum and promotion fixtures where required
- `kb_creator/tests/test_audit_mineru_ai_merge_fidelity.py`
- reconstruction control-plane, CPU packet, materializer, promotion, promotion-adversarial, and publication-control fixtures/tests affected by the new v2 shapes

No comparison producer, OCR provider, source PDF, existing immutable run, or publication content needs mutation for this bounded fix.

## Required adversarial tests

1. Short selected original block plus a longer unselected raster block with the page-5 suffix: selected recall is `1.0`, completeness fails.
2. Select the longer raster block and include the suffix: completeness passes.
3. Page N ends `malle-`; page N+1 evidence contains `ability of the human body...`; omission of the next-page unit fails even though it is under 20 tokens, while faithful two-sided preservation passes.
4. Delete one middle word, final word, whole short block, or page-start block: each fails at the exact page/unit.
5. Reorder two selected blocks while preserving every token: recall remains high but ordered-span validation fails.
6. Smart quotes, punctuation, soft/line hyphens, and OCR word joins/splits pass normalization; arbitrary or unequal-count replacements fail. Existing repeated-substitution allowlist tests remain unchanged.
7. Omitted header/page number/decorative cover text fails without an exact exclusion; exact `non_reader`/`decorative` rows pass; unused, duplicate, wrong-page, wrong-raw-index, wrong-text-hash, wrong-visual-hash, wildcard, and selected-and-excluded rows fail.
8. `visual_only` fails without a selected/materialized matching asset. Advertisement, decorative, and OCR-artifact classifications require exact visual evidence and cannot suppress another block.
9. A visual assertion is required and covered when all OCR views miss visible text; missing assertion text, wrong bbox/image identity, or unused assertion fails.
10. Missing required view, optional-view-only text, comparison hash drift, packet drift, queue drift, decision drift, allowlist drift, path escape, symlink, junction, or reparse point fails closed.
11. V2 threshold cannot be lowered below `1.0`; a zero-reader-unit visual page passes only when every extracted textual unit is explicitly disposed.
12. Stage05 argv includes exact v2 authorities; Stage06 is not invoked after an audit failure; Stage06 provenance binds the exact passed audit.
13. Promotion rejects v1 audit under v2, a replaced/resealed audit, authority mismatch, absent provenance binding, and packaged allowlist mismatch.
14. Explicit run-spec-v1 legacy tests still pass without gaining source-text exclusion capability.
15. Determinism/portability test: stable UTF-8 LF JSON, stable ordering, no scenario constants, no device path in the portable package.

## Acceptance criteria

- The old page-5 decision fixture and the omitted page-3/page-4 continuation fixture both fail v2 Stage05 with a precise page/unit error despite the old selected recall passing.
- Corrected decisions plus exact reviewed exclusions/assertions achieve per-page completeness `1.0`, zero unaccounted units, monotonic selected spans, closed boundaries, and the unchanged selected-fidelity sub-gate.
- All new contracts are closed (`additionalProperties: false`) and reject downgrade/unknown fields.
- V2 resume/cache/provenance/promotion all bind the same queue, comparison, packet, decision, allowlist, and audit identities.
- Full scoped tests pass, followed by an independent implementation critic review and the repository-required independent release review. This architecture receipt is not release approval.

## Assumptions and residual boundary

- The three required MinerU views plus explicit visual review are the best available local source evidence. No automated text audit can discover text missed by all extractors without a reviewer-created visual assertion; the v2 ledger makes that limitation explicit and reviewable instead of silently claiming PDF-complete OCR.
- Local one-for-one OCR substitutions are treated as representation variance, not omission; the existing repeated-pattern gate remains responsible for systematic glyph drift.
- The current Stage03/04 artifacts already preserve the raw blocks and visual identities required by this design.

## Blockers and next action

- Blocker: v2 source-visible completeness, report validation, audit-to-candidate provenance, and adversarial coverage are not implemented or independently reviewed.
- Blocker: implementing the fix changes sealed reconstruction implementation identity, so `20260915-cpu-first-05` cannot be resumed under it.
- Next action: orchestrator assigns the bounded implementation above to engineering/execution, then bounded QA, independent implementation criticism, a fresh immutable reconstruction run and decision revalidation, and finally the required independent release review.

## Files checked or changed

Checked read-only:

- `AGENTS.md`
- `docs/governance/nri_goal_governance.md`
- `.agents/skills/kb-creator-scenario-reconstruction/SKILL.md`
- canonical plan/context/status for `20260914-dissociation-publication`
- `critic_dissociation_decisions_run_05_closure_20260915.md`
- `kb_creator/scripts/audit_mineru_ai_merge_fidelity.py`
- `kb_creator/scripts/materialize_mineru_ai_merge.py`
- `kb_creator/scripts/compare_mineru_three_views.py`
- `kb_creator/scripts/build_mineru_visual_merge_bundle.py`
- `kb_creator/pipeline/reconstruction.py`
- `kb_creator/pipeline/reconstruction_promotion.py`
- relevant contract schemas and fidelity/materializer/control-plane/promotion/publication tests
- run `20260915-cpu-first-05`: run spec, review queue, Stage03 comparison, Stage04 stage manifest/bundle/merge packets, and current six-page decision set

Changed:

- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_source_visible_text_completeness_audit_20260915.md` only.

## Verification performed

- Read-only structural and identity inspection only; no live audit, resume, materialization, network, GPU, remote/API, or Git command was run.
- Confirmed current decision-set file byte/SHA identities match all six decision files at the final inspection point.
- Confirmed no Stage05 output directory exists in run `20260915-cpu-first-05` at the inspection point.
- Confirmed comparison identity in the review queue is `449244` bytes / `7136F138D81C0A47F1CF30918985D7ED1B41BCDC36BF30A0B38860039BCCB19E` and the queue seal is `4D68E89A72B628F735542BD693580E30897980B52D62BD6BEABE41ECD10B271F`.

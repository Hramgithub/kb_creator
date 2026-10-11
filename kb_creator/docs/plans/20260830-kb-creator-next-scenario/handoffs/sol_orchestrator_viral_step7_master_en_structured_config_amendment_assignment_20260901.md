# Viral Step 7 MASTER_EN — executable structured config amendment

## Ownership and scope

- Owner: NRI architecture/content role, `gpt-5.6-sol` / `high`.
- Orchestrator remains `/root`; integration and downstream authorization do not transfer.
- Allowed writes are exactly:
  - `kb_creator/working/viral/master_en/publication_config_v1.json`;
  - `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_content_viral_step7_master_en_structured_config_amendment_20260901.md`.
- Accepted v4/source PDF, builder/verifier/tests, plan/context, candidate/output, MinerU surfaces, ignored bytecode and Git are read-only.
- Use `python -B` for every Python read. Do not delete or refresh the existing `__pycache__` artifact.
- Do not run MinerU or the historical 371/119/490 matrix.

## Pinned inputs

- Whole publication config: 741,991 bytes / SHA-256 `5391A55C2ABEB0835F3526BE6F6CD06334A9001DD3B00B168EDF4BB18A20A0BA`.
- Canonical current `structured_content` subtree: 135,802 bytes / SHA-256 `84E740194388A568144FE97E4098855A2F868174D9865DBAAF5C1252E18AE5F2`.
- Authoritative 29-row architecture audit:
  `handoffs/sol_architect_viral_step7_master_en_structured_contract_audit_20260901.md`,
  31,635 bytes / SHA-256 `5B609CBBF8664CAF5FD4338300F3C30ED01A656F49FD5395FACE03DB009B6A1F`.
- Accepted v4 package inventory SHA-256 `68C17FB765A89C6146398868E61F1F6EB7B2FE4EAFBA8C2C2C8F42260BBDBA83`.
- Accepted xref executor is read-only at builder SHA-256 `C3096022D395A26CB05689E401E4B219F591BE99C52DD85B12B142F06CCF13F6` and test SHA-256 `BF03D81A6FDFD1F143A12585F83B4AD003DA18371C04F14EAAE584A9B6030023`.

Read the architecture audit in full. Its per-row matrix, mismatch list, minimal schema and two seam corrections are binding; this packet does not replace their exact source facts.

## Required amendment

1. Keep the existing 29-row `structured_content` list and all existing top-level classes. Do not add a parallel framework or generated reader Markdown.
2. Remove `accepted_v4_markdown` from all 33 `source_units`. The only allowed source-unit keys become exact `page`, repo-relative `path` and uppercase `sha256`. The hash-bound accepted page file is the sole authorial-text authority; config must contain zero embedded whole-page Markdown and zero duplicated authorial bodies.
3. Replace each row's current open semantic `fact_expectations` with the smallest closed class-specific executable contract described in the architecture receipt:
   - common exact region fragments with page, exact binding anchor, `line_exact` start and exclusive end or deterministic record-count termination;
   - pipe tables versus numbered-record series, exact source header tokens/line, exact per-fragment ordered first-column keys, explicit repeated/headerless continuation, exact attached-note selectors;
   - cards/statblocks with exact ordered source heading/section/field label tokens, exact boundaries, required literal substrings, literal lexical protections and forbidden literal tokens;
   - visual forms with exact asset id/page/owner/SHA/reader/full-page identity, exact ordinary + structured review ids, `emit_exactly_once=true` and `semantic_duplicate_forbidden=true`.
4. Apply every row correction literally from the 29-row matrix. Critical examples are mandatory, not exhaustive:
   - Rumors header `Roll / Rumor` and repeated continuation;
   - rowing five printed rows with `STR Roll / Result`;
   - DSS throw three columns and printed ordering;
   - Outdoor/Hospital/Catacomb and two D10 tables as exact numbered series;
   - Taint `Modifiers` plural;
   - no invented Plague Monk stats;
   - Reliquae two Infection tables and no Plague Zombie table;
   - Iuramentum includes `Skills Gained`; Control Reliquae has only literal `Cost:` / `Casting Time:` fields;
   - pregen backgrounds use exact sections, and blank form ends with `Fellow Investigators`.
5. Preserve literal source oddities as explicit exact protections: `Hastaÿk's corruption`, `avatar of Hasalÿk`, and `a significant portion is ties up in video and audio gear.` Do not normalize or editorially repair accepted v4.
6. Correct exactly two binding seams as specified by the audit:
   - add page 59 to `viral-appendix-encounters-outdoor.continuation_pages`; remove only the page-start locator from `viral-appendix-encounters-hospital`, retaining its exact heading locator;
   - add page 67 to `viral-appendix-new-mythos-horrors-reliquae.continuation_pages`; remove only the page-start locator from the Infection child, retaining its exact first infection-table locator.
   Update matching hierarchy/source-disposition ownership only if required by the unchanged strict resolver; do not alter unrelated bindings.
7. Reconcile the accepted exact xref contract after those seams. In particular, `p067-infection` source line 7 will belong to the Reliquae root fragment while still linking to the Infection target; update only its `owner_anchor` if the corrected resolver proves that ownership. All 41 source lines/42 segments and all generated/source counts must remain exact.
8. Preserve all unrelated config data and counts: 13 top keys, 168 hierarchy rows, 124 dispositions, 237 xrefs, 41 handouts, 29 structures, 123 assets, 91 visual rows and nine noise rows. Canonical UTF-8/LF JSON and stable ordering remain required.

## Verification

Because the current builder intentionally expects the pre-amendment structured schema, do not weaken it or edit code to make this config pass. Use bounded read-only audit code instead:

- parse canonical JSON and prove all exact counts/closed per-class shapes;
- prove zero `accepted_v4_markdown` keys/values and zero embedded page bodies;
- validate every source-unit path/hash against accepted v4;
- validate every region selector/token/ordered fact against its exact accepted page and declared binding fragment;
- run the unchanged current `resolve_bindings` directly on parsed JSON and require 219 locator checks, 1,935 blocks, 1,862 owned + 73 generated and zero unowned/duplicate/unauthorized suppression after seam correction;
- run the unchanged current `resolve_source_xrefs` directly and require 41/41 source rows, 42/42 segments, valid owners/targets and zero errors after the p067 owner update;
- prove 11/10/2/6 exact class counts, 29 unique ids, 28 logical owners, and six exact form assets/reviews;
- prove no config mutation outside `structured_content`, the two seam rows and the necessary p067 xref owner field.

## Receipt

Return `PASS_STRUCTURED_CONFIG`, `FAIL`, or `BLOCKED` with:

- old/new whole config bytes/SHA and old/new canonical structured-subtree bytes/SHA;
- exact schema delta and count of removed embedded pages/characters;
- 29-row compact evidence table with class/regions/facts/owner/representation/result;
- both seam before/after declarations and unchanged-resolver conservation evidence;
- p067 xref before/after owner plus 41/42 exact xref evidence;
- six visual-form asset/review closure;
- explicit zero fuzzy/zero authorial re-write/zero duplicated body/zero code/candidate statement;
- exact changed files, elapsed time and token availability.

A PASS unlocks only Terra/medium implementation in the existing builder + compact builder tests. C2b, verifier implementation, durable candidate, translation and publication remain closed.

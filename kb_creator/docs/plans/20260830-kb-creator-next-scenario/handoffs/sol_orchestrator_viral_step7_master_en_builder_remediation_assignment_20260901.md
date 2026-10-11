# Viral Step 7 MASTER_EN builder engineering remediation assignment

Date: 2026-09-01  
Owner: same bounded `gpt-5.6-terra` engineer at `medium`  
Working directory: `D:\NRI\.worktrees\kb-creator-viral`

## Decision and baseline

The first engineering attempt is a truthful frozen `FAIL`, not an accepted
implementation. Its receipt is
`terra_engineering_viral_step7_master_en_builder_20260901.md`; it reported only
3 tests and explicitly omitted required rendering, semantic gates and negative
coverage. Baseline identities are:

- builder 6,055 bytes / SHA-256
  `B077342E0A04D3881F3E2C9460DDBBD14CDD1B24420F75AC77012E697A39588A`;
- verifier 2,509 bytes / SHA-256
  `A551E16A278DB6CEE415BA92D5A930DF1D34AFA2CE990A0696B3209510BA4516`;
- builder test 2,047 bytes / SHA-256
  `5607DB6A34C5C2BDF848A17E6B8B5CA7554F405E8810390992ACA6335C780279`;
- verifier test 888 bytes / SHA-256
  `C3B67E7516E19F3D30C87AC179F26919478249D63F973AFB3EE16451EFDF80BA`.

Replace/supersede the incomplete implementation. Do not preserve behavior just
because the three scaffold tests pass.

## Accepted production-shaped interface

Read completely before editing:

- original sealed engineering packet
  `sol_orchestrator_viral_step7_master_en_builder_engineering_assignment_20260901.md`,
  8,386 bytes / SHA-256
  `83FD2FF13C6EC47BE82A3593DC61F62569D58ACDDE9F14F6D05E2E532C7F0231`;
- accepted architecture packet SHA-256
  `36B20416AEF0D7B7031859DAC119D65D99B61F0CA10C25CB44C34B0F23036117`;
- accepted explicit config
  `kb_creator/working/viral/master_en/publication_config_v1.json`,
  630,533 bytes / SHA-256
  `9B915863B058EA0DF73203E63FD338394159E9922AF4B21D5168FBE2E82DBADE`;
- config receipt
  `sol_content_viral_step7_master_en_publication_config_20260901.md`,
  9,393 bytes / SHA-256
  `3AE6CA2930837D265BD7895078F9AB819F5CE4B6BB4253FB1276B37051A411E8`;
- accepted v4 reconstruction/package/review identities pinned by the config.

The config has the exact 13 architecture top-level keys and one closed row
shape per array except the two explicit asset variants. Counts are:

- hierarchy 168;
- primary source disposition 124;
- xrefs 237;
- handouts 41;
- structured content 29;
- assets 123 = 121 accepted + 2 source renders; 107 reader + 16 evidence-only;
- visual review 91;
- reader-noise classifications 9.

Use the actual nested rows. Do not invent an alternate fixture-only config
shape. In particular:

- `accepted_reconstruction` contains nested file identity objects and an
  external repository-relative acceptance receipt path; it is not a receipt
  inside the package;
- accepted package inventory uses ordinal UTF-8 LF rows
  `relative_path<TAB>bytes<TAB>UPPER_SHA256<LF>`, not JSON-row hashing;
- every source row uses `page`, `source_path`, `primary_unit_id`, `role`,
  `disposition`, `target_anchors`, nested `sub_units`, preservation/suppression
  fields and closure status;
- each hierarchy row is explicit
  `anchor,level,parent_anchor,semantic_role,source_pages,title,toc_entry`;
- xrefs are selected by `source_page`, `source_selector`, `visible_text`,
  `classification`, `target_anchors` and `link_policy`;
- structured rows embed accepted-v4 source-unit Markdown/hashes plus exact fact
  expectations, classification, representation, owner and placement;
- accepted assets pin actual bytes/SHA/path/owner/representation; render assets
  use the separate `source_page_render` shape;
- external gates in `document` are required and pending.

## Exact ownership

You are not alone in the worktree. Do not revert other changes. You may modify
only the same four code/test files and create one new receipt:

- `kb_creator/scripts/build_scenario_master_en.py`;
- `kb_creator/scripts/verify_scenario_master_en.py`;
- `kb_creator/tests/test_build_scenario_master_en.py`;
- `kb_creator/tests/test_verify_scenario_master_en.py`;
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_step7_master_en_builder_remediation_20260901.md`.

The failed receipt is immutable. Config, source, accepted v4, plan/context,
working outputs, root checkout, dependencies, caches and Git are read-only.
The transient root config path is absent; do not recreate or touch it.

## Required remediation

1. Implement the actual closed nested config schema above with precise error
   messages. Reject unknown/missing fields and wrong types/values before target
   creation. Provide a read-only preflight mode or function that validates the
   real config/package/source/receipt identities without creating the target.

2. Resolve repository-relative config paths against the repository/worktree
   root deterministically and keep them inside it. Recheck contract, source,
   every accepted reconstruction sidecar, external acceptance receipt, all 121
   accepted asset binaries and ordinal package inventory. Never read source PDF
   as text or `SELECTED_OVERLAY.pdf` as a reader source.

3. Assemble from the 124 pinned `source_path` page Markdown files under explicit
   source dispositions. Remove only classified technical reader noise; preserve
   page text otherwise. Apply hierarchy/anchors/TOC, relocation, handout units,
   xrefs, structured facts and asset placement from config data. Demote/rebuild
   headings so the output has one H1 and every declared anchor once. Do not just
   prepend 168 headings to the untouched full reconstruction.

4. Xref handling must be selector/page-scoped and support repeated visible text,
   multi-target ranges and the one external bibliographic retention row. It must
   prove all 237 rows classified and all internal targets resolve without global
   blind `.replace()`.

5. Enforce 124 page preservation/disposition, 41 exact handout identities,
   p82 contextual exclusion, all 29 structured expectations, 123 asset ownership
   rows and 91 declared visual-review units. Evidence-only assets must never be
   linked or copied into reader output. Reader assets must be placed once at the
   owning anchor with declared alt text and content-addressed names.

6. Implement declared `source_page_render` via discovered Poppler `pdftoppm`
   version `26.05.0`: page-select only, MediaBox, rotation-upright, 200 DPI PNG,
   1700x2200 RGB white no-alpha, metadata stripped. Use Pillow after Poppler to
   normalize RGB/metadata deterministically. Record renderer/version/arguments,
   source/page/output identities in provenance. Refuse version/settings/page or
   dimension mismatch. Do not run the PDF authoring marker; it already ran once
   for this logical goal.

7. Generate exact closed topology and deterministic provenance/disposition/
   asset/QA/inventory sidecars. Define `INVENTORY.json` non-self-referential
   scope explicitly (all candidate files except `INVENTORY.json`) with ordinal
   row digest, and have verifier reproduce it. Candidate and QA status must be
   review-only; external visual/release/user gates remain pending and cannot be
   forged. No acceptance file.

8. Independent verifier must not import builder. It must re-parse the full config
   and independently recompute predecessor/config/source/output identities,
   closed topology/inventory, semantic anchors/TOC/xrefs, disposition, handouts,
   structured expectations, reader/evidence asset closure, noise/lexical
   protection and external pending gates. Never trust QA sidecar alone.

9. Add explicit source-authorial conservation checks from config and classify
   every visible lexical delta as structural/link/relocation/authorized. Current
   authorized editorial lexical delta count is zero. Preserve the seven protected
   source oddities; verify p80 `Babez` remains present and scheduled for visual
   reinspection.

## Focused tests — bounded by failure class

Replace the three toy nodes with production-shaped synthetic fixtures matching
the exact current config row shapes. Use one or a small number of nodes per
failure class, not a combinatorial mutation matrix; approximately 25-50 focused
nodes is appropriate. Cover every item in the original packet, plus:

- actual 13-key/nested-schema parsing and real production config read-only
  preflight with exact SHA `9B915863...DBADE` and no target creation;
- correct ordinal predecessor/candidate inventory and external receipt path;
- multi-page assembly, one H1, hierarchy/parent closure, generated TOC;
- selector-scoped repeated/multi-target/external xrefs;
- source preservation and forbidden PDF/overlay text fallback;
- 41-label variants and p82 exclusion;
- structured fact/field/table mismatch rejection;
- evidence-only leakage and asset ownership/alt/path/hash failures;
- real valid synthetic PDF from `pypdf`, actual discovered Poppler render,
  Pillow RGB/no-alpha/1700x2200/metadata checks and two-build byte equality;
- Poppler version, page, dimension and settings mismatch rejection;
- candidate tampering across every sidecar class and independent verifier;
- forged gates/acceptance file/current time/extra output/path escape;
- protected source oddity loss and unauthorized lexical delta;
- no import from builder in verifier.

`pypdf 6.14.0`, Pillow `12.2.0` and bundled Poppler `26.05.0` are currently
available. Do not install anything. Run only the two owned focused test files
with bytecode/cache disabled, `py_compile`, owned-file `git diff --check`, and
one read-only production-config preflight. Do not build the real Viral target,
render real source pages, run unrelated suites or 371/119/490.

## Receipt

Result must be `PASS`, `FAIL` or `BLOCKED`. Record exact new file identities,
actual collected/passed node count, actual Poppler synthetic render evidence,
production-config preflight result, negative-class coverage, limitations and
next action. A small green subset is still `FAIL`; do not claim conformance
unless every required class is implemented and tested.


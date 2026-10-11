# Viral Step 7 reusable MASTER_EN builder engineering assignment

Date: 2026-09-01  
Owner: `gpt-5.6-terra` engineering at `medium`  
Working directory: `D:\NRI\.worktrees\kb-creator-viral`

## Purpose

Implement and test the reusable, scenario-data-driven MASTER_EN builder and a
separate independent verifier required by the accepted Step 7 architecture.
This task owns infrastructure only. It must not author the Viral publication
config, build a real Viral candidate, render real Viral pages, edit accepted v4,
perform content decisions, translation, HTML/PDF publication, promotion or Git.

## Required authorities

Read completely before implementation:

- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_viral_step7_master_en_publication_packet_20260901.md`,
  43,067 bytes, SHA-256
  `36B20416AEF0D7B7031859DAC119D65D99B61F0CA10C25CB44C34B0F23036117`;
- especially sections 3-12: page disposition, hierarchy/anchors, xrefs,
  handouts, structured content, assets, lexical conservation, traceability,
  deterministic interface/output contract and gates;
- accepted reconstruction receipt
  `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_step6a_reconstructed_en_package_v4_review_20260901.md`,
  16,598 bytes, SHA-256
  `E515C184F7287151EA0D3E4A12398C1D36204210A7E399E717F496B0C5E77890`;
- nearest `AGENTS.md`, governance and existing `kb_creator/scripts`/tests for
  deterministic JSON, fail-closed fresh-target and inventory conventions.

The actual v4 package is read-only evidence at
`kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4`.
Do not encode its content or hashes in reusable code.

PDF render requirements follow the loaded PDF skill: use Poppler for declared
`source_page_render` operations, treat text extraction as insufficient for
visual fidelity, and make visual QA a separate later gate. The PDF authoring
marker has already been run exactly once for this logical goal; do not run it
again. This engineering task may create only synthetic test PDFs/assets inside
pytest-managed temporary roots, never a real Viral render.

## Exact ownership

You are not alone in the worktree. Do not revert or overwrite any other change.
You may create or modify only:

- `kb_creator/scripts/build_scenario_master_en.py`;
- `kb_creator/scripts/verify_scenario_master_en.py`;
- `kb_creator/tests/test_build_scenario_master_en.py`;
- `kb_creator/tests/test_verify_scenario_master_en.py`;
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_step7_master_en_builder_20260901.md`.

No config, schema file outside the scripts, source, v4 package, working output,
plan/context, accepted/production artifact, dependency install, cache cleanup or
Git mutation is authorized. If a missing dependency prevents bounded synthetic
tests, report `BLOCKED`; do not install or redesign around it silently.

## Required implementation contract

1. Provide the exact CLI shape:

   `python -B kb_creator/scripts/build_scenario_master_en.py --contract <json> --reconstruction-package <accepted-root> --publication-config <json> --source-pdf <pdf> --target <fresh-root>`

   and an independent verifier CLI accepting config/source/package/candidate
   inputs plus expected candidate inventory when appropriate. The verifier must
   not import the builder implementation.

2. Accept only closed config schema
   `kb_creator.master_en_publication.v1` with the minimum top-level fields from
   architecture section 11. Fail unknown/missing fields where the schema is
   closed. Scenario rules live in arrays, never Python conditionals keyed to
   `viral`, Innsmouth or page numbers.

3. Recheck all configured byte/SHA identities for contract, source PDF,
   accepted reconstruction root/inventory, `RECONSTRUCTED_EN.md`, QA,
   provenance, asset manifest and reconstruction-acceptance receipt before any
   target write. Source PDF may be read only by declared `source_page_render`
   asset operations; it is never a fallback text source.

4. Target must be absent/new. Refuse occupied target, overwrite, path escape,
   absolute/parent-traversal reader paths, hidden fallback input, unpinned
   predecessor, duplicate anchor/asset/handout/page ownership, missing xref,
   extra output and current-time-dependent content. A failed preflight creates
   no target. A post-write failure remains a non-accepted candidate and must be
   truthfully reported; do not delete it automatically.

5. Generate only the closed candidate topology:

   - `MASTER_EN.md`;
   - `MASTER_EN.provenance.json`;
   - `SOURCE_DISPOSITION.json`;
   - `ASSET_MANIFEST.json`;
   - `MASTER_EN.qa.json`;
   - `MASTER_EN.qa.md`;
   - `INVENTORY.json`;
   - `assets/<sha256>.<ext>`.

   Never generate `MASTER_EN.acceptance.json` in a review candidate.

6. Implement generic operations needed by sections 3-10, driven entirely by
   config: retain/structure/relocate/link semantic reconstruction units;
   explicit hierarchy/anchors/TOC; exact xref replacement; handout unit mapping;
   structured table/statblock/card materialization from config fact ledgers;
   accepted-asset copy/placement; evidence-only suppression; declared reader
   noise removal; deterministic `source_page_render` for clean cover/back cover;
   provenance spans and lexical-delta classification. Do not silently copyedit.

7. Enforce all automatable parts of architecture gates 1-9. Gates 10-12
   (full visual QA, independent release review, explicit user reading
   acceptance) remain external/pending and must never be reported as passed by
   the builder. Candidate status is review-only, never accepted/released.

8. Serialization is UTF-8 without BOM, LF, stable JSON ordering/indentation,
   stable config array order, content-addressed assets, metadata-stripped
   deterministic source renders and Python/codepoint ordinal portable inventory
   rows. Two clean builds from identical fixture/config inputs must be
   byte-identical with the same inventory digest.

9. The verifier independently parses files/config and rechecks identities,
   closed topology, inventory, hashes, anchors/TOC/xrefs, page/source
   disposition, handout mapping, structured facts, asset closure, reader-noise
   absence, lexical-delta classifications and review-only status. It cannot
   simply trust `MASTER_EN.qa.json` or call/import builder functions.

10. Keep the implementation reusable, stdlib-first and explicit. A narrow
    Poppler subprocess seam is allowed for declared renders. Discover tools
    from PATH/bundled runtime; do not hard-code device paths. Capture renderer
    version/settings in provenance and fail if config pins do not match.

## Required tests

Use production-shaped but compact synthetic fixtures. At minimum cover:

- happy-path build plus independent verifier pass;
- two fresh builds byte-identical, including render asset when Poppler is
  available in the configured test seam;
- exact closed output topology and absence of acceptance file;
- accepted reconstruction/source/contract/receipt hash mismatch fails before
  target creation;
- occupied target and path escape refusal;
- source PDF cannot supply undeclared/fallback text;
- unknown config field/schema mismatch;
- duplicate/missing source page disposition;
- duplicate/missing anchors, unresolved xrefs and unclassified printed refs;
- handout label/ordinal/page mismatch including variants;
- structured table/statblock fact mismatch and raster evidence substitution;
- orphan/missing/duplicate asset and evidence-only reader leakage;
- reader technical-noise and unauthorized lexical delta;
- tampered candidate/inventory/QA/provenance rejected independently;
- verifier does not import builder implementation;
- external gates 10-12 remain pending and cannot be forged to pass.

Run only the two new focused files with bytecode/cache disabled, plus
`py_compile` and `git diff --check` on owned files. Do not run the historical
371/119/490 matrix or unrelated suites.

## Receipt

The receipt must report exact files/hashes/bytes, CLI/schema/output contract,
test node count and result, dependency/tool behavior, limitations, blockers and
next action. Do not claim the real Viral config/candidate exists. Result is
`PASS`, `FAIL` or `BLOCKED`; a test failure is evidence, not permission to edit
outside scope.


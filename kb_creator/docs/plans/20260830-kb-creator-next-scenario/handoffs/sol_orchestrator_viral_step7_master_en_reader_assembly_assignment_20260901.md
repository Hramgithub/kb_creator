# Viral Step 7 MASTER_EN Phase C2a reader-assembly assignment

## Role and scope

- Owner: `gpt-5.6-terra` engineering, `medium`, accelerated service when exposed.
- Orchestration remains with `/root`.
- Write only `kb_creator/scripts/build_scenario_master_en.py`, `kb_creator/tests/test_build_scenario_master_en.py`, and new immutable receipt `handoffs/terra_engineering_viral_step7_master_en_reader_assembly_20260901.md`.
- Verifier/tests, config, source/reconstruction, plans/context, durable candidate/output, governance and Git are read-only. Preserve all other edits.

## Pinned foundation

- Config: 717,058 bytes, SHA-256 `314058BEC330D16CC26B4D1D5E3DA07E3C98AFF8B3820AF5ECE2644648FE5D0E`.
- Builder: SHA-256 `3CEFD63C6B7EB7B921E276AC29742A12951B01C2593401ABB6B427CBD3933E18`.
- Builder tests after orchestrator integration: SHA-256 `C7F621054487FEACCEF88281BD7247114D1A80977F373A3403EC72CE2756EF58`.
- C1 strict evidence: 168 bindings, 219 locators, 1,935 blocks = 1,862 explicit owners + 73 generated navigation; all error counts zero; focused builder+verifier tests 20 passed.
- Accepted architecture: `sol_architect_viral_step7_master_en_publication_packet_20260901.md` and `sol_architect_viral_step7_master_en_assembly_binding_remediation_20260901.md`.

## Required C2a implementation

1. Add a reusable reader-assembly function that consumes only the validated config, C1 binding index and Phase B asset ledger. It writes only into a caller-created empty temporary staging root. Normal production CLI remains fail-closed with `implementation_phase_incomplete`.
2. Produce deterministic UTF-8/LF/no-BOM `MASTER_EN.md` with exactly one H1 `Viral`, all 168 unique explicit anchors in binding order, configured heading levels/titles, and generated Contents entries for every `toc_entry` row.
3. Execute each binding action exactly: insert/replace headings, retain line-prefix remainder, consume continuation labels without losing body, preserve shared prefixes once, append continuation pages, and emit generated/physical/owned units without duplicate source spans.
4. Rewrite reader image references to content-addressed `assets/<sha>.<ext>` using the Phase B ledger and config alt text/ownership. Reader Markdown may reference all and only the 107 reader assets (105 accepted + clean p1/p124 renders); 16 evidence-only assets remain unreferenced by reader text. Never use the overlay or incomplete cover crops as covers.
5. Preserve accepted-v4 body lexical content exactly except already authorized structural operations. Remove only declared technical/duplicate reader-noise classes. Keep authorial oddities, p80 note, table/statblock values and handout text exact.
6. Apply configured xrefs deterministically: generated TOC/handout/map/pregen indices and source-selector links. Visible wording must remain unchanged; every internal target resolves and the sole external bibliographic row remains visible non-link text.
7. Render structured tables/cards/statblocks from the already accepted `accepted_v4_markdown`/facts without lexical edits or duplicate evidence crops. Preserve 41 physical handouts, six map units over seven pages, 12 pregen/template units and 29 structured units.
8. Return in-memory/staging evidence: Markdown bytes/SHA, anchor/link/asset counts, unit counts, lexical-conservation result and reader-noise findings. Do not write provenance/QA/disposition/manifest/inventory sidecars yet; those are C2b.

## Compact verification

Extend the focused suite by meaningful classes only; target roughly 28-36 builder+verifier nodes total. Include:

- exact real temporary reader build and two-run byte identity;
- 1 H1 / 168 unique anchors / all internal links resolve;
- 107 reader refs, zero evidence-only refs, clean p1/p124 renders;
- action semantics for p42 prefix, p20-22 continuation, p74/p75 shared prefix, p93 multi-unit and p106-107 map;
- p80 handwritten note exact text and reader asset presence;
- 41 handouts, six maps/seven pages, 12 pregens, 29 structures;
- generated navigation/xrefs preserve visible text;
- zero source comments, technical paths/hashes/overlay scaffolding or unauthorized lexical delta;
- occupied staging/output collision refusal and no acceptance/sidecar/candidate output;
- retained C1 conservation, Phase B assets and fail-closed normal CLI.

Use the real amended config/source only inside fresh `TemporaryDirectory` roots and normal cleanup. Run compile, compact builder+verifier pytest and scoped diff-check. Do not run MinerU or 371/119/490.

## Receipt

Return `PASS_READER_ASSEMBLY`, `FAIL`, or `BLOCKED`; changed hashes, exact test count, two-run reader hashes/bytes, all count/gate evidence, any lexical/noise gaps, forbidden-output absence, remaining C2b work, elapsed time and token use if available. No durable candidate or release claim is authorized.

# Viral Step 7 MASTER_EN — executable xref contract correction assignment

## Ownership and scope

- Owner: NRI architecture/content role, `gpt-5.6-sol` / `high`.
- Orchestrator remains `/root`; ownership of plan, integration, user-facing decisions and downstream authorization does not transfer.
- Allowed writes are exactly:
  - `kb_creator/working/viral/master_en/publication_config_v1.json`;
  - `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_content_viral_step7_master_en_xref_contract_correction_20260901.md`.
- Source PDF, accepted v4 reconstruction, builder, verifier, tests, plan/context, candidate/output, MinerU surfaces and Git are read-only.
- Do not run MinerU or the historical 371/119/490 mutation matrix.

## Pinned inputs

- Publication config: 717,058 bytes / SHA-256 `314058BEC330D16CC26B4D1D5E3DA07E3C98AFF8B3820AF5ECE2644648FE5D0E`.
- Builder: SHA-256 `3D84DA82F31CCADAA8EFA831C21CB12DD7C35232A4B7F90E6B6BC215C8009CEE`.
- Builder tests: SHA-256 `608E65A96C8916AD4D1B4E699E97DEA5D0B929785A98AA19D66A906B06D532D1`.
- Accepted reconstruction remains:
  `kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4`.
- The publication architecture packet remains authoritative, especially section 5: internal references retain the visible semantic phrase, remove/replace the printed page locator construct with a Markdown link, and preserve the sole Keeper Rulebook reference as visible non-link text.

## Why this correction is required

The first corrected C2a implementation exposed that the config is closed by count but not yet executable by exact source evidence:

- 237 xref rows = 196 generated navigation rows + 41 source-page rows;
- 236 are internal and one is external bibliographic;
- a fresh read-only audit of the 41 source rows found only 28 whose current `visible_text` occurs exactly once on the declared accepted-v4 page; 13 have zero exact occurrence;
- several numeric `line N` selectors do not point at a line containing the declared phrase;
- the current builder therefore appends generated links at EOF and uses `target_anchors[0]`, which is not accepted;
- the handout-range rows `p032-handout-7` and `p037-handout-21` have multiple targets and need an explicit readable execution rule rather than arbitrary first-target selection.

Terra must not infer or fuzzy-match around these content-contract gaps.

## Required config correction

1. Audit all 237 rows, with an exhaustive accepted-v4 check of all 41 source-page rows. Generated TOC/handout/map/pregen rows may not change meaning or inventory.
2. Establish the smallest closed executable row contract that makes each source xref deterministic without fuzzy search. Each source row must explicitly and separately encode or unambiguously identify:
   - the exact accepted-v4 page and exact source line selector;
   - the exact source substring/construct to transform or validate;
   - the exact reader-facing semantic text after the authorized removal of any internal printed-page locator;
   - the exact output target or targets and link behavior.
   A minimal conditional field amendment is allowed when the existing seven fields cannot carry these facts without overloading. Do not add a new top-level key or a parallel framework.
3. Every source selector must resolve exactly one raw accepted-v4 line on its declared page and every declared source substring must occur exactly once within that resolved line. Zero/multiple matches are forbidden. Record the resolved raw line number and owning assembly anchor in the receipt.
4. Internal page references must follow the architecture policy: retain the semantic phrase as link text and remove only the printed page locator/construct. Do not silently edit authorial wording beyond that authorization.
5. Room and handout references without a printed page locator retain their complete accepted source wording, with Markdown link syntax added around the explicitly declared segment(s).
6. Resolve both multi-target handout rows explicitly. The config/receipt must state the exact reader text, link segmentation, targets and derived link-count contribution. Do not select `target_anchors[0]` merely because Markdown has one target per link.
7. The external `p057-keeper-rulebook` row must resolve exactly and remain its complete visible source wording with no internal link and no invented URI.
8. If accepted v4 contains a suspect/corrupt character in a referenced phrase, do not repair it silently in Step 7. Preserve accepted-v4 evidence and return `BLOCKED` with the exact source/config discrepancy if an editorial correction is required.
9. Preserve all unrelated config content and counts: 13 top-level keys, 168 hierarchy rows, 124 dispositions, 237 xrefs, 41 handouts, 29 structured rows, 123 assets, 91 visual rows and nine noise rows. Canonical UTF-8/LF JSON and stable ordering remain required.

## Required evidence

The receipt must return `PASS_XREF_CONFIG`, `FAIL`, or `BLOCKED` and include:

- old/new config bytes and SHA-256;
- exact schema delta, if any;
- generated/source/internal/external counts;
- 41/41 selector-line and source-substring exact-resolution evidence;
- per-row compact table: xref id, page, resolved raw line, owner anchor, source substring, reader text, targets and emitted-link contribution;
- the two multi-target decisions and total derived internal-link count;
- external non-link proof;
- zero fuzzy/zero target0-fallback/zero silent lexical correction statement;
- changed-file list, elapsed time and token availability.

No builder/test change or candidate construction is authorized by this packet. A PASS unlocks only a bounded Terra/medium implementation against the amended xref contract.

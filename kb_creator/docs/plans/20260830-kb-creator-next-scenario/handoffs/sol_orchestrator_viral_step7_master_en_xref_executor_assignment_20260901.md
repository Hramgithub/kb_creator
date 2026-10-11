# Viral Step 7 MASTER_EN — exact xref executor assignment

## Ownership and scope

- Owner: NRI engineering role, `gpt-5.6-terra` / `medium`.
- Orchestrator remains `/root`; integration and downstream authorization do not transfer.
- Allowed writes are exactly:
  - `kb_creator/scripts/build_scenario_master_en.py`;
  - `kb_creator/tests/test_build_scenario_master_en.py`;
  - `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_step7_master_en_xref_executor_20260901.md`.
- Publication config, source PDF, accepted reconstruction, verifier, plan/context, candidate/output, MinerU surfaces and Git are read-only.
- Another contributor may add only a new structured-contract audit receipt. Do not revert or overwrite unrelated work.
- Do not run MinerU or the historical 371/119/490 matrix.

## Pinned inputs

- Amended publication config: 741,991 bytes / SHA-256 `5391A55C2ABEB0835F3526BE6F6CD06334A9001DD3B00B168EDF4BB18A20A0BA`.
- Xref config receipt: 8,965 bytes / SHA-256 `72145F9055E1CC042D0BBB56A3AE15B0531B577CE134055D57807988A50E6DEA`.
- Baseline builder: SHA-256 `3D84DA82F31CCADAA8EFA831C21CB12DD7C35232A4B7F90E6B6BC215C8009CEE`.
- Baseline builder tests: SHA-256 `608E65A96C8916AD4D1B4E699E97DEA5D0B929785A98AA19D66A906B06D532D1`.
- Accepted reconstruction remains `kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4`.
- Existing Phase B asset materialization, strict C1 conservation and corrected C2a binding/action/asset interleaving must remain intact.

## Required implementation

1. Replace the single old xref row parser with an exact conditional schema:
   - 196 generated rows retain their existing seven keys and one of `generated_toc`, `generated_handout_index`, `generated_map_index`, `generated_pregen_index`;
   - 41 source rows have the exact amended keys and require `source_selector == line_exact`, exact full `source_line`, exact `owner_anchor`, and ordered non-empty `segments` with exact keys `source_text`, `reader_text`, `target_anchor`, `emit_link`;
   - internal source rows use `replace_exact_segments`; the external row uses `validate_exact_non_link`;
   - validate exact counts from config data, not constants used as PASS claims.
2. Validate every source row against accepted v4 and C1 ownership before assembly:
   - `source_line` occurs exactly once on its declared page and exactly once inside its declared owner binding spans;
   - every ordered `source_text` occurs exactly once and segments do not overlap;
   - `reader_text` is explicit and non-empty;
   - linked segments have a valid exact target anchor; non-link segments have null target and cannot invent a URI;
   - `target_anchors` closes exactly over the emitted segment targets;
   - fail on zero/multiple line, zero/multiple/overlapping segment, wrong owner, wrong page, missing target, target0 fallback or undeclared field.
3. Execute generated rows only at their owning generated section:
   - `generated_toc` -> `viral-contents` (137 rows);
   - `generated_handout_index` -> `viral-player-handouts` (41 rows);
   - `generated_map_index` -> `viral-keeper-maps` (six rows);
   - `generated_pregen_index` -> `viral-pregenerated-investigators` (12 rows).
   Preserve config order and exact visible labels/targets. Do not build a parallel hierarchy-derived TOC and do not append any index at EOF.
4. Execute each source row inside its exact owner span. Replace only its ordered `source_text` segment with `[reader_text](#target_anchor)` when `emit_link` is true. For the external row, validate the segment and leave the complete source wording unchanged and unlinked. Preserve all surrounding source bytes except already authorized structural actions.
5. Explicitly prove the two range decisions:
   - `p032-handout-7` emits exact `Handouts #1-7` once as one link to `viral-player-handouts`;
   - `p037-handout-21` emits `Handout #30` and `Handout #31` as two links within the one original line, preserving all joining words/punctuation.
6. Remove the current EOF xref append loop completely. Each of 237 xref rows must be executed exactly once. Return derived evidence for 196 generated rows, 41 source rows, 42 source segments, 41 source link contributions, one external non-link and 237 total internal links. Every internal target must resolve to one of the 168 emitted anchors.
7. Populate each owner transformation ledger's `xref_ids` from actual execution. The union must cover all 237 ids exactly once, with generated rows attributed to their owning generated section and source rows to declared owner anchors.
8. Preserve the current structured blocker: do not implement or claim the 29-row structured path in this assignment. A successful result is `PASS_XREF_EXECUTOR`, not C2a acceptance. Normal CLI remains fail-closed; no sidecars or durable candidate.

## Compact verification

Retain all existing Phase B/C1/C2a tests and add only meaningful xref classes, targeting roughly 27-32 total nodes rather than a selector matrix:

- real amended schema and 41/42 exact resolution;
- generated indices under the four exact owners with no parallel TOC or EOF dump;
- representative in-span printed-page removal, room link, handout link, p032 collection link, p037 two-link segmentation and p057 external non-link;
- 237-row execution ledger, 237 resolved links and exact per-owner xref IDs;
- failure on zero/multiple source line, missing/duplicate/overlapping segment, wrong owner/page/target and illegal external link;
- two fresh temporary reader builds remain byte-identical; strict conservation, asset ownership, staging collision refusal and fail-closed normal CLI remain green;
- no candidate, sidecar, acceptance, config/source/verifier mutation or durable output.

Run `py_compile`, the compact builder test file only, a real two-run temporary build, and scoped diff checks. Do not run the historical verifier mutation suite.

## Receipt

Return `PASS_XREF_EXECUTOR`, `FAIL`, or `BLOCKED` with:

- old/new builder and test hashes;
- compile/test command and exact test count;
- two-run temporary reader bytes/SHA;
- exact generated/source/segment/link/external/ledger evidence;
- representative rendered snippets or assertions for p011/p032/p037/p057;
- confirmation that structured completion is still pending and C2a/candidate are not accepted;
- changed files, elapsed time and token availability.

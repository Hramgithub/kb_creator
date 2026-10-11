# Viral Step 7 MASTER_EN — exact structured executor assignment

## Ownership and scope

- Owner: NRI engineering role, `gpt-5.6-terra` / `medium`.
- Orchestrator remains `/root`; integration, C2a acceptance and downstream authorization do not transfer.
- Allowed writes are exactly:
  - `kb_creator/scripts/build_scenario_master_en.py`;
  - `kb_creator/tests/test_build_scenario_master_en.py`;
  - `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_step7_master_en_structured_executor_20260901.md`.
- Config, accepted reconstruction/source PDF, verifier and its tests, plan/context, candidate/output, MinerU surfaces, ignored bytecode and Git are read-only.
- Use `python -B`; do not delete or refresh the existing ignored `.pyc`.
- Do not run MinerU or the historical 371/119/490 matrix.

## Pinned inputs

- Structured publication config: 659,173 bytes / SHA-256 `AF38313BDA788B0B2EC0449EDA60E10DE719AE7A6787D47F8EBCE8769F8A2E7B`.
- Canonical structured subtree: 43,174 bytes / SHA-256 `488D6D09F7B01DAB2681F89E623B5BA0C733155E45C383A0B3F773D5279EF37F`.
- Corrected structured-config receipt: 12,068 bytes / SHA-256 `AE236F3B46F71752CF579609BDCA6CE95D07A4ECC9B74999FC02FA9F62CD2728`.
- Authoritative 29-row architecture audit: 31,635 bytes / SHA-256 `5B609CBBF8664CAF5FD4338300F3C30ED01A656F49FD5395FACE03DB009B6A1F`.
- Baseline accepted xref builder: SHA-256 `C3096022D395A26CB05689E401E4B219F591BE99C52DD85B12B142F06CCF13F6`.
- Baseline tests: SHA-256 `BF03D81A6FDFD1F143A12585F83B4AD003DA18371C04F14EAAE584A9B6030023` with 27 compact nodes.
- Accepted v4 package inventory remains `68C17FB765A89C6146398868E61F1F6EB7B2FE4EAFBA8C2C2C8F42260BBDBA83`.

Read both structured receipts in full. All scenario facts and exact tokens must come from config; no Viral literal belongs in reusable code.

## Required implementation

1. Replace the old open structured parser with exact conditional schema validation for the amended config:
   - common 29-row keys and exact `source_units={page,path,sha256}` only; reject `accepted_v4_markdown` or any embedded body;
   - table contracts: exact contract kind, region list, formats, selectors, headers, ordered keys, continuation/termination and attached notes;
   - card/statblock contracts: exact regions, ordered literal tokens, required/forbidden literals and lexical protections;
   - visual-form contracts: exact asset/page/owner/SHA/reader/full-page/review/once/no-duplicate fields;
   - reject unknown/missing keys, duplicate ids or placement indices, unsupported class/representation/contract combinations and wrong source-unit identity.
2. Remove the hard-coded `locator_count == 219`. Validate `binding_index.locator_count` against the actual sum of config locator objects (now 217); continuation claims are ownership, not locator objects. Preserve strict conservation at 1,935 total / 1,862 owned / 73 generated / zero error.
3. Add a reusable exact structured resolver driven only by config, binding index and hash-bound accepted pages:
   - require each fragment's `binding_anchor` to be the logical owner or a declared hierarchy descendant, never a sibling/unrelated anchor;
   - resolve each `line_exact` start and termination exactly once inside that binding's owned source span;
   - parse `markdown_pipe_table` and `numbered_record_series` without rewriting; verify exact configured headers, key order/count, repeated/headerless continuation and attached notes;
   - verify cards/statblocks by exact ordered tokens, literal requirements/protections, forbidden tokens and exact boundaries; no snake_case/fuzzy inference;
   - verify visual forms through the exact owned reader/full-page asset and both review rows, never an evidence-only/context image.
4. Preserve accepted structure text byte-for-byte except the existing authorized heading/image/xref transformations. Do not generate replacement tables/cards/statblocks and do not append a duplicate structured section. Each source fragment must be consumed/emitted exactly once.
5. Honor configured logical region order even when it crosses binding anchors. The critical real case is Outdoor: the emitted sequence must remain records 1, 2-9 under the declared Cold Spot descendant anchor, then 10-12, then Hospital 1-12. The new root/child/root fragments must not appear as 1,10-12,2-9. Implement this as a scenario-neutral config-driven fragment/anchor interleave or exact relocation with a consumption ledger; do not hard-code ids/pages/keys. Emit every one of the 168 canonical anchors exactly once and do not duplicate or lose any owned source span.
6. Reliquae must emit the p66 base, p67 ATTACKS/SPECIAL ABILITIES, then the two Infection tables under the child anchor in correct order. The accepted `p067-infection` xref remains sourced from the Reliquae root and targets the Infection child. Preserve the already accepted 237-link executor and ledger.
7. After reader assembly, prove every semantic region occurs exactly once in its declared logical owner/descendant output sequence and every form asset occurs exactly once. Derive an ordered 29-row `structured_evidence` list containing id/class/logical owner/representation plus per-fragment source page, binding anchor, source start/end/SHA, emitted occurrence/range/SHA and exact fact results; include asset/review identity for visual forms.
8. `structured_units` must be derived from the exact evidence id set, never a config-set count. Fail on missing/duplicate/fabricated evidence, wrong emitted order/hash, absent/extra key, missing note/token/protection, forbidden token, wrong visual asset/review/owner or semantic duplicate.
9. Preserve all current Phase B/C1/xref behavior: 107 reader assets, 237 actual internal links, 237 executed xref ids, 41 source link segments, exact source conservation, occupied-staging refusal and fail-closed normal CLI. No sidecar or durable candidate.

## Compact verification

Expand the current 27-node builder suite only by meaningful invariant classes; target roughly 36-42 total nodes, not a 29-row or selector matrix:

- current real config resolves exactly 29 evidence rows with 11/10/2/6 class counts;
- pipe tables: single page, repeated-header continuation, attached note, three-column table and nested Reliquae infection tables;
- numbered series: single page and Outdoor root/descendant/root cross-page order 1..12 before Hospital 1..12;
- cards/statblocks: combined field line, literal no-stat Plague Monk, ordered tokens, forbidden token, source oddity protection and exclusive end;
- six visual forms: exact reader asset/reviews, one emitted asset each, no semantic/evidence-only duplicate;
- negative representatives: embedded body; absent/duplicate region; wrong/sibling owner; wrong/reordered header/key; broken continuation; missing note/token/protection; forbidden injected stat/table; changed emitted body/hash; wrong/duplicate/evidence-only form; fabricated/missing/duplicate evidence id;
- scenario-neutral synthetic fixture with different ids/tokens, or equivalent code-literal inspection plus synthetic region proof, demonstrating no Viral fact in reusable implementation;
- two fresh temporary real reader builds are byte-identical and all pre-existing 27 tests remain green.

Run in-memory compile without writing bytecode, compact builder tests only, a real two-run TemporaryDirectory reader build and scoped diff checks. Do not run verifier mutation tests.

## Receipt

Return `PASS_STRUCTURED_EXECUTOR`, `FAIL`, or `BLOCKED` with:

- old/new builder/test hashes and exact test count/commands;
- two-run reader bytes/SHA and derived topology;
- 29-row evidence count/class split and representative source/emitted hashes;
- exact Outdoor and Reliquae emitted order evidence;
- six form exactly-once evidence;
- retained xref/asset/conservation evidence;
- explicit no reauthor/no duplicate/no hard-coded Viral fact/no candidate statement;
- changed files, elapsed time and token availability.

A PASS is only a bounded implementation result. The orchestrator must independently inspect the real temporary reader and obtain an independent implementation review before C2a/C2b or candidate construction.

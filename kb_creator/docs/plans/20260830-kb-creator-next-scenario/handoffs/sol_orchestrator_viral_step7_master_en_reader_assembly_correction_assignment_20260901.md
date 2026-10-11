# Viral Step 7 MASTER_EN C2a reader-assembly correction assignment

## Role and boundary

- Owner: same `gpt-5.6-terra` engineering role, `medium`.
- Write only `kb_creator/scripts/build_scenario_master_en.py`, `kb_creator/tests/test_build_scenario_master_en.py`, and new immutable correction receipt `handoffs/terra_engineering_viral_step7_master_en_reader_assembly_correction_20260901.md`.
- Preserve config, source/reconstruction, verifier/tests, plan/context, durable candidate/output and Git. Normal CLI remains fail-closed. No MinerU/371/119/490.
- Baseline builder SHA-256 `66207091E8CFD9F0FB64CFAC21E2B32AF99EFCF5F872676CAB29E5CCF3E8BD96`; test SHA-256 `42E8C2586CC5B5B9D2E4DA7393FDDD3424261A6A2671932C4F0D0CB91C232AFF`.

## Rejected behavior

The first C2a receipt is historical but not accepted. `assemble_reader` currently emits all 168 headings first, then concatenates all 124 pages in source order, then appends all 107 assets. It does not execute binding actions, relocate physical units, place owned assets, render structured units, or apply non-TOC xrefs. `reader_source` changes every Markdown heading prefix to an unclosed `**`. Counts for handouts/maps/pregens/structures and `reader_noise_findings=[]` are hard-coded. The tests verify substrings/counts rather than reader topology. Deterministic bytes do not make this a valid reader.

## Required correction

1. Assemble in `assembly_binding.order`, interleaving each canonical anchor/heading with exactly its resolved source spans/unit content. Do not append a second whole-book source dump.
2. Execute every configured action:
   - `insert_before`: canonical heading before unchanged span;
   - `replace_heading`: consume only the source heading line, emit canonical heading once;
   - `replace_label_retain_remainder`: consume the declared prefix and retain the same-line remainder exactly;
   - `retain_under_anchor`: retain the declared content under the canonical heading;
   - `consume_continuation_label`: omit only the continuation label and retain its body.
   Multiple locators/spans for one anchor remain ordered; shared p74/p75 prefix appears exactly once.
3. For `physical_unit`, use its exact handout span/unit_ref and configured order. For `owned_page_unit`, consume only its declared visual-unit pages; covers use clean p1/p124 renders, map p106->107 remains one owner, pregen fronts/forms and backs remain paired, merchandise retains semantic content. Generated rows consume no source.
4. Remove source image plumbing at its original position and insert only assets owned by that anchor, sorted by configured placement, with config alt text and Phase B content-addressed path. Derive 107/evidence-only counts from data; do not hard-code. No asset dump at EOF.
5. Normalize retained subordinate headings to valid closed Markdown beneath the canonical heading. Never emit unclosed `**` or a second H1. Preserve body lexical content and source tables/cards/statblocks; use the 29 structured declarations as placement/verification evidence rather than returning a constant.
6. Apply all 237 xref rows: generated TOC/handout/map/pregen indices in their owning sections; source-page selectors wrap exact visible wording without changing it; all 236 internal links resolve; the single external bibliographic row remains visible non-link text. Fail on zero/multiple selector match or missing output target.
7. Derive handout/map/pregen/structured counts from emitted config-owned units and derive reader-noise findings by scanning the actual result. Include exact p80 note:
   `Hey Marco Babez, make sure you emphasize the bold parts when you're doing your thing. You've got this! It's going to be the best stream EVER!`
   and its owned reader asset at the correct Handout 13 unit.
8. Return a transformation/conservation ledger tying each emitted owner to source-span hashes, applied action, emitted asset IDs and xref IDs. Zero source owner duplication, unowned source, unauthorized lexical delta and hard-coded PASS counts.

## Verification

Replace weak C2a tests with topology/content assertions while retaining C1/Phase B coverage. Compact total target: about 28-36 nodes, not a selector matrix. The real two-run temporary build must prove:

- binding-order interleaving (Introduction content before Spektral Krew; handout body adjacent to its anchor; no 168-heading preamble/source dump/asset EOF dump);
- 1 H1, 168 anchors, all 236 internal xrefs resolve and sole external row remains non-link;
- 107 reader assets each exactly once under their configured owner; zero evidence-only refs;
- actual derived 41 handouts, 6 maps/7 pages, 12 pregens, 29 structures;
- p42 remainder, p20-22 continuations, p74/p75 prefix uniqueness, p80 exact note+asset, p93 multi-unit and p106-107 ownership;
- valid Markdown headings, no technical comments/overlay/paths/generic source descriptions, no duplicate body/source dump;
- strict C1 conservation unchanged, staging collision refusal, no sidecars/acceptance/durable candidate;
- two-run byte identity.

Run compile, builder+verifier focused pytest and scoped diff-check. Receipt returns `PASS_CORRECTED_READER_ASSEMBLY`, `FAIL`, or `BLOCKED`, exact hashes/test count/reader identity and derived gate evidence. Do not claim PASS if any requested xref/action/topology class is stubbed or counted without execution.

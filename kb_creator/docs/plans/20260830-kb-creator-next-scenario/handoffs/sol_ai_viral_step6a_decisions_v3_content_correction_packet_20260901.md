# Sol content-correction packet — Viral Step 6A decisions v3

## Assignment

- Goal: `20260830-kb-creator-next-scenario`.
- Role: content reconciliation and source-faithful correction.
- Requested profile: `gpt-5.6-sol`, reasoning `high`, accelerated service when
  available.
- This is not orchestration, engineering, QA or independent criticism.
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`.

Create one successor decision set from the frozen v2 decisions. Correct only
visually proven page-016 OCR defects and add visually proven printed Handout
identities 1-18. Do not materialize a candidate and do not change code or tests.

## Immutable inputs

- v2 decisions:
  `kb_creator/working/viral/source_reconstruction/20260901_step6a_ai_merge_decisions_v2/pages`
  (`124` JSON files; ordered decision-set digest recorded by the predecessor as
  `AA13DF843FAC3473144D69678056BB30B7FFFFE53185408841D5672C38F47232`).
- viewer-readable triptychs:
  `C:\Users\BogdanD\.codex\visualizations\2026\08\30\01a05392-3683-7292-b5d5-20ddc8b54a80\viral-step6a-visual-qa\viewer_previews_v1\triptychs`.
- frozen raw/visual roots and source PDF are read-only.
- v1, v2 and both materialized predecessor candidates are immutable.

## Allowed writes

Exactly these two surfaces:

1. fresh root
   `kb_creator/working/viral/source_reconstruction/20260901_step6a_ai_merge_decisions_v3/pages`;
2. receipt
   `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_ai_viral_step6a_decisions_v3_content_correction_20260901.md`.

The v3 root was confirmed absent before assignment. Copy all 124 v2 JSON files
before editing. Preserve formatting where practical. In every modified JSON,
only the `markdown` string may change; all other keys and values must remain
identical to v2. Files outside the modified-page allowlist must remain
byte-identical to v2.

## Required visual review

Open the viewer-readable triptychs at original detail for page 016 and every
page 069 through 086. Do not infer missing words from a translation. Use the
printed English source and the three frozen MinerU views.

### Page 016

Correct every unmistakable OCR substitution visible in the printed source on
this page, but make no stylistic rewrite, modernization or proofreading change.
At minimum, inspect all occurrences resembling `ae` where the printed source
may read `He`, and inspect `aospital`. Record every exact before/after replacement
in the receipt. If any reading is not visually certain, leave it unchanged and
record it as residual risk.

### Printed Handout identities

Add the canonical exact italic identity line `*Handout #...*` at the correct
visual boundary for each printed handout, matching the frozen v2 representation
of Handouts #19-39. Preserve subparts as printed. The visually established
page map to confirm is:

- page 069: `Handout #1`;
- page 070: `Handout #2a`;
- page 071: `Handout #2b`;
- page 072: `Handout #3a`;
- page 073: `Handout #3b`;
- page 074: `Handout #4`, `Handout #5`;
- page 075: `Handout #6`, `Handout #7`;
- page 076: `Handout #8`;
- page 077: `Handout #9`;
- page 078: `Handout #10`, `Handout #11`;
- page 079: `Handout #12`;
- page 080: `Handout #13`;
- page 081: `Handout #14`;
- page 082: no numbered Handout heading; it is introductory/Keeper material;
- page 083: `Handout #15`;
- page 084: `Handout #16`;
- page 085: `Handout #17`;
- page 086: `Handout #18`.

Place labels where the corresponding printed handout begins. Pages with two
handouts must receive two separate identity lines at their respective boundaries, not
a combined inventory line. Do not change the existing Handout #19-39 pages.

## Required self-checks

Before finishing, prove in the receipt:

- exactly 124 v3 JSON files, unique `source_page` 1-124 and valid schema;
- exact modified-file set;
- all files outside that set are byte-identical to v2;
- for modified files, deep comparison after removing only `markdown` is equal;
- page 082 is byte-identical to v2;
- pages 087-124 are byte-identical to v2;
- regex inventory over v3 Markdown yields physical labels
  `1, 2a, 2b, 3a, 3b, 4 ... 39` with no duplicate full label;
- unique numeric ordinals are exactly 1-39;
- no unresolved field, selected block, overlay preference, asset or review
  metadata changed;
- deterministic v3 file count, byte count and ordered digest.

## Forbidden actions

- Do not run MinerU.
- Do not run the 371/119/490 verifier matrix.
- Do not edit source, contract, raw roots, visual bundle, v1, v2, candidates,
  scripts, tests, plan, context, status, production, Git index or history.
- Do not create an overlay PDF or any downstream output.
- Do not use historical translations as source text.

## Return

Return only a compact summary: result, exact modified pages, page-016
replacements, v3 identity, receipt path/hash and any residual visual ambiguity.

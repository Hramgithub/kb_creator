# Viral Step 7 visual-QA priority transport remediation assignment

- Role: Terra/medium engineering.
- Cause: `view_image` can inspect the scratch bundle but receives Windows
  `os error 5` for candidate-A asset paths.
- Scope: make the existing reusable bundle generator transport the 39 priority
  originals byte-for-byte into a new scratch bundle. This is not image editing,
  proxy generation, visual QA, candidate repair or acceptance.

## Frozen evidence

- Worktree: `D:\NRI\.worktrees\kb-creator-viral`
- Candidate A is immutable.
- Candidate `INVENTORY.json` SHA-256:
  `EF28700403FFE5FC781D1004979B83DC4ACC5F743E93F02201820071211AC3F8`
- Candidate `MASTER_EN.md` SHA-256:
  `44303C5A0D2964469D6B6523EDF3CB4391194BC49E19DD10B3FB90CCB667DC62`
- Current generator SHA-256:
  `DCF89F275F415719F9F9D0026A43F1BC54B4B802938BBA02A911CF8D441E7B8A`
- Current test SHA-256:
  `C1C8BD61B7EF72447A5F4B3C659BAD1D633385774D0508C8F3382F2AD189437B`
- Existing v2 manifest SHA-256:
  `055C063058A8A609021113F7E5600955D3927D1C5387705592EBED6A427B332A`
- Luna BLOCKED receipt SHA-256:
  `020F6AEB1CF9205125DF0D9E1C8B864DB7AA65E59074A2A4DD013230F9D9CF20`
- Existing useful visual evidence: 27/27 contact sheets and p80 passed; only
  direct inspection of 39 priority originals is missing.

## Allowed writes

1. `kb_creator/scripts/build_master_en_visual_qa_bundle.py`
2. `kb_creator/tests/test_build_master_en_visual_qa_bundle.py`
3. `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_step7_visual_qa_priority_transport_remediation_20260902.md`
4. One new absent scratch output root only:
   `C:\Users\BogdanD\.codex\visualizations\2026\08\30\01a05392-3683-7292-b5d5-20ddc8b54a80\viral-master-en-visual-qa-bundle-20260902-v3`

Candidate, v2 bundle, source/reconstruction, config, other code/tests, plan,
context, prior receipts, Git and release/production surfaces are read-only.
Do not delete any output or temporary artifact owned by another step.

## Required minimal change

1. For each of the exactly 39 already selected `priority_assets`, copy the
   original candidate asset bytes unchanged into the output bundle beneath
   `priority_originals/`. Preserve the original extension and use a stable,
   collision-free filename derived from its existing candidate-relative name.
2. Do not decode/re-encode, resize, crop, convert, annotate or otherwise alter
   an image. The transported file must have exactly the source bytes and SHA-256.
3. Extend each `priority_assets` manifest row with its bundle-relative
   transported path and independently recomputed bytes/SHA-256/dimensions.
   Retain `original_candidate_path` unchanged.
4. Add `priority_originals: 39` to manifest counts. Fail closed if the selected
   set is not exactly 39, a path escapes, a destination collides, copy bytes or
   hash differ, dimensions differ, or any copied file is missing/extra.
5. Keep all existing v2 behavior unchanged: 123/107/91/107/27 counts, zero
   generation errors, ordered tiles/sheets, p80 render and `Babez` proof.
6. Preserve deterministic output identity for two identical synthetic runs and
   candidate immutability.

## Verification

- In-memory compile or `py_compile` without retained cache.
- Focused test module only; add coverage for exact transported bytes/hashes,
  count/path closure, mismatch failure, no candidate mutation and two-run
  determinism. Do not run historical or unrelated suites.
- Scoped `git diff --check` on the two owned files.
- One real run to the exact absent v3 root above.
- Recompute all 39 transported file hashes against their candidate sources and
  require 39/39 equality; also recheck the two frozen candidate hashes.
- Do not open images or claim visual QA.

Write the receipt only after the real v3 run passes. It must record current
script/test hashes, v3 manifest hash, exact counts, 39/39 byte/hash identity,
candidate immutability and the exact next action: Luna/high reopens only the 39
v3 `priority_originals` files at original detail and appends a new QA receipt.

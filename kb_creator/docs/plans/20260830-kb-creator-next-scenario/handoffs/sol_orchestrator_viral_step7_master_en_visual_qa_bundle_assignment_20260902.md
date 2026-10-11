# Viral Step 7 MASTER_EN visual-QA bundle assignment

- Role: Terra/medium engineering.
- Goal surface: reusable read-only candidate visual-QA bundle generator.
- Candidate input: `viral-master-en-candidate-20260901-a`, immutable.
- This assignment does not perform visual inspection or accept/release content.

## Allowed writes

1. `kb_creator/scripts/build_master_en_visual_qa_bundle.py`
2. `kb_creator/tests/test_build_master_en_visual_qa_bundle.py`
3. `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_step7_master_en_visual_qa_bundle_20260902.md`

All candidates, source/reconstruction, config, existing scripts/tests, plan,
context, receipts, Git and production surfaces are read-only.

## Required behavior

The CLI accepts candidate root, publication config, source PDF, an absent output
root and optional `pdftoppm` command. It must fail closed before writes on input
identity/schema/path errors and create only the requested output root.

From the closed candidate asset manifest and config it must:

- verify 123 total assets, 107 reader assets and 91 visual-review units;
- verify each reader asset path/hash/bytes/dimensions and exact candidate identity;
- generate 107 equal-size labeled RGB review tiles, preserving aspect ratio and
  showing ordinal, asset id, source page, semantic role and owner;
- reuse the existing `build_contact_sheets()` utility on those tiles to generate
  exactly 27 ordered four-tile contact sheets;
- identify every cover, back cover, full-page, map and handout reader asset as a
  priority asset and record its original candidate path;
- render source PDF page 80 once into the bundle at reader scale, using Poppler,
  and record command/version/hash/dimensions;
- locate candidate owner block `viral-handout-13` and require the exact visible
  text `Hey Marco Babez` once;
- explicitly include front-cover p1 and clean-source back-cover p124 renders in
  the priority set;
- write canonical `VISUAL_QA_BUNDLE.json` containing input identities, ordered
  reader rows, all 91 review-unit mappings/special requirements, tile/contact/
  priority identities, p80 render identity, counts and zero open generation
  errors. It must make no claim that visual inspection passed.

The generator must be deterministic for identical inputs. Tests use synthetic
images/PDF-render stub and cover schema/path/hash/dimension/count failures,
ordering, tile/contact counts, p80 `Babez`, no candidate mutation and two-run
bundle identity. Do not use or run MinerU or historical 371/119/490.

## Gates

- in-memory compile or equivalent;
- focused new test module;
- scoped `git diff --check`;
- one real scratch-only dry run against candidate A, followed by candidate hash
  preservation check; remove no output and do not inspect/accept visuals;
- receipt only after PASS, with script/test hashes and exact bundle counts.

After engineering PASS, Luna/high receives a separate frozen execution and
direct-inspection packet. Luna may execute/inspect only and must not edit code.

# Task packet: Viral v2 complete authoring Phase A1b

## Ownership

Reuse the same `nri-engineer` / medium. Exclusive paths:

- `kb_creator/scripts/build_scenario_master_en.py`
- `kb_creator/scripts/verify_scenario_master_en.py`
- `kb_creator/tests/test_build_scenario_master_en.py`
- `kb_creator/tests/test_verify_scenario_master_en.py`
- receipt
  `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_v2_complete_authoring_phase_a1b_20260903.md`

Do not touch helper/config/candidates/Git. Preserve identity and v1 behavior.

## Required A1b closure

1. Add required top-level closed `source_partition` to transitional v2 schema;
   migrate all compact builder/verifier fixtures to provide 122 ordered page
   rows and spans. Do not add `migration` yet.
2. Wire independent `v2_source_partition` into v2 input binding/preflight after
   package/page identities.
3. Validate exact pages 1--122, safe exact `pages/page-NNN.md` source path,
   page identity, UTF-8/no BOM, raw size/hash, closed EOL profile counts and
   ordered unique span ids.
4. Validate all span scalar types (booleans rejected), safe page/path binding,
   unique ids, allowed classification/owner enums, decision-ref shape,
   byte bounds/UTF-8 boundaries, exact char offsets, raw byte hash, decoded text
   hash, order, adjacency and 0..page-bytes coverage. Recompute aggregate page,
   byte, line-slot/nonblank/EOL metrics from reconstruction.
5. Add builder and independent-verifier tests for tiny full partition plus:
   unclaimed nonblank byte, unclaimed blank/CR/LF byte, overlap, duplicate id,
   reorder, wrong source path/page, wrong byte/text hash, wrong char offsets,
   invalid UTF-8 boundary/BOM, wrong enum/EOL profile and mutated source.
6. Existing compact v2 candidate tests must remain green after fixture
   migration; both real v1 preflights unchanged.

## Output

Run both focused modules, four-module baseline and py_compile. Return
`READY_FOR_V2_COMPLETE_AUTHORING_PHASE_A2` only if A1b is fully wired/tested;
otherwise precise partial token. Record hashes/counts and confirm no forbidden
outputs. No claim about migration/event/payload completeness yet.

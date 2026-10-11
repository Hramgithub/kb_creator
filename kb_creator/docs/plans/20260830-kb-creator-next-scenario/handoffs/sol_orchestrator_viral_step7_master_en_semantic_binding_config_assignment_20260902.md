# Viral Step 7 MASTER_EN semantic-binding config assignment

- Role: Terra/medium bounded config engineering.
- Subphase: exact 25 semantic seams and their non-asset dependencies only.
- Architecture receipt SHA-256:
  `BD537483C7BB3C78076DC2A6F7FC8937BF4040261B74E58312D3CBC6FEFC901D`.
- Asset-count erratum SHA-256:
  `02F71E5B14AF5F05A3F6F9F1BFAB2F279848324F5810F1CD666DB7D50FE7547D`.

## Frozen input

- Worktree: `D:\NRI\.worktrees\kb-creator-viral`
- Config SHA-256 after accepted asset/alt subphase:
  `0AA96D45123FFA36EE90D86D324D367A1A95EDACC5B79A15EF2FAC786373B397`
  (679,855 bytes).
- Asset/alt receipt SHA-256:
  `84632B3123C3703A3D52E0DD10871477959197C831365FBDD41877904C6D6C0E`.
- The 35 corrected asset owners and exact 107 alt values are frozen within this
  subphase and must remain semantically identical.
- Candidate A/B immutable; candidate C absent.

## Allowed writes

1. `kb_creator/working/viral/master_en/publication_config_v1.json`
2. `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_step7_master_en_semantic_binding_config_20260902.md`

Everything else is read-only. Do not add `reader_surface` yet and do not edit
assets/alts, code/tests, source/reconstruction, candidates, plan/context or Git.

## Exact amendment

Implement all 25 S01-S25 rows from the architecture's **Exact semantic-fragment
repairs** table using existing hierarchy `source_pages`, locators and
`continuation_pages` primitives. Preserve every selected byte and fragment order.

Apply every explicitly named non-asset dependency consequence, including:

- xrefs `p039-history`, `p049-infected-flesh`, `p049-handout-5`,
  `p052-handout-5` and all stay-put xrefs stated by the table;
- p55 structures `viral-structure-dss-incendiary-grenades` and
  `viral-structure-dss-throw-results`;
- the three exact p55 attached-note selectors and their `binding_anchor` values;
- every owner/source-page/continuation change required for the repaired 168-unit
  hierarchy.

Do not reapply asset-owner consequences: the preceding accepted subphase already
installed the complete corrected 35-row asset table. Instead require those 35
owners and all 107 alts to remain exactly unchanged.

## Verification

- Config parses and preserves canonical formatting/style.
- Resolve all 168 hierarchy units/171 source locators against immutable accepted
  v4 using current selector semantics.
- Independently materialize every S01-S25 raw range from the architecture table;
  require exact selector match, raw SHA-256, current-owner-to-correct-owner
  transition, order and non-overlap.
- Require every affected xref/structure/note dependency to have the architecture
  owner and every explicitly stay-put dependency to remain unchanged.
- Prove a semantic JSON diff contains only declared hierarchy/xref/structure/note
  fields; assets/alts and all unrelated config subtrees are identical to input.
- Config-scoped `git diff --check` passes.
- Candidate A/B and accepted reconstruction hashes unchanged; candidate C absent.

Do not run builder/verifier/tests, builds, MinerU, visual QA or mutation matrices.

Write one receipt only after `PASS_SEMANTIC_BINDING_CONFIG`, with old/new config
hash/bytes, 25/168/171 closure, dependency table proof, semantic-diff closure and
immutable evidence. Do not claim the config executable until reader_surface and
code/test phases complete.

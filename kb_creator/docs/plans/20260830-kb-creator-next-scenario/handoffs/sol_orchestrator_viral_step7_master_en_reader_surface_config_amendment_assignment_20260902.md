# Viral Step 7 MASTER_EN reader-surface config amendment assignment

- Role: Terra/medium bounded config engineering.
- Phase: one of two; data contract only. Builder/verifier/tests follow separately.
- Authoritative architecture receipt SHA-256:
  `BD537483C7BB3C78076DC2A6F7FC8937BF4040261B74E58312D3CBC6FEFC901D`.
- Aggregate-count erratum: 35 asset-owner changes (34 reader + 1 evidence-only)
  and 279 total atomic defects; erratum file must be read before editing.

## Frozen state

- Worktree: `D:\NRI\.worktrees\kb-creator-viral`
- Config input SHA-256:
  `CEAA522F8ADA7EF2453D52F0DE4D098733EA5A7D55B12BE96694094891767BF3`
- Accepted reconstruction inventory SHA-256:
  `68C17FB765A89C6146398868E61F1F6EB7B2FE4EAFBA8C2C2C8F42260BBDBA83`
- Candidate A/B are immutable rejected evidence.
- `viral-master-en-candidate-20260902-c` must remain absent.

The preceding broad engineering assignment performed baseline analysis only and
made no durable implementation write. This packet supersedes it for config data.

## Allowed writes

1. `kb_creator/working/viral/master_en/publication_config_v1.json`
2. `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_step7_master_en_reader_surface_config_amendment_20260902.md`

Everything else is read-only, including builder/verifier/tests, source,
reconstruction, candidates, bundles, plan/context, architecture/review receipts,
Git and downstream outputs.

## Required amendment

Apply the architecture's data contract completely and mechanically:

1. repair all 25 semantic fragment seams through exact existing hierarchy
   locators/source-pages/continuations;
2. update every named xref, both p55 structures, all three attached notes and
   every other dependency in the architecture table;
3. apply all 35 real asset-owner changes from the explicit table;
4. set all 107 reader-image `alt_text` values exactly from the one-based ledger,
   binding row ordinal as `placement_index + 1` and proving exact 1..107 closure;
5. add the strict top-level `reader_surface` object with only
   `schema_version`, `semantic_fragments`, `authorized_suppressions`,
   `heading_policy`, and `alt_policy`;
6. encode exactly 25 semantic fragment rows and 22 suppression rows with the
   architecture's exact selectors, owners, hashes, order, dispositions,
   replacement asset ids and authorial flags;
7. encode the exact heading and alt policies from the architecture receipt.

Do not invent or omit a row, alter accepted text/assets, or compensate for code
that has not yet been updated. Current builder may reject the new top-level key;
that expected intermediate state is not a reason to weaken the config.

## Config-only verification

Before writing the receipt, perform read-only structured checks over the final
JSON and immutable v4 pages:

- JSON parses and preserves canonical style/order expected by the project;
- exactly 168 hierarchy units, 25 semantic fragments, 22 suppressions,
  107 reader assets with ordinal closure, 35 actual owner changes and the closed
  policies/schema shapes;
- every selector matches exactly as specified and every raw hash agrees;
- all named xref/structure/note/asset dependencies point to corrected owners;
- unknown/extra keys are absent in every new nested record;
- config-scoped `git diff --check` passes;
- Candidate A/B and accepted reconstruction hashes remain unchanged;
- candidate C remains absent.

Do not run builder/verifier tests, builds, MinerU, visual QA or mutation matrices
in this config-only phase.

## Receipt

Write the receipt only on `PASS_READER_SURFACE_CONFIG`. Record old/new config
hash/bytes, exact 25/22/107/35 counts, dependency checks, selector/hash closure,
immutable evidence and the next code/test phase. Do not claim executable builder,
candidate, release or acceptance readiness.

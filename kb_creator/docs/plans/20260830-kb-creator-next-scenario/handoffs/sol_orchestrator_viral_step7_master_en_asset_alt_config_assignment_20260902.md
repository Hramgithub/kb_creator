# Viral Step 7 MASTER_EN asset-owner and alt config assignment

- Role: Terra/medium bounded config engineering.
- This is a mechanical subphase of the superseded broad config updater.
- Authoritative architecture receipt SHA-256:
  `BD537483C7BB3C78076DC2A6F7FC8937BF4040261B74E58312D3CBC6FEFC901D`.
- Mandatory aggregate erratum SHA-256:
  `02F71E5B14AF5F05A3F6F9F1BFAB2F279848324F5810F1CD666DB7D50FE7547D`.

## Frozen input

- Worktree: `D:\NRI\.worktrees\kb-creator-viral`
- Config SHA-256:
  `CEAA522F8ADA7EF2453D52F0DE4D098733EA5A7D55B12BE96694094891767BF3`
- Candidate A/B and accepted reconstruction are immutable; candidate C absent.

## Allowed writes

1. `kb_creator/working/viral/master_en/publication_config_v1.json`
2. `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_step7_master_en_asset_alt_config_20260902.md`

Everything else is read-only. This subphase must not touch hierarchy locators,
xrefs, structures, notes, add `reader_surface`, or edit code/tests.

## Exact change

1. Expand every SHA-prefix row in the architecture's **Asset semantic-owner
   corrections** table to the unique full existing asset id and set exactly the
   declared owner. There are 35 real changes: 34 reader assets and one
   evidence-only asset (`98252d0b...`). No row is a no-op.
2. Apply the architecture's **Complete 107-alt contract** exactly. It is
   one-based: ledger ordinal equals existing zero-based `placement_index + 1`.
   Require exact ordinal closure 1..107, one unique reader asset per ordinal and
   no change to evidence-only/non-reader alt data outside the ledger.
3. Do not reorder assets or change path, representation, bytes/hash/dimensions,
   source page/region, placement index, open/accept state or any other field.

## Verification

- Config parses; canonical formatting/style is preserved.
- Exactly 35 owner values changed and they match all explicit table rows.
- Exactly 107 reader alt values equal the ledger; no empty value and no current
  `Scenario illustration owned by`, repeated generic sheet/silhouette label,
  hash/path/tooling/page-provenance form remains.
- Asset count/ordering/ids/representations and every field other than the
  declared 35 owners plus 107 alt values are byte-semantically unchanged.
- Candidate A/B and accepted reconstruction hashes unchanged; candidate C absent.
- Config-scoped `git diff --check` passes.

Do not run builder/verifier/tests, build candidates, MinerU or visual QA. Current
builder compatibility is evaluated only after remaining config subphases.

Write one receipt only after `PASS_ASSET_ALT_CONFIG`, including old/new config
hash/bytes, exact 35/107 closure, semantic diff proof and immutable evidence.

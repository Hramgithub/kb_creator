# Viral Step 7 MASTER_EN final reader-surface config-contract assignment

- Role: Terra/medium bounded config engineering.
- This packet completes the config after accepted asset/alt work and the saved
  semantic-binding checkpoint. It supersedes the unreceipted remainder of the
  semantic-only packet; it does not discard its durable config changes.
- Architecture receipt SHA-256:
  `BD537483C7BB3C78076DC2A6F7FC8937BF4040261B74E58312D3CBC6FEFC901D`.
- Aggregate-count erratum SHA-256:
  `02F71E5B14AF5F05A3F6F9F1BFAB2F279848324F5810F1CD666DB7D50FE7547D`.
- Reader-ordinal erratum SHA-256:
  `CFC47AAADC4A831982E6EB202D9BD6E8654221AF810C2D7E3CB614322851DAA5`.

## Frozen checkpoint

- Worktree: `D:\NRI\.worktrees\kb-creator-viral`
- Current config SHA-256:
  `463D246BEC22390A1164FEBA80ABC00D97E681E2EE72975E7E40A625A11B93AD`
  (676,573 bytes).
- Current checkpoint already contains the 35 owner corrections, exact 107 alts,
  semantic page-claim transfers, named xref/structure/review-unit changes and
  closed `1935 / 1862 / 73 / 0 / 0 / 0` resolver conservation.
- `reader_surface` is currently absent.
- Candidate A/B immutable; candidate C absent.

## Allowed writes

1. `kb_creator/working/viral/master_en/publication_config_v1.json`
2. `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_step7_master_en_reader_surface_config_contract_20260902.md`

Everything else is read-only. No code/tests/build/candidate change is allowed.

## Required completion

1. Preserve all correct current semantic transfers and complete any still-missing
   exact locator/source-page/continuation declaration required by S01-S25.
2. Complete the three p55 attached-note owner and nested `binding_anchor` changes
   and prove every affected/stay-put xref/structure/note dependency from the
   architecture table.
3. Add one top-level `reader_surface` object with exactly:
   `schema_version`, `semantic_fragments`, `authorized_suppressions`,
   `heading_policy`, `alt_policy`. Use schema version
   `kb_creator.master_en_reader_surface.v1`.
4. Add exactly 25 ordered semantic fragment rows S01-S25 using the architecture's
   exact source pages, start/end selectors, expected owners, raw hashes and order.
   Resolve each against immutable accepted v4 and reject zero/multiple/empty/
   overlapping/out-of-order ranges.
5. Add exactly 22 ordered authorized suppression rows N01-N22. Each must select
   exactly the architecture's complete block once, record the recomputed raw
   SHA-256, correct current owner, disposition, replacement asset or null,
   `expected_occurrence: 1`, and `authorial_text_affected: false`.
6. Add the exact closed heading policy and alt policy from the architecture. The
   alt policy must accept the installed 107 ledger and reject the specified
   provenance/generic/hash/path/tooling/page forms.
7. Retain the accepted 35 asset owners and 107 alts exactly. Reader ordinal remains
   filtered reader order sorted by unchanged placement index, enumerated 1..107.

All new objects and selectors use exactly the closed nested key sets in the
architecture receipt. No broad suppression, inferred hash or unknown key is
allowed.

## Final config-only audit

Before receipt, independently prove from final JSON and immutable v4:

- 168 units and the checkpoint's closed conservation;
- 25/25 semantic ranges match exact raw hashes, once, ordered, non-overlapping,
  and resolve to the specified owners;
- 22/22 suppressions match exact full blocks/hashes once and are non-authorial;
- all affected xref/two structures/three notes/review-unit bindings and all
  stated stay-put dependencies are correct;
- 35 asset-owner corrections and exact 107 alt ledger remain installed;
- new schema/key closure and policies are exact; no extra key exists;
- semantic diff versus checkpoint changes only the declared completion/dependency
  fields plus new `reader_surface`;
- config parses, scoped `git diff --check` passes, accepted inputs/A/B unchanged,
  candidate C absent.

Do not run current builder/verifier/tests: executable support is the next separate
phase. Do not run MinerU, reconstruction, visual QA or mutation matrices.

Write one receipt only after `PASS_READER_SURFACE_CONFIG_CONTRACT`, recording
checkpoint/final hashes and bytes, all exact closure counts/hashes/dependencies,
immutable evidence and the next code/test phase. Do not claim candidate, release,
acceptance or downstream readiness.

# Task packet — Viral v2 Phase B1c asset/xref serialization

## Role and ownership

- Role: `nri-engineer` / GPT-5.6-terra / medium.
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`.
- Own only the author helper, its focused tests and receipt:
  `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_v2_complete_authoring_phase_b1c_asset_xref_serialization_20260903.md`.
- Canonical config and all candidates remain forbidden. Temporary configs may
  exist only in OS temp and must be removed.
- Do not edit builder/verifier/other tests, plan/context, frozen inputs/evidence,
  scratch, Git, MASTER_RU, Step 8A, HTML/PDF/output.

## Bound B1b state

- B1b receipt:
  `758DB382526D7BD8D98D87BB7D6FDCBB6DD87B9E304229A1648D8168CB94DBB0`.
- Starting helper:
  `16BFE0A6ECB7D634085D22B4C8AD30547A634F29DA8CE6A12F86EEE79792DB42`.
- Starting tests:
  `58050D04238C3B70AC3A6C77015512DA85BEDD66DE54A69F6FAE52EF3F471A61`.
- Source graph checkpoint: 122 pages, 410 contiguous spans, 346,793 bytes,
  186 approved units, 168-row hierarchy projection, ordinary events retained,
  typed inventory and sealed recoveries.
- Parent Phase B requirements, architecture, fixed A3 builder/verifier and all
  input identities remain binding.

Refuse on drift.

## Required implementation

Remove the B1b fail-closed seam only after materializing a complete closed
temporary v2 config:

- turn every reviewed typed unit into its exact A3 schema, including all fields,
  counts/order/contains/end boundaries and payload bindings reconstructed byte
  for byte from source slices or sealed recovery; zero placeholder literals;
- inherit and migrate all 123 frozen assets with explicit outcome, owner,
  asset-owned image-reference source spans, exact before/after/inside placement,
  reader policy and identities; implement p106/107 map and all six p111--122
  page pairs, platform/promo/evidence suppression and city->boat->Prologue;
- inherit and migrate all 237 xrefs with exact visible-text source slices,
  source event/page, target anchor and exact `xrefs:<xref_id>` migration id;
  preserve technical invisible anchors such as Infection;
- complete six-domain migration target closure and new reviewed targets without
  duplicates/orphans/pending ids;
- create dynamic visual-review units covering every heading, structured kind,
  xref/recovery and reader asset exactly as required;
- materialize complete source disposition, document identities and metrics;
- serialize canonical deterministic JSON to an explicitly supplied absent temp
  path atomically; refuse overwrite and leave no file on failure.

The temporary config must pass current builder and independent verifier public
preflight APIs. Neither author nor tests may import builder helpers as authoring
truth; invoking their public preflight gates after authoring is required.

## Tests

Extend real-input tests to author two temp files, prove byte identity, parse and
assert full counts/closure, then pass both preflights. Add mutation/failure tests
for typed omissions/bindings, asset outcomes/owner/placement/reader ids,
xref text/target/migration, migration duplicate/orphan, visual-review coverage,
p123/124 leakage, deterministic ordering, placeholders and atomic cleanup.

Run focused author tests, current 104-test baseline, py-compile, both frozen-v1
preflights, fixed hashes, diff and forbidden-output checks. Canonical
`publication_config_v2.json` stays absent and no candidate/scratch is retained.

End with:

- `READY_FOR_V2_COMPLETE_AUTHORING_PHASE_B2_MATERIALIZATION`, or
- `PARTIAL_V2_COMPLETE_AUTHORING_PHASE_B1C` with concrete code/tests and exact
  failing builder/verifier seam. Do not return analysis-only status.

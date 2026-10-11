# Task packet — Viral v2 complete authoring Phase B1 author foundation

## Role and exact deliverable

- Role: `nri-engineer` / GPT-5.6-terra / medium.
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`.
- Own only:
  - `kb_creator/scripts/author_viral_master_en_v2_config.py`;
  - new `kb_creator/tests/test_author_viral_master_en_v2_config.py`;
  - receipt
    `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_v2_complete_authoring_phase_b1_author_foundation_20260903.md`.
- Do not create the canonical config in this slice. Tests may author only into
  OS temporary directories and must remove them.
- Do not edit builder/verifier/other tests, plan/context, immutable inputs,
  evidence/v1 configs, candidates, retained scratch, Git, MASTER_RU, Step 8A,
  HTML/PDF or production.

## Bound state

- Parent Phase B packet:
  `TASK_PACKET_terra_engineering_viral_v2_complete_authoring_phase_b_real_config_20260903.md`.
- Parent partial receipt SHA-256:
  `CC67EB51B8D5DF81E30F6F1F5D33DC78044EA87BE6C355A68E9EC4834A190FB8`.
- Obsolete helper starting SHA-256:
  `3FD74EF9933C2D327A64250F719EAD454A6C998279A61C5F9075E66EA71F1FD7`.
- A3 approval:
  `C6F947123151E3B5F315F7B13D05FD81D43B536BC0CDD0506ED3290ABC26B181`.
- Fixed builder/verifier:
  `2C2A5A998C55FEF07B141CC6D146A2CD40302F7E95679E1DF1272385C7DD346B`,
  `7FD59EF3BB2BCB01E9DB943FB8921F7AF7C95C79D3873379A8167153C59F06F8`.
- Fixed builder/verifier tests:
  `EE0F021497A15879A878A83703427DC42DB5AD7D364D87829669A41606BCA376`,
  `1828EE86ED5C994D9C33C1A9AEBC5315E45861B750076EE1E31477F9FB4C8417`.
- All source/v1/reconstruction/ledger/approval hashes are those bound in the
  parent packet and must be rechecked.

Refuse on drift. Read the full parent packet, architecture, registry, ledger
approval, A3 approval, current schemas/tests and full real inputs before edits.

## Required implementation

Replace the obsolete helper completely. Deliver an executable deterministic,
fail-closed author that accepts an explicit absent output path and builds the
full real Viral v2 config in an OS temporary directory without any candidate.
It must satisfy every content/partition/migration/typed/hierarchy/xref/asset/
scope requirement in the parent packet and pass both current builder and
independent verifier public preflight APIs on its temporary result.

Mandatory principles:

- start from exhaustive source and frozen-v1 inheritance, not only reviewed
  ledger units;
- cover every accepted page 1--122 byte/character and ordinary prose;
- convert only exact reviewed spans into typed overlays;
- no `Source-backed`, `See source`, fallback, guessed or placeholder literals;
- every authorial leaf uses exact source slices or sealed recovery;
- full 168/123/237/124/41/29 migration closure and exact target ids;
- full closed A3 payload fields, including map/pairs and creature nested tables;
- exact 123/124 exclusion and all reviewed defect fixtures;
- output path must be absent; write atomically and never overwrite;
- no network and no dependency on builder helpers as authoring truth.

## Tests

Create focused tests that use the real frozen inputs and temporary output:

- two independent authors are byte-identical and canonical JSON;
- both builder and verifier preflight the authored temp config;
- assert exact scopes, migration counts, full source partition conservation,
  monotonic events, hierarchy and asset closure, required typed kinds/known
  defect fixtures, zero placeholders and zero p123/124 leakage;
- mutation tests for every bound identity, partition gap/overlap/EOL/order,
  missing ordinary prose, titles/hierarchy/representation, all typed schemas,
  recovery, xref migration, assets, migration duplicates/counts and overwrite/
  atomic failure;
- prove no candidate/config/scratch is left in the repository.

Run helper tests plus the current 104-test baseline, py-compile, both v1
preflights, fixed hashes, diff and forbidden-output checks. The canonical
`publication_config_v2.json` must remain absent.

End with:

- `READY_FOR_V2_COMPLETE_AUTHORING_PHASE_B2_MATERIALIZATION`, or
- `PARTIAL_V2_COMPLETE_AUTHORING_PHASE_B1` with implemented functions/tests and
  exact remaining failing seam. Do not return a status-only partial without
  modifying the owned implementation toward the required result.

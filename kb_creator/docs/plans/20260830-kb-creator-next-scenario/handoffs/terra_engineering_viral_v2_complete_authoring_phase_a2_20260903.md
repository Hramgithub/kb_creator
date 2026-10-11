# Viral v2 complete authoring Phase A2 migration-ledger engineering receipt

## Receipt metadata

- Goal id: `20260830-kb-creator-next-scenario`.
- Scope: bounded Phase A2 migration ledger contract only; A3/helper/config/candidate work was not started.
- Result: partial, fail-closed A2 schema/binding checkpoint.
- Engineer role: `nri-engineer` / requested `gpt-5.6-terra` / medium.
- Orchestrator policy owner: main chat / `gpt-5.6-sol` / medium.
- Assignment state: implementation completed for the bounded schema/input-binding seam; independent review remains required.
- Scoped override: none.
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`.
- Timestamp: `2026-09-03T06:20:00+03:00` (Europe/Moscow).
- Elapsed time: approximately 45 minutes.
- Token use: unavailable.

## Bound prerequisites

- Complete-publication architecture receipt: `39F9B514F82ABAAD58D0A637E07C395206E57BED7106864EC0247A9477E24ADC`.
- A1b engineering receipt: `2DD8839D6DB1B2FFF251634966E0E3D35A6DC570B4B9E3076F8EF2A6C4DED1A5`.
- A1b independent approval receipt: `0D99E9B4F9B70F93D66118C555D2C2ED0077587360DD2A3027B532CD3FBAA23C`.
- Frozen v1 config: `C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30`.

## Result and closed design

Builder and independent verifier now require a closed top-level `migration`
section. It has `inputs`, exactly six exhaustive frozen-v1 ledgers, and
`new_reviewed_targets`. Each ledger row is closed as
`source_id`, `source_row_sha256`, `outcome`, `final_target_ids`, and
`decision_ref`. The canonical source-row algorithm is SHA-256 of canonical
UTF-8 JSON with `sort_keys=true` and separators `(',', ':')`.

The source-id/target namespace is `domain:id`, using v1 collection names:
`hierarchy:anchor`, `assets:asset_id`, `xrefs:xref_id`,
`source_disposition:page`, `handouts:anchor`, and
`structured_content:structure_id`. New materialized target ids are closed by
`new_reviewed_targets` and a valid evidence decision reference. Existing v2
hierarchy/assets/xrefs cannot appear unreferenced.

Decision references are membership-checked, not merely nonempty: every
non-unchanged row and every new target must occur in UTF-8 text of one of the
exact bytes/SHA-bound `migration.inputs.decision_evidence` files. Input paths
are independently resolved as safe repository-relative identities in both
modules, with existing identity/topology protections.

`retained_unchanged` cannot carry a decision reference. Because A3 has not
yet materialized final immutable-field projections, it can only use the closed
`pending_a3:domain:id` target form. Both input-binding/preflight routes reject
any pending-A3 target, so it cannot make a real v2 config or helper pass before
field-parity validation exists.

Mandatory six-ledger cardinalities, source identity/hash closure,
domain-outcome subsets, unique target ids, source-disposition page 123/124
targetless advertising exclusion, and source-page 123/124 asset target
suppression are enforced. The builder and verifier do not import one another.

## Files changed

- `kb_creator/scripts/build_scenario_master_en.py`
  `B9A90CA83517505EB1B56D77ACA5338EA05058EFAC3F60CE6E4383F4F9DC6530`.
- `kb_creator/scripts/verify_scenario_master_en.py`
  `B7108E64E2166F84654D8C0A88C2233831A4C5CF30BB3D92CC2B3886588E8F6B`.
- `kb_creator/tests/test_build_scenario_master_en.py`
  `BE36818FE21317C665E254748BB0D27A3A12AF0CBE57050C3DB358DE11F18375`.
- `kb_creator/tests/test_verify_scenario_master_en.py`
  `E352A279973F47C583B2E0B78AC189E0A78B7EA22DB9294E42E31079C56F65BE`.
- This immutable receipt.

## Verification and evidence

- `python -B -m py_compile` over all four assigned modules: exit `0`.
- Focused new builder/verifier A2 migration tests: `Ran 2 tests`, `OK`.
- Focused two-module regression command:
  `python -B -m unittest -q kb_creator.tests.test_build_scenario_master_en kb_creator.tests.test_verify_scenario_master_en`: exit `0`.
- Real frozen-v1 builder preflight: `preflight_passed`; source SHA
  `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05`,
  reconstruction aggregate
  `68C17FB765A89C6146398868E61F1F6EB7B2FE4EAFBA8C2C2C8F42260BBDBA83`.
- Real frozen-v1 independent verifier preflight: `preflight_passed`; config SHA
  `C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30`.
- Scoped `git diff --check`: exit `0`.

## Forbidden-output evidence

- `kb_creator/working/viral/master_en/publication_config_v2.json`: absent.
- Accepted-v4 `INVENTORY.json`: absent.
- `kb_creator/working/viral/master_en/candidates/a2-forbidden-probe`: absent.
- No helper, candidate, immutable source/reconstruction/v1 config, Git index,
  commit, remote, Step 8A, HTML, PDF, or production output was changed.

## Blockers and next action

This is not complete A2 acceptance. The precise remaining gap is the A3-owned
materialized final-field projection for hierarchy/assets/xrefs/handouts/
structured/source-disposition targets. Until that exists, `retained_unchanged`
cannot prove immutable-field equality against a final target; the implemented
pending-A3 route intentionally blocks real preflight. Asset binary/semantic
identity parity and duplicate logical reader representation also require that
A3 target projection. A fresh independent critic must review this engineering
checkpoint before any continuation.

Terminal status:

`PARTIAL_V2_COMPLETE_AUTHORING_PHASE_A2`

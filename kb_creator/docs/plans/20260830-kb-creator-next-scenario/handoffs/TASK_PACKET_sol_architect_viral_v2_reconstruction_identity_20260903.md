# Task packet: Viral v2 reconstruction-package identity

## Role

- Owner: `nri-architect` (`gpt-5.6-sol`, high).
- Orchestrator: main chat (`gpt-5.6-sol`, medium).
- This is analysis/specification only; do not edit implementation or tests.

## Goal

Specify the smallest closed v2-only contract change that binds the already
accepted immutable reconstruction v4 without inventing a missing
`INVENTORY.json`, while preserving independent builder/verifier parity and all
v1 behavior.

## Evidence

- Package: `kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4`.
- Frozen v1 config: `kb_creator/working/viral/master_en/publication_config_v1.json`.
- V1 accepted aggregate identity: 377 files, 41,079,424 bytes, SHA-256
  `68C17FB765A89C6146398868E61F1F6EB7B2FE4EAFBA8C2C2C8F42260BBDBA83`.
- Current v2 enforcement:
  `kb_creator/scripts/build_scenario_master_en.py` and
  `kb_creator/scripts/verify_scenario_master_en.py`.
- Blocked helper:
  `kb_creator/scripts/author_viral_master_en_v2_config.py`.
- Blocked receipt:
  `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_v2_config_authoring_retry_20260903.md`.

## Required decisions

1. Exact closed JSON shape and field names for the v2 reconstruction-package
   identity.
2. Canonical aggregate hashing algorithm, scope, path resolution and topology
   rules, using accepted v1 semantics where possible.
3. Exact builder and independent-verifier validation steps and first-error
   behavior.
4. Required positive and negative tests, including immutable package mutation,
   wrong root, wrong counts/bytes/hash, unsafe path and v1 non-regression.
5. Confirm that candidate output `INVENTORY.json` remains unchanged and is not
   confused with reconstruction input identity.

## Constraints

- Do not mutate accepted reconstruction v4, source PDF, v1 config, ledgers,
  candidate roots or Git.
- Do not weaken identity binding or accept an unsealed directory.
- Do not couple independent verifier to builder helpers.
- Config authoring and candidate execution remain closed.

## Output

Write only
`kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_viral_v2_reconstruction_identity_20260903.md`
with: decision, exact schema, algorithms/checks, test matrix, migration steps,
risks, changed-path allowance for the engineer, and terminal token `READY_FOR_V2_RECONSTRUCTION_IDENTITY_IMPLEMENTATION` or a precise blocker.

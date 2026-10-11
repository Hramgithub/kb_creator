# Task packet — Viral v2 complete authoring Phase A2 migration ledgers

## Start condition and role

- Start only after the orchestrator records independent terminal approval
  `APPROVED_V2_COMPLETE_AUTHORING_PHASE_A1B` for the exact A1b hashes.
- Role: `nri-engineer` / GPT-5.6-terra / medium.
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`.
- You are not alone in the worktree. Preserve all unrelated/user edits and do
  not revert or normalize them.
- Own only:
  - `kb_creator/scripts/build_scenario_master_en.py`;
  - `kb_creator/scripts/verify_scenario_master_en.py`;
  - `kb_creator/tests/test_build_scenario_master_en.py`;
  - `kb_creator/tests/test_verify_scenario_master_en.py`;
  - one receipt
    `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_v2_complete_authoring_phase_a2_20260903.md`.
- Do not edit helper/config, A3 event/payload/hierarchy authoring, visual QA,
  immutable source/reconstruction/v1 config/evidence, candidates, plan/context,
  Git index/commits/remotes, MASTER_RU, Step 8A, HTML/PDF or production output.

## Bound specification and prerequisite

- Architecture receipt SHA-256:
  `39F9B514F82ABAAD58D0A637E07C395206E57BED7106864EC0247A9477E24ADC`.
- A1b engineering receipt SHA-256:
  `2DD8839D6DB1B2FFF251634966E0E3D35A6DC570B4B9E3076F8EF2A6C4DED1A5`.
- A1b independent approval receipt:
  `gpt55_critic_viral_v2_complete_authoring_phase_a1b_review_20260903.md`,
  SHA-256
  `0D99E9B4F9B70F93D66118C555D2C2ED0077587360DD2A3027B532CD3FBAA23C`.
- Frozen v1 config:
  `kb_creator/working/viral/master_en/publication_config_v1.json`, SHA-256
  `C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30`.
- Preserve the already approved A1b implementation and tests unless the A2
  closed-schema integration strictly requires an additive change.

## Required implementation

Add a closed top-level v2 `migration` section to builder and independent
verifier. Do not import validation code between them. It contains `inputs` and
exactly six exhaustive ledgers:

```text
hierarchy_rows          168
asset_rows              123
xref_rows               237
source_disposition_rows 124
handout_rows             41
structured_rows          29
```

For every frozen-v1 row:

1. derive a stable domain source id from its immutable v1 identity field(s);
2. bind the canonical SHA-256 of the complete source row using one explicitly
   documented UTF-8 canonical-JSON algorithm;
3. require exactly one migration row and one allowed domain-specific outcome;
4. require zero or more unique final target ids;
5. allow `decision_ref:null` only for `retained_unchanged` and require exact
   immutable-field preservation for that outcome;
6. require a nonempty decision reference for every other outcome and prove it
   exists in one of the exact bound registry/semantic/boundary/review inputs;
7. reject every final target that is neither referenced by a source migration
   row nor separately declared `new_reviewed` with a valid decision reference.

Allowed outcomes are domain-specific subsets of:
`retained_unchanged`, `retained_rebound`, `reclassified`, `replaced`, `split`,
`merged`, `suppressed_reviewed`, `excluded_advertising`. Reject an outcome that
is semantically impossible for its domain.

`migration.inputs` must use safe repository-relative path plus bytes/SHA-256
bindings for the frozen v1 config and all decision evidence needed by A2.
Independently resolve paths, reject absolute/backslash/traversal and
symlink/reparse/special topology, recompute bytes/SHA and reject substitutions.
Reconstruction/source identity remains owned by the already approved document
binding; do not duplicate or weaken it.

Mandatory domain invariants:

- asset ledger has exactly the 123 unique frozen asset ids and a mutually
  exclusive conservation outcome for every id; preserve complete binary and
  semantic identity unless a valid decision changes it; forbid missing,
  duplicate, drifted, silently promoted evidence, duplicate reader logical
  representation, and page-123/124 reader assets;
- pages 123 and 124 source-disposition rows are exactly
  `excluded_advertising` and targetless; no A2 target in any domain may create
  reader leakage for those pages;
- all 168 hierarchy, 237 xref, 41 handout and 29 structured source rows are
  accounted exactly once;
- retained targets and source ids close against the existing materialized v2
  sections where A3 is not required; any closure intentionally deferred to A3
  must be represented by an explicit, closed pending target type and must not
  allow the author helper or real config to pass preflight prematurely.

## Tests and evidence

Add positive miniature fixtures plus deterministic negative mutations for at
least:

- missing, duplicate and unreferenced source row in each of six domains;
- complete-row hash drift and wrong source id/domain/count;
- invalid/domain-incompatible outcome;
- missing, empty or unknown decision ref; decision ref on
  `retained_unchanged`;
- `retained_unchanged` immutable-field drift;
- duplicate/orphan/unreviewed final target and invalid `new_reviewed` target;
- missing/duplicate v1 asset, evidence promotion, identity drift, duplicate
  logical reader representation and page-123/124 leakage;
- page-123/124 source-disposition not excluded, nonempty target or target leak;
- mutated bound input path/bytes/SHA and unsafe topology/path;
- boolean-as-integer/scalar and unknown-key rejection throughout.

Every failed builder test must assert destination absence. Keep all v1 tests,
A1b tests, py-compile, four-module baseline and both real v1 preflights green.
No real `publication_config_v2.json`, accepted-v4 input `INVENTORY.json`,
candidate or scratch output may remain.

## Handoff

Receipt must record bound hashes, exact changed files/hashes, test counts,
preflight results, forbidden-output checks, blockers and one terminal line:

- `READY_FOR_V2_COMPLETE_AUTHORING_PHASE_A3` only if A2 is fully complete; or
- `PARTIAL_V2_COMPLETE_AUTHORING_PHASE_A2` with the exact remaining gap.

This is engineering evidence only. A3 and all author/config/candidate work stay
closed pending orchestration and independent review.

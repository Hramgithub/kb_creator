# Architecture contributor receipt

- Goal id: `20260830-kb-creator-next-scenario`
- Step id: `3-generic-scenario-contract-specification`
- Role: architecture/root-cause
- Policy model: `gpt-5.6-sol`
- Policy reasoning effort: `high`
- Actual platform model/effort: `unavailable` (not independently exposed to the contributor)
- Orchestrator policy owner: main chat `gpt-5.6-sol`, `medium`
- Assignment state: `matched` by the `nri-architect` role
- Scoped override: `none`
- Timestamp: `2026-08-30T20:16:30+03:00`
- Elapsed time: approximately 50 minutes
- Token use: `unavailable`

## Scope

Read the assigned governance, goal plan/context, pipeline summary and README;
inspect Innsmouth scripts, tests, accepted/production manifests and the legacy
Viral package read-only; specify the minimal declarative scenario-contract
boundary proven by Innsmouth versus Viral. No implementation, source copy,
extraction, OCR, translation, rendering, accepted/production mutation, Git
mutation, commit, push, canonical-state edit, Foundry work, or Sourcefold
mutation was authorized.

Owned write scope was exactly:

1. `kb_creator/docs/plans/20260830-kb-creator-next-scenario/scenario_contract_architecture.md`
2. `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_scenario_contract_20260830.md`

## Result

Completed a reviewable `ScenarioContract.v1` architecture candidate. It fixes
the stage graph in trusted reusable code and moves only reviewed scenario facts
and policies into a closed declarative contract. It includes the generic versus
scenario-specific matrix, schema and page-role taxonomy, stage/state/identity
contracts, translation/reference rules, OCR/text/visual controls, fail-closed
exceptions, acceptance and full-scope QA gates, asset/release closure,
incremental Innsmouth-preserving migration, and an exact first implementation
slice with evidence and stop conditions.

The design rejects a copied Viral script family, importing the legacy
`translator/config/viral.package.json`, executable configuration, generated
output hashes in mutable policy, and big-bang Innsmouth replacement.

Architecture artifact identity:

- bytes: `43577`
- lines: `807`
- SHA-256: `EF96C3B155EB749FBABDFEA5B86BD4C190854F3029D8693E7F09D051F4B9FDBE`

## Files checked

- `AGENTS.md`
- `docs/governance/nri_goal_governance.md`
- `kb_creator/docs/KB_CREATOR_PIPELINE_SUMMARY_20260830.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/plan.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/context.md`
- `kb_creator/README.md`
- all 23 `kb_creator/scripts/*innsmouth*.py` files were inventoried; the active
  reconstruction, EN/RU freeze, HTML, PDF, and production scripts were inspected
  at constants/function boundaries, with the production packager read in detail
- representative Innsmouth build/freeze/production tests under
  `kb_creator/tests/`
- current accepted EN/RU/HTML/PDF acceptance manifests and
  `kb_creator/inputs/innsmouth/production/PRODUCTION_MANIFEST.json`
- `.gitattributes` and read-only Git text-attribute/config state
- `translator/config/viral.package.json` as legacy evidence only
- `C:/Users/BogdanD/.codex/memories/MEMORY.md` narrow registry search; its older
  checkout-specific Innsmouth page-proof record was not used as current product
  authority

## Files changed

- Created
  `kb_creator/docs/plans/20260830-kb-creator-next-scenario/scenario_contract_architecture.md`.
- Created this immutable receipt.
- No other file was intentionally changed.

## Verification and evidence

- Confirmed all required architecture sections exist and Markdown fences are
  balanced.
- Confirmed the receipt target was absent before creation.
- Confirmed the design traces current script constants, accepted manifests,
  tests, canonical context, and legacy Viral evidence without treating the
  latter as authority.
- Confirmed the first implementation slice does not modify existing Innsmouth
  scripts or accepted/production artifacts and forbids `build_viral_*` /
  `freeze_viral_*` duplication.
- Ran the existing production verifier read-only with bytecode disabled:
  `python -B kb_creator/scripts/build_innsmouth_production_package.py --verify`.
  It failed with `ValueError: production package file identity mismatch`.
- Root-cause evidence: Git reports the HTML as `text: auto` with
  `core.autocrlf=true`; the live file is 227,220 bytes with 1,106 CRLF pairs and
  SHA-256
  `BC66D5A2380288B23B8FBED9E85533EE120010A85E408C8DA5E3925A34DF2B49`.
  In-memory LF normalization yields the manifest-bound 226,114 bytes and
  SHA-256
  `B2525DB71F7B6DFA8B0EC935D90E5855A64E4356A7E0CB2DA8595E0BD9995A3C`.
  No accepted file was edited; the architecture records a scoped LF checkout
  rule as an implementation prerequisite and rejects verifier normalization.
- No commit or push was performed.

## Blockers

- No blocker to Step 3 architecture delivery.
- Material implementation remains blocked until the main-chat orchestrator
  captures this result and a fresh independent Step 4 architecture review
  resolves any P0/P1 findings.
- The live Innsmouth production regression cannot currently be called green in
  this Windows checkout until the scoped HTML LF serialization issue is resolved
  and verified from a clean checkout without changing Git blob identities.
- Final release acceptance remains pending the required fresh independent
  `gpt-5.5` release review of a future frozen production candidate.

## Next action

The main-chat orchestrator should verify the two owned artifacts, update
canonical plan/context state, and dispatch a fresh independent `gpt-5.5`
architecture review. If the design is accepted, engineering should execute only
the six-path first implementation allowlist and stop on any Innsmouth identity
or regression conflict.

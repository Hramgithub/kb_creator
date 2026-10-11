# Critic receipt: publication contract authoring closure

- Goal id: `20260914-dissociation-publication`
- Step id: `publication-contract-authoring-closure`
- Review kind: `implementation`
- Role: independent critic
- Requested model / effort: `gpt-5.5` / `medium`
- Actual platform model / effort: unavailable
- Implemented or materially designed candidate: no
- Orchestrator policy owner: `gpt-5.6-sol`, medium
- Assignment state: `platform-unverified`
- Scoped override: none for critic; engineering override remains out of scope
- Timestamp: `2026-09-14T14:23:42+03:00`
- Elapsed time: approximately 2 minutes 12 seconds
- Token use: orchestrator-visible local goal counter `58354` at pre-write checkpoint

## Scope

Reviewed only the publication contract authoring P1/P2 remediation for:

- `kb_creator/scripts/author_scenario_publication_contract.py`
- `kb_creator/contracts/scenario_publication_blueprint.v1.schema.json`
- `kb_creator/contracts/scenario_publication_contract.v1.schema.json`
- `kb_creator/pipeline/publication.py`
- `kb_creator/pipeline/reconstruction_promotion.py`
- `kb_creator/tests/test_author_scenario_publication_contract.py`
- `kb_creator/tests/test_publication_contracts.py`
- `kb_creator/tests/test_reconstruction_promotion.py`
- `kb_creator/docs/plans/20260914-dissociation-publication/plan.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/context.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/critic_pre_gpu_publication_increments_20260914.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_publication_contract_authoring_20260914.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_publication_contract_authoring_remediation_20260914.md`
- `docs/governance/nri_goal_governance.md`

I did not edit production implementation, tests, canonical plan, canonical
context, project status, release files, or Git state. I wrote only this
immutable critic receipt.

## Evidence

- Focused author/schema suite with repository-local `.tools` Python:
  `53 passed, 13 skipped in 1.49s` for
  `kb_creator/tests/test_author_scenario_publication_contract.py` and
  `kb_creator/tests/test_publication_contracts.py`.
- Direct P1/P2 attack selection:
  `24 passed, 11 skipped, 25 deselected in 0.92s`.
  Covered Windows ADS/base-file mutation, portable alternate colon, drive-
  relative, UNC, reserved, hidden, non-json, traversal and unsafe output names,
  output-parent reparse guard, no-overwrite, and whitespace-only semantic field
  rejection. The skipped cases are the jsonschema-gated schema parity rows; the
  runtime rows executed.
- Determinism and zero-write selection:
  `7 passed in 0.57s`.
  Covered byte-deterministic authoring, CLI authored status, runtime validation
  failure cleanup, no final output after failure, and missing/extra/acceptance
  blueprint fields before output.
- Concurrent bridge parity check:
  `1 passed in 0.79s` for
  `test_publication_contract_schema_and_runtime_require_exact_four_roles`.
  This verifies both publication schemas require the exact four upstream roles
  now exported by `ROLE_PATHS`: `reconstructed_en`,
  `reconstruction_manifest`, `reconstruction_qa`, `source_identity`, and that a
  shortened role list fails runtime preflight before creating the run root.
- `py_compile` passed for the author and focused author test.
- Static schema/runtime inspection found the blueprint schema uses a reusable
  `nonblank` definition with pattern `\S` for scenario titles, profile names,
  required QA entries, config paths, and terminology paths. Runtime ingress
  now rejects strings whose `.strip()` is empty.
- `git diff --check --` over the scoped tracked files emitted no whitespace
  diagnostics. The reviewed candidate files are mostly untracked in this
  workspace, so this command is not complete whitespace evidence for every
  candidate file.

## Findings

No remaining P0, P1, or P2 finding in the scoped blueprint-to-contract author
remediation.

The prior P1 is closed: output syntax is rejected before blueprint reads,
validation staging, or final output creation for ADS/colon-bearing, drive-
relative, UNC, hidden, non-json, reserved, traversal-bearing, unsafe component,
and whitespace-tailed paths. Existing visible output remains byte-unchanged,
including the Windows `contract.json:ads` attack against an existing base file.

The prior P2 is closed at the authoring boundary: whitespace-only scenario
titles, profile names, QA labels, config paths, and terminology paths fail
before final output. Blueprint schema parity is present in the schema, but the
jsonschema execution rows remain skipped in this repository-local environment
because `jsonschema` is not installed in `.tools/python-test-deps`.

## Release Fields

This is not a release review and not live acceptance. Candidate revision,
manifest SHA-256, freeze evidence, QA references for a frozen artifact,
declared release exclusions, and invalidation-on-mutation are not applicable to
this implementation closure receipt. Any future frozen release candidate still
requires a fresh independent `release` review.

## Blockers

No scoped authoring blocker remains.

Out-of-scope note: direct validation of independently supplied publication
contracts still uses some `minLength: 1` contract-schema and private runtime
checks for human labels. Contracts produced through this author cannot carry
the remediated blank values, so this is not a remaining blocker for the scoped
authoring candidate.

## Recommendation

Approve the publication contract authoring P1/P2 remediation for integration
within Step 4PD. This recommendation does not approve publication execution,
user acceptance, release acceptance, the reconstruction-promotion bridge, or
any frozen candidate.

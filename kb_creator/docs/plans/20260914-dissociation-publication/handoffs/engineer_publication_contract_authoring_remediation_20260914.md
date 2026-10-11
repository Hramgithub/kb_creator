# Engineering receipt: publication contract authoring remediation

- Goal id: `20260914-dissociation-publication`
- Step id: `publication-contract-authoring-remediation`
- Contributor role: engineering remediation
- Requested model / effort: `gpt-5.6-sol` / `high`
- Actual platform model / effort: unavailable
- Orchestrator policy owner: `gpt-5.6-sol`, medium
- Assignment state: `platform-unverified`
- Scoped override: bounded remediation used the orchestrator-assigned Sol/high profile instead of the default engineering Terra/medium profile
- Timestamp: `2026-09-14T14:19:35+03:00`
- Elapsed time: approximately 24 minutes
- Token use: unavailable

## Scope

Remediated the two findings in
`critic_pre_gpu_publication_increments_20260914.md` at the owned publication
blueprint-author boundary. I did not edit the promotion bridge,
`scenario_master_ru.py`, `publication_adapters.py`, canonical plan/context/status,
README files, live artifacts, or Git state. Concurrent exact-four upstream-role
changes were preserved.

## Result

P1 is closed fail-closed at author ingress:

- Output syntax is rejected before blueprint reads, validation staging, or final
  output creation when it is ADS/colon-bearing, drive-relative, UNC, hidden,
  non-`.json`, reserved, whitespace-tailed, traversal-bearing, or otherwise an
  unsafe path component.
- A local absolute drive prefix remains valid; any colon after that prefix is
  rejected as an NTFS alternate data stream.
- The output parent must already exist, resolve to a directory, and pass the
  reparse-component guard before use. The resolved parent is rechecked and the
  output target is checked for absence again before exclusive creation.
- Write-failure cleanup removes the output only when this author invocation
  successfully created it. It no longer unlinks an arbitrary path merely
  because an `OSError` coincides with an existing object.
- The exact Windows regression `contract.json:ads` against an existing
  user-owned `contract.json` passes with the base bytes unchanged and no ADS
  created. Portable syntax probes cover the same defect class independently of
  NTFS support.

P2 is closed at blueprint/schema ingress:

- Runtime scalar and list string validation now requires at least one
  non-whitespace character.
- The blueprint schema has one reusable `nonblank` definition and applies it to
  scenario titles, profile names, required-QA entries, and relative config or
  terminology file strings.
- Runtime and conditional-jsonschema parity tests cover both scenario titles,
  both profiles, every required-QA policy group, a config path, and a
  terminology path. Enumerated/constant string fields were already closed to
  whitespace-only values.

## Files changed

- `kb_creator/scripts/author_scenario_publication_contract.py`
- `kb_creator/contracts/scenario_publication_blueprint.v1.schema.json`
- `kb_creator/tests/test_author_scenario_publication_contract.py`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_publication_contract_authoring_remediation_20260914.md`

## Verification

All commands used repository-local executables under `.tools`.

- Focused author/schema regression:
  `53 passed, 13 skipped in 2.27s` for
  `test_author_scenario_publication_contract.py` and
  `test_publication_contracts.py`.
- Direct P1 regression selection: `12 passed in 0.49s`, covering the exact
  Windows ADS/base-file case, ten portable invalid-path cases, and the
  fail-before-write output-parent reparse guard.
- Skip accounting: 12 jsonschema-gated cases skipped because `jsonschema` is
  absent from the repository-local `.tools/python-test-deps`; one real symlink
  probe skipped because Windows denied symlink creation. The portable reparse
  guard probe passed.
- Repository-local Python `py_compile` passed for the author and focused test;
  the blueprint schema parsed as JSON.
- PortableGit `diff --no-index --check` against an empty file emitted no
  whitespace diagnostics for each untracked owned implementation file.

## Residual blockers and scope boundaries

- No scoped implementation blocker remains for the blueprint author.
- JSON Schema runtime parity tests are present but could not execute in this
  repository-local tool environment because `jsonschema` is not installed.
  Structural schema assertions and JSON parsing did execute.
- The pre-existing direct contract-schema/private-runtime-validator behavior
  identified by the critic was not changed because
  `scenario_publication_contract.v1.schema.json` and
  `kb_creator/pipeline/publication.py` were outside the assigned ownership.
  Contracts produced through this author cannot contain the blank values now,
  but hardening direct ingestion of independently supplied contracts remains a
  separate owner decision.
- The critic's reconstruction-promotion bridge fixture blocker is outside this
  remediation and was not rerun.

## Next action

The orchestrator should inspect this receipt and the scoped diff, decide whether
to route direct contract-ingestion whitespace hardening to its owning step, and
then request a fresh independent implementation review of the remediated
publication increment.

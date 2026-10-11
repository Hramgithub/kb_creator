# Engineer receipt: MASTER_RU rebind provenance remediation

- Goal id: `20260914-dissociation-publication`
- Step id: `master_ru_rebind_provenance_fix`
- Timestamp: `2026-09-16T01:08:50.4212373+03:00`
- Role: engineering
- Repository-policy engineering assignment: `gpt-5.6-terra` / `medium`
- Actual model and effort telemetry: unavailable
- Orchestrator policy owner: `gpt-5.6-sol` / `medium`
- Assignment state: `platform-unverified`
- Scoped override: none
- Elapsed time: approximately 30 minutes
- Token use: unavailable

## Scope and result

Completed the bounded remediation of the independent critic's P1 finding in
`critic_master_ru_translation_rebind_20260916.md`. Only the assigned script,
test file, and this receipt were changed. No live publication command ran and
no run, acceptance, configuration, canonical plan/context/status, README, or
`.codex` artifact was changed.

Every non-exact translation rebind now requires one exact, previously unused
row from the current accepted MASTER_EN v3 `page_boundary_transitions` ledger.
The proof includes `from_page`, `to_page`, join `mode`, and SHA-256 of the prior
left/right boundary lines. The prior unit stream must contain the exact
`left -> source-page-to_page marker -> right` topology, and its nearest earlier
page marker must prove `from_page`. The current unit stream must contain the
joined source immediately followed by the same `to_page` marker.

The current provenance is discovered beside the packet-bound MASTER_EN, but is
trusted only after the current MASTER_EN acceptance resolves its hash-bound
publication producer stage and that stage's sealed output inventory contains
the exact provenance and MASTER_EN identities. The provenance top level and
nested v3 inputs, projection, master identity, derived metrics, and transition
rows are closed and validated. Duplicate page transitions are rejected. Every
declared transition must be consumed exactly once; an exact-only rebind passes
only when the ledger is empty.

Exact-source translation reuse, separate current/prior authority roots, absent
destination checks, staging, replace, and report rollback behavior remain in
place. The sealed report now includes the current provenance identity, the
transition count, and the exact provenance row used by each non-exact join.

## Changed files

- `kb_creator/scripts/scenario_master_ru.py`
  - SHA-256: `E5A4CD081A2BEAF3818A9A29DB7A5E091302FD928FD360901E61241A6641F725`
- `kb_creator/tests/test_scenario_master_ru.py`
  - SHA-256: `04AE92E18446643DD896D5216A201D7886C95EA93847F5C44894C11C5C11938C`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_master_ru_rebind_provenance_fix_20260916.md`

## Verification evidence

- Seven focused resolver/rebind tests: `7 passed`.
- Remaining test module with the environment-dependent schema test excluded:
  `24 passed, 1 skipped`.
- The unmodified full test-module command reached `24 passed, 1 skipped` and
  one environment error: bundled Python lacks the optional `jsonschema`
  package used only by
  `test_author_submission_is_byte_deterministic_and_schema_valid`. This is not
  a product-code or assertion failure and no dependency was installed.
- `py_compile` passed for the script and test file.
- Scoped `git diff --check` passed.
- Read-only run-14 authority probe resolved the exact hash-bound
  `MASTER_EN.provenance.json` and its two transitions:
  `3->4 dehyphenated_word`, `4->5 continued_prose`.
- Read-only run-12 -> run-14 data probe through the remediated pure rebind path
  produced 84 current translations from 86 prior units with counts:
  `exact_source=82`, `dehyphenated_word=1`, `continued_prose=1`; both provenance
  rows were consumed exactly once.
- Adversarial tests reject a text-shaped join absent from the ledger, wrong
  mode, wrong page pair, wrong left hash, wrong right hash, duplicate ledger
  page pair, unused ledger rows, non-v3/extra-field provenance, current MASTER_EN
  identity drift, and stage-inventory provenance drift.

## Risks and next action

- P0/P1 known in this bounded implementation: none after focused verification.
- The provenance resolver intentionally requires the accepted current
  `publication_stage_manifest.v1` producer inventory; a non-publication packet
  cannot silently supply an unbound adjacent ledger and fails closed.
- The earlier critic's crash-window P2 for destination-directory replace before
  report write is unchanged; normal exceptions still roll the destination back.
- Next action: independent `gpt-5.5` implementation review, then a fresh
  publication run only if the orchestrator authorizes it. This receipt does not
  approve release or live execution.

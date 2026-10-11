# Engineer receipt: MASTER_RU submission, hard-break and independent QA closure

## Metadata and result

- Goal id: `20260914-dissociation-publication`
- Step: generic Stage 20/21 P1.1-P1.3 remediation
- Role: engineering under the user-scoped `gpt-5.6-sol` / `high` override
- Timestamp: `2026-09-15T13:20:25+03:00`
- Authority: `architect_dissociation_master_ru_stage20_execution_20260915.md`
- Authority SHA-256: `9BC7B733D63965486791FFA564BF209374B578133923894639DB8971BA341B68`
- Result: PASS for bounded implementation and self-contained verification
- Schema decision: no schema change was needed; the existing
  `master_ru_submission.v1` shape expresses every required identity and seal
- Live actions: none; no config/contract/glossary/source/current run/accepted
  package/canonical state mutation, publication execution, acceptance,
  translation content, MinerU/CPU, Word/Poppler execution, commit, or push

## Implemented closure

### P1.1 - generic submission author

`scenario_master_ru author-submission` now accepts only `--packet-root`,
`--batch-root`, `--destination`, and `--authority-root`. It derives scenario and
authority identities from the validated packet, requires the exact expected
batch filenames, closed outer/unit shapes, unchanged source fields and order,
nonempty Russian payloads, recomputed batch/unit/file identities, closed review,
and a full passing runtime submission validation. The destination must be
absent, run-local and non-reparse. Canonical output is written through a
same-parent temporary file and atomically renamed; failures remove staging and
never overwrite an existing destination.

### P1.2 - Markdown line topology

The generic producer signature now retains ordered per-line structural class,
the exact two-space hard-break boolean for every line, explicit `<br>` counts,
fenced-code boundary kind/width, and per-line emphasis delimiter structure in
addition to existing page marker, anchor, image/link, heading, list, table and
mechanics checks. The synthetic compact statblock passes with exactly ten hard
breaks; the otherwise identical zero-hard-break attack returns the stable
`markdown_or_mechanics_drift` finding and cannot author or materialize output.

Read-only confirmation against the immutable historical Stage 10 candidate:
`20,863` bytes, `87` translation units, with `unit-00087` containing exactly
`10` hard breaks. No file under that run was written.

### P1.3 - independent Stage 21 verification and acceptance

Added `verify_scenario_master_ru.py`, a standard-library-only verifier with no
producer-module import. It independently validates and rederives accepted
MASTER_EN authority, packet/task/batch/source topology and counts, split-unit
coverage, submission/batch/Russian hashes, Markdown/mechanics signatures,
applicable terminology and forbidden variants, exact assembled MASTER_RU,
copied assets, producer QA, terminology QA, provenance, closed candidate file
set and inventory. Its sealed result is explicitly
`verified_candidate_pending_user_acceptance`, never acceptance.

Stage 21 runs this verifier before publication, checks its candidate,
submission, packet, contract, inventory and required-QA identities, writes
`evidence/MASTER_RU.verification.json`, and quarantines partial staging if the
verifier fails. The implementation inventory now binds the verifier.

For publication contracts requiring `independent_translation_qa`, MASTER_RU
acceptance now requires exactly both `MASTER_RU.qa.json` and
`MASTER_RU.verification.json`. Producer-only, verifier-only, stale/non-pass,
wrong candidate/submission/packet/contract/inventory/required-QA and substituted
evidence fail closed. Legacy contracts without that new declared requirement
retain their existing route.

No scenario-specific constant appears in reusable implementation.

## File identities

- `kb_creator/scripts/scenario_master_ru.py`: `44026` bytes,
  SHA-256 `2B0B5CE22665A618C880AE53C6ECC0E245179A92EAC28AC7430D14F419744DA2`
- `kb_creator/scripts/verify_scenario_master_ru.py`: `34552` bytes,
  SHA-256 `90B18E798E29AFD2CA9338C4B73088421167BC0987B3E9ACF8DD76550203B610`
- `kb_creator/pipeline/publication_adapters.py`: `46466` bytes,
  SHA-256 `0999DDBA41473B22A103798EBC759C437DE58A6FD72C79B48619C1D4300F012B`
- `kb_creator/pipeline/publication.py`: `74416` bytes,
  SHA-256 `32A39B5FFFEB46CE1E8225AA4C3D860A26A829F1AFD76A997429CA2533E42B0C`
- `kb_creator/tests/test_scenario_master_ru.py`: `21598` bytes,
  SHA-256 `63A7A4F69025BBD06C89C015E05DE42C35CA501EDC856F4B989DF58AD34A4082`
- `kb_creator/tests/test_verify_scenario_master_ru.py`: `10338` bytes,
  SHA-256 `1F712F4C08BB9A783D86D50063F439D9FC1F6D77C9570F18FD4D1D49564C7A2D`
- `kb_creator/tests/test_publication_registry_e2e.py`: `23762` bytes,
  SHA-256 `3DE1686873F19385CBE04C56638823558A2CC4EC1D9C5A494DB708266D765895`

All seven owned code/test paths were already untracked working-tree artifacts
or contained adjacent uncommitted publication work when this packet began.
Edits were restricted to the assigned functions/tests; adjacent work was not
reverted.

## Verification evidence

Runtime: repository-local `.tools/MinerU/.venv/Scripts/python.exe` used only as
Python with `PYTHONPATH=.tools/python-test-deps`; no dependency installation or
MinerU model/CPU pipeline invocation.

1. `py_compile` for all four implementation files and three owned test files:
   PASS.
2. Final self-contained producer/verifier/registry/control-plane matrix on the
   final code: `65 passed, 1 skipped, 17 subtests passed` in `93.86s`.
   The skip is the Windows `WinError 1314` inability to create the test symlink;
   the reparse rejection logic remains covered structurally and is fail-closed.
3. Remaining publication contract/HTML/DOCX/PDF/render regression set on the
   final code: `17 passed, 1 skipped` in `19.37s`.
   The skip is the already documented Word COM activation limitation
   `0x80070520`; no Word or Poppler production execution was attempted.
4. Combined final evidence: `82 passed`, `2` explicit host-conditional skips,
   `17 subtests passed`.
5. Direct immutable Stage 10 read-only signature probe: `87` units and exactly
   `[('unit-00087', 10)]` for nonzero hard-break units.
6. `git diff --check` over all seven owned implementation/test paths: PASS.

Coverage includes deterministic author output and JSON Schema validity;
missing/extra/renamed batches; duplicate/reordered units; source text/hash and
empty-RU attacks; mechanics, terminology, hard-break, `<br>`, fence and emphasis
drift; destination escape/no-overwrite/reparse behavior; stale packet and
submission identities; independent split-unit verification; candidate, asset,
QA, terminology, provenance and inventory tampering; Stage 21 verifier-failure
quarantine; implementation inventory binding; and the complete MASTER_RU
acceptance evidence matrix.

## Findings, blockers, next action

- P0: none.
- P1: P1.1, P1.2 and P1.3 are implemented and locally closed by the bounded
  matrix above.
- P2: none in the owned implementation. Two host-conditional skips are recorded
  as environment evidence, not inferred passes.
- Blockers to this bounded packet: none.
- Remaining gate: independent implementation review. The current publication
  run remains immutable/non-resumable because its sealed implementation identity
  predates these changes.

Next action: an independent critic reviews the seven owned code/test paths and
this receipt. Only after no P0/P1 remains may the orchestrator create a fresh
absent publication run, reproduce Stage 10, independently verify it, and return
to explicit MASTER_EN user acceptance before Stage 20.

# Engineer receipt: shared terminology gate

- Goal id: `20260914-dissociation-publication`
- Step id: `shared-terminology-gate-remediation`
- Role: engineering contributor
- Requested model: `gpt-5.6-sol`
- Actual platform model: unavailable
- Effort: `high`
- Orchestrator policy owner: `gpt-5.6-sol`, medium
- Assignment state: `user-overridden-platform-unverified`
- Scoped override: engineering implementation for this goal uses
  `gpt-5.6-sol` at high instead of the repository Terra/medium default.
- Timestamp: `2026-09-14T14:02:39+03:00`
- Elapsed time: unavailable
- Token use: unavailable

## Scope

Close two scenario-neutral publication gaps: fail-closed parsing and per-unit
enforcement of declared MASTER_RU terminology authorities, and retention of
the exact authorities in the Stage 70 production package. No acceptance,
release, schema, live-artifact, canonical plan/context/status, README, Git, or
`.codex` state was changed.

## Result

Completed.

- Legacy JSON terminology remains supported through a closed `terms` object.
- The shared CoC CSV schema and strict three-column Markdown terminology table
  are parsed. Unsupported suffixes, malformed headers/rows, empty accepted
  authorities, unsafe empty source/target values, duplicate normalized sources
  within one authority, and conflicting cross-authority decisions fail closed.
- Compatible decisions repeated across different authorities merge
  deterministically; this is required by the selected CoC CSV and Markdown
  authorities, which overlap on five identically accepted terms.
- Accepted targets, aliases, and known bad variants are matched with word/phrase
  boundaries in each applicable source/Russian unit. Evidence includes the
  authority role(s) and unit id. Markdown notes are not mined heuristically.
- Stage 70 validates every `contract.master_ru.terminology` record with closed
  identity, containment/reparse, exact bytes/SHA-256, suffix, and duplicate
  identity checks before copying. Each authority is copied once to
  `configs/source/terminology/authority-NN<suffix>` and is included
  automatically in `config_inventory`. The package role list remains exactly
  22 entries.

## Files changed

- `kb_creator/scripts/scenario_master_ru.py`
- `kb_creator/pipeline/publication_adapters.py`
- `kb_creator/tests/test_scenario_master_ru.py`
- `kb_creator/tests/test_publication_registry_e2e.py`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_shared_terminology_gate_20260914.md`

## Verification

- Focused suite:
  `12 passed, 6 subtests passed in 11.97s` for
  `test_scenario_master_ru.py` and `test_publication_registry_e2e.py`.
- Expanded publication regression:
  `65 passed, 2 skipped, 4 subtests passed in 81.98s` across MASTER_RU,
  publication contracts/control, HTML, DOCX, DOCX-to-PDF, render QA, package
  verifier, and registry E2E tests. The two skips are existing host-conditional
  cases.
- The two real selected authorities parse together as `80` merged terms and
  `85` authority bindings; their five compatible overlaps are retained.
- `py_compile` passed for both changed modules and both changed tests.
- Portable Git whitespace checks passed, including `--no-index --check` for
  the currently untracked publication files.
- E2E evidence proves exact CSV/Markdown package bytes, presence in
  `config_inventory`, exact 22 roles, and offline-verifier rejection after a
  copied authority is tampered. Focused tests also prove duplicate identity and
  source-authority drift rejection before package writes.

## Blockers

None for this bounded implementation. Live publication and user acceptance
remain outside this task.

## Next action

Run independent implementation review against this receipt and the changed
files. If accepted, the orchestrator may update canonical goal state; final
release acceptance still requires the independent release gate.

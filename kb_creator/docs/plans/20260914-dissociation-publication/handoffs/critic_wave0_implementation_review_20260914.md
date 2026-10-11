# Independent critic receipt - Wave 0 implementation review

## Assignment receipt

- Goal id: `20260914-dissociation-publication`
- Step id: `3R-wave0-implementation-review`
- Review kind: `implementation`
- Role: independent critic
- Requested model: `gpt-5.5`
- Requested reasoning effort: `medium`
- Actual platform model/effort: unavailable; repository-policy assignment only
- Participation declaration: I did not implement or materially design the candidate under review.
- Orchestrator policy owner: `gpt-5.6-sol` at `medium`; actual platform identity unverified
- Assignment state: `platform-unverified`
- Scoped override: none
- Scope: read-only implementation review of the current shared worktree for the neutral reconstruction contract and Wave 0 reconstruction control plane. No reviewed code, schemas, canonical plan/context/status, generated artifacts, release files, or Git state were edited.
- Verdict: reject for live execution until P1-1 is fixed and retested. The earlier neutral-contract blocker is closed, but the real production resume adapter is currently wired to the wrong merge-packet root.
- Timestamp: `2026-09-14T04:07:49+03:00` (`Europe/Moscow`)
- Elapsed time: approximately `00:45:00`
- Token use: unavailable

## Files checked or changed

Checked:

- `kb_creator/docs/plans/20260914-dissociation-publication/plan.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/context.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_generic_reconstruction_control_plane_spec_20260914.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/critic_generic_reconstruction_control_plane_review_20260914.md`
- `.agents/skills/kb-creator-scenario-reconstruction/SKILL.md`
- `kb_creator/__main__.py`
- `kb_creator/pipeline/identity.py`
- `kb_creator/pipeline/process.py`
- `kb_creator/pipeline/manifests.py`
- `kb_creator/pipeline/reconstruction.py`
- `kb_creator/contracts/scenario_reconstruction_contract.v1.schema.json`
- `kb_creator/contracts/run_spec.v1.schema.json`
- `kb_creator/contracts/stage_manifest.v1.schema.json`
- `kb_creator/contracts/review_queue.v1.schema.json`
- `kb_creator/contracts/reconstruction_decision_set.v1.schema.json`
- `kb_creator/scripts/prepare_mineru_three_view_inputs.py`
- `kb_creator/scripts/build_mineru_visual_merge_bundle.py`
- `kb_creator/scripts/audit_mineru_ai_merge_fidelity.py`
- `kb_creator/scripts/materialize_mineru_ai_merge.py`
- `kb_creator/tests/test_pipeline_identity.py`
- `kb_creator/tests/test_reconstruction_control_plane.py`
- `kb_creator/tests/test_mineru_three_view_tools.py`
- `kb_creator/tests/test_mineru_visual_merge_bundle.py`
- `kb_creator/tests/test_audit_mineru_ai_merge_fidelity.py`
- `kb_creator/tests/test_materialize_mineru_ai_merge.py`
- current `git status --short --branch` and `git diff --stat`

Changed:

- added this receipt only:
  `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/critic_wave0_implementation_review_20260914.md`

## Tests and probes run

- Passed: `C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m py_compile kb_creator/__main__.py kb_creator/pipeline/identity.py kb_creator/pipeline/process.py kb_creator/pipeline/manifests.py kb_creator/pipeline/reconstruction.py kb_creator/scripts/prepare_mineru_three_view_inputs.py kb_creator/scripts/build_mineru_visual_merge_bundle.py`
- Could not run focused pytest suite in this shell: bundled Python reports `No module named pytest`; `py -m pytest --version` reports `No installed Python found!`.
- Direct temporary probe of `audit_mineru_ai_merge_fidelity.audit()` confirmed the root contract: calling it with a root containing `merge_index.json` passes, while calling it with that root's `pages/` subdirectory fails with `ValueError: merge index: invalid JSON`.

## Findings

### P1-1 - Production resume adapter passes the wrong merge-packet root to the fidelity auditor

Evidence:

- `kb_creator/pipeline/reconstruction.py:1428-1434` builds the production fidelity audit argv and passes `--merge-packets-root` as `bundle_root / "merge_packets" / "pages"`.
- `kb_creator/scripts/audit_mineru_ai_merge_fidelity.py:61-62` defines `_packet_index(root)` and opens `root / "merge_index.json"`.
- The actual bundle layout puts the index at `<bundle>/merge_packets/merge_index.json`, not under `<bundle>/merge_packets/pages/`.
- `kb_creator/tests/test_reconstruction_control_plane.py:258-282` verifies resume through injected `resume_adapters()`, so the synthetic six-stage pass does not exercise the real production fidelity argv.
- The direct probe reproduced the mismatch: correct packet root passes; `packets/pages` root fails before audit.

Impact:

The real `resume` path cannot complete fidelity audit and materialization with the current production adapter. This blocks live Dissociation execution and any claim that Wave 0 can resume from reviewed decisions using the production command path.

Exact remediation:

1. Change the production fidelity argv to pass `str(bundle_root / "merge_packets")` to `--merge-packets-root`.
2. Add a regression test that exercises `production_resume_adapters()` or captures its real argv and proves the auditor receives the index root, not `pages/`.
3. Add a small real-adapter smoke using a minimal bundle/decision fixture where possible, or refactor only enough to inject `pipeline_process.run` and assert the production command line.
4. Rerun the focused control-plane, audit, materializer, visual-bundle, and geometry tests before authorizing any live run.

### P2-1 - Review queue issue kinds are under-derived from the contract and comparison evidence

Evidence:

- The architecture spec requires queue items to surface issue kinds from contract traits/strategies, MediaBox-versus-CropBox differences, comparison conflicts, unmatched assets, and diagnostics.
- `kb_creator/pipeline/reconstruction.py:884-930` builds queue rows but always emits `issue_kinds: ["page_fidelity"]`.
- The queue does preserve `contract_traits` and `contract_strategies`, so the raw data is not lost, but the typed routing signal is weaker than specified.

Impact:

This does not by itself allow silent acceptance because every page remains open and must be visually reviewed through the decision set. It does, however, weakens the repeatable review queue and could cause Dissociation-specific risks such as `reading_order`, `ocr_region`, `visual_preserve`, `structured_statblock`, or `geometry_box_difference` to be missed by a reviewer relying on queue categories.

Exact remediation:

1. Derive at least `reading_order`, `visual_preserve`, `ocr_region`, `structured_statblock`, and `form_like` from contract strategies/traits.
2. Add comparison-derived `semantic_conflict` and `asset_ambiguity` when those records appear in the comparison or merge packet.
3. Record `geometry_box_difference` when prepare/contract evidence shows CropBox differs from MediaBox.
4. Add a synthetic test proving those issue kinds appear without scenario-specific constants.

### P2-2 - Current live test evidence is not independently reproducible in this shell

Evidence:

- The active plan/context claims a focused suite of `81` tests passes.
- In this review shell, `python` is not on PATH; the bundled Python exists but has no `pytest`; `py` reports no installed Python.
- `py_compile` is clean, and static/probe evidence was collected, but the focused pytest suite could not be rerun.

Impact:

The implementation may have passed in a different environment, but this review cannot independently confirm the current `81`-test claim. Because P1-1 already rejects live execution, this is secondary rather than the primary blocker.

Exact remediation:

1. Provide or select the approved pytest/PDF dependency environment used for the claimed focused suite.
2. Rerun the focused tests after P1-1 is fixed.
3. Capture the exact Python path, command, and result in the implementation follow-up receipt.

## Closed prior findings and accepted areas

- Neutral contract separation: accepted. `scenario_reconstruction_contract.v1` is reconstruction-only and contains no `viral_print`, `accepted_html -> pdf`, ArtView, DOCX, PDF, production, or publication authority. `validate_contract()` rejects `kb_creator.scenario_contract.v1` by schema/contract-revision mismatch.
- Downstream target rejection: accepted at implementation level. `__main__.py:87-99` rejects non-`reconstructed_en` targets before calling `run_engine()` or `resume_engine()`, and `preflight()` rejects unsupported targets before loading source/contract or creating a run root.
- No contract-driven Viral 124-page fallback: accepted with one caveat. The production run adapter passes `--reconstruction-contract`, and `build_mineru_visual_merge_bundle.py:273-293` derives page count and roles from the neutral contract when supplied. The legacy 124-page fallback remains for direct legacy compatibility.
- Source/contract/tool/implementation/local binding checks: accepted. The run binds source bytes/hash/geometry, contract hash, implementation inventory, tool identities, and local paths; resume revalidates these before stages.
- Reproducible StageManifest hashing: accepted. `reproducible_sha256` is computed from the `reproducible` section only, excluding execution timestamps and diagnostics.
- Output/path/reparse safety: mostly accepted. Stage output inventories are deterministic and symlink-rejecting; writable path components are checked for reparse points; stale outputs and path escapes fail closed.
- Decision and allowlist identity: accepted. Decision set, page decisions, and optional allowlist are included in resume stage inputs/cache identity.
- Failure quarantine: accepted. Partial staging output is moved under `failures/<stage_id>` and no passing stage manifest remains.
- Production run adapter argv: accepted for prepare, MinerU, compare, and visual bundle. Production resume adapter argv is rejected by P1-1.
- Publication boundary: accepted for Wave 0. No Wave 0 public target implements MASTER, ArtView, HTML, DOCX, PDF, production, acceptance, freeze, or release.

## Recommendation

Reject live execution and do not authorize a Dissociation runtime run until P1-1 is fixed and retested. After P1-1 closure, a short follow-up implementation review can be limited to the production resume argv, real-adapter regression coverage, focused test rerun, and the P2 queue-category improvement if the orchestrator wants it closed before live work.

This is not a release review and does not approve a frozen candidate.

## Next action

Engineering/orchestrator should patch only the production fidelity adapter root and add a real production-adapter regression, then rerun the focused suite in an approved Python environment. Live MinerU execution remains blocked until a critic verifies P1 closure.

## Closure review - 2026-09-14T04:13:01+03:00

### Closure receipt

- Review kind: `implementation`
- Scope: short Step 3R closure review of changes since this receipt was first written. No implementation, canonical state, code, schema, generated, release, or Git files were edited.
- Participation declaration: I did not implement or materially design the closure changes.
- Orchestrator policy owner: `gpt-5.6-sol` at `medium`; actual platform identity unverified
- Assignment state: `platform-unverified`
- Scoped override: none
- Changed by this closure review: appended this section only.
- Verdict: approve Step 3R closure for live Dissociation reconstruction-contract materialization and preflight. This is not reconstruction acceptance, live candidate acceptance, release review, Git approval, or publication authorization.

### Closure evidence

- P1-1 is closed. `kb_creator/pipeline/reconstruction.py:1489-1494` now passes `--merge-packets-root` as `bundle_root / "merge_packets"`, matching `audit_mineru_ai_merge_fidelity.py:61-62`, which expects `root / "merge_index.json"`.
- Direct production-adapter regression is present. `kb_creator/tests/test_reconstruction_control_plane.py:568-596` monkeypatches the production resume adapter command runner and asserts the captured `--merge-packets-root` is `outputs/04-visual-merge-bundle/merge_packets` and not `pages`.
- P2-1 is closed for Wave 0. `kb_creator/pipeline/reconstruction.py:954-986` derives review issue kinds from contract strategies, traits, geometry-box differences, and merge review signals. `kb_creator/tests/test_reconstruction_control_plane.py:537-562` verifies `reading_order`, `visual_preserve`, `ocr_region`, `structured_statblock`, `structured_table`, `form_like`, `geometry_box_difference`, `semantic_conflict`, and `asset_ambiguity` without scenario constants.
- `make_queue()` now receives the prepared manifest at `kb_creator/pipeline/reconstruction.py:1241-1248`, allowing MediaBox/CropBox differences from prepare evidence to feed queue issue kinds.
- Scenario leakage check over Wave 0 code/contracts/tests found no `Dissociation`, `Innsmouth`, `Viral`, `viral_print`, `accepted_html`, direct print-to-PDF, or production-PDF route in the new control-plane authority. The only `html-to-pdf` hit is the negative unsupported-target test.

### Exact focused test

Command run:

```powershell
$env:PYTHONPATH='C:\_Hobby\_work\NRI\tmp\kb_creator_test_deps;C:\_Hobby\_work\NRI'
& 'C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest -q kb_creator\tests\test_pipeline_identity.py kb_creator\tests\test_reconstruction_control_plane.py kb_creator\tests\test_mineru_three_view_tools.py kb_creator\tests\test_mineru_visual_merge_bundle.py kb_creator\tests\test_audit_mineru_ai_merge_fidelity.py kb_creator\tests\test_materialize_mineru_ai_merge.py
```

Result: `83 passed in 9.42s`.

### Remaining findings

- P0: none.
- P1: none remaining for Step 3R closure.
- P2: none remaining that blocks live contract materialization or preflight. Publication-contract, ArtView, DOCX, PDF-from-DOCX, production packaging, freeze, and release review remain later scoped work.

### Closure recommendation

Step 3R may close. The orchestrator may proceed to write/validate the Dissociation neutral reconstruction contract and run live preflight under the normal immutable-source and no-acceptance gates. Any live MinerU run still remains a reconstruction execution step, not reconstruction acceptance or release approval.

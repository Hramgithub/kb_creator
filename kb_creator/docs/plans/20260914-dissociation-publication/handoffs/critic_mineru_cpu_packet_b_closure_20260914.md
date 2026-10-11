# Independent implementation critic receipt - MinerU CPU-first Packet B closure

## Receipt

- Goal id: `20260914-dissociation-publication`
- Step id: `packet-b-runspec-view-execution-comparison`
- Review kind: `implementation`
- Candidate state reviewed: non-frozen implementation candidate for Packet B; not a release candidate
- Role: independent implementation critic
- Policy critic role/model/effort: `gpt-5.5` at `medium`
- Actual platform model/effort: unavailable; repository-policy assignment only
- Implemented or materially designed candidate: no
- Orchestrator policy owner: `gpt-5.6-sol` at `medium`; orchestration ownership does not transfer
- Assignment state: `platform-unverified`
- Scoped override: none for this critic review
- Timestamp: `2026-09-14T20:19:53.1224362+03:00` (`Europe/Moscow`)
- Elapsed time: approximately `00:07:43`
- Token use: unavailable in platform terms; local goal meter reported `150357` tokens at receipt write

This receipt is independent implementation criticism only. It is not a real
Dissociation source run, human merge decision, reconstruction acceptance,
publication acceptance, release review, release approval, Git action, or
orchestration ownership transfer.

## Authority reviewed

- `AGENTS.md`
- `docs/governance/nri_goal_governance.md`
- `kb_creator/README.md`
- `kb_creator/PROJECT_STATUS.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_mineru_cpu_first_execution_spec_20260914.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_mineru_cpu_packet_b_20260914.md`
- assigned receipt path checked absent before writing:
  `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/critic_mineru_cpu_packet_b_closure_20260914.md`

## Files checked

- `kb_creator/__main__.py`
- `kb_creator/pipeline/reconstruction.py`
- `kb_creator/pipeline/mineru_cpu_first.py`
- `kb_creator/scripts/run_mineru_three_view.ps1`
- `kb_creator/scripts/compare_mineru_three_views.py`
- `kb_creator/scripts/build_mineru_visual_merge_bundle.py`
- `kb_creator/contracts/run_spec.v1.schema.json`
- `kb_creator/contracts/run_spec.v2.schema.json`
- `kb_creator/contracts/mineru_provider_capabilities.v1.schema.json`
- `kb_creator/contracts/mineru_view_execution.v1.schema.json`
- `kb_creator/contracts/mineru_view_set.v1.schema.json`
- `kb_creator/contracts/mineru_multi_view_comparison.v2.schema.json`
- `kb_creator/tests/test_mineru_cpu_packet_b.py`
- `kb_creator/tests/test_reconstruction_control_plane.py`
- `kb_creator/tests/test_mineru_three_view_tools.py`
- `kb_creator/tests/test_mineru_visual_merge_bundle.py`
- `kb_creator/tests/test_audit_mineru_ai_merge_fidelity.py`
- `kb_creator/tests/test_materialize_mineru_ai_merge.py`
- `kb_creator/tests/test_finalize_mineru_reconstruction.py`
- `kb_creator/tests/test_reconstruction_promotion.py`
- `kb_creator/tests/test_reconstruction_promotion_adversarial.py`
- `kb_creator/tests/test_pipeline_identity.py`

Only this immutable receipt was written. No implementation, test, schema,
canonical plan/context/status/release, `.tools`, immutable source, generated
output, Git index, commit, remote, install, download, network, GPU, API, or
real PDF action was performed.

## Evidence

Static review found the Packet B implementation matches the required
CPU-first shape:

- `kb_creator.run_spec.v2` is additive and preserves strict v1 handling.
- The v2 profile is fixed to `mineru_cpu_first_three_view_v1`.
- The view plan is exactly ordered as three required CPU views followed by two
  optional CUDA enrichment views:
  `original_pipeline_txt`, `original_pipeline_ocr`,
  `raster_pipeline_ocr`, `original_hybrid_high`, `original_vlm`.
- The v2 path requires provider capabilities, MinerU source root, and closed
  `ocr_language` together before run-root creation.
- Provider receipt order is exact: `pipeline_cpu`, `hybrid_cuda`, `vlm_cuda`.
  Required CPU must be `ready`; optional `invalid` fails; optional
  `unavailable` is the only skip-producing path.
- Ready providers bind verification receipt, install receipt, Python, MinerU,
  config, lock, installed distributions, source inventory, and model rows.
- Stage 01 validation requires `MediaBox`, raster-only mode,
  `raster_has_text_layer: false`, exact source identity, and exact page
  mapping.
- Stage 02 validates per-view receipts, output inventories, page coverage, and
  the five required MinerU artifact classes for succeeded views; skipped views
  must be output-free and not invoked.
- Stage 03 manifest mode derives all pairwise comparisons from succeeded
  views and records skipped optional views without inventing parity.
- Stage 04 rebuilds packets from comparison evidence and keeps the required
  CPU triptych as baseline; every source page must have an open packet.
- Resume revalidates run, source, contract, implementation, frozen provider
  snapshot, profile/tool/model/config/lock identity, Stage 01-04 evidence,
  queue, decisions, and stage inventories before writing Stages 05-06.
- Production CPU-first adapter constructs closed local argv and does not take
  command, executable, URL, endpoint, remote, API, or scenario-specific route
  from the scenario contract.
- Public promotion CLI names remain `reconstruction-promotion materialize` and
  `record-acceptance`; Packet B did not change promotion bridge files.

Commands run:

- `compileall` on Packet B Python files:
  `kb_creator/pipeline/mineru_cpu_first.py`,
  `kb_creator/pipeline/reconstruction.py`,
  `kb_creator/scripts/compare_mineru_three_views.py`,
  `kb_creator/scripts/build_mineru_visual_merge_bundle.py`,
  `kb_creator/tests/test_mineru_cpu_packet_b.py`
  -> PASS.
- PowerShell parser:
  `kb_creator/scripts/run_mineru_three_view.ps1`
  -> PASS.
- JSON parse:
  `run_spec.v1.schema.json`, `run_spec.v2.schema.json`,
  `mineru_provider_capabilities.v1.schema.json`,
  `mineru_view_execution.v1.schema.json`,
  `mineru_view_set.v1.schema.json`,
  `mineru_multi_view_comparison.v2.schema.json`
  -> PASS.
- Dependency probe:
  bundled Codex Python had no `pytest`; `.tools/python-test-deps` contained
  flat packages, so tests were run read-only with
  `PYTHONPATH=.tools\python-test-deps`. Probe confirmed `pytest 9.1.1`.
- Focused Packet B/reconstruction slice:
  `test_mineru_cpu_packet_b.py`,
  `test_reconstruction_control_plane.py`,
  `test_mineru_three_view_tools.py`,
  `test_mineru_visual_merge_bundle.py`,
  `test_reconstruction_promotion.py`,
  `test_reconstruction_promotion_adversarial.py`,
  `test_pipeline_identity.py`
  -> `144 passed, 1 skipped in 50.63s`.
- Materializer/fidelity/finalize slice:
  `test_audit_mineru_ai_merge_fidelity.py`,
  `test_materialize_mineru_ai_merge.py`,
  `test_finalize_mineru_reconstruction.py`
  -> `67 passed in 21.79s`.
- Combined Packet B candidate-adjacent slice:
  all ten files above
  -> `211 passed, 1 skipped in 69.46s`.
- Expanded mixed suite including broader publication/master-package tests:
  -> `180 passed, 2 skipped, 6 subtests passed, 63 failed in 100.20s`.
  Every reported failure shown was in `test_build_scenario_master_en.py` and
  stemmed from missing or drifted Viral v2 fixture authorities such as
  `kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf`,
  `publication_config_v1.json`, and
  `kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4`.
  I do not classify those as Packet B findings.
- Scoped `git diff --check` on Packet B-owned files:
  PASS; Git emitted only the Windows advisory that
  `kb_creator/scripts/run_mineru_three_view.ps1` LF will be replaced by CRLF
  the next time Git touches it.

## Findings

### P0

None found.

### P1

None found.

### P2

1. Shared wrapper accepts CPU-first profile names in legacy mode.

   Evidence: `kb_creator/scripts/run_mineru_three_view.ps1` expands the top
   `ValidateSet` from `hybrid_high`, `pipeline_ocr` to include
   `pipeline_txt` and `vlm_local`. In the CPU-first `-ToolRoot` branch those
   values are handled correctly and are covered by tests. In the legacy
   `-MinerURoot` branch, however, any profile other than `hybrid_high` falls
   through to legacy pipeline OCR. This does not affect the new v2 production
   path, which always supplies `-ToolRoot`, and the legacy adapters inspected
   still call only the old legacy profile names. It is nevertheless a small
   direct-CLI surface change, so it should be tightened later by rejecting
   `pipeline_txt` and `vlm_local` unless `-ToolRoot` is present.

## Blockers

No Packet B P0/P1 blocker remains.

Non-blocking evidence caveats:

- The current review did not run a live real Dissociation PDF through MinerU,
  by assignment.
- The broader unrelated `test_build_scenario_master_en.py` suite is not
  runnable in this workspace state because Viral v2 fixture authorities are
  missing or drifted.
- Native Python launchers/environments did not expose `pytest`; successful
  pytest evidence required the existing flat `.tools/python-test-deps` package
  directory on `PYTHONPATH`.

## Recommendation

GO from Packet B implementation-review scope for a fresh real Dissociation
CPU-only reconstruction run on the current station, provided the main
orchestrator confirms the already closed Packet A/profile and Packet C/
promotion gates are still current and the candidate has not mutated after this
receipt.

The future real run must remain local/current-station only, use the verified
CPU profile with `ocr_language: en`, create a fresh v2 run root, preserve the
old whole-run CUDA skip as immutable/unpromotable history, and stop at the
human review gate before any acceptance claim.

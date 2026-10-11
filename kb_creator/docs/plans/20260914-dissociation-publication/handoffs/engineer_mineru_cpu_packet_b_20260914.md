# Engineering receipt — MinerU CPU-first Packet B

## Assignment receipt

- Goal id: `20260914-dissociation-publication`
- Step id: `packet-b-runspec-view-execution-comparison`
- Role: engineering worker
- Assigned role/model/effort: engineering / `gpt-5.6-sol` / `high`
- Repository-policy default for engineering assistance: `gpt-5.6-terra`,
  `medium` (superseded by the scoped user override)
- Assignment state: `assigned-with-scoped-override`
- Orchestrator policy owner: `gpt-5.6-sol`, `medium`
- Architecture input:
  `architect_mineru_cpu_first_execution_spec_20260914.md`
- Result: reusable CPU-first RunSpec/view execution/comparison path implemented
- Timestamp: `2026-09-14` (`Europe/Moscow`)
- Token use: unavailable

This receipt is implementation evidence only. It is not a real source run,
human merge decision, reconstruction acceptance, publication acceptance,
independent closure, or release decision.

## Result

Packet B adds the closed `kb_creator.run_spec.v2` profile
`mineru_cpu_first_three_view_v1` while preserving the v1 loader, legacy
adapters, six-stage graph, decision gate, and public promotion interface.

The new portable identity fixes the exact ordered plan:

1. required `original_pipeline_txt`;
2. required `original_pipeline_ocr`;
3. required `raster_pipeline_ocr`;
4. optional `original_hybrid_high`;
5. optional `original_vlm`, with method explicitly null and omitted from argv.

Preflight validates the exact sealed provider snapshot, required ready CPU
profile, used profile verification/install receipts, managed executable,
MinerU executable, source inventory, installed-distribution receipt,
configuration, lock, required model rows, wrapper/helper identities, and
implementation inventory before run-root creation. CPU-first CLI dispatch
requires provider receipt, MinerU source root, and closed OCR language together;
partial dispatch is rejected without writes.

Stage 01 remains MediaBox/raster-only and binds page mapping and source lineage.
Stage 02 creates three mandatory CPU view receipts and either successful
optional views or sealed output-free provider-local skips. The wrapper builds
only the reviewed local argv, validates the sealed profile receipt and CLI
help/version surface, clears the child environment, then supplies a closed
offline/concurrency-one environment. Provider invocation failures remain fatal
and are quarantined by the existing stage boundary.

Stage 03 consumes the additive view-set manifest, requires the CPU baseline,
derives all pairwise comparisons from the succeeded set, preserves optional
skip evidence, rejects unsafe assets/missing layouts/page gaps, and makes only
a `pass_for_review` claim. Stage 04 keeps the CPU triptych stable, adds ready
optional views as companions, and leaves every page packet open. Resume
revalidates the frozen provider/profile graph, every view receipt and current
artifact, recomputed normalized views/pairwise evidence, and every exact page
packet. A later GPU capability change cannot add a view to an existing run.

## Files changed

- `kb_creator/contracts/run_spec.v2.schema.json`
- `kb_creator/contracts/mineru_view_execution.v1.schema.json`
- `kb_creator/contracts/mineru_view_set.v1.schema.json`
- `kb_creator/contracts/mineru_multi_view_comparison.v2.schema.json`
- `kb_creator/pipeline/mineru_cpu_first.py`
- `kb_creator/pipeline/reconstruction.py`
- `kb_creator/__main__.py`
- `kb_creator/scripts/run_mineru_three_view.ps1`
- `kb_creator/scripts/compare_mineru_three_views.py`
- `kb_creator/scripts/build_mineru_visual_merge_bundle.py`
- `kb_creator/tests/test_mineru_cpu_packet_b.py`
- this receipt

No actual `.tools` content, dependency, model, immutable source, old sealed
skip run, canonical plan/context/status, promotion bridge, critic receipt,
`.codex/config.toml`, Git index, or Git history was changed. No install,
download, network, real PDF, Word, GPU, remote, API, commit, or handoff action
was run.

## Verification

- Synthetic six-page absent-GPU E2E: PASS. Three CPU views succeeded; two
  optional views produced sealed output-free skips; Stages 01-04 succeeded;
  first pass returned exit `10`; closed decisions resumed through Stages 05-06
  to a run-local candidate.
- Synthetic GPU-ready E2E: PASS. Five views succeeded, ten dynamic pairs were
  generated, and the mandatory CPU triptych remained first and unchanged.
- Adversarial coverage: PASS for unavailable required CPU, partial v2 dispatch,
  required-view skip, source/model/config/lock/tool drift, output mutation,
  provider change after sealing, and resealed Stage 03/04 semantic attacks.
- JSON Schema validation: PASS for generated RunSpec v2, view, view-set, and
  comparison receipts; all new schemas are closed at their authority boundary.
- Relevant regression suite: `187 passed, 1 skipped in 50.72s`, covering
  reconstruction control plane, legacy/new three-view tools, visual bundle,
  fidelity audit, materializer, promotion and adversarial promotion, identity,
  and Packet B tests.
- Python compile: PASS for the modified Python control-plane/scripts/tests.
- PowerShell parser: PASS for `run_mineru_three_view.ps1` on PowerShell 7.6.2.
- Scoped `git diff --check`: PASS; Git emitted only its Windows LF-to-CRLF
  advisory for the PowerShell wrapper.

## Residual risk and next action

The generic path has synthetic evidence only. It deliberately has no live
MinerU timing, memory, or layout-quality result. The next gate is independent
Packet B implementation criticism. Only after P0/P1 closure across Packets A,
B, and C may a bounded executor create a fresh current-station real-source run.
That future run must use `ocr_language: en`; the immutable historical global
skip run remains non-resumable and unpromotable.

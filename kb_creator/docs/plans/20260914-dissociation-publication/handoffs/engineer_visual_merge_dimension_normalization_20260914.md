# Engineer receipt: visual-merge dimension normalization

Date: 2026-09-14

## Assignment

- Goal: `20260914-dissociation-publication`.
- Packet: bounded implementation of `architect_visual_merge_dimension_normalization_20260914.md` after independent architecture GO in `critic_visual_merge_dimension_normalization_architecture_20260914.md`.
- Assigned/actual requested role: engineering, `gpt-5.6-sol` at `high` reasoning under the user-scoped override (repository-policy engineering default is `gpt-5.6-terra` / `medium`).
- Boundary observed: no real Dissociation/MinerU/PDF source run, `.tools` mutation, install/download, network, GPU, remote/API, immutable run-root mutation, canonical plan/context/status edit, Git commit, or publication action.

## Result

Implemented the accepted source-authoritative v2 geometry contract while retaining the legacy v1 dispatch.

- CPU-first Stage 01 now explicitly selects `source_displayed_mediabox_v1`. It rejects non-finite/non-positive geometry, mixed MediaBox sizes/rotations, non-right-angle rotation, and non-unit `UserUnit`; samples the full source MediaBox using the existing ceiling rule; embeds those unchanged samples on the exact source-displayed physical canvas; flattens rotation; sets CropBox equal to MediaBox; and reopens the result to prove exact canvas, one image, original sample dimensions, rotation zero, `UserUnit=1`, and no text layer.
- The historical preparer default remains `kb_creator.mineru_three_view_inputs.v1` with its prior pixel-grid physical canvas and output shape. The CPU-first adapter alone opts into the new v2 manifest.
- RunSpec v2 now seals the geometry policy, decimal tolerances, zero pixel tolerance, rounding rule, renderer recipe, and the added implementation schemas. Stage 04 receives the exact Stage 01 manifest identity as a direct stage input and as closed argv.
- CPU-first Stage 04 performs a full PDF metadata preflight before the first page render. The source-displayed Stage 01 record is the sole target authority; CropBox is diagnostic only. Original views may preserve or flatten a right-angle rotation, while the raster view must be flat. Three, four, and five succeeded views are supported in sealed order.
- Geometry uses `Decimal`, `0.001 pt` absolute dimension tolerance, `0.000005` relative aspect tolerance, and exact ceiling target pixels. The v2 path contains no crop, pad, resize, fit, stretch, thumbnail, scale-to, or one-pixel repair.
- Rendering remains a closed `pdftoppm` MediaBox argv. Each RGB PNG must match the exact target. The first three CPU views remain the stable triptych; optional succeeded views receive ordered labeled companion panels without changing their rendered pixels.
- Stage 04 emits sealed `kb_creator.mineru_geometry_plan.v1` and `kb_creator.mineru_visual_merge_bundle.v2` evidence with renderer, layout, page geometry, target/actual PNG, complete file topology, identities, and explicit false transform declarations.
- A geometry reject atomically emits only sealed `geometry-failure.json` before render (or after removal of an unpublished render staging tree for a pixel-mode/dimension reject). Its deterministic first mismatch and complete observed matrix are retained by the existing Stage 04 quarantine beside `stage-failure.json`; it is never rewritten as a skip.
- Validation/resume recomputes Stage 01 source geometry, raster-PDF topology, current succeeded-view/layout PDF graph, policy/tolerances/renderer identity, page targets, PNG identities/dimensions/mode, sealed plan/manifest, packet semantics, and exact output topology. Provider enrichment and stale v1 evidence therefore cannot enter a v2 resume.

## Changed files

- `kb_creator/scripts/prepare_mineru_three_view_inputs.py`
- `kb_creator/scripts/build_mineru_visual_merge_bundle.py`
- `kb_creator/pipeline/reconstruction.py`
- `kb_creator/pipeline/mineru_cpu_first.py`
- `kb_creator/contracts/run_spec.v2.schema.json`
- `kb_creator/contracts/mineru_three_view_inputs.v2.schema.json`
- `kb_creator/contracts/mineru_geometry_plan.v1.schema.json`
- `kb_creator/contracts/mineru_visual_merge_bundle.v2.schema.json`
- `kb_creator/contracts/mineru_geometry_failure.v1.schema.json`
- `kb_creator/tests/test_mineru_cpu_packet_b.py`
- `kb_creator/tests/test_mineru_geometry_normalization.py`
- this receipt

No MinerU source/model/profile/lock, source PDF, immutable run root, promotion bridge, audit/materializer behavior, Viral/Innsmouth fixture, canonical plan/context/status, or user configuration was changed.

## Verification

Synthetic-only checks:

- `test_mineru_geometry_normalization.py`: **28 passed**. Covers the exact `595 x 841 pt -> 1653 x 2337 samples -> 595 x 841 pt -> 910 x 1285 px` regression; Letter, landscape, fractional and non-zero-origin MediaBoxes; rotations 0/90/180/270; preserved original versus flattened raster rotation; CropBox lure; mixed/non-right-angle/non-unit/invalid geometry; decimal tolerance boundaries; exact 3/4/5 views; page-count matrix; one-pixel rejection; optional companions; failure seal/output absence; closed argv/static transform prohibition; v2 builder success and pre-render failure; and rejection of extra output files and rendered-byte tampering.
- `test_mineru_three_view_tools.py` + `test_mineru_visual_merge_bundle.py` + geometry suite: **55 passed** after the final legacy-dispatch changes.
- `test_mineru_cpu_packet_b.py`: **27 passed** after RunSpec/Stage01/Stage04 synthetic fixture migration, including geometry quarantine.
- Full relevant eight-module regression command over geometry, three-view, visual bundle, Packet B, reconstruction control plane, audit, materializer, and scenario reconstruction: **503 passed in 3410.45s**. That long process had already imported the modules before the final closed-input/topology test hardening; the affected current-code modules were therefore rerun independently afterward with the 28/55/27 green results above.
- Python compile: PASS for both geometry scripts, both control-plane modules, and the new geometry tests.
- JSON parse: PASS for all 28 current contract schemas; direct jsonschema validation passes for generated Stage01 v2, geometry-plan v1, visual-bundle v2, and geometry-failure v1 evidence.
- Scoped `git diff --check`: PASS. Static source scan found no scenario-name routing, URL/network path, crop/scale flags, or image-resize primitive in the v2 geometry path.

## Risk assessment

- P0: none known.
- P1: none known after synthetic integration, adversarial geometry, quarantine, semantic resume, and legacy regression checks.
- P2: the real host Poppler/MinerU output has intentionally not been exercised in this packet. Renderer version is captured twice during build and is resume-bound together with the exact executable SHA-256; live execution remains gated on independent closure.

## Next action

Independent critic closure against this receipt and diff. Do not resume immutable `20260914-cpu-first-03`; if closure is granted, the orchestrator may authorize a new absent run root and provide the exact live command.

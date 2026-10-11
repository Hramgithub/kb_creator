# Orchestrator decision — local MinerU execution policy

Date: 2026-09-14  
Owner: main orchestrator  
Authority: explicit user correction and acceptance

## Decision

MinerU remains the primary reconstruction tool. Lack of NVIDIA/CUDA does not
remove MinerU and does not skip the reconstruction run.

The mandatory current-station views are:

1. original immutable PDF through MinerU `pipeline --method txt`;
2. original immutable PDF through MinerU `pipeline --method ocr`;
3. rasterized derivative PDF through MinerU `pipeline --method ocr`.

MinerU `hybrid-engine` and `vlm-engine` are optional local enrichment. If their
required GPU capability is absent, only those provider invocations receive a
sealed successful `SKIPPED` result. Comparison, review queue, fidelity audit,
candidate materialization, promotion and acceptance continue from the mandatory
CPU views.

`auto` is an input-method selector between text extraction and OCR, not an
independent evidence view. Production reconstruction therefore records the
explicit `txt` and `ocr` choices rather than treating `auto` as a third method.

Remote execution, task handoff, another workstation, and an external MinerU
HTTP service are outside the authorized execution boundary.

## Required generic remediation

- split the current CUDA-only dependency lock into a pinned CPU baseline and an
  optional CUDA enrichment layer, both installed below repository `.tools`;
- make the capability receipt provider-scoped instead of run-global;
- extend the generic wrapper with `pipeline_txt` and CPU `pipeline_ocr` routes;
- preserve the existing three-view comparison/review/fidelity/promotion gates;
- replace tests that require all six stages to skip when CUDA is absent with
  tests that require CPU completion and only GPU-provider skip evidence;
- start a fresh run root after independent implementation review; never resume
  `20260914-no-cuda-skip-01`.

This decision changes execution policy only. It does not accept a reconstruction
candidate or authorize any later publication acceptance.

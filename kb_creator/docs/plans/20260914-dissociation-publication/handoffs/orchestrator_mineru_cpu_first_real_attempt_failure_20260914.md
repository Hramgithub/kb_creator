# Orchestrator receipt — first real CPU-first run attempt

- Goal: `20260914-dissociation-publication`
- Run id: `20260914-cpu-first-01`
- Run root: `kb_creator/working/dissociation/reconstruction/20260914-cpu-first-01`
- Execution boundary: current local Windows station only
- Source mutation: none
- Result: failed closed in Stage 02 before the first view was produced
- Resume/promote status: forbidden

## Immutable run evidence

- portable run identity:
  `991F284F04FE872F061B6C5B951F079ED81A9AEF63BED2694A13B69B05BE9EDA`
- `run.json`: `27969` bytes,
  SHA-256 `E0DA99CAB2BE6DC3F0E690CDC96BC19583079C25B2E809E8B672F82D2F723C8D`
- Stage 01 manifest: `5901` bytes,
  SHA-256 `53D5D28E183225CAEB72A0575938266C98F86ED69481BC23092D893FADA2A6BB`
- Stage 01 raster: `32689131` bytes,
  SHA-256 `EDE12A820242009DC98B1450B2AAB163F8A0489A4B4F74E6FCE980ACDCFBB548`
- Stage 01 page manifest: `3938` bytes,
  SHA-256 `9519C1415E92C4794E88597C2624676029EAF2EC6B8E7E6A63AEE97B8C3C0281`
- `failures/02-mineru-three-view` exists but contained no files at inspection.

Stage 01 succeeded and produced the deterministic six-page raster. Stage 02
returned PowerShell exit `1`; no comparison, review queue, candidate, acceptance
or publication artifact was created. This run is failure evidence and must not
be repaired in place or reused as a fresh run.

## Root cause reproduction

A separate one-page diagnostic invocation used the same cleared, allowlisted
CPU child environment and the immutable original PDF. It failed before creating
diagnostic output:

```text
modelscope.utils.file_utils -> pathlib.Path.home()
RuntimeError: Could not determine home directory.
```

The CPU-first wrapper removed the real user profile correctly but did not supply
a repository-local synthetic Windows home. The wrapper also discarded the
child stdout/stderr on failure, leaving the quarantined Stage 02 directory empty.
Both are reusable pipeline defects, not a Dissociation-specific source defect.

Post-failure process inspection found no process executing from
`.tools/MinerU`; no manual termination or deletion was required.

## Remediation boundary

Add a profile-runtime-contained synthetic home/appdata environment and durable,
bounded, sanitized child-failure evidence. Close focused tests and independent
review before creating a new run id. Do not mutate this failed run.

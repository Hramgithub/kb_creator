# Orchestrator handoff — Dissociation live environments

> **SUPERSEDED — DO NOT EXECUTE THE GPU-HOST PROCEDURE BELOW.** The user
> explicitly limited execution to the current station. The accepted policy is
> mandatory local MinerU CPU `pipeline/txt` and `pipeline/ocr`, with only local
> GPU-backed `hybrid`/`vlm` enrichment capability-skipped. This document is
> retained only as historical evidence of the earlier incorrect boundary.

Date: 2026-09-14  
Owner: main orchestrator  
Scope: live reconstruction and later Word publication environment only

## Immutable authority

- Scenario: `dissociation` / `Dissociation`.
- Source PDF: user-supplied `Dissociation.PDF`.
- Source bytes: `2159317`.
- Source SHA-256:
  `01855CD1AA2E3F90C31B572AA01D2643FC862935B892FD7D49A7530CAACD947B`.
- Reconstruction contract:
  `kb_creator/contracts/dissociation.reconstruction.json`.
- Contract SHA-256:
  `99B01F09AA9CFCE72AC407ADBFF21E54BC11A2FDA73A00FDB0FC763024FEAD4E`.
- The source and contract are read-only authorities. Stop on any identity drift.

## Current CPU-only host

The sealed run root
`kb_creator/working/dissociation/reconstruction/20260914-no-cuda-skip-01`
is capability evidence only. It contains `run.json` and `skip.json`, has portable
run identity
`72095696C9C0E304E3F8D8CED9B387C21272203592567ACAEF1D984AB63CF292`,
and must never be resumed or reused as a candidate.

The repository-local capability receipt is `.tools/MinerU/capability.json` with
`state: unavailable` and `reason_code: nvidia_device_not_detected`. Setup,
verification and reconstruction therefore return an explicit non-error
`SKIPPED` path and install no CUDA runtime. Interrupted CUDA packages and large
pip unpack payloads were removed from this host.

## Fresh NVIDIA/CUDA host procedure

Run from a reviewed checkout of the same repository state. Keep task-installed
runtime, model, cache, temporary and Poppler files below `<repo>/.tools`.
`powershell.exe` is an operating-system integration, not a task-installed tool.

```powershell
$repo = (& git rev-parse --show-toplevel).Trim()
$source = "<absolute path to the immutable Dissociation.PDF>"
$mineruTools = Join-Path $repo ".tools\MinerU"
$mineruPython = Join-Path $mineruTools ".venv\Scripts\python.exe"
$pdftoppm = Join-Path $repo ".tools\poppler\poppler-26.02.0\Library\bin\pdftoppm.exe"
$powershell = (Get-Command powershell.exe -ErrorAction Stop).Source
$runId = "dissociation-<UTC timestamp>-gpu-01"
$runRoot = Join-Path $repo "kb_creator\working\dissociation\reconstruction\$runId"

& (Join-Path $repo "MinerU\scripts\probe-capability.ps1") -ToolRoot $mineruTools
& (Join-Path $repo "MinerU\scripts\setup.ps1") -ToolRoot $mineruTools
& (Join-Path $repo "MinerU\scripts\verify.ps1") -ToolRoot $mineruTools -FullModelHash

& $mineruPython -m kb_creator run `
  --contract (Join-Path $repo "kb_creator\contracts\dissociation.reconstruction.json") `
  --source $source `
  --run-root $runRoot `
  --run-id $runId `
  --mineru-root $mineruTools `
  --pdftoppm $pdftoppm `
  --powershell $powershell `
  --python $mineruPython `
  --json
```

Required observations before the run:

- the capability receipt says `state: available`;
- setup and full verification succeed without `SKIPPED`;
- `nvidia-smi`, Torch CUDA and pinned dependency/model checks pass;
- `$runRoot` does not exist before invocation;
- the source byte count and SHA-256 still match the immutable authority.

A successful extraction intentionally returns `state: needs_review` and process
exit code `10`. That is a review boundary, not a failure. Review
`review/review_queue.json`, complete a copy of
`review/decision_set.template.json` under a controlled decisions root, and only
then resume on the same host:

```powershell
$decisionsRoot = "<absolute controlled decisions directory>"
$decisions = Join-Path $decisionsRoot "decision_set.json"

& $mineruPython -m kb_creator resume `
  --run-root $runRoot `
  --decisions $decisions `
  --decisions-root $decisionsRoot `
  --json
```

Resume success creates a candidate ready for reconstruction QA. It does not
accept `RECONSTRUCTED_EN`. Return the run, decisions, fidelity evidence and
candidate to the main orchestrator for independent QA and explicit user
acceptance before publication Stage 10.

## Later Word publication boundary

The installed Word executable on the current station is
`C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE`, but COM
activation from the current Codex logon fails with `0x80070520`. This is an
environment limitation, not successful DOCX/PDF evidence.

Stages 50 and 60 must therefore run in an interactive Windows logon where Word
COM activation succeeds. Stage 50 may retain only DOCX plus complete PNG/JSON
render QA; any private render bridge is deleted before stage success. Stage 60
must freshly export the exact accepted DOCX through Word COM and render every
final PDF page with repository-local `.tools` Poppler. LibreOffice, Chromium,
and direct HTML-to-PDF fallbacks are forbidden.

## Stop conditions

- Never resume the sealed no-CUDA run.
- Never treat `SKIPPED`, `needs_review`, a candidate or passing tests as user
  acceptance.
- Never start publication Stage 10 before accepted reconstruction evidence.
- Never start HTML before accepted MASTER_RU plus accepted ArtView/configs.
- Never start DOCX before accepted HTML.
- Never create the retained PDF from anything except the exact accepted DOCX.
- Never claim release before the frozen package receives the independent
  `gpt-5.5` release review.

# GPT-5.5 independent critic receipt — Viral Step 6A MinerU bridge

- Goal id: `20260830-kb-creator-next-scenario`
- Step id: `6-source-reconstruction-step6a-runtime-bridge-review`
- Review kind: `process` with architecture-boundary checks
- Role: fresh independent critic
- Policy model / effort: `gpt-5.5` / `medium`
- Actual platform model / effort: `unavailable` (not exposed to this task)
- Orchestrator policy owner: main chat `gpt-5.6-sol` / `medium`
- Assignment state: `matched` by `nri-independent-critic`; platform runtime unverified
- Scoped override: `none`
- Independence declaration: I did not implement, remediate, or materially design the Step 6A MinerU bridge amendment or the candidate under review.
- Timestamp: `2026-08-31T01:20:16.5887361+03:00` (`Europe/Moscow`)
- Elapsed time: unavailable as an exact platform value
- Token use: unavailable to this contributor; no precision invented
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`
- Required HEAD: `54607bd3b9362adbb0c4bca64e8751482797f380`
- Observed HEAD: `54607bd3b9362adbb0c4bca64e8751482797f380`
- Result: `rejected_pending_narrow_amendment`

## Scope

Reviewed only the Step 6A MinerU runtime bridge amendment as a process /
architecture-boundary change. I did not review a reconstruction candidate,
`MASTER_EN`, translation, HTML/PDF, production packaging, or release readiness.
The known repository-wide 15 missing-`kb_creator.pdf_raw` collection errors
remain outside this bridge review except as a declared baseline.

## Candidate identity verified

| Input | Expected SHA-256 | Observed SHA-256 | Result |
|---|---|---|---|
| `handoffs/terra_engineering_viral_source_reconstruction_packet_20260831.md` | `011CF87FFA0B0DACC85559DEF601A5FD9EED0755F86EB877C263CF2F2D8FABBC` | `011CF87FFA0B0DACC85559DEF601A5FD9EED0755F86EB877C263CF2F2D8FABBC` | match |
| `handoffs/luna_executor_viral_source_reconstruction_20260831.md` | `31A50C84CF8EDC3F90EE1DED5643C019AEA47C00C0C0F31D466E13AD18E79B44` | `31A50C84CF8EDC3F90EE1DED5643C019AEA47C00C0C0F31D466E13AD18E79B44` | match |
| `handoffs/terra_engineering_viral_step6a_mineru_bridge_20260831.md` | `B41041A90791A5FD2888ECEC0470592F4D87C55BA2A616B3D45FB1584D86A603` | `B41041A90791A5FD2888ECEC0470592F4D87C55BA2A616B3D45FB1584D86A603` | match |

## Files checked

- `D:\NRI\AGENTS.md`
- `D:\NRI\.worktrees\kb-creator-viral\docs\governance\nri_goal_governance.md`
- `D:\NRI\.worktrees\kb-creator-viral\kb_creator\docs\plans\20260830-kb-creator-next-scenario\plan.md`
- `D:\NRI\.worktrees\kb-creator-viral\kb_creator\docs\plans\20260830-kb-creator-next-scenario\context.md`
- `D:\NRI\.worktrees\kb-creator-viral\kb_creator\docs\plans\20260830-kb-creator-next-scenario\handoffs\terra_engineering_viral_source_reconstruction_packet_20260831.md`
- `D:\NRI\.worktrees\kb-creator-viral\kb_creator\docs\plans\20260830-kb-creator-next-scenario\handoffs\luna_executor_viral_source_reconstruction_20260831.md`
- `D:\NRI\.worktrees\kb-creator-viral\kb_creator\docs\plans\20260830-kb-creator-next-scenario\handoffs\terra_engineering_viral_step6a_mineru_bridge_20260831.md`
- `D:\NRI\MinerU\scripts\verify.ps1`
- `D:\NRI\MinerU\scripts\run-hybrid.ps1`
- `D:\NRI\MinerU\scripts\initialize.ps1`
- `D:\NRI\.worktrees\kb-creator-viral\MinerU\scripts\verify.ps1`
- `D:\NRI\.worktrees\kb-creator-viral\MinerU\scripts\run-hybrid.ps1`
- `D:\NRI\.worktrees\kb-creator-viral\MinerU\scripts\initialize.ps1`
- `D:\NRI\MinerU\models\manifest.json`
- `D:\NRI\MinerU\config\mineru.template.json`
- `D:\NRI\MinerU\.runtime\mineru.json`
- `D:\NRI\MinerU\.venv\Scripts\mineru.exe`
- `D:\NRI\MinerU\.venv\Scripts\python.exe`

## Files changed

Only this immutable receipt:

`kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_step6a_mineru_bridge_review_20260831.md`

No implementation, source, runtime, contract, test, accepted/production,
canonical plan/context/status/release, staging, commit, push, or remote mutation
was performed.

## Verification performed

- Verified worktree HEAD exactly
  `54607bd3b9362adbb0c4bca64e8751482797f380`.
- Verified the original Step 6 packet, blocked receipt, and bridge amendment
  hashes exactly as listed above.
- Re-read governance and canonical plan/context. The plan/context make Step 6A
  a bounded candidate/evidence task only, with internal agents reserved for
  independent criticism.
- Re-read the original Step 6 packet. It requires a closed three-code/test-file
  implementation allowlist plus the run root
  `kb_creator/working/viral/source_reconstruction/20260831_step6a/**`, refuses
  accepted/production/contract publication, and requires runtime verification
  before source observation and `ScenarioContract.resolve_source_path()`.
- Re-read the blocked executor receipt. It stopped before source observation
  because worktree-local `MinerU\.venv` was absent; the receipt correctly did
  not claim a reconstruction candidate.
- Independently checked that the Step 6A implementation files
  `scenario_source_reconstruction.py`, `reconstruct_scenario_source.py`, and
  `test_scenario_source_reconstruction.py` do not yet exist, and that the
  Step 6A run root is absent.
- Independently checked raw hashes and normalized text identity for main and
  worktree `verify.ps1`, `run-hybrid.ps1`, and `initialize.ps1`.
- Independently inspected the main script mutation surfaces:
  `verify.ps1` invokes `initialize.ps1`; `run-hybrid.ps1` invokes
  `initialize.ps1`, creates `$runtime\tmp` and `$runtime\hf`, and sets
  `MINERU_TOOLS_CONFIG_JSON`; `initialize.ps1` creates `.runtime\models\vlm`,
  can assemble `model.safetensors`, copies VLM mirror files, and rewrites
  `.runtime\mineru.json`.
- Independently verified `D:\NRI\MinerU\models\manifest.json` hash, 55 manifest
  rows, `0` missing files, `0` size mismatches, and `0` hash mismatches.
- Independently verified the runtime VLM mirror as 14 files total: 13 expected
  non-part manifest files plus assembled `model.safetensors`, with `0` missing,
  `0` extra, and `0` mismatched mirror files.
- Independently verified pinned identities:
  - `D:\NRI\MinerU\models\manifest.json`:
    `6DB91244B9FD72F7604BDDFFA75EB29AD870E24A611BA59B225C9C35FE5B6768`
  - `D:\NRI\MinerU\config\mineru.template.json`:
    `935CFEDBB81E0359CA7E50A24BFA069D73A9876FFF136847FF6F815EF83D9650`
  - `D:\NRI\MinerU\.runtime\mineru.json`:
    `E288DBCA304EDE7825FDD67C1AAFBE9509F2005FC470B0C9D51D40FA6C6FB11C`
  - `D:\NRI\MinerU\.venv\Scripts\mineru.exe`:
    `D9D6964BC2E00835C7F62026C3608692F8471E81C76A5F242A5BFB8EE1F3DCEB`
  - `D:\NRI\MinerU\.venv\Scripts\python.exe`:
    `79346CEE67890CC40143CE78D8CB5A7F8956AE600C3AEA44D801682F1CC86801`
  - assembled VLM `.runtime/models/vlm/model.safetensors`:
    `2312126640` bytes,
    `abf8681ca63b8dec7b67de257af47b821f179442f72998d0696ae2ed9232a5f0`
- Confirmed the exact main bridge surface is Git-clean:
  `MinerU/scripts/verify.ps1`, `MinerU/scripts/run-hybrid.ps1`,
  `MinerU/scripts/initialize.ps1`, `MinerU/models/manifest.json`, and
  `MinerU/config/mineru.template.json` have no status output. Broader main
  `MinerU` dirt exists and remains diagnostic only.

## Architecture/process assessment

The bridge is directionally correct on the major safety boundary: invoking the
main `verify.ps1` or `run-hybrid.ps1` would mutate main `.runtime`, so the
amendment properly forbids those scripts and moves toward a direct pinned
`mineru.exe` invocation. The script evidence supports that conclusion.

The admission order is also correctly specified at the process level:
the amendment requires runtime verification first, then independent PDF
observation, then `ScenarioContract.resolve_source_path()`, and only then
`pdfinfo`, MinerU extraction, rendering, text extraction, asset extraction, or
OCR. This preserves the original Step 6 source admission boundary.

The direct command construction is acceptably non-executable from contract data
if the executor implements it as argv/literal-path construction inside the
approved generic seam. The amendment does not add a new wrapper, script import,
custom DAG, legacy `build_viral_*`/`freeze_viral_*` family, or legacy
`translator/config/viral.package.json` authority.

However, the amendment does not yet close the whole hidden-write/network/cache
surface it claims to close. The configured MinerU runtime declares
`"model-source": "modelscope"` in `D:\NRI\MinerU\.runtime\mineru.json`, while
the proposed bridge redirects Hugging Face, temp, Torch, TorchInductor, Triton,
CUDA, XDG, and Matplotlib paths only. It does not redirect or fail-closed-audit
ModelScope and Paddle/PaddleOCR-style cache roots that may use user-profile or
local-app-data defaults before the run-root inventory can see them.

## Findings

### P1 — ModelScope/Paddle/user-profile cache surface is not closed

Evidence:

- Amendment `terra_engineering_viral_step6a_mineru_bridge_20260831.md:93`
  identifies the main runtime/config/model identities.
- Amendment lines `229-272` define the exact bridge command and environment.
  The environment redirects `HF_HOME`, `HUGGINGFACE_HUB_CACHE`,
  `HF_XET_CACHE`, `TEMP`, `TMP`, `TORCH_HOME`,
  `TORCHINDUCTOR_CACHE_DIR`, `TRITON_CACHE_DIR`, `CUDA_CACHE_PATH`,
  `XDG_CACHE_HOME`, `MPLCONFIGDIR`, and sets `PYTHONDONTWRITEBYTECODE`.
- Independently inspected `D:\NRI\MinerU\.runtime\mineru.json` declares
  `"model-source": "modelscope"` and model directories under the main
  `D:\NRI\MinerU` tree.
- The amendment stop condition at lines `319-348` rejects attempted network
  access or writes outside the run root, but the mutation audit at lines
  `350-380` explicitly audits the Viral worktree and `D:\NRI\MinerU`; it does
  not define an executor-checkable pre/post audit for user-profile cache roots
  that ModelScope, Paddle, PaddleOCR, or Python dependency code may choose by
  default.

Why this matters:

The bridge's safety claim is that every volatile/cache/output write is under
the original Step 6A run root and that attempted network/model-cache mutation is
fail-closed. With `model-source: modelscope` and no ModelScope/Paddle/PaddleOCR
cache redirection or user-profile audit, the executor can satisfy the written
environment map while still allowing hidden writes under user profile or local
app data. That violates the task boundary and makes the "all cache/temp/output
env redirected" claim unproven.

Required remediation:

Before retry authorization, amend the bridge with a closed, executor-testable
hidden-write control for the installed MinerU dependency stack. At minimum it
must do one of the following:

1. redirect all relevant ModelScope, Paddle/PaddleOCR, Python bytecode/cache,
   and dependency cache roots into `$volatileRoot` using exact environment
   variable names and run-root-relative inventory requirements; or
2. document verified evidence that the installed MinerU path cannot use those
   cache roots for this command, and add a pre/post audit that proves no writes
   occur outside the allowlisted run root and main read-only identity set.

The remediation must include explicit stop conditions for any user-profile,
`%APPDATA%`, `%LOCALAPPDATA%`, ModelScope, Paddle/PaddleOCR, Python cache, or
network/download write touched during runtime verification or extraction. The
retry remains blocked until this is captured in an accepted amendment or
equivalent orchestrator-resolved packet update.

### P2 — Run-root schema wording needs an explicit cache-evidence exception

Evidence:

- Original Step 6 packet lines `80-116` allow
  `engine/mineru_hybrid_high/**` but also state that temporary caches and model
  payloads are forbidden inside the run root.
- Amendment lines `229-272` create `_bridge_runtime` under
  `engine/mineru_hybrid_high` and classify volatile/cache artifacts as
  evidence-bearing working artifacts to be inventoried.

Why this matters:

The glob technically permits `_bridge_runtime`, but the original prose still
forbids temporary caches inside the run root. That creates an avoidable
interpretation conflict for the executor and later QA.

Required remediation:

When fixing the P1 cache boundary, explicitly state that
`engine/mineru_hybrid_high/_bridge_runtime/**` is the sole allowed exception to
the original temporary-cache prohibition, only for redirected bridge runtime
artifacts, and that every retained file there must be inventoried by
run-root-relative path, byte count, SHA-256, and purpose. Model downloads,
Python bytecode, pytest caches, browser profiles, raw unrelated logs, and any
file outside the closed run-root schema remain forbidden.

## Non-findings / accepted controls

- No P0 findings.
- The missing worktree-local `MinerU\.venv` is a real dependency blocker in the
  original executor receipt and is not treated as an implementation defect.
- The main `verify.ps1` and `run-hybrid.ps1` are correctly rejected for retry
  use because they invoke `initialize.ps1` and mutate main `.runtime`.
- Main/worktree script line-ending differences are not a semantic mismatch:
  strict UTF-8 plus CRLF/CR normalization produced identical normalized text
  and normalized SHA-256 for all three script pairs.
- The main bridge surface cleanliness gate is adequate for the named files; the
  broader dirty `MinerU/README.md` and untracked benchmark/FAQ/archive files are
  diagnostic only unless they become runtime inputs.
- The source admission order preserves the fixed Viral runtime graph for this
  slice: runtime verification precedes PDF observation; PDF observation
  precedes `ScenarioContract.resolve_source_path()`; extraction follows only
  after source admission.
- The shadow/legacy translation boundary remains intact: the amendment does
  not introduce `translator/config/viral.package.json` as runtime authority and
  does not copy a `build_viral_*` or `freeze_viral_*` family.
- The amendment does not accept reconstruction, pages 1-5 modes,
  `reconstruction_ready`, `MASTER_EN`, or publication.
- The full-suite 15 missing-`kb_creator.pdf_raw` collection errors remain a
  separate baseline and are not a Step 6A bridge blocker.

## Recommendation

`reject`

Retry is not authorized yet. The amendment needs the P1 hidden-write/cache
closure above. After the orchestrator resolves that P1 in a narrow amended
packet or amendment receipt, a fresh independent critic check can be limited to
that delta. Material Step 6A correction/retry may begin only when no P0/P1
remains.

## Blockers and next action

Blocker: open P1 hidden-write/cache/network-control gap for ModelScope/Paddle/
PaddleOCR/user-profile cache surfaces.

Next action: orchestrator requests a narrow engineering amendment that closes
the hidden-write surface and reconciles the `_bridge_runtime` run-root schema
exception. Do not dispatch the Step 6A reconstruction retry until that amended
control receives independent acceptance with no open P0/P1.

## Detached receipt SHA-256

Compute after final write.

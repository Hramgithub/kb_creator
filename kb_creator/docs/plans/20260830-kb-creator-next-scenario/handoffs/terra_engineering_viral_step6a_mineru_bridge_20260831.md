# Terra engineering amendment — Viral Step 6A MinerU runtime bridge

- Goal id: `20260830-kb-creator-next-scenario`
- Step id: `6-source-reconstruction-step6a-runtime-bridge`
- Role: engineering assistance
- Policy model / effort: `gpt-5.6-terra` / `medium`
- Actual platform model / effort: `unavailable` (not exposed to this task)
- Orchestrator policy owner: main chat `gpt-5.6-sol` / `medium`
- Assignment state: `platform-unverified`; policy role honored
- Scoped override: `none`
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`
- Branch / required HEAD: `codex/kb-creator-viral` / `54607bd3b9362adbb0c4bca64e8751482797f380`
- Superseded boundary: only the MinerU invocation/preflight portion of
  `terra_engineering_viral_source_reconstruction_packet_20260831.md`, SHA-256
  `011CF87FFA0B0DACC85559DEF601A5FD9EED0755F86EB877C263CF2F2D8FABBC`
- Blocked evidence amended:
  `luna_executor_viral_source_reconstruction_20260831.md`, SHA-256
  `31A50C84CF8EDC3F90EE1DED5643C019AEA47C00C0C0F31D466E13AD18E79B44`
- Timestamp: `2026-08-31` (`Europe/Moscow`)
- Result: `amendment_ready_pending_independent_review`

## Decision and exact scope

The missing worktree-local `MinerU\.venv` is not to be repaired. The already
installed `D:\NRI\MinerU` environment may serve as a read-only external
toolchain for the same Step 6A candidate. This removes the original
`dependency_verification` design blocker without authorizing setup, install,
upgrade, download, copy, symlink, junction, source-PDF copy, worktree MinerU
edit, script import, or a fourth implementation/test path.

The original Step 6A write allowlist remains closed to the same three reusable
paths and the same run root:

1. `kb_creator/scripts/scenario_source_reconstruction.py`;
2. `kb_creator/scripts/reconstruct_scenario_source.py`;
3. `kb_creator/tests/test_scenario_source_reconstruction.py`;
4. `kb_creator/working/viral/source_reconstruction/20260831_step6a/**`.

The retry receipt is a governance artifact, not a fourth implementation path:

`kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/luna_executor_viral_source_reconstruction_step6a_retry_20260831.md`

The original blocked receipt is immutable and must not be rewritten. All other
packet restrictions remain binding, including no contract, accepted,
production, `MASTER_EN`, Innsmouth, plan/context/status, staging, commit, push,
or remote mutation.

## CRLF/LF identity decision and script invocation boundary

The main and worktree copies of `verify.ps1` and `run-hybrid.ps1` are acceptable
as the same pinned **semantic specification**. Their raw SHA-256 values differ
only because the worktree copies use CRLF and the main copies use LF. Strict
UTF-8 decode followed by `CRLF -> LF` and lone `CR -> LF` normalization produces
byte-identical normalized text, equal character counts, equal normalized
SHA-256 values, and no semantic Git diff.

That conclusion does **not** authorize invoking either main script during the
retry. The reason is independent of line endings: both scripts call
`D:\NRI\MinerU\scripts\initialize.ps1`. `initialize.ps1` creates runtime
directories, can assemble/copy model files, and always rewrites
`D:\NRI\MinerU\.runtime\mineru.json`; `run-hybrid.ps1` additionally creates and
uses `D:\NRI\MinerU\.runtime\tmp` and `.runtime\hf`. Direct script invocation
would therefore violate the required read-only main-runtime boundary and the
rule that all Step 6A volatile/output writes stay below the original run root.

The bridge instead invokes the already installed
`D:\NRI\MinerU\.venv\Scripts\mineru.exe` directly with the exact pinned
`run-hybrid.ps1` profile and environment semantics. It reads the existing
verified main config/models but redirects every declared cache, temporary, and
engine path into `engine/mineru_hybrid_high/**` under the allowlisted run root.
This is an execution command inside the accepted three-file seam, not an added
implementation path and not a script import.

## Independently reproduced identities

### Script identities

Normalization is strict UTF-8, no BOM insertion, `CRLF -> LF`, then lone
`CR -> LF`; the normalized SHA-256 is over UTF-8 without BOM.

| Script | Copy | Raw bytes | Raw SHA-256 | Normalized chars | Normalized SHA-256 |
|---|---|---:|---|---:|---|
| `verify.ps1` | worktree | 2716 | `1AA3DA2DDD0C1B7BC3425827EC9696F3FC6F2484FE8A08840F5113DC76563BDF` | 2635 | `3ABA78D2888F1EC77AAA50AAA50F1266F000E58E41B4EB82DB3DEF40A701EEDB` |
| `verify.ps1` | main | 2635 | `3ABA78D2888F1EC77AAA50AAA50F1266F000E58E41B4EB82DB3DEF40A701EEDB` | 2635 | `3ABA78D2888F1EC77AAA50AAA50F1266F000E58E41B4EB82DB3DEF40A701EEDB` |
| `run-hybrid.ps1` | worktree | 2718 | `A1D07F0A063AC42B5D635E13BDF263C06CDA72FCC9FBA5700EC7ABBD7A16196E` | 2632 | `643DAD0EF878220438BEDB0E74489A1834E115EC4A11B7B58496D80CD2B1851E` |
| `run-hybrid.ps1` | main | 2632 | `643DAD0EF878220438BEDB0E74489A1834E115EC4A11B7B58496D80CD2B1851E` | 2632 | `643DAD0EF878220438BEDB0E74489A1834E115EC4A11B7B58496D80CD2B1851E` |
| `initialize.ps1` | worktree | 3032 | `815A22AA51824D8F00EEBEE2EA964BD72F6542D8AE2D3AFA9D1602673939B19C` | 2946 | `316A3CB5823EDAD09AD912C7A83FE70136A3C1CD0CA013E0AC88F58EA6762092` |
| `initialize.ps1` | main | 2946 | `316A3CB5823EDAD09AD912C7A83FE70136A3C1CD0CA013E0AC88F58EA6762092` | 2946 | `316A3CB5823EDAD09AD912C7A83FE70136A3C1CD0CA013E0AC88F58EA6762092` |

Any raw or normalized mismatch is a stop. Normalization is an identity check
only; it never rewrites either checkout.

### Main runtime and model identities

- `D:\NRI\MinerU\models\manifest.json`: `11548` bytes, raw SHA-256
  `6DB91244B9FD72F7604BDDFFA75EB29AD870E24A611BA59B225C9C35FE5B6768`,
  exactly `55` `files` rows;
- read-only full verification of all 55 manifest rows: `0` missing, `0` size
  mismatches, `0` SHA-256 mismatches;
- assembled VLM declared by the manifest: `.runtime/models/vlm/model.safetensors`,
  `2312126640` bytes, SHA-256
  `ABF8681CA63B8DEC7B67DE257AF47B821F179442F72998D0696AE2ED9232A5F0`;
- runtime VLM mirror: 13 non-part model-store files plus the assembled model,
  14 runtime files total, with `0` missing, extra, or hash-mismatched mirror
  files;
- read-only runtime config `D:\NRI\MinerU\.runtime\mineru.json`: `546` bytes,
  SHA-256
  `E288DBCA304EDE7825FDD67C1AAFBE9509F2005FC470B0C9D51D40FA6C6FB11C`;
- config template: `506` bytes, SHA-256
  `935CFEDBB81E0359CA7E50A24BFA069D73A9876FFF136847FF6F815EF83D9650`;
- launcher `D:\NRI\MinerU\.venv\Scripts\mineru.exe`: `108390` bytes,
  SHA-256
  `D9D6964BC2E00835C7F62026C3608692F8471E81C76A5F242A5BFB8EE1F3DCEB`;
- runtime Python `D:\NRI\MinerU\.venv\Scripts\python.exe`: `45568` bytes,
  SHA-256
  `79346CEE67890CC40143CE78D8CB5A7F8956AE600C3AEA44D801682F1CC86801`;
- runtime probe: MinerU `3.4.4`, Python environment with Torch
  `2.8.0+cu128`, Torch CUDA `12.8`, CUDA available, GPU
  `NVIDIA GeForce RTX 5080`, lmdeploy `0.11.1`, transformers `4.57.6`, and
  torch-c-dlpack-ext `0.1.5`.

The worktree-local command was independently replayed and remains the expected
fail-closed result:

```powershell
& .\MinerU\scripts\verify.ps1 -FullModelHash
```

Exit `1`: `MinerU environment is missing. Run scripts\setup.ps1.` It stops
before `initialize.ps1`, so this observation made no runtime write.

### Main Git/status boundary

At amendment time the main checkout was `D:\NRI`, branch `main`, HEAD
`bc77068bdc75e63af1a3746d846be6d64c1bf197`, `ahead 1, behind 5`. Its broader
`MinerU` subtree was intentionally not clean: `MinerU/README.md` was modified
and benchmark/FAQ/archive files were untracked. None is part of this bridge.

The exact bridge source surface below was tracked and clean relative to that
HEAD:

```text
MinerU/scripts/verify.ps1
MinerU/scripts/run-hybrid.ps1
MinerU/scripts/initialize.ps1
MinerU/models/manifest.json
MinerU/config/mineru.template.json
```

The main branch name, HEAD, ahead/behind state, `README.md`, and unrelated
untracked evidence are diagnostic, not acceptance identities. A changed main
HEAD does not by itself reject a retry if every pinned raw/normalized/runtime
identity and the exact bridge-surface cleanliness gate still match. Any dirty
bridge-surface path, unexpected file identity, runtime version drift, model
mismatch, or new path under the read-only main runtime is a stop.

## Exact fail-closed preflight

Run from `D:\NRI\.worktrees\kb-creator-viral`. The executor may implement the
three-file seam only after the worktree/Git and runtime checks pass. It may not
open the Viral PDF until the entire runtime verification below has passed.

### 1. Worktree and packet boundary

```powershell
git rev-parse --show-toplevel
git branch --show-current
git rev-parse HEAD
git status --short --branch -uall
git diff --check
git diff --name-only
git ls-files --others --exclude-standard
Test-Path -LiteralPath MinerU\.venv
Test-Path -LiteralPath kb_creator\working\viral\source_reconstruction\20260831_step6a
Get-FileHash kb_creator\docs\plans\20260830-kb-creator-next-scenario\handoffs\terra_engineering_viral_source_reconstruction_packet_20260831.md -Algorithm SHA256
Get-FileHash kb_creator\docs\plans\20260830-kb-creator-next-scenario\handoffs\luna_executor_viral_source_reconstruction_20260831.md -Algorithm SHA256
```

Require the exact branch/HEAD and packet/blocked-receipt hashes above,
worktree-local `.venv` absent, and the run root absent. Preserve every
pre-existing status line; do not clean, reset, stage, or repair it.

### 2. Read-only main toolchain identity and full verification

Do not call `verify.ps1` or `initialize.ps1`. The retry must perform their
verification logic read-only: verify the raw and normalized script table,
require the exact bridge surface to be Git-clean, require the manifest raw hash
and count, hash all 55 manifest files, hash and compare the 14-file runtime VLM
mirror including the assembled model, require the config/launcher/Python hashes,
and then run this version/GPU probe:

```powershell
& D:\NRI\MinerU\.venv\Scripts\python.exe -B -c "import importlib.metadata,json,torch; print(json.dumps({'cuda_available':torch.cuda.is_available(),'cuda_device':torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,'torch':torch.__version__,'torch_cuda':torch.version.cuda,'lmdeploy':importlib.metadata.version('lmdeploy'),'mineru':importlib.metadata.version('mineru'),'transformers':importlib.metadata.version('transformers'),'torch_c_dlpack_ext':importlib.metadata.version('torch-c-dlpack-ext')},ensure_ascii=False))"
```

All values must exactly match the identity section. The executor records the
PowerShell commands and their complete structured results in memory until the
run root is admitted; once admitted, it serializes them into
`evidence/COMMANDS.json`. No check may repair, assemble, copy, initialize,
download, or normalize a file.

### 3. Source admission order

Only after Step 2 is fully green:

1. run the trusted code-owned independent PDF observer using `pypdf` or `fitz`;
2. require a regular, unencrypted 124-page PDF with every media box exactly
   `612 x 792` pt and rotation `0`;
3. pass those **observed** values to
   `ScenarioContract.resolve_source_path()` and require its independent byte
   count `20718150` and SHA-256
   `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05`;
4. only after `resolve_source_path()` succeeds, run `pdfinfo` as a diagnostic
   and then permit MinerU extraction, rendering, text extraction, asset
   extraction, or OCR.

Supplying contract constants as observer results, opening the PDF before the
runtime gate, or treating `pdfinfo` as authority is forbidden. The generic
preflight command remains:

```powershell
python -B kb_creator/scripts/reconstruct_scenario_source.py preflight --contract kb_creator/contracts/viral.json --source "D:\яндекс\Yandex.Disk\НРИ\1_Зов Ктулху\english\7th Edition Call of Cthulhu\Adventures\Call_of_Cthulhu_Viral.pdf" --run-root kb_creator/working/viral/source_reconstruction/20260831_step6a
```

Its evidence must prove the order `runtime_verified -> pdf_observed ->
resolve_source_path_passed`; extraction refuses to start if any state is
missing or reordered.

## Exact bridge extraction command

After successful source admission, create only directories below the admitted
run root and invoke the pinned executable directly. The CLI/generic library may
construct this command, but no wrapper/module/script file may be added.

```powershell
$sourcePath = 'D:\яндекс\Yandex.Disk\НРИ\1_Зов Ктулху\english\7th Edition Call of Cthulhu\Adventures\Call_of_Cthulhu_Viral.pdf'
$runRoot = (Resolve-Path -LiteralPath 'kb_creator\working\viral\source_reconstruction\20260831_step6a').Path
$engineRoot = Join-Path $runRoot 'engine\mineru_hybrid_high'
$volatileRoot = Join-Path $engineRoot '_bridge_runtime'
New-Item -ItemType Directory -Force -Path $engineRoot, (Join-Path $volatileRoot 'tmp'), (Join-Path $volatileRoot 'hf'), (Join-Path $volatileRoot 'torch'), (Join-Path $volatileRoot 'torchinductor'), (Join-Path $volatileRoot 'triton'), (Join-Path $volatileRoot 'cuda'), (Join-Path $volatileRoot 'xdg'), (Join-Path $volatileRoot 'mpl') | Out-Null

foreach ($name in @('HTTP_PROXY','HTTPS_PROXY','ALL_PROXY','GIT_HTTP_PROXY','GIT_HTTPS_PROXY','http_proxy','https_proxy','all_proxy')) {
  if (Test-Path "Env:$name") { Remove-Item "Env:$name" }
}
$env:NO_PROXY = '*'
$env:no_proxy = '*'
$env:HF_HOME = Join-Path $volatileRoot 'hf'
$env:HUGGINGFACE_HUB_CACHE = Join-Path $volatileRoot 'hf\hub'
$env:HF_XET_CACHE = Join-Path $volatileRoot 'hf\xet'
$env:HF_HUB_DISABLE_SYMLINKS_WARNING = '1'
$env:HF_HUB_OFFLINE = '1'
$env:TRANSFORMERS_OFFLINE = '1'
$env:TEMP = Join-Path $volatileRoot 'tmp'
$env:TMP = $env:TEMP
$env:TORCH_HOME = Join-Path $volatileRoot 'torch'
$env:TORCHINDUCTOR_CACHE_DIR = Join-Path $volatileRoot 'torchinductor'
$env:TRITON_CACHE_DIR = Join-Path $volatileRoot 'triton'
$env:CUDA_CACHE_PATH = Join-Path $volatileRoot 'cuda'
$env:XDG_CACHE_HOME = Join-Path $volatileRoot 'xdg'
$env:MPLCONFIGDIR = Join-Path $volatileRoot 'mpl'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:MINERU_TOOLS_CONFIG_JSON = 'D:\NRI\MinerU\.runtime\mineru.json'
$env:MINERU_LMDEPLOY_BACKEND = 'pytorch'
$env:TORCHINDUCTOR_USE_STATIC_CUDA_LAUNCHER = '0'
if (Test-Path 'Env:TORCH_COMPILE_DISABLE') { Remove-Item 'Env:TORCH_COMPILE_DISABLE' }

& 'D:\NRI\MinerU\.venv\Scripts\mineru.exe' --path $sourcePath --output $engineRoot --backend hybrid-engine --effort high --formula True --table True
if ($LASTEXITCODE -ne 0) { throw "MinerU failed with exit code $LASTEXITCODE" }
```

The retry may not add `--start`/`--end`; the full 124-page source is required.
Any attempted network access, model/cache write outside `$volatileRoot`, source
rewrite, or output outside `$engineRoot` is a stop. All `_bridge_runtime`
artifacts are evidence-bearing working artifacts: inventory every retained file
by run-root-relative path, bytes, and SHA-256; reject raw tool logs, Python
bytecode, pytest caches, browser profiles, and files outside the packet's closed
run-root schema.

Then run the unchanged packet commands:

```powershell
python -B kb_creator/scripts/reconstruct_scenario_source.py build --contract kb_creator/contracts/viral.json --source "D:\яндекс\Yandex.Disk\НРИ\1_Зов Ктулху\english\7th Edition Call of Cthulhu\Adventures\Call_of_Cthulhu_Viral.pdf" --run-root kb_creator/working/viral/source_reconstruction/20260831_step6a
python -B kb_creator/scripts/reconstruct_scenario_source.py verify --contract kb_creator/contracts/viral.json --source "D:\яндекс\Yandex.Disk\НРИ\1_Зов Ктулху\english\7th Edition Call of Cthulhu\Adventures\Call_of_Cthulhu_Viral.pdf" --run-root kb_creator/working/viral/source_reconstruction/20260831_step6a
```

All focused tests, anti-copy scans, Innsmouth regression, deterministic
two-build/refuse-overwrite checks, visual-review limitations, and the separate
repository-wide 15-`kb_creator.pdf_raw` baseline remain exactly as specified in
the original packet.

## Provenance requirements

`evidence/COMMANDS.json`, `SOURCE_IDENTITY.json`, and
`RECONSTRUCTED_EN.qa.json` must bind:

- worktree branch/HEAD and before/after status identities;
- original packet, blocked receipt, and this accepted amendment SHA-256;
- raw plus normalized identities and normalized character counts for all three
  script pairs;
- main checkout diagnostic branch/HEAD/ahead-behind and exact bridge-surface
  Git cleanliness result;
- manifest bytes/SHA/count, every manifest-file verification result, assembled
  model identity, runtime mirror closure, config/executable identities;
- every runtime version/GPU result and command exit code;
- explicit `script_invoked: false`, `initialize_invoked: false`,
  `setup_invoked: false`, and bridge mode `direct_pinned_executable`;
- environment variable names and run-root-relative values, with no secret
  values and no identity-bearing absolute source path;
- exact admitted source observation and ScenarioContract resolution order;
- engine command/profile, start/end disposition (`full_document`), return code,
  and complete engine/volatile output inventory;
- confirmation that main toolchain/runtime identities were unchanged and that
  no source, accepted, production, contract, historical translation, or
  canonical governance state was mutated.

Absolute paths may appear only in diagnostic command records. Canonical
manifests/digests use run-root-relative paths and the contract/source hashes.

## Stop conditions

In addition to every original packet stop condition, stop before source access
or extraction if any of these occurs:

- this amendment lacks an accepted independent critic receipt with no open
  P0/P1;
- branch/HEAD, packet/receipt/amendment identity, or pre-existing worktree
  status boundary differs unexpectedly;
- any raw/normalized script identity, normalized length, manifest/config/
  executable/model identity, model count, runtime mirror, or runtime version
  differs;
- the exact main bridge surface is dirty, missing, or untracked;
- read-only verification would require `initialize.ps1`, `verify.ps1`, setup,
  install, update, copy, assembly, repair, download, or a model write;
- the main runtime config does not resolve exclusively to the verified main
  model trees;
- the direct executable attempts a network access or a write outside the
  allowlisted run-root, including under `D:\NRI\MinerU` or a user-profile
  cache;
- runtime verification, PDF observation, and `resolve_source_path()` do not
  occur in the required order;
- engine output escapes `engine/mineru_hybrid_high/**`, a fourth code/test path
  is needed, or any existing path must be edited beyond the original allowlist;
- full-suite behavior differs from exactly the separately known 15 missing
  `kb_creator.pdf_raw` collection errors or introduces a new failure class.

On stop, do not repair or broaden. Preserve only already allowed run-root
evidence, mark the retry `blocked`, write the exact blocker/mutation audit to
the retry receipt, and return to the orchestrator.

## Mutation audit

Before and after the retry, record the original packet commands exactly:

```powershell
git rev-parse HEAD
git status --short --branch -uall
git diff --check
git diff --name-only
git ls-files --others --exclude-standard
```

Additionally record from `D:\NRI` before and after:

```powershell
git branch --show-current
git rev-parse HEAD
git status --short --branch -uall -- MinerU
git status --short -- MinerU/scripts/verify.ps1 MinerU/scripts/run-hybrid.ps1 MinerU/scripts/initialize.ps1 MinerU/models/manifest.json MinerU/config/mineru.template.json
```

Recompute all pinned main script, manifest, config, executable, model-store,
assembled-model, and runtime-mirror hashes after extraction. The permitted
content/path delta under `D:\NRI\MinerU` is exactly zero. The broader known
main `MinerU` dirt remains diagnostic and must be byte/path-preserved; do not
clean or absorb it.

The permitted retry delta in the Viral worktree is exactly the original three
implementation/test paths, the original `20260831_step6a` run root, and the new
immutable retry receipt. Preserve all prior status lines. Directly hash ignored
run-root files. No stage, commit, push, branch move, remote operation, or cleanup
is permitted.

## Retry task packet

After independent acceptance, create one UI-visible task named
**`Viral Step 6A reconstruction candidate retry`** with bounded executor role
`gpt-5.6-luna` at `medium`.

Prompt boundary:

> Retry only the original Viral Step 6A candidate at worktree
> `D:\NRI\.worktrees\kb-creator-viral`, branch/HEAD
> `codex/kb-creator-viral` / `54607bd3b9362adbb0c4bca64e8751482797f380`.
> Fully apply the accepted original packet and accepted MinerU bridge amendment.
> Use `D:\NRI\MinerU` read-only through the direct pinned executable bridge;
> do not invoke its verify/run/initialize scripts. Preserve the exact three-file
> implementation/test allowlist, original closed run root, and new immutable
> retry receipt. Enforce runtime verification, independent PDF observer, then
> `ScenarioContract.resolve_source_path()` before extraction. Stop rather than
> setup/install/copy/link/import/edit/broaden. Produce only a truthful
> `candidate_needs_review` or `blocked` result; no contract or publication
> promotion, Git stage/commit/push, or remote mutation.

Completion condition remains the original packet's Step 6A candidate boundary.
This amendment does not accept reconstruction, pages 1-5 modes, or `MASTER_EN`.

## Review requirement and blocker disposition

The worktree-local missing-environment blocker is technically resolved by a
fully specified, identity-bound, read-only main-runtime bridge. Retry remains
procedurally blocked until a fresh independent `gpt-5.5` critic at `medium`
reviews this amendment as a `process/architecture` change and returns no open
P0/P1. The critic must not implement or materially redesign the bridge. Any
material amendment after that review invalidates its receipt and requires a new
review.

The known repository-wide 15 missing-`kb_creator.pdf_raw` collection errors
remain a separate baseline. They are not a Step 6A bridge blocker and do not
authorize a whole-repository green claim or any repair in this retry.

## Engineering receipt

- Files read: applicable `D:\NRI\AGENTS.md`; canonical goal governance,
  plan/context; original Step 6 packet; blocked executor receipt; main/worktree
  MinerU verify/run/initialize scripts; model manifest/config/runtime identities;
  worktree and main Git boundaries.
- Read-only evidence reproduced: worktree verify exit `1`; exact normalized
  equality of all three script pairs; 55/55 manifest files with full hashes;
  runtime VLM mirror and assembled model closure; exact runtime versions/GPU;
  exact main bridge Git surface clean.
- Only file changed: this amendment receipt.
- No extraction, source observation, source copy, implementation, test run,
  setup/install, MinerU initialization, accepted/production/contract mutation,
  staging, commit, push, or remote operation occurred.
- Blocker: technical dependency blocker resolved in specification; retry awaits
  independent critic acceptance.
- Next action: independent critic review; only after acceptance may the bounded
  UI-visible retry task be dispatched.
- Elapsed time: unavailable as an exact platform value.
- Token use: unavailable to this contributor; no precision invented.

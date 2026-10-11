# GPT-5.5 independent critic receipt — Viral Step 6A cache-closure delta

- Goal id: `20260830-kb-creator-next-scenario`
- Step id: `6-source-reconstruction-step6a-cache-closure-review`
- Review kind: `process`
- Role: fresh independent critic
- Policy model / effort: `gpt-5.5` / `medium`
- Actual platform model / effort: `unavailable` (not exposed to this task)
- Orchestrator policy owner: main chat `gpt-5.6-sol` / `medium`
- Assignment state: `matched` by `nri-independent-critic`; platform runtime unverified
- Scoped override: `none`
- Independence declaration: I did not implement, remediate, or materially design
  the Step 6A MinerU bridge, the cache-closure delta, or the candidate under
  review.
- Timestamp: `2026-08-31T01:38:48.9316271+03:00` (`Europe/Moscow`)
- Elapsed time: unavailable as an exact platform value
- Token use: unavailable to this contributor; no precision invented
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`
- Required HEAD: `54607bd3b9362adbb0c4bca64e8751482797f380`
- Observed HEAD: `54607bd3b9362adbb0c4bca64e8751482797f380`
- Result: `rejected_pending_audit-scope_delta`

## Scope

This is a delta review only. I reviewed whether
`terra_engineering_viral_step6a_cache_closure_20260831.md` closes the prior
Step 6A bridge review's P1 hidden-write/cache/network-control finding and P2
`_bridge_runtime/**` run-root wording finding.

I did not review a reconstruction candidate, Step 6A implementation, QA result,
`MASTER_EN`, translation, HTML/PDF, production packaging, or release readiness.
The known repository-wide 15 missing-`kb_creator.pdf_raw` collection errors
remain outside this review except as the declared baseline.

## Candidate identities verified

| Input | Expected SHA-256 | Observed SHA-256 | Result |
|---|---|---|---|
| Prior bridge amendment: `terra_engineering_viral_step6a_mineru_bridge_20260831.md` | `B41041A90791A5FD2888ECEC0470592F4D87C55BA2A616B3D45FB1584D86A603` | `B41041A90791A5FD2888ECEC0470592F4D87C55BA2A616B3D45FB1584D86A603` | match |
| Prior reject receipt: `gpt55_critic_viral_step6a_mineru_bridge_review_20260831.md` | `508684F9E99DA4C68DCF3D41B3BABB05721EABF2500F6D3B8BEA8D0496BABBE5` | `508684F9E99DA4C68DCF3D41B3BABB05721EABF2500F6D3B8BEA8D0496BABBE5` | match |
| Cache-closure delta: `terra_engineering_viral_step6a_cache_closure_20260831.md` | `C84E0352B748643618E84A814BA555A5B681038FF98644C493526D3D5252C802` | `C84E0352B748643618E84A814BA555A5B681038FF98644C493526D3D5252C802` | match |
| Original Step 6 packet: `terra_engineering_viral_source_reconstruction_packet_20260831.md` | `011CF87FFA0B0DACC85559DEF601A5FD9EED0755F86EB877C263CF2F2D8FABBC` | `011CF87FFA0B0DACC85559DEF601A5FD9EED0755F86EB877C263CF2F2D8FABBC` | match |
| Blocked Step 6A receipt: `luna_executor_viral_source_reconstruction_20260831.md` | `31A50C84CF8EDC3F90EE1DED5643C019AEA47C00C0C0F31D466E13AD18E79B44` | `31A50C84CF8EDC3F90EE1DED5643C019AEA47C00C0C0F31D466E13AD18E79B44` | match |

## Files checked

- `D:\NRI\AGENTS.md`
- `D:\NRI\.worktrees\kb-creator-viral\docs\governance\nri_goal_governance.md`
- `D:\NRI\.worktrees\kb-creator-viral\kb_creator\docs\plans\20260830-kb-creator-next-scenario\plan.md`
- `D:\NRI\.worktrees\kb-creator-viral\kb_creator\docs\plans\20260830-kb-creator-next-scenario\context.md`
- `D:\NRI\.worktrees\kb-creator-viral\kb_creator\docs\plans\20260830-kb-creator-next-scenario\handoffs\terra_engineering_viral_source_reconstruction_packet_20260831.md`
- `D:\NRI\.worktrees\kb-creator-viral\kb_creator\docs\plans\20260830-kb-creator-next-scenario\handoffs\luna_executor_viral_source_reconstruction_20260831.md`
- `D:\NRI\.worktrees\kb-creator-viral\kb_creator\docs\plans\20260830-kb-creator-next-scenario\handoffs\terra_engineering_viral_step6a_mineru_bridge_20260831.md`
- `D:\NRI\.worktrees\kb-creator-viral\kb_creator\docs\plans\20260830-kb-creator-next-scenario\handoffs\gpt55_critic_viral_step6a_mineru_bridge_review_20260831.md`
- `D:\NRI\.worktrees\kb-creator-viral\kb_creator\docs\plans\20260830-kb-creator-next-scenario\handoffs\terra_engineering_viral_step6a_cache_closure_20260831.md`
- `D:\NRI\MinerU\.runtime\mineru.json`
- `D:\NRI\MinerU\.venv\pyvenv.cfg`
- `D:\NRI\MinerU\.venv\Lib\site-packages\mineru-3.4.4.dist-info\METADATA`
- `D:\NRI\MinerU\.venv\Lib\site-packages\modelscope_hub\constants.py`
- `D:\NRI\MinerU\.venv\Lib\site-packages\modelscope_hub\config.py`
- `D:\NRI\MinerU\.venv\Lib\site-packages\modelscope\hub\utils\utils.py`
- `D:\NRI\MinerU\.venv\Lib\site-packages\modelscope\hub\snapshot_download.py`
- `D:\NRI\MinerU\src\mineru\utils\models_download_utils.py`
- `D:\NRI\MinerU\src\mineru\utils\config_reader.py`
- `D:\NRI\MinerU\src\mineru\model\ocr\pytorch_paddle.py`
- `D:\NRI\MinerU\src\mineru\model\utils\tools\infer\pytorchocr_utility.py`
- `D:\NRI\MinerU\src\mineru\utils\language.py`
- `D:\NRI\MinerU\.venv\Lib\site-packages\fast_langdetect\ft_detect\infer.py`
- `C:\Users\BogdanD\AppData\Roaming\uv\python\cpython-3.12-windows-x86_64-none\Lib\ntpath.py`

## Files changed

Only this immutable receipt:

`kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_step6a_cache_closure_review_20260831.md`

No implementation, remediation, source processing, runtime mutation, contract
mutation, test edit, accepted/production change, canonical plan/context/status/
release edit, staging, commit, push, or remote mutation was performed.

## Verification performed

- Verified worktree HEAD exactly
  `54607bd3b9362adbb0c4bca64e8751482797f380`.
- Verified all five requested hashes exactly as listed above.
- Re-read governance and canonical plan/context to confirm main-chat
  orchestration ownership, critic independence, Step 6 candidate-only boundary,
  and no publication/release authority.
- Re-read the prior reject receipt to bind this review to its two findings:
  P1 hidden-write/cache/network closure and P2 run-root cache exception
  wording.
- Independently inspected installed-code evidence for:
  - `MINERU_MODEL_SOURCE=local` support in
    `src/mineru/utils/models_download_utils.py`;
  - configured local model roots from
    `src/mineru/utils/config_reader.py` and
    `D:\NRI\MinerU\.runtime\mineru.json`;
  - ModelScope cache/home controls in `modelscope_hub` and legacy
    `modelscope` compatibility code;
  - absence of installed `paddle*` / `paddleocr*` distributions or directories
    in this venv;
  - absence of scanned installed-code support for invented names such as
    `MODELSCOPE_OFFLINE`, `PADDLE_HOME`, and `PADDLEOCR_HOME`;
  - CPython `--help-env` support for `PYTHONDONTWRITEBYTECODE`,
    `PYTHONPYCACHEPREFIX`, and `PYTHONNOUSERSITE`;
  - Windows `ntpath.expanduser` use of `USERPROFILE`;
  - fast-langdetect `FTLANG_CACHE`;
  - NVIDIA GPU identity as `NVIDIA GeForce RTX 5080, 581.80`.

## Delta assessment

The delta materially improves the bridge. It addresses the prior cache-control
substance by:

- selecting `MINERU_MODEL_SOURCE=local` instead of relying on the configured
  `"model-source": "modelscope"` remote preference;
- using only installed-code-supported ModelScope controls
  `MODELSCOPE_CACHE` and `MODELSCOPE_HOME`;
- not inventing unsupported `MODELSCOPE_OFFLINE`, `PADDLE_HOME`, or
  `PADDLEOCR_HOME` controls;
- removing credential-like environment variables from the child by name
  without recording values;
- making `HOME`, `USERPROFILE`, `APPDATA`, and `LOCALAPPDATA` child-only;
- replacing dependency-import runtime verification with metadata/config/hash
  checks plus `python.exe -I -B --version` and `nvidia-smi`;
- explicitly defining `_bridge_runtime/**` as the sole run-root cache exception
  with a closed purpose enum.

Those choices are directionally sound and resolve the original P2 wording
problem in principle. They also close most of the original P1 cache-redirection
gap.

The remaining blocker is the proposed proof mechanism: the delta requires a
complete recursive pre/post snapshot and SHA-256 hashing of the real user
profile, real AppData roots, real temp root, and Python base, then rejects any
metadata or content delta even if caused by unrelated desktop activity. That is
too broad for a bounded Step 6A executor, risks reading credential/private
files, and is likely infeasible or nondeterministically blocking on an active
Windows desktop.

## Findings

### P1 — External mutation audit is overbroad, privacy-risky, and not executable as a bounded gate

Evidence:

- Cache-closure delta lines `269-315` require resolving
  `real_userprofile`, `real_appdata`, `real_localappdata`, `real_temp`, and
  `python_base`, then creating complete snapshots for every root before and
  after runtime activity.
- The same section requires every regular file in those roots to record bytes,
  `LastWriteTimeUtc`, and SHA-256, while not following reparse points and
  treating inaccessible/disappearing files as stop conditions.
- Lines `309-315` permit zero delta under `real_userprofile`,
  `real_appdata`, `real_localappdata`, `real_temp`, and `python_base`.
- Lines `316-323` reject any outside delta even if another process appears to
  have caused it and explicitly forbid attribution-based exceptions.
- Root `D:\NRI\MinerU\.venv\pyvenv.cfg` identifies the Python base as
  `C:\Users\BogdanD\AppData\Roaming\uv\python\cpython-3.12-windows-x86_64-none`,
  so the proposed audit reaches outside the project/tool root into the real
  user profile/AppData hierarchy.

Why this matters:

The delta is trying to prevent hidden writes, but the proposed audit reads far
more than the MinerU dependency cache surface. A complete user-profile/AppData
hash walk can touch credential stores, browser/application data, cloud-sync
state, and unrelated private files. Even if the receipt records only hashes,
the executor still reads data outside the authorized project/tool scope. It
also makes retry success depend on the entire Windows desktop staying
metadata-quiet during a long GPU extraction, which is not a stable or
executor-testable acceptance condition.

This does not merely create a nuisance stop; it turns a narrow cache closure
into broad local-profile surveillance and a high-probability false blocker.
That violates the minimal bounded-task model and does not preserve the intended
separation between Step 6A reconstruction evidence and unrelated host state.

Required remediation:

Replace the full-profile/AppData/temp recursive snapshot with a scoped,
executor-testable outside-write audit limited to the actual default and
redirected surfaces implicated by the installed code. The amended gate must:

1. audit only named roots/path prefixes that MinerU, ModelScope, Hugging Face,
   Python, fast-langdetect, Torch/Triton/CUDA, Matplotlib, temp handling, and
   the configured Python base could plausibly touch for this command;
2. explicitly include the known real-profile defaults being defended against,
   such as `real_userprofile\.cache\modelscope`,
   `real_userprofile\.modelscope`, relevant Hugging Face/cache defaults if not
   redirected, real temp, Python base/package directories, and main
   `D:\NRI\MinerU` runtime/model/config paths;
3. avoid recursively hashing arbitrary credential/browser/application data
   outside those named path prefixes;
4. record path/metadata/hash only for files inside those named audit prefixes,
   with secret-value redaction and no file-content capture;
5. treat an observed delta inside a named protected prefix as a stop, but not
   require the entire real user profile or AppData trees to remain unchanged;
6. keep child-only `HOME`, `USERPROFILE`, `APPDATA`, `LOCALAPPDATA`, cache
   env overrides, credential-variable stripping, and `_bridge_runtime/**`
   inventory semantics.

Until this audit scope is narrowed, Step 6A retry remains procedurally blocked.

### P2 — Network-attempt detection remains best-effort and should be stated as such or made authoritative

Evidence:

- Cache-closure delta lines `213-230` route ModelScope endpoint/proxies to an
  asserted-unbound loopback sink and reject any observed TCP/UDP endpoint by
  the MinerU process tree.
- Lines `289-307` require read-only samples of `Get-NetTCPConnection` and
  `Get-NetUDPEndpoint` for the process tree from creation until exit, with
  sampling failure as a stop.

Why this matters:

Sampling OS connection tables may miss very short-lived attempts and does not
by itself enforce a network block. The offline controls are useful, and the
loopback sink makes ordinary HTTP-client leakage fail closed, but the claim
should not overstate proof of no network attempt unless the executor uses an
authoritative mechanism such as an actual process-contained network deny rule,
ETW/netsh trace with sufficient capture, or equivalent evidence.

Required remediation:

Either state this as a best-effort audit plus fail-closed loopback/proxy
containment residual risk, or require an authoritative network-deny/capture
mechanism for the MinerU child process tree. This is not independently a retry
blocker if the P1 audit scope is fixed and the residual risk is recorded.

## Non-findings / accepted delta controls

- No P0 findings.
- The original P2 run-root wording issue is substantively closed: delta lines
  `326-366` define `engine/mineru_hybrid_high/_bridge_runtime/**` as the sole
  cache exception, restrict it to redirected bridge runtime artifacts, require
  provenance rows, and forbid model/download parts, bytecode, pytest caches,
  browser profiles, credentials, sessions, raw unrelated logs, source copies,
  accepted outputs, and unknown-purpose files.
- The installed-code evidence supports `MINERU_MODEL_SOURCE=local` as a real
  control path. In `models_download_utils.py`, `local` is an accepted source
  and returns configured local roots instead of choosing the snapshot-download
  branches.
- The installed-code evidence supports `MODELSCOPE_CACHE` and
  `MODELSCOPE_HOME`; it also supports not inventing `MODELSCOPE_OFFLINE`.
- The no-Paddle/PaddleOCR-distribution claim is supported by the installed
  venv listing and MinerU metadata: `mineru-3.4.4.dist-info\METADATA` declares
  `modelscope>=1.26.0` and does not declare Paddle/PaddleOCR.
- Child-only `HOME`/`USERPROFILE`/`APPDATA`/`LOCALAPPDATA` isolation is
  conceptually valid for a pinned child process, provided the audit does not
  expand into whole-profile hashing.
- Replacing the pre-source Torch import probe with metadata/hash checks plus
  `python.exe -I -B --version` and `nvidia-smi` is a safer runtime-verification
  boundary and preserves the order
  `runtime_verified -> pdf_observed -> resolve_source_path_passed -> extraction`.
- Credential handling is directionally correct: the delta removes sensitive
  child environment variable names and records only redacted names, not values.
- The delta does not authorize setup/install/update/copy/link/junction, main
  script invocation, contract mutation, source-PDF copy, historical
  translation authority, `build_viral_*`/`freeze_viral_*` copies, publication,
  staging, commit, push, or remote mutation.

## Recommendation

`reject`

The prior P2 is closed, and the prior P1 is mostly closed at the child
environment level, but the proposed external mutation audit introduces an open
P1. Step 6A retry is not authorized until that audit is narrowed to specific
installed-code-relevant protected roots/path prefixes without recursively
hashing the real user profile/AppData trees.

## Residual risks if remediated

- Even with narrowed path-prefix auditing, network-attempt detection will remain
  partly evidentiary unless an authoritative deny/capture mechanism is added.
- GPU/runtime libraries may still create transient files under redirected
  cache roots; the `_bridge_runtime/**` inventory and closed-purpose enum must
  classify them strictly.
- Any implementation of the child environment must avoid parent-process
  environment mutation and must construct argv without shell interpolation.

## Blockers and next action

Blocker: open P1 overbroad external-root audit and credential/private-file
read risk.

Next action: orchestrator requests a narrow engineering delta replacing
whole-profile/AppData hashing with a scoped protected-prefix audit while
preserving the accepted child-environment controls and `_bridge_runtime/**`
semantics. A fresh independent critic check may then be limited to that audit
delta. Material Step 6A retry may begin only after no P0/P1 remains.

## Detached receipt SHA-256

Compute after final write.

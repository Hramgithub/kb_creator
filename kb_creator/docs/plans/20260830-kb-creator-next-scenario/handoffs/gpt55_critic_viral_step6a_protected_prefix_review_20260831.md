# GPT-5.5 independent critic receipt — Viral Step 6A protected-prefix audit delta

- Goal id: `20260830-kb-creator-next-scenario`
- Step id: `6-source-reconstruction-step6a-protected-prefix-review`
- Review kind: `process`
- Role: fresh independent critic
- Policy model / effort: `gpt-5.5` / `medium`
- Actual platform model / effort: `unavailable` (not exposed to this task)
- Orchestrator policy owner: main chat `gpt-5.6-sol` / `medium`
- Assignment state: `matched` by `nri-independent-critic`; platform runtime unverified
- Scoped override: `none`
- Independence declaration: I did not implement, remediate, or materially design
  the Step 6A MinerU bridge, cache closure, protected-prefix delta, or runtime
  candidate under review.
- Timestamp: `2026-08-31T01:47:25.6848731+03:00` (`Europe/Moscow`)
- Elapsed time: unavailable as an exact platform value
- Token use: unavailable to this contributor; no precision invented
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`
- Required HEAD: `54607bd3b9362adbb0c4bca64e8751482797f380`
- Observed HEAD: `54607bd3b9362adbb0c4bca64e8751482797f380`
- Result: `accepted_delta`

## Scope

This is a narrow delta review limited to the remaining P1 protected-prefix
audit issue and P2 network-wording issue from
`gpt55_critic_viral_step6a_cache_closure_review_20260831.md`. I did not review
a Step 6A implementation, reconstruction candidate, QA result, `MASTER_EN`,
translation, HTML/PDF, production package, or release readiness.

## Candidate identities verified

| Input | Expected SHA-256 | Observed SHA-256 | Result |
|---|---|---|---|
| Prior cache-closure reject receipt: `gpt55_critic_viral_step6a_cache_closure_review_20260831.md` | `15B3E311F1ADA607C45F8FB4A9464B8068E7C0425159F04F7F49A2C01A070BFB` | `15B3E311F1ADA607C45F8FB4A9464B8068E7C0425159F04F7F49A2C01A070BFB` | match |
| Protected-prefix delta: `terra_engineering_viral_step6a_protected_prefix_audit_20260831.md` | `C8A7C8A7AA81113F557A3642328D88878F12BFFC1A89B441F34DB74E572E8DBB` | `C8A7C8A7AA81113F557A3642328D88878F12BFFC1A89B441F34DB74E572E8DBB` | match |
| Cache-closure delta: `terra_engineering_viral_step6a_cache_closure_20260831.md` | `C84E0352B748643618E84A814BA555A5B681038FF98644C493526D3D5252C802` | `C84E0352B748643618E84A814BA555A5B681038FF98644C493526D3D5252C802` | match |
| Bridge amendment: `terra_engineering_viral_step6a_mineru_bridge_20260831.md` | `B41041A90791A5FD2888ECEC0470592F4D87C55BA2A616B3D45FB1584D86A603` | `B41041A90791A5FD2888ECEC0470592F4D87C55BA2A616B3D45FB1584D86A603` | match |

## Files checked

- `D:\NRI\AGENTS.md`
- `D:\NRI\.worktrees\kb-creator-viral\docs\governance\nri_goal_governance.md`
- `D:\NRI\.worktrees\kb-creator-viral\kb_creator\docs\plans\20260830-kb-creator-next-scenario\plan.md`
- `D:\NRI\.worktrees\kb-creator-viral\kb_creator\docs\plans\20260830-kb-creator-next-scenario\context.md`
- `D:\NRI\.worktrees\kb-creator-viral\kb_creator\docs\plans\20260830-kb-creator-next-scenario\handoffs\gpt55_critic_viral_step6a_cache_closure_review_20260831.md`
- `D:\NRI\.worktrees\kb-creator-viral\kb_creator\docs\plans\20260830-kb-creator-next-scenario\handoffs\terra_engineering_viral_step6a_protected_prefix_audit_20260831.md`
- `D:\NRI\.worktrees\kb-creator-viral\kb_creator\docs\plans\20260830-kb-creator-next-scenario\handoffs\terra_engineering_viral_step6a_cache_closure_20260831.md`
- `D:\NRI\.worktrees\kb-creator-viral\kb_creator\docs\plans\20260830-kb-creator-next-scenario\handoffs\terra_engineering_viral_step6a_mineru_bridge_20260831.md`
- `D:\NRI\MinerU\.runtime\mineru.json`
- `D:\NRI\MinerU\.venv\pyvenv.cfg`
- `D:\NRI\MinerU\.venv\Lib\site-packages\mineru-3.4.4.dist-info\METADATA`
- `D:\NRI\MinerU\src\mineru\utils\models_download_utils.py`
- `D:\NRI\MinerU\src\mineru\utils\config_reader.py`
- `D:\NRI\MinerU\.venv\Lib\site-packages\modelscope_hub\constants.py`
- `D:\NRI\MinerU\.venv\Lib\site-packages\modelscope_hub\config.py`
- `D:\NRI\MinerU\.venv\Lib\site-packages\modelscope\hub\utils\utils.py`
- `D:\NRI\MinerU\.venv\Lib\site-packages\modelscope\hub\snapshot_download.py`
- `D:\NRI\MinerU\.venv\Lib\site-packages\huggingface_hub\constants.py`
- `D:\NRI\MinerU\.venv\Lib\site-packages\torch\hub.py`
- `D:\NRI\MinerU\src\mineru\utils\language.py`
- `D:\NRI\MinerU\.venv\Lib\site-packages\fast_langdetect\ft_detect\infer.py`
- `C:\Users\BogdanD\AppData\Roaming\uv\python\cpython-3.12-windows-x86_64-none\Lib\tempfile.py`
- `C:\Users\BogdanD\AppData\Roaming\uv\python\cpython-3.12-windows-x86_64-none\Lib\ntpath.py`

## Files changed

Only this immutable receipt:

`kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_step6a_protected_prefix_review_20260831.md`

No implementation, remediation, source processing, runtime verification,
extraction, tests, contract mutation, accepted/production change, canonical
plan/context/status/release edit, staging, commit, push, or remote mutation was
performed.

## Verification performed

- Verified required worktree HEAD exactly
  `54607bd3b9362adbb0c4bca64e8751482797f380`.
- Verified the prior reject receipt, new protected-prefix delta, cache-closure
  delta, and bridge amendment hashes exactly as listed above.
- Re-read governance and canonical plan/context to confirm critic independence,
  main-chat orchestration ownership, Step 6 candidate-only boundary, and
  no-publication/no-release authority.
- Re-read the prior cache-closure reject receipt to bind this review to its
  remaining P1/P2 only.
- Independently re-checked installed evidence that supports the bounded-prefix
  set:
  - MinerU metadata declares `mineru 3.4.4` and `modelscope>=1.26.0` without
    Paddle/PaddleOCR dependency declarations.
  - Installed venv listing showed no `paddle*` or `paddleocr*` distribution
    directory.
  - `models_download_utils.py` supports `MINERU_MODEL_SOURCE=local` and returns
    configured local model roots before snapshot-download branches.
  - `config_reader.py` reads `MINERU_TOOLS_CONFIG_JSON` and configured
    `models-dir` roots; pinned `mineru.json` contains local pipeline/VLM roots
    while retaining configured `"model-source": "modelscope"`.
  - ModelScope code supports `MODELSCOPE_CACHE`, `MODELSCOPE_HOME`, and
    endpoint selection; no installed-code support for `MODELSCOPE_OFFLINE` was
    found in the searched paths.
  - Hugging Face constants derive `~/.cache/huggingface/{hub,assets,xet}` and
    token material under the Hugging Face home root.
  - Torch hub derives `~/.cache/torch` through `TORCH_HOME` /
    `XDG_CACHE_HOME`.
  - CPython `tempfile.py` chooses `TMPDIR`, then `TEMP`, then `TMP`, then
    platform defaults; the child setting `TEMP`/`TMP` is therefore relevant.
  - CPython `ntpath.py` uses `USERPROFILE` for `expanduser` on Windows.
  - `fast_langdetect` uses `FTLANG_CACHE` for high-memory model cache/download
    location.
  - No installed Matplotlib package directory was found in the pinned venv.

## Findings

None. No P0, P1, or P2 findings remain for this delta scope.

## Closure assessment

The new delta closes the prior P1 audit-scope blocker.

Evidence:

- Lines `31-44` explicitly supersede and revoke the prior full recursive scans
  of `real_userprofile`, `real_appdata`, `real_localappdata`, `real_temp`, and
  `python_base`, and also revoke authoritative no-network wording based on
  endpoint-table sampling.
- Lines `58-85` derive the protected set from installed-code/default-path
  evidence rather than from a parent-directory scan.
- Lines `87-117` define a bounded protected-prefix table. It limits recursive
  hashing to specific non-sensitive cache prefixes:
  `real_userprofile\.cache\modelscope`,
  `real_userprofile\.cache\huggingface\hub`,
  `real_userprofile\.cache\huggingface\assets`,
  `real_userprofile\.cache\huggingface\xet`, and
  `real_userprofile\.cache\torch`.
- The sensitive `real_userprofile\.modelscope` and Hugging Face root are
  sentinel-only. The delta explicitly forbids opening/enumerating credential,
  cookie, token, session, user-record, or unknown sibling paths.
- The exact pinned runtime/model/code identity set remains bounded to accepted
  explicit paths, manifest rows, named distribution `METADATA`/`RECORD` files,
  and exact installed source/module files used for model/cache decisions. It
  does not reintroduce recursive scans of `python_base`, `Lib`, all
  `site-packages`, `APPDATA`, or all `D:\NRI\MinerU`.
- Lines `119-140` explicitly decline broad scans for real temp,
  fast-langdetect `/tmp`, Matplotlib, TorchInductor/Triton/CUDA, roaming/local
  AppData, and Python-base parent paths, recording those as residuals instead
  of silently expanding audit scope.
- Lines `145-217` provide executable pseudocode that uses exact named sets,
  lexical child checks, reparse-safe traversal, sentinel-only handling for
  sensitive roots, and secret-free delta reporting.

The new delta also closes the prior P2 network wording issue.

Evidence:

- Lines `219-242` state that `Get-NetTCPConnection` /
  `Get-NetUDPEndpoint` sampling is best-effort observation, not enforcement and
  not authoritative proof of network denial.
- The same section preserves substantive containment controls:
  local model resolution, `MINERU_MODEL_SOURCE=local`, credential-name removal
  without value reads, Hugging Face offline flags, loopback endpoint/proxy sink,
  disabled LLM-aided config, and rejection of model/download/session/credential
  artifacts in `_bridge_runtime`.
- Sampling unavailable, permission-limited, or incomplete is recorded as a
  residual rather than converted into an admin/firewall/tool-install
  requirement or a false authoritative claim.

Accepted controls preserved from prior deltas:

- direct pinned `D:\NRI\MinerU\.venv\Scripts\mineru.exe` bridge only;
- no main `verify.ps1`, `run-hybrid.ps1`, `initialize.ps1`, setup, install,
  update, model assembly, copy, symlink, junction, or wrapper path;
- child-only `HOME`, `USERPROFILE`, `APPDATA`, `LOCALAPPDATA`, cache roots, and
  working directory under `_bridge_runtime`;
- secret-bearing environment values are not read or serialized;
- `MINERU_MODEL_SOURCE=local`, `MODELSCOPE_CACHE`, `MODELSCOPE_HOME`,
  supported HF/Torch/temp/Python/fast-langdetect cache controls, and no
  invented unsupported Paddle/ModelScope offline env names;
- `engine/mineru_hybrid_high/_bridge_runtime/**` remains the sole run-root cache
  exception with closed inventory semantics;
- original three-file implementation/test allowlist, original run root, and
  retry receipt boundary remain unchanged;
- runtime order remains
  `runtime_verified -> pdf_observed -> resolve_source_path_passed -> extraction`;
- no historical translation, `translator/config/viral.package.json`,
  `build_viral_*`, or `freeze_viral_*` authority is introduced.

## Recommendation

`accept`

Step 6A retry is authorized after orchestrator integration of this accepted
delta. This review accepts only the protected-prefix/cache/network process
delta; it does not accept any future runtime output, reconstruction candidate,
page/content-mode closure, `reconstruction_ready`, `MASTER_EN`, publication, or
release state.

## Residual risks

- Network observation is intentionally best-effort. Local-model selection,
  offline flags, credential stripping, and loopback/proxy containment reduce the
  practical risk, but they are not a process-level firewall.
- Native code that ignores `TEMP`/`TMP`, cache overrides, or child profile
  values could still write to an unknown host path. The delta records this as a
  residual instead of authorizing broad host scans.
- Sensitive roots such as `.modelscope` and Hugging Face home are sentinel-only
  to avoid credential exposure; mutations below existing sensitive children are
  intentionally not proven.
- Exact implementation remains important: argv must be constructed without
  shell interpolation, parent environment must not be mutated, and protected
  prefixes must be computed as lexical children without parent enumeration.

## Blockers and next action

Blockers: none in this delta scope.

Next action: orchestrator may dispatch the UI-visible Step 6A reconstruction
candidate retry using the original packet plus the accepted bridge,
cache-closure, and protected-prefix deltas. The retry remains candidate-only
and must stop on any original or amended stop condition.

## Detached receipt SHA-256

Compute after final write.

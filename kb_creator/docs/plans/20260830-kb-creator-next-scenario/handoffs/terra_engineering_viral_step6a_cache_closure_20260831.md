# Terra engineering remediation — Viral Step 6A MinerU hidden-write closure

- Goal id: `20260830-kb-creator-next-scenario`
- Step id: `6-source-reconstruction-step6a-cache-closure`
- Role: engineering assistance
- Policy model / effort: `gpt-5.6-terra` / `medium`
- Actual platform model / effort: `unavailable` (not exposed to this task)
- Orchestrator policy owner: main chat `gpt-5.6-sol` / `medium`
- Assignment state: `platform-unverified`; policy role honored
- Scoped override: `none`
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`
- Branch / required and observed HEAD: `codex/kb-creator-viral` /
  `54607bd3b9362adbb0c4bca64e8751482797f380`
- Timestamp: `2026-08-31T01:33:40.6407428+03:00` (`Europe/Moscow`)
- Result: `remediation_ready_pending_fresh_independent_accept`
- Files changed: only this receipt

## Candidate identity and authority

This receipt closes only the two findings in the rejected bridge review. It is
an additive, narrow correction to the MinerU invocation/preflight portion of
the original Step 6 packet and bridge amendment. It does not replace or relax
any original allowlist, admission step, QA requirement, or stop condition.

| Immutable input | Required and observed SHA-256 |
|---|---|
| `terra_engineering_viral_source_reconstruction_packet_20260831.md` | `011CF87FFA0B0DACC85559DEF601A5FD9EED0755F86EB877C263CF2F2D8FABBC` |
| `luna_executor_viral_source_reconstruction_20260831.md` | `31A50C84CF8EDC3F90EE1DED5643C019AEA47C00C0C0F31D466E13AD18E79B44` |
| `terra_engineering_viral_step6a_mineru_bridge_20260831.md` | `B41041A90791A5FD2888ECEC0470592F4D87C55BA2A616B3D45FB1584D86A603` |
| `gpt55_critic_viral_step6a_mineru_bridge_review_20260831.md` | `508684F9E99DA4C68DCF3D41B3BABB05721EABF2500F6D3B8BEA8D0496BABBE5` |

No setup, install, update, copy, model assembly, link/junction, wrapper, script
import, main MinerU script invocation, source observation, extraction, test,
contract mutation, plan/context/status/release edit, staging, commit, push, or
remote operation was performed or is authorized by this receipt.

## Read-only installed-stack evidence

The following evidence was read directly from the installed MinerU environment;
no package was imported to obtain it.

1. `D:\NRI\MinerU\.venv\Lib\site-packages\mineru-3.4.4.dist-info\METADATA`
   declares MinerU `3.4.4`, requires `modelscope>=1.26.0`, and does not declare
   Paddle or PaddleOCR.
2. The installed distributions are `modelscope 1.39.1` and
   `modelscope-hub 0.2.0`. No `paddle*` or `paddleocr*` distribution/directory
   exists in this venv.
3. The editable finder maps installed package `mineru` to
   `D:\NRI\MinerU\src\mineru`.
4. `src/mineru/utils/models_download_utils.py:14,211-245` defines and reads
   `MINERU_MODEL_SOURCE`; value `local` is explicitly supported. Lines 279-324
   return the configured local model roots for `local` and call ModelScope or
   Hugging Face snapshot download only for a remote source.
5. `src/mineru/utils/config_reader.py:219-226` obtains both local model roots
   from the pinned config. The pinned `D:\NRI\MinerU\.runtime\mineru.json`
   declares remote preference `modelscope`, but also declares absolute local
   roots `D:\NRI\MinerU\models\pipeline` and
   `D:\NRI\MinerU\.runtime\models\vlm`; the bridge amendment already pins the
   config SHA-256 and verifies all 55 manifest rows plus the 14-file VLM mirror.
6. MinerU imports `modelscope.snapshot_download` at
   `src/mineru/utils/models_download_utils.py:8`; therefore ModelScope import
   side effects still require containment even when `local` prevents the
   downloader call.
7. `modelscope/hub/snapshot_download.py:60-112` delegates the actually imported
   API to `modelscope_hub.compat` and defaults `local_files_only` to false.
   MinerU does not pass that argument. No installed code-supported
   `MODELSCOPE_OFFLINE` environment variable was found, so this receipt does
   not invent or rely on one.
8. `modelscope_hub/constants.py:263-269` names exactly
   `MODELSCOPE_CACHE` and `MODELSCOPE_HOME`. `modelscope_hub/config.py:36-66`
   reads them and otherwise falls back to `Path.home()/.cache/modelscope` and
   `Path.home()/.modelscope`; lines 135-140 can create cache/config/credential
   directories.
9. The legacy compatibility lookup also honors `MODELSCOPE_CACHE` and otherwise
   uses the user home (`modelscope/hub/utils/utils.py:182-202,205-250`).
10. `src/mineru/model/ocr/pytorch_paddle.py:8-27,50-107` is the active
    `PytorchPaddleOCR` implementation: NumPy/OpenCV/PyTorch-side code with local
    model resolution through MinerU. The word `paddle` in this path describes
    the converted model family, not an installed Paddle/PaddleOCR runtime.
    `MINERU_SEAL_OCR_DEBUG_DIR` is the only supported debug-output override in
    this file (`:114-137`); debug is disabled unless explicitly enabled.
11. `src/mineru/model/utils/tools/infer/pytorchocr_utility.py:141` declares a
    relative `./log_output/` default, although no use of `save_log_path` was
    found in the installed MinerU source. A volatile working directory is still
    required so any future relative write cannot escape.
12. CPython is `3.12.13`. Its installed `--help-env` documents
    `PYTHONDONTWRITEBYTECODE`, `PYTHONPYCACHEPREFIX`, and `PYTHONNOUSERSITE`.
    Installed `Lib/ntpath.py:351-375` shows Windows `expanduser` selects
    `USERPROFILE`; thus `XDG_CACHE_HOME` alone cannot close Windows user-home
    writes.
13. MinerU `src/mineru/utils/language.py:5-10` supports `FTLANG_CACHE`.
    Installed `fast_langdetect/ft_detect/infer.py:15-20,128-171` can download a
    large FastText model into that cache for high-memory use; its normal
    `detect_language` entry point defaults to the bundled low-memory model.
14. MinerU CLI file logging found in the installed source is stderr-only
    (`cli/client.py`, `cli/fast_api.py`, and `cli/gradio_app.py`). No supported
    global MinerU file-log-root environment variable was found.

These observations support only the exact controls below. In particular, no
`PADDLE_HOME`, `PADDLEOCR_HOME`, `MODELSCOPE_OFFLINE`, or other unverified name
is authorized.

## P1 closure: exact isolated child environment

The direct pinned executable remains exactly
`D:\NRI\MinerU\.venv\Scripts\mineru.exe`; its argv/profile remains exactly:

```text
--path <admitted immutable source> --output <engineRoot>
--backend hybrid-engine --effort high --formula True --table True
```

The original full-document rule remains: no `--start` or `--end`. The only
command construction delta is that the approved generic three-file seam must
start that executable with an isolated child-process environment and working
directory instead of mutating the parent PowerShell environment and invoking
`& mineru.exe` directly.

Create these additional directories only below the existing `$volatileRoot`:

```text
profile/
profile/appdata/roaming/
profile/appdata/local/
cwd/
tmp/
modelscope/cache/
modelscope/home/
hf/hub/
hf/xet/
torch/
torchinductor/
triton/
cuda/
xdg/
mpl/
python/pycache/
fastlang/
seal_ocr_debug/
```

Construct a child-only environment map. Preserve the parent environment
unchanged. Paths below are `$volatileRoot`-relative in provenance; the child
receives resolved absolute paths only at launch.

| Child environment name | Exact child value / target | Reason |
|---|---|---|
| `MINERU_TOOLS_CONFIG_JSON` | pinned absolute `D:\NRI\MinerU\.runtime\mineru.json` | read-only config identity |
| `MINERU_MODEL_SOURCE` | `local` | code-supported hard selection of configured local model roots; prevents ModelScope/HF downloader selection |
| `MODELSCOPE_CACHE` | `modelscope/cache` | installed ModelScope cache override |
| `MODELSCOPE_HOME` | `modelscope/home` | installed ModelScope config/session/credential-root override |
| `MODELSCOPE_ENDPOINT` | `http://127.0.0.1:9` | installed endpoint override; fail-closed local sink, never an external endpoint |
| `HF_HOME` | `hf` | Hugging Face root |
| `HUGGINGFACE_HUB_CACHE` | `hf/hub` | Hub cache |
| `HF_XET_CACHE` | `hf/xet` | Xet cache |
| `HF_HUB_OFFLINE` | `1` | installed HF offline convention retained from accepted amendment |
| `TRANSFORMERS_OFFLINE` | `1` | Transformers offline convention retained from accepted amendment |
| `TEMP`, `TMP` | `tmp` | Python/native temporary paths |
| `TORCH_HOME` | `torch` | Torch cache |
| `TORCHINDUCTOR_CACHE_DIR` | `torchinductor` | TorchInductor cache |
| `TRITON_CACHE_DIR` | `triton` | Triton cache |
| `CUDA_CACHE_PATH` | `cuda` | CUDA cache |
| `XDG_CACHE_HOME` | `xdg` | XDG-aware dependencies |
| `MPLCONFIGDIR` | `mpl` | Matplotlib cache/config |
| `PYTHONDONTWRITEBYTECODE` | `1` | prohibit bytecode writes |
| `PYTHONPYCACHEPREFIX` | `python/pycache` | defense-in-depth if bytecode suppression is ignored by a subprocess |
| `PYTHONNOUSERSITE` | `1` | prohibit user-site participation |
| `FTLANG_CACHE` | `fastlang` | supported fast-langdetect cache/download target; high-memory download remains forbidden |
| `MINERU_SEAL_OCR_DEBUG` | `0` | disable supported OCR debug output |
| `MINERU_SEAL_OCR_DEBUG_DIR` | `seal_ocr_debug` | containment defense; directory must remain empty when debug is disabled |
| `HOME`, `USERPROFILE` | `profile` | close `Path.home`, `expanduser`, and direct HOME consumers |
| `APPDATA` | `profile/appdata/roaming` | close roaming-appdata defaults |
| `LOCALAPPDATA` | `profile/appdata/local` | close local-appdata defaults |
| `HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`, lowercase equivalents | `http://127.0.0.1:9` | fail closed if an HTTP client ignores application-local model selection |
| `NO_PROXY`, `no_proxy` | empty string | do not permit direct proxy bypass |
| `MINERU_LMDEPLOY_BACKEND` | `pytorch` | unchanged pinned bridge profile |
| `TORCHINDUCTOR_USE_STATIC_CUDA_LAUNCHER` | `0` | unchanged pinned bridge profile |

Before launch, require that TCP and UDP port `127.0.0.1:9` have no listener.
Unset from the child, without reading or recording values:

- `MODELSCOPE_API_TOKEN`, `HF_TOKEN`, `HUGGING_FACE_HUB_TOKEN`,
  `OPENAI_API_KEY`;
- every inherited name containing `TOKEN`, `SECRET`, `PASSWORD`,
  `CREDENTIAL`, or ending in `_KEY` (case-insensitive);
- `PYTHONPATH`, `PYTHONHOME`, `PYTHONSTARTUP`, `PYTHONUSERBASE`,
  `TORCH_COMPILE_DISABLE`.

Do not serialize any inherited environment value. Provenance records only the
closed allowlisted names above, run-root-relative values, and a list of redacted
names removed from the child. Secret values are never read into evidence.

Set the child process working directory exactly to `$volatileRoot\cwd` and
redirect stdout/stderr through the approved generic CLI into structured command
records in memory. Do not retain raw tool-log files. After the run root is
admitted, store only bounded, secret-redacted structured fields in
`evidence/COMMANDS.json`.

### HOME/USERPROFILE safety decision

`HOME` and `USERPROFILE` are not changed in the parent process, user profile,
registry, or machine configuration. They are overridden only in the one pinned
MinerU child and its descendants. This is required because installed ModelScope
uses `Path.home()` and CPython on Windows uses `USERPROFILE` for `expanduser`.
It is safe for this command only because the executable, config, both model
roots, admitted source, engine output, temp/cache roots, and working directory
are all resolved and identity-checked absolute paths before launch; user-site
loading is disabled; credential variables are removed; and any attempt to fall
back to the real profile is rejected by the external mutation audit. If the
child cannot start or resolve the pinned runtime under these overrides, stop;
do not remove an override or repurpose the real profile.

### Offline/network decision

Offline mode is closed at the installed application path, not claimed from a
nonexistent ModelScope flag:

1. `MINERU_MODEL_SOURCE=local` selects the pinned local-root branch before any
   snapshot downloader call.
2. The full manifest/runtime-mirror verification proves every admitted local
   model payload exists before source access.
3. Hugging Face/Transformers offline flags remain set.
4. All HTTP proxy variables and the supported ModelScope endpoint point to an
   asserted-unbound loopback sink; direct proxy bypass is empty.
5. LLM-aided configuration must remain disabled with empty endpoint/model/key,
   and no credential value is inherited by the child.
6. Any observed TCP/UDP endpoint opened by the MinerU process tree, including a
   loopback attempt to port 9, is a rejecting network-attempt finding.

No model download is permitted even inside `$volatileRoot`. If any file appears
under `modelscope/cache`, `hf/hub`, `hf/xet`, or `fastlang`, classify it by
content/purpose before acceptance: a model payload, download part, lock, repo
snapshot, session, cookie, or credential artifact is an immediate stop and
must not be accepted as bridge evidence.

## Read-only runtime verification

The amendment's pre-source Python probe imported Torch and other packages
before cache containment. Replace only that probe with this read-only sequence:

1. Hash the already pinned launcher, Python executable, config, manifest,
   55 model rows, 14-file VLM mirror, installed `METADATA`/`RECORD` files for
   MinerU, ModelScope, ModelScope Hub, Torch, Transformers, lmdeploy, and
   torch-c-dlpack-ext, plus Torch `version.py`; compare with the accepted pinned
   identities/versions.
2. Run only `python.exe -I -B --version`; require `Python 3.12.13`. This command
   imports no project/dependency module and must produce zero filesystem delta.
3. Query the already installed NVIDIA driver with read-only `nvidia-smi`
   name/driver output; require the accepted GPU name. Do not run a Python/Torch
   CUDA probe before the isolated child is launched.
4. Parse the JSON config and distribution metadata as data, without importing
   MinerU, Torch, ModelScope, or Paddle-family modules.
5. Perform the original independent PDF observer only after the complete
   runtime gate is green; then call `ScenarioContract.resolve_source_path()`;
   only then may extraction begin.

This preserves the required order exactly:

```text
runtime_verified -> pdf_observed -> resolve_source_path_passed -> extraction
```

Runtime verification may write only its structured evidence below the admitted
run root. Every toolchain, model, main-runtime, real-profile, AppData, and temp
target remains read-only. An access error, metadata ambiguity, version drift,
or need to import a dependency to decide identity is a stop, not permission to
probe or repair.

## Outside-write and network mutation audit

Resolve the real roots before constructing the child environment. Assign stable
labels; evidence must not substitute the child-overridden values:

```text
main_mineru       = D:\NRI\MinerU
viral_worktree    = D:\NRI\.worktrees\kb-creator-viral
real_userprofile  = parent USERPROFILE
real_appdata      = parent APPDATA
real_localappdata = parent LOCALAPPDATA
real_temp         = parent TEMP
python_base       = home from D:\NRI\MinerU\.venv\pyvenv.cfg
```

Before any runtime probe or source access, record `audit_start_utc` and create a
complete snapshot for every root. After the child and all descendants exit,
record `audit_end_utc` and repeat it. Do not follow reparse points. For each
directory record root label, relative path, type, reparse target if present,
and `LastWriteTimeUtc`. For every regular file record root label, relative path,
bytes, `LastWriteTimeUtc`, and SHA-256. Record missing roots explicitly.

Compare snapshots as exact sets and emit four sorted deltas:

```text
added_paths
removed_paths
metadata_changed_paths
content_changed_paths  # bytes or SHA-256 differs
```

The audit must also retain the MinerU process id, every observed descendant id,
start/end UTC, exit code, and read-only samples of `Get-NetTCPConnection` and
`Get-NetUDPEndpoint` for that process tree from creation until final exit. A
sampling/permission failure, watcher overflow, inaccessible file, disappearing
file during hashing, unresolved reparse point, failure to enumerate a root, or
failure to account for a descendant is itself a stop. The audit may use an
in-process `FileSystemWatcher` only as an additional early signal; the complete
pre/post hash snapshots remain authoritative.

Permitted deltas are exactly:

- under `viral_worktree`, the original packet's three implementation/test
  paths, the original `20260831_step6a/**` run root, and the immutable retry
  receipt;
- within that run root, only its closed schema as corrected below;
- zero delta under `main_mineru`, `real_userprofile`, `real_appdata`,
  `real_localappdata`, `real_temp`, and `python_base`.

Because the real AppData roots are nested under the real profile on this host,
duplicate observations must normalize to one physical path identity. Any
outside delta rejects the attempt even if another process appears to have caused
it; this remediation intentionally does not authorize attribution-based
exceptions. Do not clean or revert the delta. Preserve only allowed run-root
evidence, mark the retry blocked, and return the exact path/hash/timestamp delta
to the orchestrator without exposing file contents or credential values.

## P2 closure: sole run-root cache exception

`engine/mineru_hybrid_high/_bridge_runtime/**` is the sole and exact exception
to the original packet's prohibition on temporary caches inside the run root.
The exception exists only for redirected bridge runtime artifacts created by
the pinned MinerU child. It does not enlarge the original
`engine/mineru_hybrid_high/**` path glob or authorize any additional root.

Every retained regular file under `_bridge_runtime` must have one provenance
row with:

```text
relative_path        # relative to 20260831_step6a, slash-normalized
bytes
sha256
purpose              # closed enum below
producer              # pinned mineru child or approved runtime component
created_or_observed_utc
retention_reason
```

The closed `purpose` enum is:

```text
runtime_cache_evidence
runtime_config_evidence
runtime_temp_evidence
runtime_compilation_evidence
```

Directories may be empty and are inventoried as directories without a SHA.
Files with unknown purpose are forbidden. Model payloads or download parts,
Python bytecode, pytest caches, browser profiles, cookies, credentials, session
files, unrelated/raw logs, source copies, accepted outputs, and files produced
by any process other than the pinned child/approved runtime component remain
forbidden everywhere, including `_bridge_runtime`. A forbidden file is not made
acceptable by hashing or relabeling it.

The complete `_bridge_runtime` inventory is bound into
`evidence/COMMANDS.json` and `RECONSTRUCTED_EN.qa.json`; every row is reconciled
against the full run-root inventory with no missing or extra path.

## Provenance delta

Keep every original provenance field and add this closed object to
`evidence/COMMANDS.json`; bind its canonical SHA-256 from
`SOURCE_IDENTITY.json` and `RECONSTRUCTED_EN.qa.json`:

```json
{
  "bridge_cache_closure": {
    "remediation_receipt_sha256": "<this finalized receipt SHA-256>",
    "model_source_configured": "modelscope",
    "model_source_effective": "local",
    "model_source_override_evidence": "installed MinerU code lines and pinned config",
    "child_environment": [
      {"name": "<allowlisted name>", "value_kind": "literal|volatile_relative|pinned_absolute", "value": "<redacted or relative>"}
    ],
    "removed_sensitive_environment_names": ["<names only; values never read or recorded>"],
    "parent_environment_mutated": false,
    "child_working_directory": "engine/mineru_hybrid_high/_bridge_runtime/cwd",
    "home_userprofile_child_only": true,
    "paddle_runtime_distribution_present": false,
    "paddle_env_names_invented": false,
    "runtime_verification_imported_dependencies": false,
    "offline_controls": {
      "mineru_local_model_source": true,
      "hf_offline": true,
      "transformers_offline": true,
      "modelscope_offline_env_available": false,
      "loopback_sink_unbound_before_launch": true,
      "network_attempts_observed": 0
    },
    "mutation_audit": {
      "audit_start_utc": "<UTC>",
      "audit_end_utc": "<UTC>",
      "root_snapshots": ["<root labels and snapshot SHA-256 identities>"],
      "added_paths": [],
      "removed_paths": [],
      "metadata_changed_paths": [],
      "content_changed_paths": [],
      "outside_allowed_delta_count": 0,
      "audit_complete": true
    },
    "bridge_runtime_inventory": [
      {"relative_path": "<path>", "bytes": 0, "sha256": "<SHA-256>", "purpose": "<closed enum>", "producer": "<identity>", "created_or_observed_utc": "<UTC>", "retention_reason": "<reason>"}
    ]
  }
}
```

Absolute external paths remain diagnostic-only and must not appear in canonical
source identity or digest fields. Environment provenance never contains token,
key, cookie, credential, proxy credential, or other secret values.

## Consolidated stop conditions

All original packet and bridge-amendment stops remain binding. Additionally,
stop before PDF observation if:

- any of the four immutable input hashes, branch, or HEAD differs;
- a fresh independent critic has not accepted this exact finalized receipt with
  no open P0/P1;
- the read-only runtime gate would require a dependency import, setup, install,
  update, copy, assembly, link, download, script invocation, or model write;
- `MINERU_MODEL_SOURCE=local` or either pinned local model root does not resolve
  exactly as installed code/config specifies;
- any required external audit root cannot be completely snapshotted and hashed;
- the child-only HOME/USERPROFILE/AppData isolation changes launcher, config,
  model, source, output, or runtime identity resolution.

Stop during or after launch if:

- a TCP/UDP endpoint is opened or attempted by the MinerU process tree;
- any model/download/session/credential artifact appears in a redirected root;
- any file appears outside `$engineRoot`, or any volatile/relative write escapes
  `$volatileRoot`;
- any external-root path/content/metadata delta is nonzero;
- `_bridge_runtime` contains a file outside the closed purpose enum or lacks a
  path/bytes/SHA/purpose/producer/time/retention row;
- a fourth code/test path, new wrapper, main script, legacy implementation path,
  or changed admission order would be required.

On stop, do not repair, retry, clean, copy, delete, broaden, or publish. Preserve
only already allowed run-root evidence, write the truthful blocker and audit to
the already authorized retry receipt, and return to the orchestrator.

## Readiness and next action

This receipt resolves the engineering specification for critic P1 and P2 only.
The Step 6A retry is **not authorized and not yet technically ready**. It becomes
technically ready only after a fresh independent `gpt-5.5` critic at `medium`
reviews this exact finalized receipt as a narrow process/architecture delta and
returns `accept` with no open P0/P1. The critic must not implement or materially
redesign the closure. Any material change after that review invalidates the
acceptance and requires another fresh review.

Even after acceptance, the original retry packet, three-file allowlist,
admission order, candidate-only result boundary, full QA, mutation audits, and
no-publication/no-Git rules remain unchanged. This receipt does not accept
reconstruction, pages 1-5 modes, `reconstruction_ready`, `MASTER_EN`, or any
release state.

## Engineering receipt

- Files read: applicable `AGENTS.md`, goal governance, canonical plan/context,
  all four immutable Step 6 inputs, pinned MinerU config/metadata/source modules,
  ModelScope/ModelScope Hub cache and download code, CPython help/home behavior,
  fast-langdetect cache/download code, and Paddle-named MinerU OCR code.
- Files changed: only this receipt.
- Extraction/test/runtime import performed: none.
- Blocker: fresh independent acceptance is required before retry.
- Next action: finalize SHA-256 and submit this immutable receipt for the narrow
  independent critic review.
- Elapsed time: unavailable as an exact platform value.
- Token use: unavailable to this contributor; no precision invented.

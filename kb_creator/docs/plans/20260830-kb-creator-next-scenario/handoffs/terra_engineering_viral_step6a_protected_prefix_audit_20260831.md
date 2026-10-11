# Terra engineering receipt — Viral Step 6A protected-prefix audit delta

- Goal id: `20260830-kb-creator-next-scenario`
- Step id: `6-source-reconstruction-step6a-protected-prefix-audit`
- Role: engineering assistance
- Policy model / effort: `gpt-5.6-terra` / `medium`
- Actual platform model / effort: `unavailable` (not exposed to this task)
- Orchestrator policy owner: main chat `gpt-5.6-sol` / `medium`
- Assignment state: `matched` by the UI-visible engineering task; platform runtime unverified
- Scoped override: `none`
- Timestamp: `2026-08-31T01:43:32.8202893+03:00` (`Europe/Moscow`)
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`
- Required branch / HEAD: `codex/kb-creator-viral` / `54607bd3b9362adbb0c4bca64e8751482797f380`
- Observed branch / HEAD: `codex/kb-creator-viral` / `54607bd3b9362adbb0c4bca64e8751482797f380`
- Result: `engineering_delta_complete_retry_still_blocked_pending_fresh_critic`

## Scope and immutable inputs

This receipt closes only the remaining Step 6A protected-prefix-audit P1 and
network-wording P2. It does not run or authorize runtime verification, PDF
observation, extraction, tests, reconstruction acceptance, `MASTER_EN`, any
later publication stage, or release.

| Input | Required SHA-256 | Observed SHA-256 | Result |
|---|---|---|---|
| Bridge amendment: `terra_engineering_viral_step6a_mineru_bridge_20260831.md` | `B41041A90791A5FD2888ECEC0470592F4D87C55BA2A616B3D45FB1584D86A603` | `B41041A90791A5FD2888ECEC0470592F4D87C55BA2A616B3D45FB1584D86A603` | match |
| First bridge review: `gpt55_critic_viral_step6a_mineru_bridge_review_20260831.md` | `508684F9E99DA4C68DCF3D41B3BABB05721EABF2500F6D3B8BEA8D0496BABBE5` | `508684F9E99DA4C68DCF3D41B3BABB05721EABF2500F6D3B8BEA8D0496BABBE5` | match |
| Cache-closure delta: `terra_engineering_viral_step6a_cache_closure_20260831.md` | `C84E0352B748643618E84A814BA555A5B681038FF98644C493526D3D5252C802` | `C84E0352B748643618E84A814BA555A5B681038FF98644C493526D3D5252C802` | match |
| Second reject receipt: `gpt55_critic_viral_step6a_cache_closure_review_20260831.md` | `15B3E311F1ADA607C45F8FB4A9464B8068E7C0425159F04F7F49A2C01A070BFB` | `15B3E311F1ADA607C45F8FB4A9464B8068E7C0425159F04F7F49A2C01A070BFB` | match |

## Exact supersession rule

This receipt **supersedes, revokes, and replaces** the cache-closure receipt's
entire `Outside-write and network mutation audit` section, including its
requirements to recursively enumerate/hash `real_userprofile`, `real_appdata`,
`real_localappdata`, `real_temp`, or `python_base`, to demand zero delta across
those full roots, and to stop on inability to enumerate those full roots. Those
requirements are no longer operative and must not be combined with this delta.

This receipt also supersedes every claim in the bridge/cache-closure receipts
that absence of sampled `Get-NetTCPConnection` or `Get-NetUDPEndpoint` rows is
authoritative proof that no connection was attempted, and every requirement to
treat unavailable/permission-limited endpoint sampling as proof failure. The
replacement is the best-effort observation rule below.

All other accepted controls remain operative without expansion: exact local
model resolution with `MINERU_MODEL_SOURCE=local`; installed-code-supported
`MODELSCOPE_CACHE` and `MODELSCOPE_HOME`; no invented unsupported environment
names; child-only `HOME`, `USERPROFILE`, `APPDATA`, and `LOCALAPPDATA`;
sensitive-environment removal without reading values; offline flags and
loopback endpoint/proxy containment; parent-environment immutability;
`engine/mineru_hybrid_high/_bridge_runtime/**` as the sole fully inventoried
run-root cache exception with its closed purpose enum; the original three-file
implementation/test allowlist and closed `20260831_step6a/**` run root; and the
admission order
`runtime_verified -> pdf_observed -> resolve_source_path_passed -> extraction`.

## Installed-code/default-path evidence boundary

The protected set below is derived only from the already installed stack and
the critic's required examples:

- `modelscope_hub/constants.py` declares defaults `~/.cache/modelscope` and
  `~/.modelscope`, while the latter can contain credentials and sessions;
- `huggingface_hub/constants.py` derives `~/.cache/huggingface/{hub,assets,xet}`
  and can place token material at the Hugging Face home root;
- `torch/hub.py` derives `~/.cache/torch` when `TORCH_HOME` and
  `XDG_CACHE_HOME` are absent;
- `fast_langdetect/ft_detect/infer.py` declares the platform-insensitive literal
  `/tmp/fasttext-langdetect`; the child uses supported `FTLANG_CACHE` instead;
- CPython `tempfile.py` chooses `TMPDIR`, then `TEMP`, then `TMP`; the child sets
  `TEMP` and `TMP` to `_bridge_runtime/tmp`;
- CPython's ordinary bytecode default is module-adjacent `__pycache__`; the
  child sets `PYTHONDONTWRITEBYTECODE=1` and redirects defense-in-depth through
  `PYTHONPYCACHEPREFIX` to `_bridge_runtime/python/pycache`, so only the exact
  manifest-bound installed module files need a real Python-location audit;
- `D:\NRI\MinerU\.venv\pyvenv.cfg` binds the Python base under real roaming
  AppData, but the accepted runtime identity gate already names exact launcher,
  executable, config, distribution `METADATA`/`RECORD`, source/module, model,
  and mirror files;
- no installed Matplotlib package was found in this pinned venv, so
  `MPLCONFIGDIR` remains containment defense only, not evidence for scanning a
  real-profile Matplotlib default.

No evidence above authorizes reading an unrelated parent tree.

## Bounded protected-prefix table

Resolve `real_userprofile` once from the parent environment **before** building
the child map. Join only the literal descendants shown below, normalize them to
absolute paths, and require each normalized result to remain below the stated
parent. Resolving a listed path must not enumerate any parent directory.

Common snapshot rules for recursively audited prefixes: do not follow symbolic
links, junctions, mount points, or other reparse points; a reparse object inside
the named prefix is recorded by path, type, attributes, target text when the OS
returns it without traversal, and metadata, but is never followed. Record only
slash-normalized path, type, bytes, `LastWriteTimeUtc`, attributes, and SHA-256
for regular files. Never capture file contents. Before and after snapshots are
compared as exact sets of added, removed, metadata-changed, and content-changed
paths. Any nonzero delta **inside the stated auditable scope** is a stop. No
delta outside a named scope is asserted, inferred, or required.

| Protected prefix / set | Existence handling | Bounded metadata/hash scope | Privacy exclusion and comparison |
|---|---|---|---|
| `real_userprofile\.cache\modelscope` | Before: record `missing` or directory identity. A file or reparse object at the prefix is a pre-launch stop. After: repeat; missing/present transition is a delta. | If present as a real directory, recursively snapshot only this prefix. | Do not leave this prefix or capture contents. Any in-scope delta stops the attempt. |
| `real_userprofile\.modelscope` | Record only prefix `missing`/present, object type, attributes, and root `LastWriteTimeUtc`; a reparse object is a pre-launch stop. Repeat after. | **No child enumeration and no file hashing.** Compare only the root sentinel/metadata. | Never open or enumerate `credentials/**`, cookies, tokens, sessions, user records, or any other child. A root sentinel/metadata delta stops; undetectable modification below an existing sensitive child is a recorded privacy residual, not permission to inspect it. |
| `real_userprofile\.cache\huggingface\hub` | Same missing/directory/reparse handling as ModelScope cache. | Recursively snapshot only this exact prefix. | No content capture; any in-scope delta stops. |
| `real_userprofile\.cache\huggingface\assets` | Same missing/directory/reparse handling as ModelScope cache. | Recursively snapshot only this exact prefix. | No content capture; any in-scope delta stops. |
| `real_userprofile\.cache\huggingface\xet` | Same missing/directory/reparse handling as ModelScope cache. | Recursively snapshot only this exact prefix. | No content capture; any in-scope delta stops. |
| `real_userprofile\.cache\huggingface` root sentinel | Record only root `missing`/present, type, attributes, and `LastWriteTimeUtc`; repeat after. | No enumeration other than the three exact non-secret children above. | Never open/hash `token`, `stored_tokens`, credential, session, or unknown sibling paths. Root delta stops; hidden mutation inside an excluded existing sibling is a privacy residual. |
| `real_userprofile\.cache\torch` | Same missing/directory/reparse handling as ModelScope cache. | Recursively snapshot only this exact prefix. | No content capture; any in-scope delta stops. |
| Exact pinned runtime/model/code identity set | Every already required path must exist as its required type before launch and after exit; drift/missing is a stop. | Hash only the previously accepted explicit paths and manifest rows: pinned launcher/Python/config, 55 model rows, 14-file VLM mirror, named distribution `METADATA`/`RECORD` files and the exact installed source/module files used for model/cache decisions. For a distribution, validate only paths named by its accepted `RECORD`; do not recursively enumerate `python_base`, `Lib`, all `site-packages`, `APPDATA`, or `D:\NRI\MinerU`. | Never open credential/session/browser/profile files. Compare exact path/type/bytes/time/SHA rows before/after; any delta in this named set stops. This is the sole Python-base/AppData audit surface. |

The generic seam must deduplicate physical identities if an exact pinned file
also falls beneath another named prefix. It emits one comparison row with all
applicable labels, never broadens to a common parent.

### Defaults intentionally not promoted to broad scans

- **Real temp:** CPython proves only an environment-selected temp directory and
  does not prove a stable child filename/prefix under the parent's real temp.
  Because the child sets both `TEMP` and `TMP` to `_bridge_runtime/tmp`, no real
  temp prefix is audited. The residual is that native code ignoring the child
  environment could write an unknown real-temp name; closing that residual
  would require separate evidence, not a recursive real-temp scan.
- **FastText/fast-langdetect:** the installed literal
  `/tmp/fasttext-langdetect` is not a proven real Windows host prefix for this
  isolated child. Supported `FTLANG_CACHE` containment remains mandatory; no
  drive-root `/tmp` tree is scanned. High-memory model download remains
  forbidden.
- **Matplotlib:** the package is absent from the pinned venv. Retain
  `MPLCONFIGDIR` containment, but do not invent or scan a real-profile default.
- **TorchInductor, Triton, CUDA, roaming/local AppData:** their child cache
  overrides remain mandatory. Where this installed-code review did not prove an
  exact unredirected host prefix, retain child containment and record the
  residual; do not scan `real_appdata`, `real_localappdata`, the Python-base
  parent, or any general profile tree.

These residuals are explicit and do not silently reactivate the revoked broad
audit. If future installed-code evidence proves another exact default, the
orchestrator must obtain a reviewed amendment naming that literal child prefix;
the executor may not improvise a parent-root scan.

## Executable audit pseudocode for the existing generic seam

This algorithm is to be implemented inside the original allowed generic seam,
not in a wrapper, fourth code path, helper script, or runtime directory:

```python
# Python 3.12 pseudocode; uses only stdlib and the existing generic seam.
SAFE_RECURSIVE = [
    real_userprofile / ".cache/modelscope",
    real_userprofile / ".cache/huggingface/hub",
    real_userprofile / ".cache/huggingface/assets",
    real_userprofile / ".cache/huggingface/xet",
    real_userprofile / ".cache/torch",
]
ROOT_SENTINELS = [
    real_userprofile / ".modelscope",
    real_userprofile / ".cache/huggingface",
]

def lexical_child(parent, literal_child):
    # abspath/normcase only; do not enumerate parent and do not resolve reparse targets
    p = os.path.abspath(os.path.join(parent, literal_child))
    if os.path.commonpath([os.path.normcase(parent), os.path.normcase(p)]) != os.path.normcase(parent):
        raise Stop("protected prefix escaped expected parent")
    return p

def sentinel(path):
    if not os.path.lexists(path):
        return {"state": "missing"}
    st = os.stat(path, follow_symlinks=False)
    return {"state": "present", "type": object_type(st),
            "attributes": st.st_file_attributes, "mtime_ns": st.st_mtime_ns}

def bounded_tree(prefix):
    head = sentinel(prefix)
    if head["state"] == "missing":
        return {".": head}
    if head["type"] != "directory" or os.path.islink(prefix) or os.path.isjunction(prefix):
        raise Stop("protected prefix is not a real directory")
    rows = {".": head}
    stack = [prefix]
    while stack:
        current = stack.pop()
        for entry in os.scandir(current):
            rel = slash_relative(entry.path, prefix)
            st = entry.stat(follow_symlinks=False)
            if entry.is_symlink() or os.path.isjunction(entry.path) or is_other_reparse(st):
                rows[rel] = reparse_metadata_only(entry.path, st)  # never follow/open target
            elif entry.is_dir(follow_symlinks=False):
                rows[rel] = metadata_only(st)
                stack.append(entry.path)
            elif entry.is_file(follow_symlinks=False):
                rows[rel] = metadata_plus_streamed_sha256(entry.path, st)
            else:
                rows[rel] = metadata_only(st)
    return rows

before = {
    "trees": {label(p): bounded_tree(p) for p in SAFE_RECURSIVE},
    "sentinels": {label(p): sentinel(p) for p in ROOT_SENTINELS},
    "pinned": snapshot_exact_manifest_bound_files(PINNED_ACCEPTED_FILE_SET),
}
# Existing seam then performs only its already approved launch/admission sequence.
after = same_snapshot_functions_and_exact_same_path_sets()
deltas = exact_row_set_comparison(before, after)
if deltas:
    raise Stop("delta inside named protected prefix/set", secret_free_rows(deltas))
```

An access/hash race **inside a named non-sensitive recursive prefix or exact
pinned file set** is a stop because that bounded evidence is incomplete. An
excluded sensitive child is never opened to avoid the race. No failure outside
these exact scopes is generated because no other tree is read.

## P2 network observation: best-effort residual only

Keep all substantive containment controls: resolve and verify local models
before source access; require `MINERU_MODEL_SOURCE=local`; remove sensitive
child environment names without reading values; keep supported HF offline
flags; set ModelScope endpoint and all HTTP(S)/ALL proxy variants to an
asserted-unbound `127.0.0.1:9`; keep direct proxy bypass empty; require LLM-aided
configuration disabled; and reject any model/download/session/credential
artifact in `_bridge_runtime`.

`Get-NetTCPConnection` and `Get-NetUDPEndpoint` sampling for the pinned child
PID and observed descendants is **best-effort observation**, not enforcement
and not authoritative proof of network denial. Record command availability,
permission/result status, sample times, observed process ids, and any matching
rows. An observed endpoint or loopback attempt is a stop. No observed row does
not prove no short-lived attempt occurred. Sampling unavailable, permission
limited, or incomplete is recorded as a residual; it does not require admin,
firewall mutation, ETW/netsh installation, a new tool, or a new implementation
path, and it must not be reported as an authoritative no-network result.

The accepted loopback/offline/proxy/local-model controls make ordinary remote
resolution fail closed, but they are containment rather than a process-level
network-deny boundary. Residual risk remains that a dependency could bypass
those controls and a short-lived attempt could evade endpoint-table sampling.
This receipt neither requires nor claims firewall/admin/tool-install closure.

## Consolidated stop and readiness decision

All original packet and accepted bridge/cache-closure stops remain binding
except the expressly revoked broad-root audit and authoritative-network wording.
For this delta specifically, stop if an immutable input, branch, or HEAD drifts;
a named auditable prefix is an unexpected file/reparse object; an exact bounded
snapshot cannot complete; a before/after delta occurs inside a named protected
scope; local model/config/runtime identity fails; child containment would have
to be removed; an endpoint is observed; or any original allowlist, admission
order, run-root, candidate-only, or no-publication boundary would be broadened.

On stop, do not repair, retry, clean, revert, copy, delete, install, or broaden.
Return a secret-free blocker using only the already authorized retry receipt and
allowed run-root evidence.

The Step 6A retry remains **unauthorized**. A fresh independent `gpt-5.5`
critic at `medium` must review this exact finalized receipt as the narrow P1/P2
delta and return `accept` with no open P0/P1 before any runtime verification,
source observation, or extraction. Any material change to this receipt after
review invalidates that decision and requires another fresh review.

## Engineering receipt

- Files checked: applicable `AGENTS.md`; canonical goal governance, plan, and
  context; the four SHA-bound inputs above; and read-only installed-code/default
  path evidence for ModelScope, Hugging Face, Torch, fast-langdetect, CPython
  temp handling, the venv Python base, and Matplotlib package presence.
- Files changed: only this receipt.
- Runtime import, runtime verification, source observation, extraction, or test
  performed: none.
- Blocker: fresh independent critic acceptance of this exact SHA-bound receipt.
- Next action: compute this receipt's SHA-256 and submit it for a fresh narrow
  independent critic review; do not dispatch the Step 6A retry yet.
- Elapsed time: unavailable as an exact platform value.
- Token use: unavailable to this contributor; no precision invented.

## Detached receipt SHA-256

Compute after final write.

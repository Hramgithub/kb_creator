# Terra engineering amendment — Viral Step 6A source-copy runtime delta

- Goal id: `20260830-kb-creator-next-scenario`
- Step id: `6-source-reconstruction-step6a-source-copy-runtime-delta`
- Role / policy effort: `gpt-5.6-terra` engineering assistance / `medium`
- Actual platform model / effort: `unavailable`
- Orchestrator policy owner: `gpt-5.6-sol` / `medium`
- Assignment state: `platform-unverified`; scoped override: `none`
- Worktree / required branch and HEAD:
  `D:\NRI\.worktrees\kb-creator-viral` / `codex/kb-creator-viral` /
  `54607bd3b9362adbb0c4bca64e8751482797f380`
- Result: `amendment_ready_pending_user_cleanup_authority_and_fresh_independent_accept`
- Permitted changed file: this receipt only

## Decision

**No already-installed, supported no-copy direct-file MinerU 3.4.4 route was
found.** The pinned public `mineru` entry point is `mineru.cli.client:main`.
For `--api-url` omitted (the accepted local profile), `client.run_orchestrated_cli`
starts `LocalAPIServer`; `submit_task` creates `UploadAsset(path=<source>)`; and
`api_client.submit_parse_task_sync` sends it as multipart. The local FastAPI
`/tasks` route accepts uploaded files, and `fast_api.save_upload_files` writes
each upload in chunks to `<task output>/uploads/<normalized name>`. This is
the exact admitted-PDF copy recorded by the latest blocker receipt.

The installed public entry points are `mineru`, `mineru-api`, `mineru-router`,
model download, VLM-server and Gradio commands. Their documented/request
surface is upload based; no local-path task field or no-copy switch is exposed.
`mineru.cli.common.do_parse` is an internal bytes API, not a supported public
direct-file protocol; adopting it would require a materially new invocation
and result/provenance contract, so it is rejected for this narrow retry.

Accordingly, this amendment selects one minimal route: a **single, strictly
bounded, runtime-only transport-copy exception** for the already pinned local
MinerU CLI/API protocol. It does not weaken immutability of the external PDF:
the original remains the only admitted source, and the transport object is
never a source authority, input to the generic reconstructor, candidate asset,
accepted artifact, publication artifact, or promotable evidence.

Execution remains blocked until both gates below are satisfied:

1. the user supplies explicit authority for the specified automatic
   cleanup/deletion behaviour; and
2. a fresh independent `gpt-5.5` critic at `medium` accepts this exact receipt
   with no open P0/P1.

## Immutable bindings and read-only findings

| Binding | SHA-256 / state |
|---|---|
| Original Step 6 packet | `011CF87FFA0B0DACC85559DEF601A5FD9EED0755F86EB877C263CF2F2D8FABBC` |
| MinerU bridge amendment | `B41041A90791A5FD2888ECEC0470592F4D87C55BA2A616B3D45FB1584D86A603` |
| Cache closure | `C84E0352B748643618E84A814BA555A5B681038FF98644C493526D3D5252C802` |
| Protected-prefix delta | `C8A7C8A7AA81113F557A3642328D88878F12BFFC1A89B441F34DB74E572E8DBB` |
| Protected-prefix accept | `458F60956C5918A9B505A89686B2745216089708B26A4878BA70E1E1F6C2FF93` |
| Loopback/output delta | `12EA488E8732FF8523DC996725A915B43BD628BF5AC7506A2A02F74AAA437857` |
| Loopback/output accept | `D7EB6A6FDBBE97469EFD930A4B93E4ED74E961C4F89FAA032D06E8186A5BA61F` |
| Latest blocked loopback receipt | `B06D632C055048B05716BD05BDEA59F7499D03BE79B39346D6FC8D3105609A5C` |
| External admitted source | `20718150` bytes / `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05` |

The immutable predecessor roots are:

- `kb_creator/working/viral/source_reconstruction/20260831_step6a/`;
- `kb_creator/working/viral/source_reconstruction/20260831_step6a_loopback_retry/`.

They are failure evidence only. The executor must hash/inventory them only as
needed for the stated bindings; it must not write, rename, clean, delete,
reuse, or copy any predecessor artifact into the successor.

Installed-code evidence was inspected read-only at `D:\NRI\MinerU`:

- `src/mineru/cli/client.py:705-723` builds upload assets from the `--path`
  file; `:910-1034` starts a local API when `--api-url` is absent.
- `src/mineru/cli/api_client.py:467-523` creates
  `TemporaryDirectory(prefix="mineru-api-client-")`, starts `fast_api` and
  uses its `output` child; `:864-895` posts every `UploadAsset` as multipart.
- `src/mineru/cli/fast_api.py:747-775` writes each `UploadFile` to its
  `uploads` directory. The observed
  `_bridge_runtime/tmp/mineru-api-client-*/output/*/uploads/Call_of_Cthulhu_Viral.pdf`
  therefore has a direct code-path explanation, not an unexplained cache.
- The direct CLI also downloads a result ZIP and extracts it, so replacing it
  with an internal helper would be a new unreviewed integration path.
- The pinned model/cache/profile controls from accepted bridge/cache/protected
  prefix amendments remain unchanged: local models, hybrid-engine/high,
  formulas/tables enabled, child-only isolated environment, bounded protected
  prefixes, no main MinerU script invocation, and best-effort network evidence.

## Exact successor and closed writes

The only possible successor is:

```text
run id:   20260831_step6a_source_copy_exception_retry
run root: D:\NRI\.worktrees\kb-creator-viral\kb_creator\working\viral\source_reconstruction\20260831_step6a_source_copy_exception_retry
```

It must be absent before the task begins, be resolved as an absolute path,
contain no reparse point at any component, and refuse overwrite. The only
writes outside it are the existing three-file seam and the new executor receipt:

```text
kb_creator/scripts/scenario_source_reconstruction.py
kb_creator/scripts/reconstruct_scenario_source.py
kb_creator/tests/test_scenario_source_reconstruction.py
kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/
  luna_executor_viral_source_reconstruction_step6a_source_copy_exception_retry_20260831.md
```

No fourth implementation/test/helper/wrapper/module, no MinerU source edit,
no main-runtime script, no contract/accepted/production/publication/canonical
state edit, and no Git action is allowed. The successor inherits the original
closed run-root schema, with the already accepted sole cache exception
`engine/mineru_hybrid_high/_bridge_runtime/**`, plus the specific transport
object below. All normal runtime artifacts retain the accepted closed-purpose
inventory requirements.

## Transport-copy exception

The exception is valid only when every property below is observed before any
candidate result is considered:

| Property | Mandatory value |
|---|---|
| Type | regular file; `.pdf`; never a link, junction, or reparse point |
| Count | exactly one live transport copy for the one permitted MinerU launch |
| Path class | `engine/mineru_hybrid_high/_bridge_runtime/tmp/mineru-api-client-*/output/*/uploads/Call_of_Cthulhu_Viral.pdf` relative to the successor root |
| Bytes | exactly `20718150` |
| SHA-256 | exactly `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05` |
| Producer | pinned `D:\NRI\MinerU\.venv\Scripts\mineru.exe` local API server, proved by recorded process tree and API-client temporary root |
| Purpose | `runtime_source_transport_copy` only |
| Lifetime | created after source admission; retained only while the pinned CLI/API request/result transaction and its child tree require it; automatic runtime cleanup may begin only after result transfer/terminal stop and complete process-tree exit |
| Promotion | prohibited: it cannot appear in `RECONSTRUCTED_EN`, page/asset/content provenance, candidate inventory as a source asset, QA outputs, accepted inputs, production, or publication |

The initial source read/admission stays unchanged: runtime verification,
independent observer, then `ScenarioContract.resolve_source_path()`, then
`pdfinfo`; no transport copy may be created before those gates pass.

Immediately after its creation is observable, the executor records the
path-relative row, type, bytes, SHA-256, producer PID lineage, creation UTC,
source identity binding, and purpose in successor `evidence/COMMANDS.json`.
It must additionally record a negative full successor inventory assertion:
no second file with the admitted source hash/byte count, no other PDF under
`_bridge_runtime`, no copied source outside the one path class, and no source
bytes in any output/provenance field except this redacted transport row.

Any mismatch, duplicate, escaped path, unknown producer, hash failure,
inability to inventory before cleanup, source transport copy outside this path,
or source-copy appearance in a final/accepted/publication path is an immediate
`blocked` stop. Do not invoke a fallback, retry, source substitute, or direct
internal library path.

### Cleanup and retention authority — explicitly separate

The installed `LocalAPIServer` owns a `TemporaryDirectory` and calls cleanup on
its normal `stop()` path. That makes removal of the temporary source transport
copy a deletion, even though it is not the immutable original PDF.

- **New user authority is required before execution** to permit the one
  runtime-owned automatic removal of the exactly bound transport-copy path
  after the result is transferred or the process tree has stopped. The future
  executor must not treat this engineering receipt or critic acceptance as
  deletion authority.
- Until that explicit authority exists, no successor task may launch MinerU.
- The two existing immutable failure roots, including the existing copied PDF,
  have **no cleanup authority**. Their deletion or any retention-policy change
  needs a separate explicit user instruction after exact path/type/hash
  verification.
- If automatic cleanup fails, or a stop occurs before a complete transport row
  is written, retain the entire successor root as immutable failure evidence;
  do not manually delete any residual copy. A later cleanup request remains a
  separate user-authorized destructive action.

## Exact runtime invocation and controls

The executor uses no main `verify.ps1`, `run-hybrid.ps1`, `initialize.ps1`,
setup, install, update, API/router service, firewall/admin operation, or
external server. It must reuse every accepted bridge/cache/protected-prefix/
loopback child-only environment and audit unchanged, including:

- `MINERU_MODEL_SOURCE=local` and the pinned read-only main config/model roots;
- child-only ModelScope/HF/Torch/temp/profile/cache values below the successor
  `_bridge_runtime` root; sensitive names stripped without reading values;
- `HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY` and lowercase counterparts plus
  `MODELSCOPE_ENDPOINT` set to `http://127.0.0.1:9` with port 9 unbound;
- `NO_PROXY` and `no_proxy` exactly `127.0.0.1,localhost,::1`;
- an absolute resolved child CWD below `_bridge_runtime/cwd`; and
- output set once, as the exact absolute successor engine root, never relative.

The only permitted engine argv is:

```text
D:\NRI\MinerU\.venv\Scripts\mineru.exe
  --path <admitted external Viral PDF>
  --output <absolute successor>\engine\mineru_hybrid_high
  --backend hybrid-engine --effort high --formula True --table True
```

There is one launch maximum, no `--start`/`--end`, no `--api-url`, and no
alternative backend. This preserves the installed local models and the required
hybrid/high/formula/table behavior. Parent environment mutation and shell
interpolation remain forbidden.

## Wildcard listener finding

The accepted local API client path does **not** specify a wildcard bind:
`api_client._build_local_api_server_cli_args()` forcibly passes
`--host 127.0.0.1`, and the client base URL is `http://127.0.0.1:<ephemeral>`.
The installed MinerU source search finds wildcard host handling only in the
separate user-facing `mineru-api`/router server options; neither is part of the
permitted argv. A local address recorded as `0.0.0.0:<port>` means an IPv4
wildcard listener (all local interfaces), not an alias for loopback. If a
process remains bound that way, it may be reachable from LAN interfaces subject
to host firewall/routing; it is not compatible with a strict loopback-only
listener condition merely because the client connected through `127.0.0.1`.

The predecessor evidence does not bind a retained PID/command line to that
observed wildcard row. Installed code therefore supports this limited,
evidence-honest conclusion: the required local API is loopback-bound, but the
specific wildcard descendant owner is **unattributed** (possibly a dependency
or separately spawned service), not proven to be `fast_api`. It must not be
silently accepted as harmless.

For the successor, process/endpoint audit must capture each root and descendant
PID, PPID, executable/command-line identity where readable, start/end UTC, and
all sampled TCP/UDP rows. A non-loopback listener or endpoint — including
`0.0.0.0`, `::`, LAN/private/public address, or a listener not proven as the
pinned local `127.0.0.1` API — is a stop. This rule is stricter than the
accepted proxy loopback exception: `NO_PROXY` permits only health-check client
traffic to `127.0.0.1`, `localhost`, or `::1`; it does not authorize a wildcard
server bind. Endpoint sampling remains best-effort evidence, not firewall proof.

On any stop after a process starts, first stop only the verified descendant
tree rooted at the recorded pinned MinerU launch, using its recorded process
group/PID lineage; wait and re-sample until no member remains. Do not stop an
unrelated process merely because it shares a port or executable name. Failure
to attribute, stop, or prove tree exit is itself `blocked`; preserve evidence
and request operator intervention rather than broad termination.

## Implementation, test, and audit requirements

The existing three-file seam may add only generic, test-covered machinery to:

1. build the literal argv/environment without shell interpolation;
2. reject source-copy artifacts except the exact one-row exception;
3. capture/validate the transport row before candidate processing;
4. enforce the result-transfer/cleanup authority gate; and
5. apply the strict listener/process-tree stop policy.

Focused tests must remain bytecode-disabled and add deterministic fixtures for:

- zero, duplicate, wrong-name, wrong-byte-count, wrong-hash, symlink/reparse,
  outside-root, and post-cleanup-uninventoried transport-copy rejection;
- a single correct transport row being evidence-only and absent from all
  source/asset/final promotion sets;
- exact argv (`hybrid-engine`, `high`, formula/table `True`, one absolute
  output, no API URL/range flags), child-only environment, and parent unchanged;
- listener classification: `127.0.0.1` acceptable only for the recorded local
  API; `0.0.0.0`, `::`, external endpoint, unknown listener, or orphan PID
  rejects; and
- no automatic/manual cleanup path runs without an explicit execution-time
  cleanup-authority flag supplied by the orchestrator task packet.

Run only the accepted focused ScenarioContract/reconstruction/Innsmouth checks
and repository-wide diagnostic with `-B` and `-p no:cacheprovider`; preserve
the known 15 missing-`kb_creator.pdf_raw` collection baseline. No `py_compile`,
MinerU verify/run/initialize script, model/runtime test, GPU probe, source
probe outside the prescribed admission sequence, or second MinerU launch is
permitted by this amendment itself.

Before/after audit preserves all pre-existing worktree Git status and binds:

- branch/HEAD; all listed immutable receipt hashes; installed launcher/config/
  model identities; predecessor-root inventories; and successor absence;
- only the closed successor root, three permitted implementation/test paths,
  and named executor receipt as task delta;
- bounded protected-prefix/main-MinerU zero-delta rules from accepted deltas;
- process tree and best-effort endpoint samples; and
- complete successor inventory with the sole controlled transport row and no
  retained source copy after authorized normal cleanup.

## Stop conditions and blocker disposition

The `source_copy_inside_bridge_runtime` blocker is **not eliminated**; it is
specified as a separately authorized runtime transport exception. It remains
`open_procedurally` until user cleanup authority and a fresh critic `accept`
exist, and `open_runtime` until a successor produces compliant evidence.

Stop without repair, cleanup, retry, or scope expansion if the worktree/HEAD,
hash bindings, preflight/admission order, local-model/cache/protected-prefix
gate, source identity, exact argv, one-launch rule, output containment,
transport-row controls, process-tree identity, endpoint policy, test baseline,
or any no-publication/no-Git restriction fails. A future candidate may only be
`candidate_needs_review` or `blocked`; this amendment accepts neither content
nor reconstruction.

## Required fresh critic and exact next UI task

A fresh independent `gpt-5.5` critic at `medium` must review this exact,
finalized receipt as a `process/architecture` delta, declare independence, and
return `accept` with no P0/P1. The critic receipt must be:

`kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_step6a_source_copy_runtime_delta_review_20260831.md`

Only after that review **and explicit user authority for the described automatic
runtime cleanup** may the orchestrator create this UI-visible executor task:

> Continue only the bounded Viral Step 6A candidate in worktree
> `D:\NRI\.worktrees\kb-creator-viral`, required branch/HEAD
> `codex/kb-creator-viral` / `54607bd3b9362adbb0c4bca64e8751482797f380`.
> Read and SHA-verify the original Step 6 packet, bridge/cache/protected-prefix/
> loopback deltas and reviews, this accepted source-copy delta and its critic
> receipt, and both immutable predecessor roots/receipts. Do not write, clean,
> reuse, rename, or delete either predecessor root. Use only successor run id
> `20260831_step6a_source_copy_exception_retry` and its exact root; only the
> three generic seam/test files and
> `handoffs/luna_executor_viral_source_reconstruction_step6a_source_copy_exception_retry_20260831.md`
> may be written outside it. Apply every accepted local-model, cache/profile,
> protected-prefix, loopback, absolute-output, source-admission, no-history,
> no-publication and no-Git control. Launch exactly once with the pinned direct
> MinerU argv (`hybrid-engine`, `high`, formula/table true). The only allowed
> source duplicate is one regular PDF under the exact API-client `uploads`
> path class, with exactly 20,718,150 bytes and SHA-256
> `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05`;
> record it only as `runtime_source_transport_copy`, never promote it, and use
> only the separately supplied user authority for its automatic runtime cleanup.
> Stop on a duplicate/mismatch/escape/unknown producer, any wildcard or
> non-loopback listener, unknown/orphan process, unauthorized cleanup, or any
> other original/amended stop. Stop only the verified MinerU descendant tree;
> do not kill unrelated processes. Do not use a main MinerU script, API/router
> service, firewall/admin action, install, GPU/model probe, py_compile,
> fallback, second launch, or destructive cleanup. Return only truthful
> `candidate_needs_review` or `blocked` evidence; no `MASTER_EN`, contract,
> accepted, production, publication, stage, commit, push, or remote operation.

## Engineering receipt

- Read: applicable `AGENTS.md`; governance; canonical plan/context; original
  packet; all bridge/cache/protected-prefix/loopback amendments and reviews;
  predecessor receipt and two immutable failure roots; installed MinerU 3.4.4
  entry-point, client, API-client, FastAPI upload, router, output and VLM code.
- Read-only checks: required branch/HEAD matched; latest receipt SHA-256 matched
  `B06D632C055048B05716BD05BDEA59F7499D03BE79B39346D6FC8D3105609A5C`;
  the exact multipart upload write path was established from code and evidence.
- No MinerU/PDF/runtime/GPU/model/test execution, source processing, cleanup,
  implementation, installation, network/firewall/admin operation, canonical
  state edit, staging, commit, push, or remote operation occurred.
- Changed: this receipt only.
- Next action: obtain explicit user cleanup authority, then fresh independent
  critic acceptance before any successor execution.
- Elapsed time: unavailable. Token use: unavailable.

## Detached SHA-256

Compute after final write; do not edit this receipt to embed its own hash.

# Terra engineering amendment — Viral Step 6A loopback and absolute-output delta

- Goal id: `20260830-kb-creator-next-scenario`
- Step id: `6-source-reconstruction-step6a-loopback-output-delta`
- Role: engineering assistance
- Policy model / effort: `gpt-5.6-terra` / `medium`
- Actual platform model / effort: `unavailable` (not exposed as a verifiable runtime value)
- Orchestrator policy owner: main chat `gpt-5.6-sol` / `medium`
- Assignment state: `platform-unverified`; policy role honored
- Scoped override: `none`
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`
- Required and observed branch / HEAD: `codex/kb-creator-viral` / `54607bd3b9362adbb0c4bca64e8751482797f380`
- Timestamp: `2026-08-31` (`Europe/Moscow`)
- Result: `engineering_amendment_complete_retry_blocked_pending_fresh_independent_critic`
- Files changed: only this receipt

## Purpose and bounded decision

This amendment closes exactly the two new execution defects recorded by the
latest continuation receipt:

1. the pinned MinerU CLI starts and health-checks its own IPv4 loopback HTTP
   API, but the accepted child environment sent that health check to the
   external-network proxy sink because `NO_PROXY` / `no_proxy` were empty;
2. the accepted launch passed a relative `--output` while the child working
   directory was isolated, so MinerU created an empty nested relative-output
   directory chain below `_bridge_runtime/cwd`.

This amendment changes only the child proxy-bypass values, the absolute output
construction/validation boundary, the retry run id, and the tests/evidence
needed to prove those two corrections. It does not broaden or weaken the
accepted original Step 6 packet, direct-runtime bridge, cache closure, or
protected-prefix audit.

The following controls remain binding without reinterpretation:

- direct pinned `D:\NRI\MinerU\.venv\Scripts\mineru.exe` only;
- no main `verify.ps1`, `run-hybrid.ps1`, `initialize.ps1`, `setup.ps1`,
  install, update, repair, model assembly, copy, symlink, junction, wrapper, or
  fourth implementation/test path;
- `MINERU_MODEL_SOURCE=local`, pinned local model roots, supported
  ModelScope/Hugging Face/profile/cache/temp controls, child-only profile and
  working directory, sensitive-environment removal without reading values;
- every HTTP(S)/ALL proxy variant remains the unbound sink
  `http://127.0.0.1:9`; supported offline controls remain set; external traffic
  is not authorized;
- bounded protected-prefix audit; no broad profile/AppData/temp scan;
- `engine/mineru_hybrid_high/_bridge_runtime/**` remains the sole cache
  exception and every retained regular file remains strictly inventoried;
- no source copy, historical translation/config authority, contract mutation,
  accepted/production/publication work, `MASTER_EN`, stage, commit, push, or
  remote operation;
- the known 15 missing `kb_creator.pdf_raw` collection errors remain a separate
  repository-wide baseline and are neither repaired nor called green here.

## Immutable authorities and evidence

All required identities were read-only verified before this amendment was
written.

| Artifact | Required and observed SHA-256 |
|---|---|
| Original Step 6 packet: `terra_engineering_viral_source_reconstruction_packet_20260831.md` | `011CF87FFA0B0DACC85559DEF601A5FD9EED0755F86EB877C263CF2F2D8FABBC` |
| Original blocked executor receipt: `luna_executor_viral_source_reconstruction_20260831.md` | `31A50C84CF8EDC3F90EE1DED5643C019AEA47C00C0C0F31D466E13AD18E79B44` |
| MinerU bridge amendment: `terra_engineering_viral_step6a_mineru_bridge_20260831.md` | `B41041A90791A5FD2888ECEC0470592F4D87C55BA2A616B3D45FB1584D86A603` |
| Bridge reject review: `gpt55_critic_viral_step6a_mineru_bridge_review_20260831.md` | `508684F9E99DA4C68DCF3D41B3BABB05721EABF2500F6D3B8BEA8D0496BABBE5` |
| Cache-closure amendment: `terra_engineering_viral_step6a_cache_closure_20260831.md` | `C84E0352B748643618E84A814BA555A5B681038FF98644C493526D3D5252C802` |
| Cache-closure reject review: `gpt55_critic_viral_step6a_cache_closure_review_20260831.md` | `15B3E311F1ADA607C45F8FB4A9464B8068E7C0425159F04F7F49A2C01A070BFB` |
| Protected-prefix amendment: `terra_engineering_viral_step6a_protected_prefix_audit_20260831.md` | `C8A7C8A7AA81113F557A3642328D88878F12BFFC1A89B441F34DB74E572E8DBB` |
| Accepted protected-prefix review: `gpt55_critic_viral_step6a_protected_prefix_review_20260831.md` | `458F60956C5918A9B505A89686B2745216089708B26A4878BA70E1E1F6C2FF93` |
| Prior retry receipt: `luna_executor_viral_source_reconstruction_step6a_retry_20260831.md` | `413FB3B7AB48FBE3CE874A8AC87299AC44BE98CF9EC538C5B1678AFEB38B1DF9` |
| Latest continuation receipt: `luna_executor_viral_source_reconstruction_step6a_continuation_20260831.md` | `CFAB4FD677E78FA6F896575FC56A294E19FBA4C7F6448BEA096F2301E74AA810` |

The latest continuation hash matches the required value. Its blocker class is
`mineru_bridge_local_api_healthcheck_failure`; its earliest failing layer is
the direct pinned executable orchestration. It proves source admission but does
not accept or authorize reuse of runtime output.

The existing blocked run root is immutable predecessor/failure evidence:

`kb_creator/working/viral/source_reconstruction/20260831_step6a/`

Its three regular files are:

| Relative path | Bytes | SHA-256 |
|---|---:|---|
| `SCENARIO_CONTRACT.json` | `4067` | `C2EF2DD143E304F59C8973E8DB82CF83B094BC35DDA37BB2299686E1FE6DA194` |
| `SOURCE_IDENTITY.json` | `78948` | `4B8234024F80F8792C84C43A0AEBA939950B97FEA44551F7A996B74807B08B67` |
| `evidence/COMMANDS.json` | `42937` | `942AA26F1BE698B37B83D1FF0815261A20E8D4EB9724FB0A04A09854061CA365` |

The predecessor also contains the empty nested relative-output directory chain
below:

`engine/mineru_hybrid_high/_bridge_runtime/cwd/kb_creator/working/viral/source_reconstruction/20260831_step6a/engine/mineru_hybrid_high/`

That chain and the entire predecessor root must not be deleted, cleaned,
renamed, moved, reused, overwritten, or written by the retry. Directory
emptiness is evidence and is not permission to clean it.

## Installed MinerU 3.4.4 loopback evidence

The following was inspected read-only from the installed environment. No
MinerU module, PDF, model, or runtime was executed.

| Installed file | Bytes | SHA-256 |
|---|---:|---|
| `D:\NRI\MinerU\src\mineru\cli\api_client.py` | `36222` | `61E126DDB2D5B604E76747DA774AD6AEB41A207B87232E0ACA8ED693ADCF640D` |
| `D:\NRI\MinerU\src\mineru\cli\client.py` | `38974` | `0300DDD0CAA868DF21EB3EF9B03D86DD61B7AEE196000C87A2DBA9EAAD4F7DAE` |
| `D:\NRI\MinerU\src\mineru\cli\output_paths.py` | `1511` | `BD9FB9696BE5BC4D015F9A3F070DAA4450CDA1D577C724F9EC6A70CF432AE311` |
| installed HTTPX `httpx/_utils.py` | `8285` | `FD355EA802AFC4990A1DDCFB74579BE2CD0B66A41781E1645D281F88704AFF5A` |
| installed HTTPX `httpx/_client.py` | `65714` | `C43F941BAEFE58C91E96D00039E1868FE719D91453026D7DB1647194563BFF8D` |
| installed HTTPX `METADATA` | `7052` | `FEBB9B0F8F3E80D57C8199C304F35C4336E8581D1D18D7983C92766B82793B25` |

The installed metadata declares MinerU `3.4.4` and HTTPX `0.28.1`. The three
named MinerU source files have no Git status delta in the main checkout.

Exact code behavior:

1. `api_client.py:651-655` creates an `AF_INET` / `SOCK_STREAM` socket, binds
   `("127.0.0.1", 0)`, listens, and returns the OS-selected ephemeral port.
2. `api_client.py:355-366` strips caller-supplied host/port values and forces
   the spawned API CLI args to `--host 127.0.0.1 --port <resolved_port>`.
3. `api_client.py:480-485` constructs the orchestration base URL exactly as
   `http://127.0.0.1:<resolved_port>`.
4. `api_client.py:761-802` calls `<base_url>/health` repeatedly through the
   supplied HTTPX client until healthy or timeout.
5. `client.py:944-954` constructs `httpx.AsyncClient(...)` without
   `trust_env=False`, starts the local API when `--api-url` is absent, and uses
   that same client for the health check. HTTPX therefore honors the child
   proxy environment.
6. HTTPX `0.28.1` `get_environment_proxies()` reads HTTP, HTTPS, ALL, and
   NO_PROXY from the environment. Exact IPv4 hosts become `all://<host>` direct
   mounts, exact IPv6 hosts become `all://[<host>]`, and exact `localhost`
   becomes a direct mount. `NO_PROXY=*` would disable all proxies and is
   forbidden here.
7. HTTPX builds scheme/all proxy mounts plus the more-specific direct
   NO_PROXY mounts. Therefore the exact `127.0.0.1` health URL bypasses both
   `HTTP_PROXY` and `ALL_PROXY`; external HTTP/HTTPS hosts retain the sink.

The local API path uses IPv4 `127.0.0.1` only. It does not construct
`localhost`, `127.0.0.2`, an arbitrary `127/8` address, `[::1]`, or another IPv6
URL. `localhost` and `::1` are nevertheless included as exact defensive
loopback spellings for dependencies/descendants; no wildcard, suffix, subnet,
CIDR, LAN address, or external hostname is bypassed.

## Exact child-process proxy environment delta

Replace only the two empty bypass values in the accepted child-only environment:

| Name | Old value | Required successor value |
|---|---|---|
| `NO_PROXY` | empty | `127.0.0.1,localhost,::1` |
| `no_proxy` | empty | `127.0.0.1,localhost,::1` |

The exact successor value is byte-for-byte the comma-separated ASCII string
above, without spaces, wildcard, scheme, port, CIDR, or trailing comma. Both
case variants must be present with the same value so Windows/stdlib/third-party
case handling cannot select an empty inherited alternative.

All six proxy variables remain exactly:

```text
HTTP_PROXY=http://127.0.0.1:9
HTTPS_PROXY=http://127.0.0.1:9
ALL_PROXY=http://127.0.0.1:9
http_proxy=http://127.0.0.1:9
https_proxy=http://127.0.0.1:9
all_proxy=http://127.0.0.1:9
```

`MODELSCOPE_ENDPOINT` also remains `http://127.0.0.1:9`. The new loopback
bypass does not make that endpoint external: if erroneously used, it connects
directly to the same asserted-unbound loopback sink and fails. Before launch,
the executor must again prove TCP and UDP `127.0.0.1:9` have no listener.

All other accepted child environment entries and sensitive-name removal are
unchanged. The parent environment must remain unchanged. Environment evidence
records only the allowlisted names and literal/run-root-relative value kinds;
it never records inherited values or secret contents.

### External-network containment and honest residual

This delta authorizes only direct loopback connections whose URL host is
exactly `127.0.0.1`, `localhost`, or `::1`. It does not authorize direct access
to any other address or hostname. External HTTP/HTTPS and generic proxy-aware
traffic continues to hit the unbound `127.0.0.1:9` sink; local model selection,
offline flags, disabled LLM-aided configuration, stripped credentials, pinned
model/config identities, redirected caches, and forbidden download artifacts
remain operative.

Best-effort endpoint sampling remains evidence, not enforcement and not proof
of complete network denial. The expected local API listener/health traffic is
now an allowed observation only when all of these are true:

- address is loopback and URL host is one of the three exact bypass tokens;
- for the MinerU-owned API proven by installed code, bind/connect is
  `127.0.0.1:<ephemeral>` and the port is not `9`;
- owning process is the pinned MinerU child or an observed managed descendant;
- remote address is loopback; no non-loopback local/remote endpoint appears;
- the API process exits through normal MinerU orchestration and no orphan
  remains after the pinned child exits.

An observed non-loopback endpoint, DNS/external attempt, listener on a
non-loopback interface, loopback port `9` listener, model/download/session/
credential artifact, or proxy removal/change is a stop. Sampling unavailable,
permission-limited, or incomplete remains a recorded residual and does not
authorize firewall/admin changes, ETW/netsh installation, a new tool, or broad
network access. No authoritative no-network claim may be made.

## Exact successor run id and closed write allowlist

The sole successor run id is:

`20260831_step6a_loopback_retry`

The sole successor run root is:

`D:\NRI\.worktrees\kb-creator-viral\kb_creator\working\viral\source_reconstruction\20260831_step6a_loopback_retry\`

It was absent at amendment time and must be absent at executor start. No other
successor name, suffix, timestamp, retry number, temporary root, or reused root
is authorized.

The executor write allowlist is exactly:

1. `kb_creator/scripts/scenario_source_reconstruction.py`;
2. `kb_creator/scripts/reconstruct_scenario_source.py`;
3. `kb_creator/tests/test_scenario_source_reconstruction.py`;
4. `kb_creator/working/viral/source_reconstruction/20260831_step6a_loopback_retry/**`;
5. governance receipt
   `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/luna_executor_viral_source_reconstruction_step6a_loopback_retry_20260831.md`.

Item 5 is not a fourth implementation/test path. The three seam/test files may
receive only the loopback/output/run-id implementation and focused tests needed
by this amendment; unrelated reconstruction redesign is forbidden.

The successor root preserves the original Step 6 closed schema exactly,
including the same top-level files/directories and the sole accepted cache
exception:

```text
SCENARIO_CONTRACT.json
SOURCE_IDENTITY.json
RECONSTRUCTED_EN.md
RECONSTRUCTED_EN.qa.json
pages/page-001.md .. pages/page-124.md
evidence/PAGE_PROVENANCE.json
evidence/CONTENT_PROVENANCE.json
evidence/ASSET_PROVENANCE.json
evidence/ENTITY_INVENTORY.json
evidence/HANDOUT_INVENTORY.json
evidence/NAVIGATION_INVENTORY.json
evidence/CONTENT_MODE_REVIEW.json
evidence/REFERENCE_ONLY_AUDIT.json
evidence/BLOCKER_LEDGER.json
evidence/COMMANDS.json
engine/mineru_hybrid_high/**
renders/source/page-001.png .. renders/source/page-124.png
renders/contact_sheets/**
crops/**
assets/source/**
assets/derived/**
ocr/**
```

`engine/mineru_hybrid_high/_bridge_runtime/**` remains the sole cache exception
with the already accepted closed purpose enum and inventory requirements. No
new schema path is authorized.

## Absolute successor path construction and output containment

The successor CLI commands must receive the fully resolved absolute successor
run root. The generic seam must reject a relative run root for this retry; it
must not silently anchor it to the child CWD.

The executor command setup is exactly:

```powershell
$repoRoot = (git rev-parse --show-toplevel).Trim()
if ($repoRoot -ne 'D:/NRI/.worktrees/kb-creator-viral' -and $repoRoot -ne 'D:\NRI\.worktrees\kb-creator-viral') {
  throw "Unexpected repository root: $repoRoot"
}
$successorRunRoot = [System.IO.Path]::GetFullPath((Join-Path $repoRoot 'kb_creator\working\viral\source_reconstruction\20260831_step6a_loopback_retry'))
$expectedRunRoot = [System.IO.Path]::GetFullPath('D:\NRI\.worktrees\kb-creator-viral\kb_creator\working\viral\source_reconstruction\20260831_step6a_loopback_retry')
if (-not [StringComparer]::OrdinalIgnoreCase.Equals($successorRunRoot, $expectedRunRoot)) {
  throw "Successor run root mismatch"
}
if (Test-Path -LiteralPath $successorRunRoot) {
  throw "Successor run root already exists"
}
```

For preflight, the run root is absent and is validated lexically against the
exact expected absolute path before creation. For build, it must exist as a
real directory. Before any `_child_environment` directory creation or
`subprocess.Popen`, the generic seam must perform all of these checks:

1. `run_root.is_absolute()` is true;
2. the resolved existing `run_root` equals the exact successor path above under
   Windows case-insensitive comparison;
3. `engineRoot` is constructed only as
   `(run_root / "engine/mineru_hybrid_high").resolve(strict=True)`;
4. `engineRoot` is absolute, equals the exact expected successor engine path,
   and `os.path.commonpath([run_root, engineRoot])` equals `run_root` after
   normalized-case comparison;
5. `volatileRoot` and child CWD resolve strictly below that exact engine root;
6. the successor run root, engine root, volatile root, and child CWD are real
   directories, not symlinks, junctions, mount points, or other reparse-point
   escapes;
7. the argv contains exactly one `--output`, its next element is exactly the
   fully resolved absolute `engineRoot`, and no relative, alternate,
   normalized-different, or second output argument exists;
8. the admitted source path is the already resolved absolute path returned by
   `resolve_source_path()`; contract data never supplies an executable or
   output path.

The exact successor engine path passed to MinerU is:

`D:\NRI\.worktrees\kb-creator-viral\kb_creator\working\viral\source_reconstruction\20260831_step6a_loopback_retry\engine\mineru_hybrid_high`

The exact child working directory remains:

`D:\NRI\.worktrees\kb-creator-viral\kb_creator\working\viral\source_reconstruction\20260831_step6a_loopback_retry\engine\mineru_hybrid_high\_bridge_runtime\cwd`

The output path must not be recomputed relative to that CWD. A relative output,
path traversal, symlink/junction/reparse escape, common-path mismatch, duplicate
`--output`, or any output outside the exact successor engine root is a
pre-launch stop. No child process may start and no fallback path may be tried.

The installed MinerU evidence makes this required rather than cosmetic:
`client.py:1048-1054` accepts `--output` as a Click `Path` without resolving it;
`client.py:937` calls `output_dir.mkdir(...)`; and downstream output helpers
join under that value. A relative value is therefore relative to the isolated
child CWD.

## Predecessor evidence versus mandatory successor evidence

The old run root is read-only predecessor evidence only. The successor must
bind, not copy, these four predecessor identities:

- continuation receipt SHA-256
  `CFAB4FD677E78FA6F896575FC56A294E19FBA4C7F6448BEA096F2301E74AA810`;
- predecessor `SCENARIO_CONTRACT.json` SHA-256
  `C2EF2DD143E304F59C8973E8DB82CF83B094BC35DDA37BB2299686E1FE6DA194`;
- predecessor `SOURCE_IDENTITY.json` SHA-256
  `4B8234024F80F8792C84C43A0AEBA939950B97FEA44551F7A996B74807B08B67`;
- predecessor `evidence/COMMANDS.json` SHA-256
  `942AA26F1BE698B37B83D1FF0815261A20E8D4EB9724FB0A04A09854061CA365`.

Bind them through exact, closed additions to the existing evidence objects,
not through new top-level schema files:

- in successor `SOURCE_IDENTITY.json`, the existing `packet_hashes` map gains
  exact keys `loopback_output_delta`, `loopback_output_delta_review`,
  `predecessor_continuation_receipt`, `predecessor_contract_snapshot`,
  `predecessor_source_identity`, and `predecessor_commands`;
- in successor `evidence/COMMANDS.json`, existing
  `bridge_cache_closure` gains exact fields `predecessor_run_id`,
  `successor_run_id`, `loopback_bypass_hosts`,
  `loopback_output_delta_receipt_sha256`,
  `loopback_output_delta_review_sha256`, and
  `absolute_engine_output_run_relative`.

No predecessor JSON content, observer rows, command rows, protected-prefix
snapshot, or diagnostic path is copied and relabeled as current evidence.

The following must be freshly re-observed and re-emitted in the successor:

1. full worktree/packet/amendment/review gate;
2. complete read-only runtime/model/code identity gate, including the newly
   pinned MinerU/HTTPX source identities in this amendment;
3. fresh bounded protected-prefix `before` snapshot;
4. fresh independent PDF observation of encryption, all 124 page media boxes,
   and rotations;
5. fresh `ScenarioContract.resolve_source_path()` using those observed values,
   including current source bytes and SHA-256;
6. fresh `pdfinfo` diagnostic after contract resolution;
7. fresh canonical `SCENARIO_CONTRACT.json` emitted from the currently loaded
   accepted contract and required to match the predecessor/current contract
   identity;
8. fresh `SOURCE_IDENTITY.json` and `evidence/COMMANDS.json` in the same closed
   schemas, with successor-relative identities and current command results;
9. fresh post-child protected-prefix snapshot/delta, endpoint observations,
   engine/runtime inventory, and all later candidate evidence if extraction
   succeeds.

### Fail-closed rerun decision

`runtime gate`, `source observer`, `resolve_source_path()`, and `pdfinfo` all
must rerun. There is no justified exception. The successor changes the child
environment and output path, must be independently self-contained, and cannot
inherit a current-state claim from a failed immutable root. Reusing the old
admission JSON, copying it, or skipping any step is a stop.

The mandatory order remains exactly:

```text
runtime_verified
-> protected_prefix_before_captured
-> pdf_observed
-> resolve_source_path_passed
-> pdfinfo_diagnostic
-> absolute_output_validated
-> mineru_child_launched
```

## Exact retry commands

No MinerU/PDF/runtime command is run by this engineering task. After fresh
critic acceptance only, the bounded executor runs from the exact worktree:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
python -B -m pytest kb_creator/tests/test_scenario_source_reconstruction.py -q -p no:cacheprovider
python -B -m pytest kb_creator/tests/test_scenario_contract.py kb_creator/tests/test_scenario_source_reconstruction.py -q -p no:cacheprovider

python -B kb_creator/scripts/reconstruct_scenario_source.py preflight --contract kb_creator/contracts/viral.json --source "D:\яндекс\Yandex.Disk\НРИ\1_Зов Ктулху\english\7th Edition Call of Cthulhu\Adventures\Call_of_Cthulhu_Viral.pdf" --run-root "$successorRunRoot"

python -B kb_creator/scripts/reconstruct_scenario_source.py build --contract kb_creator/contracts/viral.json --source "D:\яндекс\Yandex.Disk\НРИ\1_Зов Ктулху\english\7th Edition Call of Cthulhu\Adventures\Call_of_Cthulhu_Viral.pdf" --run-root "$successorRunRoot"

python -B kb_creator/scripts/reconstruct_scenario_source.py verify --contract kb_creator/contracts/viral.json --source "D:\яндекс\Yandex.Disk\НРИ\1_Зов Ктулху\english\7th Edition Call of Cthulhu\Adventures\Call_of_Cthulhu_Viral.pdf" --run-root "$successorRunRoot"
```

The generic seam, not PowerShell shell interpolation or contract data,
constructs the direct pinned MinerU argv as an argument list. Its invariant
profile remains:

```text
<pinned mineru.exe>
--path <freshly admitted absolute source>
--output D:\NRI\.worktrees\kb-creator-viral\kb_creator\working\viral\source_reconstruction\20260831_step6a_loopback_retry\engine\mineru_hybrid_high
--backend hybrid-engine
--effort high
--formula True
--table True
```

No `--api-url`, `--start`, `--end`, alternate backend, wrapper, or second
launch is authorized.

After a successful build/verify, run the unchanged remaining original gates:

```powershell
python -B -m pytest kb_creator/tests/test_build_innsmouth_reconstructed_en.py -q -p no:cacheprovider
python -B -m pytest kb_creator/tests -q -p no:cacheprovider
rg --files kb_creator/scripts kb_creator/contracts kb_creator/tests | rg '(^|[\\/])(build|freeze)_viral_[^\\/]*\.py$'
rg -n --glob '*.py' --glob '*.json' 'translator[\\/]config[\\/]viral\.package\.json|viral\.package\.json' kb_creator/scripts kb_creator/contracts kb_creator/tests
```

The repository-wide suite remains diagnostic only. It must reproduce exactly
the known 15 missing-`kb_creator.pdf_raw` collection errors and introduce no
new class/count drift; it is not a green Step 6A gate.

`py_compile` is forbidden. Test/cache execution must retain `python -B`,
`PYTHONDONTWRITEBYTECODE=1`, and `-p no:cacheprovider`.

## Required focused tests

The existing focused module remains the only test path. Add exact tests for:

1. `_child_environment` emits both `NO_PROXY` and `no_proxy` exactly as
   `127.0.0.1,localhost,::1`;
2. all six HTTP(S)/ALL proxy variants and `MODELSCOPE_ENDPOINT` remain exactly
   `http://127.0.0.1:9`, and neither bypass variable contains `*`, CIDR, scheme,
   port, LAN address, or external hostname;
3. the accepted child environment continues to be child-only and preserves all
   prior local-model/cache/profile/offline/sensitive-removal controls;
4. the exact installed MinerU/HTTPX code identities used by this amendment are
   pinned by the runtime gate; drift stops before PDF observation;
5. successor preflight rejects a relative run root and any run id other than
   `20260831_step6a_loopback_retry` before creating it;
6. build rejects a relative run root, missing root, alternate root, symlink,
   junction, mount/reparse path, or normalized path outside the exact worktree;
7. engine/volatile/CWD resolution yields the exact absolute paths specified
   above and remains below the exact successor root;
8. argv has exactly one `--output` and its value is the exact fully resolved
   absolute engine path;
9. relative `--output`, `..` escape, absolute outside-root output, duplicate
   `--output`, or output changed after validation raises `ReconstructionStop`
   before `_child_environment`, directory creation beyond the already admitted
   successor schema, or `subprocess.Popen`;
10. a mocked launch sees list argv, exact absolute source/output, exact child
    CWD, exact loopback bypass, and no shell interpolation;
11. the predecessor root is rejected as a run root and is never a write target;
12. successor evidence uses the original closed top-level schema, emits the
    exact predecessor hash bindings, and does not copy predecessor admission
    rows as current observations;
13. failed loopback health or engine exit remains a single-run stop: no
    automatic second launch, fallback proxy mutation, alternate output, or
    cleanup occurs;
14. the pre-existing console-encoding test and all prior 22 focused tests
    remain green without bytecode/cache files.

Tests must mock process launch and filesystem escape cases; they must not start
MinerU, open the Viral PDF, probe models/GPU, access the network, or create a
second run root. Any test requiring a fourth file is a stop.

## Mutation audits

Before implementation, before preflight, after preflight, after child exit, and
at task end, record the original worktree audit:

```powershell
git rev-parse --show-toplevel
git branch --show-current
git rev-parse HEAD
git status --short --branch -uall
git diff --check
git diff --name-only
git ls-files --others --exclude-standard
```

Preserve every pre-existing status line. Directly inventory ignored files.
The task delta may contain only the three seam/test paths, exact successor run
root, and exact executor receipt.

Before and after, compute a deterministic predecessor-root manifest containing
every relative path and type plus bytes/SHA-256 for each regular file. Require
the same path/type/file-hash set and the exact three file hashes recorded above.
Do not use directory timestamps as authority; do not touch the tree to audit
it. Any path addition/removal/type change/file hash drift is a stop.

Repeat all accepted main MinerU exact-file/model/config/manifest/runtime mirror
and bounded protected-prefix audits, now including the exact MinerU/HTTPX files
pinned by this amendment. Main `D:\NRI\MinerU` permitted delta remains zero on
the named bridge/runtime surface; broader pre-existing main dirt remains
diagnostic and must be preserved.

At task end verify:

- old `20260831_step6a/**` manifest exactly unchanged;
- new writes exist only under the exact successor schema and receipt/seam
  allowlist;
- no `.pyc`, `__pycache__` addition, pytest cache, raw log, source copy,
  model/download/session/credential artifact, browser profile, or alternate
  output chain exists;
- no source, contract, accepted, production, historical translation,
  canonical plan/context/status/release, Innsmouth, or unrelated path changed;
- no stage, commit, push, branch move, remote mutation, install, admin/firewall
  action, cleanup, or process kill occurred.

## Consolidated stop conditions

Every original packet and accepted amendment stop remains binding except the
two values/path rules explicitly replaced here. Additionally stop without
repair, retry, cleanup, fallback, or broadening if:

- this amendment or its fresh critic acceptance is absent or any bound hash,
  branch, HEAD, code/runtime/model identity, or predecessor manifest differs;
- the successor root exists before preflight, differs from the exact id/path,
  or is relative/reparse/escaped;
- runtime gate, protected-prefix baseline, PDF observer,
  `resolve_source_path()`, or `pdfinfo` is skipped, reused, copied, reordered,
  or disagrees;
- either bypass variable differs from
  `127.0.0.1,localhost,::1`, a wildcard/CIDR/external bypass appears, any proxy
  sink changes, or port `9` has a listener;
- output is not the exact resolved absolute successor engine path, is relative,
  contains an escape, resolves through a reparse point, differs after argv
  construction, or is duplicated;
- MinerU binds/listens on a non-loopback interface, observes a non-loopback
  endpoint, attempts an external/DNS connection, creates a forbidden artifact,
  fails health/extraction, or leaves an orphan process;
- any file/directory appears in the old blocked root or outside the exact new
  run-root schema/three-file/receipt allowlist;
- the executor would need firewall/admin privileges, installation, a new tool,
  wrapper, main script, fourth code/test path, source copy, historical
  translation, contract/publication mutation, cleanup, second launch, or Git
  mutation;
- focused/ScenarioContract/Innsmouth tests fail or the repository-wide
  diagnostic differs from the separate known 15-error baseline.

On stop, preserve the successor's already allowed evidence, mark it `blocked`,
write the exact secret-free blocker/mutation audit to the authorized executor
receipt, and return to the orchestrator. Do not delete either run root and do
not attempt another successor id.

## Blocker disposition and critic gate

Engineering disposition:

- loopback root cause: `specified_closed` by exact host-only proxy bypass;
- relative-output root cause: `specified_closed` by exact absolute successor
  path construction and pre-launch containment checks;
- blocker `mineru_bridge_local_api_healthcheck_failure`: remains
  `open_procedurally` until a fresh independent critic accepts this exact
  finalized amendment and a later bounded executor produces truthful runtime
  evidence.

This amendment does not accept a reconstruction candidate, source content,
page/content modes, `reconstruction_ready`, `MASTER_EN`, or publication.

A fresh independent `gpt-5.5` critic at `medium` must review this receipt as a
narrow `process/architecture` delta. The critic must not implement or materially
redesign it. Retry is authorized only if the critic returns `accept` with no
open P0/P1. Any material change after review invalidates that decision and
requires another fresh review.

The critic receipt name must be:

`kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_step6a_loopback_output_delta_review_20260831.md`

## Exact next UI-visible executor task

After critic acceptance and orchestrator integration, create one UI-visible
task named **`Viral Step 6A loopback retry`** using bounded executor role
`gpt-5.6-luna` at `medium`.

Exact task prompt:

> Continue only the bounded Viral Step 6A candidate in worktree
> `D:\NRI\.worktrees\kb-creator-viral`, required branch/HEAD
> `codex/kb-creator-viral` /
> `54607bd3b9362adbb0c4bca64e8751482797f380`. Fully read and SHA-verify the
> accepted original Step 6 packet, MinerU bridge/cache/protected-prefix
> amendments and reviews, prior retry/continuation receipts, and the freshly
> accepted loopback/output delta plus critic receipt. Preserve the existing
> `20260831_step6a` root and latest blocked receipt as immutable failure
> evidence: do not delete, clean, reuse, overwrite, rename, or write them. Use
> only successor run id/root `20260831_step6a_loopback_retry` /
> `D:\NRI\.worktrees\kb-creator-viral\kb_creator\working\viral\source_reconstruction\20260831_step6a_loopback_retry`.
> Keep the three implementation/test paths and executor receipt
> `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/luna_executor_viral_source_reconstruction_step6a_loopback_retry_20260831.md`
> as the exact write allowlist outside that root. Rerun the complete read-only
> runtime/model/code/protected-prefix gate, independent PDF observer,
> `ScenarioContract.resolve_source_path()`, and `pdfinfo`; never reuse prior
> admission evidence. Start only the direct pinned MinerU executable with
> child-only `NO_PROXY` and `no_proxy` exactly
> `127.0.0.1,localhost,::1`; keep every HTTP(S)/ALL proxy and
> `MODELSCOPE_ENDPOINT` on the unbound `http://127.0.0.1:9` sink. Pass
> `--output` only as the fully resolved exact absolute successor engine path;
> reject relative, duplicate, escaped, or reparse-point output before launch.
> Preserve all accepted local-model/cache/profile/offline/sensitive-env,
> `_bridge_runtime` inventory, bounded audit, best-effort-network-residual,
> no-source-copy/no-history/no-publication/no-Git controls. Do not invoke main
> verify/run/initialize/setup scripts, install, use firewall/admin, run
> `py_compile`, clean either run root, or launch a fallback/second attempt.
> Return only truthful `candidate_needs_review` or `blocked` evidence; no
> `MASTER_EN`, contract, accepted, production, or publication work.

The UI task completion condition is the original Step 6A candidate boundary,
using the exact successor root and amended controls. After the orchestrator
captures and verifies the receipt, it archives the UI task. A later bounded QA
and independent acceptance remain required; the next action is not
`MASTER_EN`.

## Engineering contributor receipt

- Files read: applicable `AGENTS.md`; NRI goal governance; full canonical
  plan/context; accepted original Step 6 packet; all MinerU bridge/cache/
  protected-prefix amendments and reviews; prior retry and latest continuation
  receipts; current three-file seam/tests; exact immutable predecessor run-root
  inventory and closed JSON top-level schemas; installed MinerU 3.4.4 local API,
  client/output-path code; installed HTTPX 0.28.1 proxy parsing/client code.
- Read-only verification: required branch/HEAD matched; latest continuation
  receipt matched expected SHA-256; installed code proves IPv4
  `127.0.0.1:<ephemeral>` bind/base URL and environment-trusting health client;
  installed output option remains unresolved relative `Path`; successor/receipt
  paths were absent before this write.
- Files changed: only this receipt.
- MinerU/PDF/runtime/test/source execution: none.
- Source, old run root, implementation/tests, contract, accepted/production,
  plan/context/status/release, Git index/branch/remote: unchanged by this task.
- Blocker: fresh independent critic acceptance is required before retry.
- Next action: finalize SHA-256, obtain the named fresh critic review, and only
  after `accept` with no P0/P1 dispatch the exact UI-visible bounded retry.
- Elapsed time: unavailable as an exact platform value.
- Token use: unavailable to this contributor; no precision invented.

## Detached receipt SHA-256

Compute after final write; do not edit this receipt to embed its own hash.

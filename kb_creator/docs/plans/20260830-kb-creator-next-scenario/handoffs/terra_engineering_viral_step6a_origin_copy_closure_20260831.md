# Terra engineering amendment — Viral Step 6A origin-copy closure

- Goal id: `20260830-kb-creator-next-scenario`
- Step id: `6-source-reconstruction-step6a-origin-copy-closure`
- Role / policy effort: engineering assistance, `gpt-5.6-terra` / `medium`
- Actual platform model / effort: `unavailable`
- Orchestrator policy owner: `gpt-5.6-sol` / `medium`
- Assignment state: `platform-unverified`; scoped override: `none`
- Worktree / required branch and HEAD: `D:\NRI\.worktrees\kb-creator-viral` / `codex/kb-creator-viral` / `54607bd3b9362adbb0c4bca64e8751482797f380`
- Result: `amendment_ready_pending_fresh_independent_accept`
- Permitted changed file: this receipt only

## Decision

The installed, pinned public MinerU `3.4.4` CLI cannot suppress
`return_original_file` while retaining the accepted direct `mineru` launch,
one-launch limit, local temporary API, `hybrid-engine`, `high`, formula and
table settings.  The public Click options expose no such switch; instead,
`client.py:683-700` unconditionally submits `return_original_file=True` and
`response_format_zip=True`.  Disabling it requires a wrapper, a source edit, or
a materially different internal/API/main-script integration boundary, all
forbidden for this narrow retry.

The successor therefore admits exactly two, and only two, named byte-identical
runtime byproducts.  Neither is an admitted source, reconstruction input,
asset, provenance authority, accepted artifact, or publication artifact.  The
external PDF remains the sole source authority.  This amendment does **not**
authorize execution: a fresh independent critic must accept it with no P0/P1
before execution or before any cleanup authority is requested.

## Fixed bindings and immutable scope

| Binding | SHA-256 / state |
|---|---|
| Original Step 6 packet | `011CF87FFA0B0DACC85559DEF601A5FD9EED0755F86EB877C263CF2F2D8FABBC` |
| MinerU bridge | `B41041A90791A5FD2888ECEC0470592F4D87C55BA2A616B3D45FB1584D86A603` |
| Cache closure | `C84E0352B748643618E84A814BA555A5B681038FF98644C493526D3D5252C802` |
| Protected-prefix delta / accept | `C8A7C8A7AA81113F557A3642328D88878F12BFFC1A89B441F34DB74E572E8DBB` / `458F60956C5918A9B505A89686B2745216089708B26A4878BA70E1E1F6C2FF93` |
| Loopback/output delta / accept | `12EA488E8732FF8523DC996725A915B43BD628BF5AC7506A2A02F74AAA437857` / `D7EB6A6FDBBE97469EFD930A4B93E4ED74E961C4F89FAA032D06E8186A5BA61F` |
| Rejected source-copy delta / critic reject | `611741B1032E425521555327AF6DED9CADCE44299CCA5F41C04CA321D2DB0907` / `B7E0CC9C037F7AE9B07F6E0B697BE6F9F0FB5AC6A4BF5E547F4C165A49F960E0` |
| Latest blocked retry receipt | `B06D632C055048B05716BD05BDEA59F7499D03BE79B39346D6FC8D3105609A5C` |
| Sole admitted external source | `20718150` bytes / `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05` |

The immutable failure roots remain permanently out of scope:

- `kb_creator/working/viral/source_reconstruction/20260831_step6a/`;
- `kb_creator/working/viral/source_reconstruction/20260831_step6a_loopback_retry/`.

They must not be deleted, cleaned, renamed, reused, or written.  This includes
the recorded upload copy in the second root.  No retention-policy change for
either root is implied or authorized here.

The only possible new run is `20260831_step6a_origin_copy_exception_retry` at
the correspondingly named, initially absent closed run root.  All original and
accepted bridge/cache/protected-prefix/loopback controls remain unchanged,
including one pinned direct launch, exact absolute output, local models,
child-only isolated profile/cache, and candidate-only/no-publication/no-Git
boundaries.

## Installed-code conclusion and lineage

Read-only MinerU evidence is pinned to these inspected files:

| File | SHA-256 |
|---|---|
| `client.py` | `0300DDD0CAA868DF21EB3EF9B03D86DD61B7AEE196000C87A2DBA9EAAD4F7DAE` |
| `api_client.py` | `61E126DDB2D5B604E76747DA774AD6AEB41A207B87232E0ACA8ED693ADCF640D` |
| `fast_api.py` | `231C3137B036E58D2F44B9D61325B6B64DDACC496C73136C6E3AE40C8FADFD87` |
| `common.py` | `A46FE0AD824EE4DD4D70581832DBD97133FAF8F81713E0FCAB90931186230881` |

`mineru = mineru.cli.client:main` constructs multipart `UploadAsset` objects;
the loopback FastAPI child writes them to `uploads/` (`fast_api.py:747-805`).
It reads the bytes, calls the hybrid parser with `f_dump_orig_pdf=True`
(`fast_api.py:822-851`), and `common.py:300-305, 751-754` writes the origin
PDF.  The API packages it when producing the ZIP (`fast_api.py:590-604`), and
the outer CLI extracts that ZIP to `--output` (`client.py:855-863`).  The exact
hybrid parse directory is derived by `output_paths.py` as
`<output>/<pdf_stem>/hybrid_auto`.

## Closed two-copy model

Both rows must be regular, non-link, non-reparse files; each must be exactly
`20718150` bytes and the admitted source SHA-256.  Count is cardinality over
the whole successor root after the ZIP extraction and again after outer CLI
finalization; a live overlap of two rows is permitted only within this model.

| Id / purpose | Exact successor-relative path class and cardinality | Producer lineage and lifecycle | Evidence and authority |
|---|---|---|---|
| `runtime_source_transport_copy` | Exactly one live `engine/mineru_hybrid_high/_bridge_runtime/tmp/mineru-api-client-*/output/*/uploads/Call_of_Cthulhu_Viral.pdf` while request processing needs it. | Pinned outer `mineru.exe` -> `LocalAPIServer` child/descendant -> multipart `/tasks` upload writer. Created after source admission. | Record path, type, bytes, hash, UTC, process/PID lineage and source binding in the existing closed `evidence/COMMANDS.json` schema. It is redacted evidence only and cannot feed reconstruction or promotion. |
| `runtime_result_origin_copy` | Exactly one retained/extracted `engine/mineru_hybrid_high/Call_of_Cthulhu_Viral/hybrid_auto/Call_of_Cthulhu_Viral_origin.pdf`. No alternate backend/method/name or second `*_origin.*` is allowed. | Local API reads upload bytes -> hybrid `md_writer` emits origin PDF -> API result ZIP -> outer pinned CLI `safe_extract_zip` under the one absolute engine output. It exists only if result packaging/extraction completes. | Record the same immutable identity fields plus result ZIP/extraction lineage, result state, and `non_promotable_engine_evidence` purpose. It is not an asset, source authority, accepted input, normal reconstruction evidence, or publication file. |

The result-origin path cannot be safely excluded from the ZIP or extraction by
an installed public flag: the caller hard-codes both prerequisite form values.
It must therefore be retained by default as non-promotable engine evidence.
There is no automatic cleanup of this extracted output copy in the installed
CLI lifecycle.

## Cleanup, retention, and exact user authority

`LocalAPIServer.stop()` in `api_client.py:549-581` first stops the local API
child/descendant server tree through its managed process group and then invokes
`TemporaryDirectory.cleanup()`.  The outer `mineru` CLI calls that stop in its
`finally` path (`client.py:1024-1028`): cleanup occurs during outer pinned CLI
finalization, *after* the API child/descendant tree is stopped, not after the
outer CLI process itself has exited.

- **Automatic upload cleanup:** no authority is requested now.  Only after
  fresh critic acceptance may the orchestrator ask the user to authorize the
  installed `LocalAPIServer.stop()` / `TemporaryDirectory.cleanup()` deletion
  of the one verified transport-copy path class, after result transfer or
  terminal stop and after the API child/descendant tree has stopped.  It does
  not authorize outer-process killing, manual deletion, or predecessor cleanup.
- **Result-origin default:** retain it in the successor as a fully inventoried,
  non-promotable engine-evidence row.  Its retention needs no destructive
  authority, but prohibits using it as a source/asset/provenance authority.
- **Optional result-origin deletion:** only a later, separately authorized
  cleanup action may delete exactly the observed regular file at the origin
  path above, after it has been identified by absolute path, type, exact bytes
  and SHA-256, and after its inventory row is durable.  Required wording is:
  “I authorize deletion only of the verified successor
  `.../Call_of_Cthulhu_Viral_origin.pdf`, regular file, 20,718,150 bytes,
  SHA-256 `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05`; do not delete any other file, directory, source, or
  predecessor-root item.”  If the run blocks before a complete row, retain the
  entire successor root as immutable failure evidence; do not request or do
  manual deletion.

## Required implementation, tests, audits, and stops

Only the existing three generic seam/test files may gain generic enforcement;
no wrapper, MinerU edit, main script, API/router service, fourth code file, or
alternate public/internal API is allowed.  Tests must reject missing,
duplicate, wrong name/path, wrong bytes/hash, reparse/link, unknown producer,
uninventoried cleanup, promotion, and any third source-byte copy.  They must
allow only the two exact rows above and prove the origin row is absent from all
source/asset/final/accepted/publication sets.  They must also retain accepted
exact argv, one launch, child-only environment, no shell interpolation, and
cleanup-authority gating tests; run only permitted focused `-B` / no-cache
checks after this amendment is independently accepted.

Before launch, audit successor absence; branch/HEAD; every binding above;
installed file hashes; predecessor zero-delta inventories; exact allowlist;
and source admission order.  During/after the one launch, record each copy
row, complete successor inventory, result ZIP extraction lineage, PID/PPID
tree and best-effort endpoints.  Negative assertions are: no source-byte hash
or byte-count match outside the two path classes; no duplicate per class; no
other `*_origin.*`; no source bytes in output/provenance except redacted
transport/result rows; no source-derived path outside engine; and no promotion.

Immediately `blocked` with no repair, retry, fallback, cleanup, or second
launch on any binding/admission/allowlist failure, copy mismatch, missing row
when its lifecycle requires it, third copy, listener at `0.0.0.0` or `::`, any
non-loopback or unattributed listener, unknown/orphan process, cleanup without
the exact authority, or external/canonical/publication/Git mutation.  On a
post-start stop, stop only the verified pinned MinerU descendant tree from the
recorded launch lineage; never terminate an unrelated process by port or name.
Failure to attribute or stop that tree is itself `blocked` and evidence is
retained.  The strict `0.0.0.0`/`::`/unattributed-listener prohibition remains
unmodified by the loopback client exception.

## Fresh critic gate and next UI task

Fresh independent critic receipt, before execution or cleanup-authority
request, must be named:

`kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_step6a_origin_copy_closure_review_20260831.md`

It must be a `process/architecture` review, declare independence, and return
`accept` with no P0/P1.  Only then may the orchestrator request the narrowly
worded automatic-upload-cleanup authority.  The exact next UI task prompt is:

> Continue only the bounded Viral Step 6A candidate in
> `D:\NRI\.worktrees\kb-creator-viral` at
> `codex/kb-creator-viral` / `54607bd3b9362adbb0c4bca64e8751482797f380`.
> Read and SHA-verify the original packet; accepted bridge/cache/protected-
> prefix/loopback deltas and reviews; this origin-copy closure and its fresh
> critic accept; and both immutable predecessor roots/receipts. Do not write,
> clean, reuse, rename, or delete either predecessor. Use only new run id
> `20260831_step6a_origin_copy_exception_retry`; outside it write only the
> three accepted generic seam/test paths and
> `handoffs/luna_executor_viral_source_reconstruction_step6a_origin_copy_exception_retry_20260831.md`.
> Apply all accepted local-model/cache/profile/protected-prefix/loopback/
> absolute-output/source-admission controls. Launch the pinned direct MinerU
> argv once only with hybrid-engine/high/formula/table true. Permit exactly the
> two specified hash-identical source-byte runtime rows: the API upload copy
> and the extracted `hybrid_auto/..._origin.pdf`, fully inventoried and never
> promoted. Use only separately supplied authority for installed automatic
> upload cleanup; retain the origin row unless separately authorized after its
> verified inventory. Stop on any third/mismatched/escaped/unattributed copy,
> wildcard/non-loopback listener, orphan process, unauthorized cleanup, or any
> other stated stop; stop only the verified MinerU descendant tree. Do not use
> main MinerU scripts, wrapper/source edit, API/router service, install,
> firewall/admin, GPU/model probe, fallback, second launch, publication,
> contract/accepted/production edit, stage, commit, push, or remote operation.
> Return only truthful `candidate_needs_review` or `blocked` evidence.

## Engineering receipt

- Read: applicable instructions/governance, plan/context, original packet, all
  accepted amendments/reviews, rejected source-copy delta/review, immutable
  failure evidence, and installed MinerU 3.4.4 code.
- Verified: required branch/HEAD and all supplied hashes above; public CLI has
  no `return_original_file` control and its hard-coded origin-file lifecycle.
- Changed: this receipt only.  No MinerU/PDF/GPU/model/test run, implementation,
  cleanup, installation, network/firewall/admin action, canonical/output
  mutation, staging, commit, push, or remote operation occurred.
- Next action: fresh independent critic acceptance with no P0/P1; only then
  request the narrowly scoped automatic-upload-cleanup authority.
- Elapsed time: unavailable. Token use: unavailable.

## Detached SHA-256

Compute after final write; do not edit this receipt to embed its own hash.

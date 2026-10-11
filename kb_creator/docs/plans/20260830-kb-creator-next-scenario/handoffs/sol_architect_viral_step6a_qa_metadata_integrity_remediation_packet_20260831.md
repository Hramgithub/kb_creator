# Viral Step 6A QA metadata-integrity remediation specification

## Packet metadata and authority

- Goal / step: `20260830-kb-creator-next-scenario` / `6-source-reconstruction-step6a-qa-metadata-integrity-remediation`.
- Packet result: `design_ready_for_independent_review`; this packet is not execution authority.
- Architecture/root-cause owner: `gpt-5.6-sol`, requested `high`; actual platform model/effort unavailable, assignment state `user-directed / platform-unverified`.
- Orchestrator policy owner: main chat `gpt-5.6-sol`, `medium`; owns canonical plan/context/status, integration, stop/ask decisions and user-facing synthesis.
- Engineering assistance: `gpt-5.6-terra`, `medium`; advisory only if subsequently assigned.
- Fresh independent design and implementation/process critic: `gpt-5.5`, `medium`; must not implement or materially redesign the candidate it reviews.
- Bounded executor: `gpt-5.6-luna`, `medium`; only after design acceptance.
- Bounded QA: `gpt-5.6-luna`, `low`; separate from implementation.
- Scoped override: architecture/root-cause role explicitly requested for this packet only; no governance, safety, critic-independence or release-gate override.
- Worktree / branch / HEAD: `D:\NRI\.worktrees\kb-creator-viral` / `codex/kb-creator-viral` / `54607bd3b9362adbb0c4bca64e8751482797f380`.
- Upstream critic receipt: `gpt55_critic_viral_step6a_reconstruction_builder_qa_remediation_review_20260831.md`, SHA-256 `AE14A9D917FE9BAB4BD64DD1BAE84F6B3A52209D1A38D5483389E022BE69CF9B`, verdict `REJECT`, exactly two P1 findings.
- Token use for this packet: `unavailable`.

This is an architecture specification and bounded task packet. It does not run or authorize a build, MinerU, OCR, GPU/model, network, external-source access, cleanup, translation, `MASTER_EN` promotion, publication, Git staging, commit or push. Candidate state must remain `candidate_needs_review`.

## Root cause and defect-class closure

The first P1 is not merely a bad literal in one JSON file. The current remediation writer updates selected QA count/gate fields after it has changed `SOURCE_IDENTITY.json`, eight evidence JSON files and added 31 contact sheets, but it does not regenerate the recovery bindings, blocker summary or `output_inventory`. The live QA file therefore describes the 471-file pre-remediation state while the candidate is a 502-file post-remediation state.

The second P1 is the missing enforcement layer. `verify()` proves coarse topology and a few cardinalities, then returns success without proving that QA, source identity, recovery evidence, blocker ledger, inventories, live bytes/hashes and command policy agree. The focused test file is mostly static/string-level coverage, so its green result cannot detect the live contradictions.

The earliest failing layer is reusable reconstruction metadata finalization plus verification. Closure therefore requires all three of the following, not a hand-edit alone:

1. one deterministic QA/inventory finalizer used by builder/remediation code;
2. fail-closed validation of the complete evidence relationships; and
3. hermetic negative-mutation tests for each observed defect class and its direct analogues.

Semantic correctness is not in scope. Reading order, page modes, visual fidelity, asset placement/ownership, navigation semantics and handout/map/pregen attribution stay open. Passing this remediation proves evidence integrity only.

## Admitted immutable baseline

An executor must recompute every binding below before any write and stop on any mismatch. Hashes are SHA-256 of raw file bytes unless a manifest algorithm is explicitly named.

### Repository and source bindings

| Item | Required baseline |
|---|---|
| branch / HEAD | `codex/kb-creator-viral` / `54607bd3b9362adbb0c4bca64e8751482797f380` |
| working source | `kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf`; `20,718,150` bytes; `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05` |
| admission sidecar | `kb_creator/working/viral/source/SOURCE_ADMISSION.json`; `3DC6800C7515936C6434817F3DF6F9B3BF71E66C1CCCF477D168EFA53B550AA9` |
| contract source | `kb_creator/contracts/viral.json`; `67688867D4971D55137C2E4E7A71A746199596EDE4F5DD18577F4331CA87536D` |
| candidate contract snapshot | `SCENARIO_CONTRACT.json`; `C2EF2DD143E304F59C8973E8DB82CF83B094BC35DDA37BB2299686E1FE6DA194` |
| recovery root | `20260831_step6a_engine_output_salvage_candidate`; 211 regular files; canonical manifest `03E50B77DB3F4472F1650EF913F9F7EC4510ACEC59072670384B516336ACD258` |
| recovery manifest / evidence | raw hashes `41F00E41D04A19071FF0418068D7A1744C412F6EC6CDBEB7CFEE580B32B09169` / `F1F9F66AB3EA9C09196221CA82FDFEA888C94AAE024891057CA1A20FA53179BC` |
| canonical plan / context | `10957DC755651C423D03FB0995EF02E122F34761EC7973D800DD0081325F07A7` / `79E2C0879285D7334F280ECB3CB366E0B1A5ABA2EF7DD8929D763C14D4194F9C` |
| prior visual QA correction | `luna_qa_viral_step6a_reconstruction_builder_qa_retry_correction_20260831.md`; `194BF7EE471FF7E7DF859ED7958F7B3978F0F6C54536136C26CC6C6D1A7765DD` |

The external Yandex locator inside `SOURCE_ADMISSION.json` is a provenance string only. It must not be resolved, opened, statted, hashed, copied or used as a runtime argument.

### Live candidate baseline

Exact root:

`kb_creator/working/viral/source_reconstruction/20260831_step6a_reconstruction_from_salvaged_engine_candidate`

| Scope | Count | Canonical manifest SHA-256 |
|---|---:|---|
| all regular candidate files | 502 | `52E44F725AB121EC61A255B747EA467B4371481F391EB5E79B51132E67258066` |
| all files except `RECONSTRUCTED_EN.qa.json` | 501 | `2FF3FBE3D56E3F8FF3720203267776DB97A738136861A4E72140F3D4286B9592` |
| protected candidate subset, excluding only QA and `evidence/COMMANDS.json` | 500 | `98FC41EAA65528CE04C772983FB49E8DD3DAE5998FAEDB98F0829E2E41E4C027` |
| all `renders/` files | 155 | `19F600C23066DC3F64C5907BA6ADF59E3520C967249EBF7CB85CDAE53411979A` |
| `renders/source/` | 124 | `C6C14DD9219C765428E84BDB85CD9821C52B95433A2022DCAFACC8A71AEF0B5C` |
| `renders/contact_sheets/` | 31 | `B66EF1B60A0479C33F875C1CC60B576A1E785BEE16327EFE3C173F40BA77BB4A` |

Additional protected live hashes:

- `SOURCE_IDENTITY.json`: `276430E8AFC7C8310421D661F9753F0DB4AFBD1091D9B0B9C34084BB2BE438AC`;
- `evidence/BLOCKER_LEDGER.json`: `CD20D4137CF2FFA717DD36FC3D4ED433340D5886C59ABD355658C4F7BD475101`;
- `RECONSTRUCTED_EN.md`: `259B25D61D9BBFBB6314411DD73B257B56ECDFD8480B6E3EAD3DBCCA35DB5601`.

The two mutable candidate baselines are:

- `RECONSTRUCTED_EN.qa.json`: `FE142A0C8749B0D139265659A08F88F6CB67B3D34EB9815DB2B62875FA6B75DE`;
- `evidence/COMMANDS.json`: `EBD21CE0EB5EAC0986D7C4D1EABA3B9B24267858F495CEB38BF08F25FEE1DC07`.

The live contradictions to be removed are exact: QA schema `kb_creator.reconstructed_en_qa.v2`; stale recovery manifest `C32CCA...`; absent recovery-evidence hash; `open_blocker_count=3` against four open ledger rows; inventory length 470 against expected 501; 31 missing contact-sheet rows; nine stale rows; no extra or duplicate rows.

## Exact mutable allowlist

Execution may change only these material paths:

1. `kb_creator/scripts/scenario_source_reconstruction.py` (baseline `916D1A117C8FD09691502E1D2EB1DD1BF8FD9112229FE8616E770A17EBE2A446`);
2. `kb_creator/tests/test_scenario_source_reconstruction.py` (baseline `962BEC2E1A8A407FD11D8A088FBCDD18E40175F0B7C6A7B9A1DAE77E1303D63E`);
3. live candidate `evidence/COMMANDS.json`;
4. live candidate `RECONSTRUCTED_EN.qa.json`; and
5. the future immutable executor receipt `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/luna_executor_viral_step6a_qa_metadata_integrity_remediation_20260831.md`.

`kb_creator/scripts/reconstruct_scenario_source.py` is explicitly protected at baseline hash `64BD04C82A5AA21B7397885ABEB74E8A2215357B64DAD845AFDFDFC00F551DAA`. CLI modification is unnecessary: it already exposes and routes the exact `preflight`, `remediate` and `verify` actions and `--contract`, `--source`, `--recovery-root`, `--run-root` flags. A subprocess proof can exercise refusal/success through the unchanged CLI.

No other candidate evidence JSON is mutable. `SOURCE_IDENTITY.json` and `BLOCKER_LEDGER.json` are already truthful authorities; QA must be brought into agreement with them. All 155 renders, 124 page Markdown files, 209 copied engine payload files, the contract snapshot, master Markdown, recovery root, source/sidecar, plan/context/status, prior packets/receipts, accepted/production/publication artifacts, historical translations/config, Git index/refs and every path outside the allowlist are protected.

Pre-existing worktree dirt is not remediation output. The baseline includes modified `.gitattributes` and the already-untracked kb_creator plan/scripts/tests surfaces shown by `git status --short --branch`. The executor must capture the exact pre-status, may add only its allowlisted changes/receipt, and must not normalize, stage, revert or claim ownership of any pre-existing change.

## Chosen inventory rule

Retain `output_inventory` and define it as **every regular file recursively present in the exact candidate root except the root-level `RECONSTRUCTED_EN.qa.json` itself**.

This is preferred over removing the inventory because it keeps the candidate self-auditing and covers the observed stale-evidence class. Excluding only QA avoids self-hash recursion. It still includes `SOURCE_IDENTITY.json`, every evidence JSON including `COMMANDS.json`, all 31 contact sheets, 124 source renders, 124 page files, all engine payload and the remaining candidate files.

For the admitted post-remediation topology the exact inventory cardinality is `501`, and the exact total candidate cardinality is `502`. No file may be added or removed by this remediation. The post-remediation digests are intentionally not preclaimed: both must be measured after the new `COMMANDS.json` and QA bytes are final.

Each inventory row has exactly three fields:

```json
{"path": "candidate/root/relative-posix-path", "bytes": 123, "sha256": "UPPERCASE64HEX"}
```

Rules are binding:

1. enumerate regular files only; refuse symlinks, junctions/reparse points and path escape;
2. exclude exactly the root-relative string `RECONSTRUCTED_EN.qa.json` and nothing else;
3. render paths relative to candidate root with `/`, no leading `./` or `/`, no `..`, no backslash, no case folding or Unicode normalization;
4. `bytes` is raw byte length as a non-negative integer; `sha256` is uppercase SHA-256 of raw bytes;
5. construct complete records `path<TAB>bytes<TAB>sha256`;
6. sort complete records with ordinal ordering. Current candidate paths are ASCII, so Python `sorted(records)`, UTF-8 byte ordering and `.NET StringComparer.Ordinal` agree; culture-sensitive sorting is forbidden;
7. join with LF, append one final LF, encode UTF-8 without BOM, and SHA-256 that stream;
8. emit the array in the same record order.

QA v3 must add `output_inventory_rule`, `output_inventory_count=501` and `output_inventory_sha256=<measured 501-record digest>` next to the 501-row array. `verify()` independently reconstructs the array and digest from disk; it must not trust QA's count, order, bytes, hashes or digest.

The full candidate post-manifest uses the same record serialization over all 502 regular files, including QA. It is calculated only after QA is serialized, then recomputed independently a second time. Both recomputations must agree. The executor receipt records the new 502-file digest; it must differ from the admitted `52E44...` baseline because QA and command evidence changed.

## Required implementation semantics

### Shared finalization helpers

`scenario_source_reconstruction.py` should gain small deterministic helpers rather than another one-off script:

- exact local-source admission and runtime-policy validation;
- canonical candidate records/inventory calculation with an explicit exclusion set;
- strict evidence-bundle derivation/validation;
- construction of QA v3 from authoritative live evidence; and
- strict validation of QA v3 against independently derived facts.

No helper may consult the network, environment-dependent locale sorting, current time, random values or external locator. JSON remains UTF-8, sorted keys, two-space indent and final LF.

### `build()`

`build()` remains fresh-root/refuse-overwrite and must never launch MinerU/OCR. It is not run in this remediation. Its QA construction must nevertheless use the shared finalizer after every non-QA artifact for that builder stage has been written. A fresh pre-contact-sheet builder candidate may have its stage-derived inventory count (currently 470) but may not omit `recovery_evidence_sha256`, undercount its then-live blocker ledger or emit stale inventory. It remains `candidate_needs_review` and does not become final Step 6A verification evidence until remediation closure exists.

This change closes the reusable writer defect class; it does not rebuild the live candidate.

### `remediate()` for this admitted 502-file candidate

The current execution is a metadata-only branch, admitted only when all of these match before the first write:

- full 502-file manifest `52E44...`;
- mutable file hashes `FE142...` and `EBD21...`;
- protected 500-file manifest `98FC...`;
- source/sidecar/contract/recovery identities above; and
- candidate `SOURCE_IDENTITY.json`, ledger and evidence schemas/counts validate independently.

It must not call `build`, `render_source`, `make_contact_sheets`, MinerU, OCR, GPU/model or network; it must not write any render, source identity, ledger or other evidence. It performs exactly:

1. derive the truthful `COMMANDS.json` v3 object in memory;
2. derive the post-command 501-row inventory and QA v3 bytes in memory twice and require byte equality;
3. write `COMMANDS.json` once;
4. write QA once; and
5. immediately run the same strict validation used by `verify()`.

The command evidence retains the 31-sheet mapping/hashes and count map, and records exact local runtime policy. Every action record (`preflight`, `remediate`, `contact_sheets`, `verify`) must contain explicit booleans `build_invoked`, `mineru_invoked`, `ocr_invoked`, `gpu_or_model_invoked`, `network_invoked`, and `external_source_used`, all `false`. Runtime actions also record `source_flag=--source`, `run_root_flag=--run-root`, and `source_relative_path=kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf`. Omission, `true`, an absolute external locator or another source path is invalid.

After the first material write, any exception is a blocked result requiring orchestrator recovery; the executor must not widen scope, rebuild, delete/recreate the candidate or silently retry against a changed baseline. A second `remediate` invocation on the post-state must refuse because the pre-manifest no longer matches. Determinism is proved by in-memory double construction plus repeated read-only `verify`, not by rewriting the candidate twice.

### `preflight()` and exact local-source policy

`preflight`, `build`, `remediate` and `verify` must share one policy gate:

- resolve the provided `--source` strictly and require exact path equality with `<repo-root>/kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf` after normalized-case comparison appropriate to Windows;
- require a regular non-symlink/non-reparse file with exact bytes/hash/page facts;
- read and validate the sidecar at its exact local path and raw hash without opening its external locator;
- require `runtime_dependency=false`, `external_path_allowed_after_admission=false`, the exact `subsequent_source_path`, and `generated_origin_pdf_is_source=false`;
- require source identity and command evidence to bind the same admitted bytes/hash and local runtime role; and
- reject a byte-identical copy at any other path, including the provenance locator.

The external locator is permitted only as data inside the sidecar. It is forbidden in candidate JSON and runtime command evidence.

### `verify()`

`verify()` is read-only and must fail before returning success on any mismatch in these classes:

1. branch/HEAD, exact source/sidecar/contract/recovery/candidate root, containment, reparse/symlink, topology, forbidden PDF/cache/runtime/`.pyc` classes;
2. exact schema map: QA `kb_creator.reconstructed_en_qa.v3`; source identity v2; asset/navigation/page/content/entity/handout/blocker/commands v3; content-mode/reference-only v2;
3. QA recovery hashes equal both raw recovery files and `SOURCE_IDENTITY.json`; source/contract hashes agree across authoritative files;
4. ledger `open_count`, number of rows, number of `state=open` rows and QA `open_blocker_count` all equal `4`; all four existing blocker ids remain open/`needs_review` where present;
5. output inventory has exactly 501 unique rows, exact schema/order/path set/live bytes/live hashes/digest, contains all 31 contact sheets and all evidence files, and excludes only QA;
6. live total remains 502 and no unexpected path exists;
7. exact row/count closure: pages/renders/navigation `124`; contact sheets `31`; handouts `39`; engine payload/images `209/204`; assets `204`; referenced/unreferenced `112/92`; Markdown references `112`; maps/pregens/back cover `7/13/1`; content blocks `388`; content-mode review rows `5`;
8. page rows are unique 1..124 and their Markdown/render paths, byte counts and hashes match disk; navigation rows are unique `page-001`..`page-124`, indices 0..123, exact prev/next links, contract roles and matching page/render hashes;
9. asset rows are a bijection with the 204 copied engine JPEGs by path/hash/bytes; asset ids and paths are unique; reference counts conserve 112 and exactly 92 rows remain unreferenced; referenced locations resolve to observed engine Markdown evidence;
10. 31 command-evidence sheet rows map pages 1..124 exactly once in groups 1-4 through 121-124 and bind live sheet/render hashes;
11. QA scalar counts, `counts`, command counts and live-derived counts agree; required QA gate states remain pass only for identity/coverage/conservation, `needs_review` for visual/semantic uncertainty and `blocked_candidate_only` for promotion;
12. command evidence uses the exact local relative source and contains every required explicit false flag; and
13. `historical_material_opened=false`, `main_scripts_invoked=false`, no invented final semantic/ownership value and state exactly `candidate_needs_review`.

Error messages identify the earliest failing class and path/field without dumping the external locator or unrelated data.

## QA v3 exact state

The final QA object must preserve the existing truthful scalar fields and contain at least these exact derived values:

- `schema=kb_creator.reconstructed_en_qa.v3`;
- `state=candidate_needs_review`;
- contract/source hashes matching live authorities;
- recovery manifest/evidence hashes `41F00...` / `F1F9...`;
- `page_count=124`, `handout_count=39`, `block_count=388`, `asset_count=204`, `contact_sheet_count=31`, `navigation_anchor_count=124`, `referenced_asset_count=112`, `unreferenced_asset_count=92`, `open_blocker_count=4`;
- counts map: pages/renders `124/124`, sheets `31`, handouts/maps/pregens/back cover `39/7/13/1`, engine payload/images `209/204`, assets `204`, referenced/unreferenced `112/92`, navigation anchors `124`, open blockers `4`;
- `historical_material_opened=false`, `main_scripts_invoked=false`;
- unchanged candidate-only/open gate semantics; and
- the 501-row inventory rule/count/digest/array defined above.

No field may claim reconstruction acceptance, final placement, final ownership, final reading order or promotion readiness.

## Focused hermetic test packet

Tests stay in `test_scenario_source_reconstruction.py`, use `tmp_path` and monkeypatching, and do not open the real PDF/candidate/recovery, invoke Git, create cache, use network or launch external processes except the local Python CLI subprocess proof. Fixtures use small raw files plus deterministic 124/204/39-row JSON structures where cardinality logic itself is under test.

Required positive tests:

1. inventory excludes only QA, contains command evidence and representative contact sheets, uses POSIX paths, exact byte/hash rows, ordinal order, UTF-8/no-BOM/LF-final digest and deterministic bytes;
2. QA finalization copies both recovery hashes, derives four open blockers and produces the expected stage cardinality;
3. strict verify accepts one complete hermetic bundle with all cross-links/counts/hashes consistent;
4. metadata-only remediate changes only QA and commands in a fixture, preserves a protected-subset manifest and refuses a second run;
5. unchanged CLI invoked from the fixture's correct worktree cwd accepts the exact admitted local source and returns exit 0.

Required negative mutation matrix; each mutation is isolated from a fresh valid fixture and must raise `ReconstructionStop` or make CLI exit `2`:

- stale QA recovery-manifest hash;
- absent and mismatched QA recovery-evidence hash;
- `SOURCE_IDENTITY` recovery mismatch;
- ledger `open_count` vs row/open-row mismatch and QA `open_blocker_count` mismatch;
- inventory missing one ordinary file, one evidence file or one contact sheet;
- inventory extra/stale path, duplicate path, inclusion of QA, wrong cardinality, non-ordinal order, wrong bytes, wrong hash, lowercase hash, wrong digest, backslash/absolute/`..` path;
- wrong QA or evidence schema, missing required field, wrong scalar/count map, promoted state or closed uncertainty gate;
- missing/duplicate page, navigation, asset or sheet row; wrong page/index/prev/next/role; wrong page Markdown/render hash; wrong asset bytes/hash/reference total; wrong 204/112/92 conservation; wrong 39/7/13/1 closure;
- command record missing any required false flag, any flag true, wrong/stale CLI flag, missing/wrong local relative source, external locator, wrong action set, stale sheet/render hash or duplicate/missing page coverage;
- sidecar missing/wrong hash/policy, source argument outside exact local path even with identical bytes, symlink/reparse local source, and exact external-locator argument;
- unexpected candidate file, forbidden PDF/cache/runtime/`.pyc`, protected-file mutation and candidate-root escape.

At least one test must reproduce each live P1 symptom before the fix and pass only after the fix. Static source-string assertions are supplementary, never the sole proof.

## Commands from the correct worktree cwd

The executor runs only these commands, from `D:\NRI\.worktrees\kb-creator-viral`, after an independent design review accepts this packet with no open P0/P1:

```powershell
Set-Location 'D:\NRI\.worktrees\kb-creator-viral'
python -B -m pytest kb_creator/tests/test_scenario_contract.py kb_creator/tests/test_scenario_source_reconstruction.py -q -p no:cacheprovider
python -B kb_creator/scripts/reconstruct_scenario_source.py preflight --contract kb_creator/contracts/viral.json --source kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf --recovery-root kb_creator/working/viral/source_reconstruction/20260831_step6a_engine_output_salvage_candidate --run-root kb_creator/working/viral/source_reconstruction/20260831_step6a_reconstruction_from_salvaged_engine_candidate
python -B kb_creator/scripts/reconstruct_scenario_source.py remediate --contract kb_creator/contracts/viral.json --source kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf --recovery-root kb_creator/working/viral/source_reconstruction/20260831_step6a_engine_output_salvage_candidate --run-root kb_creator/working/viral/source_reconstruction/20260831_step6a_reconstruction_from_salvaged_engine_candidate
python -B kb_creator/scripts/reconstruct_scenario_source.py verify --contract kb_creator/contracts/viral.json --source kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf --recovery-root kb_creator/working/viral/source_reconstruction/20260831_step6a_engine_output_salvage_candidate --run-root kb_creator/working/viral/source_reconstruction/20260831_step6a_reconstruction_from_salvaged_engine_candidate
python -B kb_creator/scripts/reconstruct_scenario_source.py verify --contract kb_creator/contracts/viral.json --source kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf --recovery-root kb_creator/working/viral/source_reconstruction/20260831_step6a_engine_output_salvage_candidate --run-root kb_creator/working/viral/source_reconstruction/20260831_step6a_reconstruction_from_salvaged_engine_candidate
```

No `build` command is authorized. The two verify stdout payloads, exit codes and stdout SHA-256 values must be identical.

## Visual QA carry-forward rule

The 67/67 original-resolution review and 31/31 contact-sheet review in the correction receipt may be carried forward without viewing 67 pages again **only if** all of these are proved after remediation:

1. the prior QA correction receipt still hashes to `194BF7...`;
2. the 155-file render manifest remains exactly `19F600...`;
3. the 124-source-render and 31-contact-sheet submanifests remain exactly `C6C14D...` and `B66EF1...`;
4. the protected 500-file candidate manifest remains `98FC41...`;
5. the final mutation audit contains only the library, focused tests, QA, commands and executor receipt; and
6. strict verify revalidates all command-evidence render/sheet hashes and mappings.

These conditions prove that the pixels already reviewed are byte-identical and attached to the same pages/sheets. If any render count, path, bytes, hash, sheet mapping or protected manifest changes, carry-forward is void and bounded QA must repeat the affected visual scope; if the affected scope cannot be isolated, repeat all 67 pages and 31 sheets. Carry-forward does not close semantic, reading-order, placement or ownership blockers.

## Acceptance criteria

Implementation is ready for separate bounded QA only when:

- design critic accepted this packet with no unresolved P0/P1;
- focused tests pass and include all named negative classes;
- preflight/remediate/verify commands use only the admitted local source;
- only the four material allowlisted paths changed, plus the executor receipt;
- candidate remains 502 regular files and QA inventory is exactly 501 truthful ordered rows;
- post inventory and full-candidate digests are measured twice and agree;
- protected 500-file and all visual manifests are unchanged;
- source/recovery/contract/ledger/QA/commands/count/hash relationships pass strict verify twice with identical output;
- QA is v3, recovery hashes are current, open blockers equal four, all 31 sheets appear, and no stale row remains;
- no source, sidecar, recovery, render, page, engine, other evidence, plan/context/status, prior receipt, publication or Git mutation occurred; and
- receipt and mutation audit are complete.

Even after those criteria, the result is only `candidate_needs_review`. Step 6A acceptance requires separate bounded QA and a fresh independent `gpt-5.5` implementation/process review. `MASTER_EN`, release and publication remain unauthorized.

## Executor stop conditions

Stop before the first write on any branch/HEAD, source/sidecar, packet/review, candidate baseline, mutable hash, protected manifest, recovery/contract, schema/count/hash, path-containment, reparse or local-source-policy mismatch. Stop if the target root/file set differs from 502, if another process/user changes an allowlisted or protected file after admission, or if exact post bytes cannot be derived without invention.

After a write, stop and report blocked on any unexpected delta, partial-write exception, failed strict validation/test/command, nondeterministic serialization/stdout, post-manifest disagreement, missing inventory/contact sheet, protected/render hash change, external access, forbidden process, candidate promotion, semantic closure or Git mutation. Do not self-repair by widening the allowlist, rerunning MinerU/OCR, invoking build, replacing source/evidence, recreating the candidate, deleting a predecessor or editing canonical governance.

## Mutation audit and required receipts

Before execution, capture raw hashes for every mutable file, exact Git status, the 502/501/500 and visual manifests, source/sidecar/recovery/contract/plan/context/packet/review hashes. After execution, repeat them and produce an exact added/modified/deleted path comparison. Deletions and additions inside the candidate are forbidden; only QA and commands may differ there.

The executor receipt must be written once to:

`kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/luna_executor_viral_step6a_qa_metadata_integrity_remediation_20260831.md`

It records goal/step/role/model/effort, actual platform values or `unavailable`, orchestrator owner, scoped override, timestamp/elapsed/token use, worktree/branch/HEAD, packet and design-review hashes, all commands/exit codes, focused test result, local-source/sidecar bindings, pre/post mutable hashes, pre/post 502-file manifests, post 501-row inventory digest, unchanged 500/render manifests, exact mutation audit, P1 disposition, remaining four open blockers, forbidden-action declaration, result and next action.

Separate bounded QA then writes only:

`kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/luna_qa_viral_step6a_qa_metadata_integrity_remediation_20260831.md`

QA independently repeats tests, strict verify twice, manifest/inventory calculations, local-source policy and mutation audit. It may invoke the visual carry-forward rule only with all six proofs above. It implements nothing.

Fresh independent design review before execution writes only:

`kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_step6a_qa_metadata_integrity_remediation_packet_review_20260831.md`

Fresh independent implementation/process review after QA writes only:

`kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_step6a_qa_metadata_integrity_remediation_review_20260831.md`

Any material mutation after either review invalidates the corresponding review boundary. This packet itself changes no code, test, candidate, source, sidecar, plan/context/status, prior receipt or Git state.

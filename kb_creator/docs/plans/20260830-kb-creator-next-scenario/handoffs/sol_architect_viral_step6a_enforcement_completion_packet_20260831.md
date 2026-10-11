# Viral Step 6A enforcement-layer P1/P2 completion packet

## Packet identity, decision and authority

- Goal / step: `20260830-kb-creator-next-scenario` / `6-source-reconstruction-step6a-enforcement-completion`.
- Result: `design_ready_for_independent_review`; this packet is not execution or acceptance authority.
- Architecture/root-cause owner: policy `gpt-5.6-sol` / `high`; actual platform model/effort `unavailable`; assignment state `user-directed / platform-unverified`.
- Orchestrator policy owner: main chat `gpt-5.6-sol` / `medium`; it retains canonical plan/context/status, integration, stop/ask decisions and user-facing synthesis.
- Engineering assistance: `gpt-5.6-terra` / `medium`, advisory only if separately assigned.
- Bounded executor: `gpt-5.6-luna` / `medium`, only after independent design acceptance.
- Bounded QA: `gpt-5.6-luna` / `low`, separate from implementation.
- Independent design and implementation/process critic: `gpt-5.5` / `medium`; the critic must not implement or materially redesign the work under review.
- Scoped override: architecture/root-cause role only; no safety, governance, independence or release-gate override.
- Required worktree / branch / HEAD: `D:\NRI\.worktrees\kb-creator-viral` / `codex/kb-creator-viral` / `54607bd3b9362adbb0c4bca64e8751482797f380`.
- Triggering critic receipt: `gpt55_critic_viral_step6a_qa_metadata_integrity_remediation_review_20260831.md`, SHA-256 `1ECB8FEBC517BAE2BFFF949663A9A701BF8107A80B8023C16EF6ABD6712A7D2D`, verdict `REJECT`, one open enforcement-layer P1 and one build-semantics P2.
- Base metadata packet / immutable amendment: SHA-256 `C86335AFCAC0A6060BA8E9D616172115905DE7B08F3ED1E88BCB822D6CE8B648` / `9FDBC4848AAF280DDFE4080E1263B4146320436E5A832A296C50209AB9B99292`.
- Token use for this architecture task: `unavailable`.

This packet chooses **completion of the original strict contract**, not a narrower verifier contract. It closes the durable enforcement defect and restores the accepted reusable `build()` seam without running a build. It does not close semantic, reading-order, placement, ownership or visual-review uncertainty.

No live build, `remediate`, MinerU, OCR, GPU/model, network, external-source access, historical-material access, translation, semantic edit, `MASTER_EN` promotion, publication or Git mutation is authorized. The only source authority remains the admitted local PDF; the sidecar's external locator is provenance data only and must never be resolved, opened, statted, hashed, copied, printed in an error or passed to a command.

## Root cause and closure boundary

The metadata-writer P1 is closed on live data: QA v3, recovery bindings, four open blockers and the 501-row non-circular inventory are truthful. The remaining P1 is architectural: live `verify()` checks only a subset of the accepted relations, and eight mostly helper/static tests cannot prove fail-closed behavior. Branch/HEAD is checked only by `preflight()`, explicit forbidden classes and several schema/count/link relations are not durable gates, and receipt assertions substitute for executable enforcement.

The P2 is independent scope drift: `build()` was replaced by unconditional refusal instead of retaining fresh-root/refuse-overwrite behavior and calling the same finalizer as remediation/build writers. Disabling the public seam is not preservation.

Closure requires all of the following in one code/test slice:

1. one shared repository/source/recovery admission gate used by `preflight()`, `build()`, `remediate()` and `verify()`;
2. one shared, phase-ordered strict verifier that directly enforces every relationship in this packet;
3. one shared deterministic finalizer used by `build()` and existing metadata writers, with no duplicate QA construction path;
4. a complete hermetic valid bundle and isolated fail-closed mutation trials; and
5. restoration of `build()` fresh-root/refuse-overwrite behavior, proved only with hermetic fresh-root, overwrite-refusal and finalizer-parity tests.

Candidate state remains exactly `candidate_needs_review`; all four live blockers remain open.

## Admitted immutable baseline

Every future contributor recomputes these values before its first write and stops on a mismatch. Hashes are raw-byte SHA-256 unless a canonical manifest is named.

### Repository, authority and implementation baseline

| Item | Required value |
|---|---|
| branch / HEAD | `codex/kb-creator-viral` / `54607bd3b9362adbb0c4bca64e8751482797f380` |
| local source | `kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf`; 20,718,150 bytes; `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05` |
| source sidecar | `kb_creator/working/viral/source/SOURCE_ADMISSION.json`; schema `kb_creator.source_admission.v1`; `3DC6800C7515936C6434817F3DF6F9B3BF71E66C1CCCF477D168EFA53B550AA9` |
| contract source | `kb_creator/contracts/viral.json`; schema `kb_creator.scenario_contract.v1`; raw hash `67688867D4971D55137C2E4E7A71A746199596EDE4F5DD18577F4331CA87536D` |
| candidate contract snapshot | `SCENARIO_CONTRACT.json`; exact canonical bytes/hash `C2EF2DD143E304F59C8973E8DB82CF83B094BC35DDA37BB2299686E1FE6DA194` |
| recovery root | exact `20260831_step6a_engine_output_salvage_candidate`; 211 regular files; canonical manifest `03E50B77DB3F4472F1650EF913F9F7EC4510ACEC59072670384B516336ACD258` |
| recovery manifest/evidence | raw hashes `41F00E41D04A19071FF0418068D7A1744C412F6EC6CDBEB7CFEE580B32B09169` / `F1F9F66AB3EA9C09196221CA82FDFEA888C94AAE024891057CA1A20FA53179BC` |
| recovery payload | exactly 209 rows/files: five named engine Markdown/JSON files plus 204 JPEGs; 21,220,717 bytes; 112 Markdown image references; 92 unreferenced images |
| shared library | `kb_creator/scripts/scenario_source_reconstruction.py`; `581FA8D0F47C7906B29EC4664E929A98B3A3699445C974AB7CF51F398D118FA8` |
| focused tests | `kb_creator/tests/test_scenario_source_reconstruction.py`; `9F581C5C6CD9A8DF5DB06DA30F48B6FE39995713AD3CFFCC3829CF8530D1C1B0` |
| protected CLI | `kb_creator/scripts/reconstruct_scenario_source.py`; `64BD04C82A5AA21B7397885ABEB74E8A2215357B64DAD845AFDFDFC00F551DAA` |
| protected contract tests | `kb_creator/tests/test_scenario_contract.py`; `DE5603869C9517A274FCD6DB2D61D23BEE2A204BAC8A1217E16603A5BF232AC3` |
| prior visual-QA receipt | `luna_qa_viral_step6a_reconstruction_builder_qa_retry_correction_20260831.md`; `194BF7EE471FF7E7DF859ED7958F7B3978F0F6C54536136C26CC6C6D1A7765DD` |

### Live candidate baseline

Exact root:

`kb_creator/working/viral/source_reconstruction/20260831_step6a_reconstruction_from_salvaged_engine_candidate`

| Scope | Count | Canonical manifest SHA-256 |
|---|---:|---|
| all regular files | 502 | `410AED5D111E3BA8CA294095EF55F18AC7DFFD335868EA6D59522B91E14725EA` |
| all except root `RECONSTRUCTED_EN.qa.json` | 501 | `F0F243F6B8194C502CF6FEF9D5C838196BAFA49C96AE135D61EDAD799869C766` |
| protected subset excluding QA and `evidence/COMMANDS.json` | 500 | `98FC41EAA65528CE04C772983FB49E8DD3DAE5998FAEDB98F0829E2E41E4C027` |
| all candidate-relative `renders/**` rows | 155 | `19F600C23066DC3F64C5907BA6ADF59E3520C967249EBF7CB85CDAE53411979A` |
| candidate-relative `renders/source/**` rows | 124 | `C6C14DD9219C765428E84BDB85CD9821C52B95433A2022DCAFACC8A71AEF0B5C` |
| candidate-relative `renders/contact_sheets/**` rows | 31 | `B66EF1B60A0479C33F875C1CC60B576A1E785BEE16327EFE3C173F40BA77BB4A` |

Protected raw hashes include `SOURCE_IDENTITY.json` `276430E8AFC7C8310421D661F9753F0DB4AFBD1091D9B0B9C34084BB2BE438AC`, `evidence/BLOCKER_LEDGER.json` `CD20D4137CF2FFA717DD36FC3D4ED433340D5886C59ABD355658C4F7BD475101`, and `RECONSTRUCTED_EN.md` `259B25D61D9BBFBB6314411DD73B257B56ECDFD8480B6E3EAD3DBCCA35DB5601`.

The two formerly mutable files are now protected and byte-immutable in this slice:

- `RECONSTRUCTED_EN.qa.json`: 104,854 bytes; `C38CB0A4667B1D4344C5E5DD91AEAAE7A2FD3101A3BB76611104EAA13BBD8FA6`;
- `evidence/COMMANDS.json`: 37,422 bytes; `9162651A456E12C7011081F999AA3B07EDB7EA9E66CA65CC78A0382456F12B06`.

Closed live topology is four root files, 124 `pages/*.md`, ten evidence JSON files, 209 `engine/**` payload files, 124 source renders, 31 contact sheets, and empty `assets/`, `crops/` and `ocr/` subtrees. No file addition, deletion, rename or byte change inside this candidate is permitted.

## Exact future allowlist and protected orchestration rule

The bounded executor may materially change only:

1. `kb_creator/scripts/scenario_source_reconstruction.py`;
2. `kb_creator/tests/test_scenario_source_reconstruction.py`; and
3. new immutable receipt `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/luna_executor_viral_step6a_enforcement_completion_20260831.md`.

The CLI, contract library/tests, contract/source/sidecar/recovery/candidate, every render/page/evidence file, prior packet/receipt, accepted/production/publication surface, historical material, `MASTER_EN`, Git refs/index and every other path are protected. The executor must not edit QA or `COMMANDS.json`.

The subsequent independent design review writes only `gpt55_critic_viral_step6a_enforcement_completion_packet_review_20260831.md`; bounded QA writes only `luna_qa_viral_step6a_enforcement_completion_20260831.md`; final implementation/process review writes only `gpt55_critic_viral_step6a_enforcement_completion_review_20260831.md`. These receipts are separate contributor windows, not executor allowlist additions.

`plan.md`, `context.md`, `kb_creator/PROJECT_STATUS.md`, `kb_creator/README.md`, `kb_creator/docs/KB_CREATOR_PIPELINE_SUMMARY_20260830.md`, applicable release/status/README artifacts and all pre-existing handoffs are protected through dispatch-window pre/post path/existence/byte-length/raw-hash equality. They are **not** bound to packet-era fixed hashes. A legitimate orchestrator update before dispatch is allowed; any change after the contributor captures its dispatch snapshot is a fail-closed concurrent delta.

Pre-existing worktree dirt is not output. Record exact `git status --short --branch` before/after; do not normalize, stage, revert or claim unrelated paths.

## Decision: no new QA or COMMANDS fields

No new field is necessary. The live QA already contains exact schema/state, four authority hashes, nine scalar counts, the complete 14-key count map, nine gate results, two historical/process booleans and the non-circular inventory rule/count/digest/array. `COMMANDS.json` already contains the four ordered action records, 11-key count map, explicit local source/run-root flags, six explicit false flags per action, 31 sheet rows and 124 page-render mappings/hashes.

Branch/HEAD is a runtime repository authority and must be checked directly by every public operation; serializing it into candidate evidence would not make the live repository state self-proving. All other missing guarantees are derivable from existing bytes and live paths. Therefore:

- candidate QA and `COMMANDS.json` remain byte-identical;
- no re-finalization is run;
- the 502/501/500 manifests remain exactly `410AED...` / `F0F243...` / `98FC41...`; and
- any proposed candidate mutation is an executor stop, not an architecture improvisation.

## Required implementation architecture

### Production profile and dependency seams

Introduce one immutable enforcement profile containing expected repo-relative source/recovery/candidate roots, branch/HEAD, raw authority hashes, schemas, topology/counts and command/state policy. Production wrappers construct the fixed Viral Step 6A profile. Hermetic tests construct an equivalent temporary profile with tiny bytes and an injected repository-identity probe. There is no `strict=False`, `skip_*`, environment-variable bypass or caller-supplied relaxation in the public CLI path.

The repository probe returns resolved repo root, branch and HEAD. Production uses Git read-only; tests monkeypatch/inject the probe and must not spawn Git. `verify()` itself calls the shared repository gate first. It may not rely on a prior `preflight()` call, a receipt, cwd inference or a caller promise.

Use stable failure codes plus the narrow field/path, for example `E_REPO_BRANCH`, `E_CANDIDATE_FORBIDDEN_PDF`, `E_INVENTORY_HASH`, `E_COMMAND_COUNTS_PAGES`. Do not dump the external locator or unrelated JSON.

### Phase-ordered shared strict verifier

All public operations use the same primitives. `verify()` runs every phase directly and returns success only after all phases pass:

1. **Repository authority:** resolved repo root, exact branch and exact HEAD; correct-cwd and repo containment.
2. **Path admission:** exact local source, sidecar, contract, recovery and candidate roots; every ancestor and descendant relevant to the operation is non-symlink/non-junction/non-mount-point/non-reparse; no path escape.
3. **Source/contract/recovery authority:** raw hashes and all cross-bindings below.
4. **Explicit forbidden scan and closed topology:** reject before generic cardinality errors.
5. **Closed schemas and shapes:** validate exact schema strings, required members and allowed row variants.
6. **Canonical inventory transport:** independently enumerate live files and validate path/order/bytes/hash/digest.
7. **Evidence graph semantics:** page/content/navigation/asset/entity/handout/sheet relations and live bytes.
8. **QA and command policy:** every scalar, gate, action, count, hash, flag and state.
9. **No-fabricated-closure policy:** all review uncertainty remains open.

The explicit forbidden candidate classes are case-insensitive path-segment/suffix classes: any `*.pdf`; `*.pyc`; `*.pyo`; `__pycache__`; `_bridge_runtime`; `.cache`; `cache`; `caches`; `.pytest_cache`; `tmp`; or `temp`. Symlinks, junctions, mount points and any Windows reparse attribute are independently forbidden for repo/source/sidecar/contract/recovery/candidate roots and all enumerated descendants. Inventory paths reject absolute, drive-qualified, UNC, leading `/`, leading `./`, backslash, empty segment, `.`/`..`, trailing slash, case-folded aliases and non-regular files. The fixed topology also rejects every unexpected path even if it is not in a named forbidden class.

### Exact schema map and bindings

The verifier enforces these 16 schema authorities:

| Document | Exact schema |
|---|---|
| source contract | `kb_creator.scenario_contract.v1` |
| source sidecar | `kb_creator.source_admission.v1` |
| recovery manifest | `viral_raw_engine_input_recovery_manifest.v1` |
| recovery evidence | `viral_raw_engine_input_recovery_evidence.v1` |
| QA | `kb_creator.reconstructed_en_qa.v3` |
| source identity | `kb_creator.source_identity.v2` |
| page/content/asset provenance | `kb_creator.page_provenance.v3`; `kb_creator.content_provenance.v3`; `kb_creator.asset_provenance.v3` |
| entity/handout/navigation | `kb_creator.entity_inventory.v3`; `kb_creator.handout_inventory.v3`; `kb_creator.navigation_inventory.v3` |
| content-mode/reference-only | `kb_creator.content_mode_review.v2`; `kb_creator.reference_only_audit.v2` |
| blocker/commands | `kb_creator.blocker_ledger.v3`; `kb_creator.reconstruction_commands.v3` |

The contract source must load under intake validation, have the exact source facts and canonicalize byte-identically to `SCENARIO_CONTRACT.json`. `SOURCE_IDENTITY.json` must bind that canonical hash, exact local source bytes/hash/page/media/rotation facts, exact recovery root and both recovery raw hashes; its observer covers pages 1..124 and `historical_material_opened=false`.

The sidecar raw hash and all fields are binding: working relative path/bytes/hash/page/media/rotation; `runtime_dependency=false`; `external_path_allowed_after_admission=false`; `subsequent_source_path` equal to the working relative path; `generated_origin_pdf_is_source=false`; and the two copy-verification equality flags true. The external locator is never dereferenced or emitted.

The recovery root has exactly 211 regular files. Its manifest has 209 unique ordinal records whose path/bytes/hash are a bijection with the five named engine files and 204 JPEGs; successor count/bytes/root and predecessor binding are exact. Recovery evidence binds the same source, roots and manifest, exact 209/204/112/92 payload facts, zero missing Markdown targets, the allowed path classes, and all promotion fields false. No recovery PDF/cache/runtime/compiled payload is admitted.

The blocker ledger has exactly these four unique open rows and no closure alias: `full-visual-review`, `unknown-content-modes-1-5`, `handout-map-pregen-navigation-review`, `asset-placement-ownership-review`. `open_count`, row count and `state=open` count are all four; every `review_state=needs_review`; affected pages/assets/scope match the live rows. QA `open_blocker_count` and `counts.open_blockers` are both four.

### Inventory, topology and byte relationships

Retain the accepted non-circular inventory: every regular candidate file except root `RECONSTRUCTED_EN.qa.json`. Each row is exactly `{path, bytes, sha256}`. Paths are candidate-relative POSIX strings, bytes are non-negative strict integers, hashes are uppercase 64-hex raw-byte SHA-256. Sort complete `path<TAB>bytes<TAB>sha256` records ordinally; join with LF plus one final LF; hash UTF-8/no-BOM bytes. The array uses the same order.

Strict verification independently proves 501 unique rows, exact path set/order/live bytes/live hashes/digest, inclusion of `evidence/COMMANDS.json`, all ten evidence files and all 31 sheets, and exclusion of only QA. It separately proves 502 total files and the exact closed topology. It must not trust QA's array/count/digest as its source of facts.

### Page, content, Markdown and navigation graph

- `PAGE_PROVENANCE` contains unique pages 1..124, ids `page-001`..`page-124`, engine indices 0..123, exact contract roles/content modes and 388 total unique block ids.
- Each row's `markdown` and `render` objects have exact path/bytes/hash shapes and bind a live page Markdown and source PNG. Render page number, 144 dpi and `[1224,1584]` dimensions are exact.
- Each page Markdown starts with the exact source-page marker and matching `../renders/source/page-NNN.png` marker. `RECONSTRUCTED_EN.md` is byte-for-byte `b"\n".join(page_001_bytes..page_124_bytes)` and hashes to the protected value.
- `CONTENT_PROVENANCE` has 388 unique `pNNN-bNNN` rows; page/order, predecessor/successor chains and `PAGE_PROVENANCE.block_ids` agree. Raw/rendered hashes are uppercase and current. Current `operations` and `asset_ids` remain empty; every row remains `review_state=needs_review`. The verifier must not invent a semantic operation or ownership link.
- `NAVIGATION_INVENTORY` is a single 124-node chain. Anchor/page/index/path/role/render hash map one-to-one to page provenance. Page 1 has null previous and `page-002` next; page 124 has `page-123` previous and null next; every middle node has the exact adjacent anchors. All links resolve exactly once, with no cycle, fork, gap or dangling target, and every row remains `closure_state=needs_review`.

### Assets, references, entities and role-derived counts

`ASSET_PROVENANCE` is a bijection with the 204 live engine JPEGs under the fixed `hybrid_auto/images/` prefix. Asset ids, engine-relative paths and hashes are each unique; path/bytes/hash/MIME bind disk and the recovery manifest. All recovery-manifest bindings are current. Exactly 112 rows have reference count 1 and 92 have count 0; total references are 112. Reference locations use the one engine Markdown path and unique occurrences 1..112, and the referenced target at each occurrence resolves to that row's engine-relative image. All 204 ownership values remain null and all closure states remain `needs_review`; findings distinguish referenced placement/ownership review from unreferenced engine evidence.

`ENTITY_INVENTORY` and `HANDOUT_INVENTORY` contain byte-equivalent 39-row logical sets, exact ordinals 1..39, unique ids/labels and `required_count=39`; all remain `mixed`/`needs_review`. `CONTENT_MODE_REVIEW` is exactly pages 1..5, current contract value `unknown`, proposal `mixed`, reviewer state `needs_review`. `REFERENCE_ONLY_AUDIT` is empty with `historical_material_opened=false`.

Maps/pregens/back-cover are role-derived page closures, not fabricated semantic acceptance: page-provenance/navigation roles yield exactly 7 keeper-map pages, 13 pregenerated-investigator pages and one back cover. QA/COMMANDS counts must equal those derived facts.

### COMMANDS and 31-sheet enforcement

`COMMANDS.json` top-level state is `candidate_needs_review`; records are exactly ordered `preflight`, `remediate`, `contact_sheets`, `verify`, without duplicate or extra action. Every record has exactly the six explicit false flags `build_invoked`, `mineru_invoked`, `ocr_invoked`, `gpu_or_model_invoked`, `network_invoked`, `external_source_used`, plus `source_flag=--source`, `run_root_flag=--run-root`, and the exact local `source_relative_path`. The verify record has `deterministic=true`.

The count map has exactly 11 keys and live-derived values: pages/renders/contact sheets/handouts/maps/pregens/back cover/assets/referenced assets/unreferenced assets/Markdown references = `124/124/31/39/7/13/1/204/112/92/112`.

The contact-sheet record has `count=31`, coverage `[1,124]`, and exactly `sheet-001`..`sheet-031`. Every sheet has `grid=2x2`, fixed candidate-relative path and live hash, and four ordered page records. Flattened pages are exactly 1..124 once; every render path/hash equals the corresponding page-provenance row and live render. There is no trust in the command record's own counts or hashes.

### QA exact state and no fabricated closure

QA has exactly the 23 current top-level fields. Enforce all authority hashes, state and the nine scalar counts: pages 124, handouts 39, blocks 388, assets 204, sheets 31, navigation 124, referenced/unreferenced 112/92 and open blockers 4. Enforce every key/value of the exact 14-key count map: assets 204, back cover 1, sheets 31, engine images/payload 204/209, handouts 39, maps 7, navigation 124, blockers 4, pages/renders 124/124, pregens 13, referenced/unreferenced 112/92.

Enforce all nine gates exactly: identity/recovery/page/sheet/asset/navigation gates `pass`; `visual_review` and `page_1_5_modes` `needs_review`; `promotion=blocked_candidate_only`. Enforce `historical_material_opened=false`, `main_scripts_invoked=false`, exact inventory rule/count/digest/array and `state=candidate_needs_review`. No value may claim final semantic correctness, reading order, placement, ownership, reconstruction acceptance, promotion, release or publication.

## Writer/finalizer ordering and restored build semantics

### Shared finalizer

There is one production finalizer, called by every writer after all non-QA artifacts for its declared stage are closed. It:

1. reads authoritative live evidence; never copies stale QA-derived facts;
2. validates the stage's closed topology and relationships;
3. constructs stage-appropriate `COMMANDS` before inventory finalization;
4. enumerates the post-command inventory excluding only QA;
5. derives QA bytes twice in memory and requires equality;
6. writes QA once using UTF-8/no-BOM, sorted keys, two-space indent, LF-final serialization; and
7. immediately calls the same shared strict verifier with the immutable stage profile.

The live candidate is not re-finalized in this slice. Existing `remediate()` remains repeat-refusing on the post-state and, if maintained, must delegate validation/finalization rather than retain a divergent QA implementation.

### `build()` fresh-root/refuse-overwrite contract

Restore the public four-argument `build(contract_path, source_path, recovery_root, run_root)` used by the unchanged CLI. Before any write it runs repository/source/sidecar/contract/recovery admission, validates that `run_root` is a safe scenario reconstruction child, and proves the complete target path is absent. An existing file, directory, symlink, junction, reparse entry or dangling link at the target is an overwrite refusal. It must not delete, empty, merge, normalize or reuse a target.

Only after all read-only admission succeeds may it create the root once and call the fixed production non-QA writer. That writer consumes only the admitted local source and hash-bound recovery payload; it must not invoke MinerU/OCR/GPU/model/network, historical material or an external locator. It writes deterministic contract/source/recovery/page/render/content/asset/entity/handout/navigation/mode/reference/blocker/command artifacts, keeps uncertainty open, then calls the shared finalizer. A post-create failure leaves a blocked partial root for orchestrator inspection; `build()` must not self-delete or retry.

The build-stage command trace uses existing schema v3 and truthful actions (including `build`, not a fabricated `remediate`); this affects only a future fresh root, never the protected live candidate. The shared verifier accepts only the exact immutable profile for the declared stage, not arbitrary caller counts.

No live build command is authorized for this completion. P2 evidence is limited to the three hermetic tests below.

## Hermetic bundle and exact mutation matrix

### Fixture contract

`test_scenario_source_reconstruction.py` owns one factory that creates a complete valid temporary bundle with the production topology and small deterministic bytes: fake admitted source/sidecar/contract, 211-file recovery authority, 502-file candidate, 124 page Markdown/render rows, 31 sheets, 204 engine JPEGs, 388 content rows, 39 handouts, ten evidence JSON files, current QA/COMMANDS shapes and all cross-hashes. It injects repo root/branch/HEAD; it does not open the real PDF/candidate/recovery, invoke Git, spawn external tools, use network, create caches or inspect historical material.

Every ordinary negative case starts from a newly created valid fixture, applies exactly one logical mutation and expects `ReconstructionStop` with the named earliest failure code. For a semantic JSON mutation, the test helper re-seals only transport inventory/hash metadata so the intended semantic gate is reached; it must not repair the mutated fact. Missing/stale-inventory tests intentionally do not re-seal. The two historical cluster regressions below are the only deliberate multi-field specimens.

### Required Step 6A-specific coverage/count table

The following expansion is binding. Parameterization may organize code, but `pytest --collect-only` must expose the case ids and exactly **371 Step 6A-specific pytest nodes**. The protected contract suite currently contributes 119 nodes by accepted evidence (127 combined minus the live eight focused functions); with the contract-test file unchanged, the expected combined count is **490**. The executor must collect and report focused and combined counts separately; if the protected contract count is not 119, stop rather than changing this packet or the contract tests.

| Prefix | Coverage expansion | Nodes |
|---|---|---:|
| `POS` | complete valid verify twice; canonical 502/501/500 inventories; deterministic finalizer bytes; exact local-source admission; stable success payload | 5 |
| `REP` | wrong branch; wrong HEAD | 2 |
| `SRC` | six source path/identity/reparse cases; twelve sidecar raw-field/policy cases | 18 |
| `AUT` | five contract/snapshot cases; eleven source-identity cases; fourteen recovery manifest/evidence/payload cases | 30 |
| `TOP` | four root/escape/reparse cases; nine closed-topology missing/extra cases; eight explicit forbidden-class cases | 21 |
| `SCH` | wrong schema for each of 16 authorities; one missing required top-level member for each; one unexpected closed-shape member | 33 |
| `LED` | open count; row count; row state; review state; blocker-id set; affected scope/count | 6 |
| `INV` | the 18 inventory mutations listed below | 18 |
| `PAG` | the 28 page/content/master mutations listed below | 28 |
| `NAV` | the 15 navigation mutations listed below | 15 |
| `AST` | the 21 asset/reference mutations listed below | 21 |
| `SEM` | the 18 entity/handout/mode/reference/role mutations listed below | 18 |
| `CMD` | four action-set, one state, twelve false-flag, six runtime-argument, one external-locator, 22 count-map and 15 sheet/action mutations | 61 |
| `QAV` | 23 missing top fields, one extra field, one state, four authority, nine scalar, 28 count-map, 18 gate, two boolean and four inventory-metadata mutations | 90 |
| `REG` | two historical P1 family specimens | 2 |
| `BLD` | fresh-root success; overwrite refusal/no mutation; build/finalizer parity | 3 |
| **Total** | **Step 6A-specific only** | **371** |

The exact isolated mutation selectors are:

- `REP`: branch and HEAD independently wrong.
- `SRC`: byte-identical source at another path; exact sidecar external locator as runtime source; source missing; wrong bytes; wrong hash; source reparse; sidecar missing; wrong raw hash; wrong working path/bytes/hash/page/media/rotation; `runtime_dependency=true`; external path allowed; wrong subsequent path; generated origin marked source.
- `AUT`: wrong contract path/raw/canonical content; wrong snapshot bytes/hash; each source-identity contract/source page/media/rotation/recovery/root/history/state binding; wrong recovery root/raw hashes/count/bytes; manifest row path/bytes/hash/duplicate; forbidden recovery payload; recovery source/payload/allowed-path/promotion mismatch.
- `TOP`: wrong candidate root; root escape; root reparse; nested reparse; missing/extra top entry; missing/extra evidence; missing page/render/sheet/engine file; nonempty protected-empty subtree; one case for each explicit forbidden class group (`pdf`, compiled suffix, `__pycache__`, bridge runtime, cache, pytest cache, tmp, temp).
- `SCH`: each exact schema string above; required top-level shape per authority; unexpected member rejection.
- `LED`: the six ledger dimensions in the table, while QA transport is re-sealed when needed.
- `INV`: missing ordinary file; missing evidence; missing sheet; stale/extra path; duplicate path; QA included; wrong cardinality; non-ordinal order; wrong bytes; wrong hash; lowercase hash; wrong digest; backslash; absolute/drive path; `..`; leading `./`; wrong row key shape; live file changed behind a stale row.
- `PAG`: missing page row; duplicate page row; wrong page number; wrong page id; wrong engine index; wrong role; wrong contract-mode mapping; independently wrong Markdown path, bytes and hash; independently wrong render path, bytes, hash, page number, dimensions and dpi; missing live Markdown; missing live render; wrong source-page marker; wrong render marker; master concatenation mismatch; orphan content block; duplicate content block; wrong block order; wrong predecessor; wrong successor; fabricated operation; fabricated asset linkage.
- `NAV`: missing row; duplicate anchor; wrong anchor id; wrong source page; wrong engine index; non-null first previous; non-null last next; wrong middle previous; wrong middle next; dangling link; wrong Markdown path; wrong render path; wrong render hash; wrong role; promoted closure.
- `AST`: missing row; duplicate id; duplicate path; duplicate hash; wrong live bytes; wrong live hash; missing engine path; wrong engine path; wrong recovery binding; total reference conservation; unreferenced conservation; reference count outside 0/1; missing occurrence; duplicate occurrence; wrong Markdown path; target absent from engine Markdown; non-null ownership; promoted closure; finding mismatch; wrong live engine-image cardinality; wrong MIME.
- `SEM`: entity ordinal gap; duplicate entity id; handout gap; duplicate handout id; entity-handout inequality; wrong `required_count`; wrong label; wrong page range; promoted entity closure; mode-row gap; duplicate mode row; promoted mode review; nonempty reference-only rows; historical material true; wrong 7-map derivation; wrong 13-pregen derivation; wrong one-back-cover derivation; wrong 39-handout derivation.
- `CMD`: missing, duplicate, extra and reordered action independently; promoted state; each of six false flags independently missing and independently true; each source/run-root/source-path field independently missing and wrong; external locator; each of 11 count keys independently missing and independently wrong; wrong contact-sheet count; wrong coverage; missing sheet; duplicate sheet; wrong sheet id; wrong sheet path sequence; wrong grid; wrong sheet hash; missing flattened page; duplicate flattened page; out-of-order flattened page; wrong render path; wrong render hash; page/render mapping disagreement; verify determinism false.
- `QAV`: remove each of the exact 23 live top-level fields independently; add an extra field; promoted state; wrong contract/source/recovery-manifest/recovery-evidence hash; wrong each of nine scalar counts; each of 14 `counts` keys missing and each wrong; each of nine gate keys missing and each wrong/closed; historical/main-script boolean true; wrong inventory rule/count/digest/array.
- `REG-P1-STALE-METADATA`: one preserved old-family specimen combines QA v2, stale recovery manifest, absent recovery-evidence hash, blocker count 3 and 470-row stale inventory; it must fail at the earliest QA schema code. The isolated `AUT`/`LED`/`INV`/`QAV` cases prove every component separately.
- `REG-P1-MISSING-ENFORCEMENT`: mutate a formerly unchecked `COMMANDS.counts.pages` value, re-seal transport inventory, and require `E_COMMAND_COUNTS_PAGES`; this proves the old partial verifier cannot remain the enforcement boundary.
- `BLD`: only hermetic fresh-root success, existing-target refusal with byte-identical pre/post target, and QA/inventory bytes identical between `build()` and direct shared-finalizer application. No live build and no extra build-behavior test class are authorized.

Static source-string assertions are supplementary only. A green combined count without the 371-node focused collection and case-id coverage table is insufficient.

## Correct-cwd local-source-only acceptance commands

After a fresh independent design review returns no open P0/P1, the executor runs only these commands from the exact worktree. There is no live `build` or `remediate` command.

```powershell
Set-Location 'D:\NRI\.worktrees\kb-creator-viral'
python -B -m pytest kb_creator/tests/test_scenario_source_reconstruction.py --collect-only -q -p no:cacheprovider
python -B -m pytest kb_creator/tests/test_scenario_source_reconstruction.py -q -p no:cacheprovider
python -B -m pytest kb_creator/tests/test_scenario_contract.py kb_creator/tests/test_scenario_source_reconstruction.py --collect-only -q -p no:cacheprovider
python -B -m pytest kb_creator/tests/test_scenario_contract.py kb_creator/tests/test_scenario_source_reconstruction.py -q -p no:cacheprovider
python -B kb_creator/scripts/reconstruct_scenario_source.py preflight --contract kb_creator/contracts/viral.json --source kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf --recovery-root kb_creator/working/viral/source_reconstruction/20260831_step6a_engine_output_salvage_candidate --run-root kb_creator/working/viral/source_reconstruction/20260831_step6a_reconstruction_from_salvaged_engine_candidate
python -B kb_creator/scripts/reconstruct_scenario_source.py verify --contract kb_creator/contracts/viral.json --source kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf --recovery-root kb_creator/working/viral/source_reconstruction/20260831_step6a_engine_output_salvage_candidate --run-root kb_creator/working/viral/source_reconstruction/20260831_step6a_reconstruction_from_salvaged_engine_candidate
python -B kb_creator/scripts/reconstruct_scenario_source.py verify --contract kb_creator/contracts/viral.json --source kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf --recovery-root kb_creator/working/viral/source_reconstruction/20260831_step6a_engine_output_salvage_candidate --run-root kb_creator/working/viral/source_reconstruction/20260831_step6a_reconstruction_from_salvaged_engine_candidate
```

Focused collection must be 371 and focused execution `371 passed`; combined collection/execution must be 490 with the protected contract suite still 119. Preflight and both verifies exit 0, use only the exact local source, and report the required branch/HEAD. The two verify stdout payloads and their SHA-256 values are byte-identical. No cache provider, `.pyc`, temp artifact or probe may remain.

## Executor stop conditions

Stop before the first write on any branch/HEAD, source/sidecar/contract/recovery, packet/review, code/test baseline, candidate 502/501/500, raw QA/COMMANDS, render manifest, protected-document dispatch snapshot, path containment or reparse mismatch. Stop if the design review has any unresolved P0/P1, target receipt already exists, or exact changes cannot fit the three-path executor allowlist.

After the first write, stop and report blocked on any candidate/source/recovery/CLI/contract-test/protected-document delta; missing case id; focused count other than 371; combined contract count other than 119; test/collection failure; nondeterministic output; strict verify/preflight failure; forbidden process/access; candidate promotion; semantic closure; or Git mutation. Do not widen the allowlist, edit QA/COMMANDS, re-finalize the live candidate, run `remediate`, run `build`, invoke MinerU/OCR/model/network, use history, delete a partial artifact or amend canonical orchestration state.

## Mutation audit and receipts

Before execution capture:

- exact branch/HEAD and `git status --short --branch`;
- raw hashes/lengths of both mutable implementation/test files and all protected paths named above;
- source/sidecar/contract/snapshot/recovery/packet/design-review hashes;
- candidate raw QA/COMMANDS hashes and 502/501/500/155/124/31 manifests; and
- dispatch-window protected orchestration path set/existence/length/hash records.

After execution repeat every item and produce exact added/modified/deleted comparisons. The only material modifications are the library and focused test; the only new path is the executor receipt. Candidate manifests and QA/COMMANDS raw hashes must be unchanged. No deletion is allowed.

The executor receipt records goal/step/role/model/effort or `unavailable`, orchestrator owner, assignment state, scoped override, timestamp/elapsed/token use, worktree/branch/HEAD, packet/design-review hashes, pre/post allowlist hashes, all command lines/exit codes/stdout hashes, focused and combined collected/passed counts, the 371-case coverage table, preflight/verify identities, unchanged source/recovery/candidate/visual/protected bindings, exact mutation audit, P1/P2 disposition, forbidden-action declaration, remaining blockers, result and next action.

## Visual carry-forward and final gates

The prior 67/67 original-resolution and 31/31 sheet review may carry forward only if the prior QA receipt remains `194BF7...`, candidate 500-manifest remains `98FC41...`, visual 155/124/31 manifests remain `19F600...` / `C6C14D...` / `B66EF1...`, QA/COMMANDS raw hashes remain `C38CB0...` / `916265...`, and the mutation audit contains no candidate path. Any mismatch voids carry-forward and is a stop; this packet does not authorize a visual rebuild or re-review workaround. Carry-forward never closes semantic/reading-order/placement/ownership uncertainty.

Gate sequence is mandatory:

1. fresh independent `gpt-5.5` / `medium` design review of this packet, no unresolved P0/P1;
2. bounded executor implementation and receipt;
3. separate bounded QA that independently collects/runs 371 focused and 490 combined nodes, runs preflight/strict verify twice, recomputes all candidate/source/recovery/visual bindings and audits the exact mutation set;
4. fresh independent `gpt-5.5` / `medium` implementation/process review, with no implementer/designer participation and no unresolved P0/P1/P2; and
5. orchestrator integration only after those receipts are immutable and hash-bound.

Passing these gates closes only enforcement-layer P1 and reusable-build P2. The candidate remains `candidate_needs_review`; semantic/reading-order correctness, placement/layout fidelity, asset ownership/usage and broader human review remain open. `MASTER_EN`, promotion, release, publication, staging, commit and push remain unauthorized.

## Architecture-task mutation audit

This architecture task writes only `sol_architect_viral_step6a_enforcement_completion_packet_20260831.md`. Code, tests, CLI, candidate, source, sidecar, contract, recovery, render evidence, plan/context/status/README, prior packets/receipts and Git state are read-only. No Yandex path was opened; no build, remediation, verifier execution, test execution, MinerU/OCR/model/network/history/translation or Git mutation was performed.

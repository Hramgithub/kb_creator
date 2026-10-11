# Viral Step 7 MASTER_EN C2b verifier and candidate-sidecar contract

- Goal id: `20260830-kb-creator-next-scenario`
- Step id: `7 / C2b independent verifier and candidate sidecars`
- Timestamp: `2026-09-01` (`Europe/Moscow`)
- Role: architecture/root-cause, repository policy `gpt-5.6-sol` / `high`
- Actual platform model/effort: unavailable
- Orchestrator policy owner: `/root`, repository-policy `gpt-5.6-sol` / `medium`; ownership did not transfer
- Assignment state: bounded architecture complete; engineering not started
- Scoped override: sole write was this immutable receipt; every existing code, test, config, source, reconstruction, candidate, plan, context, status, Git and release surface remained read-only
- Verdict: `READY_FOR_ENGINEERING`
- Elapsed time: approximately 34 minutes
- Token use: unavailable

## 1. Accepted boundary and assumptions

C2a is accepted by `gpt55_critic_viral_step7_master_en_c2a_re_review_20260901.md`, 8,146 bytes / SHA-256 `B2933FD4B352A5C2CE97310F720312C5C96A394B7B59824F32765359830B5BCC`. The accepted temporary reader is 358,622 bytes / SHA-256 `17528F1543738CA5FAE1A215237B6F7476A9483B015D1C41889213DFA140B010`.

Pinned current implementation inputs are:

- builder: 57,356 bytes / `2851993F8E0B7420706E38E3E781744375826A8E77886E3FB4B632D519FA79AF`;
- verifier scaffold: 1,920 bytes / `F36DC836493DAC1686C033E1564AC70CDBCA6CDED1B8634CA8EB7C7E6D2FFFF5`;
- builder tests: 26,784 bytes / `96460BE29C094AB7C2B3FBAF9A8E6C472C73619527856F53805DDE35D85D7B07`;
- verifier tests: 1,336 bytes / `FCF6BB96AFA3074F936BA19422319F39902374728C8D481F74E0DD14C7784836`;
- publication config: 660,329 bytes / `CEAA522F8ADA7EF2453D52F0DE4D098733EA5A7D55B12BE96694094891767BF3`;
- runtime contract: 4,582 bytes / `67688867D4971D55137C2E4E7A71A746199596EDE4F5DD18577F4331CA87536D`;
- accepted reconstruction inventory: 377 files / 41,079,424 bytes / `68C17FB765A89C6146398868E61F1F6EB7B2FE4EAFBA8C2C2C8F42260BBDBA83`;
- immutable source PDF: 20,718,150 bytes / `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05`.

The config remains the sole scenario policy. No schema/config/source change is needed for C2b. The verifier must not import, execute, or dynamically load the builder and must not accept builder counts, hashes, status, provenance, QA or inventory without independent recomputation. A common new helper module would collapse the independence boundary and is not permitted in this minimal pass.

There is no durable candidate yet. This receipt authorizes engineering of behavior only, not a production build.

## 2. Exact CLI and atomic staging-to-target behavior

Both entry points retain the existing required arguments:

```powershell
python -B kb_creator/scripts/build_scenario_master_en.py `
  --contract kb_creator/contracts/viral.json `
  --reconstruction-package kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4 `
  --publication-config kb_creator/working/viral/master_en/publication_config_v1.json `
  --source-pdf kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf `
  --target kb_creator/working/viral/master_en/candidates/<candidate-id>

python -B kb_creator/scripts/verify_scenario_master_en.py `
  --contract kb_creator/contracts/viral.json `
  --reconstruction-package kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4 `
  --publication-config kb_creator/working/viral/master_en/publication_config_v1.json `
  --source-pdf kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf `
  --target kb_creator/working/viral/master_en/candidates/<candidate-id>
```

`--preflight-only` remains supported on both commands. Builder preflight performs the current read-only checks and creates no candidates directory, target or staging root. Verifier preflight must replace the current builder subprocess delegation with its own closed parser and identity/inventory checks; it must neither import nor run the builder.

Normal builder mode:

1. Resolve repository root from the config location. The target must be an immediate child of exactly `kb_creator/working/<scenario_id>/master_en/candidates`, and `<candidate-id>` must match `[a-z0-9][a-z0-9._-]{0,63}`. Absolute paths, `.`/`..`, backslashes, drive/UNC forms and alternate spellings are rejected.
2. Complete every input/schema/tool preflight before creating any directory. The exact candidates parent may be created only after preflight, beneath the already existing `master_en` directory.
3. Refuse an existing target of any type, including a dangling link, junction or reparse point. Recheck immediately before publication.
4. Create one private sibling staging directory on the same volume, named outside candidate content as `.<candidate-id>.staging.<opaque>`. The opaque suffix is never serialized.
5. Write assets, `MASTER_EN.md`, provenance, disposition, asset manifest, QA JSON, deterministic QA Markdown, then `INVENTORY.json`. Close file handles and run builder-owned self-consistency checks in staging.
6. Publish only by one same-parent directory rename from staging to the still-absent target. There is no copy-merge and no overwrite path. Success stdout is one sorted JSON object with status `candidate_built_for_independent_verification`, scenario id, target inventory digest, inventory-file SHA and MASTER_EN SHA; these are informational claims only.
7. A preflight failure leaves no directory. A failure after staging creation leaves the private staging root in place and reports its path; it is not renamed, not called a candidate and not automatically deleted. A verifier failure after publication leaves the review candidate intact and unaccepted.

The builder never invokes the verifier. The verifier is strictly read-only on the candidate and writes only its stdout/stderr; evidence is captured later in an external immutable receipt.

## 3. Closed candidate topology and serialization

The candidate has exactly one subdirectory, `assets`, and these seven root files:

```text
MASTER_EN.md
MASTER_EN.provenance.json
SOURCE_DISPOSITION.json
ASSET_MANIFEST.json
MASTER_EN.qa.json
MASTER_EN.qa.md
INVENTORY.json
assets/<lowercase-sha256>.<jpg|png>
```

For the current config, `assets` contains exactly 123 regular files: 121 byte-identical accepted assets plus two independently reproducible source-page renders. Exactly 107 are referenced once in the reader and 16 are evidence-only and never referenced. There are 130 candidate files total; `INVENTORY.json` contains 129 rows because it excludes itself.

`MASTER_EN.acceptance.json`, configuration/source copies, logs, caches, temporary renders, receipts, hidden files, alternate asset names and empty/extra directories are forbidden.

All text is UTF-8 without BOM, LF only, and ends with exactly one LF. Canonical JSON is `json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"`; arrays retain their declared/derived order. Paths inside sidecars are repository-relative or candidate-relative POSIX paths. No absolute path, drive, UNC prefix, backslash, empty component, `.` or `..` is legal. No timestamp, hostname, PID, staging name or current-time value is serialized.

Every candidate node and each ancestor used to reach it is checked with `lstat`. Symlinks and, on Windows, any `FILE_ATTRIBUTE_REPARSE_POINT` node (including junctions) are rejected before `resolve`; every allowed file must then resolve inside the candidate root. The same rule applies to declared input roots/files. Extra files are errors even when not listed in the inventory.

## 4. Closed sidecar schemas

All objects below are exact-key objects; missing and unknown keys fail. All hashes are uppercase 64-hex SHA-256 and all byte/range/count values are non-boolean non-negative integers.

Common `file_identity` is exactly `{path, bytes, sha256}`. Candidate paths are candidate-relative; input paths are repository-relative.

### `MASTER_EN.provenance.json`

Top keys are exactly:

```text
schema, scenario_id, candidate_state, offset_unit, producer, inputs,
master_en, units, structured_units
```

- `schema = kb_creator.master_en_provenance.v1`; `scenario_id = viral`; `candidate_state = candidate_for_independent_verification`; `offset_unit = utf8_bytes`.
- `producer` is exactly `{script_path, script_sha256}` for the live builder file. It is provenance, not an acceptance claim.
- `inputs` is exactly `{contract, publication_config, source_pdf, accepted_reconstruction}`. The first three are `file_identity`. `accepted_reconstruction` exactly mirrors the config-pinned `{root,file_count,total_bytes,inventory_algorithm,inventory_sha256,reconstructed_md,qa,provenance,asset_manifest,acceptance_receipt}` with each nested file identity exact.
- `master_en` is its candidate-relative file identity.
- `units` contains exactly 168 rows in binding order. Each row is exactly `{anchor,binding_order,operations,source_fragments,output_fragments,asset_ids,xref_ids,structured_ids}`. `operations` is a nonduplicated ordered subset of `retained,structured,relocated,linked,visualized`. A source fragment is exactly `{page,start,end,sha256}` over immutable accepted-page UTF-8 bytes. An output fragment is exactly `{start,end,sha256}` over `MASTER_EN.md` UTF-8 bytes. Half-open ranges are ordered, in bounds and non-overlapping within each list. Every emitted reader byte belongs to the independently reconstructed unit/block plan; every source fragment is consumed once or belongs to a config-declared generated/visual disposition.
- The union of unit `xref_ids`, `structured_ids` and `asset_ids` is respectively the exact 237 xref ids, 29 structured ids and 107 reader-asset ids, each exactly once in its owning unit. Evidence-only assets do not appear in unit `asset_ids`.
- `structured_units` contains exactly 29 rows in placement order. Semantic rows have exactly `{structure_id,classification,logical_owner,representation,fragments,attached_notes}`. Visual-form rows have exactly `{structure_id,classification,logical_owner,representation,asset_id,asset_sha256,review_ids,emitted_occurrence,fragments,attached_notes}`. Each semantic fragment is exactly `{source_page,binding_anchor,source_start,source_end,source_sha256,source_format,emitted_start,emitted_end,emitted_sha256}`; each attached note is the same closed source/emitted identity plus its exact selector text. Visual rows require `emitted_occurrence = 1`, empty fragments/notes, the exact staged asset hash and both configured review ids.

### `SOURCE_DISPOSITION.json`

Top keys are exactly `{schema,scenario_id,pages,summary}` with schema `kb_creator.source_disposition.v1`. `pages` is the exact 124-row config projection in numeric page order; every row and sub-unit retains the config's closed keys and repository-relative source path. `summary` is exactly `{page_count,sub_unit_count,unauthorized_suppression_count}`. The last value is zero. The verifier compares the complete projection and independently recomputes page/block ownership; matching the summary alone is insufficient.

### `ASSET_MANIFEST.json`

Top keys are exactly `{schema,scenario_id,assets,summary}` with schema `kb_creator.master_en_asset_manifest.v1`. `assets` has exactly 123 config-order rows, each exactly:

```text
asset_id, origin, logical_name, source, output_path, bytes, sha256,
media_type, dimensions, source_page, source_region, semantic_role,
representation, owner_anchor, placement_index, alt_text,
visual_review_status
```

For `accepted_reconstruction_asset`, `source` is exactly `{kind,path,bytes,sha256}` with `kind = accepted_reconstruction_asset`. For `source_page_render`, it is exactly `{kind,source_pdf,render}` and carries the full closed config declarations with `kind = source_page_render`. `output_path` is `assets/<sha256-lowercase>.<ext>`, unique and type-correct. `visual_review_status` is always `pending_external_visual_qa`. `summary` is exactly `{total,reader,evidence_only,accepted_reconstruction_asset,source_page_render}` and currently derives to `123/107/16/121/2`.

### `MASTER_EN.qa.json` and `MASTER_EN.qa.md`

QA JSON top keys are exactly `{schema,scenario_id,candidate_state,artifacts,metrics,gates,errors}` with schema `kb_creator.master_en_qa.v1`, candidate state `candidate_for_independent_verification`, and `errors = []` for a published candidate. `artifacts` is exactly `{master_en,provenance,source_disposition,asset_manifest}` using candidate file identities; it deliberately omits QA, QA Markdown and inventory to avoid hash cycles.

`metrics` is a closed object derived from bytes, never constants: `{source_pages,anchors,links,xrefs_executed,source_xref_rows,source_xref_segments,handouts,structured_units,reader_assets,candidate_assets,visual_review_units,total_blocks,owned_blocks,generated_blocks,unowned_blocks,duplicate_blocks,unauthorized_suppression_blocks,reader_noise_findings,editorial_lexical_deltas}`. Current expected values derive to `124,168,237,237,41,42,41,29,107,123,91,1935,1862,73,0,0,0,0,0`.

`gates` is ordered exactly as follows; each row is exactly `{gate,status,evidence,errors}`:

1. `accepted_reconstructed` — builder may report `pass`;
2. `source_disposition` — `pass`;
3. `semantic_navigation` — `pass`;
4. `handout_mapping` — `pass`;
5. `table_statblock_closure` — `pass`;
6. `asset_closure` — `pass`;
7. `no_technical_reader_noise` — `pass`;
8. `lexical_conservation` — `pass`;
9. `closed_inventory_serialization` — `pass`;
10. `independent_candidate_verifier` — `pending`;
11. `two_clean_build_determinism` — `pending`;
12. `full_visual_qa` — `pending`;
13. `independent_gpt55_release_review` — `pending`;
14. `explicit_user_reading_acceptance` — `pending`.

`evidence` is an ordered list of stable sidecar/metric identifiers, never prose paths outside the candidate. `errors` is an array and is empty for both `pass` and intentionally pending rows. The last three rows must equal the config external gates and may never be `pass` in a builder candidate. The process-gate rows 10-11 also remain pending because independent verification and two-run proof occur outside immutable candidate bytes.

`MASTER_EN.qa.md` is a deterministic fixed rendering of the QA JSON: one H1, candidate-state line, artifact table, metrics table, ordered gate table, and an explicit statement that no acceptance exists. It contains no extra facts. The verifier regenerates it from independently validated QA JSON and requires byte identity.

### `INVENTORY.json`

Top keys are exactly `{schema,algorithm,scope,rows,file_count,total_bytes,inventory_sha256}` with schema `kb_creator.candidate_inventory.v1`, the algorithm string `SHA-256 over ordinal UTF-8 LF relative_path<TAB>bytes<TAB>UPPER_SHA256<LF>`, and scope `all regular candidate files except INVENTORY.json`.

Rows are exactly `{path,bytes,sha256}`, sorted by Python/codepoint ordinal POSIX relative path. The digest input is one UTF-8 line per row: `path<TAB>bytes<TAB>UPPER_SHA256<LF>`. `file_count`, `total_bytes` and digest are recomputed from the 129 physical files. Candidate identity is the tuple `(SHA-256 of INVENTORY.json bytes, inventory_sha256, MASTER_EN.sha256)`; no file can self-attest the first member.

## 5. Builder claims versus independent verifier facts

The builder may write only claims directly observed while constructing staging: input identities, exact source/output ranges and hashes, transformation ownership, xref/structure/asset ledgers, canonical sidecar bytes, the nine automatable self-check gates and inventory. It may never claim independent verification, two-run determinism, visual QA, critic review, user acceptance, release or promotion.

The verifier independently performs these steps without builder code or results:

1. Parse CLI and enforce repository/target/reparse boundaries.
2. Enumerate the physical candidate tree before trusting inventory; reject every extra/missing/non-regular/reparse node and acceptance file.
3. Decode bytes, reject BOM/CR/noncanonical JSON/Markdown, and validate every closed schema.
4. Re-hash the live contract, config, source PDF, accepted reconstruction files and complete reconstruction inventory; independently validate the config declarations and pending external gates.
5. Independently enumerate the 129 inventory-scope files, recompute every row/count/byte/hash/digest and compare the inventory object. Inventory and QA claims are never short-circuit authorities.
6. Recompute the C1 binding claims and 1,935-block conservation from accepted page bytes; compare the complete disposition projection and recompute all 41 exact source xrefs/42 segments and 196 generated rows.
7. Re-hash and type/dimension-check all 123 assets. Accepted assets must equal their immutable sources byte-for-byte. Independently rerun the two pinned Poppler/Pillow source-page renders into verifier-private temporary storage and byte-compare them; never read `SELECTED_OVERLAY.pdf`.
8. Independently reconstruct expected `MASTER_EN.md` bytes from config, source pages and candidate asset paths, including binding order, fragment interleaving, actions, anchors, links, 41 handouts, 29 structured regions/notes and 107 reader assets; byte-compare to the candidate. Do not use provenance ranges to construct the expectation.
9. Independently derive the complete provenance, asset manifest, QA JSON and QA Markdown objects in memory from inputs/candidate bytes, canonicalize them and byte-compare each sidecar.

Success is exit `0`, empty stderr, and one sorted stdout JSON object with exactly `{status,scenario_id,candidate_inventory_sha256,inventory_file_sha256,master_en_sha256,publication_config_sha256}` and status `verified_candidate_pending_process_and_external_gates`. Verification does not mutate the candidate.

## 6. Stable fail-closed error order

The verifier catches expected failures and returns exit `1`, empty stdout and one deterministic stderr line `CODE: detail`. No traceback is part of the contract. If multiple defects exist, the first phase below wins; within a phase, candidate-relative paths are ordinal and config rows retain declaration order.

| Order | Stable code | Boundary |
|---:|---|---|
| 1 | `E_C2B_ARGS` | missing/invalid CLI or candidate-id form |
| 2 | `E_C2B_TARGET_PATH` | wrong parent, traversal, absolute/drive/UNC/backslash path |
| 3 | `E_C2B_REPARSE` | symlink, junction or reparse node/ancestor |
| 4 | `E_C2B_TOPOLOGY` | missing/extra/non-regular file or directory; acceptance present |
| 5 | `E_C2B_ENCODING` | BOM, CR, invalid UTF-8 or terminal-LF violation |
| 6 | `E_C2B_JSON` | JSON parse/non-object failure |
| 7 | `E_C2B_SCHEMA` | unknown/missing/type/enum/order/closed-schema member |
| 8 | `E_C2B_INPUT_IDENTITY` | contract/config/source/reconstruction pin or inventory mismatch |
| 9 | `E_C2B_INVENTORY` | physical row/count/bytes/hash/digest mismatch |
| 10 | `E_C2B_DISPOSITION` | 124-page projection, ownership or suppression mismatch |
| 11 | `E_C2B_ASSET` | manifest, asset bytes/type/dimensions/ownership/rerender mismatch |
| 12 | `E_C2B_READER` | expected Markdown, anchors, links, xrefs, noise or protected text mismatch |
| 13 | `E_C2B_HANDOUT` | 41-unit physical/narrative/context mapping mismatch |
| 14 | `E_C2B_STRUCTURE` | 29-row region/table/card/statblock/form/note mismatch |
| 15 | `E_C2B_PROVENANCE` | independently derived provenance/range/hash mismatch |
| 16 | `E_C2B_QA_STATUS` | metrics/QA Markdown mismatch or forged process/external PASS |

`detail` identifies only the first stable relative path, id or JSON pointer and contains no device path. Tests assert codes, not Python exception wording.

## 7. Compact behavior-driven tests

Do not revive the historical 371/119/490 mutation matrix. Add only these focused behaviors, using compact production-shaped fixtures and subtests where variants share one invariant:

1. Normal builder CLI creates the exact closed candidate; independent verifier subprocess passes; no acceptance file exists.
2. Two fresh candidate ids from identical inputs yield byte-identical 130-file relative inventories and identical non-self inventory/MASTER hashes.
3. Builder preflight identity failure, occupied target, out-of-parent target and injected staging failure create no target; staging failure is reported and preserved.
4. Verifier source neither imports nor subprocess-executes builder; a candidate verification succeeds with builder execution disabled.
5. Missing/extra/acceptance file and candidate/asset symlink-or-reparse fixtures fail in the documented topology precedence.
6. Absolute/parent/backslash inventory or manifest path fails before any candidate-relative read escapes the fixture.
7. One raw MASTER_EN byte mutation without reseal fails `E_C2B_INVENTORY`; the same mutation with a correctly resealed inventory fails the semantic code (`E_C2B_READER`).
8. One accepted asset mutation and one independently resealed render substitution fail `E_C2B_ASSET`; evidence-only asset reference in reader also fails.
9. A closed-sidecar unknown key and malformed JSON fail their respective ordered codes.
10. A resealed broken anchor/xref, missing protected `a millions subs babez`, and one removed structured attached note fail `E_C2B_READER`/`E_C2B_STRUCTURE` without a broad permutation suite.
11. Forging any of the five pending process/external gates to `pass` fails `E_C2B_QA_STATUS`; deterministic QA Markdown drift also fails.
12. A two-fault fixture proves precedence (for example extra file plus malformed QA JSON returns `E_C2B_TOPOLOGY`).

The real Poppler 26.05.0 two-render proof is a later frozen Luna execution gate, not a required dependency for every unit-test node; tests use the existing renderer command seam and one bounded integration node when the pinned renderer is available.

## 8. Engineering ownership, allowed files and gates

Next owner: Terra/medium reusable engineering. Exact permitted writes:

1. `kb_creator/scripts/build_scenario_master_en.py`
2. `kb_creator/scripts/verify_scenario_master_en.py`
3. `kb_creator/tests/test_build_scenario_master_en.py`
4. `kb_creator/tests/test_verify_scenario_master_en.py`
5. one new immutable `handoffs/terra_engineering_viral_step7_master_en_c2b_verifier_sidecars_20260901.md`

No config, source, reconstruction, candidate, plan/context/status, dependency, Git or release write is permitted in engineering. No new shared verifier/builder module or schema framework is needed.

Engineering commands/gates:

```powershell
python -B -m py_compile kb_creator/scripts/build_scenario_master_en.py kb_creator/scripts/verify_scenario_master_en.py kb_creator/tests/test_build_scenario_master_en.py kb_creator/tests/test_verify_scenario_master_en.py
python -B -m pytest -q -p no:cacheprovider kb_creator/tests/test_build_scenario_master_en.py kb_creator/tests/test_verify_scenario_master_en.py
git diff --check -- kb_creator/scripts/build_scenario_master_en.py kb_creator/scripts/verify_scenario_master_en.py kb_creator/tests/test_build_scenario_master_en.py kb_creator/tests/test_verify_scenario_master_en.py
```

Engineering PASS requires all 12 behavior classes, zero writes outside the five-file scope, normal production CLI still unexecuted, and exact new file hashes/counts in the receipt. It is implementation evidence, not candidate acceptance.

Next review owner after Terra: independent `gpt-5.5` / `high`, review kind `implementation`, read-only except one new review receipt. It must re-run the compact suite, inspect the verifier for builder import/subprocess/shared-helper trust, reproduce one positive fixture plus representative topology/inventory/resealed-semantic/external-gate negatives, and return accept/reject. This is not release review.

Only after accepted implementation may Luna/medium execute a frozen production packet. Luna owns commands/evidence only: pin builder/verifier/tests/config/contract/source/reconstruction/review identities; build two new candidate ids; verify both in separate processes; prove relative-file byte identity and real p1/p124 rerender identity; capture roots/hashes/exit codes; and write one execution receipt. Luna may not edit code/config/sidecars, interpret failures by resealing, run MinerU, or run 371/119/490. The orchestrator then selects/freeze-labels one verified review candidate and schedules Luna/high full visual QA plus later GPT-5.5 release review and explicit user reading acceptance. No promotion occurs in C2b.

## 9. Acceptance criteria, risks and next action

Architecture acceptance criteria are met: candidate topology and each sidecar are closed; inventory is non-self-referential; producer claims are separated from independent recomputation; traversal/reparse/extra-file behavior is fail-closed; publication is atomic; error precedence is stable; tests are risk-bounded; role/file ownership is explicit.

Residual implementation risks are bounded and not user-owned: Windows reparse detection must cover junctions, byte offsets must use UTF-8 rather than Python character indexes, inventory/QA dependencies must remain acyclic, and the verifier's independent reader reconstruction must not call the builder through any direct or indirect seam. These are engineering/review gates, not unresolved content decisions.

No user-owned decision is open. Candidate id selection is an orchestrator execution detail. Next action is the five-file Terra implementation above; candidate construction remains prohibited until that implementation is independently accepted.

## Files checked / changed

Checked read-only: canonical governance; current plan/context and NEXT_CHAT handoff; accepted C2a re-review; Phase A foundation receipt; Step 7 publication architecture and engineering packets; current builder/verifier and both focused tests; current publication config and runtime contract.

Changed: only this receipt. No candidate was created.

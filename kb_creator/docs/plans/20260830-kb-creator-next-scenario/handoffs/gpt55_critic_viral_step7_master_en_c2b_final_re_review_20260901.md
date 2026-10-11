# GPT-5.5/high final C2b implementation re-review — Viral Step 7 MASTER_EN

Timestamp: 2026-09-01T23:42:55+03:00

Review kind: implementation

Decision: REJECT_C2B

Role and scope:

- Reviewer: independent GPT-5.5/high critic role.
- Implemented or materially designed candidate under review: no.
- Orchestration ownership: remains with the gpt-5.6-sol orchestrator; this review does not transfer policy, release, or candidate ownership.
- Assignment state: fresh final C2b re-review after Terra v3 exact locator-binding remediation.
- Scoped override: implementation review only; no release approval; no fixes implemented. Sole authorized write was this immutable receipt.

## Files and inputs checked

- Prior critic receipt 1: `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_step7_master_en_c2b_implementation_review_20260901.md`
  - SHA-256: `67D038C0C1D6DD5277468C0B691DE40B796C17DBD6AAA5760EA8F744685B0A8B`
- Prior critic receipt 2: `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_step7_master_en_c2b_re_review_20260901.md`
  - SHA-256: `93DF97842C68D407AE5E12F54CC339F21E7EEAD4FC0B65CC262DB4FB624244A6`
- Corrected minimal architecture: `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_viral_step7_master_en_c2b_minimal_independent_verifier_correction_20260901.md`
  - SHA-256: `2C7B7C0842F3833FA5CEFFFB9EB2FC73700F51CFE9D4C11A4D84CE84D89D865E`
- Terra v3 remediation receipt: `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_step7_master_en_c2b_critic_remediation_v3_20260901.md`
  - SHA-256: `09BCDC9B8874D7AEE055D8794BE0226B168C3ADEE14DD379062440B436CF8E75`
- Current verifier: `kb_creator/scripts/verify_scenario_master_en.py`
  - bytes: `20164`
  - SHA-256: `36659286C0B1ACBB452775A43D40E8657F5C34652EC8E9677AFDA4DA2084DE23`
- Current verifier tests: `kb_creator/tests/test_verify_scenario_master_en.py`
  - bytes: `10088`
  - SHA-256: `64A35F211C404368E9C1A9544DAA00C6C289091C04D08D11E2C0192911F44420`
- Builder: `kb_creator/scripts/build_scenario_master_en.py`
  - bytes: `70773`
  - SHA-256: `82C720B572A73B33DF9D2548BB3FD4CB8BAE81660AE21D4273DEB984C99EDA1C`
- Builder tests: `kb_creator/tests/test_build_scenario_master_en.py`
  - bytes: `26786`
  - SHA-256: `01BDFFFC6F32833E3EF5EF831A85F30775883C1E20B5E9B5B3C0687A58AD33DF`
- Publication config: `kb_creator/working/viral/master_en/publication_config_v1.json`
  - bytes: `660329`
  - SHA-256: `CEAA522F8ADA7EF2453D52F0DE4D098733EA5A7D55B12BE96694094891767BF3`
- Governance/context read:
  - `AGENTS.md` SHA-256 `29408DBF2D7395C1D7575D02F4DABB0B370AF0FB0F2381A5AF859072ECFFC30B`
  - `docs/governance/nri_goal_governance.md` SHA-256 `263151DEB9CD6E8DBC1810D8654A4777F620C01787A53F0B5CAB1B83F4EC427F`
  - `plan.md` SHA-256 `64C62A04F15A7C54B6B16A29B3B3F561C048A119E34B33F8BD68D53983D0185E`
  - `context.md` SHA-256 `B2B20E8424AFC7D6D0019ED1DE3F4349BEB86574BE4533BC8EC8570E1CC62610`

## Static implementation inspection

Verifier isolation:

- AST imports in `verify_scenario_master_en.py`: `__future__.annotations`, `argparse`, `hashlib`, `json`, `os`, `re`, `stat`, `sys`, `pathlib.Path`.
- No verifier lexical hits for `build_scenario_master_en`, `importlib`, `subprocess`, `runpy`, `exec(`, `eval(`, `__import__`, or `shared`.

Verifier v3 improvements observed:

- Exact locator resolver exists at `expected_binding_spans(...)`.
- Local transform interpreter exists at `local_transform(...)`.
- Source xref substitution exists at `local_xrefs(...)`.
- Per-asset row key closure and config asset metadata checks exist.
- Structured top-level key checks and nested list/type checks for `fragments` and `attached_notes` exist.
- QA metrics are compared to a full literal expected object.

Implementation gap observed during code inspection:

- In `verify_scenario_master_en.py`, the expected source-span comparison is conditional:
  - `if actual_spans and actual_spans!=wanted: fail('E_C2B_PROVENANCE',anchor)`
- This means a non-generated/non-owned-page unit whose `source_fragments` and `output_fragments` are both deleted bypasses exact locator/transform validation for that unit, because `actual_spans` becomes empty and the equality check does not fire.

## Bounded suite evidence

Command:

```text
python -B -m py_compile kb_creator\scripts\build_scenario_master_en.py kb_creator\scripts\verify_scenario_master_en.py kb_creator\tests\test_build_scenario_master_en.py kb_creator\tests\test_verify_scenario_master_en.py
python -B -m pytest -q -p no:cacheprovider kb_creator\tests\test_build_scenario_master_en.py kb_creator\tests\test_verify_scenario_master_en.py
```

Result:

```text
.....................................................                    [100%]
53 passed in 27.30s
```

## Disposable positive candidate, determinism, and independent audit

Two disposable candidates were built through the builder CLI and verified through the verifier CLI. Both were removed after probing.

Build A and B both returned:

```json
{"candidate_inventory_sha256": "37189873AAF3AD31810749362C16AD959D051EEAC62FA94683911EE855560421", "inventory_file_sha256": "EF28700403FFE5FC781D1004979B83DC4ACC5F743E93F02201820071211AC3F8", "master_en_sha256": "44303C5A0D2964469D6B6523EDF3CB4391194BC49E19DD10B3FB90CCB667DC62", "scenario_id": "viral", "status": "candidate_built_for_independent_verification"}
```

Verifier A and B both returned:

```json
{"candidate_inventory_sha256": "37189873AAF3AD31810749362C16AD959D051EEAC62FA94683911EE855560421", "inventory_file_sha256": "EF28700403FFE5FC781D1004979B83DC4ACC5F743E93F02201820071211AC3F8", "master_en_sha256": "44303C5A0D2964469D6B6523EDF3CB4391194BC49E19DD10B3FB90CCB667DC62", "publication_config_sha256": "CEAA522F8ADA7EF2453D52F0DE4D098733EA5A7D55B12BE96694094891767BF3", "scenario_id": "viral", "status": "verified_candidate_pending_process_and_external_gates"}
```

Positive candidate counts:

```json
{"assets": 123, "evidence_assets": 16, "files": 130, "inventory_file_count": 129, "inventory_rows": 129, "output_fragments": 171, "reader_assets": 107, "source_fragments": 171, "structured_units": 29, "units": 168}
```

QA metrics:

```json
{"anchors": 168, "candidate_assets": 123, "duplicate_blocks": 0, "editorial_lexical_deltas": 0, "generated_blocks": 73, "handouts": 41, "links": 237, "owned_blocks": 1862, "reader_assets": 107, "reader_noise_findings": 0, "source_pages": 124, "source_xref_rows": 41, "source_xref_segments": 42, "structured_units": 29, "total_blocks": 1935, "unauthorized_suppression_blocks": 0, "unowned_blocks": 0, "visual_review_units": 91, "xrefs_executed": 237}
```

Determinism:

```json
{"build_stdout_equal": true, "inventory_digest_a": "37189873AAF3AD31810749362C16AD959D051EEAC62FA94683911EE855560421", "inventory_digest_b": "37189873AAF3AD31810749362C16AD959D051EEAC62FA94683911EE855560421", "master_sha_a": "44303C5A0D2964469D6B6523EDF3CB4391194BC49E19DD10B3FB90CCB667DC62", "master_sha_b": "44303C5A0D2964469D6B6523EDF3CB4391194BC49E19DD10B3FB90CCB667DC62", "verify_stdout_equal": true}
```

Independent all-unit/source-fragment audit on the positive candidate:

```json
{"empty_expected_units": 38, "mismatch_count": 0, "mismatches": [], "output_fragments": 171, "source_fragments": 171, "transformed_checked": 171, "units": 168}
```

This independent audit re-resolved config locators, continuation pages, page claims, source xref substitutions, and local heading/label/image transforms for all 168 units and all 171 source/output fragment pairs. It found no positive-candidate mismatch.

Candidate cleanup:

```text
CANDIDATE_DIRS_AFTER []
CANDIDATE_DIRS_AFTER_OMIT_EXACT []
```

No durable candidate remained.

## Resealed attack probes

All requested prior attacks now fail in the expected risk class:

```json
{"name": "original_extra_reader_byte_resealed", "expected": "E_C2B_PROVENANCE", "rc": 1, "first": "E_C2B_PROVENANCE: master_en", "inventory_sha256": "6C28180A6A78A704C5A9E52D7FD79A40149306DAEDCFCD6824A22C881E174BA4", "master_en_sha256": "D33E44119EEBCD3F7BBF91E695D3DD7914C0963F064F231B1779589C62516D22"}
```

```json
{"name": "original_impossible_source_provenance_resealed", "expected": "E_C2B_PROVENANCE", "rc": 1, "first": "E_C2B_PROVENANCE: viral-credits", "inventory_sha256": "E12F52F68A1137BD65BEC1EF4CB761C710AF9FFDDEEE21D1B2656F9A2388D1B6", "provenance_sha256": "666D4BBDEA3AF5381E14214E6A6A7FA4C96765B61657DCD70372081D515AA564"}
```

```json
{"name": "original_bogus_structured_unit_resealed", "expected": "E_C2B_STRUCTURE", "rc": 1, "first": "E_C2B_STRUCTURE: structured_units", "inventory_sha256": "1C76FBD0E7054F598E963449200CDFCC85EA1AFC7A5615AF28033328CFD3D11A", "provenance_sha256": "2861774E982034433C67BCAB1343C4CD236B1790D8492C94E420E6C405129110"}
```

```json
{"name": "original_invalid_open_asset_metadata_summary_resealed", "expected": "E_C2B_ASSET", "rc": 1, "first": "E_C2B_ASSET: viral-accepted-e1e2aa6964b45037691d92e4faf91dba6bbd411e409dc49c237f6b0e71e6ce85", "inventory_sha256": "A594DA1BE19A481E36D9E910935754168CC3A99A78A9A1D0C1F03413AFB9455B", "asset_manifest_sha256": "CF95CD470464D97D409AAA649F9C38AC7D80FBAD7DB00453AE20A132F2FE8355"}
```

```json
{"name": "original_false_qa_metrics_errors_resealed", "expected": "E_C2B_QA", "rc": 1, "first": "E_C2B_QA: qa", "inventory_sha256": "CE6286BB560D958A3588973653A95DA66E096B5F64EB8DEC0AE3308509C6890E", "qa_json_sha256": "D763F2B075B452F4D465FB7EE4CF234E50AF415CA57B34027A82222DF3E4D800", "qa_md_sha256": "E169430D86F0562504E8E712EB403167B2330E606EC3DE52E3A28655EF6CDC79"}
```

```json
{"name": "asset_row_unknown_key_only_resealed", "expected": "E_C2B_ASSET", "rc": 1, "first": "E_C2B_ASSET: viral-accepted-e1e2aa6964b45037691d92e4faf91dba6bbd411e409dc49c237f6b0e71e6ce85", "inventory_sha256": "9C618DAA7EB23287DD8B34DB45CC60161FC9944FC7FE9336DE74BA956940ED51", "asset_manifest_sha256": "71CCA6717DAAF58898890691A005F99470E1F26DCB05E5AF3B56669B48A3EA2E"}
```

```json
{"name": "asset_owner_anchor_only_resealed", "expected": "E_C2B_ASSET", "rc": 1, "first": "E_C2B_ASSET: viral-accepted-e1e2aa6964b45037691d92e4faf91dba6bbd411e409dc49c237f6b0e71e6ce85", "inventory_sha256": "C6C17D655AECA38817C9EA3EE8B782320EBDD315B116B596381AFA6D8A81C7D6", "asset_manifest_sha256": "D3ABD743C961F3CFCB15FC92AFA572287A6522A0EE9EEB91A932547F970EF282"}
```

```json
{"name": "structured_attached_notes_wrong_type_resealed", "expected": "E_C2B_STRUCTURE", "rc": 1, "first": "E_C2B_STRUCTURE: viral-structure-rumors", "inventory_sha256": "B859449C32EB3D401D110003C43E26715783E26B39E53285470076A6EFB1489D", "provenance_sha256": "538721221DF8A9BC8F378C04E633023C9993AF353E69490D80DD152DA7C0E381"}
```

```json
{"name": "source_fragment_empty_valid_span_resealed", "expected": "E_C2B_PROVENANCE", "rc": 1, "first": "E_C2B_PROVENANCE: viral-credits", "inventory_sha256": "8319009CA7F54A6344F9976D50052F87EE129A6DA53B11EE99BDBEFC22CBDF0E", "provenance_sha256": "54A850622ACD31F26842043A9A8736F88743293DED9F25152A2A990E0956FB89"}
```

```json
{"name": "source_fragment_nonempty_other_unit_span_resealed", "expected": "E_C2B_PROVENANCE", "rc": 1, "first": "E_C2B_PROVENANCE: viral-credits", "inventory_sha256": "6507EBA1FC399A542FA134F45257510607C988C3CA8252BE2C86085BC20550D7", "provenance_sha256": "A869134D811ACB039741E0A88D2AAA77289511B5E47C956F3CAB1C8AD6B64E39"}
```

## Finding

### P1 blocker — fragment omission from a nonempty unit still passes verification

The corrected C2b contract requires all 168 units and all 171 source/output fragments to be bound exactly once, with nonempty 1:1 provenance, source ranges, final ranges, and local transform validation. Current verifier v3 rejects wrong source spans when a fragment remains present, but it accepts deletion of the complete source/output fragment pair from a unit that should have one.

Mutation:

- Built a fresh disposable candidate.
- Selected `viral-credits`, which had one source fragment and one output fragment.
- Set:

```json
{"source_fragments": [], "output_fragments": []}
```

- Resealed `INVENTORY.json`.

Exact evidence:

```text
VICTIM_BEFORE {"anchor": "viral-credits", "output_fragments": 1, "source_fragments": 1}
OMIT_VERIFY_RC 0
OMIT_VERIFY_STDOUT {"candidate_inventory_sha256": "33866F4A45DDB9980A5B37707DB0DF7C864403A43B2521AF056FA77F579E5964", "inventory_file_sha256": "60B0F4320915234F848FA700270FD4102EE5D7E9D58E6FAF386323C7029D50BB", "master_en_sha256": "44303C5A0D2964469D6B6523EDF3CB4391194BC49E19DD10B3FB90CCB667DC62", "publication_config_sha256": "CEAA522F8ADA7EF2453D52F0DE4D098733EA5A7D55B12BE96694094891767BF3", "scenario_id": "viral", "status": "verified_candidate_pending_process_and_external_gates"}
OMIT_HASHES {"inventory_file_sha256": "60B0F4320915234F848FA700270FD4102EE5D7E9D58E6FAF386323C7029D50BB", "inventory_sha256": "33866F4A45DDB9980A5B37707DB0DF7C864403A43B2521AF056FA77F579E5964", "master_en_sha256": "44303C5A0D2964469D6B6523EDF3CB4391194BC49E19DD10B3FB90CCB667DC62", "provenance_sha256": "0C65A620352C6A005A24CBA8CB8571D61DDFDC7D9A5AA6E199FCBF9E9C1E46AC"}
```

The same omission probe also appeared in the larger run:

```json
{"name": "additional_remove_all_fragments_from_nonempty_unit_resealed", "expected": "E_C2B_PROVENANCE", "rc": 0, "inventory_sha256": "33866F4A45DDB9980A5B37707DB0DF7C864403A43B2521AF056FA77F579E5964", "inventory_file_sha256": "60B0F4320915234F848FA700270FD4102EE5D7E9D58E6FAF386323C7029D50BB", "provenance_sha256": "0C65A620352C6A005A24CBA8CB8571D61DDFDC7D9A5AA6E199FCBF9E9C1E46AC", "master_en_sha256": "44303C5A0D2964469D6B6523EDF3CB4391194BC49E19DD10B3FB90CCB667DC62"}
```

Implementation cause:

- The verifier computes expected source spans for each anchor, but only compares them when actual source spans are present.
- With both fragment arrays empty, `len(source_fragments) == len(output_fragments)` remains true.
- `actual_spans` is empty, so `if actual_spans and actual_spans != wanted` does not reject.
- No global assertion checks `source_fragments == 171`, `output_fragments == 171`, or per-unit expected-fragment presence.

Impact:

- A candidate can remove provenance evidence for a source-derived unit, reseal inventory, and still receive `verified_candidate_pending_process_and_external_gates`.
- This violates the C2b exact locator-binding requirement and the nonempty 1:1 provenance requirement.

## Recommendation

REJECT_C2B.

Minimal next action:

1. In `verify_scenario_master_en.py`, require `actual_spans == wanted` for every unit, not only when `actual_spans` is nonempty, while preserving the explicitly expected empty case for generated/owned-page/navigation-only units.
2. Assert global source/output fragment totals and fragment ID conservation, expected currently `171` source fragments and `171` output fragments for the positive package.
3. Add a negative test that removes both fragment arrays from a known nonempty unit such as `viral-credits`, reseals inventory, and expects `E_C2B_PROVENANCE`.
4. Rerun the 53-test suite plus independent disposable CLI probes.

## Blockers

- C2b cannot be accepted while verifier success is possible after deleting all provenance fragments from a nonempty source-derived unit.
- This is not release approval; release remains out of scope.

Elapsed time: approximately 38 minutes from final re-review start to receipt drafting.

Token use: exact final goal token use to be reported by the task completion tool; unavailable inside this receipt before finalization.

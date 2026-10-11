# GPT-5.5/high C2b implementation review — Viral Step 7 MASTER_EN

Timestamp: 2026-09-01T23:07:50+03:00

Review kind: implementation

Decision: REJECT_C2B

Role and scope:

- Reviewer: independent GPT-5.5/high critic role.
- Implemented or materially designed candidate under review: no.
- Orchestration ownership: remains with the gpt-5.6-sol orchestrator; this review does not transfer policy or release ownership.
- Assignment state: current C2b implementation review after Terra minimal-verifier remediation.
- Scoped override: review only; no release approval; no fixes implemented. Sole authorized write was this immutable receipt.

## Files and inputs checked

- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/plan.md`
  - SHA-256: `64C62A04F15A7C54B6B16A29B3B3F561C048A119E34B33F8BD68D53983D0185E`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/context.md`
  - SHA-256: `B2B20E8424AFC7D6D0019ED1DE3F4349BEB86574BE4533BC8EC8570E1CC62610`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_viral_step7_master_en_c2b_verifier_sidecar_contract_20260901.md`
  - SHA-256: `F00428E34CC45C92A47F0D97643D89364946C7480D3F5C028E355CEDC134B14D`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_viral_step7_master_en_c2b_minimal_independent_verifier_correction_20260901.md`
  - SHA-256: `2C7B7C0842F3833FA5CEFFFB9EB2FC73700F51CFE9D4C11A4D84CE84D89D865E`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_step7_master_en_c2b_minimal_verifier_20260901.md`
  - SHA-256: `5B85CD9D520D2AE6FDED55613F09556F6C2938AEBF5500C759D019DB420F0D6E`
- `kb_creator/scripts/build_scenario_master_en.py`
  - bytes: `70773`
  - SHA-256: `82C720B572A73B33DF9D2548BB3FD4CB8BAE81660AE21D4273DEB984C99EDA1C`
- `kb_creator/scripts/verify_scenario_master_en.py`
  - bytes: `10787`
  - SHA-256: `4B67C22F1C92DF796EB96819FAEFECBA6F660B08D5962C3150AFC511804ABF9B`
- `kb_creator/tests/test_build_scenario_master_en.py`
  - bytes: `26786`
  - SHA-256: `01BDFFFC6F32833E3EF5EF831A85F30775883C1E20B5E9B5B3C0687A58AD33DF`
- `kb_creator/tests/test_verify_scenario_master_en.py`
  - bytes: `5095`
  - SHA-256: `9CD402301A7CA437DB448AD8504153BEB5DAE685E57AF4CA55907F3DCCF451A7`
- `kb_creator/working/viral/master_en/publication_config_v1.json`
  - bytes: `660329`
  - SHA-256: `CEAA522F8ADA7EF2453D52F0DE4D098733EA5A7D55B12BE96694094891767BF3`

## Verification commands and evidence

Static verifier isolation check:

- AST imports in `verify_scenario_master_en.py`: `argparse`, `hashlib`, `json`, `os`, `re`, `stat`, `sys`, `pathlib.Path`, and `__future__.annotations`.
- No lexical hits in verifier implementation for `build_scenario_master_en`, `importlib`, `subprocess`, `runpy`, `exec(`, `eval(`, `__import__`, or `shared`.

Compact suite:

```text
python -B -m py_compile kb_creator\scripts\build_scenario_master_en.py kb_creator\scripts\verify_scenario_master_en.py kb_creator\tests\test_build_scenario_master_en.py kb_creator\tests\test_verify_scenario_master_en.py
python -B -m pytest -q -p no:cacheprovider kb_creator\tests\test_build_scenario_master_en.py kb_creator\tests\test_verify_scenario_master_en.py

....................................................                     [100%]
52 passed in 24.27s
```

Scoped whitespace check:

```text
git diff --check -- kb_creator/scripts/build_scenario_master_en.py kb_creator/scripts/verify_scenario_master_en.py kb_creator/tests/test_build_scenario_master_en.py kb_creator/tests/test_verify_scenario_master_en.py kb_creator/working/viral/master_en/publication_config_v1.json
```

Result: no output, no whitespace errors.

Disposable positive build and verifier probe:

```text
BUILD 0 {"candidate_inventory_sha256": "37189873AAF3AD31810749362C16AD959D051EEAC62FA94683911EE855560421", "inventory_file_sha256": "EF28700403FFE5FC781D1004979B83DC4ACC5F743E93F02201820071211AC3F8", "master_en_sha256": "44303C5A0D2964469D6B6523EDF3CB4391194BC49E19DD10B3FB90CCB667DC62", "scenario_id": "viral", "status": "candidate_built_for_independent_verification"}
VERIFY_BASE {"rc": 0, "stderr": "", "stdout": "{\"candidate_inventory_sha256\": \"37189873AAF3AD31810749362C16AD959D051EEAC62FA94683911EE855560421\", \"inventory_file_sha256\": \"EF28700403FFE5FC781D1004979B83DC4ACC5F743E93F02201820071211AC3F8\", \"master_en_sha256\": \"44303C5A0D2964469D6B6523EDF3CB4391194BC49E19DD10B3FB90CCB667DC62\", \"publication_config_sha256\": \"CEAA522F8ADA7EF2453D52F0DE4D098733EA5A7D55B12BE96694094891767BF3\", \"scenario_id\": \"viral\", \"status\": \"verified_candidate_pending_process_and_external_gates\"}"}
```

Observed candidate counts from independent disposable build:

```json
{"assets": 123, "evidence_assets": 16, "files": 130, "inventory_rows": 129, "qa_errors": 0, "qa_gates": 14, "reader_assets": 107, "structured_units": 29, "units": 168}
```

Control mutations:

- Raw unsealed reader mutation failed as expected: `E_C2B_INVENTORY: INVENTORY.json`.
- Asset-byte mutation with inventory reseal failed as expected: `E_C2B_ASSET: assets/00d84a08f0f7ef0b634da16d22f1832b3e099350a451425c5b2642428fe8f4b9.jpg`.

Disposable candidate cleanup:

```text
CANDIDATE_DIRS_AFTER []
CANDIDATE_DIRS_AFTER_EXACT []
```

No durable candidate root remained after probes.

## Findings

### P1 blocker — verifier accepts self-consistently inventoried reader text mutation

The corrected C2b DoD requires the verifier to reject semantic/provenance mutations and verify candidate reader identity/sidecar consistency. The current verifier accepted a modified `MASTER_EN.md` after `INVENTORY.json` was recomputed.

Mutation: append one extra `x` before the final newline in `MASTER_EN.md`, then reseal `INVENTORY.json`.

Verifier result:

```json
{
  "name": "reader_resealed",
  "verify": {
    "rc": 0,
    "stderr": "",
    "stdout": "{\"candidate_inventory_sha256\": \"6C28180A6A78A704C5A9E52D7FD79A40149306DAEDCFCD6824A22C881E174BA4\", \"inventory_file_sha256\": \"19BB886B945E0BA0BDDF77FCD004CB11AF8EF6F30301BD8FFB800FB5C9D65F6E\", \"master_en_sha256\": \"D33E44119EEBCD3F7BBF91E695D3DD7914C0963F064F231B1779589C62516D22\", \"publication_config_sha256\": \"CEAA522F8ADA7EF2453D52F0DE4D098733EA5A7D55B12BE96694094891767BF3\", \"scenario_id\": \"viral\", \"status\": \"verified_candidate_pending_process_and_external_gates\"}"
  },
  "inventory_sha256": "6C28180A6A78A704C5A9E52D7FD79A40149306DAEDCFCD6824A22C881E174BA4",
  "inventory_file_sha256": "19BB886B945E0BA0BDDF77FCD004CB11AF8EF6F30301BD8FFB800FB5C9D65F6E",
  "master_en_sha256": "D33E44119EEBCD3F7BBF91E695D3DD7914C0963F064F231B1779589C62516D22"
}
```

Base `MASTER_EN.md` SHA-256 was `44303C5A0D2964469D6B6523EDF3CB4391194BC49E19DD10B3FB90CCB667DC62`; mutated `MASTER_EN.md` SHA-256 was `D33E44119EEBCD3F7BBF91E695D3DD7914C0963F064F231B1779589C62516D22`, but the verifier still returned `rc=0`.

Implementation evidence: `verify_scenario_master_en.py` checks inventory rows, anchor count, reader asset refs, output fragment hashes, and QA markdown round-trip, but it does not compare `MASTER_EN.md` to the provenance `master_en` identity or to an independently reconstructed complete reader identity. Relevant current lines are 88-104.

Impact: a candidate can pass C2b with extra or altered reader text outside covered output fragments. This defeats the reduced C2b contract’s semantic mutation boundary.

### P1 blocker — verifier accepts invalid source provenance ranges, page, and hash

The corrected C2b DoD requires nonempty 1:1 provenance with char and UTF-8 byte ranges, source identity, no overlaps, and local fragment transform semantics. The current verifier does not validate `source_fragments` against source page text; it only checks that source/output fragment IDs match and then validates output ranges against final reader text.

Mutation: in the first source fragment, set `page=999`, `start_char=123456`, `end_char=123455`, `start_byte=654321`, `end_byte=654320`, and `sha256=000...000`, then reseal `INVENTORY.json`.

Verifier result:

```json
{
  "name": "invalid_source_provenance_resealed",
  "verify": {
    "rc": 0,
    "stderr": "",
    "stdout": "{\"candidate_inventory_sha256\": \"E12F52F68A1137BD65BEC1EF4CB761C710AF9FFDDEEE21D1B2656F9A2388D1B6\", \"inventory_file_sha256\": \"5A8B5D7008D80AE1E558A0ABAB52660AA5965CD4FAE1F65714FFC168591C6465\", \"master_en_sha256\": \"44303C5A0D2964469D6B6523EDF3CB4391194BC49E19DD10B3FB90CCB667DC62\", \"publication_config_sha256\": \"CEAA522F8ADA7EF2453D52F0DE4D098733EA5A7D55B12BE96694094891767BF3\", \"scenario_id\": \"viral\", \"status\": \"verified_candidate_pending_process_and_external_gates\"}"
  },
  "provenance_sha256": "666D4BBDEA3AF5381E14214E6A6A7FA4C96765B61657DCD70372081D515AA564"
}
```

Implementation evidence: source fragments are schema-closed at line 96 and source/output fragment IDs are compared at line 97, but no source page/range/byte/hash endpoint validation is performed for `source_fragments`.

Impact: C2b provenance can claim impossible source pages and impossible source ranges while still receiving `verified_candidate_pending_process_and_external_gates`.

### P1 blocker — verifier accepts invalid structured-unit sidecar content

The corrected C2b DoD requires exact closure for 29 structures, 11 notes, 41 handouts, and classified owner blocks. The current verifier only checks `len(prov['structured_units']) == 29` and the unique union count of `structured_ids`; it does not validate structured-unit row schema, note/handout semantics, owner block containment, source/final range identity, or attached-note selectors.

Mutation: replace the first `structured_units` entry with `{"bogus": true, "note": "not classified"}`, then reseal `INVENTORY.json`.

Verifier result:

```json
{
  "name": "invalid_structured_unit_resealed",
  "verify": {
    "rc": 0,
    "stderr": "",
    "stdout": "{\"candidate_inventory_sha256\": \"1C76FBD0E7054F598E963449200CDFCC85EA1AFC7A5615AF28033328CFD3D11A\", \"inventory_file_sha256\": \"BB187AAB6F6581BA8E9BAAD9E983B26B4FBCCAB957E2CBC2363B8CEC0EA51FE3\", \"master_en_sha256\": \"44303C5A0D2964469D6B6523EDF3CB4391194BC49E19DD10B3FB90CCB667DC62\", \"publication_config_sha256\": \"CEAA522F8ADA7EF2453D52F0DE4D098733EA5A7D55B12BE96694094891767BF3\", \"scenario_id\": \"viral\", \"status\": \"verified_candidate_pending_process_and_external_gates\"}"
  },
  "provenance_sha256": "2861774E982034433C67BCAB1343C4CD236B1790D8492C94E420E6C405129110"
}
```

Implementation evidence: `verify_scenario_master_en.py` line 90 checks the top-level count `len(prov['structured_units']) != 29`, and line 101 checks only the set cardinality of IDs referenced by units. There is no loop validating the structured-unit payloads themselves.

Impact: the verifier does not enforce the structured/note/handout contract that C2b was specifically asked to close.

### P1 blocker — verifier accepts invalid asset manifest metadata and open asset-row schema

The corrected C2b DoD requires closed sidecars and 107 reader assets / 123 total assets with owner/source semantics. The current verifier validates top-level `ASSET_MANIFEST.json` keys and asset file bytes, but does not close individual asset rows or validate owner/source metadata beyond path/hash/bytes.

Mutation: set `summary.reader=999`, change first asset `owner_anchor` to `nonexistent-anchor`, add `unexpected_extra_key=true`, then reseal `INVENTORY.json`.

Verifier result:

```json
{
  "name": "invalid_asset_metadata_resealed",
  "verify": {
    "rc": 0,
    "stderr": "",
    "stdout": "{\"candidate_inventory_sha256\": \"A594DA1BE19A481E36D9E910935754168CC3A99A78A9A1D0C1F03413AFB9455B\", \"inventory_file_sha256\": \"49C8212FA190029248E1D532AC1386E1FBCC9DFF26FE462441DFF270B0CC1D15\", \"master_en_sha256\": \"44303C5A0D2964469D6B6523EDF3CB4391194BC49E19DD10B3FB90CCB667DC62\", \"publication_config_sha256\": \"CEAA522F8ADA7EF2453D52F0DE4D098733EA5A7D55B12BE96694094891767BF3\", \"scenario_id\": \"viral\", \"status\": \"verified_candidate_pending_process_and_external_gates\"}"
  },
  "asset_manifest_sha256": "CF95CD470464D97D409AAA649F9C38AC7D80FBAD7DB00453AE20A132F2FE8355"
}
```

Implementation evidence: line 79 closes only manifest top-level keys; lines 82-85 validate `output_path`, `sha256`, bytes, and file hash. There is no per-asset `closed(...)`, no `summary` conservation check, and no owner-anchor/source-page semantic check.

Impact: asset sidecar metadata can be corrupted while all bytes and inventory remain self-consistent, and the verifier still passes.

### P1 blocker — verifier accepts invalid QA metrics/errors if QA markdown is regenerated

The corrected C2b DoD requires deterministic QA/inventory and stable risk errors. The current verifier checks QA schema top-level keys, gate order, no `pass` status in late gates, and exact regenerated Markdown, but it does not validate metrics values or the expected risk-error taxonomy/count.

Mutation: set `metrics.anchors=999`, `metrics.reader_assets=-1`, and `errors=[{"code":"E_FAKE","severity":"none"}]`, regenerate `MASTER_EN.qa.md`, then reseal `INVENTORY.json`.

Verifier result:

```json
{
  "name": "invalid_qa_metrics_errors_resealed",
  "verify": {
    "rc": 0,
    "stderr": "",
    "stdout": "{\"candidate_inventory_sha256\": \"CE6286BB560D958A3588973653A95DA66E096B5F64EB8DEC0AE3308509C6890E\", \"inventory_file_sha256\": \"2FB1F7E8F64BD798FD3D49EAD8AF29404C94616C3C8654969E18B8FA66EC399E\", \"master_en_sha256\": \"44303C5A0D2964469D6B6523EDF3CB4391194BC49E19DD10B3FB90CCB667DC62\", \"publication_config_sha256\": \"CEAA522F8ADA7EF2453D52F0DE4D098733EA5A7D55B12BE96694094891767BF3\", \"scenario_id\": \"viral\", \"status\": \"verified_candidate_pending_process_and_external_gates\"}"
  },
  "qa_json_sha256": "D763F2B075B452F4D465FB7EE4CF234E50AF415CA57B34027A82222DF3E4D800",
  "qa_md_sha256": "E169430D86F0562504E8E712EB403167B2330E606EC3DE52E3A28655EF6CDC79"
}
```

Implementation evidence: `verify_scenario_master_en.py` line 103 compares gate names/statuses and Markdown regeneration, but does not assert the literal metrics or stable risk errors.

Impact: QA sidecars can report false counts and a forged error taxonomy while still passing C2b verification.

## Non-blocking observations

- The verifier implementation is isolated from builder imports/exec in the narrow static sense.
- The test suite is too weak for this gate. `test_verify_scenario_master_en.py` imports the builder module at lines 6-7 and uses builder helpers at line 30 to reseal inventory in tests. That does not itself prove verifier coupling, but it allowed shallow tests to miss the accepted mutation gaps above.
- Positive disposable candidate build produced the expected nominal topology and counts: 130 files, 129 inventory rows, 168 units, 29 structured units, 123 assets, 107 reader assets, 16 evidence-only assets, and 14 QA gates.
- No historical durable candidate was left behind; candidate directory was empty after both independent probe runs.

## Recommendation

REJECT_C2B.

Minimal next action:

1. Remediate `verify_scenario_master_en.py` so it rejects self-consistently inventoried mutations to reader text, source provenance, structured units/notes/handouts, asset metadata/schema, and QA metrics/errors.
2. Add negative tests that do not depend on builder helper functions for the verification assertions and that reproduce the accepted mutation probes above.
3. Rerun the 52-test compact suite plus independent disposable build/verify/mutation probes before returning to C2b critic review.

## Blockers

- C2b cannot be accepted while the verifier returns success for contract-invalid, inventory-resealed candidate mutations.
- This is not release approval; release remains out of scope.

Elapsed time: approximately 7 minutes from C2b review start to receipt drafting.

Token use: goal tool reported `131031` tokens used at pre-receipt checkpoint; final exact token count is unavailable inside the receipt.

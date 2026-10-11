# Terra engineering receipt: Viral Step 6A BLD/full integration

**Status:** COMPLETE for Terra engineering evidence construction; downstream independent QA and critic review remain required.

## Frozen material

- Library SHA-256: 9802571C128D63DE5D643425FDA361EB2E032A5AE830ED9713B83A3A413B5855
- Focused tests SHA-256: FA70BBAE285EAAA10E1F6BAF90119008342A18552E580E4E8530D9462997D5F9
- Only intended worktree path delta: this receipt.
- Cache mode: python -B, pytest -p no:cacheprovider; fixture roots were one TemporaryDirectory and were automatically cleaned after capture.

## Captured full focused execution

- Command: D:\NRI\.tools\python-3.13.14\python.exe -B -m pytest -p no:cacheprovider kb_creator/tests/test_scenario_source_reconstruction.py -q
- Native exit: 0; collected/passed: 371/371; elapsed seconds: 1072.52.
- stdout bytes/SHA-256: 520 / 4F5A6D8F902EF691C8AA9FF1D9F329D29E72C7692B71CF954F9E6D0CDD4A9D6C
- stderr bytes/SHA-256: 0 / E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855
- Terminal summary: 371 passed.

## Registry/profile/routing

- Test profile serialization: {"authority_sha256": "1893BF7B2838E8DDCE6E6FA0E07F900A261308BC341DDA152803D28EF01BD00B", "kind": "test", "profile_id": "strict-fixture"}
- Provider identities: identity provider type `_Provider` (no `provider_id` attribute), bound to `1893BF7B2838E8DDCE6E6FA0E07F900A261308BC341DDA152803D28EF01BD00B`; filesystem provider type `TestFilesystemProvider`, `provider_id` `fixture-filesystem`, bound to the same seal. The complete machine-readable derivation is appended below.
- Public signature: preflight(contract_path, source_path, recovery_root, run_root); test signatures: _test_preflight, _test_build, _test_verify with sealed context.
- Route table: public→PRODUCTION_CONTEXT; test→sealed TEST context; both→_strict_verify.
- Family counts: {"AST": 21, "AUT": 30, "CMD": 61, "INJ": 5, "INV": 18, "LED": 6, "NAV": 15, "PAG": 28, "QAV": 90, "REG": 2, "REP": 2, "SCH": 33, "SEM": 18, "SRC": 18, "TOP": 21}
- Cases/callables are ordered below by the actual returned audit array; each case had one distinct physical callable name in the frozen registry.

## BLD state transitions

The former summary table is superseded by `BLD_CAPTURE_JSON` below. It is a bounded hermetic capture through the frozen helpers: `_test_build`, `_test_verify`, `_owned`, `_write_non_qa_bundle`, `_finalize_and_verify`, `_strict_verify`, `rename_no_replace`, and `remove_owned_tree`. It records exact manifest digests, normalized file-id tokens, all ownership states, existing-target immutability, parity, and PASS.

## Actual 368 MutationAudit objects (registry order)

<!-- AUDITS_JSON_BEGIN -->
[
  {
    "case_id": "REP-branch-wrong",
    "changed_before_reseal": [
      "repository#/branch"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_REPO_BRANCH",
    "family": "REP",
    "fixture_root_token": "fixture",
    "observed_code": "E_REPO_BRANCH",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "8A59B3248D31FFB11FF137FA77691E7266C1AB80F885ECF99D838F7EA1201A98",
    "semantic_before_sha256": "8A59B3248D31FFB11FF137FA77691E7266C1AB80F885ECF99D838F7EA1201A98",
    "semantic_selector": "repository#/branch",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "REP-head-wrong",
    "changed_before_reseal": [
      "repository#/head"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_REPO_HEAD",
    "family": "REP",
    "fixture_root_token": "fixture",
    "observed_code": "E_REPO_HEAD",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "66F8A43A7F5A86CB301A66B60170C42E35BEB8686746E2271708A5131C418C7F",
    "semantic_before_sha256": "66F8A43A7F5A86CB301A66B60170C42E35BEB8686746E2271708A5131C418C7F",
    "semantic_selector": "repository#/head",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SRC-source-byte-identical-alias",
    "changed_before_reseal": [
      "source#/path"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SOURCE_PATH",
    "family": "SRC",
    "fixture_root_token": "fixture",
    "observed_code": "E_SOURCE_PATH",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "4F409BE9089EB2FF818AAF83D1BD16CAC603C4D04C54817F45E9C2F9187ABCED",
    "semantic_before_sha256": "7F5D60EF5F920CDF494602476EF4BACDA89A1D629281B2D357F6F6CF622017FE",
    "semantic_selector": "source#/path",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SRC-source-external-locator",
    "changed_before_reseal": [
      "sidecar#/external_locator"
    ],
    "changed_by_reseal": [
      "sidecar#/raw_sha256"
    ],
    "declared_reseals": [
      "sidecar",
      "profile"
    ],
    "expected_code": "E_SOURCE_EXTERNAL_FORBIDDEN",
    "family": "SRC",
    "fixture_root_token": "fixture",
    "observed_code": "E_SOURCE_EXTERNAL_FORBIDDEN",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "11FB3C7235BAD50DCCB60AE35DB543B03AFDF2955F21ED0B9C8D966D5F60DE2A",
    "semantic_before_sha256": "11FB3C7235BAD50DCCB60AE35DB543B03AFDF2955F21ED0B9C8D966D5F60DE2A",
    "semantic_selector": "sidecar#/external_locator",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SRC-source-missing",
    "changed_before_reseal": [
      "source#/physical-entry"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_PATH_MISSING",
    "family": "SRC",
    "fixture_root_token": "fixture",
    "observed_code": "E_PATH_MISSING",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "FFA63583DFA6706B87D284B86B0D693A161E4840AAD2C5CF6B5D27C3B9621F7D",
    "semantic_before_sha256": "CC0B63366A207BBB86BDA988477F31B646BC3A062A13129534A470602AE7786A",
    "semantic_selector": "source#/physical-entry",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SRC-source-bytes-wrong",
    "changed_before_reseal": [
      "source#/bytes"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SOURCE_BYTES",
    "family": "SRC",
    "fixture_root_token": "fixture",
    "observed_code": "E_SOURCE_BYTES",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "E19E57CCF1FFB194B9B2700D9F8CEAAF774B23FBFA4B444EE0F43364E035CB78",
    "semantic_before_sha256": "CC0B63366A207BBB86BDA988477F31B646BC3A062A13129534A470602AE7786A",
    "semantic_selector": "source#/bytes",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SRC-source-hash-wrong",
    "changed_before_reseal": [
      "source#/sha256"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SOURCE_HASH",
    "family": "SRC",
    "fixture_root_token": "fixture",
    "observed_code": "E_SOURCE_HASH",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "CBE425D5481B4C0584C6D79F137BA3E0A0C690D97B9A1EE0D3E9F5F512F6E3AF",
    "semantic_before_sha256": "CC0B63366A207BBB86BDA988477F31B646BC3A062A13129534A470602AE7786A",
    "semantic_selector": "source#/sha256",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SRC-source-reparse",
    "changed_before_reseal": [
      "source#/reparse"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_PATH_REPARSE",
    "family": "SRC",
    "fixture_root_token": "fixture",
    "observed_code": "E_PATH_REPARSE",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "CC0B63366A207BBB86BDA988477F31B646BC3A062A13129534A470602AE7786A",
    "semantic_before_sha256": "CC0B63366A207BBB86BDA988477F31B646BC3A062A13129534A470602AE7786A",
    "semantic_selector": "source#/reparse",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SRC-sidecar-missing",
    "changed_before_reseal": [
      "sidecar#/physical-entry"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_PATH_MISSING",
    "family": "SRC",
    "fixture_root_token": "fixture",
    "observed_code": "E_PATH_MISSING",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "9B12FDF4647173D7D4B42E9690C82FCA8D519D81A02BE63AA6DFC637AF908694",
    "semantic_before_sha256": "9B12FDF4647173D7D4B42E9690C82FCA8D519D81A02BE63AA6DFC637AF908694",
    "semantic_selector": "sidecar#/physical-entry",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SRC-sidecar-raw-hash-wrong",
    "changed_before_reseal": [
      "sidecar#/raw_sha256"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SIDECAR_HASH",
    "family": "SRC",
    "fixture_root_token": "fixture",
    "observed_code": "E_SIDECAR_HASH",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "4334C3A77C9AF423D96D4627903FD86125A552F421E80109E20E6282BF999E96",
    "semantic_before_sha256": "4334C3A77C9AF423D96D4627903FD86125A552F421E80109E20E6282BF999E96",
    "semantic_selector": "sidecar#/raw_sha256",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SRC-sidecar-working-path-wrong",
    "changed_before_reseal": [
      "sidecar#/working_source/path"
    ],
    "changed_by_reseal": [
      "sidecar#/raw_sha256"
    ],
    "declared_reseals": [
      "sidecar",
      "profile"
    ],
    "expected_code": "E_SIDECAR_WORKING_PATH",
    "family": "SRC",
    "fixture_root_token": "fixture",
    "observed_code": "E_SIDECAR_WORKING_PATH",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "AAAF3D972E0861540F9CCACD248824037B999652894CF152EF404285D8F3A1D2",
    "semantic_before_sha256": "AAAF3D972E0861540F9CCACD248824037B999652894CF152EF404285D8F3A1D2",
    "semantic_selector": "sidecar#/working_source/path",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SRC-sidecar-working-bytes-wrong",
    "changed_before_reseal": [
      "sidecar#/working_source/bytes"
    ],
    "changed_by_reseal": [
      "sidecar#/raw_sha256"
    ],
    "declared_reseals": [
      "sidecar",
      "profile"
    ],
    "expected_code": "E_SIDECAR_WORKING_BYTES",
    "family": "SRC",
    "fixture_root_token": "fixture",
    "observed_code": "E_SIDECAR_WORKING_BYTES",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "5B641756803D03FA7255CA03E8812EE164229A0EED3F072DF35DD23F431615D7",
    "semantic_before_sha256": "5B641756803D03FA7255CA03E8812EE164229A0EED3F072DF35DD23F431615D7",
    "semantic_selector": "sidecar#/working_source/bytes",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SRC-sidecar-working-hash-wrong",
    "changed_before_reseal": [
      "sidecar#/working_source/sha256"
    ],
    "changed_by_reseal": [
      "sidecar#/raw_sha256"
    ],
    "declared_reseals": [
      "sidecar",
      "profile"
    ],
    "expected_code": "E_SIDECAR_WORKING_HASH",
    "family": "SRC",
    "fixture_root_token": "fixture",
    "observed_code": "E_SIDECAR_WORKING_HASH",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "FA997A60562755697A4B410175F381E2B704D3901B4EA2B54F4230E5BE921AE1",
    "semantic_before_sha256": "FA997A60562755697A4B410175F381E2B704D3901B4EA2B54F4230E5BE921AE1",
    "semantic_selector": "sidecar#/working_source/sha256",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SRC-sidecar-page-count-wrong",
    "changed_before_reseal": [
      "sidecar#/working_source/page_count"
    ],
    "changed_by_reseal": [
      "sidecar#/raw_sha256"
    ],
    "declared_reseals": [
      "sidecar",
      "profile"
    ],
    "expected_code": "E_SIDECAR_PAGE_COUNT",
    "family": "SRC",
    "fixture_root_token": "fixture",
    "observed_code": "E_SIDECAR_PAGE_COUNT",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "107D42EA634E58E5DD2F53702C069A1BF05B923740E5A055A01CDAD4145D2EBD",
    "semantic_before_sha256": "107D42EA634E58E5DD2F53702C069A1BF05B923740E5A055A01CDAD4145D2EBD",
    "semantic_selector": "sidecar#/working_source/page_count",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SRC-sidecar-media-box-wrong",
    "changed_before_reseal": [
      "sidecar#/working_source/media_box"
    ],
    "changed_by_reseal": [
      "sidecar#/raw_sha256"
    ],
    "declared_reseals": [
      "sidecar",
      "profile"
    ],
    "expected_code": "E_SIDECAR_MEDIA_BOX",
    "family": "SRC",
    "fixture_root_token": "fixture",
    "observed_code": "E_SIDECAR_MEDIA_BOX",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "A4AAD85EA729DC2208DB81017DD9E78CFE155FB6FA38DDDF53210EF5312D4B1A",
    "semantic_before_sha256": "A4AAD85EA729DC2208DB81017DD9E78CFE155FB6FA38DDDF53210EF5312D4B1A",
    "semantic_selector": "sidecar#/working_source/media_box",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SRC-sidecar-rotation-wrong",
    "changed_before_reseal": [
      "sidecar#/working_source/rotations"
    ],
    "changed_by_reseal": [
      "sidecar#/raw_sha256"
    ],
    "declared_reseals": [
      "sidecar",
      "profile"
    ],
    "expected_code": "E_SIDECAR_ROTATION",
    "family": "SRC",
    "fixture_root_token": "fixture",
    "observed_code": "E_SIDECAR_ROTATION",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "A2AA62CF90B9CB45FE7AEF534F49FA3B21D2442FD6C159930A1C2B7F2683FE15",
    "semantic_before_sha256": "A2AA62CF90B9CB45FE7AEF534F49FA3B21D2442FD6C159930A1C2B7F2683FE15",
    "semantic_selector": "sidecar#/working_source/rotations",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SRC-sidecar-runtime-dependency-true",
    "changed_before_reseal": [
      "sidecar#/policy/runtime_dependency"
    ],
    "changed_by_reseal": [
      "sidecar#/raw_sha256"
    ],
    "declared_reseals": [
      "sidecar",
      "profile"
    ],
    "expected_code": "E_SIDECAR_RUNTIME_DEPENDENCY",
    "family": "SRC",
    "fixture_root_token": "fixture",
    "observed_code": "E_SIDECAR_RUNTIME_DEPENDENCY",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "F499E56523265C36FE33C42106540DAF4EF2B199BAED56CAA85B8C79B572A12E",
    "semantic_before_sha256": "F499E56523265C36FE33C42106540DAF4EF2B199BAED56CAA85B8C79B572A12E",
    "semantic_selector": "sidecar#/policy/runtime_dependency",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SRC-sidecar-external-path-allowed",
    "changed_before_reseal": [
      "sidecar#/policy/external_path_allowed"
    ],
    "changed_by_reseal": [
      "sidecar#/raw_sha256"
    ],
    "declared_reseals": [
      "sidecar",
      "profile"
    ],
    "expected_code": "E_SIDECAR_EXTERNAL_ALLOWED",
    "family": "SRC",
    "fixture_root_token": "fixture",
    "observed_code": "E_SIDECAR_EXTERNAL_ALLOWED",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "434925BB1F176594759D33B948EE7857D2F4BBC3A3976B7E199995D30B9FF372",
    "semantic_before_sha256": "434925BB1F176594759D33B948EE7857D2F4BBC3A3976B7E199995D30B9FF372",
    "semantic_selector": "sidecar#/policy/external_path_allowed",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SRC-sidecar-subsequent-path-wrong",
    "changed_before_reseal": [
      "sidecar#/policy/subsequent_path"
    ],
    "changed_by_reseal": [
      "sidecar#/raw_sha256"
    ],
    "declared_reseals": [
      "sidecar",
      "profile"
    ],
    "expected_code": "E_SIDECAR_SUBSEQUENT_PATH",
    "family": "SRC",
    "fixture_root_token": "fixture",
    "observed_code": "E_SIDECAR_SUBSEQUENT_PATH",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "BB78F8A354863B97B852CACB5526C23055BA7CED57895EA65E0835DF809A7649",
    "semantic_before_sha256": "BB78F8A354863B97B852CACB5526C23055BA7CED57895EA65E0835DF809A7649",
    "semantic_selector": "sidecar#/policy/subsequent_path",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SRC-sidecar-origin-marked-source",
    "changed_before_reseal": [
      "sidecar#/policy/origin"
    ],
    "changed_by_reseal": [
      "sidecar#/raw_sha256"
    ],
    "declared_reseals": [
      "sidecar",
      "profile"
    ],
    "expected_code": "E_SIDECAR_ORIGIN_POLICY",
    "family": "SRC",
    "fixture_root_token": "fixture",
    "observed_code": "E_SIDECAR_ORIGIN_POLICY",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "EE53AF47F908178721192A07FEDF730BED70B7892906DB666EEE6DB58AE753C3",
    "semantic_before_sha256": "EE53AF47F908178721192A07FEDF730BED70B7892906DB666EEE6DB58AE753C3",
    "semantic_selector": "sidecar#/policy/origin",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "AUT-contract-argument-wrong",
    "changed_before_reseal": [
      "contract#/path"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_CONTRACT_PATH",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "observed_code": "E_CONTRACT_PATH",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "9C75A8EAE44433986888B6865DD8393B47840063ED7DF446DD314DE4B89A6C2B",
    "semantic_before_sha256": "2646884243746CE2CF30F33BAAAD1E4EF2A39F8CDD5E4B6F45A71B785B69D218",
    "semantic_selector": "contract#/path",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "AUT-contract-raw-hash-wrong",
    "changed_before_reseal": [
      "contract#/raw_sha256"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_CONTRACT_HASH",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "observed_code": "E_CONTRACT_HASH",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "A319FAB8632FD32BC86D56CD604B0EC9D61A92A64B6012563D1DB35E45D6F2A7",
    "semantic_before_sha256": "85E0FE754A853E8AD102EBC7B8F206172807F5DD239C999683B0021952593DAA",
    "semantic_selector": "contract#/raw_sha256",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "AUT-contract-canonical-content-wrong",
    "changed_before_reseal": [
      "contract#/scenario"
    ],
    "changed_by_reseal": [
      "contract#/raw_sha256"
    ],
    "declared_reseals": [
      "contract",
      "profile"
    ],
    "expected_code": "E_CONTRACT_CANONICAL",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "observed_code": "E_CONTRACT_CANONICAL",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "2186609E312A1BDEBBB7365A879D04060F05CF58DBE312FE66D73C7D74C33676",
    "semantic_before_sha256": "85E0FE754A853E8AD102EBC7B8F206172807F5DD239C999683B0021952593DAA",
    "semantic_selector": "contract#/scenario",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "AUT-snapshot-bytes-wrong",
    "changed_before_reseal": [
      "candidate/SCENARIO_CONTRACT.json#/scenario"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_CONTRACT_SNAPSHOT_BYTES",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "observed_code": "E_CONTRACT_SNAPSHOT_BYTES",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "2186609E312A1BDEBBB7365A879D04060F05CF58DBE312FE66D73C7D74C33676",
    "semantic_before_sha256": "85E0FE754A853E8AD102EBC7B8F206172807F5DD239C999683B0021952593DAA",
    "semantic_selector": "candidate/SCENARIO_CONTRACT.json#/scenario",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "AUT-snapshot-hash-binding-wrong",
    "changed_before_reseal": [
      "candidate/SOURCE_IDENTITY.json#/contract_snapshot_sha256"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_CONTRACT_SNAPSHOT_HASH",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "observed_code": "E_CONTRACT_SNAPSHOT_HASH",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "A572D91E2EC548ABD89664F42E8A32F955030A708104A7CF06C85BBEAB83F417",
    "semantic_before_sha256": "A653530B38C696F85E016C6A9C7F162B8A7AB878BC89512BF391BCBB98362EE7",
    "semantic_selector": "candidate/SOURCE_IDENTITY.json#/contract_snapshot_sha256",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "AUT-source-identity-contract-sha",
    "changed_before_reseal": [
      "candidate/SOURCE_IDENTITY.json#/contract_sha256"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SOURCE_IDENTITY_CONTRACT",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "observed_code": "E_SOURCE_IDENTITY_CONTRACT",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "65E061C13076B5352C25FFC31323AFF08327A2440F7F286B0B5A93455E740172",
    "semantic_before_sha256": "A653530B38C696F85E016C6A9C7F162B8A7AB878BC89512BF391BCBB98362EE7",
    "semantic_selector": "candidate/SOURCE_IDENTITY.json#/contract_sha256",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "AUT-source-identity-source-bytes",
    "changed_before_reseal": [
      "candidate/SOURCE_IDENTITY.json#/source/bytes"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SOURCE_IDENTITY_SOURCE_BYTES",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "observed_code": "E_SOURCE_IDENTITY_SOURCE_BYTES",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "46EED45BF4502DD4AE7B0AE15B0FD456ACC4476047ABC781C95B8C118B4E48B4",
    "semantic_before_sha256": "A653530B38C696F85E016C6A9C7F162B8A7AB878BC89512BF391BCBB98362EE7",
    "semantic_selector": "candidate/SOURCE_IDENTITY.json#/source/bytes",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "AUT-source-identity-source-sha",
    "changed_before_reseal": [
      "candidate/SOURCE_IDENTITY.json#/source/sha256"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SOURCE_IDENTITY_SOURCE_HASH",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "observed_code": "E_SOURCE_IDENTITY_SOURCE_HASH",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "CA21CBBD560AE5B7663128EDDF13DD0155471F899C658E37EF7EFA80F646005B",
    "semantic_before_sha256": "A653530B38C696F85E016C6A9C7F162B8A7AB878BC89512BF391BCBB98362EE7",
    "semantic_selector": "candidate/SOURCE_IDENTITY.json#/source/sha256",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "AUT-source-identity-page-count",
    "changed_before_reseal": [
      "candidate/SOURCE_IDENTITY.json#/source/page_count"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SOURCE_IDENTITY_PAGE_COUNT",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "observed_code": "E_SOURCE_IDENTITY_PAGE_COUNT",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "6EABDE6B620A81FCBB54777A4B0C37CD5202C6C3B93C23F0BD5C6A3D40D2E760",
    "semantic_before_sha256": "A653530B38C696F85E016C6A9C7F162B8A7AB878BC89512BF391BCBB98362EE7",
    "semantic_selector": "candidate/SOURCE_IDENTITY.json#/source/page_count",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "AUT-source-identity-media-box",
    "changed_before_reseal": [
      "candidate/SOURCE_IDENTITY.json#/source/media_box"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SOURCE_IDENTITY_MEDIA_BOX",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "observed_code": "E_SOURCE_IDENTITY_MEDIA_BOX",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "AE0482B46566DE4E0ED34F5DAB88999000E4B6CD15895D211EB1327FA8AAD17C",
    "semantic_before_sha256": "A653530B38C696F85E016C6A9C7F162B8A7AB878BC89512BF391BCBB98362EE7",
    "semantic_selector": "candidate/SOURCE_IDENTITY.json#/source/media_box",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "AUT-source-identity-rotation",
    "changed_before_reseal": [
      "candidate/SOURCE_IDENTITY.json#/source/rotations"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SOURCE_IDENTITY_ROTATION",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "observed_code": "E_SOURCE_IDENTITY_ROTATION",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "B38504D49302A070091FB7C12B93478DFE092BB3C75306BEB923E1C024A72F89",
    "semantic_before_sha256": "A653530B38C696F85E016C6A9C7F162B8A7AB878BC89512BF391BCBB98362EE7",
    "semantic_selector": "candidate/SOURCE_IDENTITY.json#/source/rotations",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "AUT-source-identity-recovery-manifest-sha",
    "changed_before_reseal": [
      "candidate/SOURCE_IDENTITY.json#/recovery_manifest_sha256"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SOURCE_IDENTITY_RECOVERY_MANIFEST",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "observed_code": "E_SOURCE_IDENTITY_RECOVERY_MANIFEST",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "31FBA965781DC18B6D597207C1330C736F283E78604BA93135D44A02DBC7187A",
    "semantic_before_sha256": "A653530B38C696F85E016C6A9C7F162B8A7AB878BC89512BF391BCBB98362EE7",
    "semantic_selector": "candidate/SOURCE_IDENTITY.json#/recovery_manifest_sha256",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "AUT-source-identity-recovery-evidence-sha",
    "changed_before_reseal": [
      "candidate/SOURCE_IDENTITY.json#/recovery_evidence_sha256"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SOURCE_IDENTITY_RECOVERY_EVIDENCE",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "observed_code": "E_SOURCE_IDENTITY_RECOVERY_EVIDENCE",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "32814D20C0D5EE3FC784B32E8840341156B6FDC060B01D9E05652A99A7BFEC96",
    "semantic_before_sha256": "A653530B38C696F85E016C6A9C7F162B8A7AB878BC89512BF391BCBB98362EE7",
    "semantic_selector": "candidate/SOURCE_IDENTITY.json#/recovery_evidence_sha256",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "AUT-source-identity-recovery-root",
    "changed_before_reseal": [
      "candidate/SOURCE_IDENTITY.json#/recovery_root"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SOURCE_IDENTITY_RECOVERY_ROOT",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "observed_code": "E_SOURCE_IDENTITY_RECOVERY_ROOT",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "2E923CD00603ECB8BB7E2622E6ADBAA9110FB029AE2B216DBE3ED92D7B3010E3",
    "semantic_before_sha256": "A653530B38C696F85E016C6A9C7F162B8A7AB878BC89512BF391BCBB98362EE7",
    "semantic_selector": "candidate/SOURCE_IDENTITY.json#/recovery_root",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "AUT-source-identity-history-true",
    "changed_before_reseal": [
      "candidate/SOURCE_IDENTITY.json#/historical_material_opened"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SOURCE_IDENTITY_HISTORY",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "observed_code": "E_SOURCE_IDENTITY_HISTORY",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "692F6D70411DA9DE36C79CA608496FFD73C39DF60ED4D607D1F027F36334168B",
    "semantic_before_sha256": "A653530B38C696F85E016C6A9C7F162B8A7AB878BC89512BF391BCBB98362EE7",
    "semantic_selector": "candidate/SOURCE_IDENTITY.json#/historical_material_opened",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "AUT-source-identity-state-wrong",
    "changed_before_reseal": [
      "candidate/SOURCE_IDENTITY.json#/state"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SOURCE_IDENTITY_STATE",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "observed_code": "E_SOURCE_IDENTITY_STATE",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "CFCC6E7563EB9B828E1100F3AAE6122DF2BC80E771BE6369DFC447CE8B3D006B",
    "semantic_before_sha256": "A653530B38C696F85E016C6A9C7F162B8A7AB878BC89512BF391BCBB98362EE7",
    "semantic_selector": "candidate/SOURCE_IDENTITY.json#/state",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "AUT-recovery-root-wrong",
    "changed_before_reseal": [
      "recovery#/path"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_RECOVERY_ROOT",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "observed_code": "E_RECOVERY_ROOT",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "0B478D047B38609B47D0F199E5FDA4BBA24F65CD3E8B3E4C6CF58A7B5F3B5FDD",
    "semantic_before_sha256": "EDC1C3B8A00A5FFA054876F2F445117D8A36DA74CF1E651A6BAC00A9DCD059B1",
    "semantic_selector": "recovery#/path",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "AUT-recovery-manifest-raw-hash",
    "changed_before_reseal": [
      "recovery/RECOVERY_MANIFEST.json#/raw_sha256"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_RECOVERY_MANIFEST_HASH",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "observed_code": "E_RECOVERY_MANIFEST_HASH",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "3DE0B82AA36DE8BED1D3A6A1731E9935CA1488DA3CBFACC2C5340EA7A810ADF4",
    "semantic_before_sha256": "B4245E1F0B12790B8C1A569C53CEF3A2E40C1CB791E193C2A184398B6DA5E20B",
    "semantic_selector": "recovery/RECOVERY_MANIFEST.json#/raw_sha256",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "AUT-recovery-evidence-raw-hash",
    "changed_before_reseal": [
      "recovery/RECOVERY_EVIDENCE.json#/raw_sha256"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_RECOVERY_EVIDENCE_HASH",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "observed_code": "E_RECOVERY_EVIDENCE_HASH",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "70C3C20C638F9BC68936BDCE612BFC99A18A100A640811E1CD7FF0F3EB8F9F5E",
    "semantic_before_sha256": "BA0689D836B91EF0E4323329E56FE30281920FF04B37A65AF222224533F480E1",
    "semantic_selector": "recovery/RECOVERY_EVIDENCE.json#/raw_sha256",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "AUT-recovery-successor-file-count",
    "changed_before_reseal": [
      "recovery/RECOVERY_MANIFEST.json#/successor_file_count"
    ],
    "changed_by_reseal": [
      "recovery/RECOVERY_MANIFEST.json#/raw_sha256",
      "candidate/SOURCE_IDENTITY.json#/recovery_manifest_sha256",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "recovery_manifest",
      "source_identity",
      "inventory",
      "qa",
      "profile"
    ],
    "expected_code": "E_RECOVERY_FILE_COUNT",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "observed_code": "E_RECOVERY_FILE_COUNT",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "8342FE497F0A3D94165E6DF528420B525BA263C0E28E954E8A02F57620633BB8",
    "semantic_before_sha256": "B4245E1F0B12790B8C1A569C53CEF3A2E40C1CB791E193C2A184398B6DA5E20B",
    "semantic_selector": "recovery/RECOVERY_MANIFEST.json#/successor_file_count",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "AUT-recovery-successor-total-bytes",
    "changed_before_reseal": [
      "recovery/RECOVERY_MANIFEST.json#/successor_total_bytes"
    ],
    "changed_by_reseal": [
      "recovery/RECOVERY_MANIFEST.json#/raw_sha256",
      "candidate/SOURCE_IDENTITY.json#/recovery_manifest_sha256",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "recovery_manifest",
      "source_identity",
      "inventory",
      "qa",
      "profile"
    ],
    "expected_code": "E_RECOVERY_TOTAL_BYTES",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "observed_code": "E_RECOVERY_TOTAL_BYTES",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "74FF69F45A2A134D2933600EDE920EF1A3DB0E8BA6BCF2352950738635EF317E",
    "semantic_before_sha256": "B4245E1F0B12790B8C1A569C53CEF3A2E40C1CB791E193C2A184398B6DA5E20B",
    "semantic_selector": "recovery/RECOVERY_MANIFEST.json#/successor_total_bytes",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "AUT-recovery-manifest-row-path",
    "changed_before_reseal": [
      "recovery/RECOVERY_MANIFEST.json#/files/0/path"
    ],
    "changed_by_reseal": [
      "recovery/RECOVERY_MANIFEST.json#/raw_sha256",
      "candidate/SOURCE_IDENTITY.json#/recovery_manifest_sha256",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "recovery_manifest",
      "source_identity",
      "inventory",
      "qa",
      "profile"
    ],
    "expected_code": "E_RECOVERY_ROW_PATH",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "observed_code": "E_RECOVERY_ROW_PATH",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "15D6AF325712490C99992A5E53291FE10298B9C7DEC626746903FAB61F1E74E4",
    "semantic_before_sha256": "B4245E1F0B12790B8C1A569C53CEF3A2E40C1CB791E193C2A184398B6DA5E20B",
    "semantic_selector": "recovery/RECOVERY_MANIFEST.json#/files/0/path",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "AUT-recovery-manifest-row-bytes",
    "changed_before_reseal": [
      "recovery/RECOVERY_MANIFEST.json#/files/0/bytes"
    ],
    "changed_by_reseal": [
      "recovery/RECOVERY_MANIFEST.json#/raw_sha256",
      "candidate/SOURCE_IDENTITY.json#/recovery_manifest_sha256",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "recovery_manifest",
      "source_identity",
      "inventory",
      "qa",
      "profile"
    ],
    "expected_code": "E_RECOVERY_ROW_BYTES",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "observed_code": "E_RECOVERY_ROW_BYTES",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "2D15FE67F6AE23F41DFAE1C8E1AFCDF7DC66F2994915C75C45A6190217491E9A",
    "semantic_before_sha256": "B4245E1F0B12790B8C1A569C53CEF3A2E40C1CB791E193C2A184398B6DA5E20B",
    "semantic_selector": "recovery/RECOVERY_MANIFEST.json#/files/0/bytes",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "AUT-recovery-manifest-row-hash",
    "changed_before_reseal": [
      "recovery/RECOVERY_MANIFEST.json#/files/0/sha256"
    ],
    "changed_by_reseal": [
      "recovery/RECOVERY_MANIFEST.json#/raw_sha256",
      "candidate/SOURCE_IDENTITY.json#/recovery_manifest_sha256",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "recovery_manifest",
      "source_identity",
      "inventory",
      "qa",
      "profile"
    ],
    "expected_code": "E_RECOVERY_ROW_HASH",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "observed_code": "E_RECOVERY_ROW_HASH",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "F88459EF8DDC96DBB43532C53C67FC6AE2C9BA043B1453FB59783848334715FE",
    "semantic_before_sha256": "B4245E1F0B12790B8C1A569C53CEF3A2E40C1CB791E193C2A184398B6DA5E20B",
    "semantic_selector": "recovery/RECOVERY_MANIFEST.json#/files/0/sha256",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "AUT-recovery-manifest-row-duplicate",
    "changed_before_reseal": [
      "recovery/RECOVERY_MANIFEST.json#/files/1/path"
    ],
    "changed_by_reseal": [
      "recovery/RECOVERY_MANIFEST.json#/raw_sha256",
      "candidate/SOURCE_IDENTITY.json#/recovery_manifest_sha256",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "recovery_manifest",
      "source_identity",
      "inventory",
      "qa",
      "profile"
    ],
    "expected_code": "E_RECOVERY_ROW_DUPLICATE",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "observed_code": "E_RECOVERY_ROW_DUPLICATE",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "A86DC306658F81C6A15B6CDB1AA7C0DE8F32424D81C912F46298C8DDD5E5684F",
    "semantic_before_sha256": "B4245E1F0B12790B8C1A569C53CEF3A2E40C1CB791E193C2A184398B6DA5E20B",
    "semantic_selector": "recovery/RECOVERY_MANIFEST.json#/files/1/path",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "AUT-recovery-forbidden-payload",
    "changed_before_reseal": [
      "recovery/forbidden.pdf"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_RECOVERY_FORBIDDEN",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "observed_code": "E_RECOVERY_FORBIDDEN",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "80CBAF94386B00B5734D9C567850CB5F66763F107BC735161C9827FF7E2CFC98",
    "semantic_before_sha256": "BB1CF0B4201972D880C6E8E01E343E359C265D8E4A9A1237E8D5FB02045BB47A",
    "semantic_selector": "recovery/forbidden.pdf",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "AUT-recovery-evidence-source-binding",
    "changed_before_reseal": [
      "recovery/RECOVERY_EVIDENCE.json#/source_identity"
    ],
    "changed_by_reseal": [
      "recovery/RECOVERY_EVIDENCE.json#/raw_sha256",
      "candidate/SOURCE_IDENTITY.json#/recovery_evidence_sha256",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "recovery_evidence",
      "source_identity",
      "inventory",
      "qa",
      "profile"
    ],
    "expected_code": "E_RECOVERY_SOURCE_BINDING",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "observed_code": "E_RECOVERY_SOURCE_BINDING",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "BC0B5C06F9F1AB5AA05A5796FA90E42618A52636CD5DB59FC518A11718600228",
    "semantic_before_sha256": "BA0689D836B91EF0E4323329E56FE30281920FF04B37A65AF222224533F480E1",
    "semantic_selector": "recovery/RECOVERY_EVIDENCE.json#/source_identity",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "AUT-recovery-evidence-payload-binding",
    "changed_before_reseal": [
      "recovery/RECOVERY_EVIDENCE.json#/payload"
    ],
    "changed_by_reseal": [
      "recovery/RECOVERY_EVIDENCE.json#/raw_sha256",
      "candidate/SOURCE_IDENTITY.json#/recovery_evidence_sha256",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "recovery_evidence",
      "source_identity",
      "inventory",
      "qa",
      "profile"
    ],
    "expected_code": "E_RECOVERY_PAYLOAD_BINDING",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "observed_code": "E_RECOVERY_PAYLOAD_BINDING",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "2E8D245B9F2D6179CA1DB2FFA09CE77A560BE65531DAB4AE6A12EFAF700D6E02",
    "semantic_before_sha256": "BA0689D836B91EF0E4323329E56FE30281920FF04B37A65AF222224533F480E1",
    "semantic_selector": "recovery/RECOVERY_EVIDENCE.json#/payload",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "AUT-recovery-allowed-paths",
    "changed_before_reseal": [
      "recovery/RECOVERY_EVIDENCE.json#/allowed_payload_paths"
    ],
    "changed_by_reseal": [
      "recovery/RECOVERY_EVIDENCE.json#/raw_sha256",
      "candidate/SOURCE_IDENTITY.json#/recovery_evidence_sha256",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "recovery_evidence",
      "source_identity",
      "inventory",
      "qa",
      "profile"
    ],
    "expected_code": "E_RECOVERY_ALLOWED_PATHS",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "observed_code": "E_RECOVERY_ALLOWED_PATHS",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "34C9E4DD95E7784647974CF7D9E8A8EDDB6DB4EB548FF8E53BF09C452081C8DF",
    "semantic_before_sha256": "BA0689D836B91EF0E4323329E56FE30281920FF04B37A65AF222224533F480E1",
    "semantic_selector": "recovery/RECOVERY_EVIDENCE.json#/allowed_payload_paths",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "AUT-recovery-promotion-true",
    "changed_before_reseal": [
      "recovery/RECOVERY_EVIDENCE.json#/promotion"
    ],
    "changed_by_reseal": [
      "recovery/RECOVERY_EVIDENCE.json#/raw_sha256",
      "candidate/SOURCE_IDENTITY.json#/recovery_evidence_sha256",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "recovery_evidence",
      "source_identity",
      "inventory",
      "qa",
      "profile"
    ],
    "expected_code": "E_RECOVERY_PROMOTION",
    "family": "AUT",
    "fixture_root_token": "fixture",
    "observed_code": "E_RECOVERY_PROMOTION",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "3D3074D5FE0C7CB53FAA734433AC4FD72C24067AB8BBB075FE82930FFA44735A",
    "semantic_before_sha256": "BA0689D836B91EF0E4323329E56FE30281920FF04B37A65AF222224533F480E1",
    "semantic_selector": "recovery/RECOVERY_EVIDENCE.json#/promotion",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "TOP-candidate-root-wrong",
    "changed_before_reseal": [
      "candidate#/root"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_CANDIDATE_ROOT",
    "family": "TOP",
    "fixture_root_token": "fixture",
    "observed_code": "E_CANDIDATE_ROOT",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "049618FFF08A7075D639AFF92DDD77C81320934D722BEA4A7D6D772F3BED4853",
    "semantic_before_sha256": "ADEB2123D693A2AF0A63E890F074873949D4FC12143D2C7301C53E250C1346BB",
    "semantic_selector": "candidate#/root",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "TOP-candidate-root-escape",
    "changed_before_reseal": [
      "candidate#/escape"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_PATH_ESCAPE",
    "family": "TOP",
    "fixture_root_token": "fixture",
    "observed_code": "E_PATH_ESCAPE",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "9B996FE6C39AC801F07F199E7197135012D9012CB441483C08480F370FDDF9F7",
    "semantic_before_sha256": "F23F3C62F9C2233F17DEEF0B3CD9AE8E507E1F1B67CC216AF557228B5CA8FD88",
    "semantic_selector": "candidate#/escape",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "TOP-candidate-root-reparse",
    "changed_before_reseal": [
      "candidate#/reparse"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_PATH_REPARSE",
    "family": "TOP",
    "fixture_root_token": "fixture",
    "observed_code": "E_PATH_REPARSE",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "850BF3C9424AA521E1C9A1733071E46449B808A131D603B72BDEAA294A5EB8D0",
    "semantic_before_sha256": "850BF3C9424AA521E1C9A1733071E46449B808A131D603B72BDEAA294A5EB8D0",
    "semantic_selector": "candidate#/reparse",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "TOP-nested-reparse",
    "changed_before_reseal": [
      "candidate/pages/page-001.md#/reparse"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_PATH_REPARSE",
    "family": "TOP",
    "fixture_root_token": "fixture",
    "observed_code": "E_PATH_REPARSE",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "ACEE13FCE8504E1E41A1A36B8D96C3855CBB33F3B484234464CF7070DA88B7E0",
    "semantic_before_sha256": "ACEE13FCE8504E1E41A1A36B8D96C3855CBB33F3B484234464CF7070DA88B7E0",
    "semantic_selector": "candidate/pages/page-001.md#/reparse",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "TOP-root-file-missing",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.md#/physical-entry"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_TOPOLOGY_MISSING",
    "family": "TOP",
    "fixture_root_token": "fixture",
    "observed_code": "E_TOPOLOGY_MISSING",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "59BE6F3A1EEB9B596935C1BFAB21B2DF2FABE3C9BABB331B5BE154B8B9569676",
    "semantic_before_sha256": "09553B42F09160642877BD6989226195B7BE6B0CAAADBCA0ADF548290648FACA",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.md#/physical-entry",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "TOP-root-entry-extra",
    "changed_before_reseal": [
      "candidate/EXTRA.txt#/physical-entry"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_TOPOLOGY_EXTRA",
    "family": "TOP",
    "fixture_root_token": "fixture",
    "observed_code": "E_TOPOLOGY_EXTRA",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "A3A297F4E3E79F4874FD79AF4C41090E8D52D2B7E473709DBD984B7F6B594FCB",
    "semantic_before_sha256": "52C58C567BC2756FF768B653B1BCBC3B8D929B9FE4A26CFD1689269CE6D6CE03",
    "semantic_selector": "candidate/EXTRA.txt#/physical-entry",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "TOP-evidence-file-missing",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/physical-entry"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_TOPOLOGY_MISSING",
    "family": "TOP",
    "fixture_root_token": "fixture",
    "observed_code": "E_TOPOLOGY_MISSING",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "ED19FCDF72DCA037B70570AEDB9CF5F8531D97EC09E4E8B41D4B9E22411AA0A0",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/physical-entry",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "TOP-evidence-file-extra",
    "changed_before_reseal": [
      "candidate/evidence/EXTRA.json#/physical-entry"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_TOPOLOGY_EXTRA",
    "family": "TOP",
    "fixture_root_token": "fixture",
    "observed_code": "E_TOPOLOGY_EXTRA",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "A3A297F4E3E79F4874FD79AF4C41090E8D52D2B7E473709DBD984B7F6B594FCB",
    "semantic_before_sha256": "0D07F8D0A0E57F61FF69A5A637AF9959A00EDF275A18AB6A43AC8EF6B4943D59",
    "semantic_selector": "candidate/evidence/EXTRA.json#/physical-entry",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "TOP-page-missing",
    "changed_before_reseal": [
      "candidate/pages/page-001.md#/physical-entry"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_TOPOLOGY_MISSING",
    "family": "TOP",
    "fixture_root_token": "fixture",
    "observed_code": "E_TOPOLOGY_MISSING",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "C13980595FC0791F3F7873BC3BB0FFECCCEFD5519C97339BEF6C6D6475E54B13",
    "semantic_before_sha256": "ACEE13FCE8504E1E41A1A36B8D96C3855CBB33F3B484234464CF7070DA88B7E0",
    "semantic_selector": "candidate/pages/page-001.md#/physical-entry",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "TOP-source-render-missing",
    "changed_before_reseal": [
      "candidate/renders/source/page-001.png#/physical-entry"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_TOPOLOGY_MISSING",
    "family": "TOP",
    "fixture_root_token": "fixture",
    "observed_code": "E_TOPOLOGY_MISSING",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "374BE7D614F8A3CEA6F7AB6F1BCD82ADDEB020DAC6F555F1AB05BB4A18FC612E",
    "semantic_before_sha256": "E238F0352FE0BDAC3AA96CFF6451CF65D1EA687B3EA4FF957CC7F7B7BC269679",
    "semantic_selector": "candidate/renders/source/page-001.png#/physical-entry",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "TOP-sheet-missing",
    "changed_before_reseal": [
      "candidate/renders/contact_sheets/sheet-001.png#/physical-entry"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_TOPOLOGY_MISSING",
    "family": "TOP",
    "fixture_root_token": "fixture",
    "observed_code": "E_TOPOLOGY_MISSING",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "3A18C0301FB10CE6B34FD570347FB2FFF139E8ECE354F775C9BB9BC1DAC14293",
    "semantic_before_sha256": "D42C22E0588EA37F255ABFCC5169AFA8F38BAFFC5FEEEF7867DD53E1645CE153",
    "semantic_selector": "candidate/renders/contact_sheets/sheet-001.png#/physical-entry",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "TOP-engine-payload-missing",
    "changed_before_reseal": [
      "candidate/engine/payload-001.bin#/physical-entry"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_TOPOLOGY_MISSING",
    "family": "TOP",
    "fixture_root_token": "fixture",
    "observed_code": "E_TOPOLOGY_MISSING",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "E1BA4CB79D2806787B9C86ECA0DA16E0AA9F7FBAFC47D9985780DFF1F6187EE8",
    "semantic_before_sha256": "4272EC9A0FAFE96204582DCBA6BB65927B90A306C539B7703A8F0EB95F8912AD",
    "semantic_selector": "candidate/engine/payload-001.bin#/physical-entry",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "TOP-protected-empty-subtree-nonempty",
    "changed_before_reseal": [
      "candidate/assets/probe.bin#/physical-entry"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_PROTECTED_EMPTY_SUBTREE",
    "family": "TOP",
    "fixture_root_token": "fixture",
    "observed_code": "E_PROTECTED_EMPTY_SUBTREE",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "A3A297F4E3E79F4874FD79AF4C41090E8D52D2B7E473709DBD984B7F6B594FCB",
    "semantic_before_sha256": "BF96CB52C486EC40AAB2D583B1B070AD4AEC705DE1BE12F144CC669380EBBFFC",
    "semantic_selector": "candidate/assets/probe.bin#/physical-entry",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "TOP-forbidden-pdf",
    "changed_before_reseal": [
      "candidate/forbidden.pdf#/physical-entry"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_CANDIDATE_FORBIDDEN_PDF",
    "family": "TOP",
    "fixture_root_token": "fixture",
    "observed_code": "E_CANDIDATE_FORBIDDEN_PDF",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "A3A297F4E3E79F4874FD79AF4C41090E8D52D2B7E473709DBD984B7F6B594FCB",
    "semantic_before_sha256": "0023BE0F8C013CC07E5E25BF101F51BD79095D92522914FD463A47E1F3CD2978",
    "semantic_selector": "candidate/forbidden.pdf#/physical-entry",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "TOP-forbidden-compiled-suffix",
    "changed_before_reseal": [
      "candidate/forbidden.pyc#/physical-entry"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_CANDIDATE_FORBIDDEN_COMPILED",
    "family": "TOP",
    "fixture_root_token": "fixture",
    "observed_code": "E_CANDIDATE_FORBIDDEN_COMPILED",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "A3A297F4E3E79F4874FD79AF4C41090E8D52D2B7E473709DBD984B7F6B594FCB",
    "semantic_before_sha256": "F47B1D9CB42F8BF4CE8945C34F416941D43BEE1666AC5783707ADE98EA07AD24",
    "semantic_selector": "candidate/forbidden.pyc#/physical-entry",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "TOP-forbidden-pycache",
    "changed_before_reseal": [
      "candidate/__pycache__/probe.bin#/physical-entry"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_CANDIDATE_FORBIDDEN_PYCACHE",
    "family": "TOP",
    "fixture_root_token": "fixture",
    "observed_code": "E_CANDIDATE_FORBIDDEN_PYCACHE",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "A3A297F4E3E79F4874FD79AF4C41090E8D52D2B7E473709DBD984B7F6B594FCB",
    "semantic_before_sha256": "5B67B9F28D6566AD57470140749385926F416F602B9D5DC3BB8E4962256196C5",
    "semantic_selector": "candidate/__pycache__/probe.bin#/physical-entry",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "TOP-forbidden-bridge-runtime",
    "changed_before_reseal": [
      "candidate/_bridge_runtime/probe.bin#/physical-entry"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_CANDIDATE_FORBIDDEN_BRIDGE_RUNTIME",
    "family": "TOP",
    "fixture_root_token": "fixture",
    "observed_code": "E_CANDIDATE_FORBIDDEN_BRIDGE_RUNTIME",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "A3A297F4E3E79F4874FD79AF4C41090E8D52D2B7E473709DBD984B7F6B594FCB",
    "semantic_before_sha256": "CD537A6BAA6A39717CF7E82F0CAE2FA17778ED4ACAFB044BC1DD6746E27A5A32",
    "semantic_selector": "candidate/_bridge_runtime/probe.bin#/physical-entry",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "TOP-forbidden-cache",
    "changed_before_reseal": [
      "candidate/cache/probe.bin#/physical-entry"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_CANDIDATE_FORBIDDEN_CACHE",
    "family": "TOP",
    "fixture_root_token": "fixture",
    "observed_code": "E_CANDIDATE_FORBIDDEN_CACHE",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "A3A297F4E3E79F4874FD79AF4C41090E8D52D2B7E473709DBD984B7F6B594FCB",
    "semantic_before_sha256": "BE7C5146A64E7801867F561DB55522B63B76A90FAF6D129379577E2391CBDD04",
    "semantic_selector": "candidate/cache/probe.bin#/physical-entry",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "TOP-forbidden-pytest-cache",
    "changed_before_reseal": [
      "candidate/.pytest_cache/probe.bin#/physical-entry"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_CANDIDATE_FORBIDDEN_PYTEST_CACHE",
    "family": "TOP",
    "fixture_root_token": "fixture",
    "observed_code": "E_CANDIDATE_FORBIDDEN_PYTEST_CACHE",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "A3A297F4E3E79F4874FD79AF4C41090E8D52D2B7E473709DBD984B7F6B594FCB",
    "semantic_before_sha256": "819F10411C8EC83775F2BF9227CC9743D42E942048A25832115A13C46D3DB6E3",
    "semantic_selector": "candidate/.pytest_cache/probe.bin#/physical-entry",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "TOP-forbidden-tmp",
    "changed_before_reseal": [
      "candidate/tmp/probe.bin#/physical-entry"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_CANDIDATE_FORBIDDEN_TMP",
    "family": "TOP",
    "fixture_root_token": "fixture",
    "observed_code": "E_CANDIDATE_FORBIDDEN_TMP",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "A3A297F4E3E79F4874FD79AF4C41090E8D52D2B7E473709DBD984B7F6B594FCB",
    "semantic_before_sha256": "6629095D7DA65B03E1852D896534871D1E6BDF0B98CCDE0636B9D462922746B0",
    "semantic_selector": "candidate/tmp/probe.bin#/physical-entry",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "TOP-forbidden-temp",
    "changed_before_reseal": [
      "candidate/temp/probe.bin#/physical-entry"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_CANDIDATE_FORBIDDEN_TEMP",
    "family": "TOP",
    "fixture_root_token": "fixture",
    "observed_code": "E_CANDIDATE_FORBIDDEN_TEMP",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "A3A297F4E3E79F4874FD79AF4C41090E8D52D2B7E473709DBD984B7F6B594FCB",
    "semantic_before_sha256": "2B3B109628EDB32D6109814B76D336026116A4DC7CFC2D7F59A1A13A7BC5E577",
    "semantic_selector": "candidate/temp/probe.bin#/physical-entry",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SCH-CONTRACT-schema-wrong",
    "changed_before_reseal": [
      "candidate/SCENARIO_CONTRACT.json#/schema"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SCHEMA_CONTRACT",
    "family": "SCH",
    "fixture_root_token": "fixture",
    "observed_code": "E_SCHEMA_CONTRACT",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "47621613DEB3DA08AD0648FC7AB810EDC2C64C765688A1F1D031904D7BEDA785",
    "semantic_before_sha256": "85E0FE754A853E8AD102EBC7B8F206172807F5DD239C999683B0021952593DAA",
    "semantic_selector": "candidate/SCENARIO_CONTRACT.json#/schema",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SCH-CONTRACT-required-top-member-missing",
    "changed_before_reseal": [
      "candidate/SCENARIO_CONTRACT.json#/pages"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SHAPE_CONTRACT",
    "family": "SCH",
    "fixture_root_token": "fixture",
    "observed_code": "E_SHAPE_CONTRACT",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "9C72F65A22D8782C0F8821FA8B9782974556E4567F436D51C71ED18B8803321C",
    "semantic_before_sha256": "85E0FE754A853E8AD102EBC7B8F206172807F5DD239C999683B0021952593DAA",
    "semantic_selector": "candidate/SCENARIO_CONTRACT.json#/pages",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SCH-SIDECAR-schema-wrong",
    "changed_before_reseal": [
      "source/SOURCE_ADMISSION.json#/schema"
    ],
    "changed_by_reseal": [
      "sidecar#/raw_sha256"
    ],
    "declared_reseals": [
      "sidecar",
      "profile"
    ],
    "expected_code": "E_SCHEMA_SIDECAR",
    "family": "SCH",
    "fixture_root_token": "fixture",
    "observed_code": "E_SCHEMA_SIDECAR",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "6FE028A2F0D93067542FE1C1F23F7A0B014E418B9A21ACCF9F78D6BFA8E307DD",
    "semantic_before_sha256": "CDC335E670653BFE670C3566B37D3FFA56891907A16A6178BFA8CC264F537E77",
    "semantic_selector": "source/SOURCE_ADMISSION.json#/schema",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SCH-SIDECAR-required-top-member-missing",
    "changed_before_reseal": [
      "source/SOURCE_ADMISSION.json#/external_locator"
    ],
    "changed_by_reseal": [
      "sidecar#/raw_sha256"
    ],
    "declared_reseals": [
      "sidecar",
      "profile"
    ],
    "expected_code": "E_SHAPE_SIDECAR",
    "family": "SCH",
    "fixture_root_token": "fixture",
    "observed_code": "E_SHAPE_SIDECAR",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "D89142C9483DA848E48411CB8713A682203EA1A3291D5F4CA10F9969BD25F520",
    "semantic_before_sha256": "CDC335E670653BFE670C3566B37D3FFA56891907A16A6178BFA8CC264F537E77",
    "semantic_selector": "source/SOURCE_ADMISSION.json#/external_locator",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SCH-RECOVERY_MANIFEST-schema-wrong",
    "changed_before_reseal": [
      "recovery/RECOVERY_MANIFEST.json#/schema"
    ],
    "changed_by_reseal": [
      "recovery/RECOVERY_MANIFEST.json#/raw_sha256",
      "candidate/SOURCE_IDENTITY.json#/recovery_manifest_sha256"
    ],
    "declared_reseals": [
      "recovery_manifest"
    ],
    "expected_code": "E_SCHEMA_RECOVERY_MANIFEST",
    "family": "SCH",
    "fixture_root_token": "fixture",
    "observed_code": "E_SCHEMA_RECOVERY_MANIFEST",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "D35A062B65847767803EB853C69BD9C6539CAADE498758B26768973C6ABA234E",
    "semantic_before_sha256": "B4245E1F0B12790B8C1A569C53CEF3A2E40C1CB791E193C2A184398B6DA5E20B",
    "semantic_selector": "recovery/RECOVERY_MANIFEST.json#/schema",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SCH-RECOVERY_MANIFEST-required-top-member-missing",
    "changed_before_reseal": [
      "recovery/RECOVERY_MANIFEST.json#/assets"
    ],
    "changed_by_reseal": [
      "recovery/RECOVERY_MANIFEST.json#/raw_sha256",
      "candidate/SOURCE_IDENTITY.json#/recovery_manifest_sha256"
    ],
    "declared_reseals": [
      "recovery_manifest"
    ],
    "expected_code": "E_SHAPE_RECOVERY_MANIFEST",
    "family": "SCH",
    "fixture_root_token": "fixture",
    "observed_code": "E_SHAPE_RECOVERY_MANIFEST",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "A7920B22625CD7D56FE643381854CD479A1BC36477165D4D0B6F6B8400BC4017",
    "semantic_before_sha256": "B4245E1F0B12790B8C1A569C53CEF3A2E40C1CB791E193C2A184398B6DA5E20B",
    "semantic_selector": "recovery/RECOVERY_MANIFEST.json#/assets",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SCH-RECOVERY_EVIDENCE-schema-wrong",
    "changed_before_reseal": [
      "recovery/RECOVERY_EVIDENCE.json#/schema"
    ],
    "changed_by_reseal": [
      "recovery/RECOVERY_EVIDENCE.json#/raw_sha256",
      "candidate/SOURCE_IDENTITY.json#/recovery_evidence_sha256"
    ],
    "declared_reseals": [
      "recovery_evidence"
    ],
    "expected_code": "E_SCHEMA_RECOVERY_EVIDENCE",
    "family": "SCH",
    "fixture_root_token": "fixture",
    "observed_code": "E_SCHEMA_RECOVERY_EVIDENCE",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "7A3DF8EF0BC2D61794EAF144FAA43F310ED0CF15EE573246C1AD652465F3EE36",
    "semantic_before_sha256": "BA0689D836B91EF0E4323329E56FE30281920FF04B37A65AF222224533F480E1",
    "semantic_selector": "recovery/RECOVERY_EVIDENCE.json#/schema",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SCH-RECOVERY_EVIDENCE-required-top-member-missing",
    "changed_before_reseal": [
      "recovery/RECOVERY_EVIDENCE.json#/allowed_payload_paths"
    ],
    "changed_by_reseal": [
      "recovery/RECOVERY_EVIDENCE.json#/raw_sha256",
      "candidate/SOURCE_IDENTITY.json#/recovery_evidence_sha256"
    ],
    "declared_reseals": [
      "recovery_evidence"
    ],
    "expected_code": "E_SHAPE_RECOVERY_EVIDENCE",
    "family": "SCH",
    "fixture_root_token": "fixture",
    "observed_code": "E_SHAPE_RECOVERY_EVIDENCE",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "2047D8E11289BB1D8AAA4F6787B48D474762747C25FA1E13E95429B21E333B42",
    "semantic_before_sha256": "BA0689D836B91EF0E4323329E56FE30281920FF04B37A65AF222224533F480E1",
    "semantic_selector": "recovery/RECOVERY_EVIDENCE.json#/allowed_payload_paths",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SCH-QA-schema-wrong",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/schema"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SCHEMA_QA",
    "family": "SCH",
    "fixture_root_token": "fixture",
    "observed_code": "E_SCHEMA_QA",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "9CF91757EDF872C5AB21C373FFB8BD23DD3ADDA51D1FCC2A4BD16C09B1521F16",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/schema",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SCH-QA-required-top-member-missing",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/asset_count"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SHAPE_QA",
    "family": "SCH",
    "fixture_root_token": "fixture",
    "observed_code": "E_SHAPE_QA",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "55EC79230938B872552A82308E70D3116920EE5532F82EF5AFA1A1818282D585",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/asset_count",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SCH-SOURCE_IDENTITY-schema-wrong",
    "changed_before_reseal": [
      "candidate/SOURCE_IDENTITY.json#/schema"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SCHEMA_SOURCE_IDENTITY",
    "family": "SCH",
    "fixture_root_token": "fixture",
    "observed_code": "E_SCHEMA_SOURCE_IDENTITY",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "2D84135AC5C891F0A766BB91AA44A9C2FABC392752153D83B06D85C6E7DE6B0D",
    "semantic_before_sha256": "A653530B38C696F85E016C6A9C7F162B8A7AB878BC89512BF391BCBB98362EE7",
    "semantic_selector": "candidate/SOURCE_IDENTITY.json#/schema",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SCH-SOURCE_IDENTITY-required-top-member-missing",
    "changed_before_reseal": [
      "candidate/SOURCE_IDENTITY.json#/contract_sha256"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SHAPE_SOURCE_IDENTITY",
    "family": "SCH",
    "fixture_root_token": "fixture",
    "observed_code": "E_SHAPE_SOURCE_IDENTITY",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "1EF49EAA46BC58DF6CE22817AD61DD4D787D8BBF8EE027F9455C843ED347A0EF",
    "semantic_before_sha256": "A653530B38C696F85E016C6A9C7F162B8A7AB878BC89512BF391BCBB98362EE7",
    "semantic_selector": "candidate/SOURCE_IDENTITY.json#/contract_sha256",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SCH-PAGE_PROVENANCE-schema-wrong",
    "changed_before_reseal": [
      "candidate/evidence/PAGE_PROVENANCE.json#/schema"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SCHEMA_PAGE_PROVENANCE",
    "family": "SCH",
    "fixture_root_token": "fixture",
    "observed_code": "E_SCHEMA_PAGE_PROVENANCE",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "772F37ADA7C8DF4DF6C2E7E7BEEA28AFB5A5980C585F3517D15B3D90A9C0B50E",
    "semantic_before_sha256": "8883C01AAD015435930C1509D93E433F44832A25C184A5D5D684AE0380886075",
    "semantic_selector": "candidate/evidence/PAGE_PROVENANCE.json#/schema",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SCH-PAGE_PROVENANCE-required-top-member-missing",
    "changed_before_reseal": [
      "candidate/evidence/PAGE_PROVENANCE.json#/rows"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SHAPE_PAGE_PROVENANCE",
    "family": "SCH",
    "fixture_root_token": "fixture",
    "observed_code": "E_SHAPE_PAGE_PROVENANCE",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "5E1DE32FE106BB82794B739CEB14CA0B9CFCC3417F2EF8CE85564E3F169DACBC",
    "semantic_before_sha256": "8883C01AAD015435930C1509D93E433F44832A25C184A5D5D684AE0380886075",
    "semantic_selector": "candidate/evidence/PAGE_PROVENANCE.json#/rows",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SCH-CONTENT_PROVENANCE-schema-wrong",
    "changed_before_reseal": [
      "candidate/evidence/CONTENT_PROVENANCE.json#/schema"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SCHEMA_CONTENT_PROVENANCE",
    "family": "SCH",
    "fixture_root_token": "fixture",
    "observed_code": "E_SCHEMA_CONTENT_PROVENANCE",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "7173BC346F4F89C255AF3683D77E8C9C6EBFAF5DC3BE45ABE2D5E42C082D3005",
    "semantic_before_sha256": "1AA6D23B05CD7BD4D7DE4FCE79478742086702FFFB7A9CCDC677931BD5775F0F",
    "semantic_selector": "candidate/evidence/CONTENT_PROVENANCE.json#/schema",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SCH-CONTENT_PROVENANCE-required-top-member-missing",
    "changed_before_reseal": [
      "candidate/evidence/CONTENT_PROVENANCE.json#/rows"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SHAPE_CONTENT_PROVENANCE",
    "family": "SCH",
    "fixture_root_token": "fixture",
    "observed_code": "E_SHAPE_CONTENT_PROVENANCE",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "E77304F24C7378B664308BE31EC4CBB6313EFB5BB4FE752F2D961371BC270BA8",
    "semantic_before_sha256": "1AA6D23B05CD7BD4D7DE4FCE79478742086702FFFB7A9CCDC677931BD5775F0F",
    "semantic_selector": "candidate/evidence/CONTENT_PROVENANCE.json#/rows",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SCH-ASSET_PROVENANCE-schema-wrong",
    "changed_before_reseal": [
      "candidate/evidence/ASSET_PROVENANCE.json#/schema"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SCHEMA_ASSET_PROVENANCE",
    "family": "SCH",
    "fixture_root_token": "fixture",
    "observed_code": "E_SCHEMA_ASSET_PROVENANCE",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "D79F74F73CBF97513F11C33F6F745D8D011B1E45BE370A6F6AA23A829B1E6F8E",
    "semantic_before_sha256": "A254A278D9D21535D29E390C15784F79A1CD1349058C6B4C24EDCD2A62B7BB13",
    "semantic_selector": "candidate/evidence/ASSET_PROVENANCE.json#/schema",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SCH-ASSET_PROVENANCE-required-top-member-missing",
    "changed_before_reseal": [
      "candidate/evidence/ASSET_PROVENANCE.json#/referenced"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SHAPE_ASSET_PROVENANCE",
    "family": "SCH",
    "fixture_root_token": "fixture",
    "observed_code": "E_SHAPE_ASSET_PROVENANCE",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "8E261382EF4D9F176097BC456254645BE634AF7B649D1446C6353300D3D29F91",
    "semantic_before_sha256": "A254A278D9D21535D29E390C15784F79A1CD1349058C6B4C24EDCD2A62B7BB13",
    "semantic_selector": "candidate/evidence/ASSET_PROVENANCE.json#/referenced",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SCH-ENTITY_INVENTORY-schema-wrong",
    "changed_before_reseal": [
      "candidate/evidence/ENTITY_INVENTORY.json#/schema"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SCHEMA_ENTITY_INVENTORY",
    "family": "SCH",
    "fixture_root_token": "fixture",
    "observed_code": "E_SCHEMA_ENTITY_INVENTORY",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "6E1808A9A65BDDB5D8BBAB1E73583ACBE3EC6E4F31EC2F063202902C16FA2612",
    "semantic_before_sha256": "FDAF4267C7EC1346DF421CE0D32C0AC2F57C92E50BD86C8AC8882DA0DEABF9C5",
    "semantic_selector": "candidate/evidence/ENTITY_INVENTORY.json#/schema",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SCH-ENTITY_INVENTORY-required-top-member-missing",
    "changed_before_reseal": [
      "candidate/evidence/ENTITY_INVENTORY.json#/rows"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SHAPE_ENTITY_INVENTORY",
    "family": "SCH",
    "fixture_root_token": "fixture",
    "observed_code": "E_SHAPE_ENTITY_INVENTORY",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "FFD764BE64D37C3562674579FD46149EF3C6F12056CFEFE41424F98D6F870C4D",
    "semantic_before_sha256": "FDAF4267C7EC1346DF421CE0D32C0AC2F57C92E50BD86C8AC8882DA0DEABF9C5",
    "semantic_selector": "candidate/evidence/ENTITY_INVENTORY.json#/rows",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SCH-HANDOUT_INVENTORY-schema-wrong",
    "changed_before_reseal": [
      "candidate/evidence/HANDOUT_INVENTORY.json#/schema"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SCHEMA_HANDOUT_INVENTORY",
    "family": "SCH",
    "fixture_root_token": "fixture",
    "observed_code": "E_SCHEMA_HANDOUT_INVENTORY",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "8CE39084FEE17486AD81328441AB2734BE953B4E7096023858D8556C5A36A51B",
    "semantic_before_sha256": "3BF301D194AC6B027A453AB0627ED5983B19DF82EE2D0499505F93CB360A2E9E",
    "semantic_selector": "candidate/evidence/HANDOUT_INVENTORY.json#/schema",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SCH-HANDOUT_INVENTORY-required-top-member-missing",
    "changed_before_reseal": [
      "candidate/evidence/HANDOUT_INVENTORY.json#/required_count"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SHAPE_HANDOUT_INVENTORY",
    "family": "SCH",
    "fixture_root_token": "fixture",
    "observed_code": "E_SHAPE_HANDOUT_INVENTORY",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "FCAA86A7F846B915493D0F812392387FE4599FF4B279D1999DB0E5D8154D24BB",
    "semantic_before_sha256": "3BF301D194AC6B027A453AB0627ED5983B19DF82EE2D0499505F93CB360A2E9E",
    "semantic_selector": "candidate/evidence/HANDOUT_INVENTORY.json#/required_count",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SCH-NAVIGATION_INVENTORY-schema-wrong",
    "changed_before_reseal": [
      "candidate/evidence/NAVIGATION_INVENTORY.json#/schema"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SCHEMA_NAVIGATION_INVENTORY",
    "family": "SCH",
    "fixture_root_token": "fixture",
    "observed_code": "E_SCHEMA_NAVIGATION_INVENTORY",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "D72D2F0EB8B4B86DBCC720DC206371C2DA1E3EFC8E03C7EA75428AED10EE6B3A",
    "semantic_before_sha256": "65CECA80B15F2917C8FA968ABA6103BD7C52DBB65C9C1751C1105D4866E73D39",
    "semantic_selector": "candidate/evidence/NAVIGATION_INVENTORY.json#/schema",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SCH-NAVIGATION_INVENTORY-required-top-member-missing",
    "changed_before_reseal": [
      "candidate/evidence/NAVIGATION_INVENTORY.json#/rows"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SHAPE_NAVIGATION_INVENTORY",
    "family": "SCH",
    "fixture_root_token": "fixture",
    "observed_code": "E_SHAPE_NAVIGATION_INVENTORY",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "251946893A01792323DF1CE7C4B7B369E15C22684CDAAAB8ED91E78011643EA4",
    "semantic_before_sha256": "65CECA80B15F2917C8FA968ABA6103BD7C52DBB65C9C1751C1105D4866E73D39",
    "semantic_selector": "candidate/evidence/NAVIGATION_INVENTORY.json#/rows",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SCH-CONTENT_MODE_REVIEW-schema-wrong",
    "changed_before_reseal": [
      "candidate/evidence/CONTENT_MODE_REVIEW.json#/schema"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SCHEMA_CONTENT_MODE_REVIEW",
    "family": "SCH",
    "fixture_root_token": "fixture",
    "observed_code": "E_SCHEMA_CONTENT_MODE_REVIEW",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "E375F7C446F5742E4FAA52723678DCCCC8E346046157EDEE8D17A818876BDD22",
    "semantic_before_sha256": "F79948D9403AAB66F3F058122E6C14E31AC919E9C4D54AC71E722B650BC2BDC7",
    "semantic_selector": "candidate/evidence/CONTENT_MODE_REVIEW.json#/schema",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SCH-CONTENT_MODE_REVIEW-required-top-member-missing",
    "changed_before_reseal": [
      "candidate/evidence/CONTENT_MODE_REVIEW.json#/rows"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SHAPE_CONTENT_MODE_REVIEW",
    "family": "SCH",
    "fixture_root_token": "fixture",
    "observed_code": "E_SHAPE_CONTENT_MODE_REVIEW",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "CF27276EDD95E177A48BB0BCFCC055794591FD69491FA6D8D94365BE485C89B5",
    "semantic_before_sha256": "F79948D9403AAB66F3F058122E6C14E31AC919E9C4D54AC71E722B650BC2BDC7",
    "semantic_selector": "candidate/evidence/CONTENT_MODE_REVIEW.json#/rows",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SCH-REFERENCE_ONLY_AUDIT-schema-wrong",
    "changed_before_reseal": [
      "candidate/evidence/REFERENCE_ONLY_AUDIT.json#/schema"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SCHEMA_REFERENCE_ONLY_AUDIT",
    "family": "SCH",
    "fixture_root_token": "fixture",
    "observed_code": "E_SCHEMA_REFERENCE_ONLY_AUDIT",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "92F00C91B1078E0E776B307B387AA3B2163F099DA542B98AB4E4520506957E5F",
    "semantic_before_sha256": "43D7D5E56C1CF1010822FC667E333D5123E9329885692FA6C65EF3DA3A4E86E4",
    "semantic_selector": "candidate/evidence/REFERENCE_ONLY_AUDIT.json#/schema",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SCH-REFERENCE_ONLY_AUDIT-required-top-member-missing",
    "changed_before_reseal": [
      "candidate/evidence/REFERENCE_ONLY_AUDIT.json#/historical_material_opened"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SHAPE_REFERENCE_ONLY_AUDIT",
    "family": "SCH",
    "fixture_root_token": "fixture",
    "observed_code": "E_SHAPE_REFERENCE_ONLY_AUDIT",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "CED59DD242DC1FA8EE191E0A4C32ADC9A88D71FEDA0B1E3A0154A341F25F2AF8",
    "semantic_before_sha256": "43D7D5E56C1CF1010822FC667E333D5123E9329885692FA6C65EF3DA3A4E86E4",
    "semantic_selector": "candidate/evidence/REFERENCE_ONLY_AUDIT.json#/historical_material_opened",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SCH-BLOCKER_LEDGER-schema-wrong",
    "changed_before_reseal": [
      "candidate/evidence/BLOCKER_LEDGER.json#/schema"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SCHEMA_BLOCKER_LEDGER",
    "family": "SCH",
    "fixture_root_token": "fixture",
    "observed_code": "E_SCHEMA_BLOCKER_LEDGER",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "FBEEFC73E5485305302FB99DB7CF6010C5EBE1DE36B0B666FD267ED35AC85DB4",
    "semantic_before_sha256": "80DF881212B688B0835090A00963414D693DD059A539387179A3CA01A86D7E02",
    "semantic_selector": "candidate/evidence/BLOCKER_LEDGER.json#/schema",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SCH-BLOCKER_LEDGER-required-top-member-missing",
    "changed_before_reseal": [
      "candidate/evidence/BLOCKER_LEDGER.json#/open_count"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SHAPE_BLOCKER_LEDGER",
    "family": "SCH",
    "fixture_root_token": "fixture",
    "observed_code": "E_SHAPE_BLOCKER_LEDGER",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "064FD46F050841BCA1C00E9198A4FBC39BF2C31751EBC3FD78D54C44A3BFC5DC",
    "semantic_before_sha256": "80DF881212B688B0835090A00963414D693DD059A539387179A3CA01A86D7E02",
    "semantic_selector": "candidate/evidence/BLOCKER_LEDGER.json#/open_count",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SCH-COMMANDS-schema-wrong",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/schema"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SCHEMA_COMMANDS",
    "family": "SCH",
    "fixture_root_token": "fixture",
    "observed_code": "E_SCHEMA_COMMANDS",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "6817C27E8304DCC2CAEF20BE1AFC7E1D472A5FCD6D782D2DB44BB6F2341B4579",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/schema",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SCH-COMMANDS-required-top-member-missing",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/actions"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SHAPE_COMMANDS",
    "family": "SCH",
    "fixture_root_token": "fixture",
    "observed_code": "E_SHAPE_COMMANDS",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "795051103566C873C3E6FCF5F96440F9216A785062E5B2285694935470947326",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/actions",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SCH-qa-unexpected-top-member",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/unexpected"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SHAPE_QA",
    "family": "SCH",
    "fixture_root_token": "fixture",
    "observed_code": "E_SHAPE_QA",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "7FD28E829FB2164A9E1D6B4E4631F8B64213C1961DBD7EE5BB7AE9D1ABBABC10",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/unexpected",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "LED-open-count-wrong",
    "changed_before_reseal": [
      "candidate/evidence/BLOCKER_LEDGER.json#/open_count"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_LEDGER_OPEN_COUNT",
    "family": "LED",
    "fixture_root_token": "fixture",
    "observed_code": "E_LEDGER_OPEN_COUNT",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "6964F1814CCEF26BBFDC3F52A3012B82095F88122A531E2D6555DEE4FF2F0CD3",
    "semantic_before_sha256": "80DF881212B688B0835090A00963414D693DD059A539387179A3CA01A86D7E02",
    "semantic_selector": "candidate/evidence/BLOCKER_LEDGER.json#/open_count",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "LED-row-count-wrong",
    "changed_before_reseal": [
      "candidate/evidence/BLOCKER_LEDGER.json#/rows"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_LEDGER_ROW_COUNT",
    "family": "LED",
    "fixture_root_token": "fixture",
    "observed_code": "E_LEDGER_ROW_COUNT",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "2A5015F744AA99CB9DBEE0666BB2DC6C56FFADEF77A35B99706B183BE1F81372",
    "semantic_before_sha256": "80DF881212B688B0835090A00963414D693DD059A539387179A3CA01A86D7E02",
    "semantic_selector": "candidate/evidence/BLOCKER_LEDGER.json#/rows",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "LED-row-state-closed",
    "changed_before_reseal": [
      "candidate/evidence/BLOCKER_LEDGER.json#/rows/0/state"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_LEDGER_ROW_STATE",
    "family": "LED",
    "fixture_root_token": "fixture",
    "observed_code": "E_LEDGER_ROW_STATE",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "0516AE7A6EF6F55D0B078A3C69A13823AED4205A11C34F5509E12F2E64F67310",
    "semantic_before_sha256": "80DF881212B688B0835090A00963414D693DD059A539387179A3CA01A86D7E02",
    "semantic_selector": "candidate/evidence/BLOCKER_LEDGER.json#/rows/0/state",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "LED-review-state-closed",
    "changed_before_reseal": [
      "candidate/evidence/BLOCKER_LEDGER.json#/rows/0/review_state"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_LEDGER_REVIEW_STATE",
    "family": "LED",
    "fixture_root_token": "fixture",
    "observed_code": "E_LEDGER_REVIEW_STATE",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "0F41B8AA902529007344FC2FA086593A9C7A90B3BEAD394A1B10652C115EAA08",
    "semantic_before_sha256": "80DF881212B688B0835090A00963414D693DD059A539387179A3CA01A86D7E02",
    "semantic_selector": "candidate/evidence/BLOCKER_LEDGER.json#/rows/0/review_state",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "LED-blocker-id-set-wrong",
    "changed_before_reseal": [
      "candidate/evidence/BLOCKER_LEDGER.json#/rows/0/id"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_LEDGER_IDS",
    "family": "LED",
    "fixture_root_token": "fixture",
    "observed_code": "E_LEDGER_IDS",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "1EE119F5A4F64CD435AAE1B5A59350B1C36EBAEC4E4194C7D56EDD142E61E075",
    "semantic_before_sha256": "80DF881212B688B0835090A00963414D693DD059A539387179A3CA01A86D7E02",
    "semantic_selector": "candidate/evidence/BLOCKER_LEDGER.json#/rows/0/id",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "LED-affected-scope-count-wrong",
    "changed_before_reseal": [
      "candidate/evidence/BLOCKER_LEDGER.json#/rows/0/scope"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_LEDGER_SCOPE",
    "family": "LED",
    "fixture_root_token": "fixture",
    "observed_code": "E_LEDGER_SCOPE",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "3D965A67DA9EE3CD466285A66661A941C5572E4E2793E3DF3F280AB58F174081",
    "semantic_before_sha256": "80DF881212B688B0835090A00963414D693DD059A539387179A3CA01A86D7E02",
    "semantic_selector": "candidate/evidence/BLOCKER_LEDGER.json#/rows/0/scope",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "INV-ordinary-row-missing",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/RECONSTRUCTED_EN.md"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_INV_ORDINARY_ROW_MISSING",
    "family": "INV",
    "fixture_root_token": "fixture",
    "observed_code": "E_INV_ORDINARY_ROW_MISSING",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "2651A112671B83128B71E434FC91E34E65659E33DB6B9E04CB8D703125F0D2F8",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/RECONSTRUCTED_EN.md",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "INV-evidence-row-missing",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/evidence/COMMANDS.json"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_INV_EVIDENCE_ROW_MISSING",
    "family": "INV",
    "fixture_root_token": "fixture",
    "observed_code": "E_INV_EVIDENCE_ROW_MISSING",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "17B68CB10E05F07D9502C0FDC66366C297BAFEE1A554CD718B79F509F59B8E15",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/evidence/COMMANDS.json",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "INV-sheet-row-missing",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-001.png"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_INV_SHEET_ROW_MISSING",
    "family": "INV",
    "fixture_root_token": "fixture",
    "observed_code": "E_INV_SHEET_ROW_MISSING",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "22879E7C82D5EF36B8AAF33A31B13DC58393CC3E1D10279363CA20A782ACECCE",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-001.png",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "INV-stale-extra-path",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/-"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_INV_STALE_EXTRA_PATH",
    "family": "INV",
    "fixture_root_token": "fixture",
    "observed_code": "E_INV_STALE_EXTRA_PATH",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "8558E1D46EF87E2F1ED0EEF585EC81DA11C8C1A4D1BA529725EDE6CEEC1115E4",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/-",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "INV-duplicate-path",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/1/path"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_INV_DUPLICATE_PATH",
    "family": "INV",
    "fixture_root_token": "fixture",
    "observed_code": "E_INV_DUPLICATE_PATH",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "FBE2195C712EC42FB24BCF4953003135D05195841CA5A93CE89C30661D2981F0",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/1/path",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "INV-qa-included",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/-"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_INV_QA_INCLUDED",
    "family": "INV",
    "fixture_root_token": "fixture",
    "observed_code": "E_INV_QA_INCLUDED",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "34D5BBE78AE71F27CE284216BDF10BA53933B13B0CD1056257966DAE52E8DECD",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/-",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "INV-cardinality-wrong",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_count"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_INV_CARDINALITY",
    "family": "INV",
    "fixture_root_token": "fixture",
    "observed_code": "E_INV_CARDINALITY",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "307AADAA304C7DC8663FDD5B265B3A1401BF2507CBE66E70466EAD744B09C5FC",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_count",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "INV-order-nonordinal",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_INV_ORDER_NONORDINAL",
    "family": "INV",
    "fixture_root_token": "fixture",
    "observed_code": "E_INV_ORDER_NONORDINAL",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "BAEFB33BA618FC90E3CF5B95D4CFD63E373D4579DF3D67E91479F3783DB6F325",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "INV-row-bytes-wrong",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/0/bytes"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_INV_ROW_BYTES",
    "family": "INV",
    "fixture_root_token": "fixture",
    "observed_code": "E_INV_ROW_BYTES",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "0F9B35F557A85E7A144602A71F0E1670F5C5D6C0A61A14374298959AF41A65D4",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/0/bytes",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "INV-row-hash-wrong",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/0/sha256"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_INV_ROW_HASH",
    "family": "INV",
    "fixture_root_token": "fixture",
    "observed_code": "E_INV_ROW_HASH",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "ADD3F4A0348789F3B95527EF8DAC6C225DFE2FFDE9DD879233A564313C7662FD",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/0/sha256",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "INV-row-hash-lowercase",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/0/sha256"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_INV_ROW_HASH_LOWERCASE",
    "family": "INV",
    "fixture_root_token": "fixture",
    "observed_code": "E_INV_ROW_HASH_LOWERCASE",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "D20A31815DAB374C811AA0CAD28B7A54F616EA893F70CAD9044F0E083BE33D80",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/0/sha256",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "INV-digest-wrong",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_INV_DIGEST",
    "family": "INV",
    "fixture_root_token": "fixture",
    "observed_code": "E_INV_DIGEST",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "CEAA4567B5572C8705F68424EFA7BAFC6240AA31BDF0A356E71E45E081022514",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "INV-path-backslash",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/0/path"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_INV_PATH_BACKSLASH",
    "family": "INV",
    "fixture_root_token": "fixture",
    "observed_code": "E_INV_PATH_BACKSLASH",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "06352986F961D0D965623C2682EE05A4285B413B078A98A98C157DFFA34857E6",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/0/path",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "INV-path-absolute-or-drive",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/0/path"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_INV_PATH_ABSOLUTE_OR_DRIVE",
    "family": "INV",
    "fixture_root_token": "fixture",
    "observed_code": "E_INV_PATH_ABSOLUTE_OR_DRIVE",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "0F6D1C4759923FAA39B77B14564EAB4B8E04B1E7589982184B3200F5DD6AE1F9",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/0/path",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "INV-path-parent-segment",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/0/path"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_INV_PATH_PARENT_SEGMENT",
    "family": "INV",
    "fixture_root_token": "fixture",
    "observed_code": "E_INV_PATH_PARENT_SEGMENT",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "5DD9ADF28D4C33424E89F1C42B5FDA28C80969AE41E4B2F95122D5619FE3E788",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/0/path",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "INV-path-leading-dot-slash",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/0/path"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_INV_PATH_LEADING_DOT_SLASH",
    "family": "INV",
    "fixture_root_token": "fixture",
    "observed_code": "E_INV_PATH_LEADING_DOT_SLASH",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "7BA10F91487C491D586A16DD8ABE330BE6293BF3900984F954801332728373DD",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/0/path",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "INV-row-shape-wrong",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/0/unexpected"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_INV_ROW_SHAPE",
    "family": "INV",
    "fixture_root_token": "fixture",
    "observed_code": "E_INV_ROW_SHAPE",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "05D0CBA7426DC529DF34B6C8B33928B5EB2250DC3CF73BD85D731028E37E30AE",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/0/unexpected",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "INV-live-file-changed-behind-row",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.md#/live-bytes"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_INV_LIVE_FILE_CHANGED",
    "family": "INV",
    "fixture_root_token": "fixture",
    "observed_code": "E_INV_LIVE_FILE_CHANGED",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "F9F18CA5B9D26684B212F60D47D4D6C5FEB0AA15A9ED296D455C70303C2A875C",
    "semantic_before_sha256": "09553B42F09160642877BD6989226195B7BE6B0CAAADBCA0ADF548290648FACA",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.md#/live-bytes",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "PAG-page-row-missing",
    "changed_before_reseal": [
      "candidate/evidence/PAGE_PROVENANCE.json#/rows/0"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_PAGE_SET",
    "family": "PAG",
    "fixture_root_token": "fixture",
    "observed_code": "E_PAGE_SET",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "A053D99B7AFBD8D1661C3B39474E28F1F5B3D2A727551ECEC581D90A2D26F0B5",
    "semantic_before_sha256": "8883C01AAD015435930C1509D93E433F44832A25C184A5D5D684AE0380886075",
    "semantic_selector": "candidate/evidence/PAGE_PROVENANCE.json#/rows/0",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "PAG-page-row-duplicate",
    "changed_before_reseal": [
      "candidate/evidence/PAGE_PROVENANCE.json#/rows/-"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_PAGE_DUPLICATE",
    "family": "PAG",
    "fixture_root_token": "fixture",
    "observed_code": "E_PAGE_DUPLICATE",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "60A2372F225F5256B3BD4C782AA33DFA4AC6692FC1D254C6E5B62CDCFB92B11A",
    "semantic_before_sha256": "8883C01AAD015435930C1509D93E433F44832A25C184A5D5D684AE0380886075",
    "semantic_selector": "candidate/evidence/PAGE_PROVENANCE.json#/rows/-",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "PAG-page-number-wrong",
    "changed_before_reseal": [
      "candidate/evidence/PAGE_PROVENANCE.json#/rows/0/page_number"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_PAGE_NUMBER",
    "family": "PAG",
    "fixture_root_token": "fixture",
    "observed_code": "E_PAGE_NUMBER",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "0574A8759071105A205FDFD5855613DB223BBF209A2AF8E4B0A2EE2CF434A231",
    "semantic_before_sha256": "8883C01AAD015435930C1509D93E433F44832A25C184A5D5D684AE0380886075",
    "semantic_selector": "candidate/evidence/PAGE_PROVENANCE.json#/rows/0/page_number",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "PAG-page-id-wrong",
    "changed_before_reseal": [
      "candidate/evidence/PAGE_PROVENANCE.json#/rows/0/page_id"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_PAGE_ID",
    "family": "PAG",
    "fixture_root_token": "fixture",
    "observed_code": "E_PAGE_ID",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "6949B75D232705C4C971A81FF169503178F17D962875C0D5090A54F61E99E7DA",
    "semantic_before_sha256": "8883C01AAD015435930C1509D93E433F44832A25C184A5D5D684AE0380886075",
    "semantic_selector": "candidate/evidence/PAGE_PROVENANCE.json#/rows/0/page_id",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "PAG-engine-index-wrong",
    "changed_before_reseal": [
      "candidate/evidence/PAGE_PROVENANCE.json#/rows/0/engine_page_idx"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_PAGE_ENGINE_INDEX",
    "family": "PAG",
    "fixture_root_token": "fixture",
    "observed_code": "E_PAGE_ENGINE_INDEX",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "754C9EA6DE24143B7177FC457ADA70B43274D23B916B24B5F8F2F791938B425A",
    "semantic_before_sha256": "8883C01AAD015435930C1509D93E433F44832A25C184A5D5D684AE0380886075",
    "semantic_selector": "candidate/evidence/PAGE_PROVENANCE.json#/rows/0/engine_page_idx",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "PAG-role-wrong",
    "changed_before_reseal": [
      "candidate/evidence/PAGE_PROVENANCE.json#/rows/0/contract_role"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_PAGE_ROLE",
    "family": "PAG",
    "fixture_root_token": "fixture",
    "observed_code": "E_PAGE_ROLE",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "C3903F78270479A60AF55B5864CFD325ABD8814830F925AB2A24548885368EC9",
    "semantic_before_sha256": "8883C01AAD015435930C1509D93E433F44832A25C184A5D5D684AE0380886075",
    "semantic_selector": "candidate/evidence/PAGE_PROVENANCE.json#/rows/0/contract_role",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "PAG-contract-mode-wrong",
    "changed_before_reseal": [
      "candidate/evidence/PAGE_PROVENANCE.json#/rows/0/contract_content_mode"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_PAGE_CONTENT_MODE",
    "family": "PAG",
    "fixture_root_token": "fixture",
    "observed_code": "E_PAGE_CONTENT_MODE",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "375F814D12F523AF4EC9EC6C4D2D31622563FD1FFA83EC4341F6129938E682B0",
    "semantic_before_sha256": "8883C01AAD015435930C1509D93E433F44832A25C184A5D5D684AE0380886075",
    "semantic_selector": "candidate/evidence/PAGE_PROVENANCE.json#/rows/0/contract_content_mode",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "PAG-markdown-path-wrong",
    "changed_before_reseal": [
      "candidate/evidence/PAGE_PROVENANCE.json#/rows/0/markdown/path"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_PAGE_MARKDOWN_PATH",
    "family": "PAG",
    "fixture_root_token": "fixture",
    "observed_code": "E_PAGE_MARKDOWN_PATH",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "F1636D0B732735B79249888B17E4FB28E5135B461C7799EB4A24D64C59465C5F",
    "semantic_before_sha256": "8883C01AAD015435930C1509D93E433F44832A25C184A5D5D684AE0380886075",
    "semantic_selector": "candidate/evidence/PAGE_PROVENANCE.json#/rows/0/markdown/path",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "PAG-markdown-bytes-wrong",
    "changed_before_reseal": [
      "candidate/evidence/PAGE_PROVENANCE.json#/rows/0/markdown/bytes"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_PAGE_MARKDOWN_BYTES",
    "family": "PAG",
    "fixture_root_token": "fixture",
    "observed_code": "E_PAGE_MARKDOWN_BYTES",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "6BA2138B5B84B5349C9EF0867BE60E19E5716E34EA447F4CDA5ECB1135913544",
    "semantic_before_sha256": "8883C01AAD015435930C1509D93E433F44832A25C184A5D5D684AE0380886075",
    "semantic_selector": "candidate/evidence/PAGE_PROVENANCE.json#/rows/0/markdown/bytes",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "PAG-markdown-hash-wrong",
    "changed_before_reseal": [
      "candidate/evidence/PAGE_PROVENANCE.json#/rows/0/markdown/sha256"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_PAGE_MARKDOWN_HASH",
    "family": "PAG",
    "fixture_root_token": "fixture",
    "observed_code": "E_PAGE_MARKDOWN_HASH",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "D977C4D4CFFD7299F65C12B5AF65CAF381944A5E40A477253C92F773B0D6363C",
    "semantic_before_sha256": "8883C01AAD015435930C1509D93E433F44832A25C184A5D5D684AE0380886075",
    "semantic_selector": "candidate/evidence/PAGE_PROVENANCE.json#/rows/0/markdown/sha256",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "PAG-render-path-wrong",
    "changed_before_reseal": [
      "candidate/evidence/PAGE_PROVENANCE.json#/rows/0/render/path"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_PAGE_RENDER_PATH",
    "family": "PAG",
    "fixture_root_token": "fixture",
    "observed_code": "E_PAGE_RENDER_PATH",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "DED959D578ED393C052521A5A64B1401B83EB71AAFE39418E43948CF72665BDB",
    "semantic_before_sha256": "8883C01AAD015435930C1509D93E433F44832A25C184A5D5D684AE0380886075",
    "semantic_selector": "candidate/evidence/PAGE_PROVENANCE.json#/rows/0/render/path",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "PAG-render-bytes-wrong",
    "changed_before_reseal": [
      "candidate/evidence/PAGE_PROVENANCE.json#/rows/0/render/bytes"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_PAGE_RENDER_BYTES",
    "family": "PAG",
    "fixture_root_token": "fixture",
    "observed_code": "E_PAGE_RENDER_BYTES",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "CFDBCB330C56CD8904060316C8CFC5EA6CCC6E2DFDF6D3186A43D8F24789BCBF",
    "semantic_before_sha256": "8883C01AAD015435930C1509D93E433F44832A25C184A5D5D684AE0380886075",
    "semantic_selector": "candidate/evidence/PAGE_PROVENANCE.json#/rows/0/render/bytes",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "PAG-render-hash-wrong",
    "changed_before_reseal": [
      "candidate/evidence/PAGE_PROVENANCE.json#/rows/0/render/sha256"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_PAGE_RENDER_HASH",
    "family": "PAG",
    "fixture_root_token": "fixture",
    "observed_code": "E_PAGE_RENDER_HASH",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "B794029A68DBD6677467EBC03FFC69018E84B8B5C793D6D0B1A4323B234FE6AA",
    "semantic_before_sha256": "8883C01AAD015435930C1509D93E433F44832A25C184A5D5D684AE0380886075",
    "semantic_selector": "candidate/evidence/PAGE_PROVENANCE.json#/rows/0/render/sha256",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "PAG-render-page-number-wrong",
    "changed_before_reseal": [
      "candidate/evidence/PAGE_PROVENANCE.json#/rows/0/render/page_number"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_PAGE_RENDER_NUMBER",
    "family": "PAG",
    "fixture_root_token": "fixture",
    "observed_code": "E_PAGE_RENDER_NUMBER",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "9D61A2EC6F669B4A474F381682823A4F86E9AA25300D9846DC586B9568162C9C",
    "semantic_before_sha256": "8883C01AAD015435930C1509D93E433F44832A25C184A5D5D684AE0380886075",
    "semantic_selector": "candidate/evidence/PAGE_PROVENANCE.json#/rows/0/render/page_number",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "PAG-render-dimensions-wrong",
    "changed_before_reseal": [
      "candidate/evidence/PAGE_PROVENANCE.json#/rows/0/render/dimensions"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_PAGE_RENDER_DIMENSIONS",
    "family": "PAG",
    "fixture_root_token": "fixture",
    "observed_code": "E_PAGE_RENDER_DIMENSIONS",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "CE28BEE827A2543133DC8DDD8737A3A82F59E04D210133B32B3EB226E18661E1",
    "semantic_before_sha256": "8883C01AAD015435930C1509D93E433F44832A25C184A5D5D684AE0380886075",
    "semantic_selector": "candidate/evidence/PAGE_PROVENANCE.json#/rows/0/render/dimensions",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "PAG-render-dpi-wrong",
    "changed_before_reseal": [
      "candidate/evidence/PAGE_PROVENANCE.json#/rows/0/render/dpi"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_PAGE_RENDER_DPI",
    "family": "PAG",
    "fixture_root_token": "fixture",
    "observed_code": "E_PAGE_RENDER_DPI",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "7406BB4BECFA5251EC4A14E0995ECA8D56B9911B4CDA28D2C5F0B7F7A91E185D",
    "semantic_before_sha256": "8883C01AAD015435930C1509D93E433F44832A25C184A5D5D684AE0380886075",
    "semantic_selector": "candidate/evidence/PAGE_PROVENANCE.json#/rows/0/render/dpi",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "PAG-live-markdown-missing",
    "changed_before_reseal": [
      "candidate/pages/page-002.md#/physical-entry"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_PAGE_MARKDOWN_MISSING",
    "family": "PAG",
    "fixture_root_token": "fixture",
    "observed_code": "E_PAGE_MARKDOWN_MISSING",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "FFE6B5D36221AA7013B51A879D9ACE14B923402FB86348F06F3BABE7B1198F09",
    "semantic_before_sha256": "064D3DFDF0626C24A26699C2847491D118315FB230FA0A6173C1779F45B47F5F",
    "semantic_selector": "candidate/pages/page-002.md#/physical-entry",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "PAG-live-render-missing",
    "changed_before_reseal": [
      "candidate/renders/source/page-002.png#/physical-entry"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_PAGE_RENDER_MISSING",
    "family": "PAG",
    "fixture_root_token": "fixture",
    "observed_code": "E_PAGE_RENDER_MISSING",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "76496D447F4C79E824EB1B05AD062B22F64EF6EB554413312BBAFC971F5B2CFF",
    "semantic_before_sha256": "B7C8865348910CF3C7EF85874AF66D70F2DB7A2AB646FAF27634E0B4AD2F774A",
    "semantic_selector": "candidate/renders/source/page-002.png#/physical-entry",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "PAG-source-page-marker-wrong",
    "changed_before_reseal": [
      "candidate/pages/page-001.md#/source-page-marker"
    ],
    "changed_by_reseal": [
      "candidate/evidence/PAGE_PROVENANCE.json#/rows/0/markdown/bytes",
      "candidate/evidence/PAGE_PROVENANCE.json#/rows/0/markdown/sha256",
      "candidate/evidence/PAGE_PROVENANCE.json#/rows/0/raw_markdown_sha256",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "page_provenance",
      "inventory",
      "qa"
    ],
    "expected_code": "E_PAGE_SOURCE_MARKER",
    "family": "PAG",
    "fixture_root_token": "fixture",
    "observed_code": "E_PAGE_SOURCE_MARKER",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "1E2F0AFC1A6D8763F38F4FAA6E19EF4396F3206CADAE560CBE6C75ED1D4B0F19",
    "semantic_before_sha256": "ACEE13FCE8504E1E41A1A36B8D96C3855CBB33F3B484234464CF7070DA88B7E0",
    "semantic_selector": "candidate/pages/page-001.md#/source-page-marker",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "PAG-render-marker-wrong",
    "changed_before_reseal": [
      "candidate/pages/page-001.md#/render-marker"
    ],
    "changed_by_reseal": [
      "candidate/evidence/PAGE_PROVENANCE.json#/rows/0/markdown/bytes",
      "candidate/evidence/PAGE_PROVENANCE.json#/rows/0/markdown/sha256",
      "candidate/evidence/PAGE_PROVENANCE.json#/rows/0/raw_markdown_sha256",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "page_provenance",
      "inventory",
      "qa"
    ],
    "expected_code": "E_PAGE_RENDER_MARKER",
    "family": "PAG",
    "fixture_root_token": "fixture",
    "observed_code": "E_PAGE_RENDER_MARKER",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "B7B512A2A36B8FFB6822EFB396D72E4FC4CFA64F015DD554F6844A73ECD80B99",
    "semantic_before_sha256": "ACEE13FCE8504E1E41A1A36B8D96C3855CBB33F3B484234464CF7070DA88B7E0",
    "semantic_selector": "candidate/pages/page-001.md#/render-marker",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "PAG-master-concatenation-wrong",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.md#/concatenation"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_MASTER_CONCATENATION",
    "family": "PAG",
    "fixture_root_token": "fixture",
    "observed_code": "E_MASTER_CONCATENATION",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "74E3E7B00FFAC0918C2E155B0AA6C652774ECA1A58BD316709E3A95803FCD855",
    "semantic_before_sha256": "09553B42F09160642877BD6989226195B7BE6B0CAAADBCA0ADF548290648FACA",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.md#/concatenation",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "PAG-content-orphan",
    "changed_before_reseal": [
      "candidate/evidence/CONTENT_PROVENANCE.json#/rows/0/page_number"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_CONTENT_PAGE_LINK",
    "family": "PAG",
    "fixture_root_token": "fixture",
    "observed_code": "E_CONTENT_PAGE_LINK",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "EF9F45A7E0E2F894D951F8B27FA195066BF00CCFE068C77E338BCBFD083D2724",
    "semantic_before_sha256": "1AA6D23B05CD7BD4D7DE4FCE79478742086702FFFB7A9CCDC677931BD5775F0F",
    "semantic_selector": "candidate/evidence/CONTENT_PROVENANCE.json#/rows/0/page_number",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "PAG-content-duplicate",
    "changed_before_reseal": [
      "candidate/evidence/CONTENT_PROVENANCE.json#/rows/1/block_id"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_CONTENT_DUPLICATE",
    "family": "PAG",
    "fixture_root_token": "fixture",
    "observed_code": "E_CONTENT_DUPLICATE",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "82BC18D371335828B3C1E64DF5E8B3A134F4D2AF719E7D3C1D6EED2EF65AB960",
    "semantic_before_sha256": "1AA6D23B05CD7BD4D7DE4FCE79478742086702FFFB7A9CCDC677931BD5775F0F",
    "semantic_selector": "candidate/evidence/CONTENT_PROVENANCE.json#/rows/1/block_id",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "PAG-content-order-wrong",
    "changed_before_reseal": [
      "candidate/evidence/CONTENT_PROVENANCE.json#/rows/1/order"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_CONTENT_ORDER",
    "family": "PAG",
    "fixture_root_token": "fixture",
    "observed_code": "E_CONTENT_ORDER",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "8D5079C14B862022B1B69F4621B05D588A97CF0BEDC7E8E710CE9E1DB4F572D7",
    "semantic_before_sha256": "1AA6D23B05CD7BD4D7DE4FCE79478742086702FFFB7A9CCDC677931BD5775F0F",
    "semantic_selector": "candidate/evidence/CONTENT_PROVENANCE.json#/rows/1/order",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "PAG-content-predecessor-wrong",
    "changed_before_reseal": [
      "candidate/evidence/CONTENT_PROVENANCE.json#/rows/1/predecessor_id"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_CONTENT_PREDECESSOR",
    "family": "PAG",
    "fixture_root_token": "fixture",
    "observed_code": "E_CONTENT_PREDECESSOR",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "8E357FE90745084012032F1162B5FFA333C5302615D3C9505A308EAC2BCE6587",
    "semantic_before_sha256": "1AA6D23B05CD7BD4D7DE4FCE79478742086702FFFB7A9CCDC677931BD5775F0F",
    "semantic_selector": "candidate/evidence/CONTENT_PROVENANCE.json#/rows/1/predecessor_id",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "PAG-content-successor-wrong",
    "changed_before_reseal": [
      "candidate/evidence/CONTENT_PROVENANCE.json#/rows/0/successor_id"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_CONTENT_SUCCESSOR",
    "family": "PAG",
    "fixture_root_token": "fixture",
    "observed_code": "E_CONTENT_SUCCESSOR",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "5CB6902EBC1EDD75D1023F6054F6DB2111ADFBC536197304DF37D40C37BC76A9",
    "semantic_before_sha256": "1AA6D23B05CD7BD4D7DE4FCE79478742086702FFFB7A9CCDC677931BD5775F0F",
    "semantic_selector": "candidate/evidence/CONTENT_PROVENANCE.json#/rows/0/successor_id",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "PAG-content-operation-fabricated",
    "changed_before_reseal": [
      "candidate/evidence/CONTENT_PROVENANCE.json#/rows/0/operations"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_CONTENT_OPERATION",
    "family": "PAG",
    "fixture_root_token": "fixture",
    "observed_code": "E_CONTENT_OPERATION",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "4FAD2E995DBF6B6849E7D85B394CDCA199CAAB099A81F772D66AB8B061BB81CD",
    "semantic_before_sha256": "1AA6D23B05CD7BD4D7DE4FCE79478742086702FFFB7A9CCDC677931BD5775F0F",
    "semantic_selector": "candidate/evidence/CONTENT_PROVENANCE.json#/rows/0/operations",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "PAG-content-asset-link-fabricated",
    "changed_before_reseal": [
      "candidate/evidence/CONTENT_PROVENANCE.json#/rows/0/asset_ids"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_CONTENT_ASSET_LINK",
    "family": "PAG",
    "fixture_root_token": "fixture",
    "observed_code": "E_CONTENT_ASSET_LINK",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "C9425FE5EDB6B8B8EBEFA78A2F1A32818245544BF165B2767F082C028397BA77",
    "semantic_before_sha256": "1AA6D23B05CD7BD4D7DE4FCE79478742086702FFFB7A9CCDC677931BD5775F0F",
    "semantic_selector": "candidate/evidence/CONTENT_PROVENANCE.json#/rows/0/asset_ids",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "NAV-row-missing",
    "changed_before_reseal": [
      "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/0"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_NAV_SET",
    "family": "NAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_NAV_SET",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "00EA264DB1647F03D3971062D824B9659E53BC957C594758902574AA3BA82160",
    "semantic_before_sha256": "65CECA80B15F2917C8FA968ABA6103BD7C52DBB65C9C1751C1105D4866E73D39",
    "semantic_selector": "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/0",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "NAV-anchor-duplicate",
    "changed_before_reseal": [
      "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/1/anchor_id"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_NAV_DUPLICATE",
    "family": "NAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_NAV_DUPLICATE",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "DA68C5363D7FFF4F9D825807546AA592121AF1EB7AD1CCB734F6DC0F299FA47A",
    "semantic_before_sha256": "65CECA80B15F2917C8FA968ABA6103BD7C52DBB65C9C1751C1105D4866E73D39",
    "semantic_selector": "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/1/anchor_id",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "NAV-anchor-id-wrong",
    "changed_before_reseal": [
      "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/0/anchor_id"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_NAV_ANCHOR",
    "family": "NAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_NAV_ANCHOR",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "56C3502FDC7A33531FEDE7C3A228DA83F42AA76ED8DBEB3A0016FBD60C056BC0",
    "semantic_before_sha256": "65CECA80B15F2917C8FA968ABA6103BD7C52DBB65C9C1751C1105D4866E73D39",
    "semantic_selector": "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/0/anchor_id",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "NAV-source-page-wrong",
    "changed_before_reseal": [
      "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/0/source_page_number"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_NAV_PAGE",
    "family": "NAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_NAV_PAGE",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "D51564D6549922EE94BDF873BB324B05EFFF1D269668CEE1ECFE2E42BC874363",
    "semantic_before_sha256": "65CECA80B15F2917C8FA968ABA6103BD7C52DBB65C9C1751C1105D4866E73D39",
    "semantic_selector": "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/0/source_page_number",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "NAV-engine-index-wrong",
    "changed_before_reseal": [
      "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/0/engine_page_idx"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_NAV_ENGINE_INDEX",
    "family": "NAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_NAV_ENGINE_INDEX",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "F7CE1DD5E0D2FBDD1C7939DF60EDC2A4B19AD4C3E6447732736F425E38707519",
    "semantic_before_sha256": "65CECA80B15F2917C8FA968ABA6103BD7C52DBB65C9C1751C1105D4866E73D39",
    "semantic_selector": "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/0/engine_page_idx",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "NAV-first-previous-nonnull",
    "changed_before_reseal": [
      "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/0/previous_anchor"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_NAV_FIRST_PREVIOUS",
    "family": "NAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_NAV_FIRST_PREVIOUS",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "86D3508DB880BAA5F82D884156B4050ADB5842537E40BD6CF06669D0A811157F",
    "semantic_before_sha256": "65CECA80B15F2917C8FA968ABA6103BD7C52DBB65C9C1751C1105D4866E73D39",
    "semantic_selector": "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/0/previous_anchor",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "NAV-last-next-nonnull",
    "changed_before_reseal": [
      "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/123/next_anchor"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_NAV_LAST_NEXT",
    "family": "NAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_NAV_LAST_NEXT",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "5ED269038EC796B68080E872B17FB7CC24E62C1431BE365B36858236D201B7A4",
    "semantic_before_sha256": "65CECA80B15F2917C8FA968ABA6103BD7C52DBB65C9C1751C1105D4866E73D39",
    "semantic_selector": "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/123/next_anchor",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "NAV-middle-previous-wrong",
    "changed_before_reseal": [
      "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/1/previous_anchor"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_NAV_PREVIOUS",
    "family": "NAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_NAV_PREVIOUS",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "660285FE6B0947142871D00E4AA9A21191FB862F434BFDC47CF95066DE317892",
    "semantic_before_sha256": "65CECA80B15F2917C8FA968ABA6103BD7C52DBB65C9C1751C1105D4866E73D39",
    "semantic_selector": "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/1/previous_anchor",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "NAV-middle-next-wrong",
    "changed_before_reseal": [
      "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/1/next_anchor"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_NAV_NEXT",
    "family": "NAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_NAV_NEXT",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "2735CEFD34A954C9731BBC01C14BE039EDAF14ED1B01F99BC05F8FD8CA50850A",
    "semantic_before_sha256": "65CECA80B15F2917C8FA968ABA6103BD7C52DBB65C9C1751C1105D4866E73D39",
    "semantic_selector": "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/1/next_anchor",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "NAV-dangling-link",
    "changed_before_reseal": [
      "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/1/next_anchor"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_NAV_DANGLING",
    "family": "NAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_NAV_DANGLING",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "677B172F06CE1425F49D53EFD631FAD15326DF0F3E997C9EE96B4E61C49AEC2A",
    "semantic_before_sha256": "65CECA80B15F2917C8FA968ABA6103BD7C52DBB65C9C1751C1105D4866E73D39",
    "semantic_selector": "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/1/next_anchor",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "NAV-markdown-path-wrong",
    "changed_before_reseal": [
      "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/0/page_markdown_path"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_NAV_MARKDOWN_PATH",
    "family": "NAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_NAV_MARKDOWN_PATH",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "7C531A769014DB0031AFD68B7D244350775184EBBDADBBFBECDD0F82589B8121",
    "semantic_before_sha256": "65CECA80B15F2917C8FA968ABA6103BD7C52DBB65C9C1751C1105D4866E73D39",
    "semantic_selector": "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/0/page_markdown_path",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "NAV-render-path-wrong",
    "changed_before_reseal": [
      "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/0/source_render_path"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_NAV_RENDER_PATH",
    "family": "NAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_NAV_RENDER_PATH",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "F241BC4E42E4C5E9F583A539B52A3A3E4C01E75BE2AB66AF2215AD25A9B6FEBC",
    "semantic_before_sha256": "65CECA80B15F2917C8FA968ABA6103BD7C52DBB65C9C1751C1105D4866E73D39",
    "semantic_selector": "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/0/source_render_path",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "NAV-render-hash-wrong",
    "changed_before_reseal": [
      "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/0/source_render_sha256"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_NAV_RENDER_HASH",
    "family": "NAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_NAV_RENDER_HASH",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "AB9E8848917B1E152A723A4B7B6EC340206E6F2FEF0CC3F7322B6F2F92781EC1",
    "semantic_before_sha256": "65CECA80B15F2917C8FA968ABA6103BD7C52DBB65C9C1751C1105D4866E73D39",
    "semantic_selector": "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/0/source_render_sha256",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "NAV-role-wrong",
    "changed_before_reseal": [
      "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/0/contract_role"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_NAV_ROLE",
    "family": "NAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_NAV_ROLE",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "D612FD4DD879A7CC7296C3D24C79B29C57D0E6DE3C33340382959E89307AB3D6",
    "semantic_before_sha256": "65CECA80B15F2917C8FA968ABA6103BD7C52DBB65C9C1751C1105D4866E73D39",
    "semantic_selector": "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/0/contract_role",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "NAV-closure-promoted",
    "changed_before_reseal": [
      "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/0/closure_state"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_NAV_CLOSURE",
    "family": "NAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_NAV_CLOSURE",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "464DEF21176B588C8BD1BC477193E1F2A71BE3C908090C4409175D25F5B5A203",
    "semantic_before_sha256": "65CECA80B15F2917C8FA968ABA6103BD7C52DBB65C9C1751C1105D4866E73D39",
    "semantic_selector": "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/0/closure_state",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "AST-row-missing",
    "changed_before_reseal": [
      "candidate/evidence/ASSET_PROVENANCE.json#/rows/0"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_ASSET_SET",
    "family": "AST",
    "fixture_root_token": "fixture",
    "observed_code": "E_ASSET_SET",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "BC80028CC1C0A22579BCA11632F966FAD795DB4F477AB496168578306ECF2013",
    "semantic_before_sha256": "A254A278D9D21535D29E390C15784F79A1CD1349058C6B4C24EDCD2A62B7BB13",
    "semantic_selector": "candidate/evidence/ASSET_PROVENANCE.json#/rows/0",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "AST-id-duplicate",
    "changed_before_reseal": [
      "candidate/evidence/ASSET_PROVENANCE.json#/rows/1/asset_id"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_ASSET_ID_DUPLICATE",
    "family": "AST",
    "fixture_root_token": "fixture",
    "observed_code": "E_ASSET_ID_DUPLICATE",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "E42E202FECEEF20241180068AE96391B27F8BA43D37596D8540D597977FD7F24",
    "semantic_before_sha256": "A254A278D9D21535D29E390C15784F79A1CD1349058C6B4C24EDCD2A62B7BB13",
    "semantic_selector": "candidate/evidence/ASSET_PROVENANCE.json#/rows/1/asset_id",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "AST-path-duplicate",
    "changed_before_reseal": [
      "candidate/evidence/ASSET_PROVENANCE.json#/rows/1/engine_relative_path"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_ASSET_PATH_DUPLICATE",
    "family": "AST",
    "fixture_root_token": "fixture",
    "observed_code": "E_ASSET_PATH_DUPLICATE",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "BB9B3C413D7860226C07AEF3639BA44D1B65BA0A3DE73EDA217B74AEEAD5E34B",
    "semantic_before_sha256": "A254A278D9D21535D29E390C15784F79A1CD1349058C6B4C24EDCD2A62B7BB13",
    "semantic_selector": "candidate/evidence/ASSET_PROVENANCE.json#/rows/1/engine_relative_path",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "AST-hash-duplicate",
    "changed_before_reseal": [
      "candidate/evidence/ASSET_PROVENANCE.json#/rows/1/sha256"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_ASSET_HASH_DUPLICATE",
    "family": "AST",
    "fixture_root_token": "fixture",
    "observed_code": "E_ASSET_HASH_DUPLICATE",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "04AB11A1B65A93308BE4082094942EFC50F6936F3616A03F18D9B48F7BA39A9B",
    "semantic_before_sha256": "A254A278D9D21535D29E390C15784F79A1CD1349058C6B4C24EDCD2A62B7BB13",
    "semantic_selector": "candidate/evidence/ASSET_PROVENANCE.json#/rows/1/sha256",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "AST-live-bytes-wrong",
    "changed_before_reseal": [
      "candidate/engine/payload-001.bin#/bytes"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_ASSET_BYTES",
    "family": "AST",
    "fixture_root_token": "fixture",
    "observed_code": "E_ASSET_BYTES",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "C85A1673F6CE5723F627FAA8CA8BB2220561AE89847F0C351A916F4D61A13E25",
    "semantic_before_sha256": "4272EC9A0FAFE96204582DCBA6BB65927B90A306C539B7703A8F0EB95F8912AD",
    "semantic_selector": "candidate/engine/payload-001.bin#/bytes",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "AST-live-hash-wrong",
    "changed_before_reseal": [
      "candidate/engine/payload-001.bin#/sha256"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_ASSET_HASH",
    "family": "AST",
    "fixture_root_token": "fixture",
    "observed_code": "E_ASSET_HASH",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "56E1035FA7506DB9AC3C7AEE42D9B45343AC222342AC3308507CB3859ABA7586",
    "semantic_before_sha256": "4272EC9A0FAFE96204582DCBA6BB65927B90A306C539B7703A8F0EB95F8912AD",
    "semantic_selector": "candidate/engine/payload-001.bin#/sha256",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "AST-engine-path-missing",
    "changed_before_reseal": [
      "candidate/evidence/ASSET_PROVENANCE.json#/rows/0/engine_relative_path"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_ASSET_ENGINE_MISSING",
    "family": "AST",
    "fixture_root_token": "fixture",
    "observed_code": "E_ASSET_ENGINE_MISSING",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "FB88FE9D5B4FA0E8D4E668C0EF2125800870E56EAE1D52DDB748069B3E9B45F9",
    "semantic_before_sha256": "A254A278D9D21535D29E390C15784F79A1CD1349058C6B4C24EDCD2A62B7BB13",
    "semantic_selector": "candidate/evidence/ASSET_PROVENANCE.json#/rows/0/engine_relative_path",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "AST-engine-path-wrong",
    "changed_before_reseal": [
      "candidate/evidence/ASSET_PROVENANCE.json#/rows/0/engine_relative_path"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_ASSET_ENGINE_PATH",
    "family": "AST",
    "fixture_root_token": "fixture",
    "observed_code": "E_ASSET_ENGINE_PATH",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "1D9A6039492DD73489EDC669309DFAAE9A6AAB041AB88C809660C0FB5EA89641",
    "semantic_before_sha256": "A254A278D9D21535D29E390C15784F79A1CD1349058C6B4C24EDCD2A62B7BB13",
    "semantic_selector": "candidate/evidence/ASSET_PROVENANCE.json#/rows/0/engine_relative_path",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "AST-recovery-binding-wrong",
    "changed_before_reseal": [
      "candidate/evidence/ASSET_PROVENANCE.json#/rows/0/recovery_manifest_binding"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_ASSET_RECOVERY_BINDING",
    "family": "AST",
    "fixture_root_token": "fixture",
    "observed_code": "E_ASSET_RECOVERY_BINDING",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "F788B00F1DE313A4A8320CCF6C24F8A41A4D9EACD6A5FAF839FCCFE18A19ECF1",
    "semantic_before_sha256": "A254A278D9D21535D29E390C15784F79A1CD1349058C6B4C24EDCD2A62B7BB13",
    "semantic_selector": "candidate/evidence/ASSET_PROVENANCE.json#/rows/0/recovery_manifest_binding",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "AST-reference-total-wrong",
    "changed_before_reseal": [
      "candidate/evidence/ASSET_PROVENANCE.json#/referenced"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_ASSET_REFERENCE_TOTAL",
    "family": "AST",
    "fixture_root_token": "fixture",
    "observed_code": "E_ASSET_REFERENCE_TOTAL",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "2B3FC20D1689BC0BC6CFE1060C7781A02E7D24E0A50DE1AB7EC8B03531C181AC",
    "semantic_before_sha256": "A254A278D9D21535D29E390C15784F79A1CD1349058C6B4C24EDCD2A62B7BB13",
    "semantic_selector": "candidate/evidence/ASSET_PROVENANCE.json#/referenced",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "AST-unreferenced-count-wrong",
    "changed_before_reseal": [
      "candidate/evidence/ASSET_PROVENANCE.json#/unreferenced"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_ASSET_UNREFERENCED_COUNT",
    "family": "AST",
    "fixture_root_token": "fixture",
    "observed_code": "E_ASSET_UNREFERENCED_COUNT",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "40694DDC14E3FFADDD0D548672A023C39CCA74C6D16B616233BC95A097D89B9F",
    "semantic_before_sha256": "A254A278D9D21535D29E390C15784F79A1CD1349058C6B4C24EDCD2A62B7BB13",
    "semantic_selector": "candidate/evidence/ASSET_PROVENANCE.json#/unreferenced",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "AST-reference-count-outside-zero-one",
    "changed_before_reseal": [
      "candidate/evidence/ASSET_PROVENANCE.json#/rows/0/markdown_reference_count"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_ASSET_REFERENCE_COUNT",
    "family": "AST",
    "fixture_root_token": "fixture",
    "observed_code": "E_ASSET_REFERENCE_COUNT",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "270AB3CEB5358501260A2DA9008FDC1EB8320B12536C4503FDF99A97A00590F7",
    "semantic_before_sha256": "A254A278D9D21535D29E390C15784F79A1CD1349058C6B4C24EDCD2A62B7BB13",
    "semantic_selector": "candidate/evidence/ASSET_PROVENANCE.json#/rows/0/markdown_reference_count",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "AST-occurrence-missing",
    "changed_before_reseal": [
      "candidate/evidence/ASSET_PROVENANCE.json#/rows/0/markdown_reference_locations"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_ASSET_OCCURRENCE_SET",
    "family": "AST",
    "fixture_root_token": "fixture",
    "observed_code": "E_ASSET_OCCURRENCE_SET",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "2AEC69BECA41854827B24B8FC0BFC8321A294E7D451D6EC94FF3AB27D1FA7265",
    "semantic_before_sha256": "A254A278D9D21535D29E390C15784F79A1CD1349058C6B4C24EDCD2A62B7BB13",
    "semantic_selector": "candidate/evidence/ASSET_PROVENANCE.json#/rows/0/markdown_reference_locations",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "AST-occurrence-duplicate",
    "changed_before_reseal": [
      "candidate/evidence/ASSET_PROVENANCE.json#/rows/1/markdown_reference_locations"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_ASSET_OCCURRENCE_DUPLICATE",
    "family": "AST",
    "fixture_root_token": "fixture",
    "observed_code": "E_ASSET_OCCURRENCE_DUPLICATE",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "344C7AF6B61ABAE7FDDD673A702CCF105500DC21311DA4691F67856FE6CC999A",
    "semantic_before_sha256": "A254A278D9D21535D29E390C15784F79A1CD1349058C6B4C24EDCD2A62B7BB13",
    "semantic_selector": "candidate/evidence/ASSET_PROVENANCE.json#/rows/1/markdown_reference_locations",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "AST-markdown-path-wrong",
    "changed_before_reseal": [
      "candidate/evidence/ASSET_PROVENANCE.json#/rows/0/markdown_reference_locations/0/markdown_path"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_ASSET_MARKDOWN_PATH",
    "family": "AST",
    "fixture_root_token": "fixture",
    "observed_code": "E_ASSET_MARKDOWN_PATH",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "FB812FD55ED9885D79BBBDD9DED3F1FA526B9C920BB28C0854E394A4CD8B88F3",
    "semantic_before_sha256": "A254A278D9D21535D29E390C15784F79A1CD1349058C6B4C24EDCD2A62B7BB13",
    "semantic_selector": "candidate/evidence/ASSET_PROVENANCE.json#/rows/0/markdown_reference_locations/0/markdown_path",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "AST-target-absent-from-markdown",
    "changed_before_reseal": [
      "candidate/evidence/ASSET_PROVENANCE.json#/rows/0/markdown_reference_locations/0/target"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_ASSET_TARGET_RESOLUTION",
    "family": "AST",
    "fixture_root_token": "fixture",
    "observed_code": "E_ASSET_TARGET_RESOLUTION",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "65F6D4B7A653CE853EA5BFDDFEE2B91A4FBBB7099F7B420DA8FC196D8434579D",
    "semantic_before_sha256": "A254A278D9D21535D29E390C15784F79A1CD1349058C6B4C24EDCD2A62B7BB13",
    "semantic_selector": "candidate/evidence/ASSET_PROVENANCE.json#/rows/0/markdown_reference_locations/0/target",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "AST-ownership-nonnull",
    "changed_before_reseal": [
      "candidate/evidence/ASSET_PROVENANCE.json#/rows/0/ownership"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_ASSET_OWNERSHIP",
    "family": "AST",
    "fixture_root_token": "fixture",
    "observed_code": "E_ASSET_OWNERSHIP",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "CA3983E01EFA1C575731B2E5CFE2C5610ED4A8C60B06F59DF7129974B9818791",
    "semantic_before_sha256": "A254A278D9D21535D29E390C15784F79A1CD1349058C6B4C24EDCD2A62B7BB13",
    "semantic_selector": "candidate/evidence/ASSET_PROVENANCE.json#/rows/0/ownership",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "AST-closure-promoted",
    "changed_before_reseal": [
      "candidate/evidence/ASSET_PROVENANCE.json#/rows/0/closure_state"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_ASSET_CLOSURE",
    "family": "AST",
    "fixture_root_token": "fixture",
    "observed_code": "E_ASSET_CLOSURE",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "02B5C77E8C74C03BDC1FCAB4271F481A91AFE602B2549306F29DDCC37B3D9A8E",
    "semantic_before_sha256": "A254A278D9D21535D29E390C15784F79A1CD1349058C6B4C24EDCD2A62B7BB13",
    "semantic_selector": "candidate/evidence/ASSET_PROVENANCE.json#/rows/0/closure_state",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "AST-finding-wrong",
    "changed_before_reseal": [
      "candidate/evidence/ASSET_PROVENANCE.json#/rows/0/finding"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_ASSET_FINDING",
    "family": "AST",
    "fixture_root_token": "fixture",
    "observed_code": "E_ASSET_FINDING",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "95AFB999370F516EC23711EDD27D8A35531B82C311743DD0AB2F73EA0CD6C8CF",
    "semantic_before_sha256": "A254A278D9D21535D29E390C15784F79A1CD1349058C6B4C24EDCD2A62B7BB13",
    "semantic_selector": "candidate/evidence/ASSET_PROVENANCE.json#/rows/0/finding",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "AST-engine-image-cardinality-wrong",
    "changed_before_reseal": [
      "candidate/evidence/ASSET_PROVENANCE.json#/rows/0/engine_evidence/engine_image_count"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_ASSET_ENGINE_COUNT",
    "family": "AST",
    "fixture_root_token": "fixture",
    "observed_code": "E_ASSET_ENGINE_COUNT",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "425C277DCD48884E546F5087FADF9C6C574285626180B748E109A78F931E1BA6",
    "semantic_before_sha256": "A254A278D9D21535D29E390C15784F79A1CD1349058C6B4C24EDCD2A62B7BB13",
    "semantic_selector": "candidate/evidence/ASSET_PROVENANCE.json#/rows/0/engine_evidence/engine_image_count",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "AST-mime-wrong",
    "changed_before_reseal": [
      "candidate/evidence/ASSET_PROVENANCE.json#/rows/0/mime"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_ASSET_MIME",
    "family": "AST",
    "fixture_root_token": "fixture",
    "observed_code": "E_ASSET_MIME",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "99D3EB954B415DF5B0A1145F7B86B3A847148B167B8864CC203ED03F4DB73C8F",
    "semantic_before_sha256": "A254A278D9D21535D29E390C15784F79A1CD1349058C6B4C24EDCD2A62B7BB13",
    "semantic_selector": "candidate/evidence/ASSET_PROVENANCE.json#/rows/0/mime",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SEM-entity-ordinal-gap",
    "changed_before_reseal": [
      "candidate/evidence/ENTITY_INVENTORY.json#/rows/1/ordinal"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_ENTITY_ORDINALS",
    "family": "SEM",
    "fixture_root_token": "fixture",
    "observed_code": "E_ENTITY_ORDINALS",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "AECA510692FA1662DF00867A92FABE9D5CB4040C56E5C9FCD83DCED482B9291D",
    "semantic_before_sha256": "FDAF4267C7EC1346DF421CE0D32C0AC2F57C92E50BD86C8AC8882DA0DEABF9C5",
    "semantic_selector": "candidate/evidence/ENTITY_INVENTORY.json#/rows/1/ordinal",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SEM-entity-id-duplicate",
    "changed_before_reseal": [
      "candidate/evidence/ENTITY_INVENTORY.json#/rows/1/id"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_ENTITY_ID",
    "family": "SEM",
    "fixture_root_token": "fixture",
    "observed_code": "E_ENTITY_ID",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "65F8D7568BE09C0039F42509502E5DD2FBC868075D56AA1FFFA11700A4C38EE1",
    "semantic_before_sha256": "FDAF4267C7EC1346DF421CE0D32C0AC2F57C92E50BD86C8AC8882DA0DEABF9C5",
    "semantic_selector": "candidate/evidence/ENTITY_INVENTORY.json#/rows/1/id",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SEM-handout-ordinal-gap",
    "changed_before_reseal": [
      "candidate/evidence/HANDOUT_INVENTORY.json#/rows/1/ordinal"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_HANDOUT_ORDINALS",
    "family": "SEM",
    "fixture_root_token": "fixture",
    "observed_code": "E_HANDOUT_ORDINALS",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "A17EAF9C622082D9B605B1BF3C6E315A571F532A7F20D36E40973E9EB5FDE070",
    "semantic_before_sha256": "3BF301D194AC6B027A453AB0627ED5983B19DF82EE2D0499505F93CB360A2E9E",
    "semantic_selector": "candidate/evidence/HANDOUT_INVENTORY.json#/rows/1/ordinal",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SEM-handout-id-duplicate",
    "changed_before_reseal": [
      "candidate/evidence/HANDOUT_INVENTORY.json#/rows/1/id"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_HANDOUT_ID",
    "family": "SEM",
    "fixture_root_token": "fixture",
    "observed_code": "E_HANDOUT_ID",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "5B22C3EDE76DB7257143AACB1E029381254D262AAE1B77BCC481E2B3778C353D",
    "semantic_before_sha256": "3BF301D194AC6B027A453AB0627ED5983B19DF82EE2D0499505F93CB360A2E9E",
    "semantic_selector": "candidate/evidence/HANDOUT_INVENTORY.json#/rows/1/id",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SEM-entity-handout-inequality",
    "changed_before_reseal": [
      "candidate/evidence/ENTITY_INVENTORY.json#/rows/0/disposition"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_ENTITY_HANDOUT_EQUALITY",
    "family": "SEM",
    "fixture_root_token": "fixture",
    "observed_code": "E_ENTITY_HANDOUT_EQUALITY",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "D7B6A534783EAF248B33ED0036CFECC60424CAB1B6E5322BE7515FD64E5FBA2F",
    "semantic_before_sha256": "FDAF4267C7EC1346DF421CE0D32C0AC2F57C92E50BD86C8AC8882DA0DEABF9C5",
    "semantic_selector": "candidate/evidence/ENTITY_INVENTORY.json#/rows/0/disposition",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SEM-required-count-wrong",
    "changed_before_reseal": [
      "candidate/evidence/HANDOUT_INVENTORY.json#/required_count"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_HANDOUT_REQUIRED_COUNT",
    "family": "SEM",
    "fixture_root_token": "fixture",
    "observed_code": "E_HANDOUT_REQUIRED_COUNT",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "9D4054F38415C89DCE69F3D53ADB499C5CAFD75DF586CF6923C8CAA9B9C2D705",
    "semantic_before_sha256": "3BF301D194AC6B027A453AB0627ED5983B19DF82EE2D0499505F93CB360A2E9E",
    "semantic_selector": "candidate/evidence/HANDOUT_INVENTORY.json#/required_count",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SEM-label-wrong",
    "changed_before_reseal": [
      "candidate/evidence/HANDOUT_INVENTORY.json#/rows/0/label"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_HANDOUT_LABEL",
    "family": "SEM",
    "fixture_root_token": "fixture",
    "observed_code": "E_HANDOUT_LABEL",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "3193D9CBE4BBDDBEB25DCCC74E1A513D1F88623D2C0C7505FDC744CAE9AD51C0",
    "semantic_before_sha256": "3BF301D194AC6B027A453AB0627ED5983B19DF82EE2D0499505F93CB360A2E9E",
    "semantic_selector": "candidate/evidence/HANDOUT_INVENTORY.json#/rows/0/label",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SEM-page-range-wrong",
    "changed_before_reseal": [
      "candidate/evidence/HANDOUT_INVENTORY.json#/rows/0/range"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_HANDOUT_PAGE_RANGE",
    "family": "SEM",
    "fixture_root_token": "fixture",
    "observed_code": "E_HANDOUT_PAGE_RANGE",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "622DAF696FF1F23AD6F1B4DE9ADF5A31B13790E6DBA647D9E3D53C332CA392AE",
    "semantic_before_sha256": "3BF301D194AC6B027A453AB0627ED5983B19DF82EE2D0499505F93CB360A2E9E",
    "semantic_selector": "candidate/evidence/HANDOUT_INVENTORY.json#/rows/0/range",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SEM-entity-closure-promoted",
    "changed_before_reseal": [
      "candidate/evidence/ENTITY_INVENTORY.json#/rows/0/review_state"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_ENTITY_CLOSURE",
    "family": "SEM",
    "fixture_root_token": "fixture",
    "observed_code": "E_ENTITY_CLOSURE",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "E5ABE5BDAFE9D6F2905A2DF257139159227724E73EE5F72BF58BE8F9400CAD39",
    "semantic_before_sha256": "FDAF4267C7EC1346DF421CE0D32C0AC2F57C92E50BD86C8AC8882DA0DEABF9C5",
    "semantic_selector": "candidate/evidence/ENTITY_INVENTORY.json#/rows/0/review_state",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SEM-mode-page-gap",
    "changed_before_reseal": [
      "candidate/evidence/CONTENT_MODE_REVIEW.json#/rows/4"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_MODE_PAGE_SET",
    "family": "SEM",
    "fixture_root_token": "fixture",
    "observed_code": "E_MODE_PAGE_SET",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "C9B8E4BD56A0A41B349B9588273ED79879FEA477838AD5FB0689AC04702A720A",
    "semantic_before_sha256": "F79948D9403AAB66F3F058122E6C14E31AC919E9C4D54AC71E722B650BC2BDC7",
    "semantic_selector": "candidate/evidence/CONTENT_MODE_REVIEW.json#/rows/4",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SEM-mode-row-duplicate",
    "changed_before_reseal": [
      "candidate/evidence/CONTENT_MODE_REVIEW.json#/rows/1/page"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_MODE_DUPLICATE",
    "family": "SEM",
    "fixture_root_token": "fixture",
    "observed_code": "E_MODE_DUPLICATE",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "A93CCF674647E8ABAA3905A6DACABFCA755CD5A6DC5D11881DF75DA1D6DB0958",
    "semantic_before_sha256": "F79948D9403AAB66F3F058122E6C14E31AC919E9C4D54AC71E722B650BC2BDC7",
    "semantic_selector": "candidate/evidence/CONTENT_MODE_REVIEW.json#/rows/1/page",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SEM-mode-review-promoted",
    "changed_before_reseal": [
      "candidate/evidence/CONTENT_MODE_REVIEW.json#/rows/0/review_state"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_MODE_REVIEW_STATE",
    "family": "SEM",
    "fixture_root_token": "fixture",
    "observed_code": "E_MODE_REVIEW_STATE",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "38714DFAB3D0BC4441C5FC518599F96671D049D73757DE70A82A238104004E4D",
    "semantic_before_sha256": "F79948D9403AAB66F3F058122E6C14E31AC919E9C4D54AC71E722B650BC2BDC7",
    "semantic_selector": "candidate/evidence/CONTENT_MODE_REVIEW.json#/rows/0/review_state",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SEM-reference-only-row-added",
    "changed_before_reseal": [
      "candidate/evidence/REFERENCE_ONLY_AUDIT.json#/rows/0"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_REFERENCE_ONLY_ROWS",
    "family": "SEM",
    "fixture_root_token": "fixture",
    "observed_code": "E_REFERENCE_ONLY_ROWS",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "56A16D653FBB7B94CA76EA79A73EF455032360383BF54DFD214250A6A0255F8B",
    "semantic_before_sha256": "43D7D5E56C1CF1010822FC667E333D5123E9329885692FA6C65EF3DA3A4E86E4",
    "semantic_selector": "candidate/evidence/REFERENCE_ONLY_AUDIT.json#/rows/0",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SEM-historical-material-true",
    "changed_before_reseal": [
      "candidate/evidence/REFERENCE_ONLY_AUDIT.json#/historical_material_opened"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_REFERENCE_ONLY_HISTORY",
    "family": "SEM",
    "fixture_root_token": "fixture",
    "observed_code": "E_REFERENCE_ONLY_HISTORY",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "A7BBE1C4BA7ACF8258325A8C2CEE1B49F26387B5FFB23B2C0C6D8ABC24429F13",
    "semantic_before_sha256": "43D7D5E56C1CF1010822FC667E333D5123E9329885692FA6C65EF3DA3A4E86E4",
    "semantic_selector": "candidate/evidence/REFERENCE_ONLY_AUDIT.json#/historical_material_opened",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SEM-map-role-count-wrong",
    "changed_before_reseal": [
      "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/39/semantic_role"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_ROLE_MAP_COUNT",
    "family": "SEM",
    "fixture_root_token": "fixture",
    "observed_code": "E_ROLE_MAP_COUNT",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "F4771BA7089C1D4694D0E7EAB8AD58E806341A13DE66E657AF73C17EE7D028AA",
    "semantic_before_sha256": "65CECA80B15F2917C8FA968ABA6103BD7C52DBB65C9C1751C1105D4866E73D39",
    "semantic_selector": "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/39/semantic_role",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SEM-pregen-role-count-wrong",
    "changed_before_reseal": [
      "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/46/semantic_role"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_ROLE_PREGEN_COUNT",
    "family": "SEM",
    "fixture_root_token": "fixture",
    "observed_code": "E_ROLE_PREGEN_COUNT",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "EB06C06B7AFF37264F69354A3861062774812CE847953F485B28E61015218BBD",
    "semantic_before_sha256": "65CECA80B15F2917C8FA968ABA6103BD7C52DBB65C9C1751C1105D4866E73D39",
    "semantic_selector": "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/46/semantic_role",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SEM-back-cover-role-count-wrong",
    "changed_before_reseal": [
      "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/59/semantic_role"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_ROLE_BACK_COVER_COUNT",
    "family": "SEM",
    "fixture_root_token": "fixture",
    "observed_code": "E_ROLE_BACK_COVER_COUNT",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "D905CD13C59A9AF16488CEDAD3E4CAEE9091874CBB7B3975F3A53978A0F66F96",
    "semantic_before_sha256": "65CECA80B15F2917C8FA968ABA6103BD7C52DBB65C9C1751C1105D4866E73D39",
    "semantic_selector": "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/59/semantic_role",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "SEM-handout-role-count-wrong",
    "changed_before_reseal": [
      "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/0/semantic_role"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_ROLE_HANDOUT_COUNT",
    "family": "SEM",
    "fixture_root_token": "fixture",
    "observed_code": "E_ROLE_HANDOUT_COUNT",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "DC8ABB0A4D46C542AE2E81D49DCF53C830541536EB18DBB1B9F616BF810C225C",
    "semantic_before_sha256": "65CECA80B15F2917C8FA968ABA6103BD7C52DBB65C9C1751C1105D4866E73D39",
    "semantic_selector": "candidate/evidence/NAVIGATION_INVENTORY.json#/rows/0/semantic_role",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-action-missing",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/actions/2"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_ACTIONS",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_ACTIONS",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "A1CEF51B9A126D7DB79FA4A0D7E3564730B4C5496F7C50FF3BB6CAC43D73507B",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/actions/2",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-action-duplicate",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/actions/-"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_ACTIONS",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_ACTIONS",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "983682DF2BA713B8F2FEA14A6AAE649A3D142B3F9BA0CA81FBC00042732C538C",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/actions/-",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-action-extra",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/actions/-"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_ACTIONS",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_ACTIONS",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "B0467A8C09E86B1E24D584FFEFFA9403137FB900B8CA92507BB59B31E2DF1176",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/actions/-",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-action-reordered",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/actions/0"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_ACTIONS",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_ACTIONS",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "213E9824885868B6EC03E46848FE10250A00F2F1240F2FC2C6572B231C9E78C2",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/actions/0",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-state-promoted",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/state"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_STATE",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_STATE",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "CC06F81D54B3747948160B386EF43248314F56A4F426DAE7B7EF71E2D9A649BD",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/state",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-external-locator-used",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/external_locator"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_EXTERNAL_SOURCE",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_EXTERNAL_SOURCE",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "CC7EFD2BA239AA105181E37AFEFF48BDF7939D7E5DFBF97F9067C72F67BBEF78",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/external_locator",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-flag-build_invoked-missing",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/flags/build_invoked"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_FLAG_BUILD_INVOKED",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_FLAG_BUILD_INVOKED",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "D5EC3AF672BC96DA2DF88E9D46F701870267BC1078BFDDDF9F296A522F4EAA62",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/flags/build_invoked",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-flag-build_invoked-true",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/flags/build_invoked"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_FLAG_BUILD_INVOKED",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_FLAG_BUILD_INVOKED",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "488192EC7C141867C343FB5E92F9E91350110084EAFFC9D58680AAB24E1366DA",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/flags/build_invoked",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-flag-mineru_invoked-missing",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/flags/mineru_invoked"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_FLAG_MINERU_INVOKED",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_FLAG_MINERU_INVOKED",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "F43422BC15CE3C4AD06C3BA2412538FCEB4ED4963A180AC8A75B8D6061366E89",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/flags/mineru_invoked",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-flag-mineru_invoked-true",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/flags/mineru_invoked"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_FLAG_MINERU_INVOKED",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_FLAG_MINERU_INVOKED",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "1F9F233A49FC5AF5BE15D4AE0DA2D2B9D98658F8482AF903D3D4C90F49FB8CDC",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/flags/mineru_invoked",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-flag-ocr_invoked-missing",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/flags/ocr_invoked"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_FLAG_OCR_INVOKED",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_FLAG_OCR_INVOKED",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "33EF395054239D4EB0D4C3B4C698E8222F2B73B2FD85AEA65EF1B61A317AC03C",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/flags/ocr_invoked",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-flag-ocr_invoked-true",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/flags/ocr_invoked"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_FLAG_OCR_INVOKED",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_FLAG_OCR_INVOKED",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "8221198BF79A858FE0A24A6917CA7A6A5E0E4AF656B88484B48F3D84975B7258",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/flags/ocr_invoked",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-flag-gpu_or_model_invoked-missing",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/flags/gpu_or_model_invoked"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_FLAG_GPU_OR_MODEL_INVOKED",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_FLAG_GPU_OR_MODEL_INVOKED",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "7CC85CD34D4C98CA7E5A4FC10AA747FDB4640285AB7C5B3B7B41BB31F1C04E2E",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/flags/gpu_or_model_invoked",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-flag-gpu_or_model_invoked-true",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/flags/gpu_or_model_invoked"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_FLAG_GPU_OR_MODEL_INVOKED",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_FLAG_GPU_OR_MODEL_INVOKED",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "A35180CD0CF7740F4626D09B37B0FF5EC5CF6742AAAB0BFCF40844C47C452A6D",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/flags/gpu_or_model_invoked",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-flag-network_invoked-missing",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/flags/network_invoked"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_FLAG_NETWORK_INVOKED",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_FLAG_NETWORK_INVOKED",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "4BE2FA877BE1D913FE46F737249F781364BAC02C707EE07F1A2E01E6E00FC21B",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/flags/network_invoked",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-flag-network_invoked-true",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/flags/network_invoked"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_FLAG_NETWORK_INVOKED",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_FLAG_NETWORK_INVOKED",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "5B83F9F9AFF47B403F8B7D96DA6A90F7C8C356076C945FACD95507B7F36BD1F9",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/flags/network_invoked",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-flag-external_source_used-missing",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/flags/external_source_used"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_FLAG_EXTERNAL_SOURCE_USED",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_FLAG_EXTERNAL_SOURCE_USED",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "84898953911F7146EFEBBB3B701A4736CDBE79096C66A1C1D368C8801BB03A0E",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/flags/external_source_used",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-flag-external_source_used-true",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/flags/external_source_used"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_FLAG_EXTERNAL_SOURCE_USED",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_FLAG_EXTERNAL_SOURCE_USED",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "493B71DF1F5217F1FBEEAA141E5C0492DFBCB112E06FB6A964636D29E6C87B36",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/flags/external_source_used",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-argument-source_flag-missing",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/records/0/source_flag"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_ARGUMENT_SOURCE_FLAG",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_ARGUMENT_SOURCE_FLAG",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "3A9AAF04C90B2048D52D89246D34EEDA6D05135E280F4501792F588B1540BF30",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/records/0/source_flag",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-argument-source_flag-wrong",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/records/0/source_flag"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_ARGUMENT_SOURCE_FLAG",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_ARGUMENT_SOURCE_FLAG",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "8FD614354DA115FA4AB11BD09AA16607ABFA916573D3A44C2CDE57CF4A0BB4CC",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/records/0/source_flag",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-argument-run_root_flag-missing",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/records/0/run_root_flag"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_ARGUMENT_RUN_ROOT_FLAG",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_ARGUMENT_RUN_ROOT_FLAG",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "19E71BB382FFD20D05F57BBE0D37E547344A29FE0256C27552AE82AC0BC5C99B",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/records/0/run_root_flag",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-argument-run_root_flag-wrong",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/records/0/run_root_flag"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_ARGUMENT_RUN_ROOT_FLAG",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_ARGUMENT_RUN_ROOT_FLAG",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "70C4537EF9F6B27FAA0264C3A348AED40EAC201813E3DBAE5839B70B5CC291C4",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/records/0/run_root_flag",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-argument-source_relative_path-missing",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/records/0/source_relative_path"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_ARGUMENT_SOURCE_RELATIVE_PATH",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_ARGUMENT_SOURCE_RELATIVE_PATH",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "7DE987097CD5AE1355398E5FD89EE339A96565DE25FBF9EEF8BEC0E5B8AFCFF2",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/records/0/source_relative_path",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-argument-source_relative_path-wrong",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/records/0/source_relative_path"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_ARGUMENT_SOURCE_RELATIVE_PATH",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_ARGUMENT_SOURCE_RELATIVE_PATH",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "D832C16DB07A4CCB3E01D56662493382920657F2BB04F942AE6E740F279664BC",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/records/0/source_relative_path",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-count-pages-missing",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/counts/pages"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_COUNTS_PAGES",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_COUNTS_PAGES",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "8A5E3614492A6B66EE92FC5AA489FDF8435E32D5F38B58E22DB630E473C01FC2",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/counts/pages",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-count-pages-wrong",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/counts/pages"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_COUNTS_PAGES",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_COUNTS_PAGES",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "9704137F1A03D24C4FB6A0A056E02420172D999D1DBDFC9AFEDB673DFA5D3798",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/counts/pages",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-count-renders-missing",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/counts/renders"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_COUNTS_RENDERS",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_COUNTS_RENDERS",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "B04E37BFC291A06D9AF66426148B3A397877D5622C77D693DBE493190FA50B30",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/counts/renders",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-count-renders-wrong",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/counts/renders"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_COUNTS_RENDERS",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_COUNTS_RENDERS",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "FD50E57C6A4B66560793387AE3E50A3A094512C2CEFF9D536CBF22A501330710",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/counts/renders",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-count-contact_sheets-missing",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/counts/contact_sheets"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_COUNTS_CONTACT_SHEETS",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_COUNTS_CONTACT_SHEETS",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "F3C1739D2813AD9359D51F4B6B5E0974413CB23C58CD177A06EBC28BE600FF32",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/counts/contact_sheets",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-count-contact_sheets-wrong",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/counts/contact_sheets"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_COUNTS_CONTACT_SHEETS",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_COUNTS_CONTACT_SHEETS",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "FF642A81CB33567D5E767FE1DFAED3C512E3A3304DFFE9DB468DBE902CB5958F",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/counts/contact_sheets",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-count-handouts-missing",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/counts/handouts"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_COUNTS_HANDOUTS",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_COUNTS_HANDOUTS",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "01DE4668924F960FE1965DF6D5C18AD174277FE38DE460086BF3F825B423EA11",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/counts/handouts",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-count-handouts-wrong",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/counts/handouts"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_COUNTS_HANDOUTS",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_COUNTS_HANDOUTS",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "A6EBD5F959FAD64414263A4CD056F0507F6A558372B1FEDC5F9F1834FCBD82F0",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/counts/handouts",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-count-maps-missing",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/counts/maps"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_COUNTS_MAPS",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_COUNTS_MAPS",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "7C4636FF4FA61CB1A8266343B196CDD611621992D39A4225E790C84F0329F93C",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/counts/maps",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-count-maps-wrong",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/counts/maps"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_COUNTS_MAPS",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_COUNTS_MAPS",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "4A615327DE29453C942223466C57145DFFF8CB83D5CC83A2F327F48E50DDAEE2",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/counts/maps",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-count-pregens-missing",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/counts/pregens"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_COUNTS_PREGENS",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_COUNTS_PREGENS",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "D70EE1947075979D24287997DA9982A8E721A3D6E4FAE6F42DEE1BC84F36E0CA",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/counts/pregens",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-count-pregens-wrong",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/counts/pregens"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_COUNTS_PREGENS",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_COUNTS_PREGENS",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "B24B03C507ACF0917DE59BF54F047C8140C3615414ECC7F6F049E633AB6327EF",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/counts/pregens",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-count-back_cover-missing",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/counts/back_cover"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_COUNTS_BACK_COVER",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_COUNTS_BACK_COVER",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "B159F35A61B03ED5D5546A7956C91871EC23CD8EC97D5D1857190CA724295FA6",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/counts/back_cover",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-count-back_cover-wrong",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/counts/back_cover"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_COUNTS_BACK_COVER",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_COUNTS_BACK_COVER",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "996DAB115D4095FAEDBB5A425DC9DFB487D331F3990DECE57DD7B92D341A9CE3",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/counts/back_cover",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-count-assets-missing",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/counts/assets"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_COUNTS_ASSETS",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_COUNTS_ASSETS",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "06183463FAE624EB8972FD0CCEBF21D250E6E37A24BDE21D4896F4EC81A66248",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/counts/assets",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-count-assets-wrong",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/counts/assets"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_COUNTS_ASSETS",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_COUNTS_ASSETS",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "98A8FB62731A70A7AC5FFE3D4A6DBAD3E146CD417943051E1BC42DFF99AB42F1",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/counts/assets",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-count-referenced_assets-missing",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/counts/referenced_assets"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_COUNTS_REFERENCED_ASSETS",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_COUNTS_REFERENCED_ASSETS",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "69A84C2CF02827ECC42BCFC7AD4C00FE81B5B5D96CCEE4913EFF27BC16A65FF1",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/counts/referenced_assets",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-count-referenced_assets-wrong",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/counts/referenced_assets"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_COUNTS_REFERENCED_ASSETS",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_COUNTS_REFERENCED_ASSETS",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "79269BEB5309D700B86B409D29DB95FB4891C94B683C01A3B41B41FEE6DBA40D",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/counts/referenced_assets",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-count-unreferenced_assets-missing",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/counts/unreferenced_assets"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_COUNTS_UNREFERENCED_ASSETS",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_COUNTS_UNREFERENCED_ASSETS",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "66CC0AF74636D50AAA8DCEDD0461C63F504F98D7CD6D6092C6A89123272C85D8",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/counts/unreferenced_assets",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-count-unreferenced_assets-wrong",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/counts/unreferenced_assets"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_COUNTS_UNREFERENCED_ASSETS",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_COUNTS_UNREFERENCED_ASSETS",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "E652CAB339CEA99DD2260B9B463946A5E37CFA74C605BF0C4EC97E2C96CC68E9",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/counts/unreferenced_assets",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-count-markdown_references-missing",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/counts/markdown_references"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_COUNTS_MARKDOWN_REFERENCES",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_COUNTS_MARKDOWN_REFERENCES",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "33BC55CC38B2D90C1176129F4C83CC9A7881E9D0745C2CADF6C811BC237BD7DD",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/counts/markdown_references",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-count-markdown_references-wrong",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/counts/markdown_references"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_COUNTS_MARKDOWN_REFERENCES",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_COUNTS_MARKDOWN_REFERENCES",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "43FBAB78B17019D1DBC6FA56F1F714B82CD304B03A07012AEF4957FC4114BDCD",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/counts/markdown_references",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-sheet-count-wrong",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/sheets"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_SHEET_COUNT",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_SHEET_COUNT",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "10F98D28EEF4B0091CB4267A1B34EA26E678DDBAF720287FF7BEE7F1F22672E4",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/sheets",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-sheet-coverage-wrong",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/sheets/0/pages/-"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_SHEET_COVERAGE",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_SHEET_COVERAGE",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "82509DA85977969174F55F46698F27F031CC62E470A5DD7B683B844688F24483",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/sheets/0/pages/-",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-sheet-missing",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/sheets/30"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_SHEET_SET",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_SHEET_SET",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "B77D1824C23CACC929BC85F9CEBC2CA5004E6D0A2288B2272C4DD3C5B587E4FF",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/sheets/30",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-sheet-duplicate",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/sheets/1"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_SHEET_SET",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_SHEET_SET",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "325679C9DADA9ED65193058E91BA1B204E44139449A8CF1FFB47A87522EFB779",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/sheets/1",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-sheet-id-wrong",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/sheets/0/sheet_id"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_SHEET_ID",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_SHEET_ID",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "B07CECC0167F222821B59AB29B97AA1DF2126932E726B02AB2F5060868FC1E14",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/sheets/0/sheet_id",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-sheet-path-sequence-wrong",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/sheets/0/path"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_SHEET_PATH",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_SHEET_PATH",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "574958AA706DD14D1A59F9446332F9AC7688808E9FF0994AC03263D4CA7A334D",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/sheets/0/path",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-sheet-grid-wrong",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/sheets/0/grid"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_SHEET_GRID",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_SHEET_GRID",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "D37EEAE019608D6AFA5A2071195A464F7B74BA4CA1FE28B717EEB447DBBCAC69",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/sheets/0/grid",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-sheet-hash-wrong",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/sheets/0/sha256"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_SHEET_HASH",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_SHEET_HASH",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "E6E50EA735503D146A87CB80D09CDC05866475F7B3B4687915D7F646AED734AC",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/sheets/0/sha256",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-flattened-page-missing",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/sheets/0/pages/0"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_SHEET_PAGES",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_SHEET_PAGES",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "A4A44DF13F13F87C5DD3BBB71BDF66D41B6EB50DCB4CDE32570A23EA8E570707",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/sheets/0/pages/0",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-flattened-page-duplicate",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/sheets/1/pages/0"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_SHEET_PAGES",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_SHEET_PAGES",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "CF5E9023DBB770C304F0F15EF909B2689773C2BF4FD9CE0C352AF9E31326A324",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/sheets/1/pages/0",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-flattened-page-order-wrong",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/sheets/0/pages"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_SHEET_PAGE_ORDER",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_SHEET_PAGE_ORDER",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "06663C53E2B95850A05BCB904D750D378F38022B22DF27AEBF661FE4F0F0DAE7",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/sheets/0/pages",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-render-path-wrong",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/sheets/0/page_renders/0/path"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_RENDER_PATH",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_RENDER_PATH",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "326B96E5AFDA23DB48EDA86D69D03D6F7419DC4A1F1AA52EEB68704D9FB16E5A",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/sheets/0/page_renders/0/path",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-render-hash-wrong",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/sheets/0/page_renders/0/sha256"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_RENDER_HASH",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_RENDER_HASH",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "A597261B5016316642EE3157526C66CB5296DD2075FB0BAD563F64222EB192F7",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/sheets/0/page_renders/0/sha256",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-page-render-mapping-disagrees",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/page_renders/0/page_number"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_PAGE_RENDER_MAP",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_PAGE_RENDER_MAP",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "DD4C27CE676D6B4886741299C2F834D868A3C1C67B1B17C496998F46338A5D6F",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/page_renders/0/page_number",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "CMD-verify-determinism-false",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/verify_deterministic"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_DETERMINISM",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_DETERMINISM",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "CF4FB486EC50DC831747EF33F85C8DD2172507D9F3A714FC640643601BE6E7FC",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/verify_deterministic",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-top-asset_count-missing",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/asset_count"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SHAPE_QA",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_SHAPE_QA",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "55EC79230938B872552A82308E70D3116920EE5532F82EF5AFA1A1818282D585",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/asset_count",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-top-block_count-missing",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/block_count"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SHAPE_QA",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_SHAPE_QA",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "287C548FD312CF0112FDEBA3951414F9866C428AB8E25645621399E24FCDEF26",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/block_count",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-top-contact_sheet_count-missing",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/contact_sheet_count"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SHAPE_QA",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_SHAPE_QA",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "6D51ED52A4C922822B477C693B0B2E3FBB384173BF71829DFCAAF0A1CC8AB267",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/contact_sheet_count",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-top-contract_sha256-missing",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/contract_sha256"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SHAPE_QA",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_SHAPE_QA",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "C7E38C38AF259ABAF2CB5F2B90713729055B08DED5E3518E2335C6748AF27092",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/contract_sha256",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-top-counts-missing",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/counts"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SHAPE_QA",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_SHAPE_QA",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "F792D1C0BE675285EFCE8110A42E5B5860CEE7EFD8BA80D95A42CC0E7CF9D1D9",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/counts",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-top-gate_results-missing",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/gate_results"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SHAPE_QA",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_SHAPE_QA",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "BEDB7AF040451FA53E1DA3D661BD93C53C5A0B45D2C79EECDFA64589BB4C173B",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/gate_results",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-top-handout_count-missing",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/handout_count"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SHAPE_QA",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_SHAPE_QA",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "47219F9028DC47A41793E9DFCBF629AFF0B42EF93AB0F5DD2495F98CE38D7C16",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/handout_count",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-top-historical_material_opened-missing",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/historical_material_opened"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SHAPE_QA",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_SHAPE_QA",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "52D5B395168BAE89D4FC94043BF2F5D7868FE6B556C34763F532B0FBDDF2380B",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/historical_material_opened",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-top-main_scripts_invoked-missing",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/main_scripts_invoked"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SHAPE_QA",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_SHAPE_QA",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "2E01AB3CAB8D3F4F5D51F148FA5A5713BC891B3DAEDE25E5F4681F7A3E425880",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/main_scripts_invoked",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-top-navigation_anchor_count-missing",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/navigation_anchor_count"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SHAPE_QA",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_SHAPE_QA",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "E4D27F2E7687B33D98C71A74661E430B50675C7A51B944491D5A0EA2C7D3813D",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/navigation_anchor_count",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-top-open_blocker_count-missing",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/open_blocker_count"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SHAPE_QA",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_SHAPE_QA",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "47971FE6524A337FBEA125A376184E2E70D0245357B3870B75664C6529C13A33",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/open_blocker_count",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-top-output_inventory-missing",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SHAPE_QA",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_SHAPE_QA",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "DA82B16452EFC80EABD7B32703CA8E2A0FE406B2134997506E963C5A5BDB4D24",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-top-output_inventory_count-missing",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_count"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SHAPE_QA",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_SHAPE_QA",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "1295E4A96C7F1D070DF44BAC71FBD5B6793E1F9A9B0EBA577BB4718AB818CD3D",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_count",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-top-output_inventory_rule-missing",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_rule"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SHAPE_QA",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_SHAPE_QA",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "169A47F85FF98287054F74D885C7F3115C7DB7655229A6DA9F530641FB051EB6",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_rule",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-top-output_inventory_sha256-missing",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SHAPE_QA",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_SHAPE_QA",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "B8376709024ABFECD84E991CCC8BF526B83A330557CBD0620E57976273B5527A",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-top-page_count-missing",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/page_count"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SHAPE_QA",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_SHAPE_QA",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "4E4FCE095AC45AD9D8ED7063C03A6C7D2FF5C61077E03CFD01BFFC9D85745670",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/page_count",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-top-recovery_evidence_sha256-missing",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/recovery_evidence_sha256"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SHAPE_QA",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_SHAPE_QA",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "1A8BB26534B1FF3A90CC4E060F3EC9F696364F9457C0E57B9EA6F631EBBFAF24",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/recovery_evidence_sha256",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-top-recovery_manifest_sha256-missing",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/recovery_manifest_sha256"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SHAPE_QA",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_SHAPE_QA",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "81482A26BB1B4EB20B097AE4152B54094AE6106BBC2F085F03CE87B8DCFFA2BF",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/recovery_manifest_sha256",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-top-referenced_asset_count-missing",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/referenced_asset_count"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SHAPE_QA",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_SHAPE_QA",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "489B5B16869B5A472C8D47B03F108E6EFECB9E2E5D57DF460A16CB70C764B816",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/referenced_asset_count",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-top-schema-missing",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/schema"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SHAPE_QA",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_SHAPE_QA",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "27DE6380F9B4C4E3791DC65B191FB7E818D7C5A96ED133B5C014F5583B824CC5",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/schema",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-top-source_sha256-missing",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/source_sha256"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SHAPE_QA",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_SHAPE_QA",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "D9F2965E741BF2CD679F46FDADD43A7A4E8CC1AEE90E97567BA8C4F082DE571D",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/source_sha256",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-top-state-missing",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/state"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SHAPE_QA",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_SHAPE_QA",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "8D8D73F4CDE1E96CCAC6138877F8B6B5B267C2D277527B3BF8C2C93A1CA080E7",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/state",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-top-unreferenced_asset_count-missing",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/unreferenced_asset_count"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SHAPE_QA",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_SHAPE_QA",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "31E3EE647FC189A52A660A62848E79621FF04F99479953AB685D58A095F24CB5",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/unreferenced_asset_count",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-top-extra",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/unexpected"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SHAPE_QA",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_SHAPE_QA",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "7FD28E829FB2164A9E1D6B4E4631F8B64213C1961DBD7EE5BB7AE9D1ABBABC10",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/unexpected",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-state-promoted",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/state"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_STATE",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_STATE",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "C215BC4407884F7BE9DE1800F05E2D2B0EAFEE749E25970E3BA894CD9E66BA8F",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/state",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-authority-contract",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/contract_sha256"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_CONTRACT_HASH",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_CONTRACT_HASH",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "EEBE9C61C7C3CF632CF37343B3917B2E12FF006FDFD50D563C2BEA0A545C1615",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/contract_sha256",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-authority-source",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/source_sha256"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_SOURCE_HASH",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_SOURCE_HASH",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "972594B9FF467A680905CB0D1CC13422CF32C9F0B950BA31967AFAE273267C8B",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/source_sha256",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-authority-recovery-manifest",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/recovery_manifest_sha256"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_RECOVERY_MANIFEST_HASH",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_RECOVERY_MANIFEST_HASH",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "DF4D723B94F745D118616AEDCE1EB05ACB39B6715B38B75D304C5BE95DB39642",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/recovery_manifest_sha256",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-authority-recovery-evidence",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/recovery_evidence_sha256"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_RECOVERY_EVIDENCE_HASH",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_RECOVERY_EVIDENCE_HASH",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "BDF91D7F01DB14428F86387BDB8EFBFB0FA0A2461BFA5815A82E49ADB27822B0",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/recovery_evidence_sha256",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-scalar-page_count-wrong",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/page_count"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_SCALAR_PAGE_COUNT",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_SCALAR_PAGE_COUNT",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "BD87376C3AE4402446AFAC4D821E562AEA2AC219B29D74279DEC1421C256C90F",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/page_count",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-scalar-handout_count-wrong",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/handout_count"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_SCALAR_HANDOUT_COUNT",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_SCALAR_HANDOUT_COUNT",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "3FC75805D2B47DEBE7B15B80A0E785467C7CD1FBC0130AAC85658445C0C9B5AB",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/handout_count",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-scalar-block_count-wrong",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/block_count"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_SCALAR_BLOCK_COUNT",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_SCALAR_BLOCK_COUNT",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "A586685F6D0691B93566D3845E116A1719A9354EBC35F20EC734E203F369EFD2",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/block_count",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-scalar-asset_count-wrong",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/asset_count"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_SCALAR_ASSET_COUNT",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_SCALAR_ASSET_COUNT",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "F57624FCCFF8F2A8A98127CAD414277A5673F141B8B8F0A6AF220750E52D5C97",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/asset_count",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-scalar-contact_sheet_count-wrong",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/contact_sheet_count"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_SCALAR_CONTACT_SHEET_COUNT",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_SCALAR_CONTACT_SHEET_COUNT",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "DC37A731310CCD97881EFDD78B7119052BC85DCE9837CBF0EB7589A4408F991D",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/contact_sheet_count",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-scalar-navigation_anchor_count-wrong",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/navigation_anchor_count"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_SCALAR_NAVIGATION_ANCHOR_COUNT",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_SCALAR_NAVIGATION_ANCHOR_COUNT",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "83BA71EDD0461EA490E9796A3D5645DF8B2F3C7556DF3C1AC6994D15DDF2C685",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/navigation_anchor_count",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-scalar-referenced_asset_count-wrong",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/referenced_asset_count"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_SCALAR_REFERENCED_ASSET_COUNT",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_SCALAR_REFERENCED_ASSET_COUNT",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "92F63826A0C6945FF5BF4143FA55D225EC904CA199CBED4FD1810A3BD7B6563A",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/referenced_asset_count",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-scalar-unreferenced_asset_count-wrong",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/unreferenced_asset_count"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_SCALAR_UNREFERENCED_ASSET_COUNT",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_SCALAR_UNREFERENCED_ASSET_COUNT",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "00D943BD7FC7323C145021DD3F01357716B5823FDEB97D82A860B8A93EA5047A",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/unreferenced_asset_count",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-scalar-open_blocker_count-wrong",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/open_blocker_count"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_SCALAR_OPEN_BLOCKER_COUNT",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_SCALAR_OPEN_BLOCKER_COUNT",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "4922F3FC8BA14F6F98431B95CFD5009E0726F3E901CE51E958F86138BCB5928D",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/open_blocker_count",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-counts-assets-missing",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/counts/assets"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_COUNTS_ASSETS",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_COUNTS_ASSETS",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "1B52505E36B04454982B741B2F0EB96BEC11DE35D0F3A911B56566DCB6810522",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/counts/assets",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-counts-assets-wrong",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/counts/assets"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_COUNTS_ASSETS",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_COUNTS_ASSETS",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "CF97F04ADD2E74DCE118674481027C10A7645F4CA34E40F4639465C7DB5AFA77",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/counts/assets",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-counts-back_cover-missing",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/counts/back_cover"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_COUNTS_BACK_COVER",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_COUNTS_BACK_COVER",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "19B1E4A1CF24A1C47E61DC458DE2121752B87978E4FFB541FCDE24383015CADA",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/counts/back_cover",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-counts-back_cover-wrong",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/counts/back_cover"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_COUNTS_BACK_COVER",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_COUNTS_BACK_COVER",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "F79CCA34F89680417D18272590D07035A1972E79DEC76010889BF95867C3060C",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/counts/back_cover",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-counts-contact_sheets-missing",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/counts/contact_sheets"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_COUNTS_CONTACT_SHEETS",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_COUNTS_CONTACT_SHEETS",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "634E3A2428903B1F5E1EA8E0868C776F983FE7AFDFC6B85BBB7D6063D7AFD9E3",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/counts/contact_sheets",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-counts-contact_sheets-wrong",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/counts/contact_sheets"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_COUNTS_CONTACT_SHEETS",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_COUNTS_CONTACT_SHEETS",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "75A35582AB64564AFDD4788AFF5548D8D252C17B0B4B2D203BD1EF75967D370F",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/counts/contact_sheets",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-counts-engine_images-missing",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/counts/engine_images"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_COUNTS_ENGINE_IMAGES",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_COUNTS_ENGINE_IMAGES",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "BEAD64F4D153B780FFBDA1D294DDB9470AFD24D42E9F8883F0EDF3F35DD8D24E",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/counts/engine_images",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-counts-engine_images-wrong",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/counts/engine_images"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_COUNTS_ENGINE_IMAGES",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_COUNTS_ENGINE_IMAGES",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "5292D61732B69BFEC630CB252F87B4B11CCF9B9CDF75852AE25A6FD9F6060E5E",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/counts/engine_images",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-counts-engine_payload-missing",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/counts/engine_payload"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_COUNTS_ENGINE_PAYLOAD",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_COUNTS_ENGINE_PAYLOAD",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "D8D92548F8259A4D0E3E568C43F1B4B535B871B8EB05F10AC90B03CD3A21D80B",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/counts/engine_payload",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-counts-engine_payload-wrong",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/counts/engine_payload"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_COUNTS_ENGINE_PAYLOAD",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_COUNTS_ENGINE_PAYLOAD",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "232E3B4285C3672028619CEDBF4576605423C739F75991DB15C6EE2842115511",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/counts/engine_payload",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-counts-handouts-missing",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/counts/handouts"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_COUNTS_HANDOUTS",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_COUNTS_HANDOUTS",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "781A88EBB5C981E1EDB7257DFF47405EBFE0F9BC2CEF73DB4237B620C1EA08CC",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/counts/handouts",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-counts-handouts-wrong",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/counts/handouts"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_COUNTS_HANDOUTS",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_COUNTS_HANDOUTS",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "0B9720F9765237FDAF52796863DA02CB555BE2EE29F22F744FFC6F0003660DC6",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/counts/handouts",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-counts-maps-missing",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/counts/maps"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_COUNTS_MAPS",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_COUNTS_MAPS",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "A1F5FEC050DBBA34930645DC999E7855B8F4D6674DB268D284E5EC9EEA4BA015",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/counts/maps",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-counts-maps-wrong",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/counts/maps"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_COUNTS_MAPS",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_COUNTS_MAPS",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "EDEE1F9277535513943240694C7E94B3D96D55DCB6054C90467B01205550B855",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/counts/maps",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-counts-navigation_anchors-missing",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/counts/navigation_anchors"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_COUNTS_NAVIGATION_ANCHORS",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_COUNTS_NAVIGATION_ANCHORS",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "85CFC107CAA88D754B3A90C648B9F35ED763589094E910CFA0785F6F6B5387DF",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/counts/navigation_anchors",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-counts-navigation_anchors-wrong",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/counts/navigation_anchors"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_COUNTS_NAVIGATION_ANCHORS",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_COUNTS_NAVIGATION_ANCHORS",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "992A16FC58370AF38EA7A5FD3E62E508B48DA2E4AE46C1F4BA927532F8A95699",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/counts/navigation_anchors",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-counts-open_blockers-missing",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/counts/open_blockers"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_COUNTS_OPEN_BLOCKERS",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_COUNTS_OPEN_BLOCKERS",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "AD0842E30861E6DA0F0031C2B005DE4AC158DF9B02C104AFC2E79C648AE3F927",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/counts/open_blockers",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-counts-open_blockers-wrong",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/counts/open_blockers"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_COUNTS_OPEN_BLOCKERS",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_COUNTS_OPEN_BLOCKERS",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "6351B3D725AA38DC34D5E01AF34F4BCC2E1CB1CABDD96774792927A629D1D7C2",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/counts/open_blockers",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-counts-pages-missing",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/counts/pages"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_COUNTS_PAGES",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_COUNTS_PAGES",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "432169BDEA80AC924DB562BE28DB033ED0B8FA308A629AD429813CA19FEC6DCE",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/counts/pages",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-counts-pages-wrong",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/counts/pages"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_COUNTS_PAGES",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_COUNTS_PAGES",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "2E5A37AFE16B11E2554D7E28655A81CECCFAE4D6C0C3E89D58369F3CBC25E854",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/counts/pages",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-counts-pregens-missing",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/counts/pregens"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_COUNTS_PREGENS",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_COUNTS_PREGENS",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "165D936B9637E82B42CF7D236D341C84D9EC2DDA7D30AD3D2F897E2F4166F612",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/counts/pregens",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-counts-pregens-wrong",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/counts/pregens"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_COUNTS_PREGENS",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_COUNTS_PREGENS",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "2F91DCC93251AF98CD7A8DF22290741D9F3AFD950B8924340C8E3B2E736D30BC",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/counts/pregens",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-counts-referenced_assets-missing",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/counts/referenced_assets"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_COUNTS_REFERENCED_ASSETS",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_COUNTS_REFERENCED_ASSETS",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "E60330ADAD6666B31837A0FF0BE65263186735D4BC95980D182767F2A576EEA1",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/counts/referenced_assets",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-counts-referenced_assets-wrong",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/counts/referenced_assets"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_COUNTS_REFERENCED_ASSETS",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_COUNTS_REFERENCED_ASSETS",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "26E42108FCAEF44FA4B4DF8CE2F28EB235402CD90F5769375B840BD8EE4E2E98",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/counts/referenced_assets",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-counts-renders-missing",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/counts/renders"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_COUNTS_RENDERS",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_COUNTS_RENDERS",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "500187B8D50D8A75BDDF88293F043D47975650C5F99E6E4B1F39D2052B946CB9",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/counts/renders",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-counts-renders-wrong",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/counts/renders"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_COUNTS_RENDERS",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_COUNTS_RENDERS",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "2205F50772A9067B8FBC2390D88D1F215F60F94F435AAF80EDAFCDB32AEC6037",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/counts/renders",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-counts-unreferenced_assets-missing",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/counts/unreferenced_assets"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_COUNTS_UNREFERENCED_ASSETS",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_COUNTS_UNREFERENCED_ASSETS",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "F030E65534977ABFA200AD27D808E2940316A4AEECE47246F523FB775EB8FB4D",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/counts/unreferenced_assets",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-counts-unreferenced_assets-wrong",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/counts/unreferenced_assets"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_COUNTS_UNREFERENCED_ASSETS",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_COUNTS_UNREFERENCED_ASSETS",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "94FD367D050CC2911CD8EEDE857591C775D4F870220229D34926D2AC72AACF3C",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/counts/unreferenced_assets",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-gate-asset_conservation-missing",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/asset_conservation"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_GATE_ASSET_CONSERVATION",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_GATE_ASSET_CONSERVATION",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "A89C4AD9649C4D50419D565F027B3ABD7B099372B35C22C504724A38C5BBE888",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/asset_conservation",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-gate-contact_sheet_coverage-missing",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/contact_sheet_coverage"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_GATE_CONTACT_SHEET_COVERAGE",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_GATE_CONTACT_SHEET_COVERAGE",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "18758B7DF04FE3741465327584B996CAEA35791B79D8EE2FC6E8F8A187BDD582",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/contact_sheet_coverage",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-gate-navigation_anchors-missing",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/navigation_anchors"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_GATE_NAVIGATION_ANCHORS",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_GATE_NAVIGATION_ANCHORS",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "5E91158EF1A3B8708146EAAA68F03C9DB120B44BE2F4520827D3BF51BC4C642A",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/navigation_anchors",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-gate-page_1_5_modes-missing",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/page_1_5_modes"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_GATE_PAGE_1_5_MODES",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_GATE_PAGE_1_5_MODES",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "203D6D7B6879A4C44D6156E0672DD347F47FA4FEFFC817CD27ABEDD4B6405697",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/page_1_5_modes",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-gate-page_coverage-missing",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/page_coverage"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_GATE_PAGE_COVERAGE",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_GATE_PAGE_COVERAGE",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "004FFE0AB6A597B2E25FBFB4B17A414DBDB5CAC7F70728A660D68E80069F3BAD",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/page_coverage",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-gate-promotion-missing",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/promotion"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_GATE_PROMOTION",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_GATE_PROMOTION",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "B240723A04B2A6F3D0ECE63327F45FF51B81CF316601A9A4B08CD5653BBDEF7A",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/promotion",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-gate-recovery_admission-missing",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/recovery_admission"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_GATE_RECOVERY_ADMISSION",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_GATE_RECOVERY_ADMISSION",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "5843B5B2DA746469F8C58F7B76A2F6409C4A1FCD96473C3A3B714A17A0A961A9",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/recovery_admission",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-gate-source_identity-missing",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/source_identity"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_GATE_SOURCE_IDENTITY",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_GATE_SOURCE_IDENTITY",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "C7B281A9374BD3DC8A004054D40916CFDE5FF304982590C17486CEA74E0DB474",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/source_identity",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-gate-visual_review-missing",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/visual_review"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_GATE_VISUAL_REVIEW",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_GATE_VISUAL_REVIEW",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "B85866262FCF5131EF73D852DA5D2C701FAA30D0AF551636C1F0127C1CBC220F",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/visual_review",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-gate-asset_conservation-wrong",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/asset_conservation"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_GATE_ASSET_CONSERVATION",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_GATE_ASSET_CONSERVATION",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "8699B2C1F3793E3352F36418AB793ABA4091BA9CC6AE0D79413D62A3EED25509",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/asset_conservation",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-gate-contact_sheet_coverage-wrong",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/contact_sheet_coverage"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_GATE_CONTACT_SHEET_COVERAGE",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_GATE_CONTACT_SHEET_COVERAGE",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "AE9FBFE6F09E7F7316B3AEBB1E15B1C9C760ECB333B17FE812A402300A0CAE83",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/contact_sheet_coverage",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-gate-navigation_anchors-wrong",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/navigation_anchors"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_GATE_NAVIGATION_ANCHORS",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_GATE_NAVIGATION_ANCHORS",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "1981BEA27D89E512153AD40E2367B568C1B1DC4D691D253D99216D76DAF2578E",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/navigation_anchors",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-gate-page_coverage-wrong",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/page_coverage"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_GATE_PAGE_COVERAGE",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_GATE_PAGE_COVERAGE",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "00152BD3A45269C46E2948478220493907A07ED306BA8D4637E5FB10620EA52F",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/page_coverage",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-gate-recovery_admission-wrong",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/recovery_admission"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_GATE_RECOVERY_ADMISSION",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_GATE_RECOVERY_ADMISSION",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "9285A62A97070F1E5E297856E2F6EA199C7EFE4CC8801F3F7D85C8B328E4837E",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/recovery_admission",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-gate-source_identity-wrong",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/source_identity"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_GATE_SOURCE_IDENTITY",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_GATE_SOURCE_IDENTITY",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "88D58DEC4C169DC2037FFBA7702C732D286C7D6BCAD003A3AD076D9C78A2EA46",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/source_identity",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-gate-page_1_5_modes-closed",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/page_1_5_modes"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_GATE_PAGE_1_5_MODES",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_GATE_PAGE_1_5_MODES",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "EDD2C811D7A2ADBDA99D3F2E02DE77A10D1C1756DF9651437225F56C09B0D259",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/page_1_5_modes",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-gate-promotion-closed",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/promotion"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_GATE_PROMOTION",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_GATE_PROMOTION",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "DC9BC60CE954DE047CEB1F20DCD93A55110427B5123A25153F7396D676E943C7",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/promotion",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-gate-visual_review-closed",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/visual_review"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_GATE_VISUAL_REVIEW",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_GATE_VISUAL_REVIEW",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "C9E81D47A9C13A55C8CABE33850674C400028F0B30B3CEA9B2F998791C544BF9",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/gate_results/visual_review",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-historical-material-true",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/historical_material_opened"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_HISTORY",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_HISTORY",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "DE2C2A5348DD94FA43DCECEA6DE8936268F54C6D99FB07BA9F80D2E6E9435B3A",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/historical_material_opened",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-main-scripts-invoked-true",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/main_scripts_invoked"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_MAIN_SCRIPTS",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_MAIN_SCRIPTS",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "AA82282C55DA29432F01685EFD8067862E8C594FE875895F60D0C1BA38F0658D",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/main_scripts_invoked",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-inventory-rule-wrong",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_rule"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_QA_INVENTORY_RULE",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_QA_INVENTORY_RULE",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "F6990E3CD4DE10DFDF0891D13449243BB612D41F6F3164A93C0B6E02BDD865A1",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_rule",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-inventory-count-wrong",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_count"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_INV_CARDINALITY",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_INV_CARDINALITY",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "307AADAA304C7DC8663FDD5B265B3A1401BF2507CBE66E70466EAD744B09C5FC",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_count",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-inventory-digest-wrong",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_INV_DIGEST",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_INV_DIGEST",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "CEAA4567B5572C8705F68424EFA7BAFC6240AA31BDF0A356E71E45E081022514",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "QAV-inventory-array-wrong",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/RECONSTRUCTED_EN.md"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_INV_ORDINARY_ROW_MISSING",
    "family": "QAV",
    "fixture_root_token": "fixture",
    "observed_code": "E_INV_ORDINARY_ROW_MISSING",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "2651A112671B83128B71E434FC91E34E65659E33DB6B9E04CB8D703125F0D2F8",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/RECONSTRUCTED_EN.md",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "REG-P1-stale-metadata",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/schema",
      "candidate/RECONSTRUCTED_EN.qa.json#/recovery_manifest_sha256",
      "candidate/RECONSTRUCTED_EN.qa.json#/recovery_evidence_sha256",
      "candidate/RECONSTRUCTED_EN.qa.json#/open_blocker_count",
      "candidate/RECONSTRUCTED_EN.qa.json#/counts/open_blockers",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-001.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-002.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-003.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-004.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-005.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-006.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-007.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-008.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-009.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-010.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-011.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-012.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-013.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-014.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-015.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-016.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-017.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-018.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-019.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-020.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-021.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-022.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-023.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-024.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-025.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-026.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-027.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-028.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-029.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-030.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-031.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_count",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SHAPE_QA",
    "family": "REG",
    "fixture_root_token": "fixture",
    "observed_code": "E_SHAPE_QA",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "6562C451F47120D120025C754B5B3729390BB65251F150C220017BB6F4003912",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "REG-P1-missing-enforcement",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/counts/pages"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_COUNTS_PAGES",
    "family": "REG",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_COUNTS_PAGES",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "9704137F1A03D24C4FB6A0A056E02420172D999D1DBDFC9AFEDB673DFA5D3798",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/counts/pages",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "INJ-profile-seal-mutated",
    "changed_before_reseal": [
      "profile#/authority_sha256"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_PROFILE_SEAL",
    "family": "INJ",
    "fixture_root_token": "fixture",
    "observed_code": "E_PROFILE_SEAL",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "1AEAA4B8112B2585B3539B8247DE6318C533B4D01A3DCB4C1263BA36B49A036A",
    "semantic_before_sha256": "F856879FFA48D6E869096D917CA4389D672EE9F5C01A6FB77A09F70325A0E3C4",
    "semantic_selector": "profile#/authority_sha256",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "INJ-test-route-given-production-profile",
    "changed_before_reseal": [
      "context#/profile/kind"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_PROFILE_ROUTE",
    "family": "INJ",
    "fixture_root_token": "fixture",
    "observed_code": "E_PROFILE_ROUTE",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "88531EDE02E6C8D050FB842FDF770B4FC43398ACE47E4136B50DF640347CFF7C",
    "semantic_before_sha256": "F856879FFA48D6E869096D917CA4389D672EE9F5C01A6FB77A09F70325A0E3C4",
    "semantic_selector": "context#/profile/kind",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "INJ-identity-provider-bound-to-other-profile",
    "changed_before_reseal": [
      "identity#/bound_profile_sha256"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_PROVIDER_BINDING",
    "family": "INJ",
    "fixture_root_token": "fixture",
    "observed_code": "E_PROVIDER_BINDING",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "E9A8BB593AC9A701157A7BEDC7AACEBC3E5D42C69215C26A3652F8EDD157517C",
    "semantic_before_sha256": "233B4FCC14742E1EE5E932B57872F8B7D2AA8DD96F7C528A9AFE0F2A451B28E2",
    "semantic_selector": "identity#/bound_profile_sha256",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "INJ-filesystem-provider-bound-to-other-profile",
    "changed_before_reseal": [
      "filesystem#/bound_profile_sha256"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_PROVIDER_BINDING",
    "family": "INJ",
    "fixture_root_token": "fixture",
    "observed_code": "E_PROVIDER_BINDING",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "FD1FA51B4C9CCCC64EA6B41918C1C2419B5C16605AE114929D033B48591B5FC0",
    "semantic_before_sha256": "BCBD966FB1EEC617DFB7E16A3CEB0B005EF2BF4F77C6BB7EDA653B6C1ECBA33F",
    "semantic_selector": "filesystem#/bound_profile_sha256",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "INJ-repository-root-observation-mismatch",
    "changed_before_reseal": [
      "repository#/root"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_REPO_ROOT",
    "family": "INJ",
    "fixture_root_token": "fixture",
    "observed_code": "E_REPO_ROOT",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "221EE1634732BED5F96E08FABC142ECAFB23CA089C9A44CD6657D9C2C5CC54E7",
    "semantic_before_sha256": "B3CBC8E8E1C17B222EE1FDB29B17B5448864ACAC3198029FFBEA2C973F02077B",
    "semantic_selector": "repository#/root",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  }
]
<!-- AUDITS_JSON_END -->

## Canonical six-field UTF-8/LF rows

<!-- CANONICAL_ROWS_BEGIN -->
REP-branch-wrong	repository#/branch		E_REPO_BRANCH	E_REPO_BRANCH	PASS
REP-head-wrong	repository#/head		E_REPO_HEAD	E_REPO_HEAD	PASS
SRC-source-byte-identical-alias	source#/path		E_SOURCE_PATH	E_SOURCE_PATH	PASS
SRC-source-external-locator	sidecar#/external_locator	sidecar,profile	E_SOURCE_EXTERNAL_FORBIDDEN	E_SOURCE_EXTERNAL_FORBIDDEN	PASS
SRC-source-missing	source#/physical-entry		E_PATH_MISSING	E_PATH_MISSING	PASS
SRC-source-bytes-wrong	source#/bytes		E_SOURCE_BYTES	E_SOURCE_BYTES	PASS
SRC-source-hash-wrong	source#/sha256		E_SOURCE_HASH	E_SOURCE_HASH	PASS
SRC-source-reparse	source#/reparse		E_PATH_REPARSE	E_PATH_REPARSE	PASS
SRC-sidecar-missing	sidecar#/physical-entry		E_PATH_MISSING	E_PATH_MISSING	PASS
SRC-sidecar-raw-hash-wrong	sidecar#/raw_sha256		E_SIDECAR_HASH	E_SIDECAR_HASH	PASS
SRC-sidecar-working-path-wrong	sidecar#/working_source/path	sidecar,profile	E_SIDECAR_WORKING_PATH	E_SIDECAR_WORKING_PATH	PASS
SRC-sidecar-working-bytes-wrong	sidecar#/working_source/bytes	sidecar,profile	E_SIDECAR_WORKING_BYTES	E_SIDECAR_WORKING_BYTES	PASS
SRC-sidecar-working-hash-wrong	sidecar#/working_source/sha256	sidecar,profile	E_SIDECAR_WORKING_HASH	E_SIDECAR_WORKING_HASH	PASS
SRC-sidecar-page-count-wrong	sidecar#/working_source/page_count	sidecar,profile	E_SIDECAR_PAGE_COUNT	E_SIDECAR_PAGE_COUNT	PASS
SRC-sidecar-media-box-wrong	sidecar#/working_source/media_box	sidecar,profile	E_SIDECAR_MEDIA_BOX	E_SIDECAR_MEDIA_BOX	PASS
SRC-sidecar-rotation-wrong	sidecar#/working_source/rotations	sidecar,profile	E_SIDECAR_ROTATION	E_SIDECAR_ROTATION	PASS
SRC-sidecar-runtime-dependency-true	sidecar#/policy/runtime_dependency	sidecar,profile	E_SIDECAR_RUNTIME_DEPENDENCY	E_SIDECAR_RUNTIME_DEPENDENCY	PASS
SRC-sidecar-external-path-allowed	sidecar#/policy/external_path_allowed	sidecar,profile	E_SIDECAR_EXTERNAL_ALLOWED	E_SIDECAR_EXTERNAL_ALLOWED	PASS
SRC-sidecar-subsequent-path-wrong	sidecar#/policy/subsequent_path	sidecar,profile	E_SIDECAR_SUBSEQUENT_PATH	E_SIDECAR_SUBSEQUENT_PATH	PASS
SRC-sidecar-origin-marked-source	sidecar#/policy/origin	sidecar,profile	E_SIDECAR_ORIGIN_POLICY	E_SIDECAR_ORIGIN_POLICY	PASS
AUT-contract-argument-wrong	contract#/path		E_CONTRACT_PATH	E_CONTRACT_PATH	PASS
AUT-contract-raw-hash-wrong	contract#/raw_sha256		E_CONTRACT_HASH	E_CONTRACT_HASH	PASS
AUT-contract-canonical-content-wrong	contract#/scenario	contract,profile	E_CONTRACT_CANONICAL	E_CONTRACT_CANONICAL	PASS
AUT-snapshot-bytes-wrong	candidate/SCENARIO_CONTRACT.json#/scenario		E_CONTRACT_SNAPSHOT_BYTES	E_CONTRACT_SNAPSHOT_BYTES	PASS
AUT-snapshot-hash-binding-wrong	candidate/SOURCE_IDENTITY.json#/contract_snapshot_sha256		E_CONTRACT_SNAPSHOT_HASH	E_CONTRACT_SNAPSHOT_HASH	PASS
AUT-source-identity-contract-sha	candidate/SOURCE_IDENTITY.json#/contract_sha256		E_SOURCE_IDENTITY_CONTRACT	E_SOURCE_IDENTITY_CONTRACT	PASS
AUT-source-identity-source-bytes	candidate/SOURCE_IDENTITY.json#/source/bytes		E_SOURCE_IDENTITY_SOURCE_BYTES	E_SOURCE_IDENTITY_SOURCE_BYTES	PASS
AUT-source-identity-source-sha	candidate/SOURCE_IDENTITY.json#/source/sha256		E_SOURCE_IDENTITY_SOURCE_HASH	E_SOURCE_IDENTITY_SOURCE_HASH	PASS
AUT-source-identity-page-count	candidate/SOURCE_IDENTITY.json#/source/page_count		E_SOURCE_IDENTITY_PAGE_COUNT	E_SOURCE_IDENTITY_PAGE_COUNT	PASS
AUT-source-identity-media-box	candidate/SOURCE_IDENTITY.json#/source/media_box		E_SOURCE_IDENTITY_MEDIA_BOX	E_SOURCE_IDENTITY_MEDIA_BOX	PASS
AUT-source-identity-rotation	candidate/SOURCE_IDENTITY.json#/source/rotations		E_SOURCE_IDENTITY_ROTATION	E_SOURCE_IDENTITY_ROTATION	PASS
AUT-source-identity-recovery-manifest-sha	candidate/SOURCE_IDENTITY.json#/recovery_manifest_sha256		E_SOURCE_IDENTITY_RECOVERY_MANIFEST	E_SOURCE_IDENTITY_RECOVERY_MANIFEST	PASS
AUT-source-identity-recovery-evidence-sha	candidate/SOURCE_IDENTITY.json#/recovery_evidence_sha256		E_SOURCE_IDENTITY_RECOVERY_EVIDENCE	E_SOURCE_IDENTITY_RECOVERY_EVIDENCE	PASS
AUT-source-identity-recovery-root	candidate/SOURCE_IDENTITY.json#/recovery_root		E_SOURCE_IDENTITY_RECOVERY_ROOT	E_SOURCE_IDENTITY_RECOVERY_ROOT	PASS
AUT-source-identity-history-true	candidate/SOURCE_IDENTITY.json#/historical_material_opened		E_SOURCE_IDENTITY_HISTORY	E_SOURCE_IDENTITY_HISTORY	PASS
AUT-source-identity-state-wrong	candidate/SOURCE_IDENTITY.json#/state		E_SOURCE_IDENTITY_STATE	E_SOURCE_IDENTITY_STATE	PASS
AUT-recovery-root-wrong	recovery#/path		E_RECOVERY_ROOT	E_RECOVERY_ROOT	PASS
AUT-recovery-manifest-raw-hash	recovery/RECOVERY_MANIFEST.json#/raw_sha256		E_RECOVERY_MANIFEST_HASH	E_RECOVERY_MANIFEST_HASH	PASS
AUT-recovery-evidence-raw-hash	recovery/RECOVERY_EVIDENCE.json#/raw_sha256		E_RECOVERY_EVIDENCE_HASH	E_RECOVERY_EVIDENCE_HASH	PASS
AUT-recovery-successor-file-count	recovery/RECOVERY_MANIFEST.json#/successor_file_count	recovery_manifest,source_identity,inventory,qa,profile	E_RECOVERY_FILE_COUNT	E_RECOVERY_FILE_COUNT	PASS
AUT-recovery-successor-total-bytes	recovery/RECOVERY_MANIFEST.json#/successor_total_bytes	recovery_manifest,source_identity,inventory,qa,profile	E_RECOVERY_TOTAL_BYTES	E_RECOVERY_TOTAL_BYTES	PASS
AUT-recovery-manifest-row-path	recovery/RECOVERY_MANIFEST.json#/files/0/path	recovery_manifest,source_identity,inventory,qa,profile	E_RECOVERY_ROW_PATH	E_RECOVERY_ROW_PATH	PASS
AUT-recovery-manifest-row-bytes	recovery/RECOVERY_MANIFEST.json#/files/0/bytes	recovery_manifest,source_identity,inventory,qa,profile	E_RECOVERY_ROW_BYTES	E_RECOVERY_ROW_BYTES	PASS
AUT-recovery-manifest-row-hash	recovery/RECOVERY_MANIFEST.json#/files/0/sha256	recovery_manifest,source_identity,inventory,qa,profile	E_RECOVERY_ROW_HASH	E_RECOVERY_ROW_HASH	PASS
AUT-recovery-manifest-row-duplicate	recovery/RECOVERY_MANIFEST.json#/files/1/path	recovery_manifest,source_identity,inventory,qa,profile	E_RECOVERY_ROW_DUPLICATE	E_RECOVERY_ROW_DUPLICATE	PASS
AUT-recovery-forbidden-payload	recovery/forbidden.pdf		E_RECOVERY_FORBIDDEN	E_RECOVERY_FORBIDDEN	PASS
AUT-recovery-evidence-source-binding	recovery/RECOVERY_EVIDENCE.json#/source_identity	recovery_evidence,source_identity,inventory,qa,profile	E_RECOVERY_SOURCE_BINDING	E_RECOVERY_SOURCE_BINDING	PASS
AUT-recovery-evidence-payload-binding	recovery/RECOVERY_EVIDENCE.json#/payload	recovery_evidence,source_identity,inventory,qa,profile	E_RECOVERY_PAYLOAD_BINDING	E_RECOVERY_PAYLOAD_BINDING	PASS
AUT-recovery-allowed-paths	recovery/RECOVERY_EVIDENCE.json#/allowed_payload_paths	recovery_evidence,source_identity,inventory,qa,profile	E_RECOVERY_ALLOWED_PATHS	E_RECOVERY_ALLOWED_PATHS	PASS
AUT-recovery-promotion-true	recovery/RECOVERY_EVIDENCE.json#/promotion	recovery_evidence,source_identity,inventory,qa,profile	E_RECOVERY_PROMOTION	E_RECOVERY_PROMOTION	PASS
TOP-candidate-root-wrong	candidate#/root		E_CANDIDATE_ROOT	E_CANDIDATE_ROOT	PASS
TOP-candidate-root-escape	candidate#/escape		E_PATH_ESCAPE	E_PATH_ESCAPE	PASS
TOP-candidate-root-reparse	candidate#/reparse		E_PATH_REPARSE	E_PATH_REPARSE	PASS
TOP-nested-reparse	candidate/pages/page-001.md#/reparse		E_PATH_REPARSE	E_PATH_REPARSE	PASS
TOP-root-file-missing	candidate/RECONSTRUCTED_EN.md#/physical-entry		E_TOPOLOGY_MISSING	E_TOPOLOGY_MISSING	PASS
TOP-root-entry-extra	candidate/EXTRA.txt#/physical-entry		E_TOPOLOGY_EXTRA	E_TOPOLOGY_EXTRA	PASS
TOP-evidence-file-missing	candidate/evidence/COMMANDS.json#/physical-entry		E_TOPOLOGY_MISSING	E_TOPOLOGY_MISSING	PASS
TOP-evidence-file-extra	candidate/evidence/EXTRA.json#/physical-entry		E_TOPOLOGY_EXTRA	E_TOPOLOGY_EXTRA	PASS
TOP-page-missing	candidate/pages/page-001.md#/physical-entry		E_TOPOLOGY_MISSING	E_TOPOLOGY_MISSING	PASS
TOP-source-render-missing	candidate/renders/source/page-001.png#/physical-entry		E_TOPOLOGY_MISSING	E_TOPOLOGY_MISSING	PASS
TOP-sheet-missing	candidate/renders/contact_sheets/sheet-001.png#/physical-entry		E_TOPOLOGY_MISSING	E_TOPOLOGY_MISSING	PASS
TOP-engine-payload-missing	candidate/engine/payload-001.bin#/physical-entry		E_TOPOLOGY_MISSING	E_TOPOLOGY_MISSING	PASS
TOP-protected-empty-subtree-nonempty	candidate/assets/probe.bin#/physical-entry		E_PROTECTED_EMPTY_SUBTREE	E_PROTECTED_EMPTY_SUBTREE	PASS
TOP-forbidden-pdf	candidate/forbidden.pdf#/physical-entry		E_CANDIDATE_FORBIDDEN_PDF	E_CANDIDATE_FORBIDDEN_PDF	PASS
TOP-forbidden-compiled-suffix	candidate/forbidden.pyc#/physical-entry		E_CANDIDATE_FORBIDDEN_COMPILED	E_CANDIDATE_FORBIDDEN_COMPILED	PASS
TOP-forbidden-pycache	candidate/__pycache__/probe.bin#/physical-entry		E_CANDIDATE_FORBIDDEN_PYCACHE	E_CANDIDATE_FORBIDDEN_PYCACHE	PASS
TOP-forbidden-bridge-runtime	candidate/_bridge_runtime/probe.bin#/physical-entry		E_CANDIDATE_FORBIDDEN_BRIDGE_RUNTIME	E_CANDIDATE_FORBIDDEN_BRIDGE_RUNTIME	PASS
TOP-forbidden-cache	candidate/cache/probe.bin#/physical-entry		E_CANDIDATE_FORBIDDEN_CACHE	E_CANDIDATE_FORBIDDEN_CACHE	PASS
TOP-forbidden-pytest-cache	candidate/.pytest_cache/probe.bin#/physical-entry		E_CANDIDATE_FORBIDDEN_PYTEST_CACHE	E_CANDIDATE_FORBIDDEN_PYTEST_CACHE	PASS
TOP-forbidden-tmp	candidate/tmp/probe.bin#/physical-entry		E_CANDIDATE_FORBIDDEN_TMP	E_CANDIDATE_FORBIDDEN_TMP	PASS
TOP-forbidden-temp	candidate/temp/probe.bin#/physical-entry		E_CANDIDATE_FORBIDDEN_TEMP	E_CANDIDATE_FORBIDDEN_TEMP	PASS
SCH-CONTRACT-schema-wrong	candidate/SCENARIO_CONTRACT.json#/schema		E_SCHEMA_CONTRACT	E_SCHEMA_CONTRACT	PASS
SCH-CONTRACT-required-top-member-missing	candidate/SCENARIO_CONTRACT.json#/pages		E_SHAPE_CONTRACT	E_SHAPE_CONTRACT	PASS
SCH-SIDECAR-schema-wrong	source/SOURCE_ADMISSION.json#/schema	sidecar,profile	E_SCHEMA_SIDECAR	E_SCHEMA_SIDECAR	PASS
SCH-SIDECAR-required-top-member-missing	source/SOURCE_ADMISSION.json#/external_locator	sidecar,profile	E_SHAPE_SIDECAR	E_SHAPE_SIDECAR	PASS
SCH-RECOVERY_MANIFEST-schema-wrong	recovery/RECOVERY_MANIFEST.json#/schema	recovery_manifest	E_SCHEMA_RECOVERY_MANIFEST	E_SCHEMA_RECOVERY_MANIFEST	PASS
SCH-RECOVERY_MANIFEST-required-top-member-missing	recovery/RECOVERY_MANIFEST.json#/assets	recovery_manifest	E_SHAPE_RECOVERY_MANIFEST	E_SHAPE_RECOVERY_MANIFEST	PASS
SCH-RECOVERY_EVIDENCE-schema-wrong	recovery/RECOVERY_EVIDENCE.json#/schema	recovery_evidence	E_SCHEMA_RECOVERY_EVIDENCE	E_SCHEMA_RECOVERY_EVIDENCE	PASS
SCH-RECOVERY_EVIDENCE-required-top-member-missing	recovery/RECOVERY_EVIDENCE.json#/allowed_payload_paths	recovery_evidence	E_SHAPE_RECOVERY_EVIDENCE	E_SHAPE_RECOVERY_EVIDENCE	PASS
SCH-QA-schema-wrong	candidate/RECONSTRUCTED_EN.qa.json#/schema		E_SCHEMA_QA	E_SCHEMA_QA	PASS
SCH-QA-required-top-member-missing	candidate/RECONSTRUCTED_EN.qa.json#/asset_count		E_SHAPE_QA	E_SHAPE_QA	PASS
SCH-SOURCE_IDENTITY-schema-wrong	candidate/SOURCE_IDENTITY.json#/schema		E_SCHEMA_SOURCE_IDENTITY	E_SCHEMA_SOURCE_IDENTITY	PASS
SCH-SOURCE_IDENTITY-required-top-member-missing	candidate/SOURCE_IDENTITY.json#/contract_sha256		E_SHAPE_SOURCE_IDENTITY	E_SHAPE_SOURCE_IDENTITY	PASS
SCH-PAGE_PROVENANCE-schema-wrong	candidate/evidence/PAGE_PROVENANCE.json#/schema		E_SCHEMA_PAGE_PROVENANCE	E_SCHEMA_PAGE_PROVENANCE	PASS
SCH-PAGE_PROVENANCE-required-top-member-missing	candidate/evidence/PAGE_PROVENANCE.json#/rows		E_SHAPE_PAGE_PROVENANCE	E_SHAPE_PAGE_PROVENANCE	PASS
SCH-CONTENT_PROVENANCE-schema-wrong	candidate/evidence/CONTENT_PROVENANCE.json#/schema		E_SCHEMA_CONTENT_PROVENANCE	E_SCHEMA_CONTENT_PROVENANCE	PASS
SCH-CONTENT_PROVENANCE-required-top-member-missing	candidate/evidence/CONTENT_PROVENANCE.json#/rows		E_SHAPE_CONTENT_PROVENANCE	E_SHAPE_CONTENT_PROVENANCE	PASS
SCH-ASSET_PROVENANCE-schema-wrong	candidate/evidence/ASSET_PROVENANCE.json#/schema		E_SCHEMA_ASSET_PROVENANCE	E_SCHEMA_ASSET_PROVENANCE	PASS
SCH-ASSET_PROVENANCE-required-top-member-missing	candidate/evidence/ASSET_PROVENANCE.json#/referenced		E_SHAPE_ASSET_PROVENANCE	E_SHAPE_ASSET_PROVENANCE	PASS
SCH-ENTITY_INVENTORY-schema-wrong	candidate/evidence/ENTITY_INVENTORY.json#/schema		E_SCHEMA_ENTITY_INVENTORY	E_SCHEMA_ENTITY_INVENTORY	PASS
SCH-ENTITY_INVENTORY-required-top-member-missing	candidate/evidence/ENTITY_INVENTORY.json#/rows		E_SHAPE_ENTITY_INVENTORY	E_SHAPE_ENTITY_INVENTORY	PASS
SCH-HANDOUT_INVENTORY-schema-wrong	candidate/evidence/HANDOUT_INVENTORY.json#/schema		E_SCHEMA_HANDOUT_INVENTORY	E_SCHEMA_HANDOUT_INVENTORY	PASS
SCH-HANDOUT_INVENTORY-required-top-member-missing	candidate/evidence/HANDOUT_INVENTORY.json#/required_count		E_SHAPE_HANDOUT_INVENTORY	E_SHAPE_HANDOUT_INVENTORY	PASS
SCH-NAVIGATION_INVENTORY-schema-wrong	candidate/evidence/NAVIGATION_INVENTORY.json#/schema		E_SCHEMA_NAVIGATION_INVENTORY	E_SCHEMA_NAVIGATION_INVENTORY	PASS
SCH-NAVIGATION_INVENTORY-required-top-member-missing	candidate/evidence/NAVIGATION_INVENTORY.json#/rows		E_SHAPE_NAVIGATION_INVENTORY	E_SHAPE_NAVIGATION_INVENTORY	PASS
SCH-CONTENT_MODE_REVIEW-schema-wrong	candidate/evidence/CONTENT_MODE_REVIEW.json#/schema		E_SCHEMA_CONTENT_MODE_REVIEW	E_SCHEMA_CONTENT_MODE_REVIEW	PASS
SCH-CONTENT_MODE_REVIEW-required-top-member-missing	candidate/evidence/CONTENT_MODE_REVIEW.json#/rows		E_SHAPE_CONTENT_MODE_REVIEW	E_SHAPE_CONTENT_MODE_REVIEW	PASS
SCH-REFERENCE_ONLY_AUDIT-schema-wrong	candidate/evidence/REFERENCE_ONLY_AUDIT.json#/schema		E_SCHEMA_REFERENCE_ONLY_AUDIT	E_SCHEMA_REFERENCE_ONLY_AUDIT	PASS
SCH-REFERENCE_ONLY_AUDIT-required-top-member-missing	candidate/evidence/REFERENCE_ONLY_AUDIT.json#/historical_material_opened		E_SHAPE_REFERENCE_ONLY_AUDIT	E_SHAPE_REFERENCE_ONLY_AUDIT	PASS
SCH-BLOCKER_LEDGER-schema-wrong	candidate/evidence/BLOCKER_LEDGER.json#/schema		E_SCHEMA_BLOCKER_LEDGER	E_SCHEMA_BLOCKER_LEDGER	PASS
SCH-BLOCKER_LEDGER-required-top-member-missing	candidate/evidence/BLOCKER_LEDGER.json#/open_count		E_SHAPE_BLOCKER_LEDGER	E_SHAPE_BLOCKER_LEDGER	PASS
SCH-COMMANDS-schema-wrong	candidate/evidence/COMMANDS.json#/schema		E_SCHEMA_COMMANDS	E_SCHEMA_COMMANDS	PASS
SCH-COMMANDS-required-top-member-missing	candidate/evidence/COMMANDS.json#/actions		E_SHAPE_COMMANDS	E_SHAPE_COMMANDS	PASS
SCH-qa-unexpected-top-member	candidate/RECONSTRUCTED_EN.qa.json#/unexpected		E_SHAPE_QA	E_SHAPE_QA	PASS
LED-open-count-wrong	candidate/evidence/BLOCKER_LEDGER.json#/open_count	inventory,qa	E_LEDGER_OPEN_COUNT	E_LEDGER_OPEN_COUNT	PASS
LED-row-count-wrong	candidate/evidence/BLOCKER_LEDGER.json#/rows	inventory,qa	E_LEDGER_ROW_COUNT	E_LEDGER_ROW_COUNT	PASS
LED-row-state-closed	candidate/evidence/BLOCKER_LEDGER.json#/rows/0/state	inventory,qa	E_LEDGER_ROW_STATE	E_LEDGER_ROW_STATE	PASS
LED-review-state-closed	candidate/evidence/BLOCKER_LEDGER.json#/rows/0/review_state	inventory,qa	E_LEDGER_REVIEW_STATE	E_LEDGER_REVIEW_STATE	PASS
LED-blocker-id-set-wrong	candidate/evidence/BLOCKER_LEDGER.json#/rows/0/id	inventory,qa	E_LEDGER_IDS	E_LEDGER_IDS	PASS
LED-affected-scope-count-wrong	candidate/evidence/BLOCKER_LEDGER.json#/rows/0/scope	inventory,qa	E_LEDGER_SCOPE	E_LEDGER_SCOPE	PASS
INV-ordinary-row-missing	candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/RECONSTRUCTED_EN.md		E_INV_ORDINARY_ROW_MISSING	E_INV_ORDINARY_ROW_MISSING	PASS
INV-evidence-row-missing	candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/evidence/COMMANDS.json		E_INV_EVIDENCE_ROW_MISSING	E_INV_EVIDENCE_ROW_MISSING	PASS
INV-sheet-row-missing	candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-001.png		E_INV_SHEET_ROW_MISSING	E_INV_SHEET_ROW_MISSING	PASS
INV-stale-extra-path	candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/-		E_INV_STALE_EXTRA_PATH	E_INV_STALE_EXTRA_PATH	PASS
INV-duplicate-path	candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/1/path		E_INV_DUPLICATE_PATH	E_INV_DUPLICATE_PATH	PASS
INV-qa-included	candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/-		E_INV_QA_INCLUDED	E_INV_QA_INCLUDED	PASS
INV-cardinality-wrong	candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_count		E_INV_CARDINALITY	E_INV_CARDINALITY	PASS
INV-order-nonordinal	candidate/RECONSTRUCTED_EN.qa.json#/output_inventory		E_INV_ORDER_NONORDINAL	E_INV_ORDER_NONORDINAL	PASS
INV-row-bytes-wrong	candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/0/bytes		E_INV_ROW_BYTES	E_INV_ROW_BYTES	PASS
INV-row-hash-wrong	candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/0/sha256		E_INV_ROW_HASH	E_INV_ROW_HASH	PASS
INV-row-hash-lowercase	candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/0/sha256		E_INV_ROW_HASH_LOWERCASE	E_INV_ROW_HASH_LOWERCASE	PASS
INV-digest-wrong	candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256		E_INV_DIGEST	E_INV_DIGEST	PASS
INV-path-backslash	candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/0/path		E_INV_PATH_BACKSLASH	E_INV_PATH_BACKSLASH	PASS
INV-path-absolute-or-drive	candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/0/path		E_INV_PATH_ABSOLUTE_OR_DRIVE	E_INV_PATH_ABSOLUTE_OR_DRIVE	PASS
INV-path-parent-segment	candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/0/path		E_INV_PATH_PARENT_SEGMENT	E_INV_PATH_PARENT_SEGMENT	PASS
INV-path-leading-dot-slash	candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/0/path		E_INV_PATH_LEADING_DOT_SLASH	E_INV_PATH_LEADING_DOT_SLASH	PASS
INV-row-shape-wrong	candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/0/unexpected		E_INV_ROW_SHAPE	E_INV_ROW_SHAPE	PASS
INV-live-file-changed-behind-row	candidate/RECONSTRUCTED_EN.md#/live-bytes		E_INV_LIVE_FILE_CHANGED	E_INV_LIVE_FILE_CHANGED	PASS
PAG-page-row-missing	candidate/evidence/PAGE_PROVENANCE.json#/rows/0	inventory,qa	E_PAGE_SET	E_PAGE_SET	PASS
PAG-page-row-duplicate	candidate/evidence/PAGE_PROVENANCE.json#/rows/-	inventory,qa	E_PAGE_DUPLICATE	E_PAGE_DUPLICATE	PASS
PAG-page-number-wrong	candidate/evidence/PAGE_PROVENANCE.json#/rows/0/page_number	inventory,qa	E_PAGE_NUMBER	E_PAGE_NUMBER	PASS
PAG-page-id-wrong	candidate/evidence/PAGE_PROVENANCE.json#/rows/0/page_id	inventory,qa	E_PAGE_ID	E_PAGE_ID	PASS
PAG-engine-index-wrong	candidate/evidence/PAGE_PROVENANCE.json#/rows/0/engine_page_idx	inventory,qa	E_PAGE_ENGINE_INDEX	E_PAGE_ENGINE_INDEX	PASS
PAG-role-wrong	candidate/evidence/PAGE_PROVENANCE.json#/rows/0/contract_role	inventory,qa	E_PAGE_ROLE	E_PAGE_ROLE	PASS
PAG-contract-mode-wrong	candidate/evidence/PAGE_PROVENANCE.json#/rows/0/contract_content_mode	inventory,qa	E_PAGE_CONTENT_MODE	E_PAGE_CONTENT_MODE	PASS
PAG-markdown-path-wrong	candidate/evidence/PAGE_PROVENANCE.json#/rows/0/markdown/path	inventory,qa	E_PAGE_MARKDOWN_PATH	E_PAGE_MARKDOWN_PATH	PASS
PAG-markdown-bytes-wrong	candidate/evidence/PAGE_PROVENANCE.json#/rows/0/markdown/bytes	inventory,qa	E_PAGE_MARKDOWN_BYTES	E_PAGE_MARKDOWN_BYTES	PASS
PAG-markdown-hash-wrong	candidate/evidence/PAGE_PROVENANCE.json#/rows/0/markdown/sha256	inventory,qa	E_PAGE_MARKDOWN_HASH	E_PAGE_MARKDOWN_HASH	PASS
PAG-render-path-wrong	candidate/evidence/PAGE_PROVENANCE.json#/rows/0/render/path	inventory,qa	E_PAGE_RENDER_PATH	E_PAGE_RENDER_PATH	PASS
PAG-render-bytes-wrong	candidate/evidence/PAGE_PROVENANCE.json#/rows/0/render/bytes	inventory,qa	E_PAGE_RENDER_BYTES	E_PAGE_RENDER_BYTES	PASS
PAG-render-hash-wrong	candidate/evidence/PAGE_PROVENANCE.json#/rows/0/render/sha256	inventory,qa	E_PAGE_RENDER_HASH	E_PAGE_RENDER_HASH	PASS
PAG-render-page-number-wrong	candidate/evidence/PAGE_PROVENANCE.json#/rows/0/render/page_number	inventory,qa	E_PAGE_RENDER_NUMBER	E_PAGE_RENDER_NUMBER	PASS
PAG-render-dimensions-wrong	candidate/evidence/PAGE_PROVENANCE.json#/rows/0/render/dimensions	inventory,qa	E_PAGE_RENDER_DIMENSIONS	E_PAGE_RENDER_DIMENSIONS	PASS
PAG-render-dpi-wrong	candidate/evidence/PAGE_PROVENANCE.json#/rows/0/render/dpi	inventory,qa	E_PAGE_RENDER_DPI	E_PAGE_RENDER_DPI	PASS
PAG-live-markdown-missing	candidate/pages/page-002.md#/physical-entry		E_PAGE_MARKDOWN_MISSING	E_PAGE_MARKDOWN_MISSING	PASS
PAG-live-render-missing	candidate/renders/source/page-002.png#/physical-entry		E_PAGE_RENDER_MISSING	E_PAGE_RENDER_MISSING	PASS
PAG-source-page-marker-wrong	candidate/pages/page-001.md#/source-page-marker	page_provenance,inventory,qa	E_PAGE_SOURCE_MARKER	E_PAGE_SOURCE_MARKER	PASS
PAG-render-marker-wrong	candidate/pages/page-001.md#/render-marker	page_provenance,inventory,qa	E_PAGE_RENDER_MARKER	E_PAGE_RENDER_MARKER	PASS
PAG-master-concatenation-wrong	candidate/RECONSTRUCTED_EN.md#/concatenation	inventory,qa	E_MASTER_CONCATENATION	E_MASTER_CONCATENATION	PASS
PAG-content-orphan	candidate/evidence/CONTENT_PROVENANCE.json#/rows/0/page_number	inventory,qa	E_CONTENT_PAGE_LINK	E_CONTENT_PAGE_LINK	PASS
PAG-content-duplicate	candidate/evidence/CONTENT_PROVENANCE.json#/rows/1/block_id	inventory,qa	E_CONTENT_DUPLICATE	E_CONTENT_DUPLICATE	PASS
PAG-content-order-wrong	candidate/evidence/CONTENT_PROVENANCE.json#/rows/1/order	inventory,qa	E_CONTENT_ORDER	E_CONTENT_ORDER	PASS
PAG-content-predecessor-wrong	candidate/evidence/CONTENT_PROVENANCE.json#/rows/1/predecessor_id	inventory,qa	E_CONTENT_PREDECESSOR	E_CONTENT_PREDECESSOR	PASS
PAG-content-successor-wrong	candidate/evidence/CONTENT_PROVENANCE.json#/rows/0/successor_id	inventory,qa	E_CONTENT_SUCCESSOR	E_CONTENT_SUCCESSOR	PASS
PAG-content-operation-fabricated	candidate/evidence/CONTENT_PROVENANCE.json#/rows/0/operations	inventory,qa	E_CONTENT_OPERATION	E_CONTENT_OPERATION	PASS
PAG-content-asset-link-fabricated	candidate/evidence/CONTENT_PROVENANCE.json#/rows/0/asset_ids	inventory,qa	E_CONTENT_ASSET_LINK	E_CONTENT_ASSET_LINK	PASS
NAV-row-missing	candidate/evidence/NAVIGATION_INVENTORY.json#/rows/0	inventory,qa	E_NAV_SET	E_NAV_SET	PASS
NAV-anchor-duplicate	candidate/evidence/NAVIGATION_INVENTORY.json#/rows/1/anchor_id	inventory,qa	E_NAV_DUPLICATE	E_NAV_DUPLICATE	PASS
NAV-anchor-id-wrong	candidate/evidence/NAVIGATION_INVENTORY.json#/rows/0/anchor_id	inventory,qa	E_NAV_ANCHOR	E_NAV_ANCHOR	PASS
NAV-source-page-wrong	candidate/evidence/NAVIGATION_INVENTORY.json#/rows/0/source_page_number	inventory,qa	E_NAV_PAGE	E_NAV_PAGE	PASS
NAV-engine-index-wrong	candidate/evidence/NAVIGATION_INVENTORY.json#/rows/0/engine_page_idx	inventory,qa	E_NAV_ENGINE_INDEX	E_NAV_ENGINE_INDEX	PASS
NAV-first-previous-nonnull	candidate/evidence/NAVIGATION_INVENTORY.json#/rows/0/previous_anchor	inventory,qa	E_NAV_FIRST_PREVIOUS	E_NAV_FIRST_PREVIOUS	PASS
NAV-last-next-nonnull	candidate/evidence/NAVIGATION_INVENTORY.json#/rows/123/next_anchor	inventory,qa	E_NAV_LAST_NEXT	E_NAV_LAST_NEXT	PASS
NAV-middle-previous-wrong	candidate/evidence/NAVIGATION_INVENTORY.json#/rows/1/previous_anchor	inventory,qa	E_NAV_PREVIOUS	E_NAV_PREVIOUS	PASS
NAV-middle-next-wrong	candidate/evidence/NAVIGATION_INVENTORY.json#/rows/1/next_anchor	inventory,qa	E_NAV_NEXT	E_NAV_NEXT	PASS
NAV-dangling-link	candidate/evidence/NAVIGATION_INVENTORY.json#/rows/1/next_anchor	inventory,qa	E_NAV_DANGLING	E_NAV_DANGLING	PASS
NAV-markdown-path-wrong	candidate/evidence/NAVIGATION_INVENTORY.json#/rows/0/page_markdown_path	inventory,qa	E_NAV_MARKDOWN_PATH	E_NAV_MARKDOWN_PATH	PASS
NAV-render-path-wrong	candidate/evidence/NAVIGATION_INVENTORY.json#/rows/0/source_render_path	inventory,qa	E_NAV_RENDER_PATH	E_NAV_RENDER_PATH	PASS
NAV-render-hash-wrong	candidate/evidence/NAVIGATION_INVENTORY.json#/rows/0/source_render_sha256	inventory,qa	E_NAV_RENDER_HASH	E_NAV_RENDER_HASH	PASS
NAV-role-wrong	candidate/evidence/NAVIGATION_INVENTORY.json#/rows/0/contract_role	inventory,qa	E_NAV_ROLE	E_NAV_ROLE	PASS
NAV-closure-promoted	candidate/evidence/NAVIGATION_INVENTORY.json#/rows/0/closure_state	inventory,qa	E_NAV_CLOSURE	E_NAV_CLOSURE	PASS
AST-row-missing	candidate/evidence/ASSET_PROVENANCE.json#/rows/0	inventory,qa	E_ASSET_SET	E_ASSET_SET	PASS
AST-id-duplicate	candidate/evidence/ASSET_PROVENANCE.json#/rows/1/asset_id	inventory,qa	E_ASSET_ID_DUPLICATE	E_ASSET_ID_DUPLICATE	PASS
AST-path-duplicate	candidate/evidence/ASSET_PROVENANCE.json#/rows/1/engine_relative_path	inventory,qa	E_ASSET_PATH_DUPLICATE	E_ASSET_PATH_DUPLICATE	PASS
AST-hash-duplicate	candidate/evidence/ASSET_PROVENANCE.json#/rows/1/sha256	inventory,qa	E_ASSET_HASH_DUPLICATE	E_ASSET_HASH_DUPLICATE	PASS
AST-live-bytes-wrong	candidate/engine/payload-001.bin#/bytes	inventory,qa	E_ASSET_BYTES	E_ASSET_BYTES	PASS
AST-live-hash-wrong	candidate/engine/payload-001.bin#/sha256	inventory,qa	E_ASSET_HASH	E_ASSET_HASH	PASS
AST-engine-path-missing	candidate/evidence/ASSET_PROVENANCE.json#/rows/0/engine_relative_path	inventory,qa	E_ASSET_ENGINE_MISSING	E_ASSET_ENGINE_MISSING	PASS
AST-engine-path-wrong	candidate/evidence/ASSET_PROVENANCE.json#/rows/0/engine_relative_path	inventory,qa	E_ASSET_ENGINE_PATH	E_ASSET_ENGINE_PATH	PASS
AST-recovery-binding-wrong	candidate/evidence/ASSET_PROVENANCE.json#/rows/0/recovery_manifest_binding	inventory,qa	E_ASSET_RECOVERY_BINDING	E_ASSET_RECOVERY_BINDING	PASS
AST-reference-total-wrong	candidate/evidence/ASSET_PROVENANCE.json#/referenced	inventory,qa	E_ASSET_REFERENCE_TOTAL	E_ASSET_REFERENCE_TOTAL	PASS
AST-unreferenced-count-wrong	candidate/evidence/ASSET_PROVENANCE.json#/unreferenced	inventory,qa	E_ASSET_UNREFERENCED_COUNT	E_ASSET_UNREFERENCED_COUNT	PASS
AST-reference-count-outside-zero-one	candidate/evidence/ASSET_PROVENANCE.json#/rows/0/markdown_reference_count	inventory,qa	E_ASSET_REFERENCE_COUNT	E_ASSET_REFERENCE_COUNT	PASS
AST-occurrence-missing	candidate/evidence/ASSET_PROVENANCE.json#/rows/0/markdown_reference_locations	inventory,qa	E_ASSET_OCCURRENCE_SET	E_ASSET_OCCURRENCE_SET	PASS
AST-occurrence-duplicate	candidate/evidence/ASSET_PROVENANCE.json#/rows/1/markdown_reference_locations	inventory,qa	E_ASSET_OCCURRENCE_DUPLICATE	E_ASSET_OCCURRENCE_DUPLICATE	PASS
AST-markdown-path-wrong	candidate/evidence/ASSET_PROVENANCE.json#/rows/0/markdown_reference_locations/0/markdown_path	inventory,qa	E_ASSET_MARKDOWN_PATH	E_ASSET_MARKDOWN_PATH	PASS
AST-target-absent-from-markdown	candidate/evidence/ASSET_PROVENANCE.json#/rows/0/markdown_reference_locations/0/target	inventory,qa	E_ASSET_TARGET_RESOLUTION	E_ASSET_TARGET_RESOLUTION	PASS
AST-ownership-nonnull	candidate/evidence/ASSET_PROVENANCE.json#/rows/0/ownership	inventory,qa	E_ASSET_OWNERSHIP	E_ASSET_OWNERSHIP	PASS
AST-closure-promoted	candidate/evidence/ASSET_PROVENANCE.json#/rows/0/closure_state	inventory,qa	E_ASSET_CLOSURE	E_ASSET_CLOSURE	PASS
AST-finding-wrong	candidate/evidence/ASSET_PROVENANCE.json#/rows/0/finding	inventory,qa	E_ASSET_FINDING	E_ASSET_FINDING	PASS
AST-engine-image-cardinality-wrong	candidate/evidence/ASSET_PROVENANCE.json#/rows/0/engine_evidence/engine_image_count	inventory,qa	E_ASSET_ENGINE_COUNT	E_ASSET_ENGINE_COUNT	PASS
AST-mime-wrong	candidate/evidence/ASSET_PROVENANCE.json#/rows/0/mime	inventory,qa	E_ASSET_MIME	E_ASSET_MIME	PASS
SEM-entity-ordinal-gap	candidate/evidence/ENTITY_INVENTORY.json#/rows/1/ordinal	inventory,qa	E_ENTITY_ORDINALS	E_ENTITY_ORDINALS	PASS
SEM-entity-id-duplicate	candidate/evidence/ENTITY_INVENTORY.json#/rows/1/id	inventory,qa	E_ENTITY_ID	E_ENTITY_ID	PASS
SEM-handout-ordinal-gap	candidate/evidence/HANDOUT_INVENTORY.json#/rows/1/ordinal	inventory,qa	E_HANDOUT_ORDINALS	E_HANDOUT_ORDINALS	PASS
SEM-handout-id-duplicate	candidate/evidence/HANDOUT_INVENTORY.json#/rows/1/id	inventory,qa	E_HANDOUT_ID	E_HANDOUT_ID	PASS
SEM-entity-handout-inequality	candidate/evidence/ENTITY_INVENTORY.json#/rows/0/disposition	inventory,qa	E_ENTITY_HANDOUT_EQUALITY	E_ENTITY_HANDOUT_EQUALITY	PASS
SEM-required-count-wrong	candidate/evidence/HANDOUT_INVENTORY.json#/required_count	inventory,qa	E_HANDOUT_REQUIRED_COUNT	E_HANDOUT_REQUIRED_COUNT	PASS
SEM-label-wrong	candidate/evidence/HANDOUT_INVENTORY.json#/rows/0/label	inventory,qa	E_HANDOUT_LABEL	E_HANDOUT_LABEL	PASS
SEM-page-range-wrong	candidate/evidence/HANDOUT_INVENTORY.json#/rows/0/range	inventory,qa	E_HANDOUT_PAGE_RANGE	E_HANDOUT_PAGE_RANGE	PASS
SEM-entity-closure-promoted	candidate/evidence/ENTITY_INVENTORY.json#/rows/0/review_state	inventory,qa	E_ENTITY_CLOSURE	E_ENTITY_CLOSURE	PASS
SEM-mode-page-gap	candidate/evidence/CONTENT_MODE_REVIEW.json#/rows/4	inventory,qa	E_MODE_PAGE_SET	E_MODE_PAGE_SET	PASS
SEM-mode-row-duplicate	candidate/evidence/CONTENT_MODE_REVIEW.json#/rows/1/page	inventory,qa	E_MODE_DUPLICATE	E_MODE_DUPLICATE	PASS
SEM-mode-review-promoted	candidate/evidence/CONTENT_MODE_REVIEW.json#/rows/0/review_state	inventory,qa	E_MODE_REVIEW_STATE	E_MODE_REVIEW_STATE	PASS
SEM-reference-only-row-added	candidate/evidence/REFERENCE_ONLY_AUDIT.json#/rows/0	inventory,qa	E_REFERENCE_ONLY_ROWS	E_REFERENCE_ONLY_ROWS	PASS
SEM-historical-material-true	candidate/evidence/REFERENCE_ONLY_AUDIT.json#/historical_material_opened	inventory,qa	E_REFERENCE_ONLY_HISTORY	E_REFERENCE_ONLY_HISTORY	PASS
SEM-map-role-count-wrong	candidate/evidence/NAVIGATION_INVENTORY.json#/rows/39/semantic_role	inventory,qa	E_ROLE_MAP_COUNT	E_ROLE_MAP_COUNT	PASS
SEM-pregen-role-count-wrong	candidate/evidence/NAVIGATION_INVENTORY.json#/rows/46/semantic_role	inventory,qa	E_ROLE_PREGEN_COUNT	E_ROLE_PREGEN_COUNT	PASS
SEM-back-cover-role-count-wrong	candidate/evidence/NAVIGATION_INVENTORY.json#/rows/59/semantic_role	inventory,qa	E_ROLE_BACK_COVER_COUNT	E_ROLE_BACK_COVER_COUNT	PASS
SEM-handout-role-count-wrong	candidate/evidence/NAVIGATION_INVENTORY.json#/rows/0/semantic_role	inventory,qa	E_ROLE_HANDOUT_COUNT	E_ROLE_HANDOUT_COUNT	PASS
CMD-action-missing	candidate/evidence/COMMANDS.json#/actions/2	inventory,qa	E_COMMAND_ACTIONS	E_COMMAND_ACTIONS	PASS
CMD-action-duplicate	candidate/evidence/COMMANDS.json#/actions/-	inventory,qa	E_COMMAND_ACTIONS	E_COMMAND_ACTIONS	PASS
CMD-action-extra	candidate/evidence/COMMANDS.json#/actions/-	inventory,qa	E_COMMAND_ACTIONS	E_COMMAND_ACTIONS	PASS
CMD-action-reordered	candidate/evidence/COMMANDS.json#/actions/0	inventory,qa	E_COMMAND_ACTIONS	E_COMMAND_ACTIONS	PASS
CMD-state-promoted	candidate/evidence/COMMANDS.json#/state	inventory,qa	E_COMMAND_STATE	E_COMMAND_STATE	PASS
CMD-external-locator-used	candidate/evidence/COMMANDS.json#/external_locator	inventory,qa	E_COMMAND_EXTERNAL_SOURCE	E_COMMAND_EXTERNAL_SOURCE	PASS
CMD-flag-build_invoked-missing	candidate/evidence/COMMANDS.json#/flags/build_invoked	inventory,qa	E_COMMAND_FLAG_BUILD_INVOKED	E_COMMAND_FLAG_BUILD_INVOKED	PASS
CMD-flag-build_invoked-true	candidate/evidence/COMMANDS.json#/flags/build_invoked	inventory,qa	E_COMMAND_FLAG_BUILD_INVOKED	E_COMMAND_FLAG_BUILD_INVOKED	PASS
CMD-flag-mineru_invoked-missing	candidate/evidence/COMMANDS.json#/flags/mineru_invoked	inventory,qa	E_COMMAND_FLAG_MINERU_INVOKED	E_COMMAND_FLAG_MINERU_INVOKED	PASS
CMD-flag-mineru_invoked-true	candidate/evidence/COMMANDS.json#/flags/mineru_invoked	inventory,qa	E_COMMAND_FLAG_MINERU_INVOKED	E_COMMAND_FLAG_MINERU_INVOKED	PASS
CMD-flag-ocr_invoked-missing	candidate/evidence/COMMANDS.json#/flags/ocr_invoked	inventory,qa	E_COMMAND_FLAG_OCR_INVOKED	E_COMMAND_FLAG_OCR_INVOKED	PASS
CMD-flag-ocr_invoked-true	candidate/evidence/COMMANDS.json#/flags/ocr_invoked	inventory,qa	E_COMMAND_FLAG_OCR_INVOKED	E_COMMAND_FLAG_OCR_INVOKED	PASS
CMD-flag-gpu_or_model_invoked-missing	candidate/evidence/COMMANDS.json#/flags/gpu_or_model_invoked	inventory,qa	E_COMMAND_FLAG_GPU_OR_MODEL_INVOKED	E_COMMAND_FLAG_GPU_OR_MODEL_INVOKED	PASS
CMD-flag-gpu_or_model_invoked-true	candidate/evidence/COMMANDS.json#/flags/gpu_or_model_invoked	inventory,qa	E_COMMAND_FLAG_GPU_OR_MODEL_INVOKED	E_COMMAND_FLAG_GPU_OR_MODEL_INVOKED	PASS
CMD-flag-network_invoked-missing	candidate/evidence/COMMANDS.json#/flags/network_invoked	inventory,qa	E_COMMAND_FLAG_NETWORK_INVOKED	E_COMMAND_FLAG_NETWORK_INVOKED	PASS
CMD-flag-network_invoked-true	candidate/evidence/COMMANDS.json#/flags/network_invoked	inventory,qa	E_COMMAND_FLAG_NETWORK_INVOKED	E_COMMAND_FLAG_NETWORK_INVOKED	PASS
CMD-flag-external_source_used-missing	candidate/evidence/COMMANDS.json#/flags/external_source_used	inventory,qa	E_COMMAND_FLAG_EXTERNAL_SOURCE_USED	E_COMMAND_FLAG_EXTERNAL_SOURCE_USED	PASS
CMD-flag-external_source_used-true	candidate/evidence/COMMANDS.json#/flags/external_source_used	inventory,qa	E_COMMAND_FLAG_EXTERNAL_SOURCE_USED	E_COMMAND_FLAG_EXTERNAL_SOURCE_USED	PASS
CMD-argument-source_flag-missing	candidate/evidence/COMMANDS.json#/records/0/source_flag	inventory,qa	E_COMMAND_ARGUMENT_SOURCE_FLAG	E_COMMAND_ARGUMENT_SOURCE_FLAG	PASS
CMD-argument-source_flag-wrong	candidate/evidence/COMMANDS.json#/records/0/source_flag	inventory,qa	E_COMMAND_ARGUMENT_SOURCE_FLAG	E_COMMAND_ARGUMENT_SOURCE_FLAG	PASS
CMD-argument-run_root_flag-missing	candidate/evidence/COMMANDS.json#/records/0/run_root_flag	inventory,qa	E_COMMAND_ARGUMENT_RUN_ROOT_FLAG	E_COMMAND_ARGUMENT_RUN_ROOT_FLAG	PASS
CMD-argument-run_root_flag-wrong	candidate/evidence/COMMANDS.json#/records/0/run_root_flag	inventory,qa	E_COMMAND_ARGUMENT_RUN_ROOT_FLAG	E_COMMAND_ARGUMENT_RUN_ROOT_FLAG	PASS
CMD-argument-source_relative_path-missing	candidate/evidence/COMMANDS.json#/records/0/source_relative_path	inventory,qa	E_COMMAND_ARGUMENT_SOURCE_RELATIVE_PATH	E_COMMAND_ARGUMENT_SOURCE_RELATIVE_PATH	PASS
CMD-argument-source_relative_path-wrong	candidate/evidence/COMMANDS.json#/records/0/source_relative_path	inventory,qa	E_COMMAND_ARGUMENT_SOURCE_RELATIVE_PATH	E_COMMAND_ARGUMENT_SOURCE_RELATIVE_PATH	PASS
CMD-count-pages-missing	candidate/evidence/COMMANDS.json#/counts/pages	inventory,qa	E_COMMAND_COUNTS_PAGES	E_COMMAND_COUNTS_PAGES	PASS
CMD-count-pages-wrong	candidate/evidence/COMMANDS.json#/counts/pages	inventory,qa	E_COMMAND_COUNTS_PAGES	E_COMMAND_COUNTS_PAGES	PASS
CMD-count-renders-missing	candidate/evidence/COMMANDS.json#/counts/renders	inventory,qa	E_COMMAND_COUNTS_RENDERS	E_COMMAND_COUNTS_RENDERS	PASS
CMD-count-renders-wrong	candidate/evidence/COMMANDS.json#/counts/renders	inventory,qa	E_COMMAND_COUNTS_RENDERS	E_COMMAND_COUNTS_RENDERS	PASS
CMD-count-contact_sheets-missing	candidate/evidence/COMMANDS.json#/counts/contact_sheets	inventory,qa	E_COMMAND_COUNTS_CONTACT_SHEETS	E_COMMAND_COUNTS_CONTACT_SHEETS	PASS
CMD-count-contact_sheets-wrong	candidate/evidence/COMMANDS.json#/counts/contact_sheets	inventory,qa	E_COMMAND_COUNTS_CONTACT_SHEETS	E_COMMAND_COUNTS_CONTACT_SHEETS	PASS
CMD-count-handouts-missing	candidate/evidence/COMMANDS.json#/counts/handouts	inventory,qa	E_COMMAND_COUNTS_HANDOUTS	E_COMMAND_COUNTS_HANDOUTS	PASS
CMD-count-handouts-wrong	candidate/evidence/COMMANDS.json#/counts/handouts	inventory,qa	E_COMMAND_COUNTS_HANDOUTS	E_COMMAND_COUNTS_HANDOUTS	PASS
CMD-count-maps-missing	candidate/evidence/COMMANDS.json#/counts/maps	inventory,qa	E_COMMAND_COUNTS_MAPS	E_COMMAND_COUNTS_MAPS	PASS
CMD-count-maps-wrong	candidate/evidence/COMMANDS.json#/counts/maps	inventory,qa	E_COMMAND_COUNTS_MAPS	E_COMMAND_COUNTS_MAPS	PASS
CMD-count-pregens-missing	candidate/evidence/COMMANDS.json#/counts/pregens	inventory,qa	E_COMMAND_COUNTS_PREGENS	E_COMMAND_COUNTS_PREGENS	PASS
CMD-count-pregens-wrong	candidate/evidence/COMMANDS.json#/counts/pregens	inventory,qa	E_COMMAND_COUNTS_PREGENS	E_COMMAND_COUNTS_PREGENS	PASS
CMD-count-back_cover-missing	candidate/evidence/COMMANDS.json#/counts/back_cover	inventory,qa	E_COMMAND_COUNTS_BACK_COVER	E_COMMAND_COUNTS_BACK_COVER	PASS
CMD-count-back_cover-wrong	candidate/evidence/COMMANDS.json#/counts/back_cover	inventory,qa	E_COMMAND_COUNTS_BACK_COVER	E_COMMAND_COUNTS_BACK_COVER	PASS
CMD-count-assets-missing	candidate/evidence/COMMANDS.json#/counts/assets	inventory,qa	E_COMMAND_COUNTS_ASSETS	E_COMMAND_COUNTS_ASSETS	PASS
CMD-count-assets-wrong	candidate/evidence/COMMANDS.json#/counts/assets	inventory,qa	E_COMMAND_COUNTS_ASSETS	E_COMMAND_COUNTS_ASSETS	PASS
CMD-count-referenced_assets-missing	candidate/evidence/COMMANDS.json#/counts/referenced_assets	inventory,qa	E_COMMAND_COUNTS_REFERENCED_ASSETS	E_COMMAND_COUNTS_REFERENCED_ASSETS	PASS
CMD-count-referenced_assets-wrong	candidate/evidence/COMMANDS.json#/counts/referenced_assets	inventory,qa	E_COMMAND_COUNTS_REFERENCED_ASSETS	E_COMMAND_COUNTS_REFERENCED_ASSETS	PASS
CMD-count-unreferenced_assets-missing	candidate/evidence/COMMANDS.json#/counts/unreferenced_assets	inventory,qa	E_COMMAND_COUNTS_UNREFERENCED_ASSETS	E_COMMAND_COUNTS_UNREFERENCED_ASSETS	PASS
CMD-count-unreferenced_assets-wrong	candidate/evidence/COMMANDS.json#/counts/unreferenced_assets	inventory,qa	E_COMMAND_COUNTS_UNREFERENCED_ASSETS	E_COMMAND_COUNTS_UNREFERENCED_ASSETS	PASS
CMD-count-markdown_references-missing	candidate/evidence/COMMANDS.json#/counts/markdown_references	inventory,qa	E_COMMAND_COUNTS_MARKDOWN_REFERENCES	E_COMMAND_COUNTS_MARKDOWN_REFERENCES	PASS
CMD-count-markdown_references-wrong	candidate/evidence/COMMANDS.json#/counts/markdown_references	inventory,qa	E_COMMAND_COUNTS_MARKDOWN_REFERENCES	E_COMMAND_COUNTS_MARKDOWN_REFERENCES	PASS
CMD-sheet-count-wrong	candidate/evidence/COMMANDS.json#/sheets	inventory,qa	E_COMMAND_SHEET_COUNT	E_COMMAND_SHEET_COUNT	PASS
CMD-sheet-coverage-wrong	candidate/evidence/COMMANDS.json#/sheets/0/pages/-	inventory,qa	E_COMMAND_SHEET_COVERAGE	E_COMMAND_SHEET_COVERAGE	PASS
CMD-sheet-missing	candidate/evidence/COMMANDS.json#/sheets/30	inventory,qa	E_COMMAND_SHEET_SET	E_COMMAND_SHEET_SET	PASS
CMD-sheet-duplicate	candidate/evidence/COMMANDS.json#/sheets/1	inventory,qa	E_COMMAND_SHEET_SET	E_COMMAND_SHEET_SET	PASS
CMD-sheet-id-wrong	candidate/evidence/COMMANDS.json#/sheets/0/sheet_id	inventory,qa	E_COMMAND_SHEET_ID	E_COMMAND_SHEET_ID	PASS
CMD-sheet-path-sequence-wrong	candidate/evidence/COMMANDS.json#/sheets/0/path	inventory,qa	E_COMMAND_SHEET_PATH	E_COMMAND_SHEET_PATH	PASS
CMD-sheet-grid-wrong	candidate/evidence/COMMANDS.json#/sheets/0/grid	inventory,qa	E_COMMAND_SHEET_GRID	E_COMMAND_SHEET_GRID	PASS
CMD-sheet-hash-wrong	candidate/evidence/COMMANDS.json#/sheets/0/sha256	inventory,qa	E_COMMAND_SHEET_HASH	E_COMMAND_SHEET_HASH	PASS
CMD-flattened-page-missing	candidate/evidence/COMMANDS.json#/sheets/0/pages/0	inventory,qa	E_COMMAND_SHEET_PAGES	E_COMMAND_SHEET_PAGES	PASS
CMD-flattened-page-duplicate	candidate/evidence/COMMANDS.json#/sheets/1/pages/0	inventory,qa	E_COMMAND_SHEET_PAGES	E_COMMAND_SHEET_PAGES	PASS
CMD-flattened-page-order-wrong	candidate/evidence/COMMANDS.json#/sheets/0/pages	inventory,qa	E_COMMAND_SHEET_PAGE_ORDER	E_COMMAND_SHEET_PAGE_ORDER	PASS
CMD-render-path-wrong	candidate/evidence/COMMANDS.json#/sheets/0/page_renders/0/path	inventory,qa	E_COMMAND_RENDER_PATH	E_COMMAND_RENDER_PATH	PASS
CMD-render-hash-wrong	candidate/evidence/COMMANDS.json#/sheets/0/page_renders/0/sha256	inventory,qa	E_COMMAND_RENDER_HASH	E_COMMAND_RENDER_HASH	PASS
CMD-page-render-mapping-disagrees	candidate/evidence/COMMANDS.json#/page_renders/0/page_number	inventory,qa	E_COMMAND_PAGE_RENDER_MAP	E_COMMAND_PAGE_RENDER_MAP	PASS
CMD-verify-determinism-false	candidate/evidence/COMMANDS.json#/verify_deterministic	inventory,qa	E_COMMAND_DETERMINISM	E_COMMAND_DETERMINISM	PASS
QAV-top-asset_count-missing	candidate/RECONSTRUCTED_EN.qa.json#/asset_count		E_SHAPE_QA	E_SHAPE_QA	PASS
QAV-top-block_count-missing	candidate/RECONSTRUCTED_EN.qa.json#/block_count		E_SHAPE_QA	E_SHAPE_QA	PASS
QAV-top-contact_sheet_count-missing	candidate/RECONSTRUCTED_EN.qa.json#/contact_sheet_count		E_SHAPE_QA	E_SHAPE_QA	PASS
QAV-top-contract_sha256-missing	candidate/RECONSTRUCTED_EN.qa.json#/contract_sha256		E_SHAPE_QA	E_SHAPE_QA	PASS
QAV-top-counts-missing	candidate/RECONSTRUCTED_EN.qa.json#/counts		E_SHAPE_QA	E_SHAPE_QA	PASS
QAV-top-gate_results-missing	candidate/RECONSTRUCTED_EN.qa.json#/gate_results		E_SHAPE_QA	E_SHAPE_QA	PASS
QAV-top-handout_count-missing	candidate/RECONSTRUCTED_EN.qa.json#/handout_count		E_SHAPE_QA	E_SHAPE_QA	PASS
QAV-top-historical_material_opened-missing	candidate/RECONSTRUCTED_EN.qa.json#/historical_material_opened		E_SHAPE_QA	E_SHAPE_QA	PASS
QAV-top-main_scripts_invoked-missing	candidate/RECONSTRUCTED_EN.qa.json#/main_scripts_invoked		E_SHAPE_QA	E_SHAPE_QA	PASS
QAV-top-navigation_anchor_count-missing	candidate/RECONSTRUCTED_EN.qa.json#/navigation_anchor_count		E_SHAPE_QA	E_SHAPE_QA	PASS
QAV-top-open_blocker_count-missing	candidate/RECONSTRUCTED_EN.qa.json#/open_blocker_count		E_SHAPE_QA	E_SHAPE_QA	PASS
QAV-top-output_inventory-missing	candidate/RECONSTRUCTED_EN.qa.json#/output_inventory		E_SHAPE_QA	E_SHAPE_QA	PASS
QAV-top-output_inventory_count-missing	candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_count		E_SHAPE_QA	E_SHAPE_QA	PASS
QAV-top-output_inventory_rule-missing	candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_rule		E_SHAPE_QA	E_SHAPE_QA	PASS
QAV-top-output_inventory_sha256-missing	candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256		E_SHAPE_QA	E_SHAPE_QA	PASS
QAV-top-page_count-missing	candidate/RECONSTRUCTED_EN.qa.json#/page_count		E_SHAPE_QA	E_SHAPE_QA	PASS
QAV-top-recovery_evidence_sha256-missing	candidate/RECONSTRUCTED_EN.qa.json#/recovery_evidence_sha256		E_SHAPE_QA	E_SHAPE_QA	PASS
QAV-top-recovery_manifest_sha256-missing	candidate/RECONSTRUCTED_EN.qa.json#/recovery_manifest_sha256		E_SHAPE_QA	E_SHAPE_QA	PASS
QAV-top-referenced_asset_count-missing	candidate/RECONSTRUCTED_EN.qa.json#/referenced_asset_count		E_SHAPE_QA	E_SHAPE_QA	PASS
QAV-top-schema-missing	candidate/RECONSTRUCTED_EN.qa.json#/schema		E_SHAPE_QA	E_SHAPE_QA	PASS
QAV-top-source_sha256-missing	candidate/RECONSTRUCTED_EN.qa.json#/source_sha256		E_SHAPE_QA	E_SHAPE_QA	PASS
QAV-top-state-missing	candidate/RECONSTRUCTED_EN.qa.json#/state		E_SHAPE_QA	E_SHAPE_QA	PASS
QAV-top-unreferenced_asset_count-missing	candidate/RECONSTRUCTED_EN.qa.json#/unreferenced_asset_count		E_SHAPE_QA	E_SHAPE_QA	PASS
QAV-top-extra	candidate/RECONSTRUCTED_EN.qa.json#/unexpected		E_SHAPE_QA	E_SHAPE_QA	PASS
QAV-state-promoted	candidate/RECONSTRUCTED_EN.qa.json#/state		E_QA_STATE	E_QA_STATE	PASS
QAV-authority-contract	candidate/RECONSTRUCTED_EN.qa.json#/contract_sha256		E_QA_CONTRACT_HASH	E_QA_CONTRACT_HASH	PASS
QAV-authority-source	candidate/RECONSTRUCTED_EN.qa.json#/source_sha256		E_QA_SOURCE_HASH	E_QA_SOURCE_HASH	PASS
QAV-authority-recovery-manifest	candidate/RECONSTRUCTED_EN.qa.json#/recovery_manifest_sha256		E_QA_RECOVERY_MANIFEST_HASH	E_QA_RECOVERY_MANIFEST_HASH	PASS
QAV-authority-recovery-evidence	candidate/RECONSTRUCTED_EN.qa.json#/recovery_evidence_sha256		E_QA_RECOVERY_EVIDENCE_HASH	E_QA_RECOVERY_EVIDENCE_HASH	PASS
QAV-scalar-page_count-wrong	candidate/RECONSTRUCTED_EN.qa.json#/page_count		E_QA_SCALAR_PAGE_COUNT	E_QA_SCALAR_PAGE_COUNT	PASS
QAV-scalar-handout_count-wrong	candidate/RECONSTRUCTED_EN.qa.json#/handout_count		E_QA_SCALAR_HANDOUT_COUNT	E_QA_SCALAR_HANDOUT_COUNT	PASS
QAV-scalar-block_count-wrong	candidate/RECONSTRUCTED_EN.qa.json#/block_count		E_QA_SCALAR_BLOCK_COUNT	E_QA_SCALAR_BLOCK_COUNT	PASS
QAV-scalar-asset_count-wrong	candidate/RECONSTRUCTED_EN.qa.json#/asset_count		E_QA_SCALAR_ASSET_COUNT	E_QA_SCALAR_ASSET_COUNT	PASS
QAV-scalar-contact_sheet_count-wrong	candidate/RECONSTRUCTED_EN.qa.json#/contact_sheet_count		E_QA_SCALAR_CONTACT_SHEET_COUNT	E_QA_SCALAR_CONTACT_SHEET_COUNT	PASS
QAV-scalar-navigation_anchor_count-wrong	candidate/RECONSTRUCTED_EN.qa.json#/navigation_anchor_count		E_QA_SCALAR_NAVIGATION_ANCHOR_COUNT	E_QA_SCALAR_NAVIGATION_ANCHOR_COUNT	PASS
QAV-scalar-referenced_asset_count-wrong	candidate/RECONSTRUCTED_EN.qa.json#/referenced_asset_count		E_QA_SCALAR_REFERENCED_ASSET_COUNT	E_QA_SCALAR_REFERENCED_ASSET_COUNT	PASS
QAV-scalar-unreferenced_asset_count-wrong	candidate/RECONSTRUCTED_EN.qa.json#/unreferenced_asset_count		E_QA_SCALAR_UNREFERENCED_ASSET_COUNT	E_QA_SCALAR_UNREFERENCED_ASSET_COUNT	PASS
QAV-scalar-open_blocker_count-wrong	candidate/RECONSTRUCTED_EN.qa.json#/open_blocker_count		E_QA_SCALAR_OPEN_BLOCKER_COUNT	E_QA_SCALAR_OPEN_BLOCKER_COUNT	PASS
QAV-counts-assets-missing	candidate/RECONSTRUCTED_EN.qa.json#/counts/assets		E_QA_COUNTS_ASSETS	E_QA_COUNTS_ASSETS	PASS
QAV-counts-assets-wrong	candidate/RECONSTRUCTED_EN.qa.json#/counts/assets		E_QA_COUNTS_ASSETS	E_QA_COUNTS_ASSETS	PASS
QAV-counts-back_cover-missing	candidate/RECONSTRUCTED_EN.qa.json#/counts/back_cover		E_QA_COUNTS_BACK_COVER	E_QA_COUNTS_BACK_COVER	PASS
QAV-counts-back_cover-wrong	candidate/RECONSTRUCTED_EN.qa.json#/counts/back_cover		E_QA_COUNTS_BACK_COVER	E_QA_COUNTS_BACK_COVER	PASS
QAV-counts-contact_sheets-missing	candidate/RECONSTRUCTED_EN.qa.json#/counts/contact_sheets		E_QA_COUNTS_CONTACT_SHEETS	E_QA_COUNTS_CONTACT_SHEETS	PASS
QAV-counts-contact_sheets-wrong	candidate/RECONSTRUCTED_EN.qa.json#/counts/contact_sheets		E_QA_COUNTS_CONTACT_SHEETS	E_QA_COUNTS_CONTACT_SHEETS	PASS
QAV-counts-engine_images-missing	candidate/RECONSTRUCTED_EN.qa.json#/counts/engine_images		E_QA_COUNTS_ENGINE_IMAGES	E_QA_COUNTS_ENGINE_IMAGES	PASS
QAV-counts-engine_images-wrong	candidate/RECONSTRUCTED_EN.qa.json#/counts/engine_images		E_QA_COUNTS_ENGINE_IMAGES	E_QA_COUNTS_ENGINE_IMAGES	PASS
QAV-counts-engine_payload-missing	candidate/RECONSTRUCTED_EN.qa.json#/counts/engine_payload		E_QA_COUNTS_ENGINE_PAYLOAD	E_QA_COUNTS_ENGINE_PAYLOAD	PASS
QAV-counts-engine_payload-wrong	candidate/RECONSTRUCTED_EN.qa.json#/counts/engine_payload		E_QA_COUNTS_ENGINE_PAYLOAD	E_QA_COUNTS_ENGINE_PAYLOAD	PASS
QAV-counts-handouts-missing	candidate/RECONSTRUCTED_EN.qa.json#/counts/handouts		E_QA_COUNTS_HANDOUTS	E_QA_COUNTS_HANDOUTS	PASS
QAV-counts-handouts-wrong	candidate/RECONSTRUCTED_EN.qa.json#/counts/handouts		E_QA_COUNTS_HANDOUTS	E_QA_COUNTS_HANDOUTS	PASS
QAV-counts-maps-missing	candidate/RECONSTRUCTED_EN.qa.json#/counts/maps		E_QA_COUNTS_MAPS	E_QA_COUNTS_MAPS	PASS
QAV-counts-maps-wrong	candidate/RECONSTRUCTED_EN.qa.json#/counts/maps		E_QA_COUNTS_MAPS	E_QA_COUNTS_MAPS	PASS
QAV-counts-navigation_anchors-missing	candidate/RECONSTRUCTED_EN.qa.json#/counts/navigation_anchors		E_QA_COUNTS_NAVIGATION_ANCHORS	E_QA_COUNTS_NAVIGATION_ANCHORS	PASS
QAV-counts-navigation_anchors-wrong	candidate/RECONSTRUCTED_EN.qa.json#/counts/navigation_anchors		E_QA_COUNTS_NAVIGATION_ANCHORS	E_QA_COUNTS_NAVIGATION_ANCHORS	PASS
QAV-counts-open_blockers-missing	candidate/RECONSTRUCTED_EN.qa.json#/counts/open_blockers		E_QA_COUNTS_OPEN_BLOCKERS	E_QA_COUNTS_OPEN_BLOCKERS	PASS
QAV-counts-open_blockers-wrong	candidate/RECONSTRUCTED_EN.qa.json#/counts/open_blockers		E_QA_COUNTS_OPEN_BLOCKERS	E_QA_COUNTS_OPEN_BLOCKERS	PASS
QAV-counts-pages-missing	candidate/RECONSTRUCTED_EN.qa.json#/counts/pages		E_QA_COUNTS_PAGES	E_QA_COUNTS_PAGES	PASS
QAV-counts-pages-wrong	candidate/RECONSTRUCTED_EN.qa.json#/counts/pages		E_QA_COUNTS_PAGES	E_QA_COUNTS_PAGES	PASS
QAV-counts-pregens-missing	candidate/RECONSTRUCTED_EN.qa.json#/counts/pregens		E_QA_COUNTS_PREGENS	E_QA_COUNTS_PREGENS	PASS
QAV-counts-pregens-wrong	candidate/RECONSTRUCTED_EN.qa.json#/counts/pregens		E_QA_COUNTS_PREGENS	E_QA_COUNTS_PREGENS	PASS
QAV-counts-referenced_assets-missing	candidate/RECONSTRUCTED_EN.qa.json#/counts/referenced_assets		E_QA_COUNTS_REFERENCED_ASSETS	E_QA_COUNTS_REFERENCED_ASSETS	PASS
QAV-counts-referenced_assets-wrong	candidate/RECONSTRUCTED_EN.qa.json#/counts/referenced_assets		E_QA_COUNTS_REFERENCED_ASSETS	E_QA_COUNTS_REFERENCED_ASSETS	PASS
QAV-counts-renders-missing	candidate/RECONSTRUCTED_EN.qa.json#/counts/renders		E_QA_COUNTS_RENDERS	E_QA_COUNTS_RENDERS	PASS
QAV-counts-renders-wrong	candidate/RECONSTRUCTED_EN.qa.json#/counts/renders		E_QA_COUNTS_RENDERS	E_QA_COUNTS_RENDERS	PASS
QAV-counts-unreferenced_assets-missing	candidate/RECONSTRUCTED_EN.qa.json#/counts/unreferenced_assets		E_QA_COUNTS_UNREFERENCED_ASSETS	E_QA_COUNTS_UNREFERENCED_ASSETS	PASS
QAV-counts-unreferenced_assets-wrong	candidate/RECONSTRUCTED_EN.qa.json#/counts/unreferenced_assets		E_QA_COUNTS_UNREFERENCED_ASSETS	E_QA_COUNTS_UNREFERENCED_ASSETS	PASS
QAV-gate-asset_conservation-missing	candidate/RECONSTRUCTED_EN.qa.json#/gate_results/asset_conservation		E_QA_GATE_ASSET_CONSERVATION	E_QA_GATE_ASSET_CONSERVATION	PASS
QAV-gate-contact_sheet_coverage-missing	candidate/RECONSTRUCTED_EN.qa.json#/gate_results/contact_sheet_coverage		E_QA_GATE_CONTACT_SHEET_COVERAGE	E_QA_GATE_CONTACT_SHEET_COVERAGE	PASS
QAV-gate-navigation_anchors-missing	candidate/RECONSTRUCTED_EN.qa.json#/gate_results/navigation_anchors		E_QA_GATE_NAVIGATION_ANCHORS	E_QA_GATE_NAVIGATION_ANCHORS	PASS
QAV-gate-page_1_5_modes-missing	candidate/RECONSTRUCTED_EN.qa.json#/gate_results/page_1_5_modes		E_QA_GATE_PAGE_1_5_MODES	E_QA_GATE_PAGE_1_5_MODES	PASS
QAV-gate-page_coverage-missing	candidate/RECONSTRUCTED_EN.qa.json#/gate_results/page_coverage		E_QA_GATE_PAGE_COVERAGE	E_QA_GATE_PAGE_COVERAGE	PASS
QAV-gate-promotion-missing	candidate/RECONSTRUCTED_EN.qa.json#/gate_results/promotion		E_QA_GATE_PROMOTION	E_QA_GATE_PROMOTION	PASS
QAV-gate-recovery_admission-missing	candidate/RECONSTRUCTED_EN.qa.json#/gate_results/recovery_admission		E_QA_GATE_RECOVERY_ADMISSION	E_QA_GATE_RECOVERY_ADMISSION	PASS
QAV-gate-source_identity-missing	candidate/RECONSTRUCTED_EN.qa.json#/gate_results/source_identity		E_QA_GATE_SOURCE_IDENTITY	E_QA_GATE_SOURCE_IDENTITY	PASS
QAV-gate-visual_review-missing	candidate/RECONSTRUCTED_EN.qa.json#/gate_results/visual_review		E_QA_GATE_VISUAL_REVIEW	E_QA_GATE_VISUAL_REVIEW	PASS
QAV-gate-asset_conservation-wrong	candidate/RECONSTRUCTED_EN.qa.json#/gate_results/asset_conservation		E_QA_GATE_ASSET_CONSERVATION	E_QA_GATE_ASSET_CONSERVATION	PASS
QAV-gate-contact_sheet_coverage-wrong	candidate/RECONSTRUCTED_EN.qa.json#/gate_results/contact_sheet_coverage		E_QA_GATE_CONTACT_SHEET_COVERAGE	E_QA_GATE_CONTACT_SHEET_COVERAGE	PASS
QAV-gate-navigation_anchors-wrong	candidate/RECONSTRUCTED_EN.qa.json#/gate_results/navigation_anchors		E_QA_GATE_NAVIGATION_ANCHORS	E_QA_GATE_NAVIGATION_ANCHORS	PASS
QAV-gate-page_coverage-wrong	candidate/RECONSTRUCTED_EN.qa.json#/gate_results/page_coverage		E_QA_GATE_PAGE_COVERAGE	E_QA_GATE_PAGE_COVERAGE	PASS
QAV-gate-recovery_admission-wrong	candidate/RECONSTRUCTED_EN.qa.json#/gate_results/recovery_admission		E_QA_GATE_RECOVERY_ADMISSION	E_QA_GATE_RECOVERY_ADMISSION	PASS
QAV-gate-source_identity-wrong	candidate/RECONSTRUCTED_EN.qa.json#/gate_results/source_identity		E_QA_GATE_SOURCE_IDENTITY	E_QA_GATE_SOURCE_IDENTITY	PASS
QAV-gate-page_1_5_modes-closed	candidate/RECONSTRUCTED_EN.qa.json#/gate_results/page_1_5_modes		E_QA_GATE_PAGE_1_5_MODES	E_QA_GATE_PAGE_1_5_MODES	PASS
QAV-gate-promotion-closed	candidate/RECONSTRUCTED_EN.qa.json#/gate_results/promotion		E_QA_GATE_PROMOTION	E_QA_GATE_PROMOTION	PASS
QAV-gate-visual_review-closed	candidate/RECONSTRUCTED_EN.qa.json#/gate_results/visual_review		E_QA_GATE_VISUAL_REVIEW	E_QA_GATE_VISUAL_REVIEW	PASS
QAV-historical-material-true	candidate/RECONSTRUCTED_EN.qa.json#/historical_material_opened		E_QA_HISTORY	E_QA_HISTORY	PASS
QAV-main-scripts-invoked-true	candidate/RECONSTRUCTED_EN.qa.json#/main_scripts_invoked		E_QA_MAIN_SCRIPTS	E_QA_MAIN_SCRIPTS	PASS
QAV-inventory-rule-wrong	candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_rule		E_QA_INVENTORY_RULE	E_QA_INVENTORY_RULE	PASS
QAV-inventory-count-wrong	candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_count		E_INV_CARDINALITY	E_INV_CARDINALITY	PASS
QAV-inventory-digest-wrong	candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256		E_INV_DIGEST	E_INV_DIGEST	PASS
QAV-inventory-array-wrong	candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/RECONSTRUCTED_EN.md		E_INV_ORDINARY_ROW_MISSING	E_INV_ORDINARY_ROW_MISSING	PASS
REG-P1-stale-metadata	candidate/RECONSTRUCTED_EN.qa.json#		E_SHAPE_QA	E_SHAPE_QA	PASS
REG-P1-missing-enforcement	candidate/evidence/COMMANDS.json#/counts/pages	inventory,qa	E_COMMAND_COUNTS_PAGES	E_COMMAND_COUNTS_PAGES	PASS
INJ-profile-seal-mutated	profile#/authority_sha256		E_PROFILE_SEAL	E_PROFILE_SEAL	PASS
INJ-test-route-given-production-profile	context#/profile/kind		E_PROFILE_ROUTE	E_PROFILE_ROUTE	PASS
INJ-identity-provider-bound-to-other-profile	identity#/bound_profile_sha256		E_PROVIDER_BINDING	E_PROVIDER_BINDING	PASS
INJ-filesystem-provider-bound-to-other-profile	filesystem#/bound_profile_sha256		E_PROVIDER_BINDING	E_PROVIDER_BINDING	PASS
INJ-repository-root-observation-mismatch	repository#/root		E_REPO_ROOT	E_REPO_ROOT	PASS
<!-- CANONICAL_ROWS_END -->

- Rows: 368; bytes: 51005; SHA-256: 8C5C2A0A69C212465D1429FA38B35A4802C9AFCDF52F9461A1747D5729671DD4.

## REG delta

`json
[
  {
    "case_id": "REG-P1-stale-metadata",
    "changed_before_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/schema",
      "candidate/RECONSTRUCTED_EN.qa.json#/recovery_manifest_sha256",
      "candidate/RECONSTRUCTED_EN.qa.json#/recovery_evidence_sha256",
      "candidate/RECONSTRUCTED_EN.qa.json#/open_blocker_count",
      "candidate/RECONSTRUCTED_EN.qa.json#/counts/open_blockers",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-001.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-002.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-003.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-004.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-005.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-006.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-007.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-008.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-009.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-010.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-011.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-012.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-013.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-014.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-015.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-016.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-017.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-018.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-019.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-020.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-021.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-022.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-023.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-024.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-025.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-026.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-027.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-028.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-029.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-030.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-031.png",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_count",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "changed_by_reseal": [],
    "declared_reseals": [],
    "expected_code": "E_SHAPE_QA",
    "family": "REG",
    "fixture_root_token": "fixture",
    "observed_code": "E_SHAPE_QA",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "6562C451F47120D120025C754B5B3729390BB65251F150C220017BB6F4003912",
    "semantic_before_sha256": "EC5ECFFD57E6004E468CF5B3B2733748D7BA7523B437A9716FD31F00FAF83038",
    "semantic_selector": "candidate/RECONSTRUCTED_EN.qa.json#",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  },
  {
    "case_id": "REG-P1-missing-enforcement",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/counts/pages"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "expected_code": "E_COMMAND_COUNTS_PAGES",
    "family": "REG",
    "fixture_root_token": "fixture",
    "observed_code": "E_COMMAND_COUNTS_PAGES",
    "outside_fixture_reads": 0,
    "residue": [],
    "result": "PASS",
    "semantic_after_sha256": "9704137F1A03D24C4FB6A0A056E02420172D999D1DBDFC9AFEDB673DFA5D3798",
    "semantic_before_sha256": "95BFAB1D8BA86A63F8A1621B49341990759A411ECA8BDE3512DAE923C4ED3F79",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/counts/pages",
    "strict_verify_calls": 1,
    "undeclared_changes": []
  }
]
`

REG-P1-stale-metadata changed-before-reseal has exactly 38 selectors: ["candidate/RECONSTRUCTED_EN.qa.json#/schema", "candidate/RECONSTRUCTED_EN.qa.json#/recovery_manifest_sha256", "candidate/RECONSTRUCTED_EN.qa.json#/recovery_evidence_sha256", "candidate/RECONSTRUCTED_EN.qa.json#/open_blocker_count", "candidate/RECONSTRUCTED_EN.qa.json#/counts/open_blockers", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-001.png", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-002.png", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-003.png", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-004.png", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-005.png", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-006.png", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-007.png", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-008.png", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-009.png", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-010.png", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-011.png", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-012.png", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-013.png", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-014.png", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-015.png", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-016.png", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-017.png", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-018.png", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-019.png", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-020.png", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-021.png", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-022.png", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-023.png", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-024.png", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-025.png", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-026.png", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-027.png", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-028.png", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-029.png", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-030.png", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory/renders/contact_sheets/sheet-031.png", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_count", "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"].

## Alias declaration

Declared alias pairs: SCH-QAV QA required-top-member missing/top-schema shape agreement; SCH-QAV unexpected QA top member/top-extra; INV-QAV inventory cardinality; INV-QAV inventory digest; INV-QAV ordinary row missing/inventory array; REG paired stale metadata enforcement.  Twelve members, six pairs, with distinct frozen callable identities.

## Self verification

The embedded JSON is the actual returned array, schema-checked before write.  The canonical rows are derived only from that array; their byte length/hash above were recomputed in memory.  This recovery did not claim recovery of the earlier uncaptured stream.

No Luna participated. No 119/490/live/candidate/Git/cleanup mutation occurred.

## Literal evidence correction addendum (2026-09-01)

This addendum corrects receipt transport only. `AUDITS_JSON` and `CANONICAL_ROWS` above were read, parsed, and retained verbatim; their checked payload SHA-256 values are recorded below.

<!-- REGISTRY_JSON_BEGIN -->
[
  {
    "callable_name": "mutate_REP_branch_wrong",
    "case_id": "REP-branch-wrong",
    "ordinal": 1
  },
  {
    "callable_name": "mutate_REP_head_wrong",
    "case_id": "REP-head-wrong",
    "ordinal": 2
  },
  {
    "callable_name": "mutate_SRC_source_byte_identical_alias",
    "case_id": "SRC-source-byte-identical-alias",
    "ordinal": 3
  },
  {
    "callable_name": "mutate_SRC_source_external_locator",
    "case_id": "SRC-source-external-locator",
    "ordinal": 4
  },
  {
    "callable_name": "mutate_SRC_source_missing",
    "case_id": "SRC-source-missing",
    "ordinal": 5
  },
  {
    "callable_name": "mutate_SRC_source_bytes_wrong",
    "case_id": "SRC-source-bytes-wrong",
    "ordinal": 6
  },
  {
    "callable_name": "mutate_SRC_source_hash_wrong",
    "case_id": "SRC-source-hash-wrong",
    "ordinal": 7
  },
  {
    "callable_name": "mutate_SRC_source_reparse",
    "case_id": "SRC-source-reparse",
    "ordinal": 8
  },
  {
    "callable_name": "mutate_SRC_sidecar_missing",
    "case_id": "SRC-sidecar-missing",
    "ordinal": 9
  },
  {
    "callable_name": "mutate_SRC_sidecar_raw_hash_wrong",
    "case_id": "SRC-sidecar-raw-hash-wrong",
    "ordinal": 10
  },
  {
    "callable_name": "mutate_SRC_sidecar_working_path_wrong",
    "case_id": "SRC-sidecar-working-path-wrong",
    "ordinal": 11
  },
  {
    "callable_name": "mutate_SRC_sidecar_working_bytes_wrong",
    "case_id": "SRC-sidecar-working-bytes-wrong",
    "ordinal": 12
  },
  {
    "callable_name": "mutate_SRC_sidecar_working_hash_wrong",
    "case_id": "SRC-sidecar-working-hash-wrong",
    "ordinal": 13
  },
  {
    "callable_name": "mutate_SRC_sidecar_page_count_wrong",
    "case_id": "SRC-sidecar-page-count-wrong",
    "ordinal": 14
  },
  {
    "callable_name": "mutate_SRC_sidecar_media_box_wrong",
    "case_id": "SRC-sidecar-media-box-wrong",
    "ordinal": 15
  },
  {
    "callable_name": "mutate_SRC_sidecar_rotation_wrong",
    "case_id": "SRC-sidecar-rotation-wrong",
    "ordinal": 16
  },
  {
    "callable_name": "mutate_SRC_sidecar_runtime_dependency_true",
    "case_id": "SRC-sidecar-runtime-dependency-true",
    "ordinal": 17
  },
  {
    "callable_name": "mutate_SRC_sidecar_external_path_allowed",
    "case_id": "SRC-sidecar-external-path-allowed",
    "ordinal": 18
  },
  {
    "callable_name": "mutate_SRC_sidecar_subsequent_path_wrong",
    "case_id": "SRC-sidecar-subsequent-path-wrong",
    "ordinal": 19
  },
  {
    "callable_name": "mutate_SRC_sidecar_origin_marked_source",
    "case_id": "SRC-sidecar-origin-marked-source",
    "ordinal": 20
  },
  {
    "callable_name": "mutate_AUT_contract_argument_wrong",
    "case_id": "AUT-contract-argument-wrong",
    "ordinal": 21
  },
  {
    "callable_name": "mutate_AUT_contract_raw_hash_wrong",
    "case_id": "AUT-contract-raw-hash-wrong",
    "ordinal": 22
  },
  {
    "callable_name": "mutate_AUT_contract_canonical_content_wrong",
    "case_id": "AUT-contract-canonical-content-wrong",
    "ordinal": 23
  },
  {
    "callable_name": "mutate_AUT_snapshot_bytes_wrong",
    "case_id": "AUT-snapshot-bytes-wrong",
    "ordinal": 24
  },
  {
    "callable_name": "mutate_AUT_snapshot_hash_binding_wrong",
    "case_id": "AUT-snapshot-hash-binding-wrong",
    "ordinal": 25
  },
  {
    "callable_name": "mutate_AUT_source_identity_contract_sha",
    "case_id": "AUT-source-identity-contract-sha",
    "ordinal": 26
  },
  {
    "callable_name": "mutate_AUT_source_identity_source_bytes",
    "case_id": "AUT-source-identity-source-bytes",
    "ordinal": 27
  },
  {
    "callable_name": "mutate_AUT_source_identity_source_sha",
    "case_id": "AUT-source-identity-source-sha",
    "ordinal": 28
  },
  {
    "callable_name": "mutate_AUT_source_identity_page_count",
    "case_id": "AUT-source-identity-page-count",
    "ordinal": 29
  },
  {
    "callable_name": "mutate_AUT_source_identity_media_box",
    "case_id": "AUT-source-identity-media-box",
    "ordinal": 30
  },
  {
    "callable_name": "mutate_AUT_source_identity_rotation",
    "case_id": "AUT-source-identity-rotation",
    "ordinal": 31
  },
  {
    "callable_name": "mutate_AUT_source_identity_recovery_manifest_sha",
    "case_id": "AUT-source-identity-recovery-manifest-sha",
    "ordinal": 32
  },
  {
    "callable_name": "mutate_AUT_source_identity_recovery_evidence_sha",
    "case_id": "AUT-source-identity-recovery-evidence-sha",
    "ordinal": 33
  },
  {
    "callable_name": "mutate_AUT_source_identity_recovery_root",
    "case_id": "AUT-source-identity-recovery-root",
    "ordinal": 34
  },
  {
    "callable_name": "mutate_AUT_source_identity_history_true",
    "case_id": "AUT-source-identity-history-true",
    "ordinal": 35
  },
  {
    "callable_name": "mutate_AUT_source_identity_state_wrong",
    "case_id": "AUT-source-identity-state-wrong",
    "ordinal": 36
  },
  {
    "callable_name": "mutate_AUT_recovery_root_wrong",
    "case_id": "AUT-recovery-root-wrong",
    "ordinal": 37
  },
  {
    "callable_name": "mutate_AUT_recovery_manifest_raw_hash",
    "case_id": "AUT-recovery-manifest-raw-hash",
    "ordinal": 38
  },
  {
    "callable_name": "mutate_AUT_recovery_evidence_raw_hash",
    "case_id": "AUT-recovery-evidence-raw-hash",
    "ordinal": 39
  },
  {
    "callable_name": "mutate_AUT_recovery_successor_file_count",
    "case_id": "AUT-recovery-successor-file-count",
    "ordinal": 40
  },
  {
    "callable_name": "mutate_AUT_recovery_successor_total_bytes",
    "case_id": "AUT-recovery-successor-total-bytes",
    "ordinal": 41
  },
  {
    "callable_name": "mutate_AUT_recovery_manifest_row_path",
    "case_id": "AUT-recovery-manifest-row-path",
    "ordinal": 42
  },
  {
    "callable_name": "mutate_AUT_recovery_manifest_row_bytes",
    "case_id": "AUT-recovery-manifest-row-bytes",
    "ordinal": 43
  },
  {
    "callable_name": "mutate_AUT_recovery_manifest_row_hash",
    "case_id": "AUT-recovery-manifest-row-hash",
    "ordinal": 44
  },
  {
    "callable_name": "mutate_AUT_recovery_manifest_row_duplicate",
    "case_id": "AUT-recovery-manifest-row-duplicate",
    "ordinal": 45
  },
  {
    "callable_name": "mutate_AUT_recovery_forbidden_payload",
    "case_id": "AUT-recovery-forbidden-payload",
    "ordinal": 46
  },
  {
    "callable_name": "mutate_AUT_recovery_evidence_source_binding",
    "case_id": "AUT-recovery-evidence-source-binding",
    "ordinal": 47
  },
  {
    "callable_name": "mutate_AUT_recovery_evidence_payload_binding",
    "case_id": "AUT-recovery-evidence-payload-binding",
    "ordinal": 48
  },
  {
    "callable_name": "mutate_AUT_recovery_allowed_paths",
    "case_id": "AUT-recovery-allowed-paths",
    "ordinal": 49
  },
  {
    "callable_name": "mutate_AUT_recovery_promotion_true",
    "case_id": "AUT-recovery-promotion-true",
    "ordinal": 50
  },
  {
    "callable_name": "mutate_TOP_candidate_root_wrong",
    "case_id": "TOP-candidate-root-wrong",
    "ordinal": 51
  },
  {
    "callable_name": "mutate_TOP_candidate_root_escape",
    "case_id": "TOP-candidate-root-escape",
    "ordinal": 52
  },
  {
    "callable_name": "mutate_TOP_candidate_root_reparse",
    "case_id": "TOP-candidate-root-reparse",
    "ordinal": 53
  },
  {
    "callable_name": "mutate_TOP_nested_reparse",
    "case_id": "TOP-nested-reparse",
    "ordinal": 54
  },
  {
    "callable_name": "mutate_TOP_root_file_missing",
    "case_id": "TOP-root-file-missing",
    "ordinal": 55
  },
  {
    "callable_name": "mutate_TOP_root_entry_extra",
    "case_id": "TOP-root-entry-extra",
    "ordinal": 56
  },
  {
    "callable_name": "mutate_TOP_evidence_file_missing",
    "case_id": "TOP-evidence-file-missing",
    "ordinal": 57
  },
  {
    "callable_name": "mutate_TOP_evidence_file_extra",
    "case_id": "TOP-evidence-file-extra",
    "ordinal": 58
  },
  {
    "callable_name": "mutate_TOP_page_missing",
    "case_id": "TOP-page-missing",
    "ordinal": 59
  },
  {
    "callable_name": "mutate_TOP_source_render_missing",
    "case_id": "TOP-source-render-missing",
    "ordinal": 60
  },
  {
    "callable_name": "mutate_TOP_sheet_missing",
    "case_id": "TOP-sheet-missing",
    "ordinal": 61
  },
  {
    "callable_name": "mutate_TOP_engine_payload_missing",
    "case_id": "TOP-engine-payload-missing",
    "ordinal": 62
  },
  {
    "callable_name": "mutate_TOP_protected_empty_subtree_nonempty",
    "case_id": "TOP-protected-empty-subtree-nonempty",
    "ordinal": 63
  },
  {
    "callable_name": "mutate_TOP_forbidden_pdf",
    "case_id": "TOP-forbidden-pdf",
    "ordinal": 64
  },
  {
    "callable_name": "mutate_TOP_forbidden_compiled_suffix",
    "case_id": "TOP-forbidden-compiled-suffix",
    "ordinal": 65
  },
  {
    "callable_name": "mutate_TOP_forbidden_pycache",
    "case_id": "TOP-forbidden-pycache",
    "ordinal": 66
  },
  {
    "callable_name": "mutate_TOP_forbidden_bridge_runtime",
    "case_id": "TOP-forbidden-bridge-runtime",
    "ordinal": 67
  },
  {
    "callable_name": "mutate_TOP_forbidden_cache",
    "case_id": "TOP-forbidden-cache",
    "ordinal": 68
  },
  {
    "callable_name": "mutate_TOP_forbidden_pytest_cache",
    "case_id": "TOP-forbidden-pytest-cache",
    "ordinal": 69
  },
  {
    "callable_name": "mutate_TOP_forbidden_tmp",
    "case_id": "TOP-forbidden-tmp",
    "ordinal": 70
  },
  {
    "callable_name": "mutate_TOP_forbidden_temp",
    "case_id": "TOP-forbidden-temp",
    "ordinal": 71
  },
  {
    "callable_name": "mutate_SCH_CONTRACT_schema_wrong",
    "case_id": "SCH-CONTRACT-schema-wrong",
    "ordinal": 72
  },
  {
    "callable_name": "mutate_SCH_CONTRACT_required_top_member_missing",
    "case_id": "SCH-CONTRACT-required-top-member-missing",
    "ordinal": 73
  },
  {
    "callable_name": "mutate_SCH_SIDECAR_schema_wrong",
    "case_id": "SCH-SIDECAR-schema-wrong",
    "ordinal": 74
  },
  {
    "callable_name": "mutate_SCH_SIDECAR_required_top_member_missing",
    "case_id": "SCH-SIDECAR-required-top-member-missing",
    "ordinal": 75
  },
  {
    "callable_name": "mutate_SCH_RECOVERY_MANIFEST_schema_wrong",
    "case_id": "SCH-RECOVERY_MANIFEST-schema-wrong",
    "ordinal": 76
  },
  {
    "callable_name": "mutate_SCH_RECOVERY_MANIFEST_required_top_member_missing",
    "case_id": "SCH-RECOVERY_MANIFEST-required-top-member-missing",
    "ordinal": 77
  },
  {
    "callable_name": "mutate_SCH_RECOVERY_EVIDENCE_schema_wrong",
    "case_id": "SCH-RECOVERY_EVIDENCE-schema-wrong",
    "ordinal": 78
  },
  {
    "callable_name": "mutate_SCH_RECOVERY_EVIDENCE_required_top_member_missing",
    "case_id": "SCH-RECOVERY_EVIDENCE-required-top-member-missing",
    "ordinal": 79
  },
  {
    "callable_name": "mutate_SCH_QA_schema_wrong",
    "case_id": "SCH-QA-schema-wrong",
    "ordinal": 80
  },
  {
    "callable_name": "mutate_SCH_QA_required_top_member_missing",
    "case_id": "SCH-QA-required-top-member-missing",
    "ordinal": 81
  },
  {
    "callable_name": "mutate_SCH_SOURCE_IDENTITY_schema_wrong",
    "case_id": "SCH-SOURCE_IDENTITY-schema-wrong",
    "ordinal": 82
  },
  {
    "callable_name": "mutate_SCH_SOURCE_IDENTITY_required_top_member_missing",
    "case_id": "SCH-SOURCE_IDENTITY-required-top-member-missing",
    "ordinal": 83
  },
  {
    "callable_name": "mutate_SCH_PAGE_PROVENANCE_schema_wrong",
    "case_id": "SCH-PAGE_PROVENANCE-schema-wrong",
    "ordinal": 84
  },
  {
    "callable_name": "mutate_SCH_PAGE_PROVENANCE_required_top_member_missing",
    "case_id": "SCH-PAGE_PROVENANCE-required-top-member-missing",
    "ordinal": 85
  },
  {
    "callable_name": "mutate_SCH_CONTENT_PROVENANCE_schema_wrong",
    "case_id": "SCH-CONTENT_PROVENANCE-schema-wrong",
    "ordinal": 86
  },
  {
    "callable_name": "mutate_SCH_CONTENT_PROVENANCE_required_top_member_missing",
    "case_id": "SCH-CONTENT_PROVENANCE-required-top-member-missing",
    "ordinal": 87
  },
  {
    "callable_name": "mutate_SCH_ASSET_PROVENANCE_schema_wrong",
    "case_id": "SCH-ASSET_PROVENANCE-schema-wrong",
    "ordinal": 88
  },
  {
    "callable_name": "mutate_SCH_ASSET_PROVENANCE_required_top_member_missing",
    "case_id": "SCH-ASSET_PROVENANCE-required-top-member-missing",
    "ordinal": 89
  },
  {
    "callable_name": "mutate_SCH_ENTITY_INVENTORY_schema_wrong",
    "case_id": "SCH-ENTITY_INVENTORY-schema-wrong",
    "ordinal": 90
  },
  {
    "callable_name": "mutate_SCH_ENTITY_INVENTORY_required_top_member_missing",
    "case_id": "SCH-ENTITY_INVENTORY-required-top-member-missing",
    "ordinal": 91
  },
  {
    "callable_name": "mutate_SCH_HANDOUT_INVENTORY_schema_wrong",
    "case_id": "SCH-HANDOUT_INVENTORY-schema-wrong",
    "ordinal": 92
  },
  {
    "callable_name": "mutate_SCH_HANDOUT_INVENTORY_required_top_member_missing",
    "case_id": "SCH-HANDOUT_INVENTORY-required-top-member-missing",
    "ordinal": 93
  },
  {
    "callable_name": "mutate_SCH_NAVIGATION_INVENTORY_schema_wrong",
    "case_id": "SCH-NAVIGATION_INVENTORY-schema-wrong",
    "ordinal": 94
  },
  {
    "callable_name": "mutate_SCH_NAVIGATION_INVENTORY_required_top_member_missing",
    "case_id": "SCH-NAVIGATION_INVENTORY-required-top-member-missing",
    "ordinal": 95
  },
  {
    "callable_name": "mutate_SCH_CONTENT_MODE_REVIEW_schema_wrong",
    "case_id": "SCH-CONTENT_MODE_REVIEW-schema-wrong",
    "ordinal": 96
  },
  {
    "callable_name": "mutate_SCH_CONTENT_MODE_REVIEW_required_top_member_missing",
    "case_id": "SCH-CONTENT_MODE_REVIEW-required-top-member-missing",
    "ordinal": 97
  },
  {
    "callable_name": "mutate_SCH_REFERENCE_ONLY_AUDIT_schema_wrong",
    "case_id": "SCH-REFERENCE_ONLY_AUDIT-schema-wrong",
    "ordinal": 98
  },
  {
    "callable_name": "mutate_SCH_REFERENCE_ONLY_AUDIT_required_top_member_missing",
    "case_id": "SCH-REFERENCE_ONLY_AUDIT-required-top-member-missing",
    "ordinal": 99
  },
  {
    "callable_name": "mutate_SCH_BLOCKER_LEDGER_schema_wrong",
    "case_id": "SCH-BLOCKER_LEDGER-schema-wrong",
    "ordinal": 100
  },
  {
    "callable_name": "mutate_SCH_BLOCKER_LEDGER_required_top_member_missing",
    "case_id": "SCH-BLOCKER_LEDGER-required-top-member-missing",
    "ordinal": 101
  },
  {
    "callable_name": "mutate_SCH_COMMANDS_schema_wrong",
    "case_id": "SCH-COMMANDS-schema-wrong",
    "ordinal": 102
  },
  {
    "callable_name": "mutate_SCH_COMMANDS_required_top_member_missing",
    "case_id": "SCH-COMMANDS-required-top-member-missing",
    "ordinal": 103
  },
  {
    "callable_name": "mutate_SCH_qa_unexpected_top_member",
    "case_id": "SCH-qa-unexpected-top-member",
    "ordinal": 104
  },
  {
    "callable_name": "mutate_LED_open_count_wrong",
    "case_id": "LED-open-count-wrong",
    "ordinal": 105
  },
  {
    "callable_name": "mutate_LED_row_count_wrong",
    "case_id": "LED-row-count-wrong",
    "ordinal": 106
  },
  {
    "callable_name": "mutate_LED_row_state_closed",
    "case_id": "LED-row-state-closed",
    "ordinal": 107
  },
  {
    "callable_name": "mutate_LED_review_state_closed",
    "case_id": "LED-review-state-closed",
    "ordinal": 108
  },
  {
    "callable_name": "mutate_LED_blocker_id_set_wrong",
    "case_id": "LED-blocker-id-set-wrong",
    "ordinal": 109
  },
  {
    "callable_name": "mutate_LED_affected_scope_count_wrong",
    "case_id": "LED-affected-scope-count-wrong",
    "ordinal": 110
  },
  {
    "callable_name": "mutate_INV_ordinary_row_missing",
    "case_id": "INV-ordinary-row-missing",
    "ordinal": 111
  },
  {
    "callable_name": "mutate_INV_evidence_row_missing",
    "case_id": "INV-evidence-row-missing",
    "ordinal": 112
  },
  {
    "callable_name": "mutate_INV_sheet_row_missing",
    "case_id": "INV-sheet-row-missing",
    "ordinal": 113
  },
  {
    "callable_name": "mutate_INV_stale_extra_path",
    "case_id": "INV-stale-extra-path",
    "ordinal": 114
  },
  {
    "callable_name": "mutate_INV_duplicate_path",
    "case_id": "INV-duplicate-path",
    "ordinal": 115
  },
  {
    "callable_name": "mutate_INV_qa_included",
    "case_id": "INV-qa-included",
    "ordinal": 116
  },
  {
    "callable_name": "mutate_INV_cardinality_wrong",
    "case_id": "INV-cardinality-wrong",
    "ordinal": 117
  },
  {
    "callable_name": "mutate_INV_order_nonordinal",
    "case_id": "INV-order-nonordinal",
    "ordinal": 118
  },
  {
    "callable_name": "mutate_INV_row_bytes_wrong",
    "case_id": "INV-row-bytes-wrong",
    "ordinal": 119
  },
  {
    "callable_name": "mutate_INV_row_hash_wrong",
    "case_id": "INV-row-hash-wrong",
    "ordinal": 120
  },
  {
    "callable_name": "mutate_INV_row_hash_lowercase",
    "case_id": "INV-row-hash-lowercase",
    "ordinal": 121
  },
  {
    "callable_name": "mutate_INV_digest_wrong",
    "case_id": "INV-digest-wrong",
    "ordinal": 122
  },
  {
    "callable_name": "mutate_INV_path_backslash",
    "case_id": "INV-path-backslash",
    "ordinal": 123
  },
  {
    "callable_name": "mutate_INV_path_absolute_or_drive",
    "case_id": "INV-path-absolute-or-drive",
    "ordinal": 124
  },
  {
    "callable_name": "mutate_INV_path_parent_segment",
    "case_id": "INV-path-parent-segment",
    "ordinal": 125
  },
  {
    "callable_name": "mutate_INV_path_leading_dot_slash",
    "case_id": "INV-path-leading-dot-slash",
    "ordinal": 126
  },
  {
    "callable_name": "mutate_INV_row_shape_wrong",
    "case_id": "INV-row-shape-wrong",
    "ordinal": 127
  },
  {
    "callable_name": "mutate_INV_live_file_changed_behind_row",
    "case_id": "INV-live-file-changed-behind-row",
    "ordinal": 128
  },
  {
    "callable_name": "mutate_PAG_page_row_missing",
    "case_id": "PAG-page-row-missing",
    "ordinal": 129
  },
  {
    "callable_name": "mutate_PAG_page_row_duplicate",
    "case_id": "PAG-page-row-duplicate",
    "ordinal": 130
  },
  {
    "callable_name": "mutate_PAG_page_number_wrong",
    "case_id": "PAG-page-number-wrong",
    "ordinal": 131
  },
  {
    "callable_name": "mutate_PAG_page_id_wrong",
    "case_id": "PAG-page-id-wrong",
    "ordinal": 132
  },
  {
    "callable_name": "mutate_PAG_engine_index_wrong",
    "case_id": "PAG-engine-index-wrong",
    "ordinal": 133
  },
  {
    "callable_name": "mutate_PAG_role_wrong",
    "case_id": "PAG-role-wrong",
    "ordinal": 134
  },
  {
    "callable_name": "mutate_PAG_contract_mode_wrong",
    "case_id": "PAG-contract-mode-wrong",
    "ordinal": 135
  },
  {
    "callable_name": "mutate_PAG_markdown_path_wrong",
    "case_id": "PAG-markdown-path-wrong",
    "ordinal": 136
  },
  {
    "callable_name": "mutate_PAG_markdown_bytes_wrong",
    "case_id": "PAG-markdown-bytes-wrong",
    "ordinal": 137
  },
  {
    "callable_name": "mutate_PAG_markdown_hash_wrong",
    "case_id": "PAG-markdown-hash-wrong",
    "ordinal": 138
  },
  {
    "callable_name": "mutate_PAG_render_path_wrong",
    "case_id": "PAG-render-path-wrong",
    "ordinal": 139
  },
  {
    "callable_name": "mutate_PAG_render_bytes_wrong",
    "case_id": "PAG-render-bytes-wrong",
    "ordinal": 140
  },
  {
    "callable_name": "mutate_PAG_render_hash_wrong",
    "case_id": "PAG-render-hash-wrong",
    "ordinal": 141
  },
  {
    "callable_name": "mutate_PAG_render_page_number_wrong",
    "case_id": "PAG-render-page-number-wrong",
    "ordinal": 142
  },
  {
    "callable_name": "mutate_PAG_render_dimensions_wrong",
    "case_id": "PAG-render-dimensions-wrong",
    "ordinal": 143
  },
  {
    "callable_name": "mutate_PAG_render_dpi_wrong",
    "case_id": "PAG-render-dpi-wrong",
    "ordinal": 144
  },
  {
    "callable_name": "mutate_PAG_live_markdown_missing",
    "case_id": "PAG-live-markdown-missing",
    "ordinal": 145
  },
  {
    "callable_name": "mutate_PAG_live_render_missing",
    "case_id": "PAG-live-render-missing",
    "ordinal": 146
  },
  {
    "callable_name": "mutate_PAG_source_page_marker_wrong",
    "case_id": "PAG-source-page-marker-wrong",
    "ordinal": 147
  },
  {
    "callable_name": "mutate_PAG_render_marker_wrong",
    "case_id": "PAG-render-marker-wrong",
    "ordinal": 148
  },
  {
    "callable_name": "mutate_PAG_master_concatenation_wrong",
    "case_id": "PAG-master-concatenation-wrong",
    "ordinal": 149
  },
  {
    "callable_name": "mutate_PAG_content_orphan",
    "case_id": "PAG-content-orphan",
    "ordinal": 150
  },
  {
    "callable_name": "mutate_PAG_content_duplicate",
    "case_id": "PAG-content-duplicate",
    "ordinal": 151
  },
  {
    "callable_name": "mutate_PAG_content_order_wrong",
    "case_id": "PAG-content-order-wrong",
    "ordinal": 152
  },
  {
    "callable_name": "mutate_PAG_content_predecessor_wrong",
    "case_id": "PAG-content-predecessor-wrong",
    "ordinal": 153
  },
  {
    "callable_name": "mutate_PAG_content_successor_wrong",
    "case_id": "PAG-content-successor-wrong",
    "ordinal": 154
  },
  {
    "callable_name": "mutate_PAG_content_operation_fabricated",
    "case_id": "PAG-content-operation-fabricated",
    "ordinal": 155
  },
  {
    "callable_name": "mutate_PAG_content_asset_link_fabricated",
    "case_id": "PAG-content-asset-link-fabricated",
    "ordinal": 156
  },
  {
    "callable_name": "mutate_NAV_row_missing",
    "case_id": "NAV-row-missing",
    "ordinal": 157
  },
  {
    "callable_name": "mutate_NAV_anchor_duplicate",
    "case_id": "NAV-anchor-duplicate",
    "ordinal": 158
  },
  {
    "callable_name": "mutate_NAV_anchor_id_wrong",
    "case_id": "NAV-anchor-id-wrong",
    "ordinal": 159
  },
  {
    "callable_name": "mutate_NAV_source_page_wrong",
    "case_id": "NAV-source-page-wrong",
    "ordinal": 160
  },
  {
    "callable_name": "mutate_NAV_engine_index_wrong",
    "case_id": "NAV-engine-index-wrong",
    "ordinal": 161
  },
  {
    "callable_name": "mutate_NAV_first_previous_nonnull",
    "case_id": "NAV-first-previous-nonnull",
    "ordinal": 162
  },
  {
    "callable_name": "mutate_NAV_last_next_nonnull",
    "case_id": "NAV-last-next-nonnull",
    "ordinal": 163
  },
  {
    "callable_name": "mutate_NAV_middle_previous_wrong",
    "case_id": "NAV-middle-previous-wrong",
    "ordinal": 164
  },
  {
    "callable_name": "mutate_NAV_middle_next_wrong",
    "case_id": "NAV-middle-next-wrong",
    "ordinal": 165
  },
  {
    "callable_name": "mutate_NAV_dangling_link",
    "case_id": "NAV-dangling-link",
    "ordinal": 166
  },
  {
    "callable_name": "mutate_NAV_markdown_path_wrong",
    "case_id": "NAV-markdown-path-wrong",
    "ordinal": 167
  },
  {
    "callable_name": "mutate_NAV_render_path_wrong",
    "case_id": "NAV-render-path-wrong",
    "ordinal": 168
  },
  {
    "callable_name": "mutate_NAV_render_hash_wrong",
    "case_id": "NAV-render-hash-wrong",
    "ordinal": 169
  },
  {
    "callable_name": "mutate_NAV_role_wrong",
    "case_id": "NAV-role-wrong",
    "ordinal": 170
  },
  {
    "callable_name": "mutate_NAV_closure_promoted",
    "case_id": "NAV-closure-promoted",
    "ordinal": 171
  },
  {
    "callable_name": "mutate_AST_row_missing",
    "case_id": "AST-row-missing",
    "ordinal": 172
  },
  {
    "callable_name": "mutate_AST_id_duplicate",
    "case_id": "AST-id-duplicate",
    "ordinal": 173
  },
  {
    "callable_name": "mutate_AST_path_duplicate",
    "case_id": "AST-path-duplicate",
    "ordinal": 174
  },
  {
    "callable_name": "mutate_AST_hash_duplicate",
    "case_id": "AST-hash-duplicate",
    "ordinal": 175
  },
  {
    "callable_name": "mutate_AST_live_bytes_wrong",
    "case_id": "AST-live-bytes-wrong",
    "ordinal": 176
  },
  {
    "callable_name": "mutate_AST_live_hash_wrong",
    "case_id": "AST-live-hash-wrong",
    "ordinal": 177
  },
  {
    "callable_name": "mutate_AST_engine_path_missing",
    "case_id": "AST-engine-path-missing",
    "ordinal": 178
  },
  {
    "callable_name": "mutate_AST_engine_path_wrong",
    "case_id": "AST-engine-path-wrong",
    "ordinal": 179
  },
  {
    "callable_name": "mutate_AST_recovery_binding_wrong",
    "case_id": "AST-recovery-binding-wrong",
    "ordinal": 180
  },
  {
    "callable_name": "mutate_AST_reference_total_wrong",
    "case_id": "AST-reference-total-wrong",
    "ordinal": 181
  },
  {
    "callable_name": "mutate_AST_unreferenced_count_wrong",
    "case_id": "AST-unreferenced-count-wrong",
    "ordinal": 182
  },
  {
    "callable_name": "mutate_AST_reference_count_outside_zero_one",
    "case_id": "AST-reference-count-outside-zero-one",
    "ordinal": 183
  },
  {
    "callable_name": "mutate_AST_occurrence_missing",
    "case_id": "AST-occurrence-missing",
    "ordinal": 184
  },
  {
    "callable_name": "mutate_AST_occurrence_duplicate",
    "case_id": "AST-occurrence-duplicate",
    "ordinal": 185
  },
  {
    "callable_name": "mutate_AST_markdown_path_wrong",
    "case_id": "AST-markdown-path-wrong",
    "ordinal": 186
  },
  {
    "callable_name": "mutate_AST_target_absent_from_markdown",
    "case_id": "AST-target-absent-from-markdown",
    "ordinal": 187
  },
  {
    "callable_name": "mutate_AST_ownership_nonnull",
    "case_id": "AST-ownership-nonnull",
    "ordinal": 188
  },
  {
    "callable_name": "mutate_AST_closure_promoted",
    "case_id": "AST-closure-promoted",
    "ordinal": 189
  },
  {
    "callable_name": "mutate_AST_finding_wrong",
    "case_id": "AST-finding-wrong",
    "ordinal": 190
  },
  {
    "callable_name": "mutate_AST_engine_image_cardinality_wrong",
    "case_id": "AST-engine-image-cardinality-wrong",
    "ordinal": 191
  },
  {
    "callable_name": "mutate_AST_mime_wrong",
    "case_id": "AST-mime-wrong",
    "ordinal": 192
  },
  {
    "callable_name": "mutate_SEM_entity_ordinal_gap",
    "case_id": "SEM-entity-ordinal-gap",
    "ordinal": 193
  },
  {
    "callable_name": "mutate_SEM_entity_id_duplicate",
    "case_id": "SEM-entity-id-duplicate",
    "ordinal": 194
  },
  {
    "callable_name": "mutate_SEM_handout_ordinal_gap",
    "case_id": "SEM-handout-ordinal-gap",
    "ordinal": 195
  },
  {
    "callable_name": "mutate_SEM_handout_id_duplicate",
    "case_id": "SEM-handout-id-duplicate",
    "ordinal": 196
  },
  {
    "callable_name": "mutate_SEM_entity_handout_inequality",
    "case_id": "SEM-entity-handout-inequality",
    "ordinal": 197
  },
  {
    "callable_name": "mutate_SEM_required_count_wrong",
    "case_id": "SEM-required-count-wrong",
    "ordinal": 198
  },
  {
    "callable_name": "mutate_SEM_label_wrong",
    "case_id": "SEM-label-wrong",
    "ordinal": 199
  },
  {
    "callable_name": "mutate_SEM_page_range_wrong",
    "case_id": "SEM-page-range-wrong",
    "ordinal": 200
  },
  {
    "callable_name": "mutate_SEM_entity_closure_promoted",
    "case_id": "SEM-entity-closure-promoted",
    "ordinal": 201
  },
  {
    "callable_name": "mutate_SEM_mode_page_gap",
    "case_id": "SEM-mode-page-gap",
    "ordinal": 202
  },
  {
    "callable_name": "mutate_SEM_mode_row_duplicate",
    "case_id": "SEM-mode-row-duplicate",
    "ordinal": 203
  },
  {
    "callable_name": "mutate_SEM_mode_review_promoted",
    "case_id": "SEM-mode-review-promoted",
    "ordinal": 204
  },
  {
    "callable_name": "mutate_SEM_reference_only_row_added",
    "case_id": "SEM-reference-only-row-added",
    "ordinal": 205
  },
  {
    "callable_name": "mutate_SEM_historical_material_true",
    "case_id": "SEM-historical-material-true",
    "ordinal": 206
  },
  {
    "callable_name": "mutate_SEM_map_role_count_wrong",
    "case_id": "SEM-map-role-count-wrong",
    "ordinal": 207
  },
  {
    "callable_name": "mutate_SEM_pregen_role_count_wrong",
    "case_id": "SEM-pregen-role-count-wrong",
    "ordinal": 208
  },
  {
    "callable_name": "mutate_SEM_back_cover_role_count_wrong",
    "case_id": "SEM-back-cover-role-count-wrong",
    "ordinal": 209
  },
  {
    "callable_name": "mutate_SEM_handout_role_count_wrong",
    "case_id": "SEM-handout-role-count-wrong",
    "ordinal": 210
  },
  {
    "callable_name": "mutate_CMD_action_missing",
    "case_id": "CMD-action-missing",
    "ordinal": 211
  },
  {
    "callable_name": "mutate_CMD_action_duplicate",
    "case_id": "CMD-action-duplicate",
    "ordinal": 212
  },
  {
    "callable_name": "mutate_CMD_action_extra",
    "case_id": "CMD-action-extra",
    "ordinal": 213
  },
  {
    "callable_name": "mutate_CMD_action_reordered",
    "case_id": "CMD-action-reordered",
    "ordinal": 214
  },
  {
    "callable_name": "mutate_CMD_state_promoted",
    "case_id": "CMD-state-promoted",
    "ordinal": 215
  },
  {
    "callable_name": "mutate_CMD_external_locator_used",
    "case_id": "CMD-external-locator-used",
    "ordinal": 216
  },
  {
    "callable_name": "mutate_CMD_flag_build_invoked_missing",
    "case_id": "CMD-flag-build_invoked-missing",
    "ordinal": 217
  },
  {
    "callable_name": "mutate_CMD_flag_build_invoked_true",
    "case_id": "CMD-flag-build_invoked-true",
    "ordinal": 218
  },
  {
    "callable_name": "mutate_CMD_flag_mineru_invoked_missing",
    "case_id": "CMD-flag-mineru_invoked-missing",
    "ordinal": 219
  },
  {
    "callable_name": "mutate_CMD_flag_mineru_invoked_true",
    "case_id": "CMD-flag-mineru_invoked-true",
    "ordinal": 220
  },
  {
    "callable_name": "mutate_CMD_flag_ocr_invoked_missing",
    "case_id": "CMD-flag-ocr_invoked-missing",
    "ordinal": 221
  },
  {
    "callable_name": "mutate_CMD_flag_ocr_invoked_true",
    "case_id": "CMD-flag-ocr_invoked-true",
    "ordinal": 222
  },
  {
    "callable_name": "mutate_CMD_flag_gpu_or_model_invoked_missing",
    "case_id": "CMD-flag-gpu_or_model_invoked-missing",
    "ordinal": 223
  },
  {
    "callable_name": "mutate_CMD_flag_gpu_or_model_invoked_true",
    "case_id": "CMD-flag-gpu_or_model_invoked-true",
    "ordinal": 224
  },
  {
    "callable_name": "mutate_CMD_flag_network_invoked_missing",
    "case_id": "CMD-flag-network_invoked-missing",
    "ordinal": 225
  },
  {
    "callable_name": "mutate_CMD_flag_network_invoked_true",
    "case_id": "CMD-flag-network_invoked-true",
    "ordinal": 226
  },
  {
    "callable_name": "mutate_CMD_flag_external_source_used_missing",
    "case_id": "CMD-flag-external_source_used-missing",
    "ordinal": 227
  },
  {
    "callable_name": "mutate_CMD_flag_external_source_used_true",
    "case_id": "CMD-flag-external_source_used-true",
    "ordinal": 228
  },
  {
    "callable_name": "mutate_CMD_argument_source_flag_missing",
    "case_id": "CMD-argument-source_flag-missing",
    "ordinal": 229
  },
  {
    "callable_name": "mutate_CMD_argument_source_flag_wrong",
    "case_id": "CMD-argument-source_flag-wrong",
    "ordinal": 230
  },
  {
    "callable_name": "mutate_CMD_argument_run_root_flag_missing",
    "case_id": "CMD-argument-run_root_flag-missing",
    "ordinal": 231
  },
  {
    "callable_name": "mutate_CMD_argument_run_root_flag_wrong",
    "case_id": "CMD-argument-run_root_flag-wrong",
    "ordinal": 232
  },
  {
    "callable_name": "mutate_CMD_argument_source_relative_path_missing",
    "case_id": "CMD-argument-source_relative_path-missing",
    "ordinal": 233
  },
  {
    "callable_name": "mutate_CMD_argument_source_relative_path_wrong",
    "case_id": "CMD-argument-source_relative_path-wrong",
    "ordinal": 234
  },
  {
    "callable_name": "mutate_CMD_count_pages_missing",
    "case_id": "CMD-count-pages-missing",
    "ordinal": 235
  },
  {
    "callable_name": "mutate_CMD_count_pages_wrong",
    "case_id": "CMD-count-pages-wrong",
    "ordinal": 236
  },
  {
    "callable_name": "mutate_CMD_count_renders_missing",
    "case_id": "CMD-count-renders-missing",
    "ordinal": 237
  },
  {
    "callable_name": "mutate_CMD_count_renders_wrong",
    "case_id": "CMD-count-renders-wrong",
    "ordinal": 238
  },
  {
    "callable_name": "mutate_CMD_count_contact_sheets_missing",
    "case_id": "CMD-count-contact_sheets-missing",
    "ordinal": 239
  },
  {
    "callable_name": "mutate_CMD_count_contact_sheets_wrong",
    "case_id": "CMD-count-contact_sheets-wrong",
    "ordinal": 240
  },
  {
    "callable_name": "mutate_CMD_count_handouts_missing",
    "case_id": "CMD-count-handouts-missing",
    "ordinal": 241
  },
  {
    "callable_name": "mutate_CMD_count_handouts_wrong",
    "case_id": "CMD-count-handouts-wrong",
    "ordinal": 242
  },
  {
    "callable_name": "mutate_CMD_count_maps_missing",
    "case_id": "CMD-count-maps-missing",
    "ordinal": 243
  },
  {
    "callable_name": "mutate_CMD_count_maps_wrong",
    "case_id": "CMD-count-maps-wrong",
    "ordinal": 244
  },
  {
    "callable_name": "mutate_CMD_count_pregens_missing",
    "case_id": "CMD-count-pregens-missing",
    "ordinal": 245
  },
  {
    "callable_name": "mutate_CMD_count_pregens_wrong",
    "case_id": "CMD-count-pregens-wrong",
    "ordinal": 246
  },
  {
    "callable_name": "mutate_CMD_count_back_cover_missing",
    "case_id": "CMD-count-back_cover-missing",
    "ordinal": 247
  },
  {
    "callable_name": "mutate_CMD_count_back_cover_wrong",
    "case_id": "CMD-count-back_cover-wrong",
    "ordinal": 248
  },
  {
    "callable_name": "mutate_CMD_count_assets_missing",
    "case_id": "CMD-count-assets-missing",
    "ordinal": 249
  },
  {
    "callable_name": "mutate_CMD_count_assets_wrong",
    "case_id": "CMD-count-assets-wrong",
    "ordinal": 250
  },
  {
    "callable_name": "mutate_CMD_count_referenced_assets_missing",
    "case_id": "CMD-count-referenced_assets-missing",
    "ordinal": 251
  },
  {
    "callable_name": "mutate_CMD_count_referenced_assets_wrong",
    "case_id": "CMD-count-referenced_assets-wrong",
    "ordinal": 252
  },
  {
    "callable_name": "mutate_CMD_count_unreferenced_assets_missing",
    "case_id": "CMD-count-unreferenced_assets-missing",
    "ordinal": 253
  },
  {
    "callable_name": "mutate_CMD_count_unreferenced_assets_wrong",
    "case_id": "CMD-count-unreferenced_assets-wrong",
    "ordinal": 254
  },
  {
    "callable_name": "mutate_CMD_count_markdown_references_missing",
    "case_id": "CMD-count-markdown_references-missing",
    "ordinal": 255
  },
  {
    "callable_name": "mutate_CMD_count_markdown_references_wrong",
    "case_id": "CMD-count-markdown_references-wrong",
    "ordinal": 256
  },
  {
    "callable_name": "mutate_CMD_sheet_count_wrong",
    "case_id": "CMD-sheet-count-wrong",
    "ordinal": 257
  },
  {
    "callable_name": "mutate_CMD_sheet_coverage_wrong",
    "case_id": "CMD-sheet-coverage-wrong",
    "ordinal": 258
  },
  {
    "callable_name": "mutate_CMD_sheet_missing",
    "case_id": "CMD-sheet-missing",
    "ordinal": 259
  },
  {
    "callable_name": "mutate_CMD_sheet_duplicate",
    "case_id": "CMD-sheet-duplicate",
    "ordinal": 260
  },
  {
    "callable_name": "mutate_CMD_sheet_id_wrong",
    "case_id": "CMD-sheet-id-wrong",
    "ordinal": 261
  },
  {
    "callable_name": "mutate_CMD_sheet_path_sequence_wrong",
    "case_id": "CMD-sheet-path-sequence-wrong",
    "ordinal": 262
  },
  {
    "callable_name": "mutate_CMD_sheet_grid_wrong",
    "case_id": "CMD-sheet-grid-wrong",
    "ordinal": 263
  },
  {
    "callable_name": "mutate_CMD_sheet_hash_wrong",
    "case_id": "CMD-sheet-hash-wrong",
    "ordinal": 264
  },
  {
    "callable_name": "mutate_CMD_flattened_page_missing",
    "case_id": "CMD-flattened-page-missing",
    "ordinal": 265
  },
  {
    "callable_name": "mutate_CMD_flattened_page_duplicate",
    "case_id": "CMD-flattened-page-duplicate",
    "ordinal": 266
  },
  {
    "callable_name": "mutate_CMD_flattened_page_order_wrong",
    "case_id": "CMD-flattened-page-order-wrong",
    "ordinal": 267
  },
  {
    "callable_name": "mutate_CMD_render_path_wrong",
    "case_id": "CMD-render-path-wrong",
    "ordinal": 268
  },
  {
    "callable_name": "mutate_CMD_render_hash_wrong",
    "case_id": "CMD-render-hash-wrong",
    "ordinal": 269
  },
  {
    "callable_name": "mutate_CMD_page_render_mapping_disagrees",
    "case_id": "CMD-page-render-mapping-disagrees",
    "ordinal": 270
  },
  {
    "callable_name": "mutate_CMD_verify_determinism_false",
    "case_id": "CMD-verify-determinism-false",
    "ordinal": 271
  },
  {
    "callable_name": "mutate_QAV_top_asset_count_missing",
    "case_id": "QAV-top-asset_count-missing",
    "ordinal": 272
  },
  {
    "callable_name": "mutate_QAV_top_block_count_missing",
    "case_id": "QAV-top-block_count-missing",
    "ordinal": 273
  },
  {
    "callable_name": "mutate_QAV_top_contact_sheet_count_missing",
    "case_id": "QAV-top-contact_sheet_count-missing",
    "ordinal": 274
  },
  {
    "callable_name": "mutate_QAV_top_contract_sha256_missing",
    "case_id": "QAV-top-contract_sha256-missing",
    "ordinal": 275
  },
  {
    "callable_name": "mutate_QAV_top_counts_missing",
    "case_id": "QAV-top-counts-missing",
    "ordinal": 276
  },
  {
    "callable_name": "mutate_QAV_top_gate_results_missing",
    "case_id": "QAV-top-gate_results-missing",
    "ordinal": 277
  },
  {
    "callable_name": "mutate_QAV_top_handout_count_missing",
    "case_id": "QAV-top-handout_count-missing",
    "ordinal": 278
  },
  {
    "callable_name": "mutate_QAV_top_historical_material_opened_missing",
    "case_id": "QAV-top-historical_material_opened-missing",
    "ordinal": 279
  },
  {
    "callable_name": "mutate_QAV_top_main_scripts_invoked_missing",
    "case_id": "QAV-top-main_scripts_invoked-missing",
    "ordinal": 280
  },
  {
    "callable_name": "mutate_QAV_top_navigation_anchor_count_missing",
    "case_id": "QAV-top-navigation_anchor_count-missing",
    "ordinal": 281
  },
  {
    "callable_name": "mutate_QAV_top_open_blocker_count_missing",
    "case_id": "QAV-top-open_blocker_count-missing",
    "ordinal": 282
  },
  {
    "callable_name": "mutate_QAV_top_output_inventory_missing",
    "case_id": "QAV-top-output_inventory-missing",
    "ordinal": 283
  },
  {
    "callable_name": "mutate_QAV_top_output_inventory_count_missing",
    "case_id": "QAV-top-output_inventory_count-missing",
    "ordinal": 284
  },
  {
    "callable_name": "mutate_QAV_top_output_inventory_rule_missing",
    "case_id": "QAV-top-output_inventory_rule-missing",
    "ordinal": 285
  },
  {
    "callable_name": "mutate_QAV_top_output_inventory_sha256_missing",
    "case_id": "QAV-top-output_inventory_sha256-missing",
    "ordinal": 286
  },
  {
    "callable_name": "mutate_QAV_top_page_count_missing",
    "case_id": "QAV-top-page_count-missing",
    "ordinal": 287
  },
  {
    "callable_name": "mutate_QAV_top_recovery_evidence_sha256_missing",
    "case_id": "QAV-top-recovery_evidence_sha256-missing",
    "ordinal": 288
  },
  {
    "callable_name": "mutate_QAV_top_recovery_manifest_sha256_missing",
    "case_id": "QAV-top-recovery_manifest_sha256-missing",
    "ordinal": 289
  },
  {
    "callable_name": "mutate_QAV_top_referenced_asset_count_missing",
    "case_id": "QAV-top-referenced_asset_count-missing",
    "ordinal": 290
  },
  {
    "callable_name": "mutate_QAV_top_schema_missing",
    "case_id": "QAV-top-schema-missing",
    "ordinal": 291
  },
  {
    "callable_name": "mutate_QAV_top_source_sha256_missing",
    "case_id": "QAV-top-source_sha256-missing",
    "ordinal": 292
  },
  {
    "callable_name": "mutate_QAV_top_state_missing",
    "case_id": "QAV-top-state-missing",
    "ordinal": 293
  },
  {
    "callable_name": "mutate_QAV_top_unreferenced_asset_count_missing",
    "case_id": "QAV-top-unreferenced_asset_count-missing",
    "ordinal": 294
  },
  {
    "callable_name": "mutate_QAV_top_extra",
    "case_id": "QAV-top-extra",
    "ordinal": 295
  },
  {
    "callable_name": "mutate_QAV_state_promoted",
    "case_id": "QAV-state-promoted",
    "ordinal": 296
  },
  {
    "callable_name": "mutate_QAV_authority_contract",
    "case_id": "QAV-authority-contract",
    "ordinal": 297
  },
  {
    "callable_name": "mutate_QAV_authority_source",
    "case_id": "QAV-authority-source",
    "ordinal": 298
  },
  {
    "callable_name": "mutate_QAV_authority_recovery_manifest",
    "case_id": "QAV-authority-recovery-manifest",
    "ordinal": 299
  },
  {
    "callable_name": "mutate_QAV_authority_recovery_evidence",
    "case_id": "QAV-authority-recovery-evidence",
    "ordinal": 300
  },
  {
    "callable_name": "mutate_QAV_scalar_page_count_wrong",
    "case_id": "QAV-scalar-page_count-wrong",
    "ordinal": 301
  },
  {
    "callable_name": "mutate_QAV_scalar_handout_count_wrong",
    "case_id": "QAV-scalar-handout_count-wrong",
    "ordinal": 302
  },
  {
    "callable_name": "mutate_QAV_scalar_block_count_wrong",
    "case_id": "QAV-scalar-block_count-wrong",
    "ordinal": 303
  },
  {
    "callable_name": "mutate_QAV_scalar_asset_count_wrong",
    "case_id": "QAV-scalar-asset_count-wrong",
    "ordinal": 304
  },
  {
    "callable_name": "mutate_QAV_scalar_contact_sheet_count_wrong",
    "case_id": "QAV-scalar-contact_sheet_count-wrong",
    "ordinal": 305
  },
  {
    "callable_name": "mutate_QAV_scalar_navigation_anchor_count_wrong",
    "case_id": "QAV-scalar-navigation_anchor_count-wrong",
    "ordinal": 306
  },
  {
    "callable_name": "mutate_QAV_scalar_referenced_asset_count_wrong",
    "case_id": "QAV-scalar-referenced_asset_count-wrong",
    "ordinal": 307
  },
  {
    "callable_name": "mutate_QAV_scalar_unreferenced_asset_count_wrong",
    "case_id": "QAV-scalar-unreferenced_asset_count-wrong",
    "ordinal": 308
  },
  {
    "callable_name": "mutate_QAV_scalar_open_blocker_count_wrong",
    "case_id": "QAV-scalar-open_blocker_count-wrong",
    "ordinal": 309
  },
  {
    "callable_name": "mutate_QAV_counts_assets_missing",
    "case_id": "QAV-counts-assets-missing",
    "ordinal": 310
  },
  {
    "callable_name": "mutate_QAV_counts_assets_wrong",
    "case_id": "QAV-counts-assets-wrong",
    "ordinal": 311
  },
  {
    "callable_name": "mutate_QAV_counts_back_cover_missing",
    "case_id": "QAV-counts-back_cover-missing",
    "ordinal": 312
  },
  {
    "callable_name": "mutate_QAV_counts_back_cover_wrong",
    "case_id": "QAV-counts-back_cover-wrong",
    "ordinal": 313
  },
  {
    "callable_name": "mutate_QAV_counts_contact_sheets_missing",
    "case_id": "QAV-counts-contact_sheets-missing",
    "ordinal": 314
  },
  {
    "callable_name": "mutate_QAV_counts_contact_sheets_wrong",
    "case_id": "QAV-counts-contact_sheets-wrong",
    "ordinal": 315
  },
  {
    "callable_name": "mutate_QAV_counts_engine_images_missing",
    "case_id": "QAV-counts-engine_images-missing",
    "ordinal": 316
  },
  {
    "callable_name": "mutate_QAV_counts_engine_images_wrong",
    "case_id": "QAV-counts-engine_images-wrong",
    "ordinal": 317
  },
  {
    "callable_name": "mutate_QAV_counts_engine_payload_missing",
    "case_id": "QAV-counts-engine_payload-missing",
    "ordinal": 318
  },
  {
    "callable_name": "mutate_QAV_counts_engine_payload_wrong",
    "case_id": "QAV-counts-engine_payload-wrong",
    "ordinal": 319
  },
  {
    "callable_name": "mutate_QAV_counts_handouts_missing",
    "case_id": "QAV-counts-handouts-missing",
    "ordinal": 320
  },
  {
    "callable_name": "mutate_QAV_counts_handouts_wrong",
    "case_id": "QAV-counts-handouts-wrong",
    "ordinal": 321
  },
  {
    "callable_name": "mutate_QAV_counts_maps_missing",
    "case_id": "QAV-counts-maps-missing",
    "ordinal": 322
  },
  {
    "callable_name": "mutate_QAV_counts_maps_wrong",
    "case_id": "QAV-counts-maps-wrong",
    "ordinal": 323
  },
  {
    "callable_name": "mutate_QAV_counts_navigation_anchors_missing",
    "case_id": "QAV-counts-navigation_anchors-missing",
    "ordinal": 324
  },
  {
    "callable_name": "mutate_QAV_counts_navigation_anchors_wrong",
    "case_id": "QAV-counts-navigation_anchors-wrong",
    "ordinal": 325
  },
  {
    "callable_name": "mutate_QAV_counts_open_blockers_missing",
    "case_id": "QAV-counts-open_blockers-missing",
    "ordinal": 326
  },
  {
    "callable_name": "mutate_QAV_counts_open_blockers_wrong",
    "case_id": "QAV-counts-open_blockers-wrong",
    "ordinal": 327
  },
  {
    "callable_name": "mutate_QAV_counts_pages_missing",
    "case_id": "QAV-counts-pages-missing",
    "ordinal": 328
  },
  {
    "callable_name": "mutate_QAV_counts_pages_wrong",
    "case_id": "QAV-counts-pages-wrong",
    "ordinal": 329
  },
  {
    "callable_name": "mutate_QAV_counts_pregens_missing",
    "case_id": "QAV-counts-pregens-missing",
    "ordinal": 330
  },
  {
    "callable_name": "mutate_QAV_counts_pregens_wrong",
    "case_id": "QAV-counts-pregens-wrong",
    "ordinal": 331
  },
  {
    "callable_name": "mutate_QAV_counts_referenced_assets_missing",
    "case_id": "QAV-counts-referenced_assets-missing",
    "ordinal": 332
  },
  {
    "callable_name": "mutate_QAV_counts_referenced_assets_wrong",
    "case_id": "QAV-counts-referenced_assets-wrong",
    "ordinal": 333
  },
  {
    "callable_name": "mutate_QAV_counts_renders_missing",
    "case_id": "QAV-counts-renders-missing",
    "ordinal": 334
  },
  {
    "callable_name": "mutate_QAV_counts_renders_wrong",
    "case_id": "QAV-counts-renders-wrong",
    "ordinal": 335
  },
  {
    "callable_name": "mutate_QAV_counts_unreferenced_assets_missing",
    "case_id": "QAV-counts-unreferenced_assets-missing",
    "ordinal": 336
  },
  {
    "callable_name": "mutate_QAV_counts_unreferenced_assets_wrong",
    "case_id": "QAV-counts-unreferenced_assets-wrong",
    "ordinal": 337
  },
  {
    "callable_name": "mutate_QAV_gate_asset_conservation_missing",
    "case_id": "QAV-gate-asset_conservation-missing",
    "ordinal": 338
  },
  {
    "callable_name": "mutate_QAV_gate_contact_sheet_coverage_missing",
    "case_id": "QAV-gate-contact_sheet_coverage-missing",
    "ordinal": 339
  },
  {
    "callable_name": "mutate_QAV_gate_navigation_anchors_missing",
    "case_id": "QAV-gate-navigation_anchors-missing",
    "ordinal": 340
  },
  {
    "callable_name": "mutate_QAV_gate_page_1_5_modes_missing",
    "case_id": "QAV-gate-page_1_5_modes-missing",
    "ordinal": 341
  },
  {
    "callable_name": "mutate_QAV_gate_page_coverage_missing",
    "case_id": "QAV-gate-page_coverage-missing",
    "ordinal": 342
  },
  {
    "callable_name": "mutate_QAV_gate_promotion_missing",
    "case_id": "QAV-gate-promotion-missing",
    "ordinal": 343
  },
  {
    "callable_name": "mutate_QAV_gate_recovery_admission_missing",
    "case_id": "QAV-gate-recovery_admission-missing",
    "ordinal": 344
  },
  {
    "callable_name": "mutate_QAV_gate_source_identity_missing",
    "case_id": "QAV-gate-source_identity-missing",
    "ordinal": 345
  },
  {
    "callable_name": "mutate_QAV_gate_visual_review_missing",
    "case_id": "QAV-gate-visual_review-missing",
    "ordinal": 346
  },
  {
    "callable_name": "mutate_QAV_gate_asset_conservation_wrong",
    "case_id": "QAV-gate-asset_conservation-wrong",
    "ordinal": 347
  },
  {
    "callable_name": "mutate_QAV_gate_contact_sheet_coverage_wrong",
    "case_id": "QAV-gate-contact_sheet_coverage-wrong",
    "ordinal": 348
  },
  {
    "callable_name": "mutate_QAV_gate_navigation_anchors_wrong",
    "case_id": "QAV-gate-navigation_anchors-wrong",
    "ordinal": 349
  },
  {
    "callable_name": "mutate_QAV_gate_page_coverage_wrong",
    "case_id": "QAV-gate-page_coverage-wrong",
    "ordinal": 350
  },
  {
    "callable_name": "mutate_QAV_gate_recovery_admission_wrong",
    "case_id": "QAV-gate-recovery_admission-wrong",
    "ordinal": 351
  },
  {
    "callable_name": "mutate_QAV_gate_source_identity_wrong",
    "case_id": "QAV-gate-source_identity-wrong",
    "ordinal": 352
  },
  {
    "callable_name": "mutate_QAV_gate_page_1_5_modes_closed",
    "case_id": "QAV-gate-page_1_5_modes-closed",
    "ordinal": 353
  },
  {
    "callable_name": "mutate_QAV_gate_promotion_closed",
    "case_id": "QAV-gate-promotion-closed",
    "ordinal": 354
  },
  {
    "callable_name": "mutate_QAV_gate_visual_review_closed",
    "case_id": "QAV-gate-visual_review-closed",
    "ordinal": 355
  },
  {
    "callable_name": "mutate_QAV_historical_material_true",
    "case_id": "QAV-historical-material-true",
    "ordinal": 356
  },
  {
    "callable_name": "mutate_QAV_main_scripts_invoked_true",
    "case_id": "QAV-main-scripts-invoked-true",
    "ordinal": 357
  },
  {
    "callable_name": "mutate_QAV_inventory_rule_wrong",
    "case_id": "QAV-inventory-rule-wrong",
    "ordinal": 358
  },
  {
    "callable_name": "mutate_QAV_inventory_count_wrong",
    "case_id": "QAV-inventory-count-wrong",
    "ordinal": 359
  },
  {
    "callable_name": "mutate_QAV_inventory_digest_wrong",
    "case_id": "QAV-inventory-digest-wrong",
    "ordinal": 360
  },
  {
    "callable_name": "mutate_QAV_inventory_array_wrong",
    "case_id": "QAV-inventory-array-wrong",
    "ordinal": 361
  },
  {
    "callable_name": "mutate_REG_P1_stale_metadata",
    "case_id": "REG-P1-stale-metadata",
    "ordinal": 362
  },
  {
    "callable_name": "mutate_REG_P1_missing_enforcement",
    "case_id": "REG-P1-missing-enforcement",
    "ordinal": 363
  },
  {
    "callable_name": "mutate_INJ_profile_seal_mutated",
    "case_id": "INJ-profile-seal-mutated",
    "ordinal": 364
  },
  {
    "callable_name": "mutate_INJ_test_route_given_production_profile",
    "case_id": "INJ-test-route-given-production-profile",
    "ordinal": 365
  },
  {
    "callable_name": "mutate_INJ_identity_provider_bound_to_other_profile",
    "case_id": "INJ-identity-provider-bound-to-other-profile",
    "ordinal": 366
  },
  {
    "callable_name": "mutate_INJ_filesystem_provider_bound_to_other_profile",
    "case_id": "INJ-filesystem-provider-bound-to-other-profile",
    "ordinal": 367
  },
  {
    "callable_name": "mutate_INJ_repository_root_observation_mismatch",
    "case_id": "INJ-repository-root-observation-mismatch",
    "ordinal": 368
  }
]
<!-- REGISTRY_JSON_END -->

<!-- ALIAS_PAIRS_JSON_BEGIN -->
[
  {
    "distinct_callable_names": true,
    "distinct_case_ids": true,
    "left": {
      "callable_name": "mutate_SCH_QA_required_top_member_missing",
      "case_id": "SCH-QA-required-top-member-missing",
      "ordinal": 81
    },
    "right": {
      "callable_name": "mutate_QAV_top_asset_count_missing",
      "case_id": "QAV-top-asset_count-missing",
      "ordinal": 272
    }
  },
  {
    "distinct_callable_names": true,
    "distinct_case_ids": true,
    "left": {
      "callable_name": "mutate_SCH_qa_unexpected_top_member",
      "case_id": "SCH-qa-unexpected-top-member",
      "ordinal": 104
    },
    "right": {
      "callable_name": "mutate_QAV_top_extra",
      "case_id": "QAV-top-extra",
      "ordinal": 295
    }
  },
  {
    "distinct_callable_names": true,
    "distinct_case_ids": true,
    "left": {
      "callable_name": "mutate_INV_cardinality_wrong",
      "case_id": "INV-cardinality-wrong",
      "ordinal": 117
    },
    "right": {
      "callable_name": "mutate_QAV_inventory_count_wrong",
      "case_id": "QAV-inventory-count-wrong",
      "ordinal": 359
    }
  },
  {
    "distinct_callable_names": true,
    "distinct_case_ids": true,
    "left": {
      "callable_name": "mutate_INV_digest_wrong",
      "case_id": "INV-digest-wrong",
      "ordinal": 122
    },
    "right": {
      "callable_name": "mutate_QAV_inventory_digest_wrong",
      "case_id": "QAV-inventory-digest-wrong",
      "ordinal": 360
    }
  },
  {
    "distinct_callable_names": true,
    "distinct_case_ids": true,
    "left": {
      "callable_name": "mutate_INV_ordinary_row_missing",
      "case_id": "INV-ordinary-row-missing",
      "ordinal": 111
    },
    "right": {
      "callable_name": "mutate_QAV_inventory_array_wrong",
      "case_id": "QAV-inventory-array-wrong",
      "ordinal": 361
    }
  },
  {
    "distinct_callable_names": true,
    "distinct_case_ids": true,
    "left": {
      "callable_name": "mutate_CMD_count_pages_wrong",
      "case_id": "CMD-count-pages-wrong",
      "ordinal": 236
    },
    "right": {
      "callable_name": "mutate_REG_P1_missing_enforcement",
      "case_id": "REG-P1-missing-enforcement",
      "ordinal": 363
    }
  }
]
<!-- ALIAS_PAIRS_JSON_END -->

<!-- PROFILE_ROUTE_JSON_BEGIN -->
{
  "frozen_material_post_correction": {
    "library_sha256": "9802571C128D63DE5D643425FDA361EB2E032A5AE830ED9713B83A3A413B5855",
    "tests_sha256": "FA70BBAE285EAAA10E1F6BAF90119008342A18552E580E4E8530D9462997D5F9"
  },
  "frozen_material_pre_report": {
    "library_sha256": "0A1B84C9CAD20E56F272B9311925A13926A487DFCB21F4C2570B0A7F9CCD2EAD",
    "note": "0A1B84 was the stale pre-ordering-repair report, not the frozen implementation reviewed here.",
    "tests_sha256": "FA70BBAE285EAAA10E1F6BAF90119008342A18552E580E4E8530D9462997D5F9"
  },
  "profile_seal_recomputed": "1893BF7B2838E8DDCE6E6FA0E07F900A261308BC341DDA152803D28EF01BD00B",
  "profile_serialization": {
    "authority_sha256": "1893BF7B2838E8DDCE6E6FA0E07F900A261308BC341DDA152803D28EF01BD00B",
    "kind": "test",
    "profile_id": "strict-fixture"
  },
  "providers": {
    "filesystem": {
      "bound_profile_sha256": "1893BF7B2838E8DDCE6E6FA0E07F900A261308BC341DDA152803D28EF01BD00B",
      "provider_id": "fixture-filesystem",
      "type": "TestFilesystemProvider"
    },
    "identity": {
      "bound_profile_sha256": "1893BF7B2838E8DDCE6E6FA0E07F900A261308BC341DDA152803D28EF01BD00B",
      "provider_id": null,
      "type": "_Provider"
    }
  },
  "public_signatures": {
    "_test_build": "(contract_path: 'Path', source_path: 'Path', recovery_root: 'Path', run_root: 'Path', *, context: 'EnforcementContext') -> 'dict[str, object]'",
    "_test_preflight": "(contract_path: 'Path', source_path: 'Path', recovery_root: 'Path', run_root: 'Path', *, context: 'EnforcementContext') -> 'dict[str, object]'",
    "_test_verify": "(contract_path: 'Path', source_path: 'Path', recovery_root: 'Path', run_root: 'Path', *, context: 'EnforcementContext') -> 'dict[str, object]'",
    "build": "(contract_path: 'Path', source_path: 'Path', recovery_root: 'Path', run_root: 'Path') -> 'dict[str, object]'",
    "preflight": "(contract_path: 'Path', source_path: 'Path', recovery_root: 'Path', run_root: 'Path') -> 'dict[str, object]'",
    "verify": "(contract_path: 'Path', source_path: 'Path', recovery_root: 'Path', run_root: 'Path') -> 'dict[str, object]'"
  },
  "route_table": [
    {
      "downstream": "_strict_verify",
      "entrypoints": [
        "preflight",
        "build",
        "verify"
      ],
      "required_context_identity": "PRODUCTION_CONTEXT",
      "required_profile_identity": "PRODUCTION_PROFILE",
      "route": "public"
    },
    {
      "downstream": "_strict_verify",
      "entrypoints": [
        "_test_preflight",
        "_test_build",
        "_test_verify"
      ],
      "required_context_kind": "test and not PRODUCTION_CONTEXT",
      "route": "test"
    }
  ]
}
<!-- PROFILE_ROUTE_JSON_END -->

<!-- BLD_CAPTURE_JSON_BEGIN -->
{
  "capture_command": "bounded inline Python against frozen helpers; one TemporaryDirectory automatically cleaned",
  "existing_target_public_test_helper": {
    "final_file_id_before_after": "EXISTING_FINAL",
    "helpers": [
      "_test_build"
    ],
    "immutable": true,
    "observed_code": "E_BUILD_OVERWRITE",
    "result_status": "PASS",
    "sentinel_bytes": "keep",
    "sentinel_sha256": "6CA7EA2FEEFC88ECB5ED6356ED963F47DC9137F82526FDD25D618EA626D0803F",
    "siblings_before_after": [
      "candidate",
      "contract.json",
      "recovery",
      "source"
    ],
    "temp_or_marker_siblings": []
  },
  "finalizer_parity_real_helpers": {
    "byte_identical": true,
    "file_count_left": 502,
    "file_count_right": 502,
    "finalizer_verify": {
      "deterministic": true,
      "fixture_files": 502,
      "outside_fixture_reads": 0,
      "state": "test_verified"
    },
    "functions": [
      "_test_build",
      "_owned",
      "_write_non_qa_bundle",
      "_finalize_and_verify",
      "remove_owned_tree"
    ],
    "manifests_build_and_staged": {
      "500": "A75CFBE93520CE8193B30ED4EE291836BDC537B5E86F6B591E1B7A7C7BB4EDEA",
      "501": "88813CEF31FE1BDA83319F8E072324BFBE6578E9BD709FF52470D69B25B9805C",
      "502": "A8D4C2FC724BE228AF487413908E761D21A3E186809EE3F613BC9FFB98C2E31F"
    },
    "result_status": "PASS",
    "states_after_remove_owned_tree": {
      "final_present": false,
      "marker_present": false,
      "temp_present": false
    },
    "states_before_cleanup": {
      "final_present": false,
      "marker_present": true,
      "temp_file_id": "PARITY_TEMP",
      "temp_present": true
    }
  },
  "fresh_public_test_helper": {
    "helpers": [
      "_test_build",
      "_test_verify"
    ],
    "manifests": {
      "500": "A75CFBE93520CE8193B30ED4EE291836BDC537B5E86F6B591E1B7A7C7BB4EDEA",
      "501": "88813CEF31FE1BDA83319F8E072324BFBE6578E9BD709FF52470D69B25B9805C",
      "502": "A8D4C2FC724BE228AF487413908E761D21A3E186809EE3F613BC9FFB98C2E31F"
    },
    "normalized_file_id": "FRESH_FINAL",
    "result": {
      "fixture_files": 502,
      "state": "built_candidate_needs_review"
    },
    "result_status": "PASS",
    "states": [
      "final_missing",
      "owned_temp_and_marker_created_inside__test_build",
      "final_published_temp_absent_marker_absent"
    ],
    "verifier_phases": [
      "post-finalize _finalize_and_verify",
      "post-publish _strict_verify",
      "independent _test_verify #1",
      "independent _test_verify #2"
    ],
    "verifier_results": [
      {
        "deterministic": true,
        "fixture_files": 502,
        "outside_fixture_reads": 0,
        "state": "test_verified"
      },
      {
        "deterministic": true,
        "fixture_files": 502,
        "outside_fixture_reads": 0,
        "state": "test_verified"
      }
    ]
  },
  "native_exit": 0,
  "owned_lifecycle_real_helpers": {
    "functions": [
      "_owned",
      "_write_non_qa_bundle",
      "_finalize_and_verify",
      "_validate_owned",
      "rename_no_replace",
      "_strict_verify"
    ],
    "manifests": {
      "500": "A75CFBE93520CE8193B30ED4EE291836BDC537B5E86F6B591E1B7A7C7BB4EDEA",
      "501": "88813CEF31FE1BDA83319F8E072324BFBE6578E9BD709FF52470D69B25B9805C",
      "502": "A8D4C2FC724BE228AF487413908E761D21A3E186809EE3F613BC9FFB98C2E31F"
    },
    "owned_state": {
      "final_name": "candidate",
      "final_present": false,
      "marker_file_id_tokens": [
        "OWNED_TEMP_DEV",
        "OWNED_TEMP_INO"
      ],
      "marker_present": true,
      "nonce": "REDACTED_RUNTIME_NONCE",
      "profile_sha256": "1893BF7B2838E8DDCE6E6FA0E07F900A261308BC341DDA152803D28EF01BD00B",
      "temp_file_id": "OWNED_TEMP",
      "temp_name_pattern": ".candidate.tmp-PID-NONCE",
      "temp_present": true
    },
    "post_marker_cleanup": {
      "final_present": true,
      "marker_present": false,
      "temp_present": false
    },
    "post_publish_verify": {
      "deterministic": true,
      "fixture_files": 502,
      "outside_fixture_reads": 0,
      "state": "test_verified"
    },
    "post_rename": {
      "file_id_preserved": true,
      "final_file_id": "OWNED_TEMP",
      "final_present": true,
      "marker_present": true,
      "temp_present": false
    },
    "result_status": "PASS"
  },
  "result": "PASS"
}
<!-- BLD_CAPTURE_JSON_END -->

<!-- PARSE_BACK_PROOF_JSON_BEGIN -->
{
  "aliases_parse_back": {
    "all_distinct": true,
    "frozen_cross_family_pairs": [
      [
        "SCH-QA-required-top-member-missing",
        "QAV-top-asset_count-missing"
      ],
      [
        "SCH-qa-unexpected-top-member",
        "QAV-top-extra"
      ],
      [
        "INV-cardinality-wrong",
        "QAV-inventory-count-wrong"
      ],
      [
        "INV-digest-wrong",
        "QAV-inventory-digest-wrong"
      ],
      [
        "INV-ordinary-row-missing",
        "QAV-inventory-array-wrong"
      ],
      [
        "CMD-count-pages-wrong",
        "REG-P1-missing-enforcement"
      ]
    ],
    "matches_frozen_declaration": true,
    "member_count": 12,
    "pairs": 6
  },
  "audits_json_parse_back": {
    "objects": 368,
    "payload_sha256": "4719BC2C3606EF04B0813D5A3D55F3C969181B4990605C7C0564761CDD632EC7",
    "unique_case_ids": 368
  },
  "bounded_bld_capture_native_exit": 0,
  "canonical_rows_parse_back": {
    "bytes": 51005,
    "rows": 368,
    "sha256": "8C5C2A0A69C212465D1429FA38B35A4802C9AFCDF52F9461A1747D5729671DD4",
    "terminating_newline_included": true
  },
  "control_chars": {
    "disallowed_count": 0,
    "permitted_newline_and_cr_only": true,
    "permitted_tab_count": 1840
  },
  "frozen_files_rechecked": {
    "library_sha256": "9802571C128D63DE5D643425FDA361EB2E032A5AE830ED9713B83A3A413B5855",
    "tests_sha256": "FA70BBAE285EAAA10E1F6BAF90119008342A18552E580E4E8530D9462997D5F9"
  },
  "registry_parse_back": {
    "objects": 368,
    "unique_callable_names": 368,
    "unique_case_ids": 368
  }
}
<!-- PARSE_BACK_PROOF_JSON_END -->

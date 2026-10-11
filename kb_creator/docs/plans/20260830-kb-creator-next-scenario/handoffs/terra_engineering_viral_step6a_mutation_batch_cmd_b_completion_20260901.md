# Terra engineering completion receipt — Viral Step 6A CMD-B

- Timestamp: 2026-09-01 Europe/Moscow; elapsed/token use: unavailable.
- Assignment state: completed evidence-only CMD-B scope.
- Orchestrator policy owner: main chat `gpt-5.6-sol / medium`; no ownership transfer.
- Scope: validates only the previous cache-baseline disposition and CMD-B evidence. Code/tests, blocked receipt, candidate/source/recovery/protected/Git/cache were read-only.

## Limited supersession

This receipt supersedes **only** the prior receipt's conclusion that the unchanged pre-existing cache made CMD-B non-integrable. It preserves the historical blocked receipt and all of its evidence. It makes no Step 6A, QA, release, candidate, semantic, promotion, or publication acceptance claim.

## Immutable baselines

- Completion packet SHA-256: `ADEB2FDA32DBEF89EE818853056EFA4C9538A3FFB808720A8496692C619083E5`.
- Accepted critic assignment review is bound by packet: `FEB102C7F2DA4B29EC34360C721CD52A37A2DACD6D6A6AE3E558CFC878E47269`.
- Library before/after: `231C976E57D6DC1051C326C479EC42D87525DDB8565741A0D64A0E96B37352C7` / unchanged.
- Tests before/after: `59C148D64F5CAB7B6D50723A4C10D5AD292FC0449D839CDB963DFE6F2403F1EF` / unchanged.
- Historical BLOCKED receipt before/after: `AE658CBED70482120B7482EB4C44BCA3F95D5FBEB8339295DD7DA5824B49A65E` / unchanged.

## Commands and results

All commands used `python -B` and pytest `-p no:cacheprovider`.

- CMD-B explicit chunks: `6 + 6 + 6 + 4 = 22 passed`, native exit 0.
- Representative CMD-A/SRC regression: `2 passed`, native exit 0.
- BLD: `3 passed`, native exit 0.
- Focused collection: `371 tests collected`, native exit 0.
- Stdout/stderr hashes: unavailable because this evidence-only dispatch retained no logs; command output was observed directly and no log artifact was permitted.

All 22 test nodes re-materialized their full Section-11 audit objects through `apply_case`/one `_test_verify`. Canonical packet-formula rows: 22, UTF-8/LF, **3436 bytes**, SHA-256 **`EA147EE49823AD16310D654B1E3B8D26D03852CB78779B97CD29B805035A971D`**.

## Cache baseline: before equals after

| Target | Before SHA-256 | After SHA-256 |
|---|---|---|
| `kb_creator/scripts/__pycache__/scenario_contract.cpython-313.pyc` | `168C67BC8784F76DBA57F873A32B419112998AA359C9F1A21BF3E954D3BD13C4` | same |
| `kb_creator/tests/__pycache__/test_scenario_contract.cpython-313-pytest-9.0.2.pyc` | `9F4E03CC81C749C4C29FD0F97478D3EB1A2EF735D1B225DAD191B0D451FBEF54` | same |
| `kb_creator/tests/__pycache__/test_scenario_source_reconstruction.cpython-313-pytest-9.0.2.pyc` | `DE4E516486951CE4EA9DA7621C54D7429489B0ABAB3CE1F58B28309457BDF0B9` | same |
| `.pytest_cache` | directory present; creation `2026-08-30T17:58:46Z`, last-write `2026-08-31T23:02:46Z`, seven baseline paths | identical identity and path set |

No new cache, fixture, temp sibling, owner marker, probe, log, or bytecode path was attributable to this dispatch.

## Exact changed paths

- Added only: `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_step6a_mutation_batch_cmd_b_completion_20260901.md`.
- Modified/deleted by this dispatch: none.
- Blockers: none within this evidence-only scope.

## Full CMD-B mutation audit JSON

```json
[
  {
    "case_id": "CMD-count-pages-missing",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/counts/pages",
    "semantic_before_sha256": "6C3A83C9B602D142F18DF3F9CB243AEF37C6ECC2A2943364F8EE344628990BA9",
    "semantic_after_sha256": "7DB5EC18D6FD33D91CE29FE72236D2426E6806E0EB6CC238E2E4D9F53810BCB8",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/counts/pages"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "expected_code": "E_COMMAND_COUNTS_PAGES",
    "observed_code": "E_COMMAND_COUNTS_PAGES",
    "strict_verify_calls": 1,
    "outside_fixture_reads": 0,
    "undeclared_changes": [],
    "residue": [],
    "result": "PASS"
  },
  {
    "case_id": "CMD-count-pages-wrong",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/counts/pages",
    "semantic_before_sha256": "6C3A83C9B602D142F18DF3F9CB243AEF37C6ECC2A2943364F8EE344628990BA9",
    "semantic_after_sha256": "719B7129C270F3051391DA73C631B46087C0B7D5E624438291882784711D913B",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/counts/pages"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "expected_code": "E_COMMAND_COUNTS_PAGES",
    "observed_code": "E_COMMAND_COUNTS_PAGES",
    "strict_verify_calls": 1,
    "outside_fixture_reads": 0,
    "undeclared_changes": [],
    "residue": [],
    "result": "PASS"
  },
  {
    "case_id": "CMD-count-renders-missing",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/counts/renders",
    "semantic_before_sha256": "6C3A83C9B602D142F18DF3F9CB243AEF37C6ECC2A2943364F8EE344628990BA9",
    "semantic_after_sha256": "78607F2FDE99C64B36134788A38B65A52171C10488435B6E9850839C65105878",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/counts/renders"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "expected_code": "E_COMMAND_COUNTS_RENDERS",
    "observed_code": "E_COMMAND_COUNTS_RENDERS",
    "strict_verify_calls": 1,
    "outside_fixture_reads": 0,
    "undeclared_changes": [],
    "residue": [],
    "result": "PASS"
  },
  {
    "case_id": "CMD-count-renders-wrong",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/counts/renders",
    "semantic_before_sha256": "6C3A83C9B602D142F18DF3F9CB243AEF37C6ECC2A2943364F8EE344628990BA9",
    "semantic_after_sha256": "22AE3E379D25761AD036A97469B7D6EA83BEC4AEE001FDE5112FC73E96F2FD0E",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/counts/renders"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "expected_code": "E_COMMAND_COUNTS_RENDERS",
    "observed_code": "E_COMMAND_COUNTS_RENDERS",
    "strict_verify_calls": 1,
    "outside_fixture_reads": 0,
    "undeclared_changes": [],
    "residue": [],
    "result": "PASS"
  },
  {
    "case_id": "CMD-count-contact_sheets-missing",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/counts/contact_sheets",
    "semantic_before_sha256": "6C3A83C9B602D142F18DF3F9CB243AEF37C6ECC2A2943364F8EE344628990BA9",
    "semantic_after_sha256": "DF40381C4C6C64034D35DC252145A705C0F318B8419D60D32FE8BCD61EC9A391",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/counts/contact_sheets"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "expected_code": "E_COMMAND_COUNTS_CONTACT_SHEETS",
    "observed_code": "E_COMMAND_COUNTS_CONTACT_SHEETS",
    "strict_verify_calls": 1,
    "outside_fixture_reads": 0,
    "undeclared_changes": [],
    "residue": [],
    "result": "PASS"
  },
  {
    "case_id": "CMD-count-contact_sheets-wrong",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/counts/contact_sheets",
    "semantic_before_sha256": "6C3A83C9B602D142F18DF3F9CB243AEF37C6ECC2A2943364F8EE344628990BA9",
    "semantic_after_sha256": "47649E8455C6C649B6A77FFC7B01DA30E21475833026D1D37BCB56CA5C54AFC1",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/counts/contact_sheets"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "expected_code": "E_COMMAND_COUNTS_CONTACT_SHEETS",
    "observed_code": "E_COMMAND_COUNTS_CONTACT_SHEETS",
    "strict_verify_calls": 1,
    "outside_fixture_reads": 0,
    "undeclared_changes": [],
    "residue": [],
    "result": "PASS"
  },
  {
    "case_id": "CMD-count-handouts-missing",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/counts/handouts",
    "semantic_before_sha256": "6C3A83C9B602D142F18DF3F9CB243AEF37C6ECC2A2943364F8EE344628990BA9",
    "semantic_after_sha256": "98C5231EFBD2024E5D68CC3A681FEBAEA09355FF767B42D3D56BF9B7882ED36D",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/counts/handouts"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "expected_code": "E_COMMAND_COUNTS_HANDOUTS",
    "observed_code": "E_COMMAND_COUNTS_HANDOUTS",
    "strict_verify_calls": 1,
    "outside_fixture_reads": 0,
    "undeclared_changes": [],
    "residue": [],
    "result": "PASS"
  },
  {
    "case_id": "CMD-count-handouts-wrong",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/counts/handouts",
    "semantic_before_sha256": "6C3A83C9B602D142F18DF3F9CB243AEF37C6ECC2A2943364F8EE344628990BA9",
    "semantic_after_sha256": "2A5011F9D5D0DC3822D5501F427E8D39E106CB2C35CEB98559AAA3BBAFAD626E",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/counts/handouts"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "expected_code": "E_COMMAND_COUNTS_HANDOUTS",
    "observed_code": "E_COMMAND_COUNTS_HANDOUTS",
    "strict_verify_calls": 1,
    "outside_fixture_reads": 0,
    "undeclared_changes": [],
    "residue": [],
    "result": "PASS"
  },
  {
    "case_id": "CMD-count-maps-missing",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/counts/maps",
    "semantic_before_sha256": "6C3A83C9B602D142F18DF3F9CB243AEF37C6ECC2A2943364F8EE344628990BA9",
    "semantic_after_sha256": "1584006BA9627139DC8A405027D6E373A8E4E23C8A6F6F864CE49199C628C6D7",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/counts/maps"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "expected_code": "E_COMMAND_COUNTS_MAPS",
    "observed_code": "E_COMMAND_COUNTS_MAPS",
    "strict_verify_calls": 1,
    "outside_fixture_reads": 0,
    "undeclared_changes": [],
    "residue": [],
    "result": "PASS"
  },
  {
    "case_id": "CMD-count-maps-wrong",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/counts/maps",
    "semantic_before_sha256": "6C3A83C9B602D142F18DF3F9CB243AEF37C6ECC2A2943364F8EE344628990BA9",
    "semantic_after_sha256": "18109F48E44D052B24779A7B1EAA86CF4A3BEDBAC077C94908647B63F10545CF",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/counts/maps"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "expected_code": "E_COMMAND_COUNTS_MAPS",
    "observed_code": "E_COMMAND_COUNTS_MAPS",
    "strict_verify_calls": 1,
    "outside_fixture_reads": 0,
    "undeclared_changes": [],
    "residue": [],
    "result": "PASS"
  },
  {
    "case_id": "CMD-count-pregens-missing",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/counts/pregens",
    "semantic_before_sha256": "6C3A83C9B602D142F18DF3F9CB243AEF37C6ECC2A2943364F8EE344628990BA9",
    "semantic_after_sha256": "4019E15F53BF9B95D11225ECB2CC927F404CD3315EFBEF43CA0DD51DA07AE2CB",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/counts/pregens"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "expected_code": "E_COMMAND_COUNTS_PREGENS",
    "observed_code": "E_COMMAND_COUNTS_PREGENS",
    "strict_verify_calls": 1,
    "outside_fixture_reads": 0,
    "undeclared_changes": [],
    "residue": [],
    "result": "PASS"
  },
  {
    "case_id": "CMD-count-pregens-wrong",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/counts/pregens",
    "semantic_before_sha256": "6C3A83C9B602D142F18DF3F9CB243AEF37C6ECC2A2943364F8EE344628990BA9",
    "semantic_after_sha256": "3B01BCE28A704E3F6AF97FFCAA93F1913077959600C671EDBC311F6EAF097119",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/counts/pregens"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "expected_code": "E_COMMAND_COUNTS_PREGENS",
    "observed_code": "E_COMMAND_COUNTS_PREGENS",
    "strict_verify_calls": 1,
    "outside_fixture_reads": 0,
    "undeclared_changes": [],
    "residue": [],
    "result": "PASS"
  },
  {
    "case_id": "CMD-count-back_cover-missing",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/counts/back_cover",
    "semantic_before_sha256": "6C3A83C9B602D142F18DF3F9CB243AEF37C6ECC2A2943364F8EE344628990BA9",
    "semantic_after_sha256": "6E88B3E24FB6ED4F49AD0C682C17A67DDA10E79949EFCC269780BC105682847F",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/counts/back_cover"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "expected_code": "E_COMMAND_COUNTS_BACK_COVER",
    "observed_code": "E_COMMAND_COUNTS_BACK_COVER",
    "strict_verify_calls": 1,
    "outside_fixture_reads": 0,
    "undeclared_changes": [],
    "residue": [],
    "result": "PASS"
  },
  {
    "case_id": "CMD-count-back_cover-wrong",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/counts/back_cover",
    "semantic_before_sha256": "6C3A83C9B602D142F18DF3F9CB243AEF37C6ECC2A2943364F8EE344628990BA9",
    "semantic_after_sha256": "139514733FBA493CAA70CB46801E14B6BBF2B11D41DCDAF34EA41651FFF07783",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/counts/back_cover"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "expected_code": "E_COMMAND_COUNTS_BACK_COVER",
    "observed_code": "E_COMMAND_COUNTS_BACK_COVER",
    "strict_verify_calls": 1,
    "outside_fixture_reads": 0,
    "undeclared_changes": [],
    "residue": [],
    "result": "PASS"
  },
  {
    "case_id": "CMD-count-assets-missing",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/counts/assets",
    "semantic_before_sha256": "6C3A83C9B602D142F18DF3F9CB243AEF37C6ECC2A2943364F8EE344628990BA9",
    "semantic_after_sha256": "EA45748B94EB605F4447ADB1ABB52A9AB5EB7EE0C91849B2B86B90E53E091980",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/counts/assets"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "expected_code": "E_COMMAND_COUNTS_ASSETS",
    "observed_code": "E_COMMAND_COUNTS_ASSETS",
    "strict_verify_calls": 1,
    "outside_fixture_reads": 0,
    "undeclared_changes": [],
    "residue": [],
    "result": "PASS"
  },
  {
    "case_id": "CMD-count-assets-wrong",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/counts/assets",
    "semantic_before_sha256": "6C3A83C9B602D142F18DF3F9CB243AEF37C6ECC2A2943364F8EE344628990BA9",
    "semantic_after_sha256": "317014F210492CC76E88DF5ABFC2529D33CB5CE8F4B71C6AA6CD79F4615928A4",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/counts/assets"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "expected_code": "E_COMMAND_COUNTS_ASSETS",
    "observed_code": "E_COMMAND_COUNTS_ASSETS",
    "strict_verify_calls": 1,
    "outside_fixture_reads": 0,
    "undeclared_changes": [],
    "residue": [],
    "result": "PASS"
  },
  {
    "case_id": "CMD-count-referenced_assets-missing",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/counts/referenced_assets",
    "semantic_before_sha256": "6C3A83C9B602D142F18DF3F9CB243AEF37C6ECC2A2943364F8EE344628990BA9",
    "semantic_after_sha256": "CBF836D516870881060BA9DD4416A49514B751E148BE1CF4B53DA3A4081FAC99",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/counts/referenced_assets"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "expected_code": "E_COMMAND_COUNTS_REFERENCED_ASSETS",
    "observed_code": "E_COMMAND_COUNTS_REFERENCED_ASSETS",
    "strict_verify_calls": 1,
    "outside_fixture_reads": 0,
    "undeclared_changes": [],
    "residue": [],
    "result": "PASS"
  },
  {
    "case_id": "CMD-count-referenced_assets-wrong",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/counts/referenced_assets",
    "semantic_before_sha256": "6C3A83C9B602D142F18DF3F9CB243AEF37C6ECC2A2943364F8EE344628990BA9",
    "semantic_after_sha256": "DE426D22C6E735D2F8A98CD614B9FB25F53E6E0F49EE5C5F2226387EA7C12C57",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/counts/referenced_assets"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "expected_code": "E_COMMAND_COUNTS_REFERENCED_ASSETS",
    "observed_code": "E_COMMAND_COUNTS_REFERENCED_ASSETS",
    "strict_verify_calls": 1,
    "outside_fixture_reads": 0,
    "undeclared_changes": [],
    "residue": [],
    "result": "PASS"
  },
  {
    "case_id": "CMD-count-unreferenced_assets-missing",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/counts/unreferenced_assets",
    "semantic_before_sha256": "6C3A83C9B602D142F18DF3F9CB243AEF37C6ECC2A2943364F8EE344628990BA9",
    "semantic_after_sha256": "3C9B138CE51F9BDCAAB8013E4FAAD8BF50834072AA13E7F208A7DAC16A0418EC",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/counts/unreferenced_assets"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "expected_code": "E_COMMAND_COUNTS_UNREFERENCED_ASSETS",
    "observed_code": "E_COMMAND_COUNTS_UNREFERENCED_ASSETS",
    "strict_verify_calls": 1,
    "outside_fixture_reads": 0,
    "undeclared_changes": [],
    "residue": [],
    "result": "PASS"
  },
  {
    "case_id": "CMD-count-unreferenced_assets-wrong",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/counts/unreferenced_assets",
    "semantic_before_sha256": "6C3A83C9B602D142F18DF3F9CB243AEF37C6ECC2A2943364F8EE344628990BA9",
    "semantic_after_sha256": "904F37DC1C779541D368F8052034DB5037ED64C0ECE793A48C38BDBC4C132537",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/counts/unreferenced_assets"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "expected_code": "E_COMMAND_COUNTS_UNREFERENCED_ASSETS",
    "observed_code": "E_COMMAND_COUNTS_UNREFERENCED_ASSETS",
    "strict_verify_calls": 1,
    "outside_fixture_reads": 0,
    "undeclared_changes": [],
    "residue": [],
    "result": "PASS"
  },
  {
    "case_id": "CMD-count-markdown_references-missing",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/counts/markdown_references",
    "semantic_before_sha256": "6C3A83C9B602D142F18DF3F9CB243AEF37C6ECC2A2943364F8EE344628990BA9",
    "semantic_after_sha256": "49BC5D9B41CDE95B4A0314AC6CC28B8545AB25D064C64BE498285940E7E9F015",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/counts/markdown_references"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "expected_code": "E_COMMAND_COUNTS_MARKDOWN_REFERENCES",
    "observed_code": "E_COMMAND_COUNTS_MARKDOWN_REFERENCES",
    "strict_verify_calls": 1,
    "outside_fixture_reads": 0,
    "undeclared_changes": [],
    "residue": [],
    "result": "PASS"
  },
  {
    "case_id": "CMD-count-markdown_references-wrong",
    "family": "CMD",
    "fixture_root_token": "fixture",
    "semantic_selector": "candidate/evidence/COMMANDS.json#/counts/markdown_references",
    "semantic_before_sha256": "6C3A83C9B602D142F18DF3F9CB243AEF37C6ECC2A2943364F8EE344628990BA9",
    "semantic_after_sha256": "20DA84D4CA405440C099D282E8317171026AAC72EE7268C1739D7D76BC71AD72",
    "changed_before_reseal": [
      "candidate/evidence/COMMANDS.json#/counts/markdown_references"
    ],
    "declared_reseals": [
      "inventory",
      "qa"
    ],
    "changed_by_reseal": [
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory",
      "candidate/RECONSTRUCTED_EN.qa.json#/output_inventory_sha256"
    ],
    "expected_code": "E_COMMAND_COUNTS_MARKDOWN_REFERENCES",
    "observed_code": "E_COMMAND_COUNTS_MARKDOWN_REFERENCES",
    "strict_verify_calls": 1,
    "outside_fixture_reads": 0,
    "undeclared_changes": [],
    "residue": [],
    "result": "PASS"
  }
]
```


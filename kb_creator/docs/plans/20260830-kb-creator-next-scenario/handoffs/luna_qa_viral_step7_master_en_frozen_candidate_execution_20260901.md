# Luna QA receipt — Viral Step 7 MASTER_EN frozen candidate execution

- Assignment: execute the frozen Viral Step 7 MASTER_EN candidate QA packet.
- Packet: `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_orchestrator_viral_step7_master_en_frozen_candidate_execution_20260901.md`
- Packet SHA-256: `7B159690C0C689DF52BB17724F5C7111330DA247E69D57FA99F2604CBC9DB3AA`
- Scope: `gpt-5.6-luna / high`, bounded read-only QA execution plus the two
  packet-authorized candidate builds and this receipt.
- Result: `PASS_FROZEN_CANDIDATE_EXECUTION`
- Candidate acceptance/release: not granted by this execution.

## Frozen command results (raw JSON)

1. Builder, candidate A:

```json
{"candidate_inventory_sha256": "37189873AAF3AD31810749362C16AD959D051EEAC62FA94683911EE855560421", "inventory_file_sha256": "EF28700403FFE5FC781D1004979B83DC4ACC5F743E93F02201820071211AC3F8", "master_en_sha256": "44303C5A0D2964469D6B6523EDF3CB4391194BC49E19DD10B3FB90CCB667DC62", "scenario_id": "viral", "status": "candidate_built_for_independent_verification"}
```

2. Independent verifier, candidate A:

```json
{"candidate_inventory_sha256": "37189873AAF3AD31810749362C16AD959D051EEAC62FA94683911EE855560421", "inventory_file_sha256": "EF28700403FFE5FC781D1004979B83DC4ACC5F743E93F02201820071211AC3F8", "master_en_sha256": "44303C5A0D2964469D6B6523EDF3CB4391194BC49E19DD10B3FB90CCB667DC62", "publication_config_sha256": "CEAA522F8ADA7EF2453D52F0DE4D098733EA5A7D55B12BE96694094891767BF3", "scenario_id": "viral", "status": "verified_candidate_pending_process_and_external_gates"}
```

3. Builder, candidate B:

```json
{"candidate_inventory_sha256": "37189873AAF3AD31810749362C16AD959D051EEAC62FA94683911EE855560421", "inventory_file_sha256": "EF28700403FFE5FC781D1004979B83DC4ACC5F743E93F02201820071211AC3F8", "master_en_sha256": "44303C5A0D2964469D6B6523EDF3CB4391194BC49E19DD10B3FB90CCB667DC62", "scenario_id": "viral", "status": "candidate_built_for_independent_verification"}
```

4. Independent verifier, candidate B:

```json
{"candidate_inventory_sha256": "37189873AAF3AD31810749362C16AD959D051EEAC62FA94683911EE855560421", "inventory_file_sha256": "EF28700403FFE5FC781D1004979B83DC4ACC5F743E93F02201820071211AC3F8", "master_en_sha256": "44303C5A0D2964469D6B6523EDF3CB4391194BC49E19DD10B3FB90CCB667DC62", "publication_config_sha256": "CEAA522F8ADA7EF2453D52F0DE4D098733EA5A7D55B12BE96694094891767BF3", "scenario_id": "viral", "status": "verified_candidate_pending_process_and_external_gates"}
```

## Verification evidence

- Candidate A: exactly `130` regular files; `INVENTORY.json` declares and
  contains exactly `129` rows; inventory paths match the candidate file set
  with `0` missing and `0` extra paths.
- Candidate B: exactly `130` regular files; `INVENTORY.json` declares and
  contains exactly `129` rows; inventory paths match the candidate file set
  with `0` missing and `0` extra paths.
- The four verifier/build identity values are identical across A and B:
  - `candidate_inventory_sha256` =
    `37189873AAF3AD31810749362C16AD959D051EEAC62FA94683911EE855560421`
  - `inventory_file_sha256` =
    `EF28700403FFE5FC781D1004979B83DC4ACC5F743E93F02201820071211AC3F8`
  - `master_en_sha256` =
    `44303C5A0D2964469D6B6523EDF3CB4391194BC49E19DD10B3FB90CCB667DC62`
  - `publication_config_sha256` =
    `CEAA522F8ADA7EF2453D52F0DE4D098733EA5A7D55B12BE96694094891767BF3`
- Both candidate trees have `0` relative-path differences and `0` byte/hash
  differences.
- Expected stable identities match exactly: candidate inventory
  `37189873AAF3AD31810749362C16AD959D051EEAC62FA94683911EE855560421`,
  inventory file `EF28700403FFE5FC781D1004979B83DC4ACC5F743E93F02201820071211AC3F8`,
  MASTER_EN `44303C5A0D2964469D6B6523EDF3CB4391194BC49E19DD10B3FB90CCB667DC62`,
  and publication config
  `CEAA522F8ADA7EF2453D52F0DE4D098733EA5A7D55B12BE96694094891767BF3`.
- `MASTER_EN.acceptance.json` is absent from both candidates.
- The candidates parent contains only the two named candidate directories;
  no staging sibling remains.

## Pinned input preservation

The packet hash and all explicitly pinned packet inputs were verified before
execution and remain unchanged:

| Path | SHA-256 |
|---|---|
| `kb_creator/contracts/viral.json` | `67688867D4971D55137C2E4E7A71A746199596EDE4F5DD18577F4331CA87536D` |
| `kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf` | `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05` |
| `kb_creator/working/viral/master_en/publication_config_v1.json` | `CEAA522F8ADA7EF2453D52F0DE4D098733EA5A7D55B12BE96694094891767BF3` |
| `kb_creator/scripts/build_scenario_master_en.py` | `82C720B572A73B33DF9D2548BB3FD4CB8BAE81660AE21D4273DEB984C99EDA1C` |
| `kb_creator/scripts/verify_scenario_master_en.py` | `C151967D435A31DACF706D2938C5FC157C8E7E01E10E90C1211844C620B174E5` |
| `kb_creator/tests/test_build_scenario_master_en.py` | `01BDFFFC6F32833E3EF5EF831A85F30775883C1E20B5E9B5B3C0687A58AD33DF` |
| `kb_creator/tests/test_verify_scenario_master_en.py` | `B7D6822A44B06A87457DBE6B37F9CE97CC60E33083B2387C04C665402771B04F` |
| `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_step7_master_en_c2b_acceptance_re_review_20260901.md` | `D94D1B3F6794CC075779FA51B3BE4745DF49CC8290A72AD9B57C9BB7738133F2` |
| assigned frozen packet | `7B159690C0C689DF52BB17724F5C7111330DA247E69D57FA99F2604CBC9DB3AA` |

## Executed command order

1. `python -B kb_creator/scripts/build_scenario_master_en.py --contract kb_creator/contracts/viral.json --reconstruction-package kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4 --publication-config kb_creator/working/viral/master_en/publication_config_v1.json --source-pdf kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf --target kb_creator/working/viral/master_en/candidates/viral-master-en-candidate-20260901-a`
2. `python -B kb_creator/scripts/verify_scenario_master_en.py --contract kb_creator/contracts/viral.json --reconstruction-package kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4 --publication-config kb_creator/working/viral/master_en/publication_config_v1.json --source-pdf kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf --target kb_creator/working/viral/master_en/candidates/viral-master-en-candidate-20260901-a`
3. `python -B kb_creator/scripts/build_scenario_master_en.py --contract kb_creator/contracts/viral.json --reconstruction-package kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4 --publication-config kb_creator/working/viral/master_en/publication_config_v1.json --source-pdf kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf --target kb_creator/working/viral/master_en/candidates/viral-master-en-candidate-20260901-b`
4. `python -B kb_creator/scripts/verify_scenario_master_en.py --contract kb_creator/contracts/viral.json --reconstruction-package kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4 --publication-config kb_creator/working/viral/master_en/publication_config_v1.json --source-pdf kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf --target kb_creator/working/viral/master_en/candidates/viral-master-en-candidate-20260901-b`

## Changed paths and boundaries

The only writes made for this assignment were the two packet-named candidate
directories produced by the builders and this receipt:

- `kb_creator/working/viral/master_en/candidates/viral-master-en-candidate-20260901-a/`
- `kb_creator/working/viral/master_en/candidates/viral-master-en-candidate-20260901-b/`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/luna_qa_viral_step7_master_en_frozen_candidate_execution_20260901.md`

No code, config, source, tests, plan, context, prior receipt, or release file
was edited. No MinerU command, historical 371/119/490 matrix, or additional
test was run. Candidates remain unchanged after verification.

## Pending gates and next action

Visual QA, independent release review, user reading acceptance, and downstream
MASTER_RU remain pending. Next action belongs to the orchestrator and the
separately authorized downstream gates; this receipt does not issue a release
decision.

## Governance metadata

- Assignment state: complete; `PASS_FROZEN_CANDIDATE_EXECUTION` receipt written
  once, with candidate outputs preserved.
- Orchestrator policy owner: `gpt-5.6-sol / medium`.
- Scoped override: none; repository default role contract applied
  (`gpt-5.6-luna / high` bounded QA execution).
- Elapsed time: approximately `00:07:00` wall time for preflight, four frozen
  commands, read-only checks, and receipt creation.
- Token use: unavailable.
- Timestamp: `2026-09-02T00:00:30+03:00`.

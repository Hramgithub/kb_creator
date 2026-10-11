# Viral Step 7 MASTER_EN frozen candidate execution

- Goal: `20260830-kb-creator-next-scenario`
- Step: `7 / frozen MASTER_EN candidate execution`
- Owner: `gpt-5.6-luna / high`, bounded QA command execution only
- Engineering and design: closed; Luna must not edit source, config, scripts, tests, plan, context, or prior receipts
- Candidate acceptance/release: not granted by this execution

## Pinned inputs

- contract: `kb_creator/contracts/viral.json`
- accepted reconstruction: `kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4`
- publication config: `kb_creator/working/viral/master_en/publication_config_v1.json`
  - SHA-256: `CEAA522F8ADA7EF2453D52F0DE4D098733EA5A7D55B12BE96694094891767BF3`
- source PDF: `kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf`
- builder SHA-256: `82C720B572A73B33DF9D2548BB3FD4CB8BAE81660AE21D4273DEB984C99EDA1C`
- verifier SHA-256: `C151967D435A31DACF706D2938C5FC157C8E7E01E10E90C1211844C620B174E5`
- independent C2b acceptance receipt SHA-256:
  `D94D1B3F6794CC075779FA51B3BE4745DF49CC8290A72AD9B57C9BB7738133F2`

Both targets must be absent before execution:

- `kb_creator/working/viral/master_en/candidates/viral-master-en-candidate-20260901-a`
- `kb_creator/working/viral/master_en/candidates/viral-master-en-candidate-20260901-b`

## Frozen commands

Run from the repository root in exactly this order. Do not combine, rewrite, or
add production commands.

```powershell
python -B kb_creator/scripts/build_scenario_master_en.py --contract kb_creator/contracts/viral.json --reconstruction-package kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4 --publication-config kb_creator/working/viral/master_en/publication_config_v1.json --source-pdf kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf --target kb_creator/working/viral/master_en/candidates/viral-master-en-candidate-20260901-a

python -B kb_creator/scripts/verify_scenario_master_en.py --contract kb_creator/contracts/viral.json --reconstruction-package kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4 --publication-config kb_creator/working/viral/master_en/publication_config_v1.json --source-pdf kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf --target kb_creator/working/viral/master_en/candidates/viral-master-en-candidate-20260901-a

python -B kb_creator/scripts/build_scenario_master_en.py --contract kb_creator/contracts/viral.json --reconstruction-package kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4 --publication-config kb_creator/working/viral/master_en/publication_config_v1.json --source-pdf kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf --target kb_creator/working/viral/master_en/candidates/viral-master-en-candidate-20260901-b

python -B kb_creator/scripts/verify_scenario_master_en.py --contract kb_creator/contracts/viral.json --reconstruction-package kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4 --publication-config kb_creator/working/viral/master_en/publication_config_v1.json --source-pdf kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf --target kb_creator/working/viral/master_en/candidates/viral-master-en-candidate-20260901-b
```

## Required checks

After the four commands, use read-only inspection to prove:

- both verifier results have status
  `verified_candidate_pending_process_and_external_gates`;
- each target has exactly 130 files and a 129-row `INVENTORY.json`;
- the two values for `candidate_inventory_sha256`, `inventory_file_sha256`,
  `master_en_sha256`, and `publication_config_sha256` are identical;
- expected stable identities are:
  - candidate inventory: `37189873AAF3AD31810749362C16AD959D051EEAC62FA94683911EE855560421`;
  - inventory file: `EF28700403FFE5FC781D1004979B83DC4ACC5F743E93F02201820071211AC3F8`;
  - MASTER_EN: `44303C5A0D2964469D6B6523EDF3CB4391194BC49E19DD10B3FB90CCB667DC62`;
  - config: `CEAA522F8ADA7EF2453D52F0DE4D098733EA5A7D55B12BE96694094891767BF3`;
- neither candidate contains `MASTER_EN.acceptance.json`;
- no staging sibling remains;
- source/config/scripts/tests and prior receipts retain their pinned hashes.

## Stop conditions and output

Stop immediately on a nonzero command, identity mismatch, unexpected file, or
staging residue. Do not repair, delete, rename, rerun, or edit anything.

On full PASS, keep both candidate directories unchanged. Write exactly one
receipt:

`kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/luna_qa_viral_step7_master_en_frozen_candidate_execution_20260901.md`

The receipt must contain the four raw JSON results, file/inventory counts,
identity comparison, absence checks, executed command order, changed paths, and
`PASS_FROZEN_CANDIDATE_EXECUTION`. It must explicitly state that visual QA,
independent release review, user reading acceptance and downstream MASTER_RU are
still pending.

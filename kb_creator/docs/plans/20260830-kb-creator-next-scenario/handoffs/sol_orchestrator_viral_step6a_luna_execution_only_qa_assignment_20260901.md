# Luna/high execution-only QA: Viral Step 6A engineering integration

**Owner:** `gpt-5.6-luna`, bounded QA execution at high effort.  **State:** dispatched only after Terra engineering freeze.

## Non-negotiable role boundary

Luna executes the exact prepared commands below and records their unmodified raw results. Luna must not design or edit code, tests, fixtures, mutation cases, audit objects/rows, capture logic, remediation, or receipt requirements; must not interpret a failure into a fix; and must not delegate engineering. On any non-zero exit, count mismatch, hash mismatch, unexpected mutation, missing/truncated stream, or unclear output, stop and return `FAIL` or `BLOCKED` with raw evidence. Terra remains the separate engineering owner.

## Bound frozen evidence

- Branch/HEAD: `codex/kb-creator-viral` / `54607bd3b9362adbb0c4bca64e8751482797f380`.
- Implementation: `kb_creator/scripts/scenario_source_reconstruction.py` = `9802571C128D63DE5D643425FDA361EB2E032A5AE830ED9713B83A3A413B5855`.
- Focused tests: `kb_creator/tests/test_scenario_source_reconstruction.py` = `FA70BBAE285EAAA10E1F6BAF90119008342A18552E580E4E8530D9462997D5F9`.
- Terra integration receipt: `terra_engineering_viral_step6a_bld_full_integration_20260901.md` = `827BDFC63DB8B3C918D3EE77032E05146CBCADBB1422A892BA3D0A8DD319191C`.
- Protected CLI / contract tests: `64BD04C82A5AA21B7397885ABEB74E8A2215357B64DAD845AFDFDFC00F551DAA` / `DE5603869C9517A274FCD6DB2D61D23BEE2A204BAC8A1217E16603A5BF232AC3`.
- Retained source: 20,718,150 bytes; `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05`.
- Source sidecar / contract: `3DC6800C7515936C6434817F3DF6F9B3BF71E66C1CCCF477D168EFA53B550AA9` / `67688867D4971D55137C2E4E7A71A746199596EDE4F5DD18577F4331CA87536D`.
- Recovery manifest / evidence: `41F00E41D04A19071FF0418068D7A1744C412F6EC6CDBEB7CFEE580B32B09169` / `F1F9F66AB3EA9C09196221CA82FDFEA888C94AAE024891057CA1A20FA53179BC`.
- Candidate manifests 502/501/500: `410AED5D111E3BA8CA294095EF55F18AC7DFFD335868EA6D59522B91E14725EA` / `F0F243F6B8194C502CF6FEF9D5C838196BAFA49C96AE135D61EDAD799869C766` / `98FC41EAA65528CE04C772983FB49E8DD3DAE5998FAEDB98F0829E2E41E4C027`.
- Candidate QA / COMMANDS raw: `C38CB0A4667B1D4344C5E5DD91AEAAE7A2FD3101A3BB76611104EAA13BBD8FA6` / `9162651A456E12C7011081F999AA3B07EDB7EA9E66CA65CC78A0382456F12B06`.
- Renders/source/sheets counts and manifests: 155 `19F600C23066DC3F64C5907BA6ADF59E3520C967249EBF7CB85CDAE53411979A`; 124 `C6C14DD9219C765428E84BDB85CD9821C52B95433A2022DCAFACC8A71AEF0B5C`; 31 `B66EF1B60A0479C33F875C1CC60B576A1E785BEE16327EFE3C173F40BA77BB4A`.

The exact pre-existing cache inventory is immutable: five root `.pytest_cache` files with hashes `E7C6BB...DC6D`, `37DC88...BDE4`, `420E80...6B70`, `12FD3E...BB0`, `BFA3FC...9943`, plus the three recorded `.pyc` hashes `168C67...13C4`, `9F4E03...BEF54`, `DE4E51...F0B9`. Do not remove or update them.

## Sole write

Create only the absent receipt:

`kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/luna_qa_viral_step6a_bld_full_integration_execution_only_20260901.md`

No durable probe/log/helper/script is allowed. Test-owned OS temporary roots may be created and automatically cleaned by the existing pytest fixtures. The worktree must gain no cache, temp, marker, fixture, or log residue.

## Prepared capture wrapper

For each command below, execute it through this already-specified behavior, without modifying the child argument list: use Python `subprocess.run(child_args, stdout=PIPE, stderr=PIPE)` with bytes retained in memory; record the child argument vector, native exit, elapsed seconds, complete stdout/stderr byte counts, uppercase SHA-256 values, and full decoded stdout/stderr in the receipt. Set `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` for every pytest child. The active `python` must resolve to `D:\NRI\.tools\python-3.13.14\python.exe`, version `3.13.14`; every Python child uses `-B`.

This wrapper is capture transport only. Luna may not change command semantics, select fewer nodes, rerun a failing command after edits, or create an alternate test/probe.

## Exact static command sequence

Run from `D:\NRI\.worktrees\kb-creator-viral`, in this order:

```text
python -B -m pytest -p no:cacheprovider kb_creator/tests/test_scenario_source_reconstruction.py --collect-only -q
python -B -m pytest -p no:cacheprovider kb_creator/tests/test_scenario_source_reconstruction.py -q
python -B -m pytest -p no:cacheprovider kb_creator/tests/test_scenario_contract.py --collect-only -q
python -B -m pytest -p no:cacheprovider kb_creator/tests/test_scenario_contract.py -q
python -B -m pytest -p no:cacheprovider kb_creator/tests/test_scenario_contract.py kb_creator/tests/test_scenario_source_reconstruction.py --collect-only -q
python -B -m pytest -p no:cacheprovider kb_creator/tests/test_scenario_contract.py kb_creator/tests/test_scenario_source_reconstruction.py -q
```

Required exact outcomes: focused `371 collected / 371 passed`, protected `119 collected / 119 passed`, combined `490 collected / 490 passed`, all native exit `0`, no warning/error stream. Independently read-only parse the frozen focused registry and Terra receipt to report 368 negative ids, three BLD tests, exact family table, 368 distinct callable names/objects, exact six ordered alias pairs, no generic proxy selector, all 368 closed audits, canonical 51,005 bytes / `8C5C2A0A69C212465D1429FA38B35A4802C9AFCDF52F9461A1747D5729671DD4`, and BLD capture PASS. This is inspection of existing evidence, not construction of new evidence.

Do not proceed to live commands unless every static command and frozen-evidence comparison is exact.

## Exact live read-only commands

Candidate root:

`kb_creator/working/viral/source_reconstruction/20260831_step6a_reconstruction_from_salvaged_engine_candidate`

Recovery root:

`kb_creator/working/viral/source_reconstruction/20260831_step6a_engine_output_salvage_candidate`

Run exactly:

```text
python -B kb_creator/scripts/reconstruct_scenario_source.py preflight --contract kb_creator/contracts/viral.json --source kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf --recovery-root kb_creator/working/viral/source_reconstruction/20260831_step6a_engine_output_salvage_candidate --run-root kb_creator/working/viral/source_reconstruction/20260831_step6a_reconstruction_from_salvaged_engine_candidate
python -B kb_creator/scripts/reconstruct_scenario_source.py verify --contract kb_creator/contracts/viral.json --source kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf --recovery-root kb_creator/working/viral/source_reconstruction/20260831_step6a_engine_output_salvage_candidate --run-root kb_creator/working/viral/source_reconstruction/20260831_step6a_reconstruction_from_salvaged_engine_candidate
python -B kb_creator/scripts/reconstruct_scenario_source.py verify --contract kb_creator/contracts/viral.json --source kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf --recovery-root kb_creator/working/viral/source_reconstruction/20260831_step6a_engine_output_salvage_candidate --run-root kb_creator/working/viral/source_reconstruction/20260831_step6a_reconstruction_from_salvaged_engine_candidate
```

Require native exit `0` for all three. The two verify stdout byte streams and SHA-256 must be identical. The payload must report the exact branch/HEAD and retained local source only. Never run `build` or `remediate`.

## Post-run proof and receipt

Recompute every bound hash/count/manifest and cache inventory. Prove candidate/source/recovery/CLI/contract tests/implementation/focused tests/Terra receipt/QA/COMMANDS/renders/Git branch/HEAD unchanged, and no worktree-attributable cache/temp/marker/fixture/log residue. Record every command/raw stream/hash/native exit and exact write path.

Result may be `PASS`, `FAIL`, or `BLOCKED`. `PASS` closes only independent execution QA and authorizes the separate GPT-5.5/high Fast implementation/process critic. It does not accept Step 6A, promote the candidate, start semantic review, create MASTER outputs, publish, commit, or push.

Timestamp: 2026-09-01 Europe/Moscow

# Bounded executor receipt: Viral Step 6A QA metadata-integrity remediation

- Goal / step: `20260830-kb-creator-next-scenario` / `6-source-reconstruction-step6a-qa-metadata-integrity-remediation`
- Role: bounded executor; requested model/effort `gpt-5.6-luna` / `medium`; actual platform model/effort `unavailable`
- Orchestrator policy owner: main chat `gpt-5.6-sol` / `medium`; assignment `user-directed / platform-unverified`; scoped override `none`
- Token use: `unavailable`; timestamp: `2026-08-31`; elapsed time: `unavailable`
- Worktree / branch / HEAD: `D:\NRI\.worktrees\kb-creator-viral` / `codex/kb-creator-viral` / `54607bd3b9362adbb0c4bca64e8751482797f380`
- Authority chain: base packet `C86335AFCAC0A6060BA8E9D616172115905DE7B08F3ED1E88BCB822D6CE8B648`; amendment `9FDBC4848AAF280DDFE4080E1263B4146320436E5A832A296C50209AB9B99292`; accepted amendment review `DB93AE31E552C2C5A46EAD52D9EE5D620625B6344C7DDE3D5B144E1056A4512F`; prior implementation/process REJECT `AE14A9D917FE9BAB4BD64DD1BAE84F6B3A52209D1A38D5483389E022BE69CF9B`.

## Result

Metadata-only remediation completed. Candidate remains `candidate_needs_review`; semantic, reading-order, placement and ownership uncertainty remains open. No build, MinerU/OCR, GPU/model, network, history, translation, promotion, publication, staging, commit or push was performed.

Only these material paths changed: `kb_creator/scripts/scenario_source_reconstruction.py`, `kb_creator/tests/test_scenario_source_reconstruction.py`, candidate `evidence/COMMANDS.json`, candidate `RECONSTRUCTED_EN.qa.json`, and this receipt. The protected CLI, source, sidecar, recovery, contract, candidate evidence, pages, renders, and orchestration documents were not written.

## Bindings and manifests

- Local source: `kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf`, 20,718,150 bytes, SHA-256 `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05`.
- Sidecar: `kb_creator/working/viral/source/SOURCE_ADMISSION.json`, SHA-256 `3DC6800C7515936C6434817F3DF6F9B3BF71E66C1CCCF477D168EFA53B550AA9`; external locator remained unopened and provenance-only.
- Recovery bindings: manifest `41F00E41D04A19071FF0418068D7A1744C412F6EC6CDBEB7CFEE580B32B09169`; evidence `F1F9F66AB3EA9C09196221CA82FDFEA888C94AAE024891057CA1A20FA53179BC`.
- Candidate: 502 regular files; post full canonical manifest `410AED5D111E3BA8CA294095EF55F18AC7DFFD335868EA6D59522B91E14725EA`.
- QA inventory: exactly 501 rows, excludes only root `RECONSTRUCTED_EN.qa.json`; digest `F0F243F6B8194C502CF6FEF9D5C838196BAFA49C96AE135D61EDAD799869C766`.
- Protected candidate manifest: 500 files, unchanged, `98FC41EAA65528CE04C772983FB49E8DD3DAE5998FAEDB98F0829E2E41E4C027`.
- Render carry-forward manifests unchanged: all renders 155=`19F600C23066DC3F64C5907BA6ADF59E3520C967249EBF7CB85CDAE53411979A`; source renders 124=`C6C14DD9219C765428E84BDB85CD9821C52B95433A2022DCAFACC8A71AEF0B5C`; contact sheets 31=`B66EF1B60A0479C33F875C1CC60B576A1E785BEE16327EFE3C173F40BA77BB4A`.

## Commands and evidence

1. `python -B -m pytest kb_creator/tests/test_scenario_contract.py kb_creator/tests/test_scenario_source_reconstruction.py -q -p no:cacheprovider` — pass, `127 passed`.
2. Packet `preflight` command from the correct worktree cwd — exit 0, exact local source and branch/HEAD accepted.
3. Packet `remediate` command — exit 0; wrote only COMMANDS and QA metadata; returned `post_inventory_count=501` and digest `F0F243...`.
4. Packet `verify` command — exit 0.
5. Packet `verify` command repeated — exit 0; stdout bytes and stdout SHA-256 were identical to command 4.
6. Packet `remediate` command repeated — refused stale post-state baseline; JSON reported `candidate baseline mismatch`, verified process exit `2` via `$LASTEXITCODE`; no write occurred.

`COMMANDS.json` is v3 with four action records. Every action explicitly records `build_invoked=false`, `mineru_invoked=false`, `ocr_invoked=false`, `gpu_or_model_invoked=false`, `network_invoked=false`, `external_source_used=false`, `source_flag=--source`, `run_root_flag=--run-root`, and the admitted POSIX-relative source path. QA is v3 with recovery hashes, four open blockers, 124/39/388/204/31/112/92 closures, and the complete live inventory.

## Mutation audit

Dispatch-window protected orchestration identities were read-only audited pre/post; each retained the same path, existence, byte length and SHA-256: `plan.md` 56,695 / `5FCB9B590AA64149454119C6F13B715C09317DEC74B2FC4E40E8DFF27C730CD6`; `context.md` 50,583 / `C9397E3B6B3D2DB13A83F7535028B7520AF054327EC5F4F9450126F079F365AA`; `PROJECT_STATUS.md` 99,937 / `70E4D2611EF92ACF873ED6E9649976EC88C958E4287105A740ABAF9A7082A5A1`; `README.md` 2,967 / `674288F3869392270BF329DE2221D55CC05DDEB3D44D661E8A3A02552AC59168`; pipeline summary 11,726 / `16B99B77064144CFC0C259851E73F50571A7C3F40C98BF368F9FCDF9AA8CB31C`.

Post hashes of the five material outputs are: script `581FA8D0F47C7906B29EC4664E929A98B3A3699445C974AB7CF51F398D118FA8`; tests `9F581C5C6CD9A8DF5DB06DA30F48B6FE39995713AD3CFFCC3829CF8530D1C1B0`; COMMANDS `9162651A456E12C7011081F999AA3B07EDB7EA9E66CA65CC78A0382456F12B06`; QA `C38CB0A4667B1D4344C5E5DD91AEAAE7A2FD3101A3BB76611104EAA13BBD8FA6`; receipt is the sole durable receipt path.

## Disposition

Both observed P1s are remediated at the reusable writer/verifier/test layer: stale recovery/inventory/blocker metadata is rejected and regenerated, and fail-closed cross-link validation now covers source/sidecar/recovery, schema/counts, inventory bytes/hashes/order, candidate topology, blocker conservation, command policy and local-source admission. Visual QA carry-forward is valid under the unchanged render/protected manifests, but separate bounded QA and fresh independent `gpt-5.5` implementation/process review remain required. Step 6A acceptance and any `MASTER_EN`/release/publication action remain pending and unauthorized.

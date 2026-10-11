# Bounded QA receipt: Viral Step 6A QA metadata-integrity remediation

- Result: **PASS** — independent bounded QA passed; candidate remains `candidate_needs_review`.
- Role: bounded QA `gpt-5.6-luna` / low; actual platform model/effort unavailable; token use unavailable.
- Worktree / branch / HEAD: `D:\NRI\.worktrees\kb-creator-viral` / `codex/kb-creator-viral` / `54607bd3b9362adbb0c4bca64e8751482797f380`.
- Authority: base packet `C86335AFCAC0A6060BA8E9D616172115905DE7B08F3ED1E88BCB822D6CE8B648`; amendment `9FDBC4848AAF280DDFE4080E1263B4146320436E5A832A296C50209AB9B99292`; accepted amendment review `DB93AE31E552C2C5A46EAD52D9EE5D620625B6344C7DDE3D5B144E1056A4512F`; executor receipt `27E462EBFCDA9126700BEE3CB958595C64823A3386AF55EC66AF277AD08CE645`; prior corrected visual QA `194BF7EE471FF7E7DF859ED7958F7B3978F0F6C54536136C26CC6C6D1A7765DD`.

## Findings

- P0: none.
- P1: none.
- P2: none.

## Commands and results

From the exact worktree cwd:

1. `python -B -m pytest kb_creator/tests/test_scenario_contract.py kb_creator/tests/test_scenario_source_reconstruction.py -q -p no:cacheprovider` — **127 passed in 0.19s**.
2. Local-source strict `verify` — exit 0; JSON `deterministic=true`, `state=verified_candidate_needs_review`, inventory digest `F0F243F6B8194C502CF6FEF9D5C838196BAFA49C96AE135D61EDAD799869C766`, pages/renders `124/124`, sheets `31`, assets `204` (`112/92` referenced/unreferenced), anchors `124`, handouts `39`.
3. The identical strict `verify` command repeated — exit 0 and byte-identical stdout to command 2, with the same state/counts/digest.

No live `remediate` was rerun. The existing executor receipt's second-remediate refusal was accepted as evidence; no live candidate mutation was attempted.

## Independent live-candidate checks

- Source PDF: `20,718,150` bytes, SHA-256 `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05`.
- Admission sidecar: SHA-256 `3DC6800C7515936C6434817F3DF6F9B3BF71E66C1CCCF477D168EFA53B550AA9`.
- Candidate: 502 regular files, manifest `410AED5D111E3BA8CA294095EF55F18AC7DFFD335868EA6D59522B91E14725EA`.
- QA inventory: exactly 501 rows, digest `F0F243F6B8194C502CF6FEF9D5C838196BAFA49C96AE135D61EDAD799869C766`; rule is every regular file recursively under candidate except root `RECONSTRUCTED_EN.qa.json`; paths/order/bytes/raw SHA-256 were independently reconstructed and matched.
- Protected candidate subset: 500 files, `98FC41EAA65528CE04C772983FB49E8DD3DAE5998FAEDB98F0829E2E41E4C027`.
- QA: schema `kb_creator.reconstructed_en_qa.v3`, state `candidate_needs_review`, 124 pages, 124 renders, 31 sheets, 204 assets, 112 referenced + 92 unreferenced, 124 anchors, 39 handouts / 7 maps / 13 pregens / back cover 1, 4 open blockers, page 1–5 `needs_review`.
- Recovery: `RECOVERY_MANIFEST.json` `41F00E41D04A19071FF0418068D7A1744C412F6EC6CDBEB7CFEE580B32B09169`; `RECOVERY_EVIDENCE.json` `F1F9F66AB3EA9C09196221CA82FDFEA888C94AAE024891057CA1A20FA53179BC`.
- `COMMANDS.json`: schema `kb_creator.reconstruction_commands.v3`, 4 records; counts match live QA; all records carry `--source`, `--run-root`, admitted local POSIX source path, and false `build_invoked`, `mineru_invoked`, `ocr_invoked`, `gpu_or_model_invoked`, `network_invoked`, `external_source_used`. No external locator was opened.

## Render carry-forward and negative coverage

Render/protected hashes match exactly, so the prior 67/67 visual QA carry-forward is valid without reopening images:

- all 155 renders: `19F600C23066DC3F64C5907BA6ADF59E3520C967249EBF7CB85CDAE53411979A`;
- source 124: `C6C14DD9219C765428E84BDB85CD9821C52B95433A2022DCAFACC8A71AEF0B5C`;
- contact sheets 31: `B66EF1B60A0479C33F875C1CC60B576A1E785BEE16327EFE3C173F40BA77BB4A`.

The focused hermetic tests and read-only implementation inspection cover fail-closed inventory path/order/bytes/hash, reparse/path rejection, schema/policy invariants, stale recovery/evidence, blocker/count/topology, missing inventory/contact-sheet evidence, and local-source/runtime-policy constraints. No live mutation probe was needed. The exact disposable probe `D:\NRI\_viral_step6a_metadata_integrity_qa_probe_20260831` was not created and is absent (`False`).

## Mutation and disposition

No source, sidecar, recovery, contract, candidate protected files, pages, renders, engine payload, other evidence, plan/context/status/README, prior receipt, external source, MinerU/OCR/GPU/model/network/history/translation, Git index/ref, promotion or publication was changed. Pre-existing worktree dirt remains unchanged. The only durable write in this QA turn is this receipt.

PASS authorizes only a fresh independent `gpt-5.5` implementation/process review. It does not authorize Step 6A acceptance, `MASTER_EN`, promotion, publication, commit or push. Remaining semantic, reading-order, placement and ownership blockers remain open.

Token use: unavailable.

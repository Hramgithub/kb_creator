# Luna executor receipt — Viral Step 6A raw-engine-input recovery

- Goal / step: `20260830-kb-creator-next-scenario` / `6-source-reconstruction-step6a-engine-output-salvage`
- Role / policy effort: `gpt-5.6-luna` bounded execution / `medium`
- Actual platform model / effort: `unavailable`
- Orchestrator owner: `gpt-5.6-sol` / `medium`; assignment state: `platform-unverified`
- Worktree / branch / HEAD: `D:\NRI\.worktrees\kb-creator-viral` / `codex/kb-creator-viral` / `54607bd3b9362adbb0c4bca64e8751482797f380`
- Result: `raw_engine_input_recovery_complete`
- Exact state boundary: raw engine input recovery only; not `candidate_needs_review`, `reconstruction_ready`, `MASTER_EN`, accepted, or publication

## Authorization and immutable bindings

User correction was applied as authoritative: generated MinerU origin/layout PDFs are expected raw outputs and origin byte identity is revoked. No MinerU rerun, GPU/model work, rendering/OCR, network, historical translation, main MinerU script, cleanup, Git mutation, or remote operation was performed.

| Binding | SHA-256 / identity |
|---|---|
| Original Step 6 packet | `011CF87FFA0B0DACC85559DEF601A5FD9EED0755F86EB877C263CF2F2D8FABBC` |
| Origin-semantics delta | `0894966630FA19022033AA3D93CE67B98C7B44244BADB022ED0EC2BAD08DDA2C` |
| Latest blocked executor receipt | `04B018A91BE65AD4FF2C6425C03A11391206F7355393C253BDEA2AA7800EA6E3` |
| Independent salvage accept receipt | `2FE4EEA41760F0068A30B6A551E04F5B901F4DB6208B83E952C815905FE638E4` |
| Immutable predecessor manifest | `81EA67826C139E501F1C841CBF17464FA54A409CCE32F1EAA40BB620EEA39079` |
| Admitted source | 20,718,150 bytes / `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05` |

Predecessor root `kb_creator/working/viral/source_reconstruction/20260831_step6a_origin_copy_exception_retry` was read-only throughout. Its before/after inventory remained 507 files and 71,193,544 bytes; no predecessor path was written, renamed, deleted, cleaned, or reused. Successor was absent before execution.

## Recovery output

Created only `kb_creator/working/viral/source_reconstruction/20260831_step6a_engine_output_salvage_candidate/` plus this receipt. The successor payload contains exactly five named files and exactly 204 `images/*.jpg` files copied from the immutable predecessor:

- `Call_of_Cthulhu_Viral.md`: 388,490 bytes, `9B2D0FAD9511650706EE9A24A7B3B86C6B8BFF07CB573CA901D38B2B1BBDF577`
- `Call_of_Cthulhu_Viral_content_list.json`: 749,049 bytes, `01181FA9E98C9561747416A7B935F8FBD94624CDF67826896D847E1411DE52C5`
- `Call_of_Cthulhu_Viral_content_list_v2.json`: 1,233,206 bytes, `669E5C41E35F6B62DC5FF4471CDF4DCCDD035608D03C8D2CEC0D9369585771C5`
- `Call_of_Cthulhu_Viral_middle.json`: 6,274,905 bytes, `6E4E631A6B0F2F8A56D179D66F497A269E6602331E672690C4B687DB645B395F`
- `Call_of_Cthulhu_Viral_model.json`: 2,304,099 bytes, `97D8A19A6C2CB8CFC8A21E75D93D98D1699A0DE75939D5E0E7BBF41BB9519BDF`
- 204 JPG files: 10,270,968 bytes total; full per-file source/output identities are in `RECOVERY_MANIFEST.json`; image inventory SHA-256 `1C10CD02799329BA18DEA48671DBBFE16BFF27462602FD159E1590A3E045A0E0`.

Payload closure: 209 files, 21,220,717 bytes. Every payload file matched its predecessor counterpart in size and SHA-256. `RECOVERY_MANIFEST.json` contains all 209 payload rows and has SHA-256 `41F00E41D04A19071FF0418068D7A1744C412F6EC6CDBEB7CFEE580B32B09169`; `RECOVERY_EVIDENCE.json` has SHA-256 `F1F9F66AB3EA9C09196221CA82FDFEA888C94AAE024891057CA1A20FA53179BC`.

## Structural gates and exclusions

- v1 content list: 1,840 entries, page indices exactly `0..123`.
- v2 content list: 124 records; middle `pdf_info`: 124 records; model: 124 records.
- Markdown: 387,142 decoded characters, 112 image references, 0 missing targets; 92 copied images are unreferenced engine evidence and remain retained in the closed payload.
- All payload paths remain below `engine/mineru_hybrid_high/Call_of_Cthulhu_Viral/hybrid_auto/`; no symlink or reparse point was found.
- Source/origin/layout/span PDFs, `_bridge_runtime`, caches, compiled artifacts, pages/reconstructed Markdown, source/contract snapshots, provenance/acceptance/production/publication outputs, historical translations, and legacy config are absent from the successor.
- `candidate_needs_review` is intentionally false because no reconstructed English candidate was produced. The successor is not an acceptance or promotion artifact.

## Commands and mutation audit

Read-only checks used `python -B` with `PYTHONDONTWRITEBYTECODE=1` for inventory/hash/JSON/reference validation. No `py_compile` was used. Copy operation used only exact predecessor paths for the five named files and `images/*.jpg`. No implementation/test file was changed. No MinerU command, network, PDF render/OCR, source access, cleanup, stage, commit, push, branch/ref, contract, plan, context, status, accepted, production, or remote operation occurred.

Pre/post worktree identity remained branch `codex/kb-creator-viral`, HEAD `54607bd3b9362adbb0c4bca64e8751482797f380`; pre-existing Git status was preserved. The only new paths are the successor root payload/evidence files and this receipt. `git diff --check` was not used to mutate or normalize any file; no new generic seam/test path was needed.

## Next boundary

A separate generic reconstruction builder must consume these recovered raw-engine inputs and produce the original full Step 6A schema: source/contract evidence, 124 page files and provenance, reconstructed EN, asset/block/entity/handout closure, QA and blocker evidence, and later independent visual/critic review. This receipt does not authorize that builder, contract mutation, acceptance, `MASTER_EN`, or publication.

- Elapsed time: unavailable
- Token use: unavailable
- Detached receipt SHA-256: compute after final write; do not edit this receipt to embed it.

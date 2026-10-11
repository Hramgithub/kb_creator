# Terra engineering receipt — Viral Step 6A origin semantics and no-rerun recovery

- Goal / step: `20260830-kb-creator-next-scenario` / `6-source-reconstruction-step6a-origin-semantics-delta`
- Role / policy effort: `gpt-5.6-terra` engineering assistance / `medium`; actual platform model / effort: unavailable.
- Orchestrator: `gpt-5.6-sol` / `medium`; user correction is the scoped override: `*_origin.pdf` is a normal MinerU raw-engine result, not a source-byte identity target.
- Worktree / branch / HEAD verified: `D:\NRI\.worktrees\kb-creator-viral` / `codex/kb-creator-viral` / `54607bd3b9362adbb0c4bca64e8751482797f380`.
- Result: `evidence_supports_no_rerun_salvage_pending_fresh_independent_acceptance`.

## Disposition

The old `retained_origin_copy_identity_mismatch` stop is an architecture error and is withdrawn. Source byte identity remains mandatory only for the external admitted PDF and the temporary upload transport copy. The completed 507-file engine result is technically salvageable without rerunning MinerU, but remains immutable failure evidence until a fresh independent `gpt-5.5` review accepts the recovery control with no P0/P1. It is not a candidate, accepted reconstruction, or publication artifact now.

## Identities and tools

| Item | Observed identity / result |
|---|---|
| Admitted source | `D:\яндекс\Yandex.Disk\НРИ\1_Зов Ктулху\english\7th Edition Call of Cthulhu\Adventures\Call_of_Cthulhu_Viral.pdf`; 20,718,150 bytes; `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05`; source authority only |
| Runtime origin | `...\hybrid_auto\Call_of_Cthulhu_Viral_origin.pdf`; 20,858,968 bytes; `71B959CC33492DC18985422082E0D949C3D10BC75C13D86027F83EB67C8CB49A`; raw-engine reserialized input baseline |
| Layout overlay | `Call_of_Cthulhu_Viral_layout.pdf`; 22,064,546 bytes; `A8DF1F77AFDDF8FA7250FA9B4BDB54458D43A3A19B30C15FB1A618DFAE83CFB1`; raw diagnostic only |
| Mandatory executor predecessor | `luna_executor_viral_source_reconstruction_step6a_origin_copy_exception_retry_20260831.md`; `04B018A91BE65AD4FF2C6425C03A11391206F7355393C253BDEA2AA7800EA6E3`; match |
| Tools | bundled Python `3.12.13`; Poppler `pdfinfo` / `pdftoppm` `26.05.0`; installed MinerU `3.4.4` inspected read-only |

Both source and origin: PDF 1.7, unencrypted, untagged, form-free, no JavaScript, 124 Letter pages (`612 x 792 pt`), zero rotation, zero outline entries and AcroForm fields. Source producer is Ghostscript; origin producer is PDFium.

## Installed MinerU 3.4.4 output contract

Read-only code evidence explains the different bytes. `common.py:194-247` calls `rewrite_pdf_bytes_with_pdfium()` in `convert_pdf_bytes_to_bytes`; `_prepare_pdf_bytes()` applies it before the hybrid path. `common.py:288-305` writes those prepared `pdf_bytes` as `<name>_origin.pdf` and creates `<name>_layout.pdf`; `:314-345` writes Markdown, both content lists, middle JSON and model JSON; `:751-756` passes all flags through hybrid processing. `fast_api.py:828-855` maps the API options to the same outputs. Thus byte difference and `PDFium` metadata are normal serialization outcomes, not a different-source signal.

Expected observed `hybrid_auto` outputs are: `Call_of_Cthulhu_Viral_origin.pdf`, `Call_of_Cthulhu_Viral_layout.pdf`, `Call_of_Cthulhu_Viral.md`, `Call_of_Cthulhu_Viral_content_list.json`, `Call_of_Cthulhu_Viral_content_list_v2.json`, `Call_of_Cthulhu_Viral_middle.json`, `Call_of_Cthulhu_Viral_model.json`, and `images/`. A span overlay is optional and absent.

## Full 124-page audit

Bundled Poppler rendered every page of each PDF using fixed **72 DPI, RGB JPEG**. Per-page rows were deterministically serialized as `page<TAB>source_hash<TAB>origin_hash<TAB>changed_pixels<TAB>total_pixels<TAB>changed_fraction<TAB>mean_abs_channel_diff<TAB>bbox`; all-page record manifest SHA-256: `84316E49B2B0603D3A751BA5AC9C98C48E953C65B087E03A771D5BD403B22E23`.

| Pages, all checked | Boxes / rotation | Text-order diagnostic | Raster source vs origin |
|---|---|---|---|
| 1-31 | 31/31 equal Letter, zero rotation | 31/31 text hashes equal | 31/31 rasters equal; 0 changed pixels |
| 32-62 | 31/31 equal Letter, zero rotation | 31/31 text hashes equal | 31/31 rasters equal; 0 changed pixels |
| 63-93 | 31/31 equal Letter, zero rotation | 31/31 text hashes equal | 31/31 rasters equal; 0 changed pixels |
| 94-124 | 31/31 equal Letter, zero rotation | 31/31 text hashes equal | 31/31 rasters equal; 0 changed pixels |
| **1-124 aggregate** | **124/124 page records equal** | **304,803 chars; 52,252 tokens; 653 font entries; 434 image XObjects; 40 `/Link` annotations each** | **124/124 raster files byte-identical; 0 / 60,103,296 changed pixels; every diff bbox null** |

This is visual evidence, not an inference from text or metadata. It is a fixed-profile fidelity gate only and does not make origin a source authority. The layout PDF independently has 124 unencrypted Letter pages and zero rotations; at the same profile it intentionally differs from origin on all 124 pages (35,260,812 changed pixels; zero unchanged pages; maximum page 110: 479,490 pixels; full-page bounds), as required of a layout overlay.

## 507-file completeness

The immutable root is `kb_creator/working/viral/source_reconstruction/20260831_step6a_origin_copy_exception_retry`. Sorted `relative_path<TAB>byte_count<TAB>SHA256` inventory: **507 files, 71,193,544 bytes, SHA-256 `81EA67826C139E501F1C841CBF17464FA54A409CCE32F1EAA40BB620EEA39079`**.

It contains the seven exact named engine files, 204 JPEG assets, and expected runtime/cache files. Markdown is 387,142 characters with 112 image links. `middle.json` page ids cover exactly 0-123; v1 content list has 1,840 entries covering exactly 0-123; v2 content list has 124 ordered records; model JSON has 124 records. Extension inventory: 204 `.jpg`, 75 `.json`, 1 `.md`, 2 `.pdf`, 4 `.pickle`, 34 each `.cubin`/`.llir`/`.ptx`/`.source`/`.ttgir`/`.ttir`, 15 `.pyd`, 2 extensionless. This proves raw-engine completeness, not reconstruction acceptance.

## Correct policy and no-rerun successor

`runtime_result_origin_copy` is a non-authoritative, non-promotable reserialized-input baseline. Bind its path/size/hash to the immutable predecessor manifest; do not compare it to source bytes. Require its 124-page geometry, text-order and fixed-profile raster gates above. `runtime_layout_overlay` is likewise raw diagnostic evidence: bind it, require 124-page geometry and intentional overlay differences, and never promote either PDF.

Proposed successor, not created now: `20260831_step6a_engine_output_salvage_candidate` at `kb_creator/working/viral/source_reconstruction/20260831_step6a_engine_output_salvage_candidate/`. Bind the admitted source, executor receipt `04B018...EA6E3`, predecessor manifest `81EA...39079`, seven named-file identities, and the 204-asset count. Never edit, rename, delete, or write into the predecessor root.

After fresh critic acceptance only, the executor may write only this successor root, its one receipt, and explicitly accepted generic verifier/test files. It may copy only hash-matching `Call_of_Cthulhu_Viral.md`, both content lists, `middle.json`, `model.json`, and 204 `images/*.jpg`. It must not copy/use/promote source PDFs, `*_origin.pdf`, `*_layout.pdf`, `_bridge_runtime`, or cache artifacts.

Generic gates: predecessor and copied-file hashes; exact output-name contract; JSON coverage 0-123; model/v2 count 124; every Markdown image reference resolves within copied assets; successor closed manifest; reject any raw-byte-equality requirement for origin. Audits: no MinerU/network run; predecessor byte-intact; no source/raw PDF/cache in successor; no historical translation, accepted/production, or Git mutation. Stop for every binding/count/path/page/reference failure, a pre-existing successor, any MinerU launch, out-of-allowlist copy, or promotion claim.

Required critic receipt: `handoffs/gpt55_critic_viral_step6a_engine_output_salvage_review_20260831.md`. Critic prompt: review only this no-rerun salvage control; verify authority separation, bindings, gates, allowlist and stops; accept only with no P0/P1; do not run MinerU or mutate roots. Executor prompt after acceptance: do not run MinerU; verify bindings; create only the named successor; copy only the allowed derived inputs; run generic gates/audits; preserve predecessor; return at most a candidate needing separate review.

## Lifecycle

Changed: this receipt only. The authorized scratch directory `D:\NRI\_viral_origin_semantics_probe_20260831` contained only renders/diff scripts and no source PDF copy; it is removed after this write and absence is verified.

- Elapsed time: unavailable
- Token use: unavailable
- Detached SHA-256: compute after final write; do not edit this receipt to embed it.

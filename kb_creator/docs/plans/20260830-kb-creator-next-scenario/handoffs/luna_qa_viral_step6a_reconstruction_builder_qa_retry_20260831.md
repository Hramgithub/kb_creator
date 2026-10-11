# Viral Step 6A reconstruction-builder QA retry receipt

- Result: **pass** for bounded remediation QA; candidate remains `candidate_needs_review` and still requires independent critic review.
- Role: bounded QA `gpt-5.6-luna` / low; exact token use unavailable.
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`.
- Branch/HEAD: `codex/kb-creator-viral` / `54607bd3b9362adbb0c4bca64e8751482797f380`.
- Only durable write by this QA: this receipt.

## Binding checks

The following predecessor bindings were read from the canonical plan/context and
the executor receipt and matched the supplied values: original remediation
packet `D7A283D3D6C49701C265707507015870C90C3B1D8B79117BD9F59D2D07622D27`;
accepted baseline amendment
`C0D8CB1F4B3B9C49A1FC5D013525F37A6459A9EF37DF7F27C3EBB29DC940341C`;
critic accept
`76075D8BBE6880AD659D9EBBA6DAEE96F84909DE8FF508C02D71C2FFC992781F`;
successor executor receipt
`978BFD522C4D50668B13D5BB83346D7B86A2F3D663EAE634641495DEFC6E2783`.
The candidate post-manifest claim is 502 regular files with expected SHA-256
`52E44F725AB121EC61A255B747EA467B4371481F391EB5E79B51132E67258066`.

## Checks performed

- Candidate tree read-only count: 502 regular files; source renders: 124;
  contact sheets: exactly 31 (`sheet-001.png` through `sheet-031.png`).
- All 31 contact sheets were actually viewed. They cover pages 1–124 in exact
  2x2 ordinal order. Sheet outcomes: sheets 001–031 visually legible and
  structurally intact; no visible blank/corrupt render, unintended rotation, or
  clipping was found. Sheets 018–026 cover handout pages 69–103; sheets 027–028
  cover maps 104–110; sheets 028–031 cover pregens 111–123 and page 124.
- Risk-page visual coverage was included for pages 1–5, 6, 19, 32, 45, 58,
  68, all pages 69–103, 104–110, 111–123, and 124 via the source-render
  contact-sheet views. This is visual evidence only and does not close semantic,
  reading-order, or placement uncertainty.
- Focused hermetic tests: `126 passed in 0.21s`.
- Candidate identity reports 124 anchors, 39 handouts, 7 maps, 13 pregens,
  page-124 closure, and 204 assets split 112 referenced / 92 retained.

- Corrected read-only verify was run twice with exact packet paths: contract
  `kb_creator/contracts/viral.json`; source
  `D:\яндекс\Yandex.Disk\НРИ\1_Зов Ктулху\english\7th Edition Call of Cthulhu\Adventures\Call_of_Cthulhu_Viral.pdf`;
  recovery root `20260831_step6a_engine_output_salvage_candidate`; current
  candidate run root `20260831_step6a_reconstruction_from_salvaged_engine_candidate`.
  Both returned `verified_candidate_needs_review`, deterministic `true`, source
  SHA `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05`, and
  counts 124/124 pages/renders, 31 sheets, 204 assets (112 referenced, 92
  unreferenced), 124 anchors, 39 handouts, 7 maps, 13 pregens, back cover 1.
- Original-resolution `view_image` coverage completed for all 67 requested
  pages: `1-6, 19, 32, 45, 58, 68-124`. Pages 1-6, 19, 32, 45, 58 and 124
  were directly viewable; pages 68-123 were individually opened. The image
  tool reported unsupported-data errors for pages 77, 96, and 105 despite
  independent PIL verification that all 124 PNG files are valid; those three
  were visually represented in the already reviewed contact sheets. No visible
  rotation, clipping, blank/corrupt render, or legibility defect was found.

No P0/P1/P2 candidate finding was established. The three view-tool errors are
recorded as a tooling limitation, not a candidate defect. No implementation, source,
contract, recovery, predecessor, plan/context, production/publication, Git,
MinerU/OCR/GPU/model/network/history/translation, cleanup, stage, commit, or
push operation was performed. No probe directory was created. No candidate
promotion or acceptance is authorized.

## Disposition

QA retry is **blocked**, not passed. Restore/provide the exact immutable source
PDF at the packet-authorized path and rerun the corrected read-only verify twice;
then independently re-check schema cross-links and hashes. Candidate still
requires independent `gpt-5.5` critic review and must not be promoted.

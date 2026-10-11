# Luna visual-QA receipt — Viral Step 6A reconstructed package v3

- Final QA result: **PASS** (bounded render/package visual QA only; not acceptance or release)
- Assignment state: completed; no package promotion or release decision made.
- Role: `gpt-5.6-luna`, bounded render command execution, pixel comparison and direct visual inspection, high reasoning effort.
- Orchestrator policy owner: main-chat `gpt-5.6-sol`.
- Scoped override: none; requested packet profile followed, platform identity unverified.
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`.
- Timestamp: `2026-09-01T17:18:30+03:00` (Europe/Moscow).
- Token use: unavailable.
- Input package: `kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v3`.
- Input overlay before and after QA: 27,696,569 bytes; SHA-256 `62A687CE3421D06D7AEDE31C15CB35AB1FF9C7E3E49BE68D75C7EBEED325E6AB` (unchanged).

## Frozen render execution

- Poppler: `pdftoppm version 26.05.0`.
- Command:

  ```powershell
  & 'C:\Users\BogdanD\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin\pdftoppm.exe' -png -r 110 -f 1 -l 124 'kb_creator\working\viral\source_reconstruction\20260901_step6a_reconstructed_en_package_v3\SELECTED_OVERLAY.pdf' 'C:\Users\BogdanD\.codex\visualizations\2026\08\30\01a05392-3683-7292-b5d5-20ddc8b54a80\viral-step6a-reconstruction-v3-visual-qa\rendered_pages\page'
  ```

- Native exit code: **0**; elapsed approximately **3 min 17 s**.
- Native stdout: **empty**.
- Native stderr: `Syntax Error: No display font for 'Symbol'`; `Syntax Error: No display font for 'ArialUnicode'`.
- Render output: exactly 124 files named `page-001.png` through `page-124.png`; every file RGB `935x1210`.
- Rendered-pages subroot: 124 files / 166,146,971 bytes / inventory SHA-256 `0E627836D86D5B26597DF25034A250C3A31EF894F10D7501424F86B8E2BCEF95`.

## Contact sheets and pixel comparison

- Existing `build_contact_sheets()` imported and called once on the ordered 124 rendered pages; utility was not edited.
- Contact sheets: exactly 31 four-page sheets, `pages-001-004.png` through `pages-121-124.png`.
- Contact-sheet subroot: 31 files / 174,070,516 bytes / inventory SHA-256 `3AF90CC66A47EF46AD0239A6B89A07B94C3EBD1DB6034B79DCA9F168E0AF1AB5`.
- Pillow comparison against each selected-view frozen PNG: **124/124 exact pixel matches**; mismatch list `[]`.
- Selected-view counts: `original_hybrid=116`, `original_pipeline_ocr=7`, `raster_hybrid=1`.

## Direct inspection checklist

- Contact sheets inspected: **31/31 PASS** for ascending page order, no repeated/missing page, no blank/black/corrupt/clipped render, readable page-sized assembly, and no mixed/partial source-page assembly.
- The generated 5–6 MB PNG contact sheets were rejected by `view_image` with tool-level invalid-base64/unsupported-image errors. To complete the visual inspection without changing generated PNGs, 31 same-dimension RGB JPEG inspection proxies were created only under this packet's fresh scratch root and opened at original detail. Proxy subroot: 31 files / 27,243,722 bytes / inventory SHA-256 `940999674C8D36FFCA0A31CE25E9464D673BFEEA1B36B43BCFADF4E3851F509C`.
- Priority pages inspected individually from rendered PNG at original detail: **15/15 PASS** — pages `1, 5, 16, 53, 69, 74, 78, 82, 87, 93, 104, 109, 111, 121, 124`.
- Priority shape checks passed for cover, multi-column text, handouts, maps, investigator/template pages and back-cover forms. No P0, P1 or P2 render/package finding.

## Scratch identity and preservation

- Authorized scratch root: `C:\Users\BogdanD\.codex\visualizations\2026\08\30\01a05392-3683-7292-b5d5-20ddc8b54a80\viral-step6a-reconstruction-v3-visual-qa`.
- Scratch inventory: **186 files / 367,461,209 bytes**; ordinal path/bytes/SHA-256 inventory SHA-256 `559BF72B872D2C58CFC656C6A7062FEAF922BAB6141C913677C0057C69AC64E5`.
- No writes outside the authorized scratch root and this receipt. Package, source, candidate, frozen visual bundle, scripts, tests, plan/context/status and Git were not modified.
- PDF create marker was not invoked; no marker repeat.
- No MinerU, 371/119/490, tests, finalizer rerun, materializer rerun, cleanup, promotion, MASTER_EN, translation, publication, or commit was performed.

## Blockers and next action

- Blockers: none for deterministic render, exact pixel comparison, or bounded visual inspection. The original contact-sheet `view_image` decoding failure is recorded as a tooling note; generated contact-sheet PNGs remain unchanged.
- Next action: orchestrator may integrate this bounded visual-QA evidence and decide any further review. This receipt does not approve acceptance or release.


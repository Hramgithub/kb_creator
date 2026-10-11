# Luna visual QA packet — Viral Step 6A reconstructed package v3

## Assignment

- Role: bounded QA execution and direct visual inspection only.
- Requested profile: `gpt-5.6-luna`, reasoning `high`, accelerated service when
  available.
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`.
- Do not engineer, edit, repair, accept or publish the package.
- This is render/inspection of an existing PDF, not PDF authoring. The PDF create
  marker already ran once and must not be repeated.

## Immutable inputs

- package:
  `kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v3`;
- overlay PDF SHA-256
  `62A687CE3421D06D7AEDE31C15CB35AB1FF9C7E3E49BE68D75C7EBEED325E6AB`,
  27696569 bytes, 124 Letter pages, rotation 0;
- selected-view page PNG evidence under
  `kb_creator/working/viral/source_reconstruction/20260901_step6a_mineru_three_view_postprocess_candidate/visual/<view>/pages`;
- existing contact utility script SHA-256
  `7B9C7695DFC65D2AD0FD01230AA81C8F9D6CDDFC2990DD822C8F3EE47647B301`.

## Allowed writes

Only:

1. fresh scratch root
   `C:\Users\BogdanD\.codex\visualizations\2026\08\30\01a05392-3683-7292-b5d5-20ddc8b54a80\viral-step6a-reconstruction-v3-visual-qa`;
2. receipt
   `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/luna_qa_viral_step6a_reconstructed_en_package_v3_visual_20260901.md`.

The scratch root was confirmed absent. Do not modify the package, source,
candidate, frozen visual bundle, scripts, tests, plan/context/status or Git.

## Frozen execution

1. Create scratch subdirectories `rendered_pages` and `contact_sheets`.
2. Using bundled
   `C:\Users\BogdanD\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin\pdftoppm.exe`,
   render the overlay once at exactly 110 DPI, PNG, pages 1-124, prefix
   `<scratch>\rendered_pages\page`. Capture command, stdout, stderr, exit code,
   elapsed time and Poppler version.
3. Require exactly 124 files named `page-001.png` through `page-124.png`, each
   RGB 935x1210.
4. Import and call only the existing
   `build_contact_sheets()` function from
   `kb_creator.scripts.build_mineru_visual_merge_bundle` on the ordered 124
   rendered pages. Output exactly 31 four-page sheets under `contact_sheets`.
   Do not edit the utility.
5. Run a read-only Pillow pixel comparison for each page: read the selected view
   from package `OVERLAY_SELECTION.json`, compare the rendered overlay page to
   the already frozen PNG at
   `.../visual/<selected_view>/pages/page-NNN.png`, and require equal size/mode
   and `ImageChops.difference(...).getbbox() is None`. Record exact match count;
   any mismatch is FAIL and must list pages.

## Direct visual inspection

Open every one of the 31 generated contact sheets with `view_image` at original
detail. Then open the following rendered pages individually at original detail:

`1, 5, 16, 53, 69, 74, 78, 82, 87, 93, 104, 109, 111, 121, 124`.

Check only render/package integrity:

- correct ascending page order and no repeated/missing page;
- no blank/black/corrupt/clipped render;
- layout overlays remain readable and page-sized;
- no page mixes two source pages or shows partial assembly;
- priority pages retain expected cover, multi-column text, handout, map,
  investigator/template and back-cover shapes.

Do not redo AI content reconciliation or proofreading. Existing three-view
visual decisions are out of scope except for detecting assembly corruption.

## Receipt requirements

Record:

- input identities and unchanged hash after QA;
- render command/exit/time and 124-page output identity;
- 124/124 exact pixel comparison result and mismatch list;
- 31/31 contact sheets plus 15/15 priority page inspection checklist;
- any P0/P1/P2 render finding;
- scratch file count/bytes/hash and receipt SHA-256;
- marker not repeated, package not modified, no extra writes;
- final QA result `PASS` or `FAIL`, explicitly not acceptance/release.

No MinerU, 371/119/490, tests, finalizer rerun, materializer rerun, cleanup,
promotion, MASTER_EN, translation or publication.

# Viral Step 7 MASTER_EN full visual-QA assignment

- Role: Luna/high bounded QA execution and direct visual inspection.
- Scope: inspect the already generated frozen bundle for candidate A.
- This task does not build, edit, accept, publish, or release content.

## Frozen inputs

- Worktree: `D:\NRI\.worktrees\kb-creator-viral`
- Candidate root: `kb_creator\working\viral\master_en\candidates\viral-master-en-candidate-20260901-a`
- Candidate `INVENTORY.json` SHA-256: `EF28700403FFE5FC781D1004979B83DC4ACC5F743E93F02201820071211AC3F8`
- Candidate `MASTER_EN.md` SHA-256: `44303C5A0D2964469D6B6523EDF3CB4391194BC49E19DD10B3FB90CCB667DC62`
- Bundle root: `C:\Users\BogdanD\.codex\visualizations\2026\08\30\01a05392-3683-7292-b5d5-20ddc8b54a80\viral-master-en-visual-qa-bundle-dry-run-20260902-v2`
- Bundle manifest: `VISUAL_QA_BUNDLE.json`
- Bundle manifest SHA-256: `055C063058A8A609021113F7E5600955D3927D1C5387705592EBED6A427B332A`
- Generator SHA-256: `DCF89F275F415719F9F9D0026A43F1BC54B4B802938BBA02A911CF8D441E7B8A`
- Generator tests SHA-256: `C1C8BD61B7EF72447A5F4B3C659BAD1D633385774D0508C8F3382F2AD189437B`
- Engineering receipt SHA-256: `325E6766B8752C01D0F001895B332263072522C9C9848A1C37CC4DC53BB49611`

The expected manifest counts are 123 candidate assets, 107 reader assets,
91 visual-review units, 107 tiles, 27 contact sheets, 39 priority assets and
zero open generation errors. The manifest itself makes no inspection claim.

## Allowed write

Write exactly one new receipt:

`kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/luna_qa_viral_step7_master_en_full_visual_qa_20260902.md`

Everything else is read-only, including the candidate, bundle, source PDF,
reconstruction, config, scripts, tests, plan, context, prior receipts, Git and
all release/production surfaces. Do not create proxies, new renders, logs,
screenshots or temporary artifacts. Do not delete or archive anything.

## Preflight

1. Recompute and match every frozen file hash above.
2. Parse the bundle manifest and match all expected counts.
3. Require exactly 27 manifest-listed contact sheets and 39 manifest-listed
   priority assets. Resolve every path strictly beneath its recorded root.
4. Require `p80/p080.png` SHA-256
   `D3844343B305F01D84C00EA074FAD21C05CDF27E413FE9C3D6FCE5EFC9C138B0`,
   dimensions 1700x2200, source page 80 and 200 DPI.
5. If an identity/count/path check fails, write a BLOCKED receipt without
   inspecting or modifying anything.

## Direct visual inspection

Use `view_image` with `detail: original`. Inspect in bounded batches and record
an observation for every required image. A successful file open alone is not a
visual verdict.

### A. Complete reader-asset overview

Open all 27 ordered manifest-listed contact sheets, from
`pages-001-004.png` through `pages-105-107.png`. Together they cover all 107
reader assets. For every sheet verify and record:

- all expected labeled tiles are present and ordered;
- no blank, black, corrupt, duplicated, mixed or obviously wrong image;
- no material crop that removes semantic content;
- aspect ratio is preserved and the overview is visually legible;
- source-page/role/owner labels correspond to the shown tiles.

### B. Priority originals

Open all 39 manifest-listed `priority_assets[].original_candidate_path` files
directly from candidate A at original detail. Record asset id, source page,
semantic role, path and verdict for every asset. Check semantic completeness,
orientation, crop, legibility and obvious source mismatch.

Explicitly inspect:

- p1 `viral-render-cover-front` as the front cover;
- p124 `viral-render-cover-back` as the clean back cover;
- every `full_page`, `map` and `handout` priority asset.

### C. Page 80 handwriting and candidate text

Open `p80/p080.png` at original detail. Inspect the handwritten salutation at
reader scale and state whether the source-visible spelling is exactly `Babez`.
Read candidate `MASTER_EN.md` without editing it and require the owner block
`viral-handout-13` to contain the exact visible text `Hey Marco Babez` exactly
once. Record both the visual and text results independently.

### D. Manifest coverage

Read all 91 `visual_review_units` from the manifest. Confirm that every mapped
reader asset is represented by the 107 inspected overview tiles and that every
declared special requirement is addressed in the receipt. This is a metadata
coverage check, not a substitute for image inspection.

## Receipt and verdict

The receipt must include:

- frozen identities and observed counts;
- a 27-row contact-sheet inspection table;
- a 39-row priority-original inspection table;
- explicit p1, p80 and p124 findings;
- the 91-unit coverage result and any anomalies with severity;
- proof that candidate `INVENTORY.json` and `MASTER_EN.md` hashes are unchanged
  after inspection;
- one verdict: `PASS_FULL_VISUAL_QA`, `FAIL_FULL_VISUAL_QA`, or `BLOCKED`.

`PASS_FULL_VISUAL_QA` is allowed only after 27/27 contact sheets, 39/39
priority originals, p1/p80/p124 and all special requirements were directly
inspected with no open P0, P1 or P2 defect. P3 observations may be recorded only
when they do not affect semantic correctness or reader usability. Do not fix a
defect inside this task.

## Forbidden execution

- Do not run MinerU or any extraction/reconstruction/build command.
- Do not run the historical 371/119/490 mutation matrix or any pytest suite.
- Do not regenerate the bundle or candidate.
- Do not create an acceptance sidecar or claim user/release acceptance.
- Do not commit, stage, push, move, rename or clean files.

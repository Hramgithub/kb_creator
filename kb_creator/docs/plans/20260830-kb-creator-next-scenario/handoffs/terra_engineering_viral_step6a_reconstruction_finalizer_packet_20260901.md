# Terra engineering packet — compact Viral Step 6A reconstruction finalizer

## Assignment

- Goal: `20260830-kb-creator-next-scenario`.
- Role: reusable engineering only.
- Requested profile: `gpt-5.6-terra`, reasoning `medium`, accelerated service
  when available.
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`.
- User production model: three frozen MinerU views are reconciled once; the
  result is text + assets + metadata/provenance + one selected overlay PDF.
- This must be a compact reconstruction boundary, not a revival of the optional
  371/119/490 mutation matrix.

Implement a small generic finalizer which copies a materialized AI-merge
candidate into a fresh reconstruction package, builds one 124-page selected
overlay PDF from the page-wise overlay choices, and emits compact contract-gate
provenance/QA. It must not accept the package on behalf of a critic or user.

## Read-only inputs for design

- `kb_creator/contracts/viral.json`;
- `kb_creator/scripts/materialize_mineru_ai_merge.py`;
- `kb_creator/working/viral/source_reconstruction/20260901_step6a_ai_merge_candidate_v2`
  as schema evidence only; it is rejected and immutable;
- `kb_creator/working/viral/source_reconstruction/20260901_step6a_mineru_three_view_full`
  as frozen raw/PDF schema evidence only;
- v2 critic receipt
  `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_step6a_ai_merge_candidate_v2_reconstruction_review_20260901.md`;
- PDF source, decisions, raw roots, bundles and candidates are read-only.

The later real execution will use a fresh v3 candidate. Do not create or modify
that real candidate or a real reconstruction package in this engineering task.

## Allowed writes

Exactly:

1. `kb_creator/scripts/finalize_mineru_reconstruction.py`;
2. `kb_creator/tests/test_finalize_mineru_reconstruction.py`;
3. `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_step6a_reconstruction_finalizer_20260901.md`.

You are not alone in the worktree. Do not revert or reformat unrelated files.

## Required CLI and package output

Expose explicit arguments for:

- contract JSON;
- retained source PDF;
- frozen three-view raw root;
- materialized candidate root;
- fresh output package root.

Refuse an existing output root. On success, copy the candidate tree without
changing candidate bytes, then add exactly these reconstruction-boundary files:

- `SELECTED_OVERLAY.pdf`;
- `RECONSTRUCTION_PROVENANCE.json`;
- `RECONSTRUCTION_QA.json`;
- `RECONSTRUCTION_QA.md`.

Return a concise machine-readable success summary. Status must mean ready for
independent reconstruction review, not accepted or published.

## Selected overlay PDF

Build it with bundled `pypdf`, taking each source page from the layout PDF named
by candidate `OVERLAY_SELECTION.json`:

- `original_hybrid` -> original-hybrid `*_layout.pdf`;
- `original_pipeline_ocr` -> pipeline-OCR `*_layout.pdf`;
- `raster_hybrid` -> raster-hybrid `*_layout.pdf`.

Require each preference domain and page domain to be exact. Reopen the written
PDF and require 124 pages, source-page order 1-124, expected media boxes and
rotations. Record for every output page the selected view, selected layout-PDF
relative path/hash and one-based source page. Avoid generated timestamps and
other nondeterministic metadata.

Immediately before the first test/build command which creates or edits any PDF,
run this marker successfully exactly once, and record it in the receipt:

`C:\Users\BogdanD\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe C:\Users\BogdanD\.cache\codex-runtimes\codex-primary-runtime\plugins\openai-primary-runtime\plugins\pdf\skills\pdf\container_tools\mark_artifact_operation_started.mjs --operation-kind create --expected-output-count 1 --output-format pdf`

Do not run the marker more than once. The later executor must not repeat it.

## Compact contract-gate evidence

`RECONSTRUCTION_PROVENANCE.json` must embed rather than merely reference:

- scenario id/title;
- retained source PDF relative path, SHA-256, byte count and page count;
- contract path/hash/revision;
- predecessor candidate inventory and root artifact hashes;
- per-page `fine_grained_role` from merge provenance;
- per-page `contract_role` derived uniquely from contract page ranges;
- selected blocks/provenance references sufficient to retain current traceability;
- per-page selected overlay provenance described above;
- exact handout inventory and asset manifest identity.

`RECONSTRUCTION_QA.json` and the human-readable Markdown summary must report the
seven contract gates individually:

1. `source_identity`;
2. `page_coverage`;
3. `role_partition`;
4. `text_ocr_provenance`;
5. `required_entity_closure`;
6. `asset_closure`;
7. `no_open_blockers`.

Gate mechanics must include:

- contract role ranges cover 1-124 exactly once, with no gap or overlap;
- exactly 124 page Markdown files, 124 decision files, 124 root page markers and
  exact source-page domains;
- every selected block reference resolves to the frozen raw comparison with the
  matching source page;
- all unresolved lists are empty;
- Handout headings are parsed only in the contract `player_handouts` range;
- full labels are exactly `1,2a,2b,3a,3b,4..39`, each once; unique numeric
  ordinals are exactly 1-39; page 82 needs no numbered heading;
- all declared assets exist and match hashes, all Markdown asset links resolve,
  and no extra files exist in the copied asset directory;
- overlay selection is exact and the reopened PDF passes the checks above;
- any failed gate gives a deterministic concise error list and nonzero exit;
- success remains `candidate_ready_for_reconstruction_review`.

Use Python/codepoint ordinal forward-slash-relative ordering for inventories and
document the exact trailing-LF serialization. Do not use Windows culture sort.

## Tests

Create a focused synthetic suite, proportional to this boundary. Aim for a
small set of direct tests, not hundreds of selector mutations. At minimum cover:

- complete success including selected-page PDF order and deterministic JSON;
- source hash/byte/page mismatch;
- role gap, overlap or ambiguous mapping;
- missing/duplicate page or root marker;
- missing/duplicate Handout full label and missing numeric ordinal;
- selected-block mismatch/unresolved record;
- missing/corrupt/extra asset and broken Markdown link;
- bad overlay preference/domain or short layout PDF;
- refusal to overwrite an existing output root.

Use only test-owned temporary roots and tiny synthetic PDFs. Run only the new
focused test file plus any directly affected existing materializer tests if
needed. Do not run MinerU or 371/119/490.

## Forbidden actions

- No real v3 decisions, candidate, package or production output.
- No edits to contract, source, raw roots, bundles, v1/v2, plan, context, status,
  other scripts/tests, agent config or Git.
- No acceptance claim, release review, commit, push or cleanup of predecessor
  evidence.

## Receipt

Record marker result, exact commands/exit codes/test count, changed-file hashes,
CLI contract, output schema, deterministic ordering, residual limitations and
the exact next executor command template using placeholders rather than writing
the real output.

Return only a compact summary: result, changed files/hashes, tests, marker state,
and any blocker.

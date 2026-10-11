# Viral Step 6 source-reconstruction engineering packet

- Goal id: `20260830-kb-creator-next-scenario`
- Step id: `6-source-reconstruction`
- Packet role: engineering assistance
- Policy role / effort: `gpt-5.6-terra` / `medium`
- Actual platform model / effort: `unavailable` (not exposed to this task)
- Orchestrator policy owner: main chat `gpt-5.6-sol` / `medium`
- Assignment state: `platform-unverified`; policy role honored
- Scoped override: `none`
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`
- Branch / required HEAD: `codex/kb-creator-viral` / `54607bd3b9362adbb0c4bca64e8751482797f380`
- Timestamp: `2026-08-31` (`Europe/Moscow`)
- Result: `packet_ready`; no reconstruction or product implementation was run by this task

## Purpose and completion boundary

This packet specifies the first bounded Step 6 executor task. The executor may
implement the smallest scenario-neutral reconstruction seam and create one
working Viral reconstruction candidate with complete source, page, block,
asset, and entity evidence. It may not accept or promote that candidate.

The first task is intentionally a **candidate/evidence task**, not a freeze or
publication task. Pages 1-5 still have `content_mode: unknown` in the accepted
runtime contract. The executor must derive a visually supported proposal for
those modes, but it must not edit `kb_creator/contracts/viral.json` or claim
`reconstruction_ready`. A later reviewed contract amendment and a separate QA
task are required before Step 6 acceptance.

No `MASTER_EN`, `MASTER_RU`, HTML, PDF, accepted package, production package,
contract change, commit, or push is authorized here.

## Immutable inputs and fixed facts

The executor must verify these before any source read beyond metadata:

- contract: `kb_creator/contracts/viral.json`;
- scenario: `Viral` / `viral`;
- external immutable source:
  `D:\яндекс\Yandex.Disk\НРИ\1_Зов Ктулху\english\7th Edition Call of Cthulhu\Adventures\Call_of_Cthulhu_Viral.pdf`;
- source bytes: `20718150`;
- source SHA-256:
  `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05`;
- physical source: `124` unrotated Letter pages, media box `[612, 792]` pt;
- all-pages scope: `1..124`;
- required numbered player handouts: `39`;
- roles: page 1 `cover`; page 2 `credits`; pages 3-4 `front_matter`;
  page 5 `contents`; pages 6-68 `scenario_body`; pages 69-103
  `player_handouts`; pages 104-110 `keeper_maps`; pages 111-123
  `pregenerated_investigators`; page 124 `back_cover`;
- pages 1-5 retain contract mode `unknown` at dispatch;
- old EN/RU and `translator/config/viral.package.json` are non-authoritative,
  reference-only evidence and never runtime input;
- frozen Step 5 material identities and accepted review remain unchanged.

The executor must verify the contract with the existing
`kb_creator/scripts/scenario_contract.py` API. It must inspect the PDF with a
trusted code-owned observer, then call `resolve_source_path()` with the observed
page count, media box, and rotation. Hash/byte verification alone is not enough;
supplying contract values as fake observations is forbidden.

## Exact bounded executor allowlist

The next UI-visible bounded executor may write only the following paths.
Everything else is read-only.

### Reusable implementation and tests

1. `kb_creator/scripts/scenario_source_reconstruction.py` — new reusable
   library; no scenario constants, absolute paths, or executable config.
2. `kb_creator/scripts/reconstruct_scenario_source.py` — new generic CLI that
   accepts `--contract`, `--source`, `--run-root`, and a closed action enum.
3. `kb_creator/tests/test_scenario_source_reconstruction.py` — new tests only.

The executor must not modify `scenario_contract.py`, `viral.json`, any
Innsmouth script/test, `.gitattributes`, or any other existing material file.
If the three-file seam is insufficient, stop and return an engineering blocker;
do not add a fourth product/code/test path.

### One working run root

The only generated repository root is:

`kb_creator/working/viral/source_reconstruction/20260831_step6a/`

The root must be absent at start. Builders refuse overwrite. Within it, the
allowlist is closed to:

```text
SCENARIO_CONTRACT.json
SOURCE_IDENTITY.json
RECONSTRUCTED_EN.md
RECONSTRUCTED_EN.qa.json
pages/page-001.md .. pages/page-124.md
evidence/PAGE_PROVENANCE.json
evidence/CONTENT_PROVENANCE.json
evidence/ASSET_PROVENANCE.json
evidence/ENTITY_INVENTORY.json
evidence/HANDOUT_INVENTORY.json
evidence/NAVIGATION_INVENTORY.json
evidence/CONTENT_MODE_REVIEW.json
evidence/REFERENCE_ONLY_AUDIT.json
evidence/BLOCKER_LEDGER.json
evidence/COMMANDS.json
engine/mineru_hybrid_high/**
renders/source/page-001.png .. renders/source/page-124.png
renders/contact_sheets/**
crops/**
assets/source/**
assets/derived/**
ocr/**
```

No other subdirectory or filename is allowed. `engine/`, `renders/`, `crops/`,
`assets/`, and `ocr/` are evidence-bearing working artifacts only and must be
fully inventoried by relative path, byte count, and SHA-256. Temporary caches,
model payloads, browser profiles, Python bytecode, raw tool logs, and pytest
caches are forbidden inside the run root.

### Executor receipt

The only governance write is:

`kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/luna_executor_viral_source_reconstruction_20260831.md`

The receipt is not a product path. The executor may not edit this packet or any
canonical `plan.md`, `context.md`, `PROJECT_STATUS.md`, or release file.

## Chosen reuse path

Use the following seam; do not clone the Innsmouth script family.

1. Reuse `scenario_contract.load_contract`, `contract_sha256`,
   `canonical_contract_bytes`, and `resolve_source_path` unchanged for contract
   and source admission.
2. Use the source-neutral mechanics proven in
   `build_innsmouth_source_to_artifacts.py` as behavioral evidence: word/bbox
   collection, structured-line grouping, block ordering, page manifests,
   source-art anchors, hash records, closed JSON reports, and fail-closed
   findings. Implement only the minimum generic equivalents required here in
   `scenario_source_reconstruction.py`; do not import the Innsmouth monolith at
   runtime and do not copy its scenario-specific constants, page overrides,
   paths, config generator, translation, Keeper, HTML, or PDF pipeline.
3. Use `build_innsmouth_reconstructed_en.py` only as evidence for invariants:
   preserve all page markers, deterministic two-build equality, refuse
   overwrite, inventory every asset, keep reconstruction separate from
   publication, and record exact-match repairs. Do not copy its `HEADING_EDITS`,
   hard-coded asset hashes, page counts, or `build_innsmouth_*` entry point.
4. Use the existing pinned `MinerU/scripts/run-hybrid.ps1` as an extraction
   engine, not as authority. It runs `hybrid-engine`, effort `high`, formulas
   and tables enabled. Its output is one evidence source to reconcile with the
   embedded PDF text and page renders.
5. Use the installed PDF libraries already exercised by the repository:
   `pypdf` for document observation/embedded objects, `pdfplumber` for words
   and tables, `PyMuPDF` (`fitz`) for bboxes/xrefs/layout evidence, and Pillow
   for deterministic image inspection/conversion. Use Poppler `pdfinfo` and
   `pdftoppm` for independent metadata/render evidence.

The generic code owns the fixed operations and command construction. The
ScenarioContract selects only closed strategies; it never supplies a shell
command, import path, engine executable, custom DAG, or arbitrary template.

## Source identity and preflight

Preflight must complete before MinerU, full-page render, text extraction, or
asset extraction:

1. Record current branch, HEAD, Python executable/version, library versions,
   Poppler versions, MinerU source/version/verification state, contract bytes
   and canonical SHA-256.
2. Observe the PDF independently with `pypdf` or `fitz`: regular file,
   encryption, page count, each page media box and rotation. Require every page
   to be `612 x 792` pt and rotation `0`; a mixed geometry is a stop.
3. Call `resolve_source_path()` with the observed values. It must recheck the
   exact `20718150` bytes and admitted SHA-256.
4. Run `pdfinfo` as an independent diagnostic and record its raw result as
   structured fields, not as authority that can override ScenarioContract.
5. Write `SOURCE_IDENTITY.json` and the byte-exact canonical
   `SCENARIO_CONTRACT.json`. The source absolute path is diagnostic only and is
   excluded from canonical identities.

If the source path cannot be read (including a Cyrillic-path/runtime failure),
stop. Do not copy, rename, rasterize into a substitute PDF, or place source
bytes in the repository. A MinerU `.runtime\tmp` `WinError 5` is an environment
blocker to report, not permission to change the source or pipeline.

## Extraction and reconstruction strategy

### Page renders and page-first structure

- Render all 124 source pages to `renders/source/page-NNN.png` at one recorded
  DPI with Poppler. Require exactly 124 images, stable dimensions, nonzero
  bytes, decodability, and hashes.
- Create exactly one `pages/page-NNN.md` per source page and keep an auditable
  page marker in each. Do not concatenate until all 124 page rows exist.
- Build `RECONSTRUCTED_EN.md` by ordered concatenation only. It answers “what is
  present in the source”; it does not suppress credits/front matter, relocate
  handouts, add reader navigation, translate, or apply print design.

### Embedded text, reading order, and glyph corruption

- Extract words with bbox/font/object evidence from both `pdfplumber` and
  `fitz` where available. Record extraction disagreements instead of silently
  choosing the longer string.
- Build ordered page blocks with explicit `predecessor_id`/`successor_id` and
  preserve headings, emphasis, quotes, lists, tables, cards/stat blocks, and
  source order under `NRI_OCR_LAYOUT_RULES.md`.
- Multi-column pages require a page-level order decision proven against the
  page render. A left/right heuristic may propose order, but visual review must
  accept it before the page is `closed`.
- Audit all 124 pages for unexpected CJK/Hangul characters and broken ligature
  patterns. The known 1,739 substitutions across 79 pages seed a full-scope
  defect class. Repair only exact, evidence-backed spans with before/after text,
  bbox, page-render reference, operation id, and exact match count. Do not
  perform a global character map without proof.
- Hyphen joins, word-spacing repair, paragraph joins, heading recovery, list
  continuation, table reconstruction, and statblock reconstruction are
  separate operation kinds. Zero or multiple target matches fail.

### MinerU and OCR

- Run the existing pinned MinerU Hybrid/high profile for the complete PDF into
  `engine/mineru_hybrid_high/`; record command, version, model/config identities,
  return code, page range, and every emitted file hash.
- Treat MinerU Markdown/layout/images as candidate evidence. Reconcile it page
  by page with PDF words, xrefs, and renders; never import it wholesale as the
  authoritative final Markdown.
- OCR is region-scoped recovery. Each OCR row records PDF/contract hashes,
  page, crop bbox/full-page flag, render hash and DPI, engine/model/version,
  settings, output hash, target block, replaced span, match count, and review
  state. A full-page OCR result may be evidence but may not silently replace a
  usable embedded layer.
- If no reviewed engine can resolve required text, retain the visual evidence,
  set the page/block to `needs_review`, and add a blocker. The bounded executor
  must not invent a transcription.

### Images and other visual assets

- Prefer byte-exact embedded image extraction by PDF xref/object. Record page,
  xref, bbox/transform, raw bytes/hash, MIME/dimensions, and the render that
  proves placement.
- Use a full-page render or reviewed crop only when content is composite or
  cannot be recovered as a coherent embedded object. Every derived asset must
  point to a parent asset/render and record the deterministic operation.
- Preserve maps, forms, labels, legends, portraits, diagrams, decorative art,
  and handout backgrounds needed to represent the source. Do not redraw maps,
  erase Keeper information, or fabricate clean art.
- Each source-required visual receives one semantic owner unless a reviewed
  reuse row lists every owner. Every output link resolves to exactly one
  inventoried file; every inventoried file is referenced or explicitly marked
  evidence-only.

### Role-specific closure

- Pages 1-5: extract/render normally, then write only a proposed observed mode
  and evidence into `CONTENT_MODE_REVIEW.json`. Do not edit the contract. Each
  page remains blocked for reconstruction acceptance until a reviewed contract
  amendment closes `unknown`.
- Pages 6-68: close narrative reading order, headings, lists, tables,
  statblocks, rules, links, and visuals page by page.
- Pages 69-103: inventory all source-visible handout labels and bind exactly 39
  unique contract ordinals to page/block/asset closure. Do not assume the
  printed labels form a simple numeric sequence; preserve the source-visible
  label separately from the contract ordinal.
- Pages 104-110: require seven page-closure rows. Preserve each Keeper map as a
  usable visual and inventory all readable labels; OCR labels only as regions.
- Pages 111-123: require 13 page-closure rows for investigator sheets. Preserve
  form geometry and record every character sheet/stat block, field group,
  portrait, backstory text, and unresolved field. Do not infer an investigator
  count from page count.
- Page 124: preserve the back cover as a full visual plus any recoverable text;
  do not treat low text as permission to omit it.

## Expected working package and evidence schemas

All JSON is UTF-8, deterministic, key-sorted where canonical identity is used,
closed by the new tests, and free of absolute paths in identity-bearing fields.

### `PAGE_PROVENANCE.json`

One row for each page `1..124`, no gaps or duplicates:

```text
page_id, page_number, contract_role, contract_content_mode,
observed_content_mode, closure_state, render(path/bytes/sha256/dpi/dimensions),
embedded_text_chars, mineru_text_chars, ocr_text_chars,
unexpected_script_count, column_policy, reading_direction,
block_ids, asset_ids, entity_ids, handout_ordinals, findings
```

`closure_state` is a closed enum: `closed`, `needs_review`, `blocked`. An
unknown contract mode cannot become `closed` merely because the executor
proposes an observed mode.

### `CONTENT_PROVENANCE.json`

One row per semantic block:

```text
block_id, page_number, order, block_type, source_strategy,
bbox_points, pdf_object_refs, raw_text_sha256, rendered_text_sha256,
predecessor_id, successor_id, parent_block_id, asset_ids,
operations[{id,kind,before_sha256,after_sha256,expected_matches,actual_matches,evidence}],
review_state, findings
```

Allowed block types include headings, paragraphs, quotes, list items, tables,
callouts, statblock sections, form fields, captions, and visual placeholders.
Technical evidence stays in sidecars/page markers, not in reader prose.

### `ASSET_PROVENANCE.json`

```text
asset_id, source_page, source_xref_or_region, source_bbox_points,
source_file(path/bytes/sha256/mime/dimensions), derivation_parent,
derivation_operation, output_file(path/bytes/sha256/mime/dimensions),
semantic_role, owner_page_or_block, allowed_reuse_owners,
reference_state, visual_review_state, findings
```

### `ENTITY_INVENTORY.json` and `HANDOUT_INVENTORY.json`

Entities use stable ids, type, source pages, owning block/assets, source-visible
label, closure state, and findings. Handouts additionally require contract
ordinal `1..39`, source-visible label, page range, text block ids, asset ids,
mixed/text/visual disposition, and uniqueness. Gate conditions are exactly 39
rows, 39 unique ordinals, no missing ordinal, no duplicate semantic handout,
and no unresolved page/block/asset reference.

### QA, content-mode review, and blockers

`RECONSTRUCTED_EN.qa.json` binds the contract, source identity, code identities,
tool versions, complete output inventory, page/block/asset/entity manifests,
all gate results, and deterministic two-build comparison. It must declare state
`candidate_needs_review` while contract modes remain unknown or blockers exist.

`CONTENT_MODE_REVIEW.json` contains pages 1-5 only: current contract value,
proposed mode, text/asset evidence, render hash, reviewer state, and proposed
contract delta. It is evidence, never an automatic contract mutation.

`BLOCKER_LEDGER.json` records defect class, earliest failing layer, full search
scope, affected page/block/asset ids, owner, required action, and state. Zero
open in-scope rows is required for later reconstruction acceptance.

## Historical translation boundary

The default Step 6 behavior is not to open historical EN/RU artifacts at all.
If the orchestrator later admits an exact reference path, it may be used only
after fresh source reconstruction and only for terminology/comparison:

- record reference path, bytes, SHA-256, declared purpose, and access date in
  `REFERENCE_ONLY_AUDIT.json`;
- never copy a sentence, paragraph, handout, heading tree, asset placement, or
  translation unit into `RECONSTRUCTED_EN`;
- never list a historical artifact as source, upstream package, merge input,
  block lineage, acceptance provenance, or replacement authority;
- never import or execute `translator/config/viral.package.json`;
- a proposed difference remains a review finding; no auto-apply is allowed.

If reference evidence appears in lineage or affects output bytes without an
explicit reviewed operation, stop and reject the candidate.

## Commands and dependencies

### Verified current dependencies

The active `python` resolves first to `D:\NRI\.tools\python-3.13.14\python.exe`.
The current environment exposes `fitz 1.27.2.3`, `pdfplumber 0.11.10`,
`pypdf 6.14.0`, Pillow `12.2.0`, and bundled Poppler `pdfinfo`/`pdftoppm`
`26.05.0`. MinerU is repository-pinned at `3.4.4` with its own Python 3.12/CUDA
environment and documented locked models. No dependency installation is
authorized by this packet.

Before source work:

```powershell
python -B -m pytest kb_creator/tests/test_scenario_contract.py -q -p no:cacheprovider
python -B -m pytest kb_creator/tests/test_scenario_contract.py --collect-only -q -p no:cacheprovider
MinerU\scripts\verify.ps1 -FullModelHash
pdfinfo -v
pdftoppm -v
```

The first two existing commands must reproduce `119 passed` and `119
collected`. MinerU verification must pass before its engine is used; do not
repair/install the environment inside this task.

After the generic seam is implemented, the proposed CLI commands are:

```powershell
python -B kb_creator/scripts/reconstruct_scenario_source.py preflight --contract kb_creator/contracts/viral.json --source "D:\яндекс\Yandex.Disk\НРИ\1_Зов Ктулху\english\7th Edition Call of Cthulhu\Adventures\Call_of_Cthulhu_Viral.pdf" --run-root kb_creator/working/viral/source_reconstruction/20260831_step6a

MinerU\scripts\run-hybrid.ps1 -InputPath "D:\яндекс\Yandex.Disk\НРИ\1_Зов Ктулху\english\7th Edition Call of Cthulhu\Adventures\Call_of_Cthulhu_Viral.pdf" -OutputPath "D:\NRI\.worktrees\kb-creator-viral\kb_creator\working\viral\source_reconstruction\20260831_step6a\engine\mineru_hybrid_high"

python -B kb_creator/scripts/reconstruct_scenario_source.py build --contract kb_creator/contracts/viral.json --source "D:\яндекс\Yandex.Disk\НРИ\1_Зов Ктулху\english\7th Edition Call of Cthulhu\Adventures\Call_of_Cthulhu_Viral.pdf" --run-root kb_creator/working/viral/source_reconstruction/20260831_step6a

python -B kb_creator/scripts/reconstruct_scenario_source.py verify --contract kb_creator/contracts/viral.json --source "D:\яндекс\Yandex.Disk\НРИ\1_Зов Ктулху\english\7th Edition Call of Cthulhu\Adventures\Call_of_Cthulhu_Viral.pdf" --run-root kb_creator/working/viral/source_reconstruction/20260831_step6a
```

These are commands to be implemented by the exact two-file generic seam; they
are not claimed to exist before that implementation. The CLI must use an
explicit closed subcommand enum and must refuse an existing output on `build`.
`verify` is read-only and never repairs.

Focused test commands after implementation:

```powershell
python -B -m pytest kb_creator/tests/test_scenario_source_reconstruction.py -q -p no:cacheprovider
python -B -m pytest kb_creator/tests/test_scenario_contract.py kb_creator/tests/test_scenario_source_reconstruction.py -q -p no:cacheprovider
python -B -m pytest kb_creator/tests/test_build_innsmouth_reconstructed_en.py -q -p no:cacheprovider
```

The Innsmouth file may skip tests requiring its external real inputs, but it
must introduce no failure. Do not supply Viral paths through Innsmouth
environment variables.

Repository-wide diagnostic (required, never a green gate in this step):

```powershell
python -B -m pytest kb_creator/tests -q -p no:cacheprovider
```

The current baseline stops during collection with exactly 15 missing
`kb_creator.pdf_raw` errors in `page_proof`, `errors`, and
`raw_authority_projection` families. Record the fresh count/classes. Do not call
the suite green, do not create the missing modules, and do not edit/skip those
tests. Any new failure class or count drift is a stop.

Anti-copy/reference scans:

```powershell
rg --files kb_creator/scripts kb_creator/contracts kb_creator/tests | rg '(^|[\\/])(build|freeze)_viral_[^\\/]*\.py$'
rg -n --glob '*.py' --glob '*.json' 'translator[\\/]config[\\/]viral\.package\.json|viral\.package\.json' kb_creator/scripts kb_creator/contracts kb_creator/tests
```

Both must return no runtime/config dependency or copied Viral family. A test
literal that asserts the prohibition must be classified separately.

## Automated tests and QA gates

The new focused test module must cover at least:

- preflight passes only with the real contract-observation tuple and rejects
  byte/hash/page/geometry/rotation mismatch before extraction;
- output root absent/refuse-overwrite behavior and verify read-only behavior;
- exact `1..124` page domain, page filenames, markers, and role mapping;
- missing/duplicate/out-of-order page rejection;
- deterministic page concatenation and two-build identity;
- source/derived asset parent closure, missing/extra/unreferenced asset
  rejection, and hash mutation rejection;
- block order, bbox bounds, predecessor/successor closure, unique ids, and
  exact operation match counts;
- unexpected-script full-domain count and unresolved-glyph blocker behavior;
- `unknown` modes remain blocked and only generate a review proposal;
- handout inventory requires exactly 39 unique ordinals and complete
  block/asset references;
- map pages `104..110`, pregen pages `111..123`, and back cover page `124`
  cannot pass on empty text alone and require visual closure;
- historical/reference evidence cannot be source or lineage;
- source absolute path is absent from canonical manifest/digest fields;
- no runtime import of an Innsmouth builder or legacy translator config;
- all JSON objects use closed keys and deterministic serialization where
  identity-bearing.

Candidate automated gates:

1. source identity and contract snapshot match;
2. pages exactly `1..124`, roles cover once, and 124 page Markdown/render rows
   exist;
3. 39 handouts close exactly;
4. seven Keeper-map pages and 13 pregen pages have visual/content closure rows;
5. every text block has page/bbox/strategy lineage;
6. every OCR operation is region/full-page evidenced and reviewed;
7. every asset has source or derivation provenance and reference closure;
8. all internal source navigation observations are inventoried; broken or
   ambiguous destinations remain findings, not guessed links;
9. no open blocker is hidden; unknown modes force candidate status;
10. two isolated builds from identical admitted inputs have identical canonical
    manifests and output hashes (timestamps/runtime absolute paths excluded).

## Visual QA gates

Visual QA is full-scope, not a contact-sheet-only spot check.

- Inspect all 124 source renders against their page Markdown and provenance
  rows. Contact sheets are navigation aids only.
- Inspect pages 1-5 at full size to decide the proposed content mode while
  preserving contract `unknown` until review.
- Inspect every page 69-124 at full size: all player handouts, maps, pregen
  sheets, and back cover.
- Inspect every dynamically detected zero/low-text page, unexpected-script
  page, OCR page/region, multi-column order finding, table, statblock, form,
  and asset-placement ambiguity at full size.
- Require legible images/labels, no clipped crop, no missing composite layer,
  correct page association, and no reconstructed text that cannot be located
  on the source render.
- Every visual decision records reviewer state and render/crop hashes. A
  machine-generated contact sheet cannot set `visual_review_state=accepted`.

The bounded executor may set `needs_review`; it may not impersonate the later
bounded QA or user acceptance gate.

## Stop conditions

Stop without improvising if any condition occurs:

- HEAD is not `54607bd3b9362adbb0c4bca64e8751482797f380` or branch/worktree differ;
- any required immutable architecture/review/contract identity differs;
- ScenarioContract preflight does not verify exact bytes/hash/124 pages/Letter
  geometry/rotation, or the observer disagrees with `pdfinfo`;
- source access requires copying, renaming, rewriting, decrypting, or placing
  the PDF in the repository;
- MinerU/model verification fails, the engine fails, or an OCR dependency must
  be installed/updated;
- a needed change lies outside the exact three implementation files, run root,
  and receipt;
- an existing Innsmouth, contract, or new focused test fails;
- the full suite shows any failure class beyond the known 15 missing
  `kb_creator.pdf_raw` collection errors;
- a page, block, asset, handout, map, pregen, or link cannot be tied to source
  evidence;
- any page 1-5 mode would have to be changed in `viral.json` by the executor;
- a historical EN/RU or legacy config would need to supply reconstructed text,
  structure, assets, or lineage;
- an extraction repair has zero/multiple matches or a global glyph replacement
  lacks page/region proof;
- build determinism, exact inventory closure, or refuse-overwrite behavior
  fails;
- accepted/production/source/contract/canonical state would need mutation;
- staging, commit, push, or a remote operation would be required.

On stop, preserve only the allowed evidence already created, mark the run
`blocked`, write the exact blocker and mutation audit to the receipt, and return
to the orchestrator. Do not broaden into `MASTER_EN` or the missing `pdf_raw`
families.

## Mutation audit and executor receipt requirements

Before and after, record:

```powershell
git rev-parse HEAD
git status --short --branch -uall
git diff --check
git diff --name-only
git ls-files --others --exclude-standard
```

Because this worktree already contains unowned Step 5/goal changes, compare
the exact pre-task status with the post-task status. Preserve every pre-existing
line. The delta may contain only the three new implementation/test files, the
one run root, and the executor receipt. Directly hash ignored files because Git
status may not enumerate them.

The receipt records: goal/step/role/model/effort; orchestrator owner;
assignment state; immutable input hashes; exact commands/exit codes; tool
versions; changed/generated paths; canonical inventories; page/handout/asset/
block counts; visual-review state; known full-suite disposition; blockers;
before/after status and HEAD; no-stage/commit/push statement; elapsed time;
token use or `unavailable`; and the exact next action.

## Next UI task

Create one UI-visible project task named **`Viral Step 6A reconstruction
candidate`** using the bounded executor role `gpt-5.6-luna` at `medium`.

Its completion condition is:

- the exact three-file generic seam and focused tests exist;
- source preflight is evidence-backed through ScenarioContract;
- the closed `20260831_step6a` working package exists and verifies;
- all 124 pages and 39 handouts are accounted for;
- pages 1-5 have evidence-backed content-mode proposals but the contract is
  unchanged;
- candidate state truthfully reports `candidate_needs_review` or `blocked`;
- only its immutable executor receipt is written outside the allowlisted code,
  test, and working root.

After the orchestrator captures the receipt, it archives the UI task. The next
step is **not** `MASTER_EN`: first a bounded QA task must independently review
the candidate and all 124 visual rows, then the orchestrator must obtain a
reviewed Viral contract amendment for pages 1-5 if their modes are accepted.
Only after `reconstruction_ready` passes and Step 6 QA has zero open blockers
may a separate freeze/promotion decision be prepared.

## Engineering contributor receipt

- Scope/result: produced this Step 6 engineering packet only.
- Files read: applicable `D:\NRI\AGENTS.md`; goal governance; canonical
  plan/context; accepted ScenarioContract architecture, remediation, reviews,
  correction and QA receipts; `viral.json`; `NRI_OCR_LAYOUT_RULES.md`; nearest
  Innsmouth reconstruction/source-integrity scripts, focused tests,
  project status, accepted/production manifests, and block-manifest evidence;
  MinerU README/runner; active runtime dependency evidence.
- Only file changed: this packet.
- Verification: required worktree HEAD matched; accepted Step 5 evidence says
  Step 6 is unblocked; the full suite remains explicitly non-green with the
  known 15 missing-`kb_creator.pdf_raw` collection errors.
- Blocker: none to packet delivery. Runtime reconstruction may expose only the
  stop conditions above.
- Next action: orchestrator reviews this packet and dispatches the UI-visible
  `Viral Step 6A reconstruction candidate` task against the exact allowlist.
- Elapsed time: unavailable as an exact platform value.
- Token use: unavailable to this contributor; no precision invented.


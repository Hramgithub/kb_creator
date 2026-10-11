# Viral Step 6A generic reconstruction-builder engineering packet

- Goal / step: `20260830-kb-creator-next-scenario` / `6-source-reconstruction-step6a-reconstruction-builder`
- Contributor role / requested effort: engineering assistance, `gpt-5.6-terra` / `medium`
- Actual platform model / effort: `unavailable`; assignment state: `platform-unverified`
- Orchestrator policy owner: main chat `gpt-5.6-sol` / `medium`; scoped override: `none`
- Worktree / required branch / HEAD: `D:\NRI\.worktrees\kb-creator-viral` / `codex/kb-creator-viral` / `54607bd3b9362adbb0c4bca64e8751482797f380`
- Timestamp: `2026-08-31`, Europe/Moscow
- Result: `packet_ready`; this task ran no builder, MinerU, OCR, GPU/model, translation, cleanup, Git, or publication operation.

## Purpose, state, and non-negotiable boundary

Specify one separate generic builder which turns the already recovered raw MinerU
input into one complete **original Step 6A schema** candidate.  It is a
reconstruction/evidence task only.  It must return only
`candidate_needs_review`; it cannot return `reconstruction_ready`, `MASTER_EN`,
accepted, production, or publication.

This supersedes neither the original Step 6 packet nor the raw-engine recovery.
The recovery root is authoritative only as hash-bound raw engine input.  It is
not a reconstructed candidate, and the new candidate must not modify, reuse as
an output directory, or promote it.  The admitted external source and contract
remain read-only evidence.  Generated MinerU `*_origin.pdf` byte identity is
**revoked**: it is a PDFium-generated engine artifact, not a substitute source.
The admitted source byte/hash gate remains binding.

Before any implementation, a fresh independent `gpt-5.5` / `medium`
**process/architecture** review of this packet must accept with no open P0/P1.
That critic must not implement or materially redesign the builder.

## Exact inputs and immutable bindings

The executor verifies every identity before creating the new run root.  A
mismatch is a fail-closed stop, not a repair, rerun, or substitution.

| Binding | Required value |
|---|---|
| Admitted source | `D:\яндекс\Yandex.Disk\НРИ\1_Зов Ктулху\english\7th Edition Call of Cthulhu\Adventures\Call_of_Cthulhu_Viral.pdf`; `20,718,150` bytes; `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05` |
| Contract | `kb_creator/contracts/viral.json`, loaded through existing `scenario_contract` intake admission; title/id `Viral` / `viral`; 124 Letter pages `[612,792]`, rotation `0` |
| Original Step 6 packet | `terra_engineering_viral_source_reconstruction_packet_20260831.md`; `011CF87FFA0B0DACC85559DEF601A5FD9EED0755F86EB877C263CF2F2D8FABBC` |
| Origin-semantics receipt | `terra_engineering_viral_step6a_origin_semantics_delta_20260831.md`; `0894966630FA19022033AA3D93CE67B98C7B44244BADB022ED0EC2BAD08DDA2C` |
| Salvage critic accept | `gpt55_critic_viral_step6a_engine_output_salvage_review_20260831.md`; `2FE4EEA41760F0068A30B6A551E04F5B901F4DB6208B83E952C815905FE638E4` |
| Recovery executor receipt | `luna_executor_viral_step6a_engine_output_salvage_20260831.md`; `9FD0FBA8B1EADDBAB7AC1199BA2D01371896D9E18D49EC85C8369C08D5011C42` |
| Immutable engine predecessor | `working/viral/source_reconstruction/20260831_step6a_origin_copy_exception_retry`; 507 files / 71,193,544 bytes / manifest `81EA67826C139E501F1C841CBF17464FA54A409CCE32F1EAA40BB620EEA39079` |
| Recovery input root | `working/viral/source_reconstruction/20260831_step6a_engine_output_salvage_candidate`; `RECOVERY_MANIFEST.json` `41F00E41D04A19071FF0418068D7A1744C412F6EC6CDBEB7CFEE580B32B09169`; `RECOVERY_EVIDENCE.json` `F1F9F66AB3EA9C09196221CA82FDFEA888C94AAE024891057CA1A20FA53179BC` |

The recovery manifest must prove exactly 209 payload files: the five named
engine Markdown/JSON files and 204 JPEGs under
`engine/mineru_hybrid_high/Call_of_Cthulhu_Viral/hybrid_auto/`; 21,220,717
payload bytes; v1 `1,840` entries and indices `0..123`; v2/middle/model each
124 records; Markdown 387,142 characters and 112 image references with zero
missing targets.  The 92 unreferenced recovered images are retained raw engine
evidence, not silently discarded.

## New candidate root and closed write allowlist

The exact new root is initially absent and must remain a refuse-overwrite
target:

```text
kb_creator/working/viral/source_reconstruction/20260831_step6a_reconstruction_from_salvaged_engine_candidate/
```

The executor may write only the following four implementation/test paths, the
new root below, and its receipt.  No new reusable file is justified: the
existing generic seam already owns admission, deterministic JSON, CLI actions,
closed-schema checking, and its dedicated test surface; it must be generalized
away from the obsolete runtime/MinerU successor assumptions rather than forked.

1. `kb_creator/scripts/scenario_source_reconstruction.py` — replace the old
   run-specific MinerU launch/byte-identical-origin path with a generic,
   contract-driven recovered-input builder and closed verifier.  It must not
   contain a Viral-specific run id, source hash, old origin rule, or scenario
   output constant.
2. `kb_creator/scripts/reconstruct_scenario_source.py` — retain only a closed
   CLI.  Add an explicit `--recovery-root` argument for build/verify and reject
   all actions/paths not in this packet.
3. `kb_creator/tests/test_scenario_source_reconstruction.py` — add hermetic
   fixture tests for recovery admission, deterministic mapping, schemas,
   complete coverage and refusal cases; do not use the real PDF, MinerU, GPU,
   OCR, network, or untracked candidate as a test fixture.
4. `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/luna_executor_viral_step6a_reconstruction_builder_20260831.md` — immutable executor receipt.

All other files are read-only, including `scenario_contract.py`, `viral.json`,
plan/context/status, source, recovery/predecessor roots, accepted/production/
publication trees, old translations, and `translator/config/viral.package.json`.
No branch/ref/index/commit/push operation is authorized.

The candidate root has this closed topology (empty directories are permitted
only where recorded as `not_needed`; no cache, temp, `.pyc`, raw log, PDF,
symlink/reparse point, credentials, or extra top-level name is permitted):

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
engine/mineru_hybrid_high/Call_of_Cthulhu_Viral/hybrid_auto/{five recovered files,images/*.jpg}
renders/source/page-001.png .. page-124.png
renders/contact_sheets/*
crops/**
assets/source/**
assets/derived/**
ocr/**
```

`engine/` is copied only from the recovery root after every per-file hash is
checked against its manifest; it is never copied from the predecessor.  Renders,
embedded-object assets and deterministic crops are source-derived evidence;
derived assets and OCR are optional only when their required provenance rows
exist.  The builder must not extract/copy any source/origin/layout/span PDF.

## Deterministic builder design

1. Admit the source with an independent PDF observer, then
   `resolve_source_path()` using observed 124 pages, Letter media box and zero
   rotation.  Snapshot canonical contract bytes and source identity without an
   identity-bearing absolute path.
2. Admit the recovery root as a closed read-only payload.  Validate both
   recovery manifests and each of the 209 rows, no reparse points, all five
   named files, 204 JPEGs, page-index/record counts, 112 Markdown references,
   zero missing references, and 92 unreferenced images retained as
   `engine_evidence_unreferenced`.  Copy only this verified payload to the new
   candidate's `engine/` path and record source/recovery/output hashes.
3. Produce all 124 source page PNG renders at one recorded DPI and deterministic
   contact sheets.  For every source page, map MinerU's zero-based page index
   `i` to source/candidate page number `i + 1`; bind v1 content entries,
   v2/middle/model row(s), raw Markdown spans/image links, page render, and
   read-only PDF text/object observations in one `PAGE_PROVENANCE` row.
4. Produce each `pages/page-NNN.md` from ordered, source-anchored semantic
   blocks, then concatenate exactly those 124 files in numeric order to make
   `RECONSTRUCTED_EN.md`.  No generated prose may enter without a page/block
   evidence row.  Preserve `NRI_OCR_LAYOUT_RULES.md`: hierarchy, meaningful
   bold/italic/quotes, lists, real tables, cards/stat blocks, source-order
   mixed content anchors, visible source page markers, and valid Obsidian
   relative links.  Never invent a table, flatten an unverified formatting
   decision, redesign a page, or translate.
5. Build content rows with stable `pNNN-bNNN` ids, page/order, source strategy,
   bboxes/object refs, raw/rendered hashes, predecessor/successor relations,
   operations (exact expected/actual match counts), asset links, review state,
   and findings.  MinerU is candidate evidence, not wholesale authority:
   disagreements with source observation/render become findings/blockers.
6. Extract embedded images by source xref where coherent; otherwise make a
   deterministic source-render crop.  Every asset has page/region/xref,
   parent/derivation, byte/hash/MIME/dimensions, semantic role, one owner or
   explicit reviewed reuse owners, and visual-review state.  Every Markdown
   asset link resolves to exactly one inventory row.  Every inventoried asset
   is linked or marked evidence-only; retained raw engine JPEGs are all the
   latter unless a page/block link owns them.  Duplicate identical bytes may
   share one canonical asset only with all placement owners recorded; visually
   duplicate but byte-different files stay separate.  Unreferenced assets are
   never deleted automatically.
7. Build entity, navigation and handout inventories.  Handouts require exactly
   39 distinct ordinals `1..39`, unique source-visible labels, page/block/asset
   links and text/mixed/visual disposition.  Pages 104–110 require seven map
   closures; pages 111–123 require 13 investigator-sheet form/portrait/text
   closures; page 124 retains full back-cover visual and recoverable text.
8. Write pages 1–5 `CONTENT_MODE_REVIEW` proposals only.  Their contract values
   remain `unknown`; no proposal changes `viral.json` or a page to `closed`.
   Roles are fixed: 1 cover, 2 credits, 3–4 front matter, 5 contents, 6–68
   scenario, 69–103 player handouts, 104–110 keeper maps, 111–123 pregens,
   124 back cover.
9. `REFERENCE_ONLY_AUDIT` must state `historical_material_opened: false` and
   contain no rows.  Old EN/RU, translator config, accepted/production and
   publication artifacts must not be opened, executed, copied, compared or
   appear in lineage.  Their access is a stop condition.
10. Write deterministic UTF-8/LF, key-sorted JSON; make a second in-memory or
    disposable-root build from the same admitted fixtures and compare canonical
    nonvolatile outputs/hashes.  Timestamps are isolated in `COMMANDS` and
    excluded from deterministic candidate identities.  Write an exhaustive
    output inventory and candidate state only `candidate_needs_review`.

## Required schema/gates

`PAGE_PROVENANCE` has exactly pages 1..124, no gap/duplicate; `CONTENT`
contains no orphan block/relation; `ASSET`, `ENTITY`, `HANDOUT`, and
`NAVIGATION` references all resolve; `CONTENT_MODE_REVIEW` contains exactly
1..5; `REFERENCE_ONLY_AUDIT` is empty/unopened; and `COMMANDS` records only
admission, recovery validation, deterministic source rendering/extraction and
builder commands.  It must explicitly record that MinerU/OCR/model/GPU/network
execution was not invoked.

`BLOCKER_LEDGER` uses closed rows: defect class, earliest failing layer,
full-search scope, affected page/block/asset ids, owner, required action and
state.  Full-scope classes include 124-page reading order/formatting, glyph
corruption, asset ownership, handout cardinality, page 1–5 mode review,
navigation, visual review and reference-only access.  Any uncertainty is
`needs_review`/open, never silently repaired.

`RECONSTRUCTED_EN.qa.json` binds contract/source/recovery manifests/receipts,
implementation identities, output inventory, counts, deterministic-build
comparison and each gate.  Expected hard counts are 124 page files/renders and
39 handout rows.  It fails closed on any identity, count, hash, mapping,
reference, schema, output-path, duplicate-ownership, source-admission,
format-preservation or deterministic-comparison mismatch.  Open review
blockers and contract unknown modes are expected and force
`candidate_needs_review`, never a promotion.

## Commands, tests, and diagnostic boundary

All commands run from `D:\NRI\.worktrees\kb-creator-viral` with `python -B`
and no dependency installation.  Builder command shape after critic acceptance:

```powershell
python -B -m pytest kb_creator/tests/test_scenario_contract.py kb_creator/tests/test_scenario_source_reconstruction.py -q -p no:cacheprovider
python -B kb_creator/scripts/reconstruct_scenario_source.py preflight --contract kb_creator/contracts/viral.json --source "D:\яндекс\Yandex.Disk\НРИ\1_Зов Ктулху\english\7th Edition Call of Cthulhu\Adventures\Call_of_Cthulhu_Viral.pdf" --recovery-root kb_creator/working/viral/source_reconstruction/20260831_step6a_engine_output_salvage_candidate --run-root kb_creator/working/viral/source_reconstruction/20260831_step6a_reconstruction_from_salvaged_engine_candidate
python -B kb_creator/scripts/reconstruct_scenario_source.py build --contract kb_creator/contracts/viral.json --source "D:\яндекс\Yandex.Disk\НРИ\1_Зов Ктулху\english\7th Edition Call of Cthulhu\Adventures\Call_of_Cthulhu_Viral.pdf" --recovery-root kb_creator/working/viral/source_reconstruction/20260831_step6a_engine_output_salvage_candidate --run-root kb_creator/working/viral/source_reconstruction/20260831_step6a_reconstruction_from_salvaged_engine_candidate
python -B kb_creator/scripts/reconstruct_scenario_source.py verify --contract kb_creator/contracts/viral.json --source "D:\яндекс\Yandex.Disk\НРИ\1_Зов Ктулху\english\7th Edition Call of Cthulhu\Adventures\Call_of_Cthulhu_Viral.pdf" --recovery-root kb_creator/working/viral/source_reconstruction/20260831_step6a_engine_output_salvage_candidate --run-root kb_creator/working/viral/source_reconstruction/20260831_step6a_reconstruction_from_salvaged_engine_candidate
```

Focused test expectations are new/updated hermetic tests plus the existing
ScenarioContract suite.  A repository-wide collection may still report exactly
the known 15 missing-`kb_creator.pdf_raw` collection errors.  Record that as a
diagnostic boundary only: no claim of whole-repository green, no repair to
unrelated tests, and any count other than 15 or any new failure class blocks the
candidate.

Pre/post mutation audits must prove exact branch/HEAD, unchanged contract,
source, recovery root and predecessor manifest; no writes outside the four
allowlisted implementation/receipt paths and the exact new root.  Audit the
candidate topology/inventory and `git status --short`; pre-existing dirt is
reported, not changed.

## Stop conditions

Stop with an immutable blocked receipt on: missing critic acceptance; nonexact
branch/HEAD; existing new root; any hash/count/page/index/reference mismatch;
PDF/source admission drift; any MinerU/OCR/GPU/model/network launch; origin or
source PDF copy; raw cache/runtime material; historical translation/config
access; unallowlisted write; reparse point; uncertain semantic/format/asset
mapping; non-39 handout closure; absent page/render; schema/determinism failure;
candidate state other than `candidate_needs_review`; or any Git mutation.

Do not clean any root, retry MinerU, repair installation, amend contract,
promote output, stage/commit/push, or continue after a stop.  Preserve the
predecessor and recovery roots byte-intact.

## Required downstream packets and receipts

After this packet, the orchestrator dispatches in this order:

1. Fresh critic process/architecture review receipt:
   `handoffs/gpt55_critic_viral_step6a_reconstruction_builder_packet_review_20260831.md`.
   Required decision: `accept`, no P0/P1; otherwise no executor.
2. UI executor receipt named in the allowlist above.  It reports result,
   changed files, pre/post manifests, exact command/test outcomes, blocker,
   run-root inventory/hash and detached SHA-256; it must not self-accept.
3. Separate bounded QA packet/receipt:
   `handoffs/luna_qa_viral_step6a_reconstruction_builder_20260831.md`.
   QA owns no implementation and may write only that receipt plus a disposable
   external-to-candidate visual QA probe.  It independently verifies all 124
   source/page-render/page-Markdown correspondences, contact sheets, 39
   handouts, seven maps, 13 pregens, page 124, page 1–5 unknown-mode evidence,
   asset/reference closure, recovery bindings, deterministic verifier and the
   15-error diagnostic boundary.  It returns QA evidence only.
4. Fresh independent implementation/process critic receipt:
   `handoffs/gpt55_critic_viral_step6a_reconstruction_builder_review_20260831.md`.
   It is required before any Step 6 acceptance; candidate mutation invalidates
   it.  No `MASTER_EN` dispatch follows without explicit orchestrator/user gate.

## Exact next UI executor prompt

> Work only in `D:\NRI\.worktrees\kb-creator-viral` on branch/HEAD `codex/kb-creator-viral` / `54607bd3b9362adbb0c4bca64e8751482797f380`. Read the accepted reconstruction-builder packet and its fresh gpt-5.5 process/architecture accept receipt first. Implement only `kb_creator/scripts/scenario_source_reconstruction.py`, `kb_creator/scripts/reconstruct_scenario_source.py`, and `kb_creator/tests/test_scenario_source_reconstruction.py`; create only the initially absent run root `kb_creator/working/viral/source_reconstruction/20260831_step6a_reconstruction_from_salvaged_engine_candidate` and receipt `handoffs/luna_executor_viral_step6a_reconstruction_builder_20260831.md`. Consume only the hash-bound recovery root Markdown, four JSON files and 204 images, plus read-only admitted source/contract evidence. Produce the full original Step 6A schema, 124 pages/renders, 39 handout inventory rows, source/page/block/asset/entity/navigation/mode/reference/blocker/command evidence, deterministic QA and only `candidate_needs_review`. Do not run MinerU, OCR, GPU/models, network, translation, cleanup, source/origin/layout PDF copy, access old translations/config, alter contract/plan/context/accepted/production/publication, stage/commit/push, or write outside the allowlist. Stop fail-closed and write the receipt if any binding or completeness gate fails.

## Files changed, blockers, and detached SHA-256

Changed by this engineering task: only this packet.  Blockers: fresh independent
critic acceptance is pending; no implementation is authorized until it exists.
Elapsed time and token use: unavailable.  Compute this packet's detached
SHA-256 after final write; do not edit it to embed the hash.

# Viral Step 6A reconstruction-builder QA remediation packet

- Goal / step: `20260830-kb-creator-next-scenario` / `6-source-reconstruction-step6a-reconstruction-builder-qa-remediation`
- Contributor role / requested effort: engineering assistance, `gpt-5.6-terra` / `medium`
- Actual platform model / effort: `unavailable`; assignment state: `platform-unverified`
- Orchestrator policy owner: main chat `gpt-5.6-sol` / `medium`; scoped override: `none`
- Worktree / branch / HEAD: `D:\NRI\.worktrees\kb-creator-viral` / `codex/kb-creator-viral` / `54607bd3b9362adbb0c4bca64e8751482797f380`
- Result: `packet_ready`; this task did not run a build, MinerU, OCR, GPU/model, network, Git, or candidate mutation.

## Purpose and acceptance boundary

This is the minimal closed remediation for the failed bounded QA receipt
`luna_qa_viral_step6a_reconstruction_builder_20260831.md`, SHA-256
`4FDE96841683DA0516E80439EC11476BC27BE9366E885673379AC8964550C649`:

1. deterministic contact sheets proving review coverage for all 124 source renders;
2. truthful, non-empty asset provenance and navigation inventories; and
3. corrected stale executor-command documentation through a successor receipt.

The candidate remains only `candidate_needs_review`. This neither accepts,
promotes, rebuilds, translates, publishes, nor claims reconstruction completeness.
The accepted builder packet `F5B5684591586BFE7C22D0F73C67B4B3A849A206495FFEFF8261E3CE2E97138C`
and critic P2 distinction stay binding: ordinary source-derived visual or semantic
uncertainty is a `needs_review`/open row; stop only when a required identity,
count, path, anchor, ownership decision, or schema field would need invention or
false completeness.

The immutable executor receipt
`luna_executor_viral_step6a_reconstruction_builder_20260831.md`, SHA-256
`5E5A059BDD4CA9A431AAAE84079A66CE1BFD037215BE4AA9B505298162D4CFB0`, is
**left untouched**. Governance requires correction by a new successor executor
receipt, not alteration of immutable history. Its stale `--source-pdf` /
`--candidate-root` text is superseded only by that successor, which uses
`--source` / `--run-root`.

## Immutable inputs and baseline admission

Before any write, verify these bindings or stop:

| Binding | Required value |
|---|---|
| admitted source | Viral PDF; `20,718,150` bytes; `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05`; 124 Letter pages `[612,792]`, rotation `0` |
| contract snapshot | `kb_creator/contracts/viral.json`; candidate `SCENARIO_CONTRACT.json` SHA-256 `C2EF2DD143E304F59C8973E8DB82CF83B094BC35DDA37BB2299686E1FE6DA194` |
| recovery root | `.../20260831_step6a_engine_output_salvage_candidate`; manifest `41F00E41D04A19071FF0418068D7A1744C412F6EC6CDBEB7CFEE580B32B09169`; evidence `F1F9F66AB3EA9C09196221CA82FDFEA888C94AAE024891057CA1A20FA53179BC` |
| recovery facts | 209 payload files / 204 JPEGs / 112 Markdown image references / zero missing targets / 92 retained unreferenced engine images / v1 indices 0..123 |
| candidate baseline | exact existing root `.../20260831_step6a_reconstruction_from_salvaged_engine_candidate`; 471 files; canonical manifest SHA-256 `6E0872BA47E74356E590D7CFABE192ED92DD832D1B11CAA1BDBBE120AFFC4E07` |
| packets/receipts | accepted builder `F5B568...`; critic `1F496F...`; executor `5E5A...`; failed QA `4FDE...` |

The canonical candidate manifest is SHA-256 over UTF-8 bytes of sorted LF records
`relative-posix-path<TAB>byte-count<TAB>SHA256(file)\n`. Record its pre/post
values and exact changed-path set. Prove every immutable path retained its pre
hash. The copied engine payload, `pages/`, `renders/source/`,
`RECONSTRUCTED_EN.md`, and `SCENARIO_CONTRACT.json` are immutable. Any
recovery-hash serialization discrepancy in mutable candidate metadata is corrected
to admitted `41F00E...`, never treated as authority.

## Exact write allowlist

The executor may write only:

1. `kb_creator/scripts/scenario_source_reconstruction.py`
2. `kb_creator/scripts/reconstruct_scenario_source.py`
3. `kb_creator/tests/test_scenario_source_reconstruction.py`
4. candidate `SOURCE_IDENTITY.json` and `RECONSTRUCTED_EN.qa.json`
5. candidate `evidence/{ASSET_PROVENANCE,NAVIGATION_INVENTORY,PAGE_PROVENANCE,CONTENT_PROVENANCE,ENTITY_INVENTORY,HANDOUT_INVENTORY,BLOCKER_LEDGER,COMMANDS}.json`
6. candidate `renders/contact_sheets/sheet-001.png` through `sheet-031.png`, no other contact-sheet name
7. `handoffs/luna_executor_viral_step6a_reconstruction_builder_qa_remediation_20260831.md`.

Everything else is read-only: plan/context/status, contract, source PDF,
recovery/predecessor roots, all page Markdown, master Markdown, source renders,
engine payload, accepted/production/publication outputs, historical EN/RU and
`translator/config/viral.package.json`, Git index/refs, and cache/runtime. No
new root, full rebuild, cleanup, stage/commit/push, or source/origin PDF copy.

## Closed in-place implementation

Add a closed `remediate` CLI action using existing exact `--contract`,
`--source`, `--recovery-root`, and `--run-root` flags. It admits only the
existing exact candidate after baseline and immutable bindings pass; it refuses
an absent/other root, unexpected changed file, reparse point, stale prerequisite,
or overwrite outside the allowlist. `build` remains refuse-overwrite and is not
invoked.

Regenerate mutable rows deterministically from copied engine payload, candidate
page/block evidence, source-render metadata, contract roles, and admitted recovery
manifests. Do not access old translations/configuration or infer final semantics.

### Contact sheets and visual evidence

Produce exactly 31 deterministic PNG sheets, fixed 2x2 grids in numeric order:
sheets 001..031 cover `1-4`, `5-8`, ..., `121-124`. Use fixed cells,
neutral padding, page-number labels and encoder options. Do not re-render the PDF
or substitute thumbnails. `COMMANDS.json` and QA bind every sheet to its four
render paths/hashes and record 124/124 coverage with no duplicate/missing page.

QA reviews all 31 sheets. It also reviews original-resolution renders for pages
`1-5`, `6,19,32,45,58,68`, every handout page `69-103`, maps `104-110`,
pregens `111-123`, and page `124`. The receipt records exact viewed sets and
per-risk-class outcomes. Sheets never replace detailed visual review; unresolved
fidelity, reading order, labels, placement, and modes remain `needs_review`.

### Truthful asset and navigation closure

`ASSET_PROVENANCE.json` must contain exactly 204 stable, non-empty rows, one per
copied engine JPEG: `asset_id`, engine relative path, bytes, SHA-256, MIME,
`engine_evidence` source, recovery-manifest binding, Markdown reference count
and locations, ownership, closure state, findings. Exactly 112 Markdown references
resolve to rows by page/block/source-link anchors; exactly 92 rows are
`engine_evidence_unreferenced` with no placement owner. Do not manufacture PDF
xrefs, crops, final semantic roles, or ownership: unresolved placement/meaning is
`needs_review`, raw-evidence retention is truthful.

`NAVIGATION_INVENTORY.json` must contain at least 124 page-anchor rows, exactly
one stable `page-NNN` anchor per page: source number, zero-based engine index,
page Markdown, source-render path/hash, prev/next anchor when applicable,
contract role, and `needs_review`. Through those anchors it must cover all 39
handouts (69-103), seven maps (104-110), 13 pregens (111-123), and page 124
back cover. Add a source-visible contents/handout label only if exact recovered or
source evidence proves it. Never fabricate a TOC target, investigator name, final
handout label, or final navigation semantics. Pages 1-5 retain `unknown` modes
and five explicit review anchors.

Regenerated page/content/entity/handout/blocker rows cross-link only observed
facts: page/block/asset/anchor ids, partition, hashes, and `needs_review`.
The blocker ledger retains open review scope for all 124 pages, 1-5 modes, 39
handouts, seven maps, 13 pregens, page 124, asset placement/ownership, and
navigation. Required counts: pages/renders 124; contact sheets 31; handouts 39;
engine payload 209; images/assets 204; referenced/unreferenced images 112/92.

## Tests, commands, and proof

Add focused hermetic tests only: baseline admission/refusal; exact allowed delta;
31-sheet mapping/missing/duplicate refusal; 204/112/92 conservation and references;
124 navigation anchors and role partitions; 1-5 preservation; source/recovery
bindings; stale CLI flag rejection and correct flag acceptance; and verify refusal
for wrong mutable schema/count/hash. Fixtures must not use the real PDF, candidate,
MinerU, GPU, OCR, network, or cache.

After fresh critic acceptance, run only:

```powershell
python -B -m pytest kb_creator/tests/test_scenario_contract.py kb_creator/tests/test_scenario_source_reconstruction.py -q -p no:cacheprovider
python -B kb_creator/scripts/reconstruct_scenario_source.py preflight --contract kb_creator/contracts/viral.json --source "D:\яндекс\Yandex.Disk\НРИ\1_Зов Ктулху\english\7th Edition Call of Cthulhu\Adventures\Call_of_Cthulhu_Viral.pdf" --recovery-root kb_creator/working/viral/source_reconstruction/20260831_step6a_engine_output_salvage_candidate --run-root kb_creator/working/viral/source_reconstruction/20260831_step6a_reconstruction_from_salvaged_engine_candidate
python -B kb_creator/scripts/reconstruct_scenario_source.py remediate --contract kb_creator/contracts/viral.json --source "D:\яндекс\Yandex.Disk\НРИ\1_Зов Ктулху\english\7th Edition Call of Cthulhu\Adventures\Call_of_Cthulhu_Viral.pdf" --recovery-root kb_creator/working/viral/source_reconstruction/20260831_step6a_engine_output_salvage_candidate --run-root kb_creator/working/viral/source_reconstruction/20260831_step6a_reconstruction_from_salvaged_engine_candidate
python -B kb_creator/scripts/reconstruct_scenario_source.py verify --contract kb_creator/contracts/viral.json --source "D:\яндекс\Yandex.Disk\НРИ\1_Зов Ктулху\english\7th Edition Call of Cthulhu\Adventures\Call_of_Cthulhu_Viral.pdf" --recovery-root kb_creator/working/viral/source_reconstruction/20260831_step6a_engine_output_salvage_candidate --run-root kb_creator/working/viral/source_reconstruction/20260831_step6a_reconstruction_from_salvaged_engine_candidate
```

A repeat verify must be canonically identical and prove post-manifest, immutable
hashes, allowed delta only, 31/124 coverage, 204/112/92 arithmetic, 124 anchors,
39/7/13/1 closure, five unknown-mode rows, and `candidate_needs_review`. The
known 15 missing-`kb_creator.pdf_raw` collection errors are diagnostic only; no
whole-repository-green claim and any different/new class blocks the candidate.

## Stops, receipts, and review order

Stop and write a blocked successor receipt on any binding, baseline, path,
manifest, schema, count, anchor, asset-conservation, determinism, forbidden-access,
or Git-mutation failure; missing sheet; invented final semantic; or candidate state
other than `candidate_needs_review`. Do not solve a stop by rebuilding, rerunning
MinerU, changing contract, or deleting/recreating the candidate.

1. Fresh independent gpt-5.5 implementation/process review:
   `handoffs/gpt55_critic_viral_step6a_reconstruction_builder_qa_remediation_packet_review_20260831.md`; accept/no P0/P1 before execution.
2. Executor successor receipt in the allowlist, recording untouched predecessor,
   pre/post manifests, changed hashes, outcomes, counts and mutation audit.
3. Separate QA retry receipt:
   `handoffs/luna_qa_viral_step6a_reconstruction_builder_qa_retry_20260831.md`.
   QA writes only this receipt, implements nothing, runs corrected
   `--source`/`--run-root` verify, reviews all sheets and listed original-risk
   renders, and proves coverage/closure.
4. Fresh independent gpt-5.5 implementation/process review:
   `handoffs/gpt55_critic_viral_step6a_reconstruction_builder_qa_remediation_review_20260831.md`.
   No Step 6 acceptance or MASTER_EN dispatch precedes it; a later mutation
   invalidates it.

## Ready-to-paste executor prompt

> Work only in `D:\NRI\.worktrees\kb-creator-viral`, branch/HEAD `codex/kb-creator-viral` / `54607bd3b9362adbb0c4bca64e8751482797f380`. Read the accepted builder packet, critic receipt, failed QA receipt, and accepted remediation critic receipt. Mutate only the three generic source/test paths, exact generated candidate paths, and successor receipt named in this packet. Do not create a root or run build/MinerU/OCR/GPU/model/network. Add only closed in-place `remediate`, bound to 471-file baseline manifest `6E0872BA47E74356E590D7CFABE192ED92DD832D1B11CAA1BDBBE120AFFC4E07`. Preserve pages, source renders, engine payload, contract, source, recovery root, and governance history byte-for-byte. Produce exactly 31 2x2 contact sheets for pages 1-124; truthful 204-row asset provenance with 112 referenced + 92 retained unreferenced rows; and 124 page-anchor navigation with 39/7/13/page-124 closures and 1-5 unknown review. Use `--source` and `--run-root`, not stale flags. Run only focused tests, preflight, remediate, and repeated verify. Keep only `candidate_needs_review`, write the successor receipt, and stop fail-closed on mismatch, invented semantic, or forbidden side effect.

Changed by this engineering task: only this packet. Blocker: fresh independent
critic acceptance before execution. Token use: unavailable. Compute detached
SHA-256 after final write; do not edit this immutable packet to embed it.


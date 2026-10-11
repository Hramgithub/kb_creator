# Luna QA receipt — Viral Step 6A three-view MinerU sample

- Goal id: `20260830-kb-creator-next-scenario`
- Step id: `viral-step6a-mineru-three-view-sample-execution`
- Role: execution-only QA (`gpt-5.6-luna`, high)
- Orchestrator policy owner: main-chat `gpt-5.6-sol` / medium
- Assignment state: `matched` (platform runtime model/effort not independently verifiable)
- Scoped override: `none`
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`
- Timestamp: `2026-09-01T13:41:23+03:00` (evidence collection timestamp, Europe/Moscow)
- Elapsed time: approximately 9 minutes; exact platform elapsed time unavailable
- Token use: unavailable to this contributor
- Result: `BLOCKED`

## Scope

Executed the authorized 8-page three-view sample from the Terra correction
receipt. Writes observed were confined to the fresh sample root, plus this
receipt. No code, tests, source, predecessor, plan/context, governance/config,
production, Git, verifier 371/119/490, commit or push work was performed.

Fresh root:

`kb_creator/working/viral/source_reconstruction/20260901_step6a_mineru_three_view_sample`

## Bound identities

| Item | SHA-256 / identity |
|---|---|
| source `Call_of_Cthulhu_Viral.pdf` (20,718,150 bytes) | `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05` |
| vector sample (5,338,547 bytes) | `CDF84E4021B5BA23D13747922F3237D837325396CB3F591CE46CC22039D241AA` |
| raster sample (44,367,584 bytes) | `ACBB6A9CA3F75B033018EABB22DCB00B8A6E02E8B8BEDD9F42A6C9F5B05BAB72` |
| mapping manifest (1,500 bytes) | `2EEC2D820CAE6625CADEAB1B1B08EEA348450C260DA444A24691B675CD6C5AD2` |
| Terra correction receipt | `D7B498D8023A977DE302F5CC6A039FC1E32DE82EFA8E5C6EBF7B5F62C1D8323A` |
| preparer | `67873A607EA231719338E4984E598946511A4C47C263B5AB3EB8E864CBD65AB0` |
| comparator | `78FDB0908011E91DFB9A95FEE28A575EBDCE68146900AD265BC215A6AC59C976` |
| MinerU wrapper | `262E1CA20B42EF4B87C30A90CC56589CEE6DFC759FF762A5FAB430EEAEF07269` |
| focused tests | `C6C60BB6DC777C412422B8757D239CC3D2034B97DDD43E60964D9B6E03672E56` |

Manifest mapping was the required ordered sequence `5, 12, 53, 69, 104,
109, 115, 123`; manifest records 200 DPI Letter pages and
`raster_has_text_layer: false`.

## Commands and evidence

| Command | Exit | Evidence |
|---|---:|---|
| required PDF marker (`mark_artifact_operation_started.mjs`, create, expected 2, pdf) | 0 | exact packet command; no stdout |
| exact Terra preparer command | 0 | `evidence/prepare.console.txt`, 499 bytes, SHA-256 `5ADB4CAEE03CB6870840837C2035D607D2CBB18CF7D82800C9E50D7C1150596A` |
| original vector `hybrid_high` | 0 | `evidence/original_hybrid.console.txt`, 4,336 bytes, SHA-256 `702D47A3705713091F04CDDB93721AD5AF55E5F2681DEE94B8764E6115B88089`; MinerU `Processed 8/8 pages` |
| original vector `pipeline_ocr` | 0 | `evidence/original_pipeline_ocr.console.txt`, 5,395 bytes, SHA-256 `7211675974014EBF5DC68495BCE8B681B2B03F9F6DDB1703C01A89EB75AC8498`; MinerU `Processed 8/8 pages` |
| raster `hybrid_high` | 0 | `evidence/raster_hybrid.console.txt`, 3,935 bytes, SHA-256 `1F7240421A2DCE44FB1A46CC4320008677E6E6E132A9787C097E6`; MinerU `Processed 8/8 pages` |
| comparator | 0 | `evidence/compare.console.txt`, 213 bytes, SHA-256 `210DE188C96348977031E43B65A0951BF27A08D8B14D8FC6F5BF79C5D5486773`; status `pass`, failures `[]` |
| full focused tests | 0 | `evidence/terra_focused_tests.console.txt`, 101 bytes, SHA-256 `7A6F7284F144C1590976A9BE5060B5AAB6B60A1F7A841FA6BDEB63098E1EED32`; `10 passed in 1.29s` |
| sample inventory and console hashes | 0 | `evidence/sample_inventory.tsv` and `evidence/console_hashes.tsv`; 103 files and 6 pre-render console captures inventoried |
| layout locate/page-count/render command | **1** | command output confirmed 3 layout PDFs, each `Pages: 8`, and 8 PNGs per view (24 total), then exact PowerShell error below |

Runtime identities recorded by the preparer manifest: Python `3.13.14`,
pypdf `6.14.0`, PyMuPDF `1.27.2.3`, reportlab `5.0.0`. MinerU logs identify
the three requested profiles and CUDA/lmdeploy execution.

## Stop evidence and visual result

The render command completed its three `pdftoppm` invocations and printed:

```text
rendered view=original_hybrid; pdf=viral_sample_vector_layout.pdf; pages=8; pngs=8
rendered view=original_pipeline_ocr; pdf=viral_sample_vector_layout.pdf; pages=8; pngs=8
rendered view=raster_hybrid; pdf=viral_sample_raster_layout.pdf; pages=8; pngs=8
```

Immediately afterward it failed with:

```text
*>&1:
The term '*>&1' is not recognized as a name of a cmdlet, function, script file, or executable program.
```

The failing trailing redirection also meant `Tee-Object` was not invoked and
`evidence/render.console.txt` was not created. The exact failure is preserved
here; the command was not repaired or rerun. Under the packet's first-failure
rule, visual inspection stopped at this boundary.

| View | Render/page evidence | Visual inspection |
|---|---|---|
| original hybrid | layout PDF found, 8 pages; 8 PNGs produced | pages 1–8: `NOT INSPECTED — stopped on render command exit 1` |
| original pipeline/OCR | layout PDF found, 8 pages; 8 PNGs produced | pages 1–8: `NOT INSPECTED — stopped on render command exit 1` |
| raster hybrid | layout PDF found, 8 pages; 8 PNGs produced | pages 1–8: `NOT INSPECTED — stopped on render command exit 1` |

Required 24-page visual QA therefore remains unverified. This is a bounded
execution failure, not an engineering interpretation or repair.

## Files checked and artifact counts

- source: 1 immutable PDF, identity above;
- inputs: 2 PDFs plus 1 manifest;
- MinerU runs: `original_hybrid` 43 files / 7,915,035 bytes,
  `original_pipeline_ocr` 18 files / 10,872,961 bytes,
  `raster_hybrid` 31 files / 90,579,577 bytes;
- required structured artifacts were present in all views; hybrid views had
  layout/origin PDF, Markdown and JSON metadata, and pipeline additionally had
  span PDF;
- comparator report: `comparison/comparison.json`, status `pass`, no failures;
- rendered overlays: 24 PNGs physically produced (8 per view), not visually
  inspected due the mandatory stop boundary;
- predecessor roots and all forbidden paths were left untouched.

## Blocker and next action

Blocker: the frozen render/evidence command itself exited `1` after rendering
because its trailing `*>&1` token was interpreted as a command and prevented
`Tee-Object` from creating the raw render capture. This violates the execution
packet's successful-command/raw-console requirement. No profile was restarted
and no repair was attempted.

Next action: orchestrator/Terra must review this exact blocked evidence and,
if desired, issue a fresh bounded packet with a corrected render/evidence
command. Luna does not rerun or repair this completed execution.

This receipt is a single-write, detached immutable handoff artifact; compute
its SHA-256 only after the final write.

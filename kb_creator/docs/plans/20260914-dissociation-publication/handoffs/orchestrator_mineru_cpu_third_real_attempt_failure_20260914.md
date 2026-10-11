# Orchestrator receipt: MinerU CPU third real attempt failure

Date: 2026-09-14

## Scope

- Run id: `20260914-cpu-first-03`
- Run root: `kb_creator/working/dissociation/reconstruction/20260914-cpu-first-03`
- Execution boundary: current station only; CPU concurrency `1`; no network,
  remote host, API, or GPU fallback.
- Source PDF remained immutable.

## Result

The Windows Job Object remediation worked in the real pipeline. All three
required MinerU CPU views completed without manual process termination. Both
optional CUDA-backed views were sealed as provider-local skips. Stage 03 built
the dynamic comparison successfully.

Stage 04 then failed closed in the generic visual merge builder before a review
bundle was sealed. The three rendered view PDFs do not have identical pixel
dimensions, and `build_triptychs` raised `ValueError: rendered view dimensions
differ`. This is a visual-normalization contract gap, not a MinerU execution or
process-tree failure.

The run is immutable, non-resumable, and non-promotable. It has no review queue,
decision set, fidelity audit, reconstruction candidate, or acceptance claim.

## Bound evidence

- `run.json`: `28166` bytes, SHA-256
  `F3A2529CD6160D04BB607EC46078C002DD01CF5A65413F18B3C5006F981B8337`
- Stage 01 receipt: `6018` bytes, SHA-256
  `D23CCF00D1AD0366E8E5840C046CD78E8F9FA859E4F6E0E09D5BEEAB52473642`
- Stage 02 receipt: `23533` bytes, SHA-256
  `0D7057F343AB8EC358B13754FC94C15168953CF7A94D9ED45DD86906F692EEED`
- view set: `3762` bytes, SHA-256
  `71379395C4F63CCC0A64819D4C8121A949E819AB008B80A6FADB2C46C51828B6`
- Stage 03 receipt: `5214` bytes, SHA-256
  `3F5B7993E4BD2A0D0EDB449CA39EF5A774A3E8E770A52F2D4B7B7AB3A1671804`
- comparison: `449255` bytes, SHA-256
  `9F54AE7CE9504C1A85B5B67BB9DC5D0D54C345726D6BA912CDD02F2BF37D034B`
- sealed Stage 04 failure: `4780` bytes, SHA-256
  `E746DA953F3CC35BC3FC899438D5DFBB6A022B7C0E850FFF23D983043705D33F`

View inventories including each `view.json`:

- `original_pipeline_txt`: `10` files, `8326476` bytes;
- `original_pipeline_ocr`: `10` files, `8347639` bytes;
- `raster_pipeline_ocr`: `11` files, `99661070` bytes;
- `original_hybrid_high`: one skip receipt, `1701` bytes;
- `original_vlm`: one skip receipt, `1670` bytes.

## Gate

Do not resume or rewrite this run. A fresh run id may be created only after a
scenario-neutral rendered-canvas normalization contract is specified,
implemented, tested, and independently closed. Per-scenario image resizing,
cropping, padding, or manual triptych assembly is forbidden.

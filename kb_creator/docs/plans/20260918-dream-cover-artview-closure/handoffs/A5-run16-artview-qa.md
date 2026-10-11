# A5 run-16 ArtView QA receipt

- Scope: bounded verification of `publication/20260918-publication-16/outputs/30-artview-bundle`, its Stage 30 manifest, and accepted MASTER_EN/MASTER_RU and asset-manifest artifacts for this run. No candidate/code changes; no release decision.
- Result: candidate schema is `kb_creator.scenario_artview_candidate.v4`; 20 review rows; Stage 30 manifest records exit code 0 and state `succeeded`; both ArtView QA records report `pass`. The cover row/placement is `source-cover-page-001`, derived from a clean full-page render. Visual inspection shows the complete cover composition (photo, title, byline, and logo) without an evident crop or corruption.
- Placement counts: 20 review rows = 1 composite cover + 18 PDF-backed placements + 1 MASTER-only page-20 handout. The 18 ordinary PDF placements are on pages 4, 5, 6, 7 (two), 8, 9, 11, 13, 14, 15, 17, and 21–26. No page-18 row, raw object, or statblock crop appears in the candidate inventory.
- Object-count evidence: the sealed `source_visual_inventory.json` ledger contains 25 raw records total = 22 non-mask image components (4 compose the page-1 cover + 18 ordinary PDF placements) + 3 technical PDF soft masks. QA reports raw-object disposition closure. The requested counts reconcile.
- Binary integrity: all 58 files in `candidate_files.inventory.json` exist and match recorded byte counts and SHA-256 values. All 38 unique current/alternative binaries referenced by rows resolve and match their recorded sizes and hashes (0 missing, 0 mismatches).
- Master identity: accepted MASTER_EN is 75,650 bytes, SHA-256 `C3B4F13E3E43B2422704F1A7BCF61A5CF1762191B474FAAE5C4C4243289367AA`; accepted MASTER_RU is 122,946 bytes, SHA-256 `904133D5057172C404D28F3BCF2A5E4C578304A59382512D1B31FC56AE0FDAB2`. Current files match their acceptance receipts exactly. The accepted MASTER_RU asset manifest records 19 assets; its assets are represented in the embedded authority snapshot.
- Files checked: `evidence/stages/30-artview-bundle.manifest.json`; `outputs/30-artview-bundle/artifacts/{candidate_manifest.json,candidate_files.inventory.json,source_visual_inventory.json,qa.json,assets/current/pdf-page-001-cover.png}`; `outputs/30-artview-bundle/evidence/artview.qa.json`; `acceptance/{master_en.acceptance.json,master_ru.acceptance.json}`; `outputs/{10-master-en-candidate/artifacts/MASTER_EN.md,21-master-ru-candidate/artifacts/MASTER_RU.md,21-master-ru-candidate/artifacts/ASSET_MANIFEST.json}`.
- Verification/evidence: manifest fields and JSON counts inspected; all inventory file paths, sizes, and SHA-256 digests checked; accepted master hashes recalculated; cover inspected visually. Stage 30 recorded completion at `2026-09-18T12:42:03.711465Z`.
- Blockers: none within the assigned A5 verification scope. This receipt does not decide acceptance or release.
- Next action: forward the evidence to the independent release reviewer per plan A6; user acceptance of the exact HTML remains the later A7 gate.
- Elapsed time: approximately 5 minutes.
- Token use: unavailable from this bounded QA execution.
- Timestamp: `2026-09-18 12:45 UTC`.
- Orchestrator policy owner: `gpt-5.6-sol`, medium (per assigned plan).
- Assignment state: A5 bounded QA complete; orchestrator retains ownership of integration, plan/status, and next-step decisions.
- Scoped override: A5 only—read and verify the specified run-16 bundle/authority artifacts and write this receipt; no implementation, candidate edits, terminology resolution, or release decision.

# N368 — latest deliverables inventory

- Goal / step: `20260920-night-three-books` / `N368-latest-deliverables`.
- Role: bounded QA, policy `gpt-6-luna` / medium; actual runtime unavailable.
- Orchestrator policy owner: main `/root`, `gpt-6-sol` / medium.
- Assignment state: `platform-unverified`; scoped override: none.
- Timestamp: 2026-09-28 20:12:43 UTC. Elapsed: approximately 8 minutes (exact start instant not captured). Token use: unavailable.
- Scope: read-only local inventory; no rebuild, processing, Git operation, source mutation, or canonical-state edit.

## Result

All six latest DOCX identities were taken from `REVIEW_INDEX.json`; no acceptance or release state was inferred. Exact paths, included formats, asset selection, caveats, and exclusions are recorded in the companion JSON receipt. Copy only the HTML-referenced local assets listed there; keep screenshot/render PNGs, older candidates, source/OCR PDFs, duplicated package payloads, and recovery trees out of the latest-only export.

| Book | Current DOCX | HTML | DOCX-export PDF | Referenced assets | Caveat |
| --- | --- | --- | --- | --- | --- |
| Cursed Idol | review-02 | review-02 `artifacts/docx/internal.html` | Missing | 74 | Do not substitute source PDF. |
| Kremlin | review-02 continuation package | continuation `package/internal.html` | Missing | 14 | Exclude parallel package and OCR/source PDFs. |
| Leningrad | review-01 | `docx-package/internal.html` | `qa/render-n66-v02/document.pdf` | 29 unique (32 refs) | Exclude 65 page PNGs. |
| Fear | annotated V19 | V19 `internal.html` | V19 `preview/document.pdf` | 63 | Working artifact; final source/language binding remains pending. |
| Number 7 | human-reviewed DOCX | Missing current HTML | DOCX-derived preview PDF | Embedded DOCX media | Older candidate/production HTML is stale and excluded; visual review pending. |
| Dissociation | package73 revision | latest root `Dissociation_RU.html` | latest root `Dissociation_RU.pdf` | 2 | Release state remains not reviewed. |

## Evidence and limits

- HTML asset references were counted and deduplicated. Cursed Idol and Kremlin counts match their package `ASSET_MANIFEST.json` files. Leningrad's available export PDF render inventory says `source_kind=docx_candidate`.
- Dissociation `REVISION_MANIFEST.json` binds its current DOCX, HTML, and PDF. Number 7's current submission contains no HTML; earlier candidate and production HTML paths are explicitly recorded as stale.
- Missing Cursed Idol and Kremlin DOCX-export PDFs are recorded. This inventory does not authorize or perform generation.
- `kb_creator/PROJECT_STATUS.md`, the assigned goal plan/context, task packet, and review index were read. No canonical state was changed.

## Next action

Main copies the finite selections from the JSON into the new latest-only export directory. Scripts and the requested plan/context/status/debt files remain under main's integration scope.

## Files

- Checked: task packet, goal plan/context, `kb_creator/PROJECT_STATUS.md`, `REVIEW_INDEX.json`, and the six artifact locations listed in the companion JSON.
- Written: this receipt and `N368-latest-deliverables-v01.json` only.
- Blockers: Cursed Idol export PDF, Kremlin export PDF, and current Number 7 HTML unavailable.

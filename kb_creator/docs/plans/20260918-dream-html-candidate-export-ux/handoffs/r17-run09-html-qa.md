# R17 — Run09 Stage 40 HTML bounded QA

- Result: **PASS** — run09 Stage 40 is structurally and mechanically ready for the next independent review and explicit user HTML-acceptance gate. This receipt does not accept the HTML or authorize downstream stages.
- Scope: read-only inspection of frozen publication run `20260918-publication-09`, through Stage 40; this receipt is the only file changed.
- Assignment: bounded QA; orchestrator/policy owner `gpt-5.6-sol` / medium; QA policy `gpt-5.6-luna` / low. Platform-selected models/effort are unverified. Scoped override: none.
- Timestamp: 2026-09-18 02:38 UTC. Elapsed: approximately 5 minutes. Token usage: unavailable.

## Evidence

- `run.json`: run ID `20260918-publication-09`, portable identity `3626C7390775211110F1B8AC93D10EF13DA6D6336E62B031C328F0BB0B6A9401`. Output directories stop at `40-html-candidate`; acceptance directory contains only `master_en.acceptance.json`, `master_ru.acceptance.json`, and `artview.acceptance.json`. No HTML acceptance, Stage 50, DOCX, or PDF artifacts found.
- Stage 40 evidence manifest: `evidence/stages/40-html-candidate.manifest.json`, SHA-256 `EA04C2D46C3C39F581C00DA0F0951AFE875C9461AC8824C50749F5AE465F701E`; state `succeeded`, stage identity `40-html-candidate`, run identity matches. Upstream binds stages 10/20/21/30/31. Accepted MASTER_RU, ArtView acceptance, and strict decisions are manifest inputs. Accepted master source hashes match plan/context (`MASTER_EN` `3AEF660D…EAAB7B5`; `MASTER_RU` `A96BFEAF…D31A9230`).
- Independently checked all 20 Stage 40 artifact entries and 7 evidence entries against actual byte counts and SHA-256: **0 missing/mismatched**. Artifact inventory seal `7CD430F1F9824DBFE46705B4B9DC21170FF982AA48A3F2CC0BE9C2C3F0113E7E`; evidence inventory seal `1FA9ECA1D819D510A71612399E27316AB0512D1AFCA004ED067A8B97F5D4D3EF`. HTML is 162,457 bytes, SHA-256 `D338180EAA3E226882162ED6F85DDAA038149615ABF8324CE5A44234CC273193`.
- Producer report `outputs/40-html-candidate/evidence/production_html_report.json`: `pass`; 26 source pages; 19 image references, 0 missing; 7 statblock cards; 0 findings. Stage diagnostics identify `translator_build_production_html_v1`, `direct_pdf_route=false`, 19 local references.
- Semantic projection `outputs/40-html-candidate/evidence/html_semantic_projection.json`: recomputed canonical JSON seal equals declared `A64EB795651966F5F86121CD362368B14816057839981600403F9AA918836FBF`. Exactly seven projected IDs, all page 18 and ordinal 1–7: `stanwick-statblock`, `elsie-statblock`, `regular-statblock`, `heavy-statblock`, `migo-man-statblock`, `migo-statblock`, `hunting-horror-statblock`. Referenced semantic sidecar exists and its SHA-256 matches `324742569FCE6C0215E8755A340A0D05EE33D46076F7F8A61090A8D1AFA5874A`.
- HTML structure was counted directly in the page sections: page 14 has exactly 1 blockquote, containing exactly 1 `<ul>` and 4 `<li>`; page 18 has exactly 7 `review-callout statblock-card` blockquotes. Per-card `<br>` counts are `2,4,2,3,4,8,6`, preserving physical row flow.
- HTML has 19 unique local image references; all resolve within the candidate artifact bundle. The Stage 40 output manifest lists exactly 19 image files plus the HTML.

## Files checked / verification

- Plan/context: `kb_creator/docs/plans/20260918-dream-html-candidate-export-ux/{plan.md,context.md}`.
- Run authority/boundary: `kb_creator/working/number-7-dream/publication/20260918-publication-09/{run.json,acceptance/*,outputs/*}`.
- Stage records: `evidence/stages/40-html-candidate.manifest.json` and upstream manifest hashes; Stage 40 artifacts/evidence listed above.
- Commands: PowerShell read-only inventory, `Get-FileHash`, and regex counts over page-scoped HTML; bundled Python canonical-JSON SHA recomputation and semantic-sidecar check. No implementation/tests/output were changed or rebuilt.

## Blockers and next action

- Blockers: none for bounded Stage 40 QA.
- Next: independent critic review (H8), then present this exact HTML candidate for explicit user acceptance (H9). Do not infer acceptance or start Stage 50/DOCX/PDF.

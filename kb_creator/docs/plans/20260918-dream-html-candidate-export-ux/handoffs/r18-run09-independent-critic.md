# R18 run09 independent implementation/process critic receipt

- Goal / step: `20260918-dream-html-candidate-export-ux` / `H8-independent-implementation-process-review`.
- Review kind: `implementation`.
- Candidate state reviewed: assigned frozen run09 Stage 40 HTML evidence from `20260918-publication-09`; no acceptance or downstream release decision is made here.
- Implementer/designer participation: I did not implement or materially design the candidate under review.
- Role / model / effort: independent critic; repository-policy role `gpt-5.5`, medium. Platform-selected model/effort unavailable.
- Orchestrator policy owner: `gpt-5.6-sol`, medium. Orchestration ownership was not transferred.
- Assignment state: platform-unverified independent critic assignment.
- Scoped override: none.
- Scope: read-only review of governing instructions, goal plan/context, R14-R17 receipts, relevant implementation diffs, tests, and run09 Stage 40 evidence. This receipt is the only file changed.

## Files checked

- `AGENTS.md`; `docs/governance/nri_goal_governance.md`.
- Goal state: `kb_creator/docs/plans/20260918-dream-html-candidate-export-ux/plan.md`, `context.md`.
- Prior receipts: `handoffs/r14-run07-html-qa.md`, `r15-html-semantics-architecture.md`, `r16-html-semantics-implementation.md`, `r17-run09-html-qa.md`.
- Implementation surfaces: `kb_creator/pipeline/publication_adapters.py`, `translator/translator.py`.
- Regression surfaces: `kb_creator/tests/test_publication_html_adapter.py`, `translator/tests/test_recovery_support.py`, `kb_creator/tests/test_publication_control_plane.py`.
- Candidate evidence: `kb_creator/working/number-7-dream/publication/20260918-publication-09/run.json`, `acceptance/`, `evidence/stages/40-html-candidate.manifest.json`, `outputs/40-html-candidate/{artifacts,evidence}`.

## Evidence

- Run09 accepted masters remain byte-identical to the plan/context hashes: `MASTER_EN.md` SHA-256 `3AEF660DFAD007448F9F935E762EC4FED7B865773AA8899AC0CBC63DAEAAB7B5`; `MASTER_RU.md` SHA-256 `A96BFEAF5642ACB7524D25DA6551A7916EDD650563887E1781A99BD9E31A9230`.
- Run09 stops at Stage 40: `acceptance/` contains only `artview.acceptance.json`, `master_en.acceptance.json`, and `master_ru.acceptance.json`; no `html.acceptance.json`; `outputs/50-docx-candidate` and `outputs/60-pdf-candidate` are absent.
- Stage 40 manifest SHA-256 is `EA04C2D46C3C39F581C00DA0F0951AFE875C9461AC8824C50749F5AE465F701E`; it records state `succeeded`, run identity `3626C7390775211110F1B8AC93D10EF13DA6D6336E62B031C328F0BB0B6A9401`, upstream stages 10/20/21/30/31, 20 artifact outputs, and 7 evidence outputs.
- HTML candidate is 162,457 bytes, SHA-256 `D338180EAA3E226882162ED6F85DDAA038149615ABF8324CE5A44234CC273193`.
- Producer report is `pass` with `26` source pages, `19` image refs, `0` missing image refs, `7` statblock cards, and `0` findings.
- Semantic projection declares exactly seven expected IDs on page 18 ordinals 1-7: `stanwick-statblock`, `elsie-statblock`, `regular-statblock`, `heavy-statblock`, `migo-man-statblock`, `migo-statblock`, `hunting-horror-statblock`; declared projection seal is `A64EB795651966F5F86121CD362368B14816057839981600403F9AA918836FBF`.
- Direct HTML counts confirmed page 14 has one blockquote with one `<ul>` and four `<li>` rows; page 18 has seven `review-callout statblock-card` blockquotes with `<br>` counts `2,4,2,3,4,8,6`.
- Code inspection confirms Stage 40 resolves semantics through `RECONSTRUCTION_INVENTORY.json` -> exactly one `reconstruction_manifest` -> sealed `RECONSTRUCTION_MANIFEST.json` -> `candidate.files` semantic sidecar and `review.decisions`; it identity-checks content sidecar and page decisions, aligns complete per-page blockquote container counts, rejects reserved source `statblock-card` directives, injects directives into the derived source, and gates final rendered card count/page ordinal.
- Renderer inspection confirms blockquote extraction preserves trailing hard-break spaces, coalesces blank-separated same-kind quoted lists, and only uses forced physical row `<br>` flow when the callout class includes `statblock-card`.
- Focused test rerun was attempted with `.tools/MinerU/.venv/Scripts/python.exe` and bundled Codex Python, but both environments lacked `pytest`. Existing R16/R17 evidence reports the focused suite passed `136 passed, 260 subtests passed`; I did not rerun it independently.

## Findings

1. Low severity, non-blocking: `html_semantic_projection.json` labels the post-injection derived Markdown identity as `master_ru`, while the accepted `MASTER_RU` identity is bound separately in `html_adapter_receipt.json` (`bindings.master_ru`) and the Stage 40 manifest. This does not invalidate run09 because the receipt and manifest bind both accepted input and derived source, but the projection evidence would be clearer and more self-contained if it recorded `accepted_master_ru` and `derived_html_source` as separate fields in a future schema revision.

No medium or high severity findings.

## Blockers

- None for H8 implementation/process review.
- This is not a release review and does not approve HTML acceptance, Stage 50, DOCX, PDF, release, commit, or push.

## Recommendation

`PASS / READY_FOR_USER_HTML_ACCEPTANCE_GATE`.

Present only the exact run09 Stage 40 HTML candidate for explicit user acceptance. Keep run07 as immutable defect evidence. Any mutation of run09 Stage 40 artifacts, implementation inputs, accepted decisions, or accepted masters invalidates this receipt and requires fresh QA plus a new independent review.

## Accounting

- Elapsed time: approximately 42 minutes.
- Token use: unavailable to contributor.
- Timestamp: 2026-09-18T05:42:26+03:00.

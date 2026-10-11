# R14 run07 HTML bounded QA receipt

- Goal / step: `20260918-dream-html-candidate-export-ux` / `H6-run07-html-qa`.
- Result: `FAIL / NEEDS_CORRECTION` before HTML acceptance. Authority, stage integrity, assets, generic export UX, and downstream stopping checks pass; the HTML structural-semantic review found two defects below.
- Scope: read-only audit of run `20260918-publication-07` through Stage 40 and the shared ArtView generator/test evidence. No candidate, implementation, decisions, acceptance, plan/context/status, or downstream stages changed. This receipt is the only file written.
- QA role policy: `gpt-5.6-luna`, low; platform-selected model/effort unverified. Orchestrator policy owner: `gpt-5.6-sol`, medium; assignment state platform-unverified; scoped override none.

## Files checked and commands

- Goal `plan.md` and `context.md`; run07 `run.json`, acceptance receipts, Stage 30 candidate manifest, Stage 31/40 manifests and outputs, accepted/rebound decisions, `ARTVIEW_APPLIED.json`, Stage 40 HTML candidate, and local assets.
- `kb_creator/scripts/scenario_artview.py` and `kb_creator/tests/test_scenario_artview_v3.py`.
- Read-only PowerShell checks recomputed byte lengths and SHA-256 for every Stage 31/40 manifest output and Stage 40 evidence file; compared run06 accepted vs run07 rebound decision row cores and candidate current/context/alternative binary identities; compared HTML `<img src>` paths with manifest asset paths. Targeted `Select-String` and regex inventory counted semantic tags on pages 14 and 18.

## Passing evidence

- Run identity agrees across run and stage manifests: `8CB7261434C60CC8AA8CD9FAC32C64CF6003779AA21502958F5B7500B126C1E3`.
- Accepted MASTER_EN and MASTER_RU are hash-bound in run07; MASTER_RU SHA-256 `A96BFEAF5642ACB7524D25DA6551A7916EDD650563887E1781A99BD9E31A9230` equals the accepted candidate hash. Stage 40 binds the MASTER_RU acceptance receipt raw SHA `23A401C7DE4681D3ABE99EF901F3570E277D88F329C7C32A1018AEB4E8593627` and accepted ArtView receipt raw SHA `8C58ADAFD50E04834C5F258A938D9D4774EC8E83152D73709B89690D89ECCBDA`.
- ArtView acceptance receipt seal is `777AC446FF1798E0C22BEE8F28EE57FBF928D9FD661126C218E498B8CE9DB55A`. Run06 source decisions SHA `6A1326CABEE791FA321E0D2D2651CB1C7BAE9E716D90EB6D492EF54333649F24` were rebound to run07 target decisions SHA `2C9CDF929FC3971AAC8799BD613790D3BC5242BE20D173AC0318A077CD066736`. All 19 decision row cores match exactly (binary choice/candidate, presentation, reviewed flag, notes); all 19 were reviewed and kept current. Candidate current/context and alternative binary identity graphs also match exactly across source/target; target candidate manifest SHA is `794B4ECB82322076B2787D825AE9A8F19AF2079D053659A206392464446B3DE9`.
- Stage 31 `31-artview-apply` succeeded, reproducibility SHA `45A4619C7BFAC393B41FC79F5672C15BC3BB5EDFF486B1D221AE887261452FC2`; application records 19 included / 19 reviewed / 0 excluded and binds to accepted ArtView, the rebound decisions, and run07 candidate manifest.
- Stage 40 `40-html-candidate` succeeded, producer diagnostic `pass`, reproducibility SHA `F38C8D86AE3F21F0EDD5B6944943A4243FFE53F624791817D24926B27D3C3BEE`. All 23 Stage 31 outputs, all 20 Stage 40 outputs, and all six Stage 40 evidence files matched manifest byte counts and SHA-256. HTML is 162,302 bytes, SHA-256 `98F3D384887F29E955544CCBC6E2E395F9011742E5B1D715F925437E7953C242`.
- The HTML references exactly 19 unique local images, matching the 19 Stage 40 asset records; all files exist and match recorded binary identities. Producer diagnostic reports 19 local references and `direct_pdf_route=false`.
- Shared export UX is present at `scenario_artview.py:1304-1306`: download helper returns `link.download`, `copyExportLocator(filename)` attempts `navigator.clipboard.writeText(filename)`, and success/fallback explicitly state the browser controls the full path. Focused regression assertions exist in `test_scenario_artview_v3.py:501-504`. Parent reports the focused suite passed (`55 passed / 255 subtests`); I could not independently rerun it because importing the module fails with `ModuleNotFoundError: No module named 'PIL'` under the available local test Python.
- Only Stage 10/20/21/30/31/40 output directories exist. No HTML acceptance receipt, Stage 50, DOCX, or PDF exists. `acceptance/` contains MASTER_EN, MASTER_RU, and ArtView receipts only.

## Findings — blocks HTML acceptance

1. **Page 14, medium severity — one logical bulleted list is split into four HTML lists.** `Number_7_Dream_RU.html:687-698` contains a single Elsie `<blockquote class="review-callout">` and four `<li>` items, but each item is wrapped in its own `<ul>` (lines 688, 691, 694, 697). This creates four one-item lists rather than one four-item list, interrupting list semantics and adding list spacing. The accepted MASTER_RU page-14 letter has four bullets in one quoted list (`MASTER_RU.md:400-408`).
2. **Appendix A, medium severity — stat entries do not render as structured stat cards.** Page 18 has seven separate `blockquote.review-callout` containers (`Number_7_Dream_RU.html:772-781`) and zero `.statblock-card` elements; each character's fields/actions/skills are collapsed into a single `<p>` (e.g. lines 772-776, 779, 781). The surrounding HTML defines `.statblock-card` styling, but it is unused on this appendix. Thus boundaries are visually boxed as generic callouts, but the requested stat-card semantics and internal line grouping are absent.

## Next action

- Do not present run07 as HTML-acceptance-ready. Correct the generic Markdown/HTML semantic projection for callout lists and Appendix A stat cards/line groups, rebuild a fresh successor Stage 40, and rerun focused QA. Do not record HTML acceptance or run Stage 50/DOCX/PDF before a clean QA receipt and independent review.

## Accounting

- Elapsed time: approximately 12 minutes.
- Token use: unavailable.
- Timestamp: 2026-09-18 01:50 UTC.

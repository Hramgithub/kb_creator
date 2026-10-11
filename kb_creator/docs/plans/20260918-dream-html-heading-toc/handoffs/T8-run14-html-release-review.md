# T8 Run14 HTML Release-Gate Review

- timestamp: `2026-09-18T14:11:18.5723998+03:00`
- review_kind: `release`
- verdict: `PASS`
- assignment_state: `complete`
- implemented_or_materially_designed_candidate: `no`
- orchestrator_policy_owner: `/root`, repository-policy `gpt-5.6-sol` at medium
- scoped_override: read-only release-gate review of run14 HTML candidate only; this receipt is the sole permitted write
- elapsed_time: approximately 45 minutes
- token_use: unavailable

## Scope

Reviewed current plan/context, T7/T7c/T7d root-cause receipts, Stage 40 code deltas, focused tests, and fresh run14 Stage 40 evidence/artifact:

- `kb_creator/docs/plans/20260918-dream-html-heading-toc/plan.md`
- `kb_creator/docs/plans/20260918-dream-html-heading-toc/context.md`
- `kb_creator/docs/plans/20260918-dream-html-heading-toc/handoffs/T7-stage40-semantic-span-root-cause.md`
- `kb_creator/docs/plans/20260918-dream-html-heading-toc/handoffs/T7c-stage40-frontmatter-root-cause.md`
- `kb_creator/docs/plans/20260918-dream-html-heading-toc/handoffs/T7d-stage40-statblock-ordinal-root-cause.md`
- `kb_creator/pipeline/publication.py`
- `kb_creator/pipeline/publication_adapters.py`
- `translator/translator.py`
- `kb_creator/tests/test_publication_html_adapter.py`
- `kb_creator/tests/test_publication_control_plane.py`
- `translator/tests/test_recovery_support.py`
- `kb_creator/working/number-7-dream/publication/20260918-publication-14/**`

No code, outputs, acceptance files, commit state, or canonical plan/status files were edited by this review.

## Candidate Identity

- publication run: `20260918-publication-14`
- run identity: `8E280A3F4919CBC76A50FA54FBD091FD050DC2CA6CB702027247EF5F81EF2863`
- implementation inventory: `8F71F185D9D4A424BF3B62DAB08DB4817D7958F81DE9A33B2498A8C1F1BA8A9F`
- Stage 40 reproducible SHA-256: `208C8F2A87036329D9A31B71EE8C14070B42DAA5ED761622F1FA8817551F6321`
- Stage 40 cache key: `C58E2BD0E441E8B7AE2826B735B9D5C02B97A3228801B8C8C996EDD7C0FE85E9`
- HTML artifact: `outputs/40-html-candidate/artifacts/Number_7_Dream_RU.html`
- HTML bytes/SHA-256: `155889` / `3F77B38C477D8E137CF22867BA9713EAF6AFD19C8168C07F1E8664E1790D1E21`
- Stage 40 source HTML config SHA-256: `260F180C326F53925116F12EE52BBC43F5875189ABD6E1C22CD63D9BF4F10C0C`
- Stage 40 output inventory SHA-256: `4330ECD3F982982C95B2287DB7CED6E25007FAD51987F0650706AE73A0552BFA`
- Stage 40 evidence inventory SHA-256: `A8173A84493241013079E9B6778713D5A996D1AB8B23FE7CF7DCE30C48FCCD26`
- adapter receipt SHA-256: `D3FC017433FDF0189C644196CAC29DF83C408EF28F4CEE7D76A7C5B0FD907AF3`
- renderer identity recorded in run and receipt: `translator/translator.py`, bytes `662427`, SHA-256 `F2755C7AAB30700922E2F2DE16308F39CD4354045E2CDF5CAFBB05D8251E5EB5`

The run identity now includes `translator/translator.py`; this closes the T7c implementation-inventory gap where renderer bytes were previously ambient.

## Checks Performed

- Recomputed all Stage 40 listed output/evidence file identities from disk: no mismatches.
- Ran focused relevant tests:
  - `kb_creator/tests/test_publication_html_adapter.py`
  - `kb_creator/tests/test_publication_control_plane.py`
  - `translator/tests/test_recovery_support.py`
  - result: `136 passed, 5 subtests passed in 91.62s`
- Read-only artifact parser checks over `Number_7_Dream_RU.html`, `frontmatter_manifest.json`, `html_semantic_projection.json`, `production_html_report.json`, and `html_adapter_receipt.json`.
- Scanned run14 outputs/acceptance tree for downstream artifacts and acceptance state.
- Checked Git state read-only.

## Systemic Fix Review

### Semantic EN to Translation to RU Projection

PASS.

The old same-language/global-line assumption is replaced by sealed translation lineage. `publication_adapters.py` now exposes `_translation_lineage` and `_semantic_html_projection` around lines `789` and `883`; the projection evidence is schema `kb_creator.html_semantic_projection.v2`.

Run14 evidence:

- projection SHA-256: `1F27697FBAD0B014BE7E70D37E060423D4E31F1D4318D53F8B42B70F354A2154`
- accepted MASTER_RU bound by projection: bytes `122946`, SHA-256 `904133D5057172C404D28F3BCF2A5E4C578304A59382512D1B31FC56AE0FDAB2`
- projected unit ids: `unit-00225` through `unit-00231`
- target RU line ranges: `527-530`, `532-537`, `539-542`, `544-548`, `550-555`, `557-566`, `568-575`
- projected ids in order: `stanwick-statblock`, `elsie-statblock`, `regular-statblock`, `heavy-statblock`, `migo-man-statblock`, `migo-statblock`, `hunting-horror-statblock`

This matches the T7 required bridge from page-local English semantic spans through Stage 20/21 unit lineage into accepted Russian payload ranges.

### Frontmatter Order Renderer Consumption

PASS.

T7c required the renderer to consume normalized `frontmatter_order` and not rely on legacy `frontmatter_position`. Current code has `resolved_frontmatter_policy` and `credits_before_toc` in `translator/translator.py` around lines `2543` and `7736`, with placement calls using it around lines `7774` and `7814`.

Run14 evidence:

- `frontmatter_manifest.flow` prefix is `page-001 -> page-002 -> toc:source -> page-004`
- TOC manifest: mode `preserve_and_link`, source page `003`, title `СОДЕРЖАНИЕ`, origin `source`, entries `18`
- credits manifest: pages `002`
- exactly one source TOC nav exists; generated nav count is `0`
- source TOC link count is `18`, with href order ending at `prilozhenie-c-zaranee-sozdannye-personazhi-igrokov`

This closes the run12 credits/source-TOC swap.

### Renderer Implementation Inventory Closure

PASS.

`publication.py` now includes `translator/translator.py` in `_implementation()` around lines `403-407`, and `test_publication_control_plane.py` covers the renderer identity around lines `870-885`.

Run14 `run.json` records:

- implementation inventory: `8F71F185D9D4A424BF3B62DAB08DB4817D7958F81DE9A33B2498A8C1F1BA8A9F`
- `translator/translator.py`: bytes `662427`, SHA-256 `F2755C7AAB30700922E2F2DE16308F39CD4354045E2CDF5CAFBB05D8251E5EB5`

The Stage 40 adapter receipt records the same renderer identity.

### Nesting-Aware Statblock DOM Validation

PASS.

T7d required nesting-aware DOM ownership instead of lazy page regex slicing. Current `publication_adapters.py` has `_SemanticCards(HTMLParser)` and `_validate_semantic_cards` around lines `343` and `411`, and Stage 40 calls the validator around line `1121`.

Run14 DOM evidence:

- actual semantic cards are exactly seven `section.statblock-card` elements.
- each card has `data-semantic-kind="statblock"`.
- all seven are owned by production page `018`.
- card ids exactly match the projection order:
  `stanwick-statblock`, `elsie-statblock`, `regular-statblock`, `heavy-statblock`, `migo-man-statblock`, `migo-statblock`, `hunting-horror-statblock`.
- obsolete statblock containers found: `0`; no `blockquote.statblock-card` and no `review-callout statblock-card`.

This closes the run13 false ordinal mismatch while preserving the fail-closed invalid-container checks.

### TOC, Hierarchy, and Statblock Output

PASS.

Run14 production report:

- status: `pass`
- findings: `0`
- source pages: `26`
- image refs: `19`, missing image refs: `0`
- statblock cards: `7`
- source TOC entries: `18`
- removed source TOC pages: `1`

Appendix C parsed DOM heading shape:

- H1: `1` (`ПРИЛОЖЕНИЕ C — ЗАРАНЕЕ СОЗДАННЫЕ ПЕРСОНАЖИ ИГРОКОВ`)
- H2: `6` character records
- H3: `12` subordinate leaf headings

The source TOC is the only nav. It contains one scenario-level `Предыстория` entry and no repeated `Что ты знаешь о Стэнвике` leaf entries.

## Boundary Confirmation

Confirmed absent in run14:

- no HTML acceptance file
- no Stage 50 output
- no DOCX candidate output
- no PDF candidate output
- no production package or offline-verify output

Run14 outputs stop at:

- `10-master-en-candidate`
- `20-master-ru-packets`
- `21-master-ru-candidate`
- `30-artview-bundle`
- `31-artview-apply`
- `40-html-candidate`

Run14 acceptance directory contains only:

- `master_en.acceptance.json`
- `master_ru.acceptance.json`
- `artview.acceptance.json`

Git was checked read-only. Current branch is `main...origin/main [ahead 1]`, dirty and unstaged from the broader active work. This review did not commit or push.

## Blocking Findings

None.

## Residual Risks / Notes

- `plan.md` and `PROJECT_STATUS.md` still describe earlier gates/states and do not yet canonically summarize run14. This is a state-reporting lag, not a candidate artifact failure. The run14 Stage 40 evidence is internally sealed and was verified directly.
- This is a release-gate review of the HTML candidate only. It does not accept HTML, does not authorize Stage 50, and does not approve DOCX/PDF/package/release.

## Recommendation

PASS: run14 HTML candidate is ready to present for the explicit user HTML acceptance gate.

Do not continue to Stage 50/DOCX/PDF until the user explicitly accepts this exact HTML candidate hash:

`3F77B38C477D8E137CF22867BA9713EAF6AFD19C8168C07F1E8664E1790D1E21`

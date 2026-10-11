# Number 7 Dream HTML candidate and ArtView export UX context

## Accepted ArtView authority

- Source publication run: `20260918-publication-06`; portable identity
  `60B28787BDA98CF13CA271273B748179F167AF4D63B9CBCD8712E65BE8D5A4EC`.
- The user explicitly completed and exported all `19/19` review rows.
- Accepted decisions contain 19 `keep_current` binary choices, 11 centered
  non-wrapped placements and eight right-aligned text/table-wrapped placements;
  every row is explicitly reviewed.
- Accepted decisions file SHA-256:
  `6A1326CABEE791FA321E0D2D2651CB1C7BAE9E716D90EB6D492EF54333649F24`.
- Decisions seal:
  `BE770E7C5A594D7FD9EE2BABD8B6D31930F31E8A434ECD9F16F27325C959D335`.
- ArtView acceptance seal:
  `F27DC9CE59AD84EE8D0B7135AA2F9E9944E0A1154E4B3725DEC47B11C2AFF647`.
- Stage 31 reproducible SHA-256:
  `08D42487B129A6CF76C01A26BFB5F7DB0EA288AF5F8499AF0F572004792D7837`;
  application SHA-256:
  `E4288190482DB16C6E916014B4EDB4CC1EC23B74AE0143C2AA51C2C1D79B663A`.

## Generic export UX correction

The shared ArtView v3 page now returns the exact filename produced by its
download helper, attempts to copy that filename through the clipboard API, and
reports whether copying succeeded. It explicitly states that the full download
path is chosen by the browser and is not exposed to the page. This avoids a
false absolute path while still providing a useful pasteable locator.

The focused ArtView/publication-control suite passes `55 passed, 255 subtests
passed`. Coverage asserts the filename return value, clipboard call, success
message, and full-path limitation, in addition to the existing wrap/alignment
state-machine regressions.

Because this implementation changed after run06 Stage 31, run06 correctly
failed Stage 40 freshness validation. It remains immutable accepted-ArtView
evidence and was not bypassed.

## Run07 defect evidence

- Current run: `20260918-publication-07`; portable identity
  `8CB7261434C60CC8AA8CD9FAC32C64CF6003779AA21502958F5B7500B126C1E3`.
- Accepted MASTER_EN SHA-256:
  `3AEF660DFAD007448F9F935E762EC4FED7B865773AA8899AC0CBC63DAEAAB7B5`.
- MASTER_RU SHA-256:
  `A96BFEAF5642ACB7524D25DA6551A7916EDD650563887E1781A99BD9E31A9230`;
  all `298/298` translations rebound by exact source.
- Run07 ArtView decisions were rebound only after exact candidate graph and
  binary equivalence. Target decisions file SHA-256:
  `2C9CDF929FC3971AAC8799BD613790D3BC5242BE20D173AC0318A077CD066736`;
  ArtView acceptance seal:
  `777AC446FF1798E0C22BEE8F28EE57FBF928D9FD661126C218E498B8CE9DB55A`.
- Stage 40 reproducible SHA-256:
  `F38C8D86AE3F21F0EDD5B6944943A4243FFE53F624791817D24926B27D3C3BEE`.
- HTML candidate:
  `outputs/40-html-candidate/artifacts/Number_7_Dream_RU.html`, 162,302 bytes,
  SHA-256
  `98F3D384887F29E955544CCBC6E2E395F9011742E5B1D715F925437E7953C242`.
- Producer diagnostics pass through `translator_build_production_html_v1`;
  direct-PDF routing is false and all 19 local references are closed.
- Live inspection confirmed 26 source-page containers and 19/19 complete
  images, but did not establish correct list grouping or typed statblock cards.

R14 bounded QA rejected this HTML candidate before acceptance. Although all
authority bindings, 19 local references, hashes, and stage boundaries pass,
the renderer emits the four page-14 bullets as four separate one-item `<ul>`
elements. It also leaves the seven page-18 semantic stat blocks as generic
`review-callout` blockquotes, flattens most source rows into one paragraph, and
emits zero `.statblock-card` elements. Run07 is therefore immutable defect
evidence, not an acceptance candidate. The active work is a generic,
metadata-driven HTML projection correction followed by a fresh successor and
repeat QA. Stage 50, DOCX, PDF, HTML acceptance, release, commit, and push are
absent.

## Corrected run09 successor and current gate

- Current candidate run: `20260918-publication-09`; portable identity
  `3626C7390775211110F1B8AC93D10EF13DA6D6336E62B031C328F0BB0B6A9401`.
- Accepted MASTER_EN and MASTER_RU remain byte-identical at SHA-256
  `3AEF660DFAD007448F9F935E762EC4FED7B865773AA8899AC0CBC63DAEAAB7B5`
  and `A96BFEAF5642ACB7524D25DA6551A7916EDD650563887E1781A99BD9E31A9230`.
  All `298/298` translations and all `19/19` accepted ArtView decisions were
  rebound through their strict successor commands.
- Corrected HTML: `outputs/40-html-candidate/artifacts/Number_7_Dream_RU.html`,
  162,457 bytes, SHA-256
  `D338180EAA3E226882162ED6F85DDAA038149615ABF8324CE5A44234CC273193`.
  Stage-manifest SHA-256:
  `EA04C2D46C3C39F581C00DA0F0951AFE875C9461AC8824C50749F5AE465F701E`.
- Producer report is `pass`: 26 pages, 19 image references, zero missing
  references, exactly seven final `.statblock-card` elements, and zero
  findings. Projection seal:
  `A64EB795651966F5F86121CD362368B14816057839981600403F9AA918836FBF`.
- Live DOM/visual inspection confirms page 14 has one callout containing one
  `<ul>` with four `<li>` rows; page 18 has seven typed cards with physical row
  breaks (`2,4,2,3,4,8,6` `<br>` elements); all 19 images are complete with
  non-zero natural width and the console has no warnings/errors.
- Focused reusable tests pass `136 passed, 260 subtests passed`; `git diff
  --check` is clean. R17 bounded QA is `PASS`; R18 independent review is
  `PASS / READY_FOR_USER_HTML_ACCEPTANCE_GATE` with no blockers. Its only
  non-blocking note is that a future semantic-projection schema revision could
  label accepted and derived Markdown identities more explicitly; run09 binds
  both identities separately in its adapter receipt and stage manifest.
  HTML acceptance, Stage 50, DOCX, PDF, release, commit, and push remain absent.

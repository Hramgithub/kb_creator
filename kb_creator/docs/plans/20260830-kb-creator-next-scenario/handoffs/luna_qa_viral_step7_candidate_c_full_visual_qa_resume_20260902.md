# Viral Step 7 Candidate C — full visual QA resume receipt

## Scope and assignment

- Executor: `gpt-5.6-luna` / bounded QA / high.
- Scope: resume of Candidate C full visual QA after the generator schema remediation.
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`.
- Generator command: the exact command from the parent assignment, run verbatim; exit code `0`.
- Allowed writes used: the generated bundle root and this receipt only. No Candidate C, config, code, tests, plan, context, status, release, Git, MinerU, unrelated test, or cleanup mutation was made.
- Orchestrator policy owner: `gpt-5.6-sol`.
- Assignment state: bounded execution complete; receipt written for orchestrator integration.
- Scoped override: this assignment explicitly scopes execution to `gpt-5.6-luna` at high QA effort; orchestration ownership remains with `gpt-5.6-sol`.
- Timestamp: `2026-09-02T04:13:37.7623606+03:00`.
- Elapsed time: approximately 20 minutes of interactive bounded execution; no authoritative assignment-start timer was available.
- Token use: unavailable; no per-role token counter was exposed.

## Frozen and post-run identities

| Input | SHA-256 before | SHA-256 after | Result |
|---|---|---|---|
| Candidate `INVENTORY.json` | `4745E245E754FEA89BCA753C9CD73F1B85C30CE07BFE65C2BF760ED7FF4352F7` | `4745E245E754FEA89BCA753C9CD73F1B85C30CE07BFE65C2BF760ED7FF4352F7` | unchanged |
| Candidate `MASTER_EN.md` | `F486849BB6A2E8EE860F092C0AE691CD4780A08A8065BFF19C47B3BB0DC461D1` | `F486849BB6A2E8EE860F092C0AE691CD4780A08A8065BFF19C47B3BB0DC461D1` | unchanged |
| Publication config | `C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30` | `C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30` | unchanged |
| Source PDF | `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05` | `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05` | unchanged |
| Remediated QA generator | `A3704327AF4E9C0B78243673CC716B1DC5CE35530C8EFF5BA27E8398FFBA8BE7` | `A3704327AF4E9C0B78243673CC716B1DC5CE35530C8EFF5BA27E8398FFBA8BE7` | unchanged |
| Resume assignment | `7C25D390C2132590A8C33D458345ACD1E9A2D582A0AB1218AA05A608E6DDD5E7` | `7C25D390C2132590A8C33D458345ACD1E9A2D582A0AB1218AA05A608E6DDD5E7` | unchanged |

The remediated focused-test identity supplied by the resume assignment was `21A0135068564B45A77707F99EF17C9C3A7A461469E9D447ED485B57C3900C8A`; its supplied focused evidence was 10 tests passed. No additional tests were run.

## Bundle manifest and deterministic checks

Bundle root:
`C:\Users\BogdanD\.codex\visualizations\2026\08\30\01a05392-3683-7292-b5d5-20ddc8b54a80\viral-master-en-candidate-c-visual-qa-20260902-v1`

Manifest: `VISUAL_QA_BUNDLE.json` SHA-256 `315FDAEF276EE9FC2E0A5D25A21EFCCE478C7AF11420438B9424B212C9627CAF`.

| Manifest field | Actual count | Required count |
|---|---:|---:|
| candidate assets | 123 | 123 |
| reader assets | 107 | 107 |
| visual-review units | 91 | 91 |
| tiles | 107 | 107 |
| contact sheets | 27 | 27 |
| priority rows | 39 | 39 |
| transported priority originals | 39 | 39 |
| open generation errors | 0 | 0 |

Additional deterministic evidence:

- 174 output paths were referenced by the manifest; all 174 existed, were unique, and remained beneath the bundle root. Bundle file inventory was 175 files including the manifest.
- All 39 transported priority originals matched the Candidate C source byte-for-byte, SHA-256-for-SHA-256, and by decoded dimensions; mismatches: `0`.
- The required image set (27 contact sheets + 39 transported originals + p80 render) decoded successfully: `67/67`; corrupt/blank decode failures: `0`.
- p80 source render: `p80/p080.png`, source page `80`, `1700x2200`, `200 DPI`, `3,116,524` bytes, SHA-256 `D3844343B305F01D84C00EA074FAD21C05CDF27E413FE9C3D6FCE5EFC9C138B0`; source PDF identity in the render manifest matched the frozen PDF.
- Candidate proof: owner `viral-handout-13`, exact visible text `Hey Marco Babez`, occurrence count `1` in the Candidate C text and in the manifest proof.
- All 91 visual-review units were covered by the inspected reader-assets set (58 unique asset IDs across the units; no unit asset IDs missing from the 107 reader assets). The contact-sheet sequence covers all 107 reader assets.

## Direct visual inspection — contact sheets

Every row below was opened with `view_image(detail=original)`. The ordered page labels and semantic crops were coherent; no blank, black, corrupt, duplicated-generated, or orientation/aspect-ratio defect was observed. The special ranges containing p1, p80, and p124 are called out.

| # | Contact sheet | Observation |
|---:|---|---|
| 1 | `contact_sheets/pages-001-004.png` | Ordered p1–p4; front-cover opening coherent; crops and labels aligned. |
| 2 | `contact_sheets/pages-005-008.png` | Ordered p5–p8; page sequence and crop framing coherent. |
| 3 | `contact_sheets/pages-009-012.png` | Ordered p9–p12; coherent page labels and orientations. |
| 4 | `contact_sheets/pages-013-016.png` | Ordered p13–p16; no blank or malformed tile. |
| 5 | `contact_sheets/pages-017-020.png` | Ordered p17–p20; crops and aspect ratios coherent. |
| 6 | `contact_sheets/pages-021-024.png` | Ordered p21–p24; no ordering or label defect. |
| 7 | `contact_sheets/pages-025-028.png` | Ordered p25–p28; reader crops coherent. |
| 8 | `contact_sheets/pages-029-032.png` | Ordered p29–p32; labels and orientation coherent. |
| 9 | `contact_sheets/pages-033-036.png` | Ordered p33–p36; no blank/black/corrupt output. |
| 10 | `contact_sheets/pages-037-040.png` | Ordered p37–p40; crop boundaries coherent. |
| 11 | `contact_sheets/pages-041-044.png` | Ordered p41–p44; no duplicate-generated artifact. |
| 12 | `contact_sheets/pages-045-048.png` | Ordered p45–p48; labels and orientation coherent. |
| 13 | `contact_sheets/pages-049-052.png` | Ordered p49–p52; reader crops coherent. |
| 14 | `contact_sheets/pages-053-056.png` | Ordered p53–p56; full-page imagery and labels coherent. |
| 15 | `contact_sheets/pages-057-060.png` | Ordered p57–p60; no blank/black/corrupt output. |
| 16 | `contact_sheets/pages-061-064.png` | Ordered p61–p64; crop framing and labels coherent. |
| 17 | `contact_sheets/pages-065-068.png` | Ordered p65–p68; no orientation or ordering defect. |
| 18 | `contact_sheets/pages-069-072.png` | Ordered p69–p72; map/image crops coherent, including intentional source pixelation. |
| 19 | `contact_sheets/pages-073-076.png` | Ordered p73–p76; handout crops and page labels coherent. |
| 20 | `contact_sheets/pages-077-080.png` | Ordered p77–p80; map/handout crops coherent; p80 reader area present. |
| 21 | `contact_sheets/pages-081-084.png` | Ordered p81–p84; handout/image crops coherent. |
| 22 | `contact_sheets/pages-085-088.png` | Ordered p85–p88; labels and aspect ratios coherent. |
| 23 | `contact_sheets/pages-089-092.png` | Ordered p89–p92; no blank or malformed tile. |
| 24 | `contact_sheets/pages-093-096.png` | Ordered p93–p96; scene/handout crops coherent. |
| 25 | `contact_sheets/pages-097-100.png` | Ordered p97–p100; dark scene and manuscript crops remain coherent and intentional. |
| 26 | `contact_sheets/pages-101-104.png` | Ordered p101–p104; cave/landscape/map crops coherent. |
| 27 | `contact_sheets/pages-105-107.png` | Ordered p105–p107; map/merchandise-page crops coherent; no terminal-page defect. |

## Direct visual inspection — transported priority originals

Every row below was opened with `view_image(detail=original)`. The path column is the basename under `priority_originals/`. All transported files were also checked against their Candidate C sources as recorded above.

| # | Page | Role | Transported basename | Observation |
|---:|---:|---|---|---|
| 1 | 1 | front cover | `assets__bf086d551d421ea23a91bd0e18e919f183ea29b6476f149b0f75c43fdc3df643.png` | Green/black front cover; title, quote, and logos intact; no clipping. |
| 2 | 53 | full page | `assets__2ebda31f091167d0746cefffb0ba817e95c00683579e25b8ff124275717688ec.jpg` | Jet/sky full-page composition coherent and correctly oriented. |
| 3 | 69 | map | `assets__9cddc3fc484dffdcce7654b3ebc058b362dbb265508a64d64d7485b33dc600c8.jpg` | Satellite map coherent; intentional source pixelation/censoring retained. |
| 4 | 74 | handout | `assets__9ee3d23cac4831e4230386f671d228d7a53b336310983f967eada4f3d2677ad8.jpg` | Email handout crop is upright and legible. |
| 5 | 74 | handout | `assets__b1b7888cf28240790d1fd7fdc5621da9fe159c9442ec0f3bfa7f45243319cfea.jpg` | Email handout crop is upright and legible. |
| 6 | 75 | handout | `assets__f796716cd86ee8580b1d2cd8552d89cbf29f989bc8eae6be386ffa2528dc078b.jpg` | Continuation email is coherent and legible. |
| 7 | 75 | handout | `assets__2a60f183499c0a1a5f3bd353949a7efc2a389d5fbd98782e79e53d346d9c390f.jpg` | Continuation email is coherent and legible. |
| 8 | 76 | handout | `assets__8dcb6eee3da06a699ff2ac68c0b32338209a8abad3327bf0c8e246c2722dc76e.jpg` | Email plus map attachment is upright, complete, and legible. |
| 9 | 77 | map | `assets__826e5103327297822e6270444f8d57d02a135ffbc2d246ffbdb5788d297fd55a.jpg` | Annotated satellite map has coherent geometry and labels. |
| 10 | 78 | map | `assets__8dfcf412070881aa81b8933eeb329d7409edbe1316329701bb605c9dab835d65.jpg` | Hospital floor plan is upright with readable labels and intact lines. |
| 11 | 81 | handout | `assets__5246e2c434242d2ddea6226d861d9608f5b6afa86230da5ad3b6d01553bb4ca5.jpg` | Monochrome lighthouse image is coherent and fully framed. |
| 12 | 82 | handout | `assets__2e49f854b389f6c5cf89bced8318e197b6e79fd53d47dfa5dd64b0dcd697bbcc.jpg` | Dark figure/scene image remains coherent with intact framing. |
| 13 | 94 | handout | `assets__06a2c68cc38d4904595e16d0153d127eb08ae61c189a613f269a120de5233201.jpg` | Bridge scene is correctly oriented and complete. |
| 14 | 95 | handout | `assets__affb03a14eabd3ce60d78047279316ebde282a079528b6e00067698ebed92715.jpg` | Ritual-pit image is coherent and fully framed. |
| 15 | 96 | handout | `assets__373a4c9272242f27df9f3410b860e7bc5af602f17d1f08115649653754aad884.jpg` | Dark brick/window scene is coherent. |
| 16 | 97 | handout | `assets__5c03c3f42abbf1962a78d589d00014a6aac425db8b061cce69995930bd33d8b4.jpg` | Related empty-window scene is coherent and correctly oriented. |
| 17 | 98 | handout | `assets__217633ad4ab84de07789ba9c47d7c00ee382de486902cf967330d5d94061e8b5.jpg` | Cave with silhouettes is coherent and complete. |
| 18 | 99 | handout | `assets__c34aabc5bd16dfcb318cad3a11df583f9f15d4778f488832af69d182dc9d8201.jpg` | Ritual-pit scene is coherent and fully framed. |
| 19 | 100 | handout | `assets__faaf56706aeb8cc15c6cfeb89bf7731b313ccdfde78f28b12da65b123d355bcd.jpg` | Ritual slab scene is coherent. |
| 20 | 100 | handout | `assets__84f3fbba13df63026fc147880fa903b708f67969bb85a2e8ffd7ae95bc921172.jpg` | Illustrated manuscript is upright and intact. |
| 21 | 101 | handout | `assets__d18f3a9358fcdda6d5f56178aa99b37609c72d286a380e71c4189337c1a9c5ae.jpg` | Cave/skull close-up is coherent and complete. |
| 22 | 101 | handout | `assets__4e663526a507696636fce7c8f25dcc41586197a215cf2137955b498fc82ca76c.jpg` | Sarcophagus image is coherent and correctly oriented. |
| 23 | 102 | handout | `assets__76216221d1c4ed443deccf0a9e64c82ea0084ffc07ae033af3b43e69242b1b84.jpg` | Green cave/column image is coherent. |
| 24 | 103 | handout | `assets__bbcf13fecd9ade245d04db78356787f798176f58c9eb9b69c27d4936f6e888ba.jpg` | Fiery landscape is coherent and fully framed. |
| 25 | 104 | map | `assets__2594c936ac511e9594fccbbc79e2a9acdb7ad0475baec5fbf0640a4dfb24ea91.jpg` | Geographic map is upright with intact boundaries and labels. |
| 26 | 105 | map | `assets__b29535e0fb701c4072cd0198c39ef9f101871c5817bdf5b96e42794a14b18335.jpg` | Island/satellite map has intact numbered labels, circles, and scale. |
| 27 | 106 | map | `assets__adb4ff51bd5ebff464834e0fb324310c281eb20d2c4b0f4e82d1fbaf3ef72541.jpg` | Narrow scale-bar graphic is readable and correctly framed. |
| 28 | 106 | map | `assets__f7ce778cc1eb05cb6fef0f26457d06e68019ee30c76a5723f259dc82b89b321d.jpg` | West Wing floor plan has intact lines and readable labels. |
| 29 | 107 | map | `assets__e1c168ca34db2f98a27391e749f08a0fcdda832034d68e5fd0fbc38b00f584dc.jpg` | Chapel/East Wing plan has intact paths and labels. |
| 30 | 108 | map | `assets__9edcd9b27c46e8d689d4baeff43a55497376a581d87cf1e9ad8a0ea9dd63c28a.jpg` | West Wing/administration plan is coherent and correctly oriented. |
| 31 | 109 | map | `assets__00d84a08f0f7ef0b634da16d22f1832b3e099350a451425c5b2642428fe8f4b9.jpg` | East Wing/attic plan and Heroin Addict illustration are complete. |
| 32 | 110 | map | `assets__7eb3303bc8a34e16d5891aa781a21297a022e028c029fa8e0d0549f445703fe5.jpg` | Secret Underground map has coherent labels and scale. |
| 33 | 111 | full page | `assets__74f6d8049985378c8c5cc3f846b06982da3a39de05975dc31880f024e649d7a6.jpg` | Marco character sheet is full-frame, upright, and readable. |
| 34 | 113 | full page | `assets__00f35cb2535f45bfce6b8cc61c4bbf9fd5a493f2f63995a5608f14edfabfb782.jpg` | Corrina character sheet is full-frame, upright, and readable. |
| 35 | 115 | full page | `assets__ee6f908e8a15d1ee0f9f8a976427f1050ceef9810642f5ddfe1d172a0189bc3c.jpg` | Enoch character sheet is full-frame, upright, and readable. |
| 36 | 117 | full page | `assets__9407122d0650698a811b6096285828cf7fbe43efe74d3476c51995efec9dca01.jpg` | Peter character sheet is full-frame, upright, and readable. |
| 37 | 119 | full page | `assets__36e2c03c86a9b35dab62baf48f2e1d2e4fc0f77811173ca7acf8d7c44944d070.jpg` | Ku Hyeon character sheet is full-frame, upright, and readable. |
| 38 | 121 | full page | `assets__4b6c6dc23113457bf08f7aacf67bb8f009ab2aa193fbce921509695a6e261f5a.jpg` | Blank character sheet preserves the complete intended form layout. |
| 39 | 124 | back cover | `assets__378fea507e1df5929a90f53f99486fbba8da5b3f4ebe8c8ec3695c9a1621b345.png` | Back-cover quote, body text, and logos are intact; no clipping. |

## Required special findings

- p1 front cover: directly inspected as priority row 1 and within contact sheet 1; full green/black cover composition, title, quote, and logos are intact.
- p80 source render: directly inspected at original resolution; `1700x2200` at `200 DPI`; title `Marco's Intro Script`, handout #13, printed script, and handwritten note are present. The handwritten note visibly includes `Hey Marco Babez`; the exact text proof occurs once in the Candidate C text and manifest owner block.
- p124 back cover: directly inspected as priority row 39 and within the terminal contact range; quote, body text, and both logos are intact.

## Defect summary, blockers, and next action

| Severity | Observed defects |
|---|---|
| P0 | None observed. |
| P1 | None observed. |
| P2 | None observed. |
| P3 | None observed. Source-intent details such as dark imagery or intentional map pixelation were coherent and were not treated as generated defects. |

Blockers: none for this bounded visual QA execution. Next action: orchestrator integrates this receipt and performs the separately governed review/acceptance steps; this receipt does not issue a release decision.

## Verdict

`PASS_FULL_VISUAL_QA`

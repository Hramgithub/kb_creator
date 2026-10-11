# Luna/high bounded visual-QA receipt: Viral Step 7 MASTER_EN

- Assignment: `sol_orchestrator_viral_step7_master_en_full_visual_qa_assignment_20260902.md`
- Assignment SHA-256: `160C18B7E3BE63A0E33EC65E8C541A90017147B4B4DF032EC6155F456D68058D`
- Role: `gpt-5.6-luna` / bounded QA / high
- Scope: frozen candidate A visual QA only; no build, regeneration, repair,
  acceptance, release, Git, or source/config/candidate mutation.
- Candidate root: `kb_creator/working/viral/master_en/candidates/viral-master-en-candidate-20260901-a`
- Bundle root: `C:\Users\BogdanD\.codex\visualizations\2026\08\30\01a05392-3683-7292-b5d5-20ddc8b54a80\viral-master-en-visual-qa-bundle-dry-run-20260902-v2`
- Result: `BLOCKED`
- Verdict: `BLOCKED`
- Assignment state: blocked at direct priority-original visual-inspection gate.
- Orchestrator policy owner: `gpt-5.6-sol` / medium; ownership remains with the orchestrator.
- Scoped override: `none`.
- Timestamp: `2026-09-02T00:30:18+03:00` (Europe/Moscow)
- Elapsed time: approximately 25 minutes from QA start to receipt creation.
- Token use: unavailable.

## Frozen identities and preflight

All frozen identities matched before inspection:

| Item | Expected SHA-256 | Observed | Result |
|---|---|---|---|
| Assignment | `160C18B7E3BE63A0E33EC65E8C541A90017147B4B4DF032EC6155F456D68058D` | same | PASS |
| Candidate `INVENTORY.json` | `EF28700403FFE5FC781D1004979B83DC4ACC5F743E93F02201820071211AC3F8` | same | PASS |
| Candidate `MASTER_EN.md` | `44303C5A0D2964469D6B6523EDF3CB4391194BC49E19DD10B3FB90CCB667DC62` | same | PASS |
| `VISUAL_QA_BUNDLE.json` | `055C063058A8A609021113F7E5600955D3927D1C5387705592EBED6A427B332A` | same | PASS |
| Bundle generator | `DCF89F275F415719F9F9D0026A43F1BC54B4B802938BBA02A911CF8D441E7B8A` | same | PASS |
| Bundle generator tests | `C1C8BD61B7EF72447A5F4B3C659BAD1D633385774D0508C8F3382F2AD189437B` | same | PASS |
| Engineering bundle receipt | `325E6766B8752C01D0F001895B332263072522C9C9848A1C37CC4DC53BB49611` | same | PASS |

Manifest counts matched: `123` candidate assets, `107` reader assets, `91`
visual-review units, `107` tiles, `27` contact sheets, `39` priority assets,
and `0` open generation errors. All listed paths existed, matched manifest
bytes/SHA-256, and resolved beneath their recorded root. The p80 render matched
SHA-256 `D3844343B305F01D84C00EA074FAD21C05CDF27E413FE9C3D6FCE5EFC9C138B0`,
`3,116,524` bytes, and `1700x2200` dimensions.

## Contact-sheet direct inspection (27/27)

Every row below was opened with `view_image` at `detail=original` and visually
checked for ordered labels, expected tile presence, blank/black/corrupt or
duplicated content, material semantic crop, aspect-ratio preservation, and
overview legibility. No P0/P1/P2 visual defect was observed.

| # | Manifest path | Direct visual observation | Verdict |
|---:|---|---|---|
| 1 | `contact_sheets/pages-001-004.png` | Four labeled tiles present and ordered; cover/logo/introduction assets visually intact. | PASS |
| 2 | `contact_sheets/pages-005-008.png` | Four labeled social-icon tiles present and ordered; intact and legible. | PASS |
| 3 | `contact_sheets/pages-009-012.png` | Four labeled Marco assets present and ordered; portraits/logo asset content intact. | PASS |
| 4 | `contact_sheets/pages-013-016.png` | Four labeled Corrina/Enoch assets present and ordered; portraits intact. | PASS |
| 5 | `contact_sheets/pages-017-020.png` | Four labeled Peter/Emmy/new-investigator assets present and ordered; intact. | PASS |
| 6 | `contact_sheets/pages-021-024.png` | Four labeled Gear/History/Perla assets present and ordered; intact. | PASS |
| 7 | `contact_sheets/pages-025-028.png` | Four labeled Perla signs/burning/Perla NPC assets present and ordered; intact. | PASS |
| 8 | `contact_sheets/pages-029-032.png` | Four labeled Perla NPC/Isola assets present and ordered; intact. | PASS |
| 9 | `contact_sheets/pages-033-036.png` | Four labeled Isola location assets present and ordered; intact. | PASS |
| 10 | `contact_sheets/pages-037-040.png` | Four labeled Isola hospital-location assets present and ordered; intact. | PASS |
| 11 | `contact_sheets/pages-041-044.png` | Four labeled overlook/catacombs/temple/epilogue assets present and ordered; intact. | PASS |
| 12 | `contact_sheets/pages-045-048.png` | Four labeled cinematic/expanded-ending/appendix assets present and ordered; intact. | PASS |
| 13 | `contact_sheets/pages-049-052.png` | Four labeled appendix/catacomb/new-rules assets present and ordered; intact. | PASS |
| 14 | `contact_sheets/pages-053-056.png` | Four labeled paranormal/mythos/reliquae assets present and ordered; intact. | PASS |
| 15 | `contact_sheets/pages-057-060.png` | Four labeled reliquae/handout assets present and ordered; intact. | PASS |
| 16 | `contact_sheets/pages-061-064.png` | Four labeled handout 05–08 assets present and ordered; text/screenshots visually intact. | PASS |
| 17 | `contact_sheets/pages-065-068.png` | Four labeled map/handout assets present and ordered; map and hospital plan legible. | PASS |
| 18 | `contact_sheets/pages-069-072.png` | Four labeled handout 28–31 assets present and ordered; intact. | PASS |
| 19 | `contact_sheets/pages-073-076.png` | Four labeled handout 32–35 assets present and ordered; intact. | PASS |
| 20 | `contact_sheets/pages-077-080.png` | Four labeled handout 36–39 assets present and ordered; intact. | PASS |
| 21 | `contact_sheets/pages-081-084.png` | Four labeled Keeper-map assets present and ordered; maps/scale strip visually intact. | PASS |
| 22 | `contact_sheets/pages-085-088.png` | Four labeled Keeper-map assets present and ordered; map details/labels intact. | PASS |
| 23 | `contact_sheets/pages-089-092.png` | Four labeled pregen Marco/Corrina assets present and ordered; sheets/backgrounds intact. | PASS |
| 24 | `contact_sheets/pages-093-096.png` | Four labeled pregen Enoch/Peter assets present and ordered; sheets/backgrounds intact. | PASS |
| 25 | `contact_sheets/pages-097-100.png` | Four labeled pregen Ku-Hyeon/blank assets present and ordered; sheets/backgrounds intact. | PASS |
| 26 | `contact_sheets/pages-101-104.png` | Four labeled blank-background/merchandise assets present and ordered; intact. | PASS |
| 27 | `contact_sheets/pages-105-107.png` | Three labeled merchandise/QR/back-cover assets present and ordered; back cover visually clean. | PASS |

## Priority-original inspection (0/39 direct opens; blocked)

The assignment requires each `original_candidate_path` to be opened directly
from candidate A with `view_image(detail=original)`. Every attempted direct
candidate-A call failed before image access with `os error 5: Access denied`.
No copy, proxy, alternate render, screenshot, ACL change, or other bypass was
used. Therefore these rows are not visual verdicts and remain blocked.

| # | Asset id | Page | Role | Candidate path | Direct verdict |
|---:|---|---:|---|---|---|
| 1 | `viral-render-cover-front` | 1 | `front_cover` | `assets/bf086d551d421ea23a91bd0e18e919f183ea29b6476f149b0f75c43fdc3df643.png` | BLOCKED: os error 5 |
| 2 | `viral-accepted-2ebda31f091167d0746cefffb0ba817e95c00683579e25b8ff124275717688ec` | 53 | `full_page` | `assets/2ebda31f091167d0746cefffb0ba817e95c00683579e25b8ff124275717688ec.jpg` | BLOCKED: os error 5 |
| 3 | `viral-accepted-9cddc3fc484dffdcce7654b3ebc058b362dbb265508a64d64d7485b33dc600c8` | 69 | `map` | `assets/9cddc3fc484dffdcce7654b3ebc058b362dbb265508a64d64d7485b33dc600c8.jpg` | BLOCKED: os error 5 |
| 4 | `viral-accepted-9ee3d23cac4831e4230386f671d228d7a53b336310983f967eada4f3d2677ad8` | 74 | `handout` | `assets/9ee3d23cac4831e4230386f671d228d7a53b336310983f967eada4f3d2677ad8.jpg` | BLOCKED: os error 5 |
| 5 | `viral-accepted-b1b7888cf28240790d1fd7fdc5621da9fe159c9442ec0f3bfa7f45243319cfea` | 74 | `handout` | `assets/b1b7888cf28240790d1fd7fdc5621da9fe159c9442ec0f3bfa7f45243319cfea.jpg` | BLOCKED: os error 5 |
| 6 | `viral-accepted-f796716cd86ee8580b1d2cd8552d89cbf29f989bc8eae6be386ffa2528dc078b` | 75 | `handout` | `assets/f796716cd86ee8580b1d2cd8552d89cbf29f989bc8eae6be386ffa2528dc078b.jpg` | BLOCKED: os error 5 |
| 7 | `viral-accepted-2a60f183499c0a1a5f3bd353949a7efc2a389d5fbd98782e79e53d346d9c390f` | 75 | `handout` | `assets/2a60f183499c0a1a5f3bd353949a7efc2a389d5fbd98782e79e53d346d9c390f.jpg` | BLOCKED: os error 5 |
| 8 | `viral-accepted-8dcb6eee3da06a699ff2ac68c0b32338209a8abad3327bf0c8e246c2722dc76e` | 76 | `handout` | `assets/8dcb6eee3da06a699ff2ac68c0b32338209a8abad3327bf0c8e246c2722dc76e.jpg` | BLOCKED: os error 5 |
| 9 | `viral-accepted-826e5103327297822e6270444f8d57d02a135ffbc2d246ffbdb5788d297fd55a` | 77 | `map` | `assets/826e5103327297822e6270444f8d57d02a135ffbc2d246ffbdb5788d297fd55a.jpg` | BLOCKED: os error 5 |
| 10 | `viral-accepted-8dfcf412070881aa81b8933eeb329d7409edbe1316329701bb605c9dab835d65` | 78 | `map` | `assets/8dfcf412070881aa81b8933eeb329d7409edbe1316329701bb605c9dab835d65.jpg` | BLOCKED: os error 5 |
| 11 | `viral-accepted-5246e2c434242d2ddea6226d861d9608f5b6afa86230da5ad3b6d01553bb4ca5` | 81 | `handout` | `assets/5246e2c434242d2ddea6226d861d9608f5b6afa86230da5ad3b6d01553bb4ca5.jpg` | BLOCKED: os error 5 |
| 12 | `viral-accepted-2e49f854b389f6c5cf89bced8318e197b6e79fd53d47dfa5dd64b0dcd697bbcc` | 82 | `handout` | `assets/2e49f854b389f6c5cf89bced8318e197b6e79fd53d47dfa5dd64b0dcd697bbcc.jpg` | BLOCKED: os error 5 |
| 13 | `viral-accepted-06a2c68cc38d4904595e16d0153d127eb08ae61c189a613f269a120de5233201` | 94 | `handout` | `assets/06a2c68cc38d4904595e16d0153d127eb08ae61c189a613f269a120de5233201.jpg` | BLOCKED: os error 5 |
| 14 | `viral-accepted-affb03a14eabd3ce60d78047279316ebde282a079528b6e00067698ebed92715` | 95 | `handout` | `assets/affb03a14eabd3ce60d78047279316ebde282a079528b6e00067698ebed92715.jpg` | BLOCKED: os error 5 |
| 15 | `viral-accepted-373a4c9272242f27df9f3410b860e7bc5af602f17d1f08115649653754aad884` | 96 | `handout` | `assets/373a4c9272242f27df9f3410b860e7bc5af602f17d1f08115649653754aad884.jpg` | BLOCKED: os error 5 |
| 16 | `viral-accepted-5c03c3f42abbf1962a78d589d00014a6aac425db8b061cce69995930bd33d8b4` | 97 | `handout` | `assets/5c03c3f42abbf1962a78d589d00014a6aac425db8b061cce69995930bd33d8b4.jpg` | BLOCKED: os error 5 |
| 17 | `viral-accepted-217633ad4ab84de07789ba9c47d7c00ee382de486902cf967330d5d94061e8b5` | 98 | `handout` | `assets/217633ad4ab84de07789ba9c47d7c00ee382de486902cf967330d5d94061e8b5.jpg` | BLOCKED: os error 5 |
| 18 | `viral-accepted-c34aabc5bd16dfcb318cad3a11df583f9f15d4778f488832af69d182dc9d8201` | 99 | `handout` | `assets/c34aabc5bd16dfcb318cad3a11df583f9f15d4778f488832af69d182dc9d8201.jpg` | BLOCKED: os error 5 |
| 19 | `viral-accepted-faaf56706aeb8cc15c6cfeb89bf7731b313ccdfde78f28b12da65b123d355bcd` | 100 | `handout` | `assets/faaf56706aeb8cc15c6cfeb89bf7731b313ccdfde78f28b12da65b123d355bcd.jpg` | BLOCKED: os error 5 |
| 20 | `viral-accepted-84f3fbba13df63026fc147880fa903b708f67969bb85a2e8ffd7ae95bc921172` | 100 | `handout` | `assets/84f3fbba13df63026fc147880fa903b708f67969bb85a2e8ffd7ae95bc921172.jpg` | BLOCKED: os error 5 |
| 21 | `viral-accepted-d18f3a9358fcdda6d5f56178aa99b37609c72d286a380e71c4189337c1a9c5ae` | 101 | `handout` | `assets/d18f3a9358fcdda6d5f56178aa99b37609c72d286a380e71c4189337c1a9c5ae.jpg` | BLOCKED: os error 5 |
| 22 | `viral-accepted-4e663526a507696636fce7c8f25dcc41586197a215cf2137955b498fc82ca76c` | 101 | `handout` | `assets/4e663526a507696636fce7c8f25dcc41586197a215cf2137955b498fc82ca76c.jpg` | BLOCKED: os error 5 |
| 23 | `viral-accepted-76216221d1c4ed443deccf0a9e64c82ea0084ffc07ae033af3b43e69242b1b84` | 102 | `handout` | `assets/76216221d1c4ed443deccf0a9e64c82ea0084ffc07ae033af3b43e69242b1b84.jpg` | BLOCKED: os error 5 |
| 24 | `viral-accepted-bbcf13fecd9ade245d04db78356787f798176f58c9eb9b69c27d4936f6e888ba` | 103 | `handout` | `assets/bbcf13fecd9ade245d04db78356787f798176f58c9eb9b69c27d4936f6e888ba.jpg` | BLOCKED: os error 5 |
| 25 | `viral-accepted-2594c936ac511e9594fccbbc79e2a9acdb7ad0475baec5fbf0640a4dfb24ea91` | 104 | `map` | `assets/2594c936ac511e9594fccbbc79e2a9acdb7ad0475baec5fbf0640a4dfb24ea91.jpg` | BLOCKED: os error 5 |
| 26 | `viral-accepted-b29535e0fb701c4072cd0198c39ef9f101871c5817bdf5b96e42794a14b18335` | 105 | `map` | `assets/b29535e0fb701c4072cd0198c39ef9f101871c5817bdf5b96e42794a14b18335.jpg` | BLOCKED: os error 5 |
| 27 | `viral-accepted-adb4ff51bd5ebff464834e0fb324310c281eb20d2c4b0f4e82d1fbaf3ef72541` | 106 | `map` | `assets/adb4ff51bd5ebff464834e0fb324310c281eb20d2c4b0f4e82d1fbaf3ef72541.jpg` | BLOCKED: os error 5 |
| 28 | `viral-accepted-f7ce778cc1eb05cb6fef0f26457d06e68019ee30c76a5723f259dc82b89b321d` | 106 | `map` | `assets/f7ce778cc1eb05cb6fef0f26457d06e68019ee30c76a5723f259dc82b89b321d.jpg` | BLOCKED: os error 5 |
| 29 | `viral-accepted-e1c168ca34db2f98a27391e749f08a0fcdda832034d68e5fd0fbc38b00f584dc` | 107 | `map` | `assets/e1c168ca34db2f98a27391e749f08a0fcdda832034d68e5fd0fbc38b00f584dc.jpg` | BLOCKED: os error 5 |
| 30 | `viral-accepted-9edcd9b27c46e8d689d4baeff43a55497376a581d87cf1e9ad8a0ea9dd63c28a` | 108 | `map` | `assets/9edcd9b27c46e8d689d4baeff43a55497376a581d87cf1e9ad8a0ea9dd63c28a.jpg` | BLOCKED: os error 5 |
| 31 | `viral-accepted-00d84a08f0f7ef0b634da16d22f1832b3e099350a451425c5b2642428fe8f4b9` | 109 | `map` | `assets/00d84a08f0f7ef0b634da16d22f1832b3e099350a451425c5b2642428fe8f4b9.jpg` | BLOCKED: os error 5 |
| 32 | `viral-accepted-7eb3303bc8a34e16d5891aa781a21297a022e028c029fa8e0d0549f445703fe5` | 110 | `map` | `assets/7eb3303bc8a34e16d5891aa781a21297a022e028c029fa8e0d0549f445703fe5.jpg` | BLOCKED: os error 5 |
| 33 | `viral-accepted-74f6d8049985378c8c5cc3f846b06982da3a39de05975dc31880f024e649d7a6` | 111 | `full_page` | `assets/74f6d8049985378c8c5cc3f846b06982da3a39de05975dc31880f024e649d7a6.jpg` | BLOCKED: os error 5 |
| 34 | `viral-accepted-00f35cb2535f45bfce6b8cc61c4bbf9fd5a493f2f63995a5608f14edfabfb782` | 113 | `full_page` | `assets/00f35cb2535f45bfce6b8cc61c4bbf9fd5a493f2f63995a5608f14edfabfb782.jpg` | BLOCKED: os error 5 |
| 35 | `viral-accepted-ee6f908e8a15d1ee0f9f8a976427f1050ceef9810642f5ddfe1d172a0189bc3c` | 115 | `full_page` | `assets/ee6f908e8a15d1ee0f9f8a976427f1050ceef9810642f5ddfe1d172a0189bc3c.jpg` | BLOCKED: os error 5 |
| 36 | `viral-accepted-9407122d0650698a811b6096285828cf7fbe43efe74d3476c51995efec9dca01` | 117 | `full_page` | `assets/9407122d0650698a811b6096285828cf7fbe43efe74d3476c51995efec9dca01.jpg` | BLOCKED: os error 5 |
| 37 | `viral-accepted-36e2c03c86a9b35dab62baf48f2e1d2e4fc0f77811173ca7acf8d7c44944d070` | 119 | `full_page` | `assets/36e2c03c86a9b35dab62baf48f2e1d2e4fc0f77811173ca7acf8d7c44944d070.jpg` | BLOCKED: os error 5 |
| 38 | `viral-accepted-4b6c6dc23113457bf08f7aacf67bb8f009ab2aa193fbce921509695a6e261f5a` | 121 | `full_page` | `assets/4b6c6dc23113457bf08f7aacf67bb8f009ab2aa193fbce921509695a6e261f5a.jpg` | BLOCKED: os error 5 |
| 39 | `viral-render-cover-back` | 124 | `back_cover` | `assets/378fea507e1df5929a90f53f99486fbba8da5b3f4ebe8c8ec3695c9a1621b345.png` | BLOCKED: os error 5 |

## Explicit requirements and coverage

- p1 `viral-render-cover-front`: contact-sheet overview tile visually shows the
  intended front cover; direct priority-original inspection was blocked.
- p80 `p80/p080.png`: opened with `view_image(detail=original)`; the handwritten
  salutation visibly reads `Hey Marco Babez` (the spelling is `Babez`).
- p124 `viral-render-cover-back`: contact-sheet overview tile visually shows a
  clean back cover; direct priority-original inspection was blocked.
- Candidate text: read-only exact search found `Hey Marco Babez` exactly once;
  the `viral-handout-13` owner block contains the exact visible text once.
- Manifest coverage: `91` visual-review units, `107` reader rows, `107` tiles,
  and `27` ordered sheets were read/checked. Reader ordinals 001–107 are
  represented by the overview sequence. One special requirement is declared,
  and the p80 requirement was addressed independently above. No metadata
  anomaly was found; the pending external-QA status in the manifest is not an
  inspection claim.

## Candidate immutability after inspection

Final read-only hash check after all inspection attempts:

| Candidate file | Frozen SHA-256 | Post-inspection SHA-256 | Result |
|---|---|---|---|
| `INVENTORY.json` | `EF28700403FFE5FC781D1004979B83DC4ACC5F743E93F02201820071211AC3F8` | same | UNCHANGED |
| `MASTER_EN.md` | `44303C5A0D2964469D6B6523EDF3CB4391194BC49E19DD10B3FB90CCB667DC62` | same | UNCHANGED |

## Blocker and next action

The required `view_image(detail=original)` direct reads of all 39 candidate-A
priority originals, including mandatory p1 and p124, are blocked by filesystem
access (`os error 5`, Access denied). This prevents a full visual-QA verdict;
it is not a content defect finding. Next action is for the orchestrator to
restore a read-only path that `view_image` can access, then re-run this exact
39-row direct inspection without changing frozen candidate/bundle identities.

No release, acceptance, or repair decision is made by this receipt.

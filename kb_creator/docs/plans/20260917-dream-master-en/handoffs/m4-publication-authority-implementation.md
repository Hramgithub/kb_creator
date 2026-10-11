# M4 receipt: Number 7 Dream publication authority

## Receipt

- Goal: `20260917-dream-master-en`; milestone: M4.
- Role: bounded publication authority authoring and validation.
- Policy orchestrator: main-chat `gpt-5.6-sol`, medium; ownership remains with orchestrator.
- Assignment state: `platform-unverified`.
- Scoped override: none.
- Timestamp: `2026-09-18T00:28:54+03:00`.
- Elapsed time: approximately 9 minutes.
- Token use: unavailable.
- Result: **PASS**. Declarative v1 authority and the generic identity-bound contract are authored from M3 specification; all 19 reader assets match accepted bytes. No Number 7 Dream Python was added.
- Blockers: none. The bundled Python environment has no pytest module on its default import path; focused tests passed after adding the repository's existing `.tools/python-test-deps` directory to that process's import path. No dependencies were installed.
- Next action: orchestrator runs publication preflight and only Stage 10, then stops at `awaiting_master_en_acceptance`.

## Scope and changed files

Created under `kb_creator/inputs/number-7-dream/publication/v1/`:

- `publication-blueprint.json`
- `configs/master_en.json`
- `configs/master_ru.json`
- `configs/html.json`
- `configs/docx.json`
- `configs/pdf.json`
- `configs/package.json`
- `configs/artview/profile.json`
- `configs/artview/source-graph.json`
- `configs/artview/assets/<19 accepted SHA-256 names>.jpg`

Created by `author_scenario_publication_contract.py` into its previously absent target:

- `kb_creator/contracts/number-7-dream.publication.json`

This receipt is the only other file in M4 scope. No files under `working/`, pipeline code/tests, canonical plan/context/status, or other project paths were edited.

## Identity and verification evidence

- Generic author command completed with state `authored`, scenario `number-7-dream`, schema `kb_creator.scenario_publication_contract.v1`; `--config-root .` was used so all blueprint paths resolve from repository root.
- Draft 2020-12 schema and instance validation passed for the blueprint, generated contract, and ArtView profile.
- The generated contract's seven config identities and terminology identity all reopened with matching byte counts and SHA-256 values (8 identity records total).
- Source graph: 6,292 bytes, SHA-256 `7A0CFE3358D0D8E12AEA01FF64D4668AFF5C0B1046E83016F1F18D73E504B5B6`; all four ArtView source-template slots bind these exact bytes.
- 19 Markdown image references matched the frozen M3 reader set exactly. Each source asset hash was checked against accepted `content/ASSET_MANIFEST.json` before copying; copied bytes/hashes were rechecked. Pillow decoded all 19 and confirmed specified dimensions.
- Exactly 19 accepted reader assets are included. The ten page-18 `reference_only` statblock snippets are excluded from the ArtView asset tree.
- All 19 profile rows and source graph artifacts correspond in table order. No page-18 asset enters the profile.
- Focused tests: `test_author_scenario_publication_contract.py` and `test_scenario_artview_v3.py`: **79 passed, 1 skipped, 255 subtests passed**.
- `git status --short` shows the new contract and input tree as untracked, not ignored; these are eligible for a future explicit commit. No commit or push was made.
- Scenario-specific Python file count in the new input tree: 0.

## Exact text identities

| File | Bytes | SHA-256 |
|---|---:|---|
| `publication-blueprint.json` | 4,098 | `D0378A9C0D6F26D50432BABA2F78683A21497D8F3A5747B9A833939D03A006A6` |
| `configs/master_en.json` | 557 | `F20821920216F6C0DA3A8893D4E11DA0C603D330DF2968E28D6614CC63A574A1` |
| `configs/master_ru.json` | 78 | `C72AB02C24A7B079AE1C0B858D6015F6F3CC324A8391971289708BC90FD03FA6` |
| `configs/html.json` | 569 | `9A11BB8D306A85FD8975A605517F366E5F75202111DCE02DFFD5D9FDE5627039` |
| `configs/docx.json` | 1,550 | `2AF5C668263A2CF4333E734151C6D21E2459E4800506CABE9880A6DCBEDF29B2` |
| `configs/pdf.json` | 45 | `8C9875AAD9AA0CAF46642E056129477D7235A0F434B73438D612D142238F309A` |
| `configs/package.json` | 49 | `5643406F004E4996A3AC42640DB5FE72EE16CA9DF566B3202639CA50C050EA7A` |
| `configs/artview/profile.json` | 22,256 | `FC241CEBAD4D6C21A3D33A2F527571698116ADAC7A57C5BC35DC7D0114350D9B` |
| `configs/artview/source-graph.json` | 6,292 | `7A0CFE3358D0D8E12AEA01FF64D4668AFF5C0B1046E83016F1F18D73E504B5B6` |
| `kb_creator/contracts/number-7-dream.publication.json` | 5,011 | `EB23016E8890EB9D31F6338D8D9F395E49E537EF6F1D0ECDC728711BDCA207B8` |

## Reader asset SHA-256 set

All files are `configs/artview/assets/<sha256>.jpg`; the filename stem is the full lowercase SHA-256 of the exact copied bytes:

`55CA597755B7DF71C1E3699353265EE4AD9771EBBDB920410317E7073F6284FE`,
`8FC42816BF72BEDA6938FAAD5A1AFF6DEA6DE1BEF286EE8D8822A8DAC55BBBD6`,
`D546EF251ACE98DF9136EA8C332883B06594C7082D32ED1AC80C4DBD915D9523`,
`FFD474F4A049B1968C6F7B5F9068019B5CDEC558E69B9A1E995AA21663395857`,
`8D4E75A0CD6C3098CFD7B84B4FB603395E7269EC4249B8AB05734751A58EDD70`,
`456C573FB9955C8A3312CADF47A7559255D3416427B764E874D8D8D7D2B6A35C`,
`833474CC789C6F5E00034FE72DD8AD95C5C148DD553D5451056A0BE134473525`,
`BA5B7C947407C8409B5353E7A25196A98BE9E9DC47A786EE0376CD8BC23348B4`,
`F16BFB5BBC3E13437865969CF46FECB192EDEEAB07978A0E1DABF1C60ED8345B`,
`5F84FC66111294AF52199ED1C80E48D71F9F8DDB412D52EE2CF42D04E31F7E4D`,
`9F377A1D675FF226C5405C3A6968540B6A32221C151152C82E7770A708F2B981`,
`2E39199DC3787B0600AC4F9843FD02DE5F88DFB05BE59ACD833B9A17B5735421`,
`7D73DFEA3BAA03B388A63F836C0CA43F9238EFEE255AB26FFCDB49BFACF79890`,
`F21773FEB120405ACF2244939EA196833341DD24A2933AB9F08424AA1E44E5AC`,
`8CC466F9543AD6EB3BE419B505950EB16CD7B0CF0B3B33CFA0162BFA0F4C97A9`,
`F51F17C46EF8227AF096809E89EB784E968A715088739DC2B0B7F5778076E743`,
`6F1393BC7DC691B0B8F2A2039D1C502AEA957D8B8B5617DEB0E1A2A8CD804165`,
`30F29EF0AFD70573F4F5411B933170A0FAAAFEC268E1842BB6DED414C7AD1F95`,
`A334E31185E6DCB3C4CA4FF2F900EFFF0F4E77D7CD0C446FD7E4BA0392C35E1A`

No MASTER_EN preflight or publication run was performed in M4; these remain M5 actions.

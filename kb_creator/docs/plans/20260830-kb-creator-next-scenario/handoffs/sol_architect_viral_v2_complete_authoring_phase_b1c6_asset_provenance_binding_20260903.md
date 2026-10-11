# Sol architecture receipt — Viral v2 B1c6 asset-provenance input binding

## Receipt metadata

- Goal id: `20260830-kb-creator-next-scenario`.
- Step id: `7-v2-complete-publication-authoring / B1c6-asset-provenance-input-binding`.
- Role: `nri-architect`; repository-policy assignment `gpt-5.6-sol` / high.
- Actual platform model and effort: unavailable; the assigned architecture
  contract was followed.
- Orchestrator policy owner: main chat, `gpt-5.6-sol` / medium. Ownership did
  not transfer.
- Assignment state: `matched`; platform runtime identity remains unverified.
- Scoped override: exact task packet
  `TASK_PACKET_architect_viral_v2_complete_authoring_phase_b1c6_asset_provenance_binding_20260903.md`,
  observed SHA-256
  `88B45E9F986E06B5BB73CF5756DA54A8CFB860C999EC028E54F57E6A1E863B98`.
  The packet intentionally supplied no expected packet hash because the main
  chat's local approval backend failed during hashing.
- Timestamp: `2026-09-03T18:56:13.5917634+03:00` (Europe/Moscow).
- Elapsed time: approximately 50 minutes.
- Token use: unavailable.
- Result: architecture and diagnosis complete; no implementation was made.

## Scope and state boundary

This receipt is the only file created. I did not edit the author, builder,
verifier, tests, canonical plan/context/status/release files, Git state, source,
accepted reconstruction, frozen v1 config, canonical v2 config, candidates,
renders, review bundles, MASTER_EN, MASTER_RU, HTML, PDF, or any of the nine
protected historical candidate/staging roots.

The approved B1c4 exact declaration-identity gate and B1c5 exact visual-review
declarations remain unchanged. B1c6 is strictly the deeper source/input binding
of the already-approved three-kind provenance union. It does not reopen the
16/100/9 classification, replacement graph, migration identity, review rows,
or binary declaration identity.

## Hashes and identities checked

| Item | SHA-256 / identity |
| --- | --- |
| Assigned B1c6 packet | `88B45E9F986E06B5BB73CF5756DA54A8CFB860C999EC028E54F57E6A1E863B98` |
| B1c4 independent approval | `BBB983ADD8E97885B0B9FCF0226145F262BD857127853F9CCC33706E82FC2EED` |
| B1c5 independent approval | `05B4573DF3FBE1EE7ACF31711AEFDBD44BB68A2448F90CDF494A332F4D649D82` |
| author / builder / verifier | `3DA02ADF17E2224C86A1418D18ECB06754E1FC6CD628717C1652EA315968FE1C` / `8055F7B355EB711474398C84263521C4B8001D852B2B53987523D5CBE9C4D6DD` / `2CFEE758C2EDBC5F445E864EDB46E366EB07E7E19D6E19FBD64D6A99E9FF2ED5` |
| author / builder / verifier tests | `58ED6C9FF6FC5A67130830F3F4731A5D68695E6F7E6877B0D6E09786D51D5EAE` / `CE38BA49E996C414166F345D3127FC6303DEFD4949C5678D966F414D340B8555` / `61566BD4C76344CE36ACE6DC97FE94DD4E65A68176AACD21E8C11C28BFD195FA` |
| frozen v1 config | `C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30` |
| source PDF | 20,718,150 bytes; `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05` |
| accepted reconstruction package | 377 files; 41,079,424 bytes; inventory `68C17FB765A89C6146398868E61F1F6EB7B2FE4EAFBA8C2C2C8F42260BBDBA83` |
| accepted package asset manifest | `914A2C8B46401830EDBDEADDDDA24C7A8C0B6442F2775C439A79CC5529D283E9` |
| comparison evidence | `5A4DB5DB697B1E483926AB1DAB387CB496EF0539DC76EAD51B830F5DCF1862F0` |
| comparison companion input manifest | `4BE80A51F01B552536B1D51C3F43ABA90EAD31D87006F8FBB3FD48DEC2A4182E`; embedded source identity equals the admitted PDF |

Builder and verifier independently recomputed the same accepted-package tuple
`(377, 41079424, 68C17F...BA83)`. The current authored projection recomputed as
`125 = 93 reader + 32 evidence_only`, with provenance exactly `16 Markdown +
100 visual region + 9 reviewed provisional full page`.

## Exact call paths and current comparisons

### Builder

1. `preflight()` lines 1231–1240 reads the temporary public v2 declaration.
2. `v2_config()` lines 406–501 validates the closed envelope, the approved
   B1c4 declaration/identity gate (lines 445–489), and B1c5 through
   `v2_visual_review_units()` (lines 498 and 504–547).
3. `v2_input_binding()` lines 587–614 binds the CLI source PDF and reconstruction
   tree, exact package inventory, all 124 page identities, excluded scope and
   source partition; then runs B1c3, A3, and migration in that order.
4. `v2_a3_validate()` lines 162–277 reaches the stale asset block only after
   event/payload/recovery/xref checks pass. Lines 265–270 require every asset to
   expose legacy `source_span_ids`, require each span to be unique, require
   `owner_kind == asset`, `owner_id == asset_id`, and classification
   `asset_reference_source`, then read legacy `reader_value` and `placement`.
5. The first predicate at line 267 fails because none of the 125 approved B1c4
   rows has top-level `source_span_ids`, producing
   `v2 asset provenance mismatch`.

### Independent verifier

1. `preflight()` lines 412–421 calls `v2_contract()` and then
   `v2_input_binding()` before any output operation.
2. `v2_contract()` lines 529–625 independently validates B1c4 and B1c5.
3. `v2_input_binding()` lines 719–744 independently binds the CLI inputs,
   package inventory, page identities, scope, source partition, B1c3, A3 and
   migration.
4. `v2_a3_validate()` lines 147–257 repeats the stale legacy asset contract at
   lines 246–252.
5. Its first predicate at line 248 fails for the same 125 rows, producing
   `E_V2_ASSET: provenance`.

The stale block compares these fields and sources:

| Comparison | Expected by stale A3 block | Current approved B1c4 source |
| --- | --- | --- |
| provenance carrier | nonempty unique `asset.source_span_ids` | closed discriminated `asset.provenance` |
| page | legacy `asset.page` used elsewhere in the same branch | canonical `asset.source_page`; `page` is absent |
| publication disposition | legacy Boolean `asset.reader_value` | `asset.disposition` = `reader` or `evidence_only` |
| asset source owner | partition span `owner_id == final asset_id` | the 16 reviewed marker spans retain logical ledger owner ids such as `viral-asset-logo`; final asset binding is the exact marker target/binary identity |
| non-text provenance | still requires a reconstruction text span | 100 exact comparison regions and 9 exact source-PDF full-page declarations intentionally have no text span |
| placement | legacy top-level `asset.placement` and event target | not authored yet; this is the next bounded seam, not B1c6 provenance |

## Root cause

The defect is validator field routing, not authored evidence. Phase A3's
pre-B1c4 rule assumes every asset is a Markdown-reference event with a text
span. B1c4 replaced that model for canonical assets with a closed three-kind
provenance union, but the deeper A3 input-binding loop was not branched to the
new schema. B1c4's scenario-specific declaration oracle proves that the author
emitted the approved row; it does not substitute for a generic recomputation
from the CLI-bound source PDF, reconstruction package, manifest, comparison
evidence, source partition and page bytes.

Adding `source_span_ids` to the author is not a valid fix:

- only 16 qualifying spans exist;
- their owner ids are logical source-ledger unit ids, not final content-addressed
  asset ids, so the next stale predicate would reject them;
- 100 visual-region assets and 9 provisional full-page assets have truthful
  non-text provenance and cannot acquire a source Markdown span without
  inventing evidence;
- adding `reader_value` or `page` would duplicate the approved canonical
  `disposition` / `source_page` fields; adding placement would improperly
  implement the next phase.

## Complete mismatch inventory

All 125 rows lack the three legacy top-level fields `source_span_ids`,
`reader_value`, and `placement`. Their exact stable-id partition is below; the
union of the three lists is the complete 125-row current provenance mismatch.
There are no `source_page` mismatches inside either the visual or provisional
variants.

### `markdown_image_reference` — 16

```text
viral-accepted-ed4012725c597dbcf6fca51e55faeb883a53f6f1d2c9ee7496c667460d37c860
viral-accepted-4592e580aba8b9bad7a83eb2acf44e0480005e48b034ecd1ac436860efdbd137
viral-accepted-6acc049ed2ad40ebed064312a87ddfce5a404f4fc2487ea1721c656ed541c419
viral-accepted-647b583cd53fbfdaab7ac6d9643a81bbd5145c125d628c7074b02db0c9f7888b
viral-accepted-eda9c6f6d6ef94ed41034cd12401547ed37101ef2f8b1ebf30d9602b87db71ab
viral-accepted-21704f0d57843965013f5eccfa36bcd64321dcc1513cd7d99dead8627d58994e
viral-accepted-b2ba43b7e57f4c9972780be961deab50d72ea311f795285da15712ba29b6e30e
viral-accepted-af48429e4ab502e7fc33a545039dab60a3e4e28a8c03a29f56ff57b9280cdd12
viral-accepted-9bd48830bceb21ed805a645dbeeff5c19b748ac1aecd5336836bb192b12ad746
viral-accepted-4fd93a36f8650d97b80a9bde287442646eb741abefad7f520761332c4ec28834
viral-accepted-bc2ae2b3751eaf9754f625794f2d4648a03308dc3dc1042add097cc3649306b0
viral-accepted-360213a4168164f71a9ff8980d5099fb9e2feccdd37c8f10abef0f67e9e107a1
viral-accepted-b90cb9a3752383888c733905588e9c3859b113e47f1f457057c72e33689a7585
viral-accepted-da0cac1c9c0c880a75d3be69c59e965d0b7b0f223f16a077072786c8af30083e
viral-accepted-7c83b1d4c5f1a22f691eb9d0cbe19c82392bd9144d6e60d5654ce4aed160a712
viral-accepted-694c04bf754533fd1ce84a80eb659bbcc7b0a9c314a1102ae0188eb2278618cf
```

Their exact `(span_id, logical owner_id)` sequence is:

```text
span-p003-002 viral-asset-logo
span-p006-002 viral-asset-hero
span-p006-004 viral-asset-summary
span-p007-004 viral-asset-youtube
span-p007-006 viral-asset-facebook
span-p007-008 viral-asset-instagram
span-p007-010 viral-asset-twitter
span-p007-012 viral-asset-patreon
span-p013-002 viral-asset-silhouette
span-p025-004 viral-asset-santina
span-p025-008 viral-asset-padre
span-p025-012 viral-asset-church
span-p031-002 viral-asset-city
span-p032-002 viral-asset-boat
span-p034-010 viral-asset-str
span-p040-002 viral-asset-morgue
```

All 16 spans are unique, have `owner_kind=asset` and
`classification=asset_reference_source`, match the declared page and exact
byte/character range, and contain one complete Markdown image marker whose
resolved target is the row's exact accepted-package binary.

### `visual_region` — 100

```text
viral-accepted-e1e2aa6964b45037691d92e4faf91dba6bbd411e409dc49c237f6b0e71e6ce85
viral-accepted-a1d83a711a4b7962110b1ba158b2d610043f1fa836e06458e675373094acd6c1
viral-accepted-aa51315c65b2339c22c6928a566dd2ade498b2afc817f9632cf30c09c5def4df
viral-accepted-d65de690f2341a83f4360d658e72d5fb916e7ae5bae952e366262017959f7fa6
viral-accepted-2a4ae067e92473cdad591d86e4d67066cb82094fc1251c23223a9c6561fb7089
viral-accepted-1ae78ddfdbcbd36dda84dcf3e34852206355f15827052b2714401493c4765bcb
viral-accepted-a5a54caa96d84e7f6df573ce0c5faa2e52e03213b89f22da03d043087b797201
viral-accepted-739a84561947691338ea011d7950446144e6156a4b5aba7924ab24a13b2c6d5f
viral-accepted-f76ae66f2313c44b030bb9cacce1023a95663ed4072a2d93ef8feca74c829004
viral-accepted-cfb0587698f77c07987b9d5d50de4bf64d42b0bd5fa13e7276a5163ba787faf1
viral-accepted-44587a041b63942e4703761b2c3065f459e5637a06e790447d0e0899c1d9a3f6
viral-accepted-7ad2d1b6d60fff832a4fce5ffa008151db46260faa9b29ec8db01d62fdaa1208
viral-accepted-46fe7137e80db64fce723c0f4eede22b676faedca5f1f476e964b8709ccf1449
viral-accepted-290e0d241064519a8e796429310676557b8a7e50bd2224341c7ba3d3de96ec54
viral-accepted-0964f307aef670888c91bfe78498d19a3f55cdd749f113d610a5b68bc64cf070
viral-accepted-327bcc22a7c9781d732803ea2fc0e492113453b1a130ab655debb0a1c4c4b24f
viral-accepted-16f390d7a4c0fc8856f4a878a164b11ec4e922c7df6fbb002e41e285a781d2a3
viral-accepted-207028087cb3e99a6c0dbe99049ecb40bbd982de2906e0210baf884e95a11d3d
viral-accepted-29f2728884eee4feeed62b6ce0e488219c96a5933f9f4cd30a3c46ce56ae0804
viral-accepted-b8b06ff00c57b039a57df97d088b2b256c0cdd6da30e1d8dc2a3629a5d42355c
viral-accepted-10c6ced92d46c2b55ec18eb2c0fba3a1c39fcb1bb29c39a8fce8ef24fad8f7a1
viral-accepted-222ccd9a31a25cadc0bfab40f4e037eb55b91ca7ee523fc5d9784f30407e4bfa
viral-accepted-b2744fe4663d98385eaee75a7b134b506b652617dd76356cf2bf717b9a90d152
viral-accepted-7a9686ecb0457b695002ce7b7daddcb9598b27e0d1501e10155e0c51f4eac85b
viral-accepted-f0ecf36564122d99452b953117ef61c8ae8aeb306459fd2ea1a2a9934d97c60e
viral-accepted-1627aa2f652faf9837044b35d8e54bd7ddfc6b6716e7e8141363b65a83f12c4f
viral-accepted-87d8a9e48a47663469f8ae771e291ed10f27cb13f6533d80bd3b569ad7c73ffd
viral-accepted-15de2b653d40f0f520a14e685938d7d58b3bb4c6d5db2f6e420b03d88ed360b0
viral-accepted-1a47e9a1f4a4ef0aba87607b159b901cc1c3898e5bd3a995ea0341d4f52e7cbd
viral-accepted-2ebda31f091167d0746cefffb0ba817e95c00683579e25b8ff124275717688ec
viral-accepted-29e9a40a1748fbb06877c65bfbd3c16682e154a09d72a746b2432bdc3c8114f7
viral-accepted-98252d0b2a10de10cb22e3ef50f6de0261b8c7ef0b4ec4f4a3911abb064e2cf2
viral-accepted-ba787578df65b06580708e25f66e319a5d76a80ff5717b05392d2c1c4470b394
viral-accepted-c708f914e6ddda12e62831135072daa4458f2c87c1a967527e91f55bec2e9591
viral-accepted-70a9e13d96917244309a9a76922f8ba27b551040a27811beecf83f3e180016be
viral-accepted-53643514b43e23269335df5656ebce5e201bf98fc34591b1211e50e38301f35d
viral-accepted-d03da367941f779022bca6764b8bb259602fbaf7ccb50ea2ba30d7e150ad3279
viral-accepted-5d704eecea2fd918c2d47310fb1a6095a34df16dd3866e218edace6c3f4147d1
viral-accepted-309b53074a068f89a601dce791376410b5ed348ca1073928019d49d74ef96dd4
viral-accepted-baa904e61a23aecf4b6f667d035c9755ff6321c6205caa0d97977704378464aa
viral-accepted-cca3f437517c905396426e243323b562cfce53af5f2f4ba92a1399c733065124
viral-accepted-2ff7daab27132cad277a1f7e73464f1fd79c9745ca924d91bf4acced6f2f1c6e
viral-accepted-8e99d6929ef4aa5cc62d603b24317a4c65b22fd9551a8c37c5cfff9aa239436d
viral-accepted-5623aa0891db1ac91963f27adb4c7f69f46cc3a60d6fee09267ef2f5cac8d7d4
viral-accepted-81953e331e0b27630c228051831a510c123801aa360c1f6d0fa82d66516ee677
viral-accepted-6e1d78ee26178218de74fd8203ef772eb3e8f4951ea6e419a0a00e25051b8237
viral-accepted-6877882f32d30021fa519a58f1ca4227258db799b33ee28e8a64dd07e88981b2
viral-accepted-0c41d57b4240303a0fc7b83715a7476b6cc294857da88b24a0200fe71c7d2dbf
viral-accepted-ffcd5ab4e6d1d1c53dcf5089955a6124d6e4951e63c941140b3204db1c7d733a
viral-accepted-2fbd31994da00cc5320dccf115f2aae8da89b5e5997e93ad5f853afbf13bad03
viral-accepted-dbe93023f78f2a8181d333207f407d3ada63c8f33a6f53889b4f3df7bc76a416
viral-accepted-9cddc3fc484dffdcce7654b3ebc058b362dbb265508a64d64d7485b33dc600c8
viral-accepted-9ee3d23cac4831e4230386f671d228d7a53b336310983f967eada4f3d2677ad8
viral-accepted-b1b7888cf28240790d1fd7fdc5621da9fe159c9442ec0f3bfa7f45243319cfea
viral-accepted-f796716cd86ee8580b1d2cd8552d89cbf29f989bc8eae6be386ffa2528dc078b
viral-accepted-2a60f183499c0a1a5f3bd353949a7efc2a389d5fbd98782e79e53d346d9c390f
viral-accepted-8dcb6eee3da06a699ff2ac68c0b32338209a8abad3327bf0c8e246c2722dc76e
viral-accepted-826e5103327297822e6270444f8d57d02a135ffbc2d246ffbdb5788d297fd55a
viral-accepted-8dfcf412070881aa81b8933eeb329d7409edbe1316329701bb605c9dab835d65
viral-accepted-5246e2c434242d2ddea6226d861d9608f5b6afa86230da5ad3b6d01553bb4ca5
viral-accepted-2e49f854b389f6c5cf89bced8318e197b6e79fd53d47dfa5dd64b0dcd697bbcc
viral-accepted-06a2c68cc38d4904595e16d0153d127eb08ae61c189a613f269a120de5233201
viral-accepted-affb03a14eabd3ce60d78047279316ebde282a079528b6e00067698ebed92715
viral-accepted-373a4c9272242f27df9f3410b860e7bc5af602f17d1f08115649653754aad884
viral-accepted-5c03c3f42abbf1962a78d589d00014a6aac425db8b061cce69995930bd33d8b4
viral-accepted-217633ad4ab84de07789ba9c47d7c00ee382de486902cf967330d5d94061e8b5
viral-accepted-c34aabc5bd16dfcb318cad3a11df583f9f15d4778f488832af69d182dc9d8201
viral-accepted-faaf56706aeb8cc15c6cfeb89bf7731b313ccdfde78f28b12da65b123d355bcd
viral-accepted-84f3fbba13df63026fc147880fa903b708f67969bb85a2e8ffd7ae95bc921172
viral-accepted-d18f3a9358fcdda6d5f56178aa99b37609c72d286a380e71c4189337c1a9c5ae
viral-accepted-4e663526a507696636fce7c8f25dcc41586197a215cf2137955b498fc82ca76c
viral-accepted-76216221d1c4ed443deccf0a9e64c82ea0084ffc07ae033af3b43e69242b1b84
viral-accepted-bbcf13fecd9ade245d04db78356787f798176f58c9eb9b69c27d4936f6e888ba
viral-accepted-2594c936ac511e9594fccbbc79e2a9acdb7ad0475baec5fbf0640a4dfb24ea91
viral-accepted-b29535e0fb701c4072cd0198c39ef9f101871c5817bdf5b96e42794a14b18335
viral-accepted-adb4ff51bd5ebff464834e0fb324310c281eb20d2c4b0f4e82d1fbaf3ef72541
viral-accepted-f7ce778cc1eb05cb6fef0f26457d06e68019ee30c76a5723f259dc82b89b321d
viral-accepted-e1c168ca34db2f98a27391e749f08a0fcdda832034d68e5fd0fbc38b00f584dc
viral-accepted-9edcd9b27c46e8d689d4baeff43a55497376a581d87cf1e9ad8a0ea9dd63c28a
viral-accepted-00d84a08f0f7ef0b634da16d22f1832b3e099350a451425c5b2642428fe8f4b9
viral-accepted-7eb3303bc8a34e16d5891aa781a21297a022e028c029fa8e0d0549f445703fe5
viral-accepted-74f6d8049985378c8c5cc3f846b06982da3a39de05975dc31880f024e649d7a6
viral-accepted-5d2410afd9a6593cdce0d7f0d411835cf4a726551a1b1e18b6f79d04ed42230b
viral-accepted-53c2775488f57c8e41f9d42648ecb8a1d30e9a1ce0de8d4108b7926ee26a3595
viral-accepted-00f35cb2535f45bfce6b8cc61c4bbf9fd5a493f2f63995a5608f14edfabfb782
viral-accepted-331f4d575265e02a4ba97b4e204dbbb20b648e9b62d44eb47ea11ab6998c00d3
viral-accepted-89e3eae7390f0ae27a8069bcf2d2aa2956a21047eeb7168a3fd49b0b7cbfc297
viral-accepted-ee6f908e8a15d1ee0f9f8a976427f1050ceef9810642f5ddfe1d172a0189bc3c
viral-accepted-92c65562fe49c02049e4b40e4a278b667e1361568455fdd89a724389a8d01d50
viral-accepted-66088dd8192e2a93f140eb9e11fadfed92b3869c509490199a35d272197ebfcb
viral-accepted-9407122d0650698a811b6096285828cf7fbe43efe74d3476c51995efec9dca01
viral-accepted-07982af9981b82074567f2fa5d976b00cb40a0331f01438352f9fd59fc864aa4
viral-accepted-fe4c839c1ff9b15dc4a9136f6969271a7a465fe642c77b38f456aa2af38fe0c3
viral-accepted-36e2c03c86a9b35dab62baf48f2e1d2e4fc0f77811173ca7acf8d7c44944d070
viral-accepted-9d7ebb95113ecd5d9114224cff873b14f2db563d61015978164a78e4ff05953f
viral-accepted-df1e018979c88b0737200c349889745eadfa119466dc40fb024779a0f8eb4730
viral-accepted-4b6c6dc23113457bf08f7aacf67bb8f009ab2aa193fbce921509695a6e261f5a
viral-accepted-1ae1543b9ff31ba9d7c4271ae01d86f05fb722c00e9f7851ce1dffc820aee3b8
viral-accepted-dd0c2d51431a4945f9f7d8293bc7b0b5e870f891dbe31d18c931926bffbb8d8b
viral-accepted-dcf1f2f6dd9540217155f01d5b03d965aedef98d965c2a33e987f0f5996eb166
```

All 100 independently resolved to one accepted-package manifest row keyed by
both `stored_path` and digest and one comparison block keyed by view/raw index/
source reference. Their top-level `source_page` equals the comparison block
page; declared bbox and canonical row/block hashes matched. Their common
comparison companion manifest independently binds the admitted PDF identity.

### `reviewed_provisional_full_page` — 9

```text
viral-render-cover-front
viral-provisional-map-ground-floor-basement-page-106
viral-provisional-map-ground-floor-basement-page-107
viral-provisional-pregen-marco-back-page-112
viral-provisional-pregen-corrina-back-page-114
viral-provisional-pregen-enoch-back-page-116
viral-provisional-pregen-peter-back-page-118
viral-provisional-pregen-ku-hyeon-back-page-120
viral-provisional-pregen-blank-back-page-122
```

All nine have `binary=null`, exact equality between provenance PDF identity,
document PDF identity and the CLI-bound PDF, `physical_page == source_page`,
zero-based page index `source_page - 1`, exact full MediaBox, and the approved
single-page 200-DPI PNG recipe. No provisional output bytes are required or
permitted at this checkpoint.

## Proposed generic contract

No author schema change is needed. The canonical asset row remains the approved
closed B1c4 shape:

```text
{asset_id, disposition, source_page, binary, provenance, migration_outcome}
```

The existing provenance union remains exactly the approved three variants. The
new behavior is a source-binding validator in each public implementation, not a
fourth author oracle and not a second spelling of any field.

### Mode selection and compatibility

1. Determine asset mode by closed row shape, never by `scenario_id`.
2. A collection is either entirely canonical (`provenance` rows) or entirely
   legacy fixture-compatible (`source_span_ids` rows). Mixed mode fails closed.
3. Canonical rows use only `source_page`, `disposition`, and `provenance`.
   Adding legacy `page`, `reader_value`, or `source_span_ids` is a schema error.
4. Legacy `page` fallback is retained only in the existing legacy fixture path.
   It is never consulted when canonical `source_page` exists.
5. The legacy span/owner/placement behavior remains unchanged for current
   synthetic compatibility tests. It is not used as the canonical asset model.

### Common binary binding

For `markdown_image_reference` and `visual_region`, resolve `binary.path` as a
safe repository-relative, regular, non-symlink/non-junction descendant of the
CLI-bound reconstruction package. Reject a reparse point in the file or any
ancestor below the checkout root. Recompute byte count, SHA-256, magic-derived
MIME, decoded dimensions, and require exact equality. Use path plus digest as
identity; digest-only lookup is insufficient.

For `reviewed_provisional_full_page`, require `binary is null`; candidate byte
identity is intentionally unavailable before rendering.

### Markdown-reference binding

For every Markdown variant:

1. Resolve `span_id` uniquely in `source_partition.spans`; require unique use
   across assets, `owner_kind=asset`, `classification=asset_reference_source`,
   and `span.page == asset.source_page`.
2. Require the page identity to equal that page's `source_disposition` identity
   and its canonical `package/pages/page-NNN.md` path.
3. Require declared byte and character ranges to equal the partition span,
   decode on UTF-8 boundaries, and recompute `marker_sha256`.
4. Parse exactly one complete Markdown image reference from that slice. Resolve
   its target relative to the page file and require it to equal the asset's
   exact bound `binary.path`. This closes both path borrowing and digest
   borrowing; merely finding the digest text in the marker is not sufficient.
5. Do not require the source-ledger `owner_id` to equal the final content-
   addressed asset id. The truthful binding is logical asset span -> exact
   marker target -> exact immutable binary. Placement/event ownership is the
   next seam.

### Visual-region binding

For every visual variant:

1. Resolve and hash `asset_manifest_identity`; require the path to be exactly
   `CLI reconstruction package/ASSET_MANIFEST.json`.
2. Select exactly one manifest row by the conjunction of `stored_path` equal to
   the bound binary's package-relative path and `sha256` equal to the bound
   binary digest. Recompute `asset_manifest_row_sha256`.
3. Resolve and hash `comparison_identity` as a safe repository evidence file.
   Require its closed comparison schema, `status=pass`, and no failures.
4. Resolve the comparison's companion input manifest from its evidence bundle
   (use the declared companion basename/hash, not the stored device-specific
   absolute path). Recompute its hash and require its embedded source bytes and
   SHA-256 to equal `document.source_pdf` and the CLI-bound PDF.
5. Select exactly one block by the conjunction of `selected_view`, `raw_index`,
   and membership of the exact manifest `source_path` in `block.assets`.
   Require block `source_page == asset.source_page`, exact block type and bbox,
   and recompute `comparison_block_sha256`.
6. Cache each manifest/comparison/companion parse by resolved path plus digest;
   the 4 MB comparison file must not be reparsed 100 times.

### Provisional full-page binding

For every provisional variant:

1. Require exact equality
   `provenance.source_pdf_identity == document.source_pdf == CLI PDF identity`.
2. Require `physical_page == asset.source_page`, index `physical_page - 1`, a
   valid existing PDF page, and a full-media-box region equal to the page's
   actual MediaBox. Apply actual source rotation semantics; do not hard-code
   Viral or Letter geometry in the generic helper.
3. Validate the closed one-page render recipe, media type and output dimensions
   recomputed from PDF geometry and DPI. Do not render or invent output hashes.
4. Require uniqueness of the full provenance tuple within an asset id and
   continue to rely on the already-approved B1c4 migration/replacement graph
   for logical-target identity.

### Ordering and result

Run the new independent helper at the current A3 asset-provenance position,
after B1c4, B1c5, source/package/page/partition, event/payload/recovery/xref and
B1c3 checks, but before placement and candidate work. The builder returns a
diagnostic summary by kind; the verifier independently recomputes the same
facts with its own code and error namespace. Neither imports author or builder
helpers, and neither compares against `asset_b1c4_projection()` or a pasted
Viral expected-row table.

After canonical provenance succeeds, add only an explicit stop guard for the
not-yet-authored reader placement union. Do not implement placement in B1c6.

## Guarded diagnostic and exact next seam

A no-write in-memory diagnostic implemented the algorithm above directly over
the current declaration and immutable inputs. It returned:

```text
PROVENANCE_BINDING_COUNTS {
  visual_region: 100,
  markdown_image_reference: 16,
  reviewed_provisional_full_page: 9
}
errors: []
unique_markdown_spans: 16
comparison source: 20718150 / 0A80B6F3...BED05
```

The next unimplemented condition is exactly `93` reader assets lacking the
approved placement union. The first source-ordered stable id is
`viral-accepted-ed4012725c597dbcf6fca51e55faeb883a53f6f1d2c9ee7496c667460d37c860`.
Therefore the required next public pair after B1c6 is:

```text
builder:  v2 asset placement mismatch
verifier: E_V2_ASSET: placement
```

That pair is a deliberate stop boundary. Candidate materialization must remain
unreachable.

## Minimum bounded engineering scope

Files permitted to change:

1. `kb_creator/scripts/build_scenario_master_en.py`
2. `kb_creator/scripts/verify_scenario_master_en.py`
3. `kb_creator/tests/test_build_scenario_master_en.py`
4. `kb_creator/tests/test_verify_scenario_master_en.py`
5. one new immutable engineering receipt under this handoff directory

The author helper and author tests are intentionally excluded: current authored
provenance is valid and changing it would reopen B1c4. Also excluded are
scenario-contract code, B1c5 declarations, canonical config, all candidates and
downstream output.

Suggested independent helper seam in each public implementation:
`v2_asset_provenance_binding(config, root, source_pdf, reconstruction_package)`.
The canonical branch in `v2_a3_validate()` calls it at the current asset block;
the legacy branch retains the old span behavior. The canonical branch then
raises the explicit placement seam for reader rows without placement.

## Symmetric test and mutation matrix

Every row below must be exercised against builder and independent verifier.
Tests that would be intercepted by Viral's earlier B1c4 declaration oracle must
also call the new generic helper through a closed synthetic canonical fixture,
so the test proves B1c6 rather than merely reproving B1c4.

| Class | Positive | Negative mutations / required rejection |
| --- | --- | --- |
| current real projection | all 125 provenance bindings pass with 16/100/9 and no output | public preflight stops at placement pair, never returns passed and never creates target |
| schema routing | all-canonical and existing all-legacy fixture paths | mixed canonical/legacy rows; canonical row with `page`, `reader_value`, or `source_span_ids`; unknown/cross-kind keys |
| common binary | exact safe package path, bytes, digest, magic MIME and decoded dimensions | path borrowing; digest borrowing; donor binary pair; bytes/MIME/dimension substitution; path escape; file or ancestor reparse point |
| Markdown provenance | exact 16 span/page/range/marker/target bindings | donor span; duplicate span; owner-kind or classification change; page/range/char boundary change; marker hash change; marker path borrowing; marker digest text with a foreign resolved path |
| visual manifest | exact manifest identity and unique `stored_path + sha256` row | manifest identity path/hash/bytes substitution; row-hash change; stored-path borrow; digest borrow; duplicate or missing row |
| comparison evidence | exact comparison plus companion source manifest and unique block | comparison identity substitution; companion hash or source-PDF identity substitution; selected-view/raw-index/source-reference change; provenance-kind substitution; block type/page/bbox/hash substitution; duplicate/missing block |
| provisional PDF | exact source identity, page/index, MediaBox, recipe and derived dimensions | another PDF path with borrowed digest fields; digest/bytes change; page or index substitution; region/box substitution; DPI/range/format/rotation/color/alpha/metadata change; output MIME/dimensions change; non-null binary |
| canonical page routing | `source_page` is authoritative | canonical `page` alias; mismatch between asset page and span/block/PDF page; legacy fallback outside legacy mode |
| B1c4 preservation | existing declaration/binary/provenance/replacement/migration mutation tests remain green | no weakening or bypass of `declaration-identity` / B1c4-specific failures |
| B1c5 preservation | exact 136 review rows remain `2 heading + 41 xref + 93 asset`; five reviewed mutation dimensions still fail before B1c6 | semantic id, order, page, group, priority mutation |
| compatibility/no output | frozen v1 builder/verifier preflights and legacy A3 synthetic positives remain green | canonical v2 config absent; UUID temp cleaned; all nine protected roots unchanged |

Acceptance commands are the established six-file compilation (unchanged author
files may still be included), the focused four-file B1c6 suite, and the full
current 124-test scoped suite. The exact exit condition is not
`preflight_passed`; it is the new placement seam pair with zero canonical/temp/
candidate output.

## Risks and findings

### P0

None. Both public implementations currently fail closed before output.

### P1

1. **Stale all-assets-text-span routing.** Canonical B1c4 assets are sent into
   the legacy A3 shape, preventing truthful non-text provenance and masking the
   actual placement seam.
2. **Oracle reuse risk.** The Viral-specific B1c4 expected-row recomputation is
   an approved declaration-identity gate, but cannot be reused as B1c6's input
   oracle. Doing so would not prove scenario-independent source binding.
3. **Digest-only/path borrowing risk.** Current lower-level lookups often begin
   from a digest. Generic binding must use exact path plus digest and exact
   Markdown target/manifest row/block relations.
4. **Comparison/PDF provenance borrowing risk.** A valid comparison block or
   provisional PDF declaration from another evidence chain must fail unless
   its companion input manifest or PDF identity binds to this config's CLI
   source.

### P2

1. The comparison JSON stores a device-specific absolute companion-manifest
   path. The validator should use the declared basename/hash and evidence-bundle
   topology, not trust that absolute spelling.
2. Existing B1c4/B1c5 test names still say “stops at visual review” although
   their assertion is the later provenance seam. Renaming is optional and must
   not broaden the four-file implementation scope.
3. Evidence parsing should be cached; otherwise 100 repeated 4 MB JSON parses
   make the fail-closed gate unnecessarily expensive.

## Assumptions and acceptance criteria

Assumptions:

- the approved B1c4 row schema and B1c5 review list are immutable prerequisites;
- comparison bundle topology remains `comparison/comparison.json` plus sibling
  `inputs/<declared companion basename>` for this evidence schema;
- placement, owner-anchor, semantic role and asset-event authoring are the next
  bounded phase, not hidden provenance fields;
- exact platform model/effort remains unavailable.

Acceptance criteria:

1. Both public implementations independently recompute all 125 provenance
   bindings from CLI-bound immutable inputs with exact 16/100/9 counts.
2. No canonical validator imports author or builder logic or uses author output
   as expected truth.
3. All listed borrowing/substitution attacks fail in the B1c6 helper itself,
   with symmetric public error namespaces.
4. B1c4 and B1c5 positive/negative evidence remains unchanged.
5. Frozen v1 and legacy fixture compatibility remains green without allowing a
   canonical downgrade or `page` alias.
6. Unmodified public v2 reaches exactly the placement pair above; no later seam
   is implemented or claimed.
7. Canonical v2 config, temp residue, Candidate D, render/review bundle,
   MASTER_EN and all downstream output remain absent.
8. A fresh independent `gpt-5.5` / high implementation review is required
   before orchestration advances.

## Files checked or changed, blockers, and next action

- Changed: only this immutable receipt.
- Checked read-only: root instructions; NRI goal governance; assigned task
  packet; current plan/context checkpoint; approved B1c4/B1c5 receipts; author,
  builder, verifier and their tests; frozen v1 config; source PDF; accepted-v4
  reconstruction package/pages/assets/manifest; comparison JSON and companion
  input manifest.
- Blockers: none for the bounded four-file B1c6 engineering task.
- Next action: main-chat orchestrator integrates this receipt, assigns a
  hash-bound Terra/medium four-file engineering packet with the symmetric matrix
  above, reproduces the placement seam/no-output state, and then requests a
  fresh independent implementation review. Orchestration ownership remains in
  the main chat.

READY_FOR_V2_COMPLETE_AUTHORING_PHASE_B1C6_ARCHITECTURE_REVIEW

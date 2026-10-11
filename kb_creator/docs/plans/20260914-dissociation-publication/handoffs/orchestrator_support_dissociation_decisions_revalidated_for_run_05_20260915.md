# Orchestrator support: Dissociation decisions revalidated for run 05

Date: 2026-09-15  
Assignment: bounded engineering support, `gpt-5.6-sol`, high reasoning; user-scoped override active.  
State: PASS — decision submission is valid for fresh run `20260915-cpu-first-05`. This is reconstruction evidence, not user acceptance or permission to resume the run.

## Boundary

- Compared immutable run `20260914-cpu-first-04` with fresh run `20260915-cpu-first-05` read-only.
- Did not resume or mutate either run, execute MinerU/source processing, use network/GPU/remote/API/Git, or infer acceptance.
- Created only `kb_creator/working/dissociation/reconstruction/20260915-cpu-first-05-decisions/` and disposable validation artifacts below `.tools/review-cache/dissociation-20260915-cpu-first-05-decision-revalidation/`.

## Run and queue identity comparison

| Evidence | Run 04 | Run 05 | Finding |
|---|---|---|---|
| portable run identity | `D6370C968BD209E82F8DB6E9511187ED0EB0426E8EE1F48E35A267C6E683105F` | `EB59C2BF84A0F8641F1B8995EBD0DB772986A6BA368964476BC4DC55F2AE0A64` | expected fresh implementation-bound identity |
| review queue seal | `9473637F2F866385C6D6DE23AADA302E970A6D69BB32EDAC6B82A7A5F115D2C4` | `4D68E89A72B628F735542BD693580E30897980B52D62BD6BEABE41ECD10B271F` | decision set rebound to run 05 only |
| Stage03 comparison | `449244` bytes, `C76C2F43B7027207A1CE01490A0D5BC0A2EA5B0F2EC6D6B5EBCB88A35282DA26` | `449244` bytes, `7136F138D81C0A47F1CF30918985D7ED1B41BCDC36BF30A0B38860039BCCB19E` | different identity; explicit run-05 path/hash used |
| contract | `99B01F09AA9CFCE72AC407ADBFF21E54BC11A2FDA73A00FDB0FC763024FEAD4E` | same | unchanged authority |
| source | `01855CD1AA2E3F90C31B572AA01D2643FC862935B892FD7D49A7530CAACD947B` | same | unchanged immutable source |

The Stage03 JSON leaf diff contains exactly 33 changes, all confined to the fresh run identity, run-local absolute paths, view-set identities, and sealed skipped-view receipt identities. No view blocks, page coverage, pairwise evidence, required/succeeded/skipped topology, reason codes, or content semantics changed.

All six Stage04 merge packets are byte-identical between runs and retain the same role and ordered CPU views:

| Page | Bytes | SHA-256 |
|---:|---:|---|
| 001 | 7961 | `2E9D0D1CE5B75A02D6C4AE83BED04B3C68933620ED823B5C5F33B0A6D199CD94` |
| 002 | 91752 | `B6036691039492EC9653DB1E4A0587F77C0791A128C32E66084C929C8B4DEA7B` |
| 003 | 106348 | `162227C6D04730F775C63524E110713BBEF68BF05FA9A82856A5C8D8E4FFE5F0` |
| 004 | 101746 | `D65986B25A1DA40F12604BFFA6B55712D863AE6A3EC95483C8D9643A311DDB8D` |
| 005 | 44690 | `F5B4D3FE05A05B564AD89DD314F68BA29230506A51275AAEE2E37C5F779DBCA2` |
| 006 | 93763 | `32F6C966FC69D71E58DC856633FFB148EEC798F7EBF642A705BCC25A60D33753` |

## Decision revalidation and new submission

The production materializer decision validator was applied directly to the six old page decisions with run-05 packets, comparison and raw artifacts before copying. Result: `6/6` valid, `87` selected blocks resolved exactly, `2` selected assets resolved inside the matching fresh raw-view roots, roles/overlay choices valid, every `unresolved` list empty, and every `visual_reviewed` flag true.

The six new page files are exact byte copies. Their identities remain:

- page 001: `1106` bytes, `147B2397D2DD594F0E4863AD6AB71E1F4A83DD7521124C78D47D129187A46E5C`
- page 002: `7795` bytes, `3E1CA05990CC2209DC1EC11BA5EC055E58C603020DD175816FB48D6499B8FEA6`
- page 003: `7412` bytes, `D18EC8A9671CE0D3D51705C79168828CE8CE389A822EBB3BE2B78AC9EFFCB5D8`
- page 004: `7552` bytes, `0FE860EC46EB08059376629266726FC529D0463B3AF745C4589F89CCA0FB535E`
- page 005: `3269` bytes, `0455DC00336AC4EB3CCDAE11A6E6ABDFB304C3711CFFECA8E8C6EC229071D958`
- page 006: `4452` bytes, `8DB9CAEB866CA2C4D11FCB37884421E1D29FC6E9AD1C2C0C706EE201274801B6`

New `decision_set.json`: `1498` bytes, SHA-256 `C9DB4E907E328EBE74AEDE06A19DBD6A925D065C044EFA4144A865E6E16813D0`. Production `validate_queue` plus `validate_decision_set` passed with six exact rows and the run-05 queue seal.

## Production disposable validation

- Fidelity audit: PASS, schema `kb_creator.ai-merge-fidelity-audit/v1`, six pages, `errors=[]`. Long-page recall values were page 2 `0.9977298524`, page 3 `0.9805352798`, and pages 4-6 `1.0`; all exceed the applied `0.95` threshold. Audit identity: `1851` bytes, `064FBF08EC1DBFE435B5D1713268692452522B0C80746E0DE5718F86AA498862`.
- Exact production materializer invocation supplied run-05 Stage03 path plus SHA `7136F138...`; result: `candidate_ready_for_reconstruction_qa`, `6` pages, `2` assets, `2` unique asset byte sets.
- Candidate `RECONSTRUCTED_EN.md`: `20937` bytes, `C8E6A65D862150F85608F8C88D4F4513C171F2CE3F361C7E221D7EAC802CD72D`.
- Candidate `MERGE_PROVENANCE.json`: `11542` bytes, `66DE334DB0E7A6522E90D7E917A7D0E2D89ACEA34C3F4DF171604D7F5624FC2F`; status is `candidate_ready_for_reconstruction_qa`, six pages, and `raw_comparison` is the exact run-05 Stage03 file.
- Candidate `ASSET_MANIFEST.json`: `855` bytes, `8445F26F0CEC1086B7335FC2702EC5C8218A030C27241C48B16AB8FBCF488BB6`.

## Next action

The decision submission is ready for the orchestrator's controlled run-05 resume/integration path. This receipt does not perform that resume and does not constitute RECONSTRUCTED_EN acceptance.

## Superseding P1 validation — page 005 and cross-page 003→004 continuation

This section supersedes the earlier decision-set, fidelity-audit and candidate identities in this receipt. The earlier disposable candidates are intermediate evidence only and must not be used for integration.

Two source-visible omissions were corrected and then revalidated:

- Page 005 is `3401` bytes, SHA-256 `56D243C1753A85CFD9E2B6A6DAB35ACB858D10863A132B2ABE090B1C5B79E85A`. Its first selected provenance is `raster_pipeline_ocr:71`, preserving the page-start continuation `same day as it was in Aniak.`; `raster_pipeline_ocr:75` preserves the complete Laboratory sentence through `descending into the darkness.`. The remaining faithful body text and native Alaska map remain selected from `original_pipeline_txt`.
- Page 004 is `7804` bytes, SHA-256 `792E9638C5BF507FFD5AB5E9D4710A391B87E544D97ADEBB447AC62BDBA4E7CE`. Its first selected provenance is the exact `raster_pipeline_ocr:48` text `ability of the human body. The rest became vessels.`, which visibly completes page 003's final `testing the malle-`. The remaining page-004 selection is unchanged.

The page-003/page-004/page-005 triptychs were copied byte-for-byte into the final disposable review root and inspected directly:

- page 003 triptych: `3086752` bytes, `07225250A68B2FD04B07005AF66EEC84ABDC58B207474FEBB902E910B623016C`; all three views visibly end with `malle-`.
- page 004 triptych: `3302788` bytes, `079C01785B0FC43AC2520DA77910F3A51F1035DF44DFC570D7289968911B14E1`; all three views visibly begin with `ability of the human body. The rest became vessels.` above the Environment Two body.
- page 005 triptych: `2895313` bytes, `FE1F6DC0FFF69523DD3865EC25591AFAA20DDF032EB8D3A1EBBA8AE67B03131C`; all views visibly begin with `same day as it was in Aniak.`, retain the complete Laboratory paragraph across columns, and show the Alaska map in its source position.

Final run-05 decision-set identity: `1498` bytes, SHA-256 `76845A32377595F074C88BA9F3899FFF05777275E7864734C25F13BFA5F20ECB`. Production `validate_queue` and `validate_decision_set` passed all six exact decision rows against queue seal `4D68E89A72B628F735542BD693580E30897980B52D62BD6BEABE41ECD10B271F`.

The full production fidelity audit was rerun from the final six decisions:

- schema `kb_creator.ai-merge-fidelity-audit/v1`, six pages, `errors=[]`, `passed=true`;
- page 004: selected/decision tokens `951/951`, recall `1.0`, precision `1.0`;
- page 005: selected/decision tokens `327/327`, recall `1.0`, precision `1.0`;
- audit identity: `1851` bytes, SHA-256 `B946378D7AB2ECD8518D2E866A08BF5C1DFFD6D3EF1259B0F4EC1077488D2D00`.

The exact production materializer was rerun in the fresh disposable root `.tools/review-cache/dissociation-20260915-cpu-first-05-page4-page5-p1-final/` with the sealed Stage03 comparison path and SHA `7136F138D81C0A47F1CF30918985D7ED1B41BCDC36BF30A0B38860039BCCB19E`. Result: `candidate_ready_for_reconstruction_qa`, six pages, two assets, two unique asset byte sets.

- final disposable `RECONSTRUCTED_EN.md`: `21048` bytes, SHA-256 `1FCC84CA50E24D57CFD5BFA906350EF24BC81BB93A7CC5C115415765DC71D28B`;
- final `MERGE_PROVENANCE.json`: `11632` bytes, SHA-256 `F629F4903387681041E028DA25DCD3C015A89DFAE2ACF0AF678B2608E119C494`;
- final `ASSET_MANIFEST.json`: `855` bytes, SHA-256 `8445F26F0CEC1086B7335FC2702EC5C8218A030C27241C48B16AB8FBCF488BB6`.

Materialized boundary checks confirm page 003 ends in `malle-`, page 004 begins `ability of the human body. The rest became vessels.` and ends `the end of the`, and page 005 begins `same day as it was in Aniak.`. The run, source and code remained unchanged; no resume or acceptance was performed.

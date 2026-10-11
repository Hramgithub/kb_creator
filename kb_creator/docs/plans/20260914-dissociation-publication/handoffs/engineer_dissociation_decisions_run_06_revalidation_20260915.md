# Engineer receipt: Dissociation run-06 decision revalidation

- Result: **decision transfer and production decision validation complete; source-visible audit blocked before content evaluation by a production status-enum mismatch.**
- Role: engineering, `gpt-5.6-sol` / high under the user-scoped override.
- Scope: Packet D only. Compared immutable runs `20260915-cpu-first-05` and `20260915-cpu-first-06`, created a fresh run-06 decision root, byte-copied the six already corrected decisions, rebound `decision_set.json`, and invoked the production validators. No resume, Stage06, materialization, acceptance, pipeline-code edit, source/run/`.tools` mutation, network, GPU, remote/API, or Git operation was performed.

## Immutable run identities

| Evidence | Run 05 | Run 06 |
|---|---|---|
| `run.json` file SHA-256 | `45F4A8C63C23D63644E2B522BBD4E7DF968FE4F6C797D679F3FF2B7832F6423A` | `CD11D434B57B9E687BD68C5088F420F8D4C4F1FE9EF093741CC0AB94C4C48C9C` |
| portable run identity | `EB59C2BF84A0F8641F1B8995EBD0DB772986A6BA368964476BC4DC55F2AE0A64` | `AC2A5AD706BA49F7824213BC9BB166A5AC642DD94CDECB89B0717C13CE376429` |
| review-queue file SHA-256 | `E15F5DAEABBFC56A57664088C7792CA6AEBED18D0B6FEC34B6ACAEB1EEA310D0` | `F11CF0EE2E87A5F1AA9C66899714CCA12A7B48829DFED1E70B590FE175245F57` |
| review-queue internal seal | `4D68E89A72B628F735542BD693580E30897980B52D62BD6BEABE41ECD10B271F` | `F58A324477869A7E7D744E8ADD10F9A414CC2290C1248C6D2130F5FDACD77593` |
| comparison bytes / SHA-256 | `449244` / `7136F138D81C0A47F1CF30918985D7ED1B41BCDC36BF30A0B38860039BCCB19E` | `449244` / `85E1D98B47FD7B841E70835325BB89B0752113E2C72535618F2C2B14B2052F16` |
| comparison status | `pass_for_review` | `pass_for_review` |

Both queues bind the same source SHA-256 `01855CD1AA2E3F90C31B572AA01D2643FC862935B892FD7D49A7530CAACD947B` and contract SHA-256 `99B01F09AA9CFCE72AC407ADBFF21E54BC11A2FDA73A00FDB0FC763024FEAD4E`.

The required succeeded view order is identical and exact in both comparisons:

1. `original_pipeline_txt`
2. `original_pipeline_ocr`
3. `raster_pipeline_ocr`

Run-06 required-view receipts:

| View | Receipt bytes | Receipt file SHA-256 | Internal receipt seal |
|---|---:|---|---|
| `original_pipeline_txt` | 21159 | `3FDF2BD0D87C11236B8EF5930B192FDD3768ACC8282310078E12B3D49C3D92CE` | `CA8A1DE4A45924EDE1C4EC0B3F038CD7D483AE6D9DD2AFD0DE06467355714005` |
| `original_pipeline_ocr` | 21159 | `E85D5080DFF3968734225B8D3FFDA41B875CE1BE36E13E49EFC01B1DFAC81401` | `E6FE2A8D3ACB03E3757BC75CA01192BB0F48851BA438F3F235FFFEBD2BF9DF26` |
| `raster_pipeline_ocr` | 21718 | `41B3AA001A55F20ED1B81BB8BFE815DA5C3EC60D475BFD26E7483E5B56FC66E3` | `7E30BD1403AFB4A4F78A6D7C7B1857055279486D1578EDB8C22209EE844B2E30` |

Run-06 `view-set.json` is `3762` bytes, file SHA-256 `7648EB91A0AA23F72A0670162FFB1A37D21708F2F62987AF3CD78A76B766E2EF`, internal seal `40DFA26CD71F6E3132B58B4AA3C42548E79AE4DCE7F99A3A35419901C6B1C3BE`.

The required-view input/profile identities, page coverage, and all semantic output artifacts match run 05. Each output inventory has the same path cardinality (`9`, `9`, `10`) and differs only in the regenerated `*_origin.pdf` payload:

- txt: run05 `4FD7EEA4...`, run06 `EC03D66B...`, both `2142708` bytes;
- original OCR: run05 `27D6CEA7...`, run06 `98906BF2...`, both `2142708` bytes;
- raster OCR: run05 `AA309F7B...`, run06 `F3A70482...`, both `32688460` bytes.

All six queue-bound Stage04 merge packets are byte-identical between runs:

| Page | Bytes | SHA-256 |
|---:|---:|---|
| 1 | 7961 | `2E9D0D1CE5B75A02D6C4AE83BED04B3C68933620ED823B5C5F33B0A6D199CD94` |
| 2 | 91752 | `B6036691039492EC9653DB1E4A0587F77C0791A128C32E66084C929C8B4DEA7B` |
| 3 | 106348 | `162227C6D04730F775C63524E110713BBEF68BF05FA9A82856A5C8D8E4FFE5F0` |
| 4 | 101746 | `D65986B25A1DA40F12604BFFA6B55712D863AE6A3EC95483C8D9643A311DDB8D` |
| 5 | 44690 | `F5B4D3FE05A05B564AD89DD314F68BA29230506A51275AAEE2E37C5F779DBCA2` |
| 6 | 93763 | `32F6C966FC69D71E58DC856633FFB148EEC798F7EBF642A705BCC25A60D33753` |

## Decision artifacts

Created `kb_creator/working/dissociation/reconstruction/20260915-cpu-first-06-decisions/` with exactly:

- `decision_set.json`: `1498` bytes, SHA-256 `168234044726BAA7D3F7165F3797E02888E4A0D2CE9FE59E3E5DF7836CFCFEB0`, bound to run-06 queue seal `F58A3244...`;
- `pages/page-001.json`: `1106` bytes, `147B2397D2DD594F0E4863AD6AB71E1F4A83DD7521124C78D47D129187A46E5C`;
- `pages/page-002.json`: `7795` bytes, `3E1CA05990CC2209DC1EC11BA5EC055E58C603020DD175816FB48D6499B8FEA6`;
- `pages/page-003.json`: `7412` bytes, `D18EC8A9671CE0D3D51705C79168828CE8CE389A822EBB3BE2B78AC9EFFCB5D8`;
- `pages/page-004.json`: `7804` bytes, `792E9638C5BF507FFD5AB5E9D4710A391B87E544D97ADEBB447AC62BDBA4E7CE`;
- `pages/page-005.json`: `3401` bytes, `56D243C1753A85CFD9E2B6A6DAB35ACB858D10863A132B2ABE090B1C5B79E85A`;
- `pages/page-006.json`: `4452` bytes, `8DB9CAEB866CA2C4D11FCB37884421E1D29FC6E9AD1C2C0C706EE201274801B6`.

Every page decision is byte-identical to the corrected run-05 decision. Page 004 still begins with `ability of the human body. The rest became vessels.` and selects `raster_pipeline_ocr:48`. Page 005 still selects `raster_pipeline_ocr:75` and includes `with an open mine tunnel, descending into the darkness.` Both retain `unresolved: []`; this receipt does not infer acceptance.

## Production validation

The production validation call performed, in order:

1. `reconstruction.load_run`;
2. `_validate_live_run_bindings`;
3. `_validate_stage_prefix(..., RUN_STAGES)` for sealed Stages01-04;
4. `validate_queue` on the fixed run-06 queue;
5. `validate_decision_set` on the new root.

Result: **pass**, exact decision page domain `[1,2,3,4,5,6]`, run identity `AC2A5AD7...`, queue seal `F58A3244...`.

The direct production `audit_v2` call used the fixed run-06 packet root and explicit file SHA-256 values for queue, comparison, and decision set. It failed before content accounting with:

```text
ValueError: comparison required CPU authority mismatch
```

Exact root cause: `audit_v2` currently requires `comparison.status == "pass"`; the accepted Stage03 producer writes the sealed status `pass_for_review`. The comparison run identity and required-view list are otherwise exact. No report was forged, no pure-content helper was used as a bypass, and no Stage05/Stage06 directory was created.

## Blocker and risk

- **P1:** the production v2 audit cannot consume the producer's valid `pass_for_review` comparison state. This prevents source-visible completeness closure and therefore prevents resume, Stage06, promotion, or acceptance.
- Packet D explicitly forbids pipeline-code edits, so this assignment did not remediate the mismatch.
- No content-level audit result is claimed. The six decisions are production-validator-valid against run 06, but remain unapproved until the generic audit status contract is remediated, independently reviewed, and the exact production audit passes.

## Changed files

- `kb_creator/working/dissociation/reconstruction/20260915-cpu-first-06-decisions/decision_set.json`
- `kb_creator/working/dissociation/reconstruction/20260915-cpu-first-06-decisions/pages/page-001.json`
- `.../page-002.json`
- `.../page-003.json`
- `.../page-004.json`
- `.../page-005.json`
- `.../page-006.json`
- this receipt

## Next action

Authorize a narrow generic remediation aligning the v2 audit's accepted comparison state with the sealed Stage03 contract, add a production-shaped adversarial regression, obtain independent closure, then rerun the production audit against this exact run-06 decision root. Do not resume run 06 before that passes.

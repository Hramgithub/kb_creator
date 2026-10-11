# Engineer receipt: Dissociation run-07 decisions and v2 audit

- Result: **fresh run-07 decision binding and all production run/stage/queue/decision validations passed; the direct production v2 source-visible audit reached its content ledger and failed closed with 28 completeness errors.**
- Role: engineering, `gpt-5.6-sol` / high under the user-scoped override.
- Scope: Packet F only. No resume, Stage06, materialization, acceptance, pipeline-code edit, immutable-run/source/`.tools` mutation, network, GPU, remote/API, or Git operation was performed.

## Fresh authority and packet comparison

| Evidence | Run 06 | Run 07 |
|---|---|---|
| portable run identity | `AC2A5AD706BA49F7824213BC9BB166A5AC642DD94CDECB89B0717C13CE376429` | `3F7F9B4765D79BCDA5A3BBCC8EAB22723C2063161E2C31B65A3843507F81E40A` |
| `run.json` file SHA-256 | `CD11D434B57B9E687BD68C5088F420F8D4C4F1FE9EF093741CC0AB94C4C48C9C` | `85534D85D0DAFDF7FA8A9FB95AB2CC769029066FCEF190E632C97D946BE17B5F` |
| review-queue file SHA-256 | `F11CF0EE2E87A5F1AA9C66899714CCA12A7B48829DFED1E70B590FE175245F57` | `8C623A1FF380270BD660228741DBBE68FC4F5F5964789B3D78592F48F2E35F38` |
| review-queue internal seal | `F58A324477869A7E7D744E8ADD10F9A414CC2290C1248C6D2130F5FDACD77593` | `E49A5C347DC4EDD41A53E0073045F370CD0E86E95AC49D706D50F2FEB97A64A2` |
| comparison bytes / SHA-256 | `449244` / `85E1D98B47FD7B841E70835325BB89B0752113E2C72535618F2C2B14B2052F16` | `449244` / `08DD3F1C644997E579F679265E73D36E6BBFF84A9C656F03E5D240E42BCE3C95` |
| comparison state | `pass_for_review`, `failures=[]` | `pass_for_review`, `failures=[]` |

Both runs bind source `01855CD1AA2E3F90C31B572AA01D2643FC862935B892FD7D49A7530CAACD947B` and contract `99B01F09AA9CFCE72AC407ADBFF21E54BC11A2FDA73A00FDB0FC763024FEAD4E`. Run 07 retains the exact required/succeeded view order `original_pipeline_txt`, `original_pipeline_ocr`, `raster_pipeline_ocr`.

Run-07 `view-set.json` is `3762` bytes, file SHA-256 `4014F5056B8EE745DCB3CD704648CA4C5CE7AED9BD94D7B0F4EA7190AC8DF0E7`, internal seal `1A38F67756C48F665FDBE1339EBCDFA5557CEEF9CDA3674A0D9E22E01C11C7D4`. Required-view receipt identities are:

| View | Bytes | File SHA-256 | Internal seal |
|---|---:|---|---|
| `original_pipeline_txt` | 21159 | `58AFD63D9137B50E31C306BC09FB368A42308CB9C0B59F4FB45D7ACBC971EF5A` | `FE77CA1DF76F26C93B8C65B05070632A7CB91AE5BD1AE1052A3BB1A4D452AEE5` |
| `original_pipeline_ocr` | 21159 | `078F2B499CC5BF5758175D256D836E9C0E7A732D9DC63E810C3383AFF9BA5627` | `3631518D5FC13095291D815F196C6179FA22772882C081BE9F9045D705FE1AE5` |
| `raster_pipeline_ocr` | 21718 | `ED1C1C791573283AC355D73AC63980DCCDB14254BCD9D43A11D79DD74709FBC8` | `D60D377CAAF4AE9B6D9076D03A0D6AC2F70ED88A731BE8D3932FE50B0DF4CE90` |

All six queue-bound Stage04 merge packets are byte-identical between runs 06 and 07:

| Page | Bytes | SHA-256 |
|---:|---:|---|
| 1 | 7961 | `2E9D0D1CE5B75A02D6C4AE83BED04B3C68933620ED823B5C5F33B0A6D199CD94` |
| 2 | 91752 | `B6036691039492EC9653DB1E4A0587F77C0791A128C32E66084C929C8B4DEA7B` |
| 3 | 106348 | `162227C6D04730F775C63524E110713BBEF68BF05FA9A82856A5C8D8E4FFE5F0` |
| 4 | 101746 | `D65986B25A1DA40F12604BFFA6B55712D863AE6A3EC95483C8D9643A311DDB8D` |
| 5 | 44690 | `F5B4D3FE05A05B564AD89DD314F68BA29230506A51275AAEE2E37C5F779DBCA2` |
| 6 | 93763 | `32F6C966FC69D71E58DC856633FFB148EEC798F7EBF642A705BCC25A60D33753` |

## Decision artifacts

Created `kb_creator/working/dissociation/reconstruction/20260915-cpu-first-07-decisions/`:

- `decision_set.json`: `1498` bytes, SHA-256 `D13BBA3A196E8EFEA23527EF074E76DF56520BCEBE2F2A0C64F3DA72A71E7CBE`, freshly bound to queue seal `E49A5C34...`;
- page 001: `1106` bytes, `147B2397D2DD594F0E4863AD6AB71E1F4A83DD7521124C78D47D129187A46E5C`;
- page 002: `7795` bytes, `3E1CA05990CC2209DC1EC11BA5EC055E58C603020DD175816FB48D6499B8FEA6`;
- page 003: `7412` bytes, `D18EC8A9671CE0D3D51705C79168828CE8CE389A822EBB3BE2B78AC9EFFCB5D8`;
- page 004: `7804` bytes, `792E9638C5BF507FFD5AB5E9D4710A391B87E544D97ADEBB447AC62BDBA4E7CE`;
- page 005: `3401` bytes, `56D243C1753A85CFD9E2B6A6DAB35ACB858D10863A132B2ABE090B1C5B79E85A`;
- page 006: `4452` bytes, `8DB9CAEB866CA2C4D11FCB37884421E1D29FC6E9AD1C2C0C706EE201274801B6`.

The six page files are byte-identical to the corrected run-06 decisions, including the page-004 continuation and page-005 Laboratory suffix. Their `unresolved` arrays remain empty; this receipt does not infer acceptance.

## Production validation

The production call executed `load_run`, `_validate_live_run_bindings`, `_validate_stage_prefix(..., RUN_STAGES)`, `validate_queue`, and `validate_decision_set`. Result: **pass** for all four sealed pre-review stages and all six decisions, with the fresh run and queue identities above.

The production CLI then invoked direct v2 `audit_v2` with explicit queue/comparison/decision-set paths and file SHA-256 values. It traversed the complete run graph and reached content accounting. Result: **exit 1, `passed=false`**. The exact report is:

- `kb_creator/working/dissociation/reconstruction/20260915-cpu-first-07-decisions/validation/source-visible-completeness-audit.json`
- `251917` bytes
- SHA-256 `B16618741A667C9EDE15377697DC8A6F42AD993C738338DAFB03B53EE3D13299`
- schema `kb_creator.ai-merge-fidelity-audit/v2`
- five of five page boundaries report `both_sides_covered=true`, but page ledgers still contain 26 unaccounted source units and two Markdown proof errors.

| Page | Required / covered normalized chars | Completeness | Selected recall / precision | Units / unaccounted | Errors |
|---:|---:|---:|---:|---:|---:|
| 1 | 98 / 36 | 0.3673469388 | 1.0 / 0.6 | 4 / 2 | 3 |
| 2 | 12924 / 12903 | 0.9983751161 | 1.0 / 0.9997675500 | 64 / 4 | 5 |
| 3 | 12289 / 12204 | 0.9930832452 | 1.0 / 1.0 | 67 / 6 | 6 |
| 4 | 13001 / 12980 | 0.9983847396 | 1.0 / 1.0 | 65 / 4 | 4 |
| 5 | 4424 / 4392 | 0.9927667269 | 1.0 / 1.0 | 23 / 4 | 4 |
| 6 | 5891 / 5850 | 0.9930402309 | 1.0 / 1.0 | 60 / 6 | 6 |

Exact audit errors, grouped by page:

- page 1: `unaccounted full source unit original_pipeline_txt:1`; `unaccounted full source unit original_pipeline_ocr:1`; `Markdown contains omitted, reordered, or unproven reader text`.
- page 2: `unaccounted full source unit original_pipeline_txt:22`; `unaccounted full source unit original_pipeline_ocr:22`; `unaccounted full source unit raster_pipeline_ocr:1`; `unaccounted full source unit raster_pipeline_ocr:22`; `Markdown contains omitted, reordered, or unproven reader text`.
- page 3: `unaccounted full source unit original_pipeline_txt:45`; `unaccounted full source unit original_pipeline_ocr:36`; `unaccounted full source unit original_pipeline_ocr:45`; `unaccounted full source unit raster_pipeline_ocr:23`; `unaccounted full source unit raster_pipeline_ocr:37`; `unaccounted full source unit raster_pipeline_ocr:46`.
- page 4: `unaccounted full source unit original_pipeline_txt:66`; `unaccounted full source unit original_pipeline_ocr:66`; `unaccounted full source unit raster_pipeline_ocr:47`; `unaccounted full source unit raster_pipeline_ocr:69`.
- page 5: `unaccounted full source unit original_pipeline_txt:74`; `unaccounted full source unit original_pipeline_ocr:74`; `unaccounted full source unit raster_pipeline_ocr:70`; `unaccounted full source unit raster_pipeline_ocr:80`.
- page 6: `unaccounted full source unit original_pipeline_txt:91`; `unaccounted full source unit original_pipeline_ocr:91`; `unaccounted full source unit raster_pipeline_ocr:103`; `unaccounted full source unit raster_pipeline_ocr:104`; `unaccounted full source unit raster_pipeline_ocr:105`; `unaccounted full source unit raster_pipeline_ocr:106`.

## Blocker and next action

- **P1:** the direct production v2 content ledger does not accept the otherwise validated six-decision set. This is a hard blocker for Stage05/Stage06, promotion, or acceptance.
- No bypass, allowlist, pure-helper substitution, decision edit, or resume was attempted. The exact failed audit report is retained for architecture/critic diagnosis.
- Next action: independently diagnose whether the ledger must account cross-view-equivalent and cross-page units differently or whether the decisions require explicit additional dispositions. Remediate only under a separately reviewed generic contract; then create a fresh immutable run because implementation changes invalidate run 07.

## Changed files

- `kb_creator/working/dissociation/reconstruction/20260915-cpu-first-07-decisions/decision_set.json`
- `kb_creator/working/dissociation/reconstruction/20260915-cpu-first-07-decisions/pages/page-001.json` through `page-006.json`
- `kb_creator/working/dissociation/reconstruction/20260915-cpu-first-07-decisions/validation/source-visible-completeness-audit.json`
- this receipt

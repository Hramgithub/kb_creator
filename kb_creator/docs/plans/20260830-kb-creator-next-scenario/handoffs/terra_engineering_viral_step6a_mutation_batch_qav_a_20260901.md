# Terra engineering receipt: Viral Step 6A QAV-A

Result: **COMPLETE, 25/25.** Engineering evidence only; this is not protected
119/combined 490/live QA, candidate acceptance, promotion, release, or Git
authority. Role: Terra engineering (`gpt-5.6-terra` / medium). Orchestrator
policy owner: main chat (`gpt-5.6-sol` / medium); assignment state
platform-unverified; scoped override is the accepted SCH/QAV taxonomy amendment.

## Admission and material

Admitted: dispatch `F4C0485B036C5412B4C2A817EE398911A9F7BE983749F864CF5CA8C4BAFD1646`, amendment `0A692CD1A8F3067E551ACFB1581840BF9748FD2C308C6BBE79FD4B174FC75D2A`, ACCEPT review `102383E2CD10EFE91DFBAD13A905DDCFB63DFE8ADF6BCC9B1D7937E40ADAA5DB`, held assignment `5582B039B2B8D8E88B92821D1AAAF537AEBBDEA6CE5D6CD8EFF191BC06908144`.

| file | before SHA-256 | after SHA-256 |
|---|---|---|
| `kb_creator/scripts/scenario_source_reconstruction.py` | `2309CD5015B89908A5B751916F46B4C601AFB8E121EB338FC6450B7BAAE49FAC` | `0F891304301007D14D6BCB10DBA8526DC14988591C000D75755ADFD4CFE63627` |
| `kb_creator/tests/test_scenario_source_reconstruction.py` | `7B9AEC1EF0BA2870E2021544912538FE3234DAF92D0E38E34F16285118649DCF` | `6FED8CE2797E8237A2187681A59C2AC1A7DFC5C3221E3F51103B2C22993DAEC4` |

One shared phase-5 QA root predicate now checks the exact admitted QA key set
on both routes and emits `E_SHAPE_QA`; it separately emits `E_SCHEMA_QA` for a
complete wrong schema. Phase 9 independently enforces state with `E_QA_STATE`.
The 25 QAV-A physical mutators use literal `()` reseals/transports and are
unique named callables. The permitted SCH aliases remain distinct objects.

## Closed audit objects

All 25 full section-11 16-field objects were independently materialized in
fresh temporary-only fixtures. Shared literal fields for every object are:
`family=QAV`, `fixture_root_token=fixture`,
`semantic_before_sha256=5B752E120BBB949460BF0266F6D54EF4207AE52A6EB9075855F94DD6E10A6066`,
`changed_before_reseal=[semantic_selector]`, `declared_reseals=[]`,
`changed_by_reseal=[]`, `strict_verify_calls=1`, `outside_fixture_reads=0`,
`undeclared_changes=[]`, `residue=[]`, `result=PASS`.

| case / selector suffix | semantic-after SHA-256 | expected = observed |
|---|---|---|
| asset_count | `2044A354849E1F200FE347566482B4F3330F9489074CB6937452A3435DFA91C3` | E_SHAPE_QA |
| block_count | `134D2BF48BA9E81F75BB8BD84E107BE0DA4E95BF883C5A08035938374F54BA37` | E_SHAPE_QA |
| contact_sheet_count | `4EE03BAFE14F1D739234A06748030D7B052C17FFFED91CC62246C30252781D60` | E_SHAPE_QA |
| contract_sha256 | `B43DEDD1480A93DDCC4F47DE9941C01A43C3C5934C956A9738E743718D28A7E1` | E_SHAPE_QA |
| counts | `FC4D058A3B676AAE95D6B0CA51A637D47803045229377B419012F0ABB44DE702` | E_SHAPE_QA |
| gate_results | `348992D9F2DB938465B95708D533639139B75494C86C2CE2A8F7A72FAC064CD1` | E_SHAPE_QA |
| handout_count | `9419CC67C1AAE59CC7717A59C5FE74ED9958AAB905B08BABB3B62DACCE87248D` | E_SHAPE_QA |
| historical_material_opened | `DF0C474DDA52C32390FD8254E1B198D95785520BA1FB31AF916DE1AE713086C8` | E_SHAPE_QA |
| main_scripts_invoked | `FED757AF23F6E58053B7FB87678687B994B8AC990481F1E19CC4BA64F00B7F1C` | E_SHAPE_QA |
| navigation_anchor_count | `E164DCBB32E1A8159128D4F61E5559BD61344F0F7014BEDB7FFCA93EA92DF363` | E_SHAPE_QA |
| open_blocker_count | `4FCECAA4C49D035C0E2D92222C620F272FEBDC7A71FA5CCC7E8DC9B189C6EE36` | E_SHAPE_QA |
| output_inventory | `E0AD4DA5285147B2918AADBC0B52B153F7A4E8AAF579D4B474890B387D33B3B0` | E_SHAPE_QA |
| output_inventory_count | `10BC8D0EA670B7F6BBA1272044CD1F435480EE19E246547303DF3A121B2F6739` | E_SHAPE_QA |
| output_inventory_rule | `1D1A9ED52690AFFDB038BCBB1507D1F0D8958AEDBAC99C7B494A7AA68ECC27E7` | E_SHAPE_QA |
| output_inventory_sha256 | `3A2F7FDC40E2ADC2099C259CB83FB859FC4F7F5CB89102F81957179F67FDE18E` | E_SHAPE_QA |
| page_count | `9E53DF9080601E83DB193E6ED54AFE6ECF3752179CD9D54D3918E9103C4F8C8C` | E_SHAPE_QA |
| recovery_evidence_sha256 | `87809C2D7739EA849E899389F9FC5011A4E67BCA8A1D3331DD80E75481A1AE44` | E_SHAPE_QA |
| recovery_manifest_sha256 | `0C4CA28B6D1F2ACBEF00716DA8E0641624911F742D78E27E764EC3CE37EA54D5` | E_SHAPE_QA |
| referenced_asset_count | `930AA555276284E66AF1C0568A08E6CE46B28276FEE01137B2D30F18877DF24E` | E_SHAPE_QA |
| schema | `07F5B6FA834F37AE56BF4D8E342AD5AE6FDE50EEE3F0BAB846DA16DB8416E67F` | E_SHAPE_QA |
| source_sha256 | `99A35BC10DFED0192B386834CD5E90ACE9F92AC8DD8907BECDC8C8485F7A95E3` | E_SHAPE_QA |
| state missing | `931B959618173345B4B3C66BFB21D4E78F592A1C904C845A5750B1AB3934BE6D` | E_SHAPE_QA |
| unreferenced_asset_count | `6F5385199E96EDE34DDF176F31D344A1194E27DCF62E2952365DAD47A46211FB` | E_SHAPE_QA |
| extra `unexpected` | `385FA487B9625FB4E5095B3C217168021AE4C53A7A91C5EBE6F7C6FC8A46FB46` | E_SHAPE_QA |
| state promoted | `957105FCF9F300663C40A4ED6E6B66FCB5465A5A8DF1031319A8213213CC34AF` | E_QA_STATE |

Selectors are exactly `candidate/RECONSTRUCTED_EN.qa.json#/` plus the table
suffix, except the final two are `#/unexpected` and `#/state`. Case IDs are
the ordered amended matrix `QAV-top-<field>-missing` (23), `QAV-top-extra`,
and `QAV-state-promoted`. Callable ordinals are 1..25 in this table order;
each name is `mutate_` plus its case id with hyphens changed to underscores.
The four alias callables are distinct: `mutate_SCH_QA_required_top_member_missing`,
`mutate_QAV_top_asset_count_missing`, `mutate_SCH_qa_unexpected_top_member`,
`mutate_QAV_top_extra`.

Canonical row formula was validated in memory:
`case_id<TAB>semantic_selector<TAB>comma_joined_reseals<TAB>expected_code<TAB>observed_code<TAB>PASS<LF>`.
Rows: 25; UTF-8/LF bytes: 2832; SHA-256:
`F75C7C56ED91C54DA9CD596B256D2950AC106230692D4956393D5D3C08CB8856`.

## Commands, residue, and next action

With `python -B` and `-p no:cacheprovider`: QAV chunks returned native exit 0
with `8`, `8`, `8`, `1` passed; SCH aliases `2 passed`; CMD count-pages
regression `1 passed`; BLD `3 passed, 368 deselected`; focused collect
`371 tests collected`. All command stderr was empty; outputs were retained in
memory. No full focused run, protected/combined test, live preflight/verify,
or build/remediate was run.

Pre-existing cache identities remained unchanged: `168C67BC8784F76DBA57F873A32B419112998AA359C9F1A21BF3E954D3BD13C4`,
`9F4E03CC81C749C4C29FD0F97478D3EB1A2EF735D1B225DAD191B0D451FBEF54`,
`DE4E516486951CE4EA9DA7621C54D7429489B0ABAB3CE1F58B28309457BDF0B9`; the
pre-existing `.pytest_cache` persisted. Zero new cache, pyc, fixture, temp,
marker, probe, or log residue was found.

Exact attributable diff: modified the two material paths above; added this
receipt; deleted none. Blockers: none for QAV-A. Next action: downstream work
only by separately assigned roles; independent QA and critic gates remain open.
Elapsed: approximately 50 minutes. Token use: unavailable.

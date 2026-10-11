# Viral Step 7 MASTER_EN C2a independent implementation re-review

- Review kind: `implementation`
- Verdict: `ACCEPT_C2A`
- Goal id: `20260830-kb-creator-next-scenario`
- Step id: `7 / C2a structured MASTER_EN executor re-review`
- Timestamp: `2026-09-01T22:20:35.1046748+03:00` (`Europe/Moscow`)
- Role: independent critic, repository policy `gpt-5.5` / `high`
- Actual platform model / effort: `unavailable`
- Implemented or materially designed the candidate: `no`
- Orchestrator policy owner: `/root`, NRI main-chat orchestrator policy `gpt-5.6-sol` / `medium`; ownership did not transfer
- Assignment state: fresh independent C2a implementation re-review after Terra remediation; platform runtime remains `unavailable`
- Scoped override: sole allowed write was this immutable re-review receipt; builder, tests, config, source/reconstruction, verifier, candidate/output, canonical plan/context/status, MinerU, historical matrices, Git and release surfaces were read-only
- Release review fields: not applicable; this is not a release review and no frozen release candidate, release manifest, freeze evidence, release QA references, exclusions or release invalidation decision was reviewed
- Elapsed time at drafting checkpoint: approximately `00:02:29`
- Token use at drafting checkpoint: `171240`

## Files checked

- Prior reject receipt: `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_step7_master_en_c2a_implementation_review_20260901.md`
- Terra remediation receipt: `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_step7_master_en_c2a_review_remediation_20260901.md`
- `kb_creator/scripts/build_scenario_master_en.py`
- `kb_creator/tests/test_build_scenario_master_en.py`
- `kb_creator/working/viral/master_en/publication_config_v1.json`
- accepted v4 reconstruction pages reached by the current builder probes
- live `kb_creator/working/viral/master_en/` directory
- current Git status, read-only

## Current identities

- Builder: `2851993F8E0B7420706E38E3E781744375826A8E77886E3FB4B632D519FA79AF`
- Tests: `96460BE29C094AB7C2B3FBAF9A8E6C472C73619527856F53805DDE35D85D7B07`
- Publication config: `CEAA522F8ADA7EF2453D52F0DE4D098733EA5A7D55B12BE96694094891767BF3`
- Prior reject receipt: reviewed in full from the assigned worktree
- Terra C2a remediation receipt: reviewed in full from the assigned worktree

Config invariant probe:

- `accepted_v4_markdown` occurrences: `0`
- structured rows: `29`
- source units: `33`
- source unit keys: exactly `page`, `path`, `sha256`
- attached-note selectors: `11`

## Bounded suite

```text
python -B -m pytest -q -p no:cacheprovider kb_creator\tests\test_build_scenario_master_en.py
41 passed in 8.42s
```

The suite now includes direct coverage for the prior blocker classes: extra termination key, missing `record_count.count`, malformed attached-note selector, and missing/altered attached-note output with a self-consistent emitted ledger.

## Independent P1 reprobes

### Closed nested schemas

The three original schema mutations now reject during declaration validation:

- `extra_termination_key`: rejected with `structured termination closed schema mismatch`
- `missing_termination_count`: rejected with `structured termination closed schema mismatch`
- `bad_attached_note_shape`: rejected with `structured note selector closed schema mismatch`

Current implementation lines inspected:

- `build_scenario_master_en.py:251-259` closes termination by kind
- `build_scenario_master_en.py:260-262` closes each note selector as exact `kind,text`

### Attached-note evidence

All `11` current attached-note selectors produce row-level note evidence with exact binding owner, source page/range/SHA, final emitted range/SHA and emitted occurrence `1`.

Representative note evidence:

- Rumors preface: owner `viral-one-night-in-perla-exploring`, p20 source `[2752,2946)`, source SHA `5687729C36B6CE0EA6626849529CABE19862137BA2AA3E0E8844E7E8559BC375`, emitted `[70921,71114)`, emitted SHA `508E98AB7BFF43658E836D90A37B0DB6E2ED7684379DA010E51EB858EB780094`, occurrence `1`
- Lemon Grove post-note: owner `viral-isola-location-04-the-lemon-grove`, p36 source `[4836,4927)`, source SHA `F73364E15C83A7F789482841B66ECCFC98F39BBEDA86CD02489AADFCF6F152D5`, emitted `[143929,144019)`, emitted SHA `EE811DA46B4C38321B3BE2546E104CD840229A1864436376AEB8B4B61B8DFF07`, occurrence `1`
- Outdoor guidance first note: owner `viral-appendix-encounters`, p58 source `[48,658)`, source SHA `708FA8947C3DE5A93105B9E5D995A357FB402025D307EEAA7408429714A0C96E`, emitted `[242360,242969)`, emitted SHA `ED15B59A109485DB819238780865BE3A56005FC919B01CECAB386D53F559EDDB`, occurrence `1`

Direct negative reprobe deleted each of the 11 emitted notes with a self-consistent local emitted ledger. Every deletion failed as expected with `structured emitted note range mismatch`.

Direct negative reprobe altered each of the 11 emitted notes with a self-consistent local emitted ledger. Every alteration failed as expected with `structured emitted note range mismatch`.

Current implementation lines inspected:

- `build_scenario_master_en.py:352-359` resolves note source owner/range/SHA
- `build_scenario_master_en.py:360-370` resolves emitted note owner/range/SHA and exact occurrence

## Regression evidence

Two fresh temporary reader builds:

- identical: `true`
- bytes: `358622` and `358622`
- SHA-256: `17528F1543738CA5FAE1A215237B6F7476A9483B015D1C41889213DFA140B010`

Reader and structured invariants:

- anchors: `168`
- reader links: `237`
- reader assets: `107`
- structured units: `29`
- class split: `11` semantic tables / `10` semantic cards / `2` semantic statblocks / `6` visual forms
- xrefs: `237` executed ids, `237` unique ids, `41` source links
- conservation: `1935` total / `1862` owned / `73` generated / `0` unowned / `0` duplicate / `0` unauthorized suppression

Outdoor order remains correct:

- p58 `viral-appendix-encounters-outdoor` `[1593,1959)` -> emitted `[243978,244323)`
- p58 `viral-appendix-encounters-outdoor-cold-spot` `[1959,4108)` -> emitted `[244400,246535)`
- p59 `viral-appendix-encounters-outdoor` `[26,955)` -> emitted `[246538,247465)`
- Hospital follows after the Outdoor root/child/root sequence

Reliquae order remains correct:

- p66 root `[1319,2303)` -> emitted `[280677,281155)`
- p67 root `[26,1103)` -> emitted `[281158,282290)`
- p67 Infection child `[1103,1308)` -> emitted `[282376,282580)`
- p67 Infection child `[1309,1585)` -> emitted `[282582,282857)`

Six visual forms remain exact once in their owner blocks:

- `viral-structure-pregen-marco-front` -> `viral-pregen-marco-front`, occurrence `1`
- `viral-structure-pregen-corrina-front` -> `viral-pregen-corrina-front`, occurrence `1`
- `viral-structure-pregen-enoch-front` -> `viral-pregen-enoch-front`, occurrence `1`
- `viral-structure-pregen-peter-front` -> `viral-pregen-peter-front`, occurrence `1`
- `viral-structure-pregen-ku-hyeon-front` -> `viral-pregen-ku-hyeon-front`, occurrence `1`
- `viral-structure-pregen-blank-front` -> `viral-pregen-blank-front`, occurrence `1`

No durable candidate/output sidecar was present in `kb_creator/working/viral/master_en`; live listing showed only `publication_config_v1.json`. A focused scan of the reviewed builder/test files found only expected acceptance-sidecar refusal/policy references and did not find MinerU, verifier, or historical `371/490` execution surfaces.

## Findings

No P0, P1 or P2 findings remain for this bounded C2a implementation surface.

Residual boundary note: this acceptance covers the structured temporary reader executor only. It is not C2b, not durable candidate acceptance, not user reading acceptance, not full visual QA, and not a release review.

## Blockers

None within the assigned C2a implementation re-review scope.

## Recommendation

`ACCEPT_C2A`.

Next gate: orchestrator may proceed to the next separately scoped Step 7 gate for durable candidate/C2b work, including independent verifier/candidate controls as required. Release review and user/publication acceptance remain closed until their own frozen-candidate evidence exists.

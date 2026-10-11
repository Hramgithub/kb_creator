# GPT-5.5 critic receipt - Viral v2 B1c4 implementation rereview

## Receipt metadata

- Review kind: `implementation`.
- Candidate state: non-frozen B1c4 asset implementation checkpoint; no release
  candidate was reviewed.
- Implemented or materially designed candidate: no.
- Role: `nri-independent-critic` / requested `gpt-5.5` / high.
- Actual platform model / effort: unavailable.
- Orchestrator policy owner: main chat, `gpt-5.6-sol` / medium; orchestration
  ownership did not transfer.
- Assignment state: matched to assigned implementation-rereview packet;
  platform runtime identity remains unverified.
- Scoped override: exact task packet
  `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/TASK_PACKET_gpt55_critic_viral_v2_complete_authoring_phase_b1c4_implementation_rereview_20260903.md`,
  SHA-256 `2918D451DA084665CB4E7F0BB59EA99ACDCC31D84C63F58FD3E56F0691C6AEA6`.
- Timestamp: `2026-09-03T15:31:57.6211547+03:00` (Europe/Moscow).
- Elapsed time: approximately 40 minutes before receipt write.
- Token use: unavailable.
- Files changed: only this immutable rereview receipt.

## Files checked

- Root `AGENTS.md`.
- `docs/governance/nri_goal_governance.md`.
- Assigned rereview packet: SHA-256
  `2918D451DA084665CB4E7F0BB59EA99ACDCC31D84C63F58FD3E56F0691C6AEA6`.
- Original implementation-review packet: SHA-256
  `C8CA9473BDD6C7C03E278381AC37999AA8D1CD9DDA5E197F0F7AC2086B070ACF`.
- Blocking implementation review receipt: SHA-256
  `D20415E2B888A3370C00071991A16EE9919312F3F2659D80C0374D91ABBF85A1`.
- Approved architecture receipt: SHA-256
  `A68A643CEBCF11BFBC3F358A900F3677309C02A8D410AB29B4861D62DAEB6442`.
- Parent remediation packet: SHA-256
  `61C6AC7752618EFA510B25B84049D300E76C3919493C5FB84C8CF0F9EA27990D`.
- Continuation remediation packet: SHA-256
  `4188992330DD0180FD744E047FF020EB7880792B6216FD9B34BF658CCBDC5E39`.
- Partial remediation receipt: SHA-256
  `25D4F0B8397F019FBCCCCE1B5FAA6D7C376B4FE264537DB8291DB998AEE70E06`.
- Continuation remediation receipt: SHA-256
  `FD33C9F31C956FAA6A440C6EC7F636112E283B99A7902F718501C183A8DAEC7D`.
- Error-taxonomy addendum receipt: SHA-256
  `92EA06C32F773B3ECBDAAB0B17BE38E8266E9619C7CEA5DFD32A17E1C3CF9097`.
- `kb_creator/scripts/author_viral_master_en_v2_config.py`: SHA-256
  `FFE2202E0FC2CB2FCD36FCA802C8484057E714704B734027B6AD25B17F0C9249`.
- `kb_creator/tests/test_author_viral_master_en_v2_config.py`: SHA-256
  `A019999265B17005775D801E4D5DF8E83A540959F402F8837705069C58D7386F`.
- `kb_creator/scripts/build_scenario_master_en.py`: SHA-256
  `DB1CA64720E8A9525CA5F9483E4EB57444913FF83B6FAD7EAA12777752E2C367`.
- `kb_creator/tests/test_build_scenario_master_en.py`: SHA-256
  `DE1CC0AC1A20EF20A47C55F5771BBEA68B8BC67DB1B770D51F6F1F86118941C6`.
- `kb_creator/scripts/verify_scenario_master_en.py`: SHA-256
  `B5EDA81F746501116F305952F173A05C64192FC15BD1E8CBCFC573FBFED203B2`.
- `kb_creator/tests/test_verify_scenario_master_en.py`: SHA-256
  `C357DCB7EAD79F9BAFEE836514466150FFD11954F75C980D4106294AF6F5B7E6`.

## Evidence

- Bound packet, receipt and final six-file identities matched the rereview
  packet. I did not stop for identity drift.
- Six-file syntax gate passed:
  `python -m py_compile kb_creator/scripts/author_viral_master_en_v2_config.py kb_creator/tests/test_author_viral_master_en_v2_config.py kb_creator/scripts/build_scenario_master_en.py kb_creator/tests/test_build_scenario_master_en.py kb_creator/scripts/verify_scenario_master_en.py kb_creator/tests/test_verify_scenario_master_en.py`.
- Focused combined suite passed:
  `python -m unittest -q kb_creator.tests.test_author_viral_master_en_v2_config kb_creator.tests.test_build_scenario_master_en kb_creator.tests.test_verify_scenario_master_en`;
  result `Ran 122 tests in 129.497s`, `OK`.
- Frozen-v1 builder preflight passed with contract SHA-256
  `67688867D4971D55137C2E4E7A71A746199596EDE4F5DD18577F4331CA87536D`,
  reconstruction inventory SHA-256
  `68C17FB765A89C6146398868E61F1F6EB7B2FE4EAFBA8C2C2C8F42260BBDBA83`,
  source SHA-256
  `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05`,
  status `preflight_passed`.
- Frozen-v1 verifier preflight passed with publication config SHA-256
  `C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30`,
  status `preflight_passed`.
- Guarded UUID temporary public-v2 preflight pair reached the exact declared
  seam and removed the temp config: builder exit `1`,
  `v2 visual review coverage mismatch`; verifier exit `1`,
  `E_V2_REVIEW: coverage`; temp path existed after cleanup: `False`.
- Positive independent probes reproduced frozen outcomes
  `99 retained_unchanged / 2 retained_rebound / 16 reclassified /
  6 excluded_advertising`, provenance
  `16 markdown_image_reference / 100 visual_region /
  9 reviewed_provisional_full_page`, final assets `125 = 93 reader +
  32 evidence_only`, and `8` new targets with `16` unique replacement children.
- Direct mutation probes showed binary SHA drift and missing binary now fail at
  B1c4-specific gates in both builder and verifier. Replacement graph mutations
  for foreign child, child order swap, target order swap, forged target,
  decision substitution, evidence substitution, source-row decision swap,
  exclusion target leakage and replaced-child reader leakage also fail at
  B1c4-specific gates.
- The prior taxonomy addendum case was reproduced: omitting one asset migration
  row now fails at builder `v2 B1c4 migration count mismatch` and verifier
  `E_V2_MIGRATION: count`, not the earlier generic
  `v2 migration count mismatch`.
- No-output sweep: canonical
  `kb_creator/working/viral/master_en/publication_config_v2.json` absent;
  `.phase-b1c*.json` count `0`; Candidate D absent. The nine protected roots
  remained present:
  `.c2b-unittest.staging.6fenuxm0`,
  `.c2b-unittest.staging.ak72wr18`,
  `.c2b-unittest.staging.ji7arodf`,
  `.c2b-unittest.staging.jic5ciws`,
  `viral-master-en-candidate-20260901-a`,
  `viral-master-en-candidate-20260901-b`,
  `viral-master-en-candidate-20260902-c`,
  `viral-master-en-scratch-20260902-1`,
  `viral-master-en-scratch-20260902-2`.

## Severity findings

### P1 - Borrowed binary and provenance remain accepted until the later visual-review seam

Affected invariant: rereview requirements 1, 2, 3, 4 and 5; original review
questions 3, 4, 9 and 10. The public B1c4 validators must bind each logical
asset declaration to the exact frozen source row and its expected accepted-v4
binary/provenance, not merely to any real accepted-v4 binary plus internally
consistent provenance.

Evidence:

- Builder lines `445` through `472` validate each declared B1c4 provenance
  object and binary in isolation. For visual regions, line `466` finds a
  manifest row by the declared binary SHA and line `468` verifies that the
  declared comparison block matches that manifest row. This proves the borrowed
  binary/provenance pair is real, but not that it belongs to the declared
  `asset_id`.
- Builder lines `482` through `487` then compare each declared asset back to
  the frozen row only by presence, `source_page`, `migration_outcome`, and
  replaced-child disposition. They do not compare declared binary path/bytes/
  SHA/dimensions, provenance kind, manifest row, Markdown span, comparison
  block or source asset reference against the expected row for that `asset_id`.
- Verifier lines `518` through `545` and `557` through `562` implement the same
  acceptance shape independently: the borrowed evidence is validated as real
  evidence, but is not bound back to the exact logical asset row.

Direct adversarial probe:

```text
first asset:  viral-accepted-e1e2aa6964b45037691d92e4faf91dba6bbd411e409dc49c237f6b0e71e6ce85
second asset: viral-accepted-a1d83a711a4b7962110b1ba158b2d610043f1fa836e06458e675373094acd6c1
mutation: keep first asset_id/source_page/outcome/disposition, but replace its
          binary and provenance object with the second asset's valid binary and
          valid visual_region provenance.
builder:  ValueError: v2 visual review coverage mismatch
verifier: ValueError: E_V2_REVIEW: coverage
```

Both assets are page-1 `retained_unchanged` rows, so broad counts, source page
and outcome remain stable. The mutation is self-consistent as evidence, but
source-wrong for the declared asset id. It should fail at the B1c4 asset
identity/provenance gate. Reaching the later visual-review seam means the
original borrowed/fake evidence P1 is not fully remediated.

Bounded remediation: builder and verifier must independently recompute the
expected per-asset B1c4 declaration table from frozen v1, accepted-v4 manifest,
comparison JSON, Markdown marker spans and source-PDF metadata. For every
declared asset id, compare the exact expected binary path, bytes, SHA-256,
media type, dimensions, provenance kind, Markdown span or comparison block,
source asset reference, page, bbox/block hash, render recipe and migration
outcome before the visual-review gate. Add symmetric public tests that borrow
binary plus provenance from another valid asset on the same page/outcome and
require B1c4-specific rejection.

## Blockers

This P1 blocks B1c4 implementation approval. Canonical v2 config authoring,
Candidate D, MASTER_RU, Step 8A binary selection, HTML/PDF generation,
downstream output and release acceptance remain unauthorized from this
checkpoint.

## Recommendation

Require changes in the six scoped implementation/test files only, centered on
per-logical-asset expected declaration comparison in both public validators and
symmetrical borrowed-evidence regression tests. Preserve the current
no-candidate/no-render/no-canonical-output boundary and rerun an independent
implementation rereview after remediation.

CHANGES_REQUIRED_V2_COMPLETE_AUTHORING_PHASE_B1C4_IMPLEMENTATION

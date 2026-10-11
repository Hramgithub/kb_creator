# GPT-5.5 critic receipt - Viral v2 B1c4 implementation review

## Receipt metadata

- Review kind: `implementation`.
- Candidate state: non-frozen B1c4 asset implementation checkpoint; no release candidate was reviewed.
- Implemented or materially designed candidate: no.
- Role: `nri-independent-critic` / requested `gpt-5.5` / high.
- Actual platform model / effort: unavailable.
- Orchestrator policy owner: main chat, `gpt-5.6-sol` / medium; orchestration ownership did not transfer.
- Assignment state: matched to assigned implementation-review packet; platform runtime identity remains unverified.
- Scoped override: exact task packet `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/TASK_PACKET_gpt55_critic_viral_v2_complete_authoring_phase_b1c4_implementation_review_20260903.md`, SHA-256 `C8CA9473BDD6C7C03E278381AC37999AA8D1CD9DDA5E197F0F7AC2086B070ACF`.
- Timestamp: `2026-09-03T14:27:00+03:00` (Europe/Moscow).
- Elapsed time: approximately 8 minutes before receipt write.
- Token use: 124,789 at pre-receipt goal checkpoint; exact final turn usage unavailable inside the immutable receipt.
- Files changed: only this immutable receipt.

## Files checked

- Root `AGENTS.md`.
- `docs/governance/nri_goal_governance.md`.
- Assigned review packet: SHA-256 `C8CA9473BDD6C7C03E278381AC37999AA8D1CD9DDA5E197F0F7AC2086B070ACF`.
- Engineering packet `TASK_PACKET_terra_engineering_viral_v2_complete_authoring_phase_b1c4_asset_engineering_20260903.md`.
- Approved architecture `sol_architect_viral_v2_complete_authoring_phase_b1c4_asset_closure_20260903.md`: SHA-256 `A68A643CEBCF11BFBC3F358A900F3677309C02A8D410AB29B4861D62DAEB6442`.
- Architecture approval `gpt55_critic_viral_v2_complete_authoring_phase_b1c4_asset_architecture_review_20260903.md`: SHA-256 `ACD54FF5C7819F922308EFDC05B87CBF000A122028CE7CE736D980C1AA4A7ED3`.
- Engineering receipt `terra_engineering_viral_v2_complete_authoring_phase_b1c4_asset_engineering_20260903.md`: SHA-256 `9E5799222BBB7A6C1266194DF18E287715F86F36A4451C93DE5A4FB68F1B4DCA`.
- User-review registry `kb_creator/docs/plans/20260830-kb-creator-next-scenario/USER_REVIEW_TYPICAL_PROBLEMS_20260902.md`: SHA-256 `D20414D48405A761ADD31E538B6940F8A3E0F1FB11044AF73EAD122D96C616E8`.
- Frozen v1 config `kb_creator/working/viral/master_en/publication_config_v1.json`: SHA-256 `C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30`.
- Source PDF `kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf`: SHA-256 `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05`.
- `kb_creator/scripts/author_viral_master_en_v2_config.py`: SHA-256 `6E0E704B8921B9339C50FA7C7A6687C4ADCBF9C4230558A7B93BF1A65FC6EB1B`.
- `kb_creator/tests/test_author_viral_master_en_v2_config.py`: SHA-256 `4BDF8D71D200C6F0ECAF22D21C615BF2DF878BE9B4ACCD56A6E67A7BD1202904`.
- `kb_creator/scripts/build_scenario_master_en.py`: SHA-256 `BDD0D2568D79DE468FECC2FF04276C91448F84A47FAF6709C06C1F2C956746CA`.
- `kb_creator/tests/test_build_scenario_master_en.py`: SHA-256 `093DCC3385AA976045EE48D1A1B2C78B846C90682983C0E87C16E6023DCE5689`.
- `kb_creator/scripts/verify_scenario_master_en.py`: SHA-256 `DDE50D8335EDA60D715054B2C96FE0008E8F20FA774AFCF49FBE026AA3BF30AC`.
- `kb_creator/tests/test_verify_scenario_master_en.py`: SHA-256 `8FA0B9E1D35A52875BE4CC666451892AEE48A25FA3A60CE441DC1EBD96819232`.

## Evidence

- Bound identities matched. I did not stop for identity drift.
- Six-file syntax gate passed: `python -m py_compile` over the six scoped implementation/test paths.
- Combined author/builder/verifier baseline passed: `Ran 119 tests in 90.470s`, `OK`.
- Frozen-v1 builder preflight passed with contract SHA-256 `67688867D4971D55137C2E4E7A71A746199596EDE4F5DD18577F4331CA87536D`, reconstruction inventory SHA-256 `68C17FB765A89C6146398868E61F1F6EB7B2FE4EAFBA8C2C2C8F42260BBDBA83`, source SHA-256 `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05`, status `preflight_passed`.
- Frozen-v1 verifier preflight passed with publication config SHA-256 `C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30`, status `preflight_passed`.
- Guarded UUID temporary public-v2 preflights reached the declared seam and removed the temp config: builder exit `1`, `v2 visual review coverage mismatch`; verifier exit `1`, `E_V2_REVIEW: coverage`; `.phase-b1c-author-*.json` absent afterward.
- Positive author probe reproduced `123` audit rows, `121` path-backed binaries, outcome counts `99 retained_unchanged / 2 retained_rebound / 16 reclassified / 6 excluded_advertising`, and final projection `125 = 93 reader + 32 evidence_only`.
- Positive author probe showed each current B1c4 asset declaration has only `asset_id`, `binary`, `disposition`, `migration_outcome`, `provenance_kind`, and `source_page`; there is no closed `provenance` object in the public declaration.
- Forbidden-output checks: `kb_creator/working/viral/master_en/publication_config_v2.json` absent; guarded temp config absent.
- Protected candidate/staging roots present and not removed: `.c2b-unittest.staging.6fenuxm0`, `.c2b-unittest.staging.ak72wr18`, `.c2b-unittest.staging.ji7arodf`, `.c2b-unittest.staging.jic5ciws`, `viral-master-en-candidate-20260901-a`, `viral-master-en-candidate-20260901-b`, `viral-master-en-candidate-20260902-c`, `viral-master-en-scratch-20260902-1`, `viral-master-en-scratch-20260902-2`.

## Severity findings

### P1 - Public builder/verifier do not bind B1c4 asset declarations to truthful provenance or binary identity

Affected invariant: review questions 3, 4, 9 and 10; architecture requirement for a closed provenance union and independent builder/verifier validation of all 121 path-backed binaries against path, bytes, SHA-256, image magic, decoded dimensions, accepted-v4 manifest and comparison evidence.

Evidence:

- Author declaration at `kb_creator/scripts/author_viral_master_en_v2_config.py:356` through `372` emits only `provenance_kind` plus an optional `binary` object. It does not emit the architecture-required closed `provenance` union for `markdown_image_reference`, `visual_region`, `reviewed_provisional_full_page`, or `excluded_advertising`.
- Builder top-level schema at `kb_creator/scripts/build_scenario_master_en.py:445` through `451` accepts that simplified shape. A `visual_region` asset with `binary = None` is accepted by the schema.
- Verifier top-level schema at `kb_creator/scripts/verify_scenario_master_en.py:505` through `508` mirrors the same simplified acceptance.
- Builder/verifier real-input audit functions recompute counts from frozen v1 and accepted-v4 bytes, but the public config validation does not compare each declared asset binary/provenance declaration back to that audit before falling through to the later visual-review seam.

Direct adversarial probe results:

```text
asset_binary_sha_mutation builder ValueError v2 visual review coverage mismatch
asset_binary_sha_mutation verifier ValueError E_V2_REVIEW: coverage
asset_binary_missing builder ValueError v2 visual review coverage mismatch
asset_binary_missing verifier ValueError E_V2_REVIEW: coverage
positive_has_no_provenance_object builder ValueError v2 visual review coverage mismatch
positive_has_no_provenance_object verifier ValueError E_V2_REVIEW: coverage
```

The mutated config should have failed at B1c4 asset identity/provenance validation. Instead both public validators accepted the mutation until the intentional later review-coverage seam.

Bounded remediation: declare the full closed `provenance` object for every B1c4 asset row and require builder/verifier, independently and before review coverage, to validate each declaration against the accepted-v4 manifest, comparison block, Markdown span or source-PDF full-page recipe, including path/bytes/SHA/magic/dimensions and no borrowed/fake text provenance.

### P1 - Replacement graph and migration decisions are validated by counts/families, not exact prescribed row/target identity

Affected invariant: review questions 5, 6, 7, 8 and 10; architecture requirement that every replacement child exists, belongs to the prescribed page/slot/owner, occurs exactly once and in prescribed order, with no omission, duplication, foreign id, borrowed child, target swap, decision swap or evidence-identity substitution.

Evidence:

- Builder replacement closure at `kb_creator/scripts/build_scenario_master_en.py:1237` through `1257` requires 8 targets, 16 unique child strings and `viral-accepted-` prefixes, but does not compare target ids, target order, child ids, child target membership, page/slot/owner, or prescribed child order against the architecture table.
- Verifier replacement closure at `kb_creator/scripts/verify_scenario_master_en.py:445` through `463` implements the same relaxed logic independently.
- Builder/verifier migration decision logic at `build_scenario_master_en.py:1247` through `1251` and `verify_scenario_master_en.py:453` through `457` derives expected decision from the supplied row's current `outcome` and frozen page. It does not bind the exact OUT-006/OUT-007/OUT-024/OUT-025/OUT-026 memberships from the approved row list.
- B1c4 tests only assert positive real-input counts/path-binary totals in `test_build_scenario_master_en.py:143` through `147`, `test_verify_scenario_master_en.py:145` through `149`, and `test_author_viral_master_en_v2_config.py:64` through `71`. I found no B1c4 negative tests for foreign child, target swap, same-page membership swap, target id forgery, or exclusion membership swap.

Direct adversarial probe results:

```text
foreign_child builder ValueError v2 visual review coverage mismatch
foreign_child verifier ValueError E_V2_REVIEW: coverage
child_swap_between_targets builder ValueError v2 visual review coverage mismatch
child_swap_between_targets verifier ValueError E_V2_REVIEW: coverage
forged_target_id builder ValueError v2 visual review coverage mismatch
forged_target_id verifier ValueError E_V2_REVIEW: coverage
same_page_membership_swap builder ValueError v2 visual review coverage mismatch
same_page_membership_swap verifier ValueError E_V2_REVIEW: coverage
exclusion_membership_swap builder ValueError v2 visual review coverage mismatch
exclusion_membership_swap verifier ValueError E_V2_REVIEW: coverage
```

The probes preserved broad counts and shape while violating exact B1c4 row or replacement identity. They should have failed at B1c4 migration/replacement validation, not at the later review-coverage seam.

Bounded remediation: encode the approved exact B1c4 migration/replacement table as an independently recomputed validator in builder and verifier. Validate exact target ids, target order, source pages, physical unit ids, slot/owner/accessibility obligations, `replaces` child ids and child order, exact OUT memberships, exclusion source rows, evidence identity, and absence of reader output/event leakage for replaced children and exclusions. Add corresponding public mutation tests in both builder and verifier.

## Blockers

The implementation cannot be approved for B1c4 because unresolved P1 findings remain. This blocks canonical v2 config authoring, Candidate D, MASTER_RU, Step 8A binary selection, HTML/PDF generation, downstream output, and any release acceptance claim from this checkpoint.

## Recommendation

Require changes in the six scoped implementation/test files only. Preserve the current no-candidate/no-render/no-canonical-output boundary and rerun the same independent implementation review after remediation.

CHANGES_REQUIRED_V2_COMPLETE_AUTHORING_PHASE_B1C4_IMPLEMENTATION

# Task packet — independent Viral v2 B1c4 asset implementation review

## Governance and role

- Goal id: `20260830-kb-creator-next-scenario`.
- Review kind: `implementation`, not architecture and not release.
- Assigned role: `nri-independent-critic`, canonical repository profile
  `gpt-5.5` / `high`.
- Orchestrator owner remains the main `gpt-5.6-sol` / `medium` chat.
- The critic must not implement, repair, redesign, create a canonical config,
  build a candidate, render assets, mutate Git state, or edit plan/context.
- The only authorized write is the immutable review receipt:
  `gpt55_critic_viral_v2_complete_authoring_phase_b1c4_implementation_review_20260903.md`
  in this handoff directory.

## Exact review inputs

- Engineering packet:
  `TASK_PACKET_terra_engineering_viral_v2_complete_authoring_phase_b1c4_asset_engineering_20260903.md`.
- Approved architecture:
  `sol_architect_viral_v2_complete_authoring_phase_b1c4_asset_closure_20260903.md`,
  SHA-256 `A68A643CEBCF11BFBC3F358A900F3677309C02A8D410AB29B4861D62DAEB6442`.
- Architecture approval:
  `gpt55_critic_viral_v2_complete_authoring_phase_b1c4_asset_architecture_review_20260903.md`,
  SHA-256 `ACD54FF5C7819F922308EFDC05B87CBF000A122028CE7CE736D980C1AA4A7ED3`.
- Engineering receipt:
  `terra_engineering_viral_v2_complete_authoring_phase_b1c4_asset_engineering_20260903.md`,
  SHA-256 `9E5799222BBB7A6C1266194DF18E287715F86F36A4451C93DE5A4FB68F1B4DCA`.
- User-review registry:
  `../USER_REVIEW_TYPICAL_PROBLEMS_20260902.md`.
- Frozen v1 config:
  `../../../../../working/viral/master_en/publication_config_v1.json`,
  SHA-256 `C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30`.
- Accepted reconstruction package aggregate identity:
  `68C17FB765A89C6146398868E61F1F6EB7B2FE4EAFBA8C2C2C8F42260BBDBA83`.
- Immutable source PDF SHA-256:
  `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05`.

Review the final bytes of these six scoped implementation/test paths:

```text
kb_creator/scripts/author_viral_master_en_v2_config.py
  6E0E704B8921B9339C50FA7C7A6687C4ADCBF9C4230558A7B93BF1A65FC6EB1B
kb_creator/tests/test_author_viral_master_en_v2_config.py
  4BDF8D71D200C6F0ECAF22D21C615BF2DF878BE9B4ACCD56A6E67A7BD1202904
kb_creator/scripts/build_scenario_master_en.py
  BDD0D2568D79DE468FECC2FF04276C91448F84A47FAF6709C06C1F2C956746CA
kb_creator/tests/test_build_scenario_master_en.py
  093DCC3385AA976045EE48D1A1B2C78B846C90682983C0E87C16E6023DCE5689
kb_creator/scripts/verify_scenario_master_en.py
  DDE50D8335EDA60D715054B2C96FE0008E8F20FA774AFCF49FBE026AA3BF30AC
kb_creator/tests/test_verify_scenario_master_en.py
  8FA0B9E1D35A52875BE4CC666451892AEE48A25FA3A60CE441DC1EBD96819232
```

If any bound identity differs, stop with a P1 identity finding rather than
reviewing a moving target.

## Required independent review questions

The review must inspect code and run direct adversarial probes, not merely
accept the engineering receipt or rerun the happy path.

1. Prove the exact frozen conservation model:
   `99 retained_unchanged + 2 retained_rebound + 16 reclassified +
   6 excluded_advertising = 123`.
2. Prove the final declaration model:
   `125 = 93 reader + 32 evidence_only`, with eight new provisional full-page
   targets and no advertising leakage.
3. Prove truthful closed provenance alternatives for all frozen rows:
   `16 Markdown spans + 100 visual regions + 1 provisional full-page render +
   6 excluded`, without fake text spans or borrowed evidence.
4. Prove all 121 path-backed binaries against path, bytes, SHA-256, image magic,
   decoded dimensions, accepted-v4 manifest and comparison evidence.
5. Prove the exact eight-target/sixteen-child replacement graph: every child
   exists, belongs to the prescribed page/slot/owner, occurs exactly once and
   in prescribed order; no omission, duplication, foreign id, borrowed child,
   target swap, decision swap or evidence-identity substitution is accepted.
6. Prove the two `OUT-005` rebounds, `OUT-006`, `OUT-007`, `OUT-024`,
   `OUT-025` and six `OUT-026` exclusions are bound by exact source row/page
   membership, not a permissive decision-family check.
7. Prove replaced children and all six exclusions cannot emit as reader assets,
   while required retained/new targets cannot silently become evidence-only.
8. Prove marker/event placement and duplication closure, including p3 logo,
   p31 city then p32 boat immediately before `Prologue`, map pages 106/107,
   pregen pages 111/112 through 121/122 and zero p123/p124 reader leakage.
9. Prove builder and verifier implement independent validation and stable,
   distinct error mapping; neither may import or trust the author's closure.
10. Exercise meaningful positive and negative mutations for row counts,
    dispositions, provenance kind/identity, binary identity, replacement graph,
    decision/evidence identity, placement/order, reader/evidence classification,
    targetless exclusions and excluded-page leakage.
11. Confirm frozen-v1 behavior remains green and its config identity unchanged.
12. Confirm public unmutated v2 preflights reach exactly the next intentional
    seam and no earlier/later seam:
    builder `v2 visual review coverage mismatch` and verifier
    `E_V2_REVIEW: coverage`.
13. Confirm no canonical `publication_config_v2.json`, UUID temp config,
    candidate, render, asset, review bundle or downstream output was created.
    Preserve and distinguish the nine enumerated pre-existing candidate/staging
    roots; do not delete or alter them.

## Minimum commands and evidence

- Recompute all bound SHA-256 identities.
- Run six-file `py_compile`.
- Run the combined author/builder/verifier baseline; the orchestrator directly
  reproduced `119` passing tests on the bound bytes.
- Run both frozen-v1 preflights.
- Generate only guarded ephemeral in-memory/UUID test material where required,
  remove it, and independently exercise both public v2 preflight paths.
- Add direct mutation probes beyond existing tests where needed. Do not retain
  temporary configs or outputs.
- Inspect scoped diff/status and verify the review itself changed only its
  assigned receipt.

## Decision contract

The receipt must state one terminal token:

- `APPROVED_V2_COMPLETE_AUTHORING_PHASE_B1C4_IMPLEMENTATION`, only if there are
  no unresolved P0/P1/P2 findings; or
- `CHANGES_REQUIRED_V2_COMPLETE_AUTHORING_PHASE_B1C4_IMPLEMENTATION`, with
  severity, exact evidence, affected invariant and bounded remediation.

Approval is only for this B1c4 implementation checkpoint. It is not permission
to author the canonical v2 config, build Candidate D, start MASTER_RU, perform
Step 8A binary selection, generate HTML/PDF or claim release acceptance.

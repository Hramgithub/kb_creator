# Task packet — independent review of Viral v2 complete authoring Phase A1b

## Role and boundary

- Role: `nri-independent-critic` / GPT-5.5 / high.
- Review kind: implementation review; do not implement or materially redesign.
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`.
- Write exactly one new receipt:
  `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_v2_complete_authoring_phase_a1b_review_20260903.md`.
- Do not edit code, tests, config, source/reconstruction inputs, plan/context, candidates, Git index, commits, or outputs.

## Bound evidence

- Architecture receipt:
  `sol_architect_viral_v2_complete_publication_authoring_20260903.md`, SHA-256
  `39F9B514F82ABAAD58D0A637E07C395206E57BED7106864EC0247A9477E24ADC`.
- Identity approval:
  `gpt55_critic_viral_v2_reconstruction_identity_rereview_20260903.md`, SHA-256
  `0B4F6D13D082284CA7186816FF80843DB11B2F4BFB66DFB956438D6B6E334D71`.
- A1b engineering receipt:
  `terra_engineering_viral_v2_complete_authoring_phase_a1b_recovery_20260903.md`, SHA-256
  `2DD8839D6DB1B2FFF251634966E0E3D35A6DC570B4B9E3076F8EF2A6C4DED1A5`.
- Builder SHA-256:
  `28F1A0F1CDA3F735230E777E1288EB1824ABDECEC2DC54A184259212091F3D29`.
- Independent verifier SHA-256:
  `690405B68B15A797667DEF5678F86CC709111C4D39123747209732DAE0E118DC`.
- Builder tests SHA-256:
  `CC2571C4FCA15D5A5CC31B484A70E07E48DFF2E25FB9CD42B9DB00E812BCB873`.
- Verifier tests SHA-256:
  `96EC119D4959594E7E42D7387073BD7907FFEF0AAFE730696B973BEA839D5FF1`.
- Frozen v1 config SHA-256:
  `C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30`.

## Required review

Review the two implementations independently, not only the tests. Confirm the
closed `source_partition` contract proves exact source coverage for reader
pages 1..122:

1. canonical safe page/path binding and exact page sequence;
2. UTF-8/no-BOM byte decoding, byte offsets, decoded-character offsets, raw
   bytes hash and decoded-text hash;
3. ordered adjacency, zero gaps/overlaps, and exact page/full-document byte
   coverage;
4. closed EOL profiles plus recomputed page/document byte, line, nonblank and
   EOL aggregates;
5. scalar rejection, closed enums, unique span IDs, classification/owner rules;
6. builder/verifier parity without the verifier importing builder validation;
7. deterministic negative mutations for boundary, ordering, path/page, hashes,
   offsets, enums, IDs, EOL and aggregate drift.

Run at least:

- `python -B -m py_compile` for the two scripts and two test modules;
- `python -B -m unittest -q kb_creator.tests.test_build_scenario_master_en kb_creator.tests.test_verify_scenario_master_en`;
- the established four-module baseline including visual QA and semantic-unit
  proposer tests;
- real frozen-v1 builder and verifier `--preflight-only` checks;
- forbidden-output checks: no real `publication_config_v2.json`, no accepted-v4
  input `INVENTORY.json`, and no candidate/scratch leftovers created by review.

## Decision

- Approve only if there are no P0/P1 findings in this A1b scope.
- Terminal line on approval:
  `APPROVED_V2_COMPLETE_AUTHORING_PHASE_A1B`.
- Otherwise terminal line:
  `CHANGES_REQUIRED_V2_COMPLETE_AUTHORING_PHASE_A1B` and list exact findings,
  affected paths/lines, missing proof/tests and the minimal remediation boundary.
- State explicitly that approval authorizes only Phase A2 migration engineering;
  A3, real v2 config, candidate build and release remain closed.

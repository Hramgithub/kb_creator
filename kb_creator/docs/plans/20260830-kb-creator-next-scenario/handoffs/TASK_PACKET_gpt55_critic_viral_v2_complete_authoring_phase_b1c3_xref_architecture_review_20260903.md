# Task packet — independent review of Viral v2 B1c3 xref architecture

## Role and scope

- Role: `nri-independent-critic` / GPT-5.5 / high.
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`.
- Review only the B1c3 xref-closure architecture against current code,
  accepted evidence, prior approved v2 architecture and governance.
- Own only one receipt:
  `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_v2_complete_authoring_phase_b1c3_xref_architecture_review_20260903.md`.
- Do not edit architecture, code/tests, plan/context, config/candidates,
  inputs/evidence, Git or downstream.
- The critic must not implement or materially redesign the work under review.

## Bound identities

- Architecture packet:
  `94A3F6EAFA7F7FBB32574CAA36F524DD48937DB6E4CD50E11507577E2A492346`.
- Architecture receipt:
  `A859B3B2B3B413D7626CE7FD478D9519F798D282ED0E4CB7CFEF863C74769D58`.
- B1c2 receipt/helper/tests:
  `AD46004F0C6C21942C051A183323CBDCB427CAE14BEB0DD678730751A64F7736`,
  `AA5D7DA9A22E81AF79F1DC6056FDAD74675E4B45B9C57716E7E3444763C40C8D`,
  `2489E4E11B6366DF07004374E88379EA646CA52A2605C7A77AA41180D86ACE84`.
- Approved builder/verifier:
  `2C2A5A998C55FEF07B141CC6D146A2CD40302F7E95679E1DF1272385C7DD346B`,
  `7FD59EF3BB2BCB01E9DB943FB8921F7AF7C95C79D3873379A8167153C59F06F8`.

Refuse on drift.

## Review questions

Independently verify, with direct evidence rather than trusting receipt claims:

1. the frozen-v1 inventory really decomposes into 42 source segments, 194
   retained generated items and two excluded advertising rows;
2. the 236 materialized-item / 235 emitted-link / one non-link model conserves
   all 237 frozen rows and does not silently lose reader navigation;
3. a closed generated-navigation schema extension is necessary and does not
   weaken A3 source binding or let free labels/targets enter the candidate;
4. the four generated event families, exact owners/counts/order and OUT-002
   decision are semantically correct;
5. both advertising rows/targets are correctly governed by OUT-026;
6. the null-decision mechanical split exception is sufficiently narrow and
   cannot bypass ordinary decision-reference requirements;
7. the four coarse multi-owner events really require and deterministically
   produce the specified 34-event topology without byte loss/reuse;
8. the alias/migration namespace rules close all materialized targets and do
   not permit root fallback, implicit matching, cycles or fan-out;
9. the required independent builder/verifier behavior and negative-test matrix
   are adequate before any canonical config or candidate exists;
10. the expected next asset-provenance seam is consistent with current public
    gate order.

Classify findings P0/P1/P2. Any incorrect count, missing conservation path,
unbound generated text/target, weakened source invariant, insufficient split
guard, or untestable acceptance criterion is at least P1. Do not approve based
only on plausibility or green existing tests.

End with exactly one terminal decision:

- `APPROVED_V2_COMPLETE_AUTHORING_PHASE_B1C3_XREF_ARCHITECTURE`, or
- `CHANGES_REQUIRED_V2_COMPLETE_AUTHORING_PHASE_B1C3_XREF_ARCHITECTURE`.

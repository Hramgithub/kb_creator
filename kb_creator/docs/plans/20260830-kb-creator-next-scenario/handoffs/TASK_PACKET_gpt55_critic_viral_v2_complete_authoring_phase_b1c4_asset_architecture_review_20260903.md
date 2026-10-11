# Task packet — independent review of Viral v2 B1c4 asset architecture

## Role and scope

- Role: `nri-independent-critic` / GPT-5.5 / high.
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`.
- Independently review the B1c4 asset architecture; do not implement or
  materially redesign it.
- Own only receipt
  `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_v2_complete_authoring_phase_b1c4_asset_architecture_review_20260903.md`.
- All other files are read-only. Refuse on drift.

## Bound inputs

- Architecture packet:
  `7D63519464780D7E8DFB456F354D5D9CCA8C6C5504F873FB083E5038C8E7D554`.
- Architecture receipt:
  `A68A643CEBCF11BFBC3F358A900F3677309C02A8D410AB29B4861D62DAEB6442`.
- B1c3 implementation approval:
  `4F37A4E75CAE7CB6E786F6D72D80A73D9062C6582E5378EC642C417B5281F960`.
- Current author/builder/verifier and tests are the six hashes recorded in the
  architecture packet and must remain unchanged.
- Canonical v2 config/candidates are absent.

## Required independent review

Recompute from frozen-v1, accepted reconstruction, evidence ledgers and source
PDF metadata rather than trusting receipt tables:

1. the exact 123-row frozen inventory and mutually exclusive outcomes
   `99 retained_unchanged + 2 retained_rebound + 16 reclassified + 6 excluded`;
2. the primary provenance counts `16 Markdown spans + 100 visual regions + 1
   provisional full-page + 6 excluded`, including the two non-path rows;
3. the final inventory `125 = 93 reader + 32 evidence`, eight new reviewed
   full-page targets and conservation of all 123 inputs without silent drops;
4. every member of the 16 reclassified and six excluded sets against OUT-006,
   OUT-007, OUT-024, OUT-025 and OUT-026;
5. the two OUT-005 retained-rebound placement corrections and the exact p3,
   p31/p32, p6 and platform/promo regression decisions;
6. all 16 child ids in the eight-target `replaces` graph exactly once, with
   correct map/pregen physical units/pages/slots and no duplicated reader crop;
7. the necessity and closedness of the discriminated provenance union,
   including exact frozen visual-region selected-view/raw-index/bbox identity,
   binary/path/digest/media/dimension closure and no empty/fake text span;
8. whether the marker/event placement rules prove source order for all assets,
   not only the named regressions, and whether 16 Markdown plus visual-region
   provenance can be independently re-derived by builder and verifier;
9. whether provisional full-page renders are truthful Step 7 representations
   and preserve logical ids/roles/page pairs for later post-MASTER_RU Step 8A;
10. whether the migration/new-reviewed target namespace, decision refs,
    materialized closure, candidate-copy rules and negative matrix are complete,
    and whether the claimed next visual-review-coverage seam follows current
    gate order.

Run direct/adversarial probes as needed. Any wrong row membership/count,
unbound visual region, ambiguous owner/placement, duplicate/missing replacement,
invented provenance, unverifiable new render, common-mode builder/verifier
trust, or untestable acceptance rule is at least P1. Classify all findings
P0/P1/P2; do not approve based on internal arithmetic alone.

End with exactly one terminal decision:

- `APPROVED_V2_COMPLETE_AUTHORING_PHASE_B1C4_ASSET_ARCHITECTURE`, or
- `CHANGES_REQUIRED_V2_COMPLETE_AUTHORING_PHASE_B1C4_ASSET_ARCHITECTURE`.

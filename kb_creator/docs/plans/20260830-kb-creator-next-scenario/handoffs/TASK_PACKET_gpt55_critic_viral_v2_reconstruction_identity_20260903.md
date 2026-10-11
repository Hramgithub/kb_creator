# Task packet: independent review of Viral v2 reconstruction identity

## Role

- Owner: `nri-independent-critic` (`gpt-5.5`, high).
- Independent review only; do not implement or redesign material under review.
- You are not alone in the worktree. Do not revert or modify implementation,
  tests, config, inputs, candidates, plan/context or Git.

## Review target

- Architecture receipt
  `sol_architect_viral_v2_reconstruction_identity_20260903.md`, SHA-256
  `83C917A4A75DBFA8F1EC88ACC5C7248B6D6F772534DD4905DAB9971035664F5D`.
- Engineering receipt
  `terra_engineering_viral_v2_reconstruction_identity_20260903.md`, SHA-256
  `5426D05F9C9A5EBA4197F6E698D77E171C6369191EF63B08F06FFAF2E40EE35F`.
- Exact implementation/test paths listed in the engineering receipt.

## Required review

1. Inspect implementation and tests; independently run the focused modules and
   both real v1 preflights.
2. Recompute real-v4 known-answer and confirm no package mutation/input
   `INVENTORY.json` creation.
3. Review safe-root/topology/all-file aggregate/count/bytes/digest/page-binding
   order separately in builder and verifier; verify no verifier import/trust of
   builder helper.
4. Verify legacy `reconstruction_inventory` is rejected, exact closed
   `reconstruction_package` is required, helper cannot write config, v1 is
   unchanged, and candidate-output inventory semantics are unchanged.
5. Inspect negative coverage against the architecture matrix. Identify any
   missing P0/P1 case, silent weakening, TOCTOU/material topology issue or first
   error mismatch.
6. Confirm that this checkpoint does not claim to solve the 39.2% publication
   completeness blocker and creates no config/candidate.

## Output

Write only
`kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_v2_reconstruction_identity_review_20260903.md`.
List evidence, tests, P0/P1/P2 findings, exact remediation if needed and terminal
`APPROVED_V2_RECONSTRUCTION_IDENTITY` only with no unresolved P0/P1; otherwise
`CHANGES_REQUIRED_V2_RECONSTRUCTION_IDENTITY`. Include receipt SHA and token use
when available. No Git.

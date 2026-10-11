# Task packet: fresh Viral v2 identity rereview

## Role and scope

- Owner: fresh `nri-independent-critic` (`gpt-5.5`, high).
- Review only; do not implement or modify any file except assigned receipt.
- You are not alone in the worktree; do not revert others or touch Git.

Review exact architecture, initial critic and remediation receipts:

- architecture SHA
  `83C917A4A75DBFA8F1EC88ACC5C7248B6D6F772534DD4905DAB9971035664F5D`;
- changes-required receipt SHA
  `C7657199B24463149693DFBF420FDFC6209ECBEED007E0C33AFFB3C05CD815BE`;
- remediation receipt SHA
  `32FECDA76A8ADB26A7785DF1182D6E95C062CE3F3891A3C526A8BE28DB2E31F0`.

Bind the four exact implementation/test hashes recorded in context/receipt.
Verify the P1 is closed in both builder and independent verifier: unsafe lexical
root remains distinct; missing configured/CLI root, file, non-directory and
wrong directory map to stable domain errors; builder CLI emits no traceback.
Run the five targeted cases, inspect portable P2 mutation additions, both real
v1 preflights and absence of config/candidate/input inventory. Confirm no
regression to candidate-output inventory and no claim that completeness is
solved.

## Output

Write only
`kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_v2_reconstruction_identity_rereview_20260903.md`.
Return `APPROVED_V2_RECONSTRUCTION_IDENTITY` only with no unresolved P0/P1;
otherwise `CHANGES_REQUIRED_V2_RECONSTRUCTION_IDENTITY`. List P2 separately,
include exact tests/hashes and receipt SHA/token use. No long silent test phase:
send a checkpoint before commands expected to exceed one minute.

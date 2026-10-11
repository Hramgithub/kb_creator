# Task packet — independent review of Viral v2 complete authoring Phase A2

## Role and scope

- Role: `nri-independent-critic` / GPT-5.5 / high.
- Review kind: implementation; do not implement or materially redesign.
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`.
- Write exactly one receipt:
  `gpt55_critic_viral_v2_complete_authoring_phase_a2_review_20260903.md`.
- Do not edit code/tests/config/inputs/evidence/plan/context/candidates/Git or
  downstream output.

## Bound evidence

- Architecture SHA-256:
  `39F9B514F82ABAAD58D0A637E07C395206E57BED7106864EC0247A9477E24ADC`.
- A1b approval SHA-256:
  `0D99E9B4F9B70F93D66118C555D2C2ED0077587360DD2A3027B532CD3FBAA23C`.
- A2 engineering receipt SHA-256:
  `663BF432F80E81563FE5AA4BF0331B15047FCBF9DCCA51F3F37CCCAE47A48F96`.
- A2 remediation-v1 receipt SHA-256:
  `AE7BCC12062FC03CA8A0B30610B6C9C230EE7E74CE0DAB7BFEDF6161F9079D40`.
- A2 remediation-v2 receipt SHA-256:
  `050C0B9EC2BE6572A6AE94855E1509A73769DEE3B06B54D4F6CB5ED23654BB37`.
- Final files:
  - builder `B9A90CA83517505EB1B56D77ACA5338EA05058EFAC3F60CE6E4383F4F9DC6530`;
  - verifier `B7108E64E2166F84654D8C0A88C2233831A4C5CF30BB3D92CC2B3886588E8F6B`;
  - builder tests `3FD17110C0A00727DBF52790865FF13759B987B37CB838B6F7933ABD3DB3D99C`;
  - verifier tests `D851C4317D7E2E793A1A55CA262CC0F109CE110B237FBB201C199282AD8E97E7`.
- Frozen v1 config SHA-256:
  `C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30`.

## Required review

Inspect builder and verifier independently. Verify:

1. `migration` is closed and contains exact bound inputs, six exhaustive
   ledgers and closed `new_reviewed_targets`;
2. canonical full-v1-row hashing/source IDs independently prove exactly
   `168/123/237/124/41/29` source rows with zero missing/duplicate/substitute;
3. outcome subsets are domain-correct; final target namespaces/uniqueness and
   materialized hierarchy/assets/xrefs closure are fail-closed;
4. every non-unchanged outcome/new target has an exact decision identifier from
   the bound decision artifacts. Scrutinize the current implementation's
   evidence-membership algorithm: plain substring occurrence in arbitrary
   UTF-8 evidence is not sufficient if it permits prefixes, common words,
   scenario ids, or text outside structured decision-id fields. Test a
   near-match/prefix/common-substring mutation and classify as P1 if an invalid
   decision ref passes;
5. `retained_unchanged` accepts no decision and cannot pass real preflight until
   A3 proves immutable-field parity; `pending_a3:domain:id` is closed and does
   not become a bypass;
6. asset 123-row conservation, evidence/reader policy, duplicate logical
   representation and pages 123/124 exclusions are actually enforceable at
   this seam or explicitly fail closed pending A3;
7. page-123/124 source dispositions are targetless `excluded_advertising`;
8. unsafe input paths/topology and input bytes/SHA substitutions are rejected;
9. verifier does not import builder validation and equivalent mutations fail
   both implementations;
10. remediation only repaired stale test closures and did not weaken gates.

Run py-compile, exact 77-test two-module suite, four-module baseline, both real
v1 preflights, scoped diff-check, and forbidden-output checks. Add focused
read-only probes when necessary; leave no scratch/candidate output.

## Decision

- `APPROVED_V2_COMPLETE_AUTHORING_PHASE_A2` only with no P0/P1 and only if the
  partial pending-A3 boundary is sound enough for A3 implementation.
- Otherwise `CHANGES_REQUIRED_V2_COMPLETE_AUTHORING_PHASE_A2` with exact
  finding, reproduction, paths/lines and minimal remediation.
- State that even approval authorizes only A3 engineering; real v2 config,
  candidate, visual QA, release and publication remain closed.

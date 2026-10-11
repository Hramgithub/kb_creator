# Task packet — fresh independent Viral v2 Phase A2 rereview

## Role and boundary

- Role: `nri-independent-critic` / GPT-5.5 / high.
- Review kind: implementation rereview; do not implement/materially redesign.
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`.
- Write exactly one receipt:
  `gpt55_critic_viral_v2_complete_authoring_phase_a2_rereview_20260903.md`.
- Do not edit code/tests/config/inputs/evidence/plan/context/candidates/Git or
  downstream output.

## Bound evidence

- Architecture: `39F9B514F82ABAAD58D0A637E07C395206E57BED7106864EC0247A9477E24ADC`.
- A1b approval: `0D99E9B4F9B70F93D66118C555D2C2ED0077587360DD2A3027B532CD3FBAA23C`.
- Initial A2 receipt: `663BF432F80E81563FE5AA4BF0331B15047FCBF9DCCA51F3F37CCCAE47A48F96`.
- Initial A2 critic rejection: `37C5FD7B91140CB2AE566B0E634014764FCD23191DBD1BFA4E2654089C2297CC`.
- Integration recovery: `216F029F5CDA287E23BCA501FD9C27C673E504A07A877389A1F0EEEA67C9F614`.
- Collision finding receipt: `DAAEE694C9A4BECADD7B595467403D54907E572D444E145438FA8C245263F6F9`.
- Final provenance-collision remediation:
  `BB1B822DFE3712E3F452B2F34153F38CCD01461732411007AE5CA3112080829E`.
- Final full mutation matrix:
  `77247ACFE2F66BF6791103245EBF43EFBF35577C07BF192D86B28C42BE1B1123`.
- Final files:
  - builder `76DDF943D84B23A60578189F2E1C808D4606AD67028FFCCE76E0DD50418C4E3F`;
  - verifier `938A6D3635E2078D20D09A32F9792808915E23CE909D1C7BDDD81ACB08B36CFE`;
  - builder tests `F117173CD23F95E0BEE86D45813F2E2418EC7147B80C8C8E31C4F4ADE94D5D35`;
  - verifier tests `94D5CC6D27D0B93EFCB58058C8B1FF8F37FA579AADD95C4ABC7CB83491FEBD51`.
- Frozen v1 config: `C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30`.

## Required rereview

Inspect builder/verifier independently and rerun adversarial probes. Confirm:

1. all original A2 closed migration invariants remain: bound inputs, exact six
   ledgers/counts `168/123/237/124/41/29`, canonical complete-row hashes,
   domain outcome subsets, unique/closed targets, p123/p124 exclusions,
   pending-A3 preflight block and no verifier import of builder validation;
2. exact structured decision-id extraction supports only the four approved
   kinds and their explicitly enumerated fields/shapes;
3. the original common-token P1 is closed: `reader`, `viral`, field names,
   prefix/suffix/case/near matches and prose-only occurrences fail both;
4. singleton semantic/registry/closure catalog provenance and multi-ledger
   provenance are correctly enforced;
5. compatible candidate corroboration (semantic+boundary) and registry
   corroboration (registry+boundary+closure) pass, while same-kind duplicate
   catalogs, cross-ledger repeated declarations and incompatible declaration
   classes fail;
6. boundary target-unit ids are same-file references, not independent
   declarations, and missing/foreign targets fail;
7. invalid schemas/extra keys/wrong row types/invalid UTF-8/JSON/empty and
   duplicate catalogs/closure blocking inconsistency fail both;
8. test-only stale-fixture corrections did not weaken production gates.

Run py-compile, exact 89-test focused/four-module baseline, both real-v1
preflights, scoped diff-check and forbidden-output checks. Add read-only probes
for `reader`, duplicate same-kind catalog and incompatible class. Leave no
scratch/candidate artifacts.

## Decision

- Approve only with no P0/P1:
  `APPROVED_V2_COMPLETE_AUTHORING_PHASE_A2`.
- Otherwise:
  `CHANGES_REQUIRED_V2_COMPLETE_AUTHORING_PHASE_A2_REREVIEW` with exact
  reproduction, paths/lines and minimal remediation.
- Even approval authorizes only Phase A3 engineering. Real v2 config/helper,
  candidate, visual QA, release and publication remain closed.

# Task packet — Viral v2 A2 structured decision evidence completion

- Same `nri-engineer` / GPT-5.6-terra / medium and worktree.
- Preserve unrelated edits. Own only the two scripts, two focused tests and new
  receipt
  `terra_engineering_viral_v2_complete_authoring_phase_a2_decision_ref_completion_20260903.md`.
- Do not edit prior receipts/helper/config/evidence/inputs/A3/candidates/plan/
  context/Git/downstream output.

The P1 remediation receipt SHA-256 is
`EDFD37D9919D94CEF5338666C40A564CBCF2C08F6A6D3F55AAA924CBF9E95362`,
but it implements only semantic-review JSON and registry Markdown. The assigned
packet also required production decision evidence from approved boundary
ledgers and closure report. This omission blocks rereview because unit ids are
the final reviewed boundary decisions; candidate ids/registry refs alone do not
prove the selected merged/split/final owner unit.

Add independent closed extractors for:

1. `kb_creator.viral_boundary_ledger.v1`, admitting exact values only from:
   - `units[*].id`;
   - `units[*].registry_refs[*]`;
   - `candidate_dispositions[*].candidate_id`;
   - `candidate_dispositions[*].target_unit_id` only when it exactly names a
     unit id present in the same file;
   - `deferred_nonblocking[*].registry_ref`;
   reject unknown keys/shapes at each parsed decision-bearing row and reject a
   target unit absent from `units`.
2. `kb_creator.semantic_unit_closure.v2`, admitting exact ids only from
   `deferred_nonblocking[*]` and no prose/identity/common fields. Validate its
   exact closed production shape sufficiently to prevent alternative-field
   injection; zero unresolved blocking candidates/count must be consistent.

Keep exact-equality/no-casefold behavior. Reject ids present only in arbitrary
`evidence`, `reason`, `scope`, identity or title text. Add equivalent builder
and verifier positives using tiny valid fixtures and negatives for field
injection, missing target unit, free-text-only id, unsupported/extra keys,
prefix/suffix/common tokens, duplicate ids and cross-file collision if the same
id resolves to incompatible decision-bearing objects.

Re-run py-compile, the expanded focused and four-module suites, both v1
preflights and diff-check; verify forbidden outputs absent.

Terminal `READY_FOR_V2_COMPLETE_AUTHORING_PHASE_A2_REREVIEW` only when all four
production evidence kinds are implemented and tested; otherwise
`CHANGES_REQUIRED_V2_COMPLETE_AUTHORING_PHASE_A2_DECISION_REF_COMPLETION`.

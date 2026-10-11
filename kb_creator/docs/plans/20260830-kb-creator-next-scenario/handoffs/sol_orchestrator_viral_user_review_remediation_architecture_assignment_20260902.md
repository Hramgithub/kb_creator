# Viral user-review remediation architecture assignment

- goal_id: `20260830-kb-creator-next-scenario`
- step_id: `7-user-review-remediation-architecture`
- contributor role: `nri-architect`
- requested model/effort: repository profile `gpt-5.6-sol` / `high`
- orchestrator policy owner: `gpt-5.6-sol` / `medium`
- assignment state: `matched`
- scoped override: `none`

## Goal

Turn the completed user review registry into an executable, reusable remediation
specification for a successor Viral `MASTER_EN` build. Identify the earliest
failing layer for every in-scope defect class and define minimal code, test,
config/policy and rebuild work without patching generated Markdown by hand.

## Authoritative inputs

- `../USER_REVIEW_TYPICAL_PROBLEMS_20260902.md` — all OUT/PROC entries and final
  user decisions;
- `../plan.md` and `../context.md` — canonical goal state and boundaries;
- `kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4/`;
- `kb_creator/working/viral/master_en/publication_config_v1.json` — frozen
  evidence, not an authorized mutation target;
- `kb_creator/reference/viral/master_en/publication_config_v1.json` — immutable
  preserved reference;
- current reusable scripts/tests under `kb_creator/scripts/` and
  `kb_creator/tests/`;
- source PDF is immutable.

## Required output

Write an immutable architecture receipt/specification to:

`handoffs/sol_architect_viral_user_review_remediation_spec_20260902.md`

It must include:

1. a closure matrix for OUT-001 through OUT-026 and PROC-009 through PROC-026,
   explicitly distinguishing defects, accepted presentation decisions,
   non-blocking future improvements and the Step 8A-only art-finalization work;
2. earliest failing layer, reusable fix, Viral policy/config delta and regression
   evidence for every in-scope class;
3. exact proposed file ownership for the Terra implementation task, with a
   minimal ordered slice plan that avoids conflicting edits;
4. successor artifact strategy: never mutate Candidate C, retained scratch
   packages, accepted/reference config or source reconstruction; name the new
   config/candidate/evidence roots;
5. acceptance criteria and focused test commands, followed by full real rebuild,
   independent verification, visual QA and fresh GPT-5.5/high review;
6. explicit handling of pages 123–124 as `excluded_advertising` while preserving
   124-page reconstruction/audit evidence;
7. explicit boundary between semantic visual-unit correction in Step 7 and
   binary-quality candidate choice in Step 8A.

## Forbidden scope

- Do not edit code, tests, config, source reconstruction, candidates, plan,
  context, registry, Git index, commits or remote state.
- Do not start MASTER_RU, Step 8A implementation, HTML, PDF or production.
- Do not treat user examples as isolated manual patches.

## Completion condition

Return `READY_FOR_REMEDIATION_IMPLEMENTATION` only if the required receipt exists
and the specification closes the full registry without contradictions. Otherwise
return `BLOCKED` with exact missing evidence.

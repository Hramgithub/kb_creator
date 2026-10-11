# Viral user-review remediation engineering assignment

- Goal: `20260830-kb-creator-next-scenario`
- Step: `7-user-review-remediation-implementation`
- Owner: `nri-engineer`, repository profile `gpt-5.6-terra` / `medium`
- Orchestrator: main `gpt-5.6-sol` / `medium`
- Architecture receipt: `sol_architect_viral_user_review_remediation_spec_20260902.md`
- Required completion token: `READY_FOR_REMEDIATION_QA`

## Objective

Implement the complete, sequential five-slice contract in the architecture
receipt. Add reusable prevention/serialization/verification controls, build the
candidate-first semantic audit tooling and closed Viral v2 policy/evidence.
Do not build the real successor candidate; the Luna execution gate owns that.

You are not alone in the worktree. Preserve and accommodate every pre-existing
change. Do not revert, clean, stage, commit or modify files outside the exact
ownership below.

## Exclusive owned paths

Existing code/tests:

- `kb_creator/scripts/compare_mineru_three_views.py`
- `kb_creator/tests/test_mineru_three_view_tools.py`
- `kb_creator/scripts/materialize_mineru_ai_merge.py`
- `kb_creator/tests/test_materialize_mineru_ai_merge.py`
- `kb_creator/scripts/finalize_mineru_reconstruction.py`
- `kb_creator/tests/test_finalize_mineru_reconstruction.py`
- `kb_creator/scripts/build_scenario_master_en.py`
- `kb_creator/tests/test_build_scenario_master_en.py`
- `kb_creator/scripts/verify_scenario_master_en.py`
- `kb_creator/tests/test_verify_scenario_master_en.py`
- `kb_creator/scripts/build_master_en_visual_qa_bundle.py`
- `kb_creator/tests/test_build_master_en_visual_qa_bundle.py`

New code/tests and policy/evidence:

- `kb_creator/scripts/propose_scenario_semantic_units.py`
- `kb_creator/tests/test_propose_scenario_semantic_units.py`
- `kb_creator/working/viral/master_en/publication_config_v2.json`
- `kb_creator/working/viral/master_en/review_evidence/20260902_user_review_remediation_v1/`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_user_review_remediation_20260902.md`

## Required implementation

Follow sections `Publication v2 data contract`, `Closure matrix`, `Candidate-first
semantic audit required for current Viral`, `Exact Terra ownership and ordered
implementation slices`, `Pages 123-124: exact exclusion contract` and `Step 7
versus Step 8A boundary` in the architecture receipt. All OUT-001..OUT-026 and
PROC-009..PROC-026 dispositions are authoritative.

Run the five slices in the specified order. Keep v1 behavior compatible and
derive all v2 counts from declarations. Builder and verifier must remain
independent. Use typed serialization for tables/callouts/cards/statblocks and a
global source-ordered event graph. Candidate proposals require closed review
decisions before materialization. Add focused regressions for every blocking
closure row and for v1 compatibility.

The evidence root must contain exactly the required semantic candidates,
closed review, compact review HTML and closure report. It is run-local evidence,
not a publication surface.

## Protected and forbidden scope

Read-only, byte-preserved:

- source PDF;
- accepted reconstruction v4 and all its sidecars/assets;
- working and reference `publication_config_v1.json` (expected SHA-256
  `C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30`);
- Candidate C and both retained scratch candidates;
- all unrelated dirty worktree paths.

Forbidden:

- editing generated `MASTER_EN.md` by hand;
- building Candidate D or the two deterministic remediation scratch candidates;
- final PDF XObject extraction/selection (Step 8A only);
- MASTER_RU, HTML, PDF or production work;
- Git staging, commit, push, cleanup or deletion;
- editing `plan.md`, `context.md`, the review registry or architecture receipt.

## Verification and receipt

Run the focused seven-module pytest command from the architecture receipt, plus
any narrower tests useful during implementation. Run v2 builder and verifier
preflight only; do not create the real scratch/candidate roots.

Write the immutable receipt at the exact owned path above. Include:

- exact changed paths;
- mapping from every blocking OUT/PROC record to code/config/test evidence;
- focused test and preflight commands/results;
- frozen-v1 hash checks and protected-root non-mutation evidence;
- semantic review coverage and unresolved candidates;
- blockers/risks and next action;
- actual model/effort if available, elapsed time and token use (`unavailable`
  when unavailable).

Return `READY_FOR_REMEDIATION_QA` only if all owned implementation and tests are
complete with zero unresolved blocking semantic candidate. Otherwise return a
precise blocker without broadening scope.

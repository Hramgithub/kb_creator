# Viral reuse-preservation independent critic assignment — 2026-09-02

- `goal_id`: `20260830-kb-creator-next-scenario`
- `step_id`: `preservation-first-commit-review`
- `review_kind`: `implementation`
- `orchestrator`: `gpt-5.6-sol` / policy effort `medium`
- `contributor`: independent critic `gpt-5.5` / requested effort `high`
- `assignment_state`: `matched`
- `scoped_override`: none

## Objective

Independently decide whether the first preservation commit boundary safely
captures reusable MinerU reconstruction work and Viral declarative reference
data without including generated evidence, misleading scenario-bound code,
foreign dirty changes, or any release/acceptance claim.

## Authorities

- architecture review:
  `kb_creator/docs/architecture/KB_CREATOR_SCENARIO_PIPELINE_REUSE_REVIEW_20260902.md`;
- completed engineering receipt:
  `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineer_viral_reuse_preservation_resume_20260902.md`;
- current working-tree diff/status and the exact allowlist below.

## Exact candidate allowlist

```text
.gitignore
.agents/skills/kb-creator-scenario-reconstruction/SKILL.md
kb_creator/contracts/innsmouth.json
kb_creator/contracts/scenario_contract.v1.schema.json
kb_creator/contracts/viral.json
kb_creator/reference/viral/master_en/publication_config_v1.json
kb_creator/reference/viral/README.md
kb_creator/docs/KB_CREATOR_PIPELINE_SUMMARY_20260830.md
kb_creator/docs/architecture/KB_CREATOR_SCENARIO_PIPELINE_REUSE_REVIEW_20260902.md
kb_creator/docs/plans/20260830-kb-creator-next-scenario/scenario_contract_architecture.md
kb_creator/scripts/audit_mineru_ai_merge_fidelity.py
kb_creator/scripts/compare_mineru_three_views.py
kb_creator/scripts/materialize_mineru_ai_merge.py
kb_creator/scripts/prepare_mineru_three_view_inputs.py
kb_creator/scripts/run_mineru_three_view.ps1
kb_creator/tests/test_audit_mineru_ai_merge_fidelity.py
kb_creator/tests/test_materialize_mineru_ai_merge.py
kb_creator/tests/test_mineru_three_view_tools.py
```

## Required review

1. Inspect every allowlisted file and current `.gitignore` diff.
2. Confirm the five scripts and three tests are clean-checkout portable and
   scenario-neutral; a single focused `pytest -p no:cacheprovider` rerun is
   permitted.
3. Confirm the skill is routing/policy only, correctly excludes downstream
   publication, and has valid front matter/paths.
4. Confirm the frozen reference config is byte-identical to working config and
   truthfully documented as Viral-specific/non-self-contained.
5. Confirm no source PDF, overlay, candidate, working/reconstruction payload,
   visual bundle, scratch/staging root, raw transcript, repetitive receipt,
   generic-named Viral executable/test, secret, absolute device path or foreign
   tracked change is required by or present in the candidate allowlist.
6. Treat the missing Candidate C `MASTER_EN.md` as a separate known blocker.
   Verify this commit neither repairs, reseals, accepts nor releases Candidate C.
7. Return `APPROVE_PRESERVATION_COMMIT`, `REJECT_PRESERVATION_COMMIT`, or
   `BLOCKED`, with P0-P3 findings and exact remediation.

## Sole write

`kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_reuse_preservation_review_20260902.md`

The receipt records role/model/effort, participation declaration, scope,
evidence, findings, exclusions, verdict, timestamp, elapsed/token status and
next action.

## Forbidden scope

- no edits outside the sole receipt;
- no Git staging/fetch/commit/push/branch mutation;
- no Candidate C/scratch/config/source/reconstruction mutation or recovery;
- no MASTER_RU/HTML/PDF/production work;
- do not rewrite architecture/engineering receipts or canonical plan/context.

Other user/contributor changes are present. Do not revert, normalize or stage
them. The critic did not implement or materially design this package.

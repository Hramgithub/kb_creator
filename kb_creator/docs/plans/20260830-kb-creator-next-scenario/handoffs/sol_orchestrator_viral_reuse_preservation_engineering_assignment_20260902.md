# Viral reuse-preservation engineering assignment — 2026-09-02

- `goal_id`: `20260830-kb-creator-next-scenario`
- `step_id`: `preservation-portable-core-packaging`
- `orchestrator`: `gpt-5.6-sol` / policy effort `medium`
- `contributor`: engineer `gpt-5.6-terra` / requested effort `medium`
- `assignment_state`: `matched`
- `scoped_override`: none

## Architecture authority

Read and implement only the first-commit boundary in:

`kb_creator/docs/architecture/KB_CREATOR_SCENARIO_PIPELINE_REUSE_REVIEW_20260902.md`

## Objective

Package the already-created scenario-independent MinerU core, its repository
skill, the portable scenario contracts and the frozen Viral publication-policy
reference without changing any frozen working artifact.

## Allowed writes

- `.gitignore`: only narrow unignore rules required for `.agents/skills/**`,
  `kb_creator/contracts/**` and `kb_creator/reference/**`;
- replace the current draft
  `.agents/skills/kb-creator-scenario-production/SKILL.md` with the narrower
  `.agents/skills/kb-creator-scenario-reconstruction/SKILL.md` specified by the
  architecture review;
- byte-identical copy of
  `kb_creator/working/viral/master_en/publication_config_v1.json` to
  `kb_creator/reference/viral/master_en/publication_config_v1.json`;
- `kb_creator/reference/viral/README.md`;
- one completion receipt:
  `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineer_viral_reuse_preservation_20260902.md`.

Existing reusable scripts/tests, contracts, architecture docs and pipeline
summary are read-only in this step. If a P0/P1 defect requires changing one,
stop and report `BLOCKED`; do not expand scope.

## Required verification

1. Frozen reference copy: exactly 713,722 bytes and SHA-256
   `C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30`;
   original working config unchanged with the same identity.
2. Candidate C `MASTER_EN.md` remains
   `F486849BB6A2E8EE860F092C0AE691CD4780A08A8065BFF19C47B3BB0DC461D1`
   and `INVENTORY.json` remains
   `4745E245E754FEA89BCA753C9CD73F1B85C30CE07BFE65C2BF760ED7FF4352F7`.
3. Run only the three reusable synthetic modules:
   `test_mineru_three_view_tools.py`,
   `test_audit_mineru_ai_merge_fidelity.py`, and
   `test_materialize_mineru_ai_merge.py`.
4. Prove the five reusable scripts contain no Viral/Innsmouth/source hash,
   branch/HEAD, dated run root or device-local path.
5. Validate the final skill with the standard validator when possible; if its
   environment lacks PyYAML, record that and run the validator-equivalent
   structural checks without installing packages.
6. `git diff --check` for the allowed writes. Do not stage or commit.

## Forbidden scope

- no edits to any script, test, contract, Candidate C, working config, source,
  reconstruction package, plan/context/status/release or architecture review;
- no MASTER_RU/HTML/PDF/production work;
- no Git staging, fetch, commit, push, branch mutation or deletion of run data;
- do not move or publish the generic-named Viral executables or mutation suite;
- do not include handoffs beyond the one completion receipt.

Other work is present in the worktree. Do not revert, normalize, stage or
overwrite any user or concurrent contributor change.

## Completion condition

Return `READY_FOR_SCOPED_GIT_REVIEW` with exact changed paths, hashes, test
result and exclusions, or `BLOCKED` with a concrete P0/P1 issue.

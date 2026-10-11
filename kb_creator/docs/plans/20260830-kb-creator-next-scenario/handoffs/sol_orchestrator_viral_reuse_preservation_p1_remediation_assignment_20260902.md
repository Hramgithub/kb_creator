# Viral reuse-preservation P1 remediation assignment — 2026-09-02

- `goal_id`: `20260830-kb-creator-next-scenario`
- `step_id`: `preservation-p1-neutral-help-example`
- `orchestrator`: `gpt-5.6-sol` / policy effort `medium`
- `contributor`: engineer `gpt-5.6-terra` / requested effort `medium`
- `assignment_state`: `matched`
- `scoped_override`: none

## Finding authority

Independent GPT-5.5/high review receipt:
`gpt55_critic_viral_reuse_preservation_review_20260902.md`.

Verdict was `REJECT_PRESERVATION_COMMIT` for one P1: the otherwise reusable
`prepare_mineru_three_view_inputs.py` still uses `1-124` in CLI help text.

## Sole code write

In `kb_creator/scripts/prepare_mineru_three_view_inputs.py`, replace only the
scenario-shaped CLI example `1-124` with a neutral bounded example such as
`1-10`. Do not alter parsing or behavior.

## Required verification

1. Static scan of the five reusable scripts finds no `Viral`, `Innsmouth`,
   standalone `124`, admitted source hash/path, frozen branch/HEAD, dated run
   root or device-local path.
2. Run once with no cache:
   `python -B -m pytest -p no:cacheprovider` for
   `test_mineru_three_view_tools.py`,
   `test_audit_mineru_ai_merge_fidelity.py`, and
   `test_materialize_mineru_ai_merge.py`.
3. `git diff --check -- kb_creator/scripts/prepare_mineru_three_view_inputs.py`.
4. Confirm Candidate C, scratch packages, working/reference configs and all
   other allowlisted artifacts are unchanged.

## Sole receipt

`terra_engineer_viral_reuse_preservation_p1_remediation_20260902.md`

in the current handoffs directory.

## Forbidden scope

No other code, test, skill, config, contract, doc, candidate, source,
reconstruction, Git index/history, fetch/push, cleanup or downstream work.
Do not address the critic's P2 reports-ignore observation in this commit; exact
path staging is the accepted mitigation.

Other work is present. Do not revert or normalize concurrent/user changes.

## Completion

Return `READY_FOR_FRESH_CRITIC_REVIEW` or `BLOCKED` with exact evidence.

# kb_creator Pipeline Automation Review Context

Goal id: `20260913-kb-creator-pipeline-automation-review`

Status: completed

## Objective

Design a practical migration from the current agent-heavy, receipt-heavy
workflow to a user-runnable one-command artifact pipeline.

## Accepted Constraints

- Preserve all existing user changes and immutable sources.
- Review and planning only; do not implement or run the future pipeline.
- Do not delete historical tests, receipts, or reports in this goal.
- Final Git commit must be path-scoped to this review's own artifacts and the
  concise project-status update; push target is `main`.

## Current Evidence

- `README.md` describes a frozen Innsmouth v6 baseline and reproducibility
  command, while the live project has progressed through v7/source-to-artifacts,
  raw-PDF authority, page-proof, MinerU-first experiments, direct-master work,
  and next-scenario preparation.
- `PROJECT_STATUS.md` contains multiple historical/current narratives and is
  materially larger than a rollup should be.
- The active page-proof bundle has 438 handoff files across the plan tree; old
  resume text is superseded by later checkpoints and some later work exists
  only as untracked receipts.
- Recent commits show a real script-backed pipeline exists, but follow-on work
  frequently creates bespoke step scripts, matching one-off tests, and repeated
  review/authorization artifacts.
- Top-level Git is diverged and dirty; integration must remain surgical.

## Working Hypothesis

`kb_creator` has good low-level safety controls and trace evidence but lacks a
single product-level run contract. The same state is mirrored in scripts,
tests, receipts, plan/context/status prose, and reports. The migration should
retain fail-closed machine checks while collapsing routine transitions into a
declarative run specification, shared stage library, generated evidence index,
and a single CLI.

## Completed Evidence

- Architect receipt: `handoffs/architect_pipeline_automation_review_20260913.md`.
- Engineer receipt:
  `handoffs/engineer_test_script_consolidation_review_20260913.md`.
- Independent process critic receipt:
  `handoffs/critic_process_review_20260913.md`.
- Integrated report:
  `../../reviews/KB_CREATOR_PIPELINE_AUTOMATION_REVIEW_20260913.md`.

The three reviews agree that the missing product layer is a control plane, not
more extraction/build logic. Existing scripts should be wrapped behind a fixed
stage graph and shared manifests before any large builder rewrite.

## Blockers

None for the review. Implementation is intentionally not started. Release
approval is not applicable to a process/architecture report.

## Next Action

Start Wave 0 only as a new bundled implementation goal from a clean
`origin/main` baseline. The current review contains no implementation or
release acceptance.

# kb_creator Pipeline Automation Review Plan

Goal id: `20260913-kb-creator-pipeline-automation-review`

Status: completed

## Objective

Review the live `kb_creator` context, goals, plans, status, commits, scripts,
tests, review receipts, and generated artifacts. Identify duplicated tests and
reviews, manual operations, and missing orchestration. Produce a prioritized
implementation plan for a reproducible one-command pipeline that can be run by
the user without an AI orchestrator and emits a complete artifact package.

## Role Contract

- Governance: `docs/governance/nri_goal_governance.md`.
- Orchestrator policy owner: `gpt-5.6-sol`, medium; actual platform identity is
  unavailable, assignment state `platform-unverified`.
- Architect: `gpt-5.6-sol`, high, owns stage graph and root-cause analysis.
- Engineer: `gpt-5.6-terra`, medium, owns script/test consolidation analysis.
- Independent critic: `gpt-5.5`, high, owns process/review criticism and risk.
- Scoped override: none.

## Scope

- `kb_creator/README.md`, `PROJECT_STATUS.md`, `docs/plans/`, `docs/contracts/`.
- `kb_creator/scripts/`, `pdf_raw/`, `tests/`, `config/`, manifests, reports,
  working/output package boundaries, and recent `kb_creator` commits.
- Current user working tree is read-only except for this review bundle, the
  final review report, and the required concise project-status link.

Out of scope: implementing the target runner, processing a new PDF, changing
existing source/output artifacts, deleting historical evidence, or modifying
Foundry content.

## Work Plan

| Step | Owner | Dependency | Deliverable | Status |
|---|---|---|---|---|
| R1 | Orchestrator | none | Baseline inventory and current-state recovery | completed |
| R2 | Architect | R1 packet | Architecture receipt and target one-command stage graph | completed |
| R3 | Engineer | R1 packet | Script/test duplication receipt and consolidation seams | completed |
| R4 | Independent critic | R1 packet | Review/governance redundancy receipt and minimum safe gates | completed |
| R5 | Orchestrator | R2-R4 | Integrated prioritized automation report | completed |
| R6 | Orchestrator | R5 | Verification, status sync, narrow commit, and push to `main` | completed |

## Definition of Done

- Current workflow and debt are quantified from the live checkout.
- Tests are classified as reusable behavioral tests, fixture/contract tests,
  generated state assertions, one-off evidence, or duplicated checks.
- Reviews are reduced to explicit risk gates with independent release review
  preserved and routine mechanical checks delegated to scripts.
- Target CLI contract defines inputs, configuration, stages, caching/resume,
  deterministic outputs, QA, review queue, manifest, exit codes, and packaging.
- Migration waves identify what to build, consolidate, retain, archive later,
  and measure.
- Final Markdown report is committed narrowly and pushed to `main` without
  including unrelated user changes.

## Evidence Baseline

- Current branch observed: `main...origin/main [ahead 1, behind 8]`.
- Current `kb_creator` inventory observed: 29 Python scripts, 43 top-level
  Python test files, 457 plan-tree files, 438 handoff files, and a 1,612-line
  project status.
- Current tracked `kb_creator` changes and extensive untracked work belong to
  the user and must not enter this review commit.

## Result

Integrated report:
`kb_creator/docs/reviews/KB_CREATOR_PIPELINE_AUTOMATION_REVIEW_20260913.md`.

The accepted next implementation direction is Wave 0: create the package/core,
executable contracts, `doctor`/`preflight`, shared test support, and parity-wrap
one low-risk existing CLI from a clean `origin/main` baseline.

## Next Action

Implementation requires a new bundled goal starting with Wave 0 from a clean
`origin/main` baseline.

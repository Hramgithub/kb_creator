# Viral reuse-preservation architecture assignment — 2026-09-02

- `goal_id`: `20260830-kb-creator-next-scenario`
- `step_id`: `preservation-reuse-architecture`
- `orchestrator`: `gpt-5.6-sol` / policy effort `medium`
- `contributor`: architect `gpt-5.6-sol` / requested effort `high`
- `assignment_state`: `matched`
- `scoped_override`: none

## Objective

Classify the accumulated Viral pipeline work so reusable knowledge is preserved
without publishing run-local evidence or misrepresenting Viral-specific code as
generic infrastructure.

## Read scope

- `kb_creator/README.md`, `kb_creator/PROJECT_STATUS.md`;
- `kb_creator/docs/KB_CREATOR_PIPELINE_SUMMARY_20260830.md`;
- the untracked `kb_creator/scripts/*.py`, `*.ps1` and matching tests created by
  the Viral goal;
- `kb_creator/contracts/viral.json` and the current Viral goal plan/context;
- repository `.gitignore`, `.gitattributes`, and governance.

## Sole write

`kb_creator/docs/architecture/KB_CREATOR_SCENARIO_PIPELINE_REUSE_REVIEW_20260902.md`

The document also serves as the contributor receipt and must record role,
scope, evidence, blockers, recommendation, timestamp, elapsed/token status, and
the exact recommended Git include/exclude boundary.

## Required analysis

1. Separate reusable scenario-independent core, Viral reference implementation,
   run-local evidence, generated artifacts, and obsolete/unsafe material.
2. Identify misleadingly generic filenames or APIs that remain Viral-specific.
3. Recommend the smallest useful repo skill and the scripts/tests it should
   route to; do not duplicate code in the skill.
4. Define a scoped commit allowlist and explicit exclusions for source PDFs,
   overlays, candidates, visual bundles, scratch roots, raw transcripts, and
   repetitive receipts.
5. Flag P0-P2 correctness or portability issues that must be fixed before the
   preservation commit.

## Forbidden scope

- no edits to scripts, tests, configs, contracts, Candidate C, source or
  reconstruction packages;
- no MASTER_RU/HTML/PDF/production work;
- no Git staging, commit, fetch, push, branch, or deletion;
- no rewriting existing handoffs or canonical plan/context.

Other work may be present in the same worktree. Do not revert, normalize, or
stage edits made by other contributors or the user.

## Completion condition

The sole write exists, gives an evidence-backed classification table and exact
commit boundary, and reports either `READY_FOR_PRESERVATION_IMPLEMENTATION` or
`BLOCKED` with concrete blockers.

# Goal plan: model handoff

- Goal ID: `20261011-model-handoff`
- State: `completed`
- Objective: prepare a concise project summary and an operational specification
  that let another frontier model, including Claude Opus 5.5, understand and
  continue KB Creator without repeating the repository archaeology.
- Policy orchestrator: `gpt-6-sol`, medium reasoning.
- Actual orchestrator model/effort: unavailable.
- Role contract: NRI goal governance, current as of 2026-10-11.
- Scoped override: none.

## Ownership

| Step | Owner | Requested effort | Assignment state |
|---|---|---:|---|
| H1 source and repository audit | main-chat orchestrator | medium | completed |
| H2 architecture and dependency review | `gpt-6-astra` architect | high | completed; receipt captured |
| H3 summary/spec authoring and integration | main-chat orchestrator | medium | completed; candidate drafted |
| H4 bounded factual/coverage QA | `gpt-6-luna` QA | medium | completed; v02 pass |
| H5 independent release review of the frozen handoff | `gpt-6-astra` critic | high | completed; v03 approved |

The critic must not implement or materially design the handoff candidate.

## Inputs

- `kb_creator/README.md`
- `kb_creator/PROJECT_STATUS.md`
- the active and recently completed goal packets under `kb_creator/docs/plans/`
- CLI entry points, pipeline modules, schemas, tests, tracked inputs, reports,
  and deliverables in the standalone repository
- NRI governance and the verified standalone import commit

## Deliverables

- `kb_creator/docs/handoff/MODEL_HANDOFF_SUMMARY.md`
- `kb_creator/docs/handoff/MODEL_HANDOFF_SPEC.md`
- contributor receipts under this goal's `handoffs/` directory
- an updated `context.md` checkpoint

## Steps

1. Inventory the repository, active state, architecture, commands, dependencies,
   artifacts, acceptance boundaries, and known portability gaps.
2. Obtain a bounded architecture/dependency review.
3. Author the concise summary and the operational specification.
4. Run link/path/coverage checks and bounded QA.
5. Freeze the candidate and obtain independent critic review.
6. Present the uncommitted handoff to the user; commit or push only after an
   explicit request.

## Definition of Done

- A new model can identify the product purpose, pipeline stages, current state,
  repository map, important commands, invariants, acceptance gates, external
  dependencies, known risks, and the next safe action from the two documents.
- Claims about current state are tied to repository evidence and distinguish
  historical state from current authority.
- All referenced repository paths exist unless explicitly labelled external or
  intentionally absent from the standalone extraction.
- No temporary files, generated working trees, credentials, or local-only paths
  are added as handoff payloads.
- Bounded QA passes and the independent critic records a release recommendation.
- The standalone repository remains clean except for the intentional handoff
  goal packet and documents.

## Current status

Candidate v03 is independently approved for documentation handoff. The files
remain uncommitted; no commit or push is authorized for this goal.

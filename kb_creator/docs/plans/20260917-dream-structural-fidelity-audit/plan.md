# Number 7 Dream structural fidelity audit plan

Goal id: `20260917-dream-structural-fidelity-audit`

Status: completed

## Objective

Audit all 26 source pages against the Stage 06 reconstruction candidate after
the page 14 handout and page 18 stat-block failures exposed a missing semantic
structure defect class. Identify every confirmed loss of callout/sidebar,
letter/handout boundary, list, table/stat block, heading, or source-order
semantics before any promotion to MASTER_EN. Diagnose the regression in the
shared reconstruction pipeline, implement a scenario-neutral fail-closed
structural contract/audit, author a corrected immutable Dream decision set,
replay Stages 05-06, and verify the rebuilt candidate across the full document.

## Role contract

- Contract: `docs/governance/nri_goal_governance.md` current at goal start.
- Policy orchestrator: `gpt-5.6-sol`, medium; assignment state:
  `platform-unverified`; scoped override: none.
- Bounded QA: `gpt-5.6-luna`, low; assignment state: matched when dispatched.
- Independent critic: `gpt-5.5`, medium; required for the expanded
  implementation/rebuild scope at A9. This is an implementation verdict, not
  a release or reconstruction-acceptance decision.

## Steps

| Step | Owner | Effort | Dependency | Status | Evidence / next action |
|---|---|---:|---|---|---|
| A1 Audit pages 1-9 | bounded QA | low | source visuals + Stage 06 | completed | `handoffs/a1-pages-001-009-qa.md` |
| A2 Audit pages 10-18 | bounded QA | low | source visuals + Stage 06 | completed | `handoffs/a2-pages-010-018-qa.md` |
| A3 Audit pages 19-26 | bounded QA | low | source visuals + Stage 06 | completed | `handoffs/a3-pages-019-026-qa.md` |
| A4 Integrate and de-duplicate findings | orchestrator | medium | A1-A3 | completed | `structural-audit.md`: 30 units on 15 pages |
| A5 Specify reusable structural decision contract and gates | architecture | high | A4 | completed | `handoffs/a5-structural-contract-architecture.md` |
| A6 Implement shared pipeline and regression tests | engineering/executor | medium | A5 | completed | `handoffs/a6-shared-implementation.md`; final integrated suite 314 passed, 1 skipped |
| A7 Author corrected immutable Dream decisions | orchestrator/executor | medium | A4-A6 | completed | `handoffs/a7-final-successor-materialization.md`; replay-15 decisions-v26, 26 pages / 53 units |
| A8 Replay Stages 05-06 and full-scope QA | bounded QA | low | A6-A7 | completed | `handoffs/a8-final-candidate-qa.md`; independent PASS on replay-15/v26 |
| A9 Independent implementation review | independent critic | medium | A6-A8 | completed | `handoffs/a9-independent-implementation-review.md`; `APPROVE_IMPLEMENTATION`, not release |
| A10 Update canonical state and answer user | orchestrator | medium | A9 | completed | canonical docs updated; concise evidence-backed response |

## Definition of Done

- All 26 pages are visually compared with their per-page Stage 06 Markdown.
- Findings distinguish confirmed structural defects from OCR/text defects and
  from intentional image preservation.
- Each finding names page, source structure, candidate failure, severity, and
  earliest failing layer.
- Totals are reported both by affected page and by distinct structural unit.
- Existing sealed candidate and v12 decisions remain immutable; corrections
  use successor roots.
- Shared scripts/tests reject structural flattening for declared source
  containers rather than special-casing Number 7 Dream.
- Corrected Stages 05-06 pass the full-scope structural audit.
- No acceptance or MASTER_EN promotion is inferred.

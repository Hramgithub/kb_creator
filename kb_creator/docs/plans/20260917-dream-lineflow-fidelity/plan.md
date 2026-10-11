# Number 7 Dream compact line-flow fidelity plan

Goal id: `20260917-dream-lineflow-fidelity`

Status: completed

## Objective

Treat the user-reported character-field spacing on source page 24 as a seed
case, audit all 26 pages for analogous false paragraph boundaries, implement a
scenario-neutral reviewed compact-line-group contract, rebuild immutable
successor Stages 05-06, and verify semantic and visual line flow without
promoting the reconstruction to `MASTER_EN`.

## Role contract

- Contract: `docs/governance/nri_goal_governance.md` current at goal start.
- Policy orchestrator: `gpt-5.6-sol`, medium; assignment state:
  `platform-unverified`; scoped override: none.
- Architecture: `gpt-5.6-sol`, high; compact reviewed contract only.
- Engineering/execution: orchestrator, medium; shared implementation, tests,
  authoring, and replay integration.
- Bounded QA: `gpt-5.6-luna`, low; immutable candidate verification.
- Independent critic: `gpt-5.5`, medium; implementation verdict after QA.

## Steps

| Step | Owner | Effort | Dependency | Status | Evidence / next action |
|---|---|---:|---|---|---|
| L1 Classify seed and audit all 26 pages | orchestrator + bounded QA | medium/low | source visuals + replay-15 | completed | `handoffs/l1-full-scope-lineflow-qa.md`: four defects, two correct analogues, no other confirmed class members |
| L2 Specify reusable reviewed line-group contract | architecture | high | L1 | completed | `handoffs/l2-line-group-architecture.md` |
| L3 Implement shared validator/authoring support and tests | engineering | medium | L2 | completed | `handoffs/l3-shared-implementation.md`; 323 passed, 1 skipped |
| L4 Author fresh reviewed Dream decisions | orchestrator/executor | medium | L1-L3 | completed | `handoffs/l4-successor-materialization.md`; replay-16/v27 |
| L5 Replay Stages 05-06 and full-scope QA | bounded QA | low | L4 | completed | `handoffs/l5-candidate-qa.md`: PASS |
| L6 Independent implementation review | independent critic | medium | L3-L5 | completed | `handoffs/l6-independent-implementation-review.md`: `APPROVE_IMPLEMENTATION` |
| L7 Update canonical docs and report | orchestrator | medium | L6 | completed | plan/context/status/README/layout rules updated; candidate queued for the Codex file panel |

## Definition of Done

- The seed is mapped to its earliest failing layer and every analogous compact
  field group in all 26 pages is classified.
- The decision contract can declare a visually reviewed compact line group and
  Stage 05/06 fail closed if it becomes blank-separated paragraphs or loses a
  required Markdown hard break.
- The authoring helper produces the representation from reviewed source-block
  mappings; no scenario text is hard-coded in pipeline code.
- Focused and integrated regression tests pass.
- Existing replay-15/v26 artifacts remain immutable; corrections use a new
  replay and decision root.
- The rebuilt candidate is checked across all 26 pages, with exact assertions
  for every compact character-field group.
- Documentation records the defect class, pipeline layer, contract, rebuild,
  and verification. No acceptance or `MASTER_EN` promotion is inferred.

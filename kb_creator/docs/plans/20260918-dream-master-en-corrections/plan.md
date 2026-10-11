# Number 7 Dream MASTER_EN structural corrections plan

Goal id: `20260918-dream-master-en-corrections`

Status: completed_at_accepted_master_en_gate

## Objective

Correct the user-reported title word joins and redundant blank separators at
the reconstruction authority boundary, add scenario-neutral fail-closed checks
and tests, materialize immutable reconstruction/promotion/Stage 10 successors,
and bind the user's explicit MASTER_EN acceptance to the corrected verified
candidate rather than mutating or accepting the superseded bytes.

## User authority

On 2026-09-18 the user reported `THE ENLIGHTENEDWEBSITE`,
`THE ENLIGHTENEDWELLNESS CENTRE`, and five redundant blank lines between
Appendix A stat blocks, instructed that the fixes be made at the correct
pipeline stage, and stated `мастер принят`.

The acceptance is to be recorded against the corrected immutable successor
after QA. It does not authorize accepting the known-defective Stage 10 hash,
manual edits inside sealed outputs, translation invention, Git commit, push,
or release.

## Role contract

- Orchestrator: `gpt-5.6-sol`, medium; canonical context/status, integration,
  execution gates, and user-facing handoff.
- Architecture/root cause: `gpt-5.6-sol`, high; shared contract and successor
  lineage specification.
- Engineering: `gpt-5.6-terra`, medium; reusable implementation and tests.
- Bounded QA: `gpt-5.6-luna`, low; full-scope successor verification.
- Independent critic: `gpt-5.5`, medium; implementation/process verdict.

## Steps

| Step | Owner | Status | Evidence / next action |
|---|---|---|---|
| C1 Re-read authority and audit both defect classes document-wide | orchestrator + architecture | completed | `handoffs/c1-architecture.md`: exactly 3 title conflicts and 3 redundant blank runs; `SPEC_READY` |
| C2 Implement generic guards/authoring rule and regression tests | engineering | completed | `handoffs/c2-implementation.md`; focused suite `167 passed` |
| C3 Author reviewed decision-set successor from immutable baseline | orchestrator/executor | completed | delta-only v28 spec; decision set `1C2283E4...737E71` |
| C4 Materialize fresh Stage 05/06 successor and full reconstruction QA | orchestrator + bounded QA | completed | `handoffs/c4-candidate-qa.md`: PASS; 26 pages, 59 units, 3 confirmations, 0 redundant runs |
| C5 Promote and accept corrected reconstruction successor | orchestrator | completed | accepted inventory `824F7766...2C80DD`; receipt `EAA6C97B...5CEBDE` |
| C6 Build corrected Stage 10 successor and record MASTER_EN acceptance | orchestrator | completed | publication-02; MASTER_EN `3AEF660D...AB7B5`; acceptance `FE3E85C6...DF73B` |
| C7 Independent review, docs, and commit-scope audit | critic + orchestrator | completed | `APPROVE_IMPLEMENTATION`; no critical/high/medium finding; `handoffs/c7-release-review.md` |

## Definition of Done

- Source visuals prove the intended heading spaces and Appendix separation.
- The entire accepted document is audited for analogous glued headings and
  redundant blank-line runs.
- Shared validation rejects unresolved title-spacing evidence conflicts and
  redundant blank separators; the generic author can canonicalize reviewed
  separators; regression tests cover pass and fail paths.
- A fresh immutable reconstruction candidate contains corrected headings and
  exactly one blank separator between every adjacent Appendix A stat block.
- Promotion and Stage 10 successors pass identity, semantic, asset and full-
  scope QA with no downstream mutation.
- MASTER_EN acceptance records the user's exact decision reference and the
  corrected candidate identity.
- Reusable code/tests/spec/docs are Git-visible; generated `working/**`
  evidence remains ignored.

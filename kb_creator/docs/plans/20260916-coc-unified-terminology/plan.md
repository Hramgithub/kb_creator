# Unified CoC terminology plan

Goal id: `20260916-coc-unified-terminology`

Goal state: `complete`

Release state: `not_applicable`

## Objective

Use one system-level Call of Cthulhu terminology registry across every known
NRI CoC book and scenario. Remove active scenario-local duplicates, include
the complete characteristic/derived-stat profile and character skills, and
apply accepted exact replacements deterministically in Python before
`MASTER_RU` is sealed.

## Role contract

- Governance: `docs/governance/nri_goal_governance.md`.
- Orchestrator policy owner: `gpt-5.6-sol`, medium; actual platform identity
  unavailable, assignment state `platform-unverified`.
- Engineering: main-chat integration under the earlier user-scoped
  `gpt-5.6-sol`/high preference; no contributor was dispatched for this bounded
  continuation, so actual model/effort remains `platform-unverified`.
- Independent critic: not required because this is not a frozen release gate.
- Scoped override: engineering preference only; orchestration remains in the
  main chat.

## Work plan

| Step | Owner | Deliverable | Status |
|---|---|---|---|
| 1. Authority consolidation | Orchestrator | One CoC CSV with full stat/skill vocabulary and unresolved rows | completed |
| 2. Duplicate removal | Orchestrator | Remove active skill Markdown and Dissociation-local copies | completed |
| 3. Python normalization | Orchestrator | Deterministic accepted replacements plus independent verification | completed |
| 4. Cross-project wiring | Orchestrator | Dissociation, Viral, and active Innsmouth scripts reference the one CSV | completed |
| 5. Documentation/state | Orchestrator | System boundary, historical-snapshot rule, status/context | completed |
| 6. Verification | Orchestrator | Focused tests, contract identity, duplicate-reference audit, diff check | completed |

## Completion evidence

- The sole live authority is `16003` bytes, SHA-256
  `EE84E121E63ECDA3F2165205E8335FD3C68E70CF1DEFE1D00CE6C3FF97EFF3AE`.
- Repository discovery finds exactly one active
  `CoC_Terminology_Decisions.csv` and no live copy of the removed skills
  Markdown.
- Dissociation publication run `20260916-publication-29` binds that exact
  authority and completed MASTER_RU, HTML, DOCX, accepted-DOCX-only PDF,
  production packaging and offline verification without rerunning MinerU/OCR.
- The run29 terminology report passes and records `18` deterministic
  replacements. The resulting stat block uses `ТЕЛ`, `НАР`, `МОЩ`, `РАС` and
  `СКО`; obsolete `РАЗМ` and `ВНЕШ` are absent.
- Historical sealed package identities remain provenance only. They are not
  active terminology inputs.

## Definition of Done

- `CoC/Project_Reference/Terminology/CoC_Terminology_Decisions.csv` is the only
  active CoC system terminology authority.
- Scenario terminology files contain only scenario-specific names/concepts.
- No live script or current contract requires the removed skills Markdown or a
  scenario-local copy of the CoC registry.
- Historical package manifests keep their original provenance identity without
  requiring a live duplicate authority file.
- Exact Python normalization fixes `SIZ -> ТЕЛ`, `APP -> НАР`, `POW -> МОЩ`
  and declared skill variants before candidate hashing.
- Focused producer/verifier/contract/legacy compatibility checks pass; any
  unrelated pre-existing suite failure is recorded precisely rather than
  hidden.

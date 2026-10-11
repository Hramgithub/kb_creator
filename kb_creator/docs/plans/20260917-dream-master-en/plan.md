# Number 7 Dream reconstruction acceptance and MASTER_EN plan

Goal id: `20260917-dream-master-en`

Status: completed_at_master_en_acceptance_gate

## Objective

Record the user's explicit acceptance of the immutable replay-16/v27
`RECONSTRUCTED_EN`, promote it through the generic reconstruction-acceptance
bridge, author a closed scenario-neutral publication authority for Number 7
Dream, and produce a fresh Stage 10 `MASTER_EN` candidate with QA. Audit the
future Git commit scope so every reusable pipeline change, test, contract, and
canonical document is tracked or trackable while generated `working/`
artifacts remain excluded.

## User authority

The user explicitly stated in the current Codex task on 2026-09-17:
`файл реконструкции принят`. This authorizes recording reconstruction
acceptance for replay-16/v27 and proceeding to the next pipeline gate. It does
not pre-accept `MASTER_EN`, translation, ArtView, HTML, DOCX, PDF, release, Git
commit, or push.

## Role contract

- Contract: `docs/governance/nri_goal_governance.md` current at goal start.
- Policy orchestrator: `gpt-5.6-sol`, medium; assignment state:
  `platform-unverified`; scoped override: none.
- Architecture: `gpt-5.6-sol`, high; bounded Dream publication-authority and
  Stage 10 specification.
- Engineering/execution: orchestrator, medium; promotion, config integration,
  Stage 10 execution, and canonical state.
- Bounded QA: `gpt-5.6-luna`, low; acceptance/package/MASTER_EN verification.
- Independent critic: `gpt-5.5`, medium; implementation/process verdict for
  the frozen Stage 10 candidate. This is not a release review.

## Steps

| Step | Owner | Effort | Dependency | Status | Evidence / next action |
|---|---|---:|---|---|---|
| M1 Re-read live rules/status/plans/commits and audit future commit scope | orchestrator | medium | user instruction | completed | `handoffs/m1-context-and-commit-scope.md`: PASS; reusable files are trackable, working artifacts ignored |
| M2 Materialize replay-16 promotion package and record user acceptance | orchestrator/executor | medium | M1 | completed | accepted inventory `FDE1E1C5...AFA15DA`; receipt `BFEF49D2...1B4607B`; semantic promotion + handout detector fixed generically |
| M3 Specify closed Dream publication blueprint/config for Stage 10 | architecture | high | M2 + accepted reconstruction | completed | `handoffs/m3-publication-authority-architecture.md` |
| M4 Author and validate trackable publication authority | orchestrator/executor | medium | M3 | completed | `handoffs/m4-publication-authority-implementation.md`; 19 reader assets; contract `EB23016E...CA207B8` |
| M5 Preflight and run fresh publication Stage 10 | orchestrator/executor | medium | M2 + M4 | completed | `handoffs/m5-stage10-materialization.md`; candidate `4C154262...E59945`; stopped at acceptance gate |
| M6 Independent full-scope MASTER_EN QA | bounded QA | low | M5 | completed | `handoffs/m6-master-en-qa.md`: PASS, no findings |
| M7 Independent implementation/process review | independent critic | medium | M1-M6 | completed | `handoffs/m7-independent-review.md`: `APPROVE_IMPLEMENTATION`; nonblocking stale-fixture debt recorded |
| M8 Update canonical docs and hand off | orchestrator | medium | M7 | completed | `handoffs/m8-commit-scope-and-handoff.md`; next gate is explicit MASTER_EN acceptance |

## Definition of Done

- Replay-16/v27 identities are revalidated before acceptance is written.
- The generic promotion package is materialized and its acceptance receipt is
  bound to the user's current explicit decision.
- Every reusable change from reconstruction, structural fidelity, ACL repair,
  line-flow repair, and this promotion goal is classified as tracked,
  untracked-but-not-ignored, ignored generated evidence, or intentionally out
  of scope; no required script/test/contract is hidden under `working/`.
- Dream publication config is declarative and authored through the generic
  scenario publication contract author; no `build_number_7_dream_*` script is
  created.
- A fresh publication run completes only Stage 10 and stops at
  `awaiting_master_en_acceptance`.
- MASTER_EN preserves accepted page/text/assets/semantic structure and passes
  the contract-required independent verifier and bounded QA.
- Documentation records acceptance, lineage, hashes, commit scope, test
  evidence, and the next explicit user gate.
- No commit, push, translation, ArtView, HTML, DOCX, PDF, or release decision
  is inferred.

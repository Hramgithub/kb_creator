# Reconstruction candidate ACL normalization plan

- Goal ID: `20260917-reconstruction-acl-normalization`
- State: `completed`
- Objective: make every real Stage 06 reconstruction candidate readable by the Codex desktop UI and the Windows user by normalizing final-tree ACL inheritance after atomic publication, without changing artifact bytes or inferring acceptance.
- Scope boundary: reusable reconstruction replay/resume code, focused tests, documentation, live verification on the existing Number 7 Dream candidate. No source edits, acceptance, publication, Git commit, or push.

## Role contract

- Contract version: `docs/governance/nri_goal_governance.md` read 2026-09-17.
- Policy orchestrator: `gpt-5.6-sol`, medium; assignment state `platform-unverified`; scoped override `none`.
- Architecture: `gpt-5.6-sol`, high; assignment state `completed` for integration-point and failure-mode review.
- Engineering: orchestrator-owned integration; policy role `gpt-5.6-terra`, medium remains unassigned.
- Independent critic: `gpt-5.5`, medium; assignment state `completed`; final verdict `APPROVE_IMPLEMENTATION`.
- Bounded QA: `gpt-5.6-luna`, low; assignment state `completed` for Windows live evidence.
- Actual platform model/effort: `unavailable` unless exposed by the platform.

## Steps

| Step | Owner / effort | Dependency | Definition of Done | Status |
|---|---|---|---|---|
| 1. Diagnose defect class | Orchestrator / medium + architect / high | existing Stage 06 output | earliest failing layer and safe post-rename hook identified | completed; architecture receipt includes inheritance-only edge case |
| 2. Implement fail-closed normalization | Orchestrator / medium | Step 1 | final Stage 06 tree normalizes ACL only after publication; failures cannot report success | completed; exact desktop principal receives additive RX and bytes are re-inventoried |
| 3. Test reusable behavior | Orchestrator / medium | Step 2 | focused and relevant expanded tests cover managed, skipped, failure, rerun, and byte-preservation behavior | completed; 22 focused and 279 expanded tests passed, 1 expanded skip |
| 4. Live Windows verification | QA / low | Step 3 | a real managed candidate is user-readable, inheritance-enabled, byte-identical, and openable through Codex where the UI bridge permits | completed; managed Stage 06 and Dream candidate readable with matching hashes; UI navigation bridge remains `queued`, not claimed opened |
| 5. Independent review and handoff | Critic / medium + orchestrator / medium | Steps 3-4 | no unresolved P0/P1; canonical docs current; exact limitations reported | completed; final critic verdict `APPROVE_IMPLEMENTATION`, no blockers |

## Definition of Done

- Stage 06 success implies final-tree ACL normalization completed or was explicitly skipped outside a managed Windows tree.
- ACL normalization happens after the final atomic rename, not only in staging.
- Any ACL normalization failure prevents successful `candidate_ready_for_reconstruction_qa` reporting.
- Artifact identities remain unchanged.
- Existing sealed candidates can be safely repaired through the reusable helper.
- Tests and independent review pass; no commit or push occurs without explicit instruction.

## Evidence

- Seed failure: Number 7 Dream `outputs/06-materialize-candidate` had `AreAccessRulesProtected=True`, owner `CodexSandboxOnline`, and no ordinary-user read rule; both Codex UI and Notepad failed to open the file.
- Manual scoped normalization changed the directory to `AreAccessRulesProtected=False`; `RECONSTRUCTED_EN.md` SHA-256 remained `38B2D376E119D989656223A8909E93D9C295BE9D69CFF1A46B469998702BF72F`.
- Architecture receipt: `handoffs/architect_acl_integration_20260917.md`.
- Live managed synthetic candidate: inheritance enabled, exact `KAMAZNOTEBOOK\user` RX ACE present, external user process read 44 bytes and the expected page marker.
- Regression: `23 passed` focused; final expanded relevant suite `280 passed, 1 skipped`; `git diff --check` clean.
- QA receipt: `handoffs/qa_acl_windows_20260917.md`.
- Independent review: `handoffs/critic_acl_implementation_20260917.md`; final verdict `APPROVE_IMPLEMENTATION`.

## Blockers and next action

- Blockers: none. The Codex UI navigation bridge returned `queued`; filesystem readability is proved, but UI tab presentation is not claimed as independently verified.
- Next action: user handoff. Commit and push remain unperformed pending explicit instruction.

# Number 7 Dream reconstruction plan

- Goal ID: `20260916-dream-reconstruction`
- State: `completed`
- Objective: reconstruct the immutable 26-page source PDF `Number 7 Dream` through the neutral KB Creator three-view pipeline and produce a fully audited reconstruction candidate for user review.
- Scope boundary: source reconstruction only. Publication, `MASTER_EN`, `MASTER_RU`, HTML, DOCX, PDF export, Git, acceptance, and release decisions are excluded.

## Role contract

- Contract version: `docs/governance/nri_goal_governance.md` (2026-09-16 working-tree version).
- Policy orchestrator: `gpt-5.6-sol`, medium; assignment state `platform-unverified`; scoped override `none`.
- Engineering assistance: `gpt-5.6-terra`, medium; assignment state `completed` for bounded pipeline corrections.
- Independent critic: `gpt-5.5`, medium; assignment state `completed`; it did not implement or materially design the candidate.
- Architecture: `gpt-5.6-sol`, high; assignment state `completed` for the reviewed OCR-equivalence remediation specification.
- Bounded executor: `gpt-5.6-luna`, medium; assignment state `completed` for bounded implementation work.
- Bounded QA: `gpt-5.6-luna`, low; assignment state `completed` for candidate QA.
- Actual platform model/effort: `unavailable` unless exposed by the platform.

## Steps

| Step | Owner / effort | Dependency | Definition of Done | Status |
|---|---|---|---|---|
| 1. Immutable-source reconnaissance | Orchestrator / medium | source PDF | SHA-256, bytes, page count, geometry, text/image inventory, and complete-page visual contact sheets recorded | completed |
| 2. Scenario reconstruction contract | Orchestrator / medium + architect / high | Step 1 | scenario-specific topology and required entities are evidence-backed, schema-valid, and independently reviewed | completed; no P0/P1, P2 requires explicit six-pregen evidence |
| 3. Tool and run preflight | Orchestrator / medium | Step 2 | contract/source/tool bindings validate and the chosen run root is absent | completed; CPU ready, optional CUDA unavailable by receipt |
| 4. MinerU three-view reconstruction | Executor / medium | Step 3 | mandatory CPU text, PDF OCR, and raster OCR views plus comparison and visual merge bundle are sealed in a new run root | completed in fresh replay root `20260917-cpu-replay-05`; earlier failed/diagnostic runs remain immutable |
| 5. Closed merge decisions | Orchestrator / medium | Step 4 | every review-queue item has an identity-bound decision or explicit reviewed exclusion; unresolved items remain blockers | completed with reviewed decision set v12 for all 26 pages |
| 6. Fidelity audit and materialization | Orchestrator / medium + QA / low | Step 5 | source-visible completeness audit passes and a run-local candidate is materialized without acceptance inference | completed; audit passed 26/26 at completeness 1.0, 29 assets materialized, `acceptance_inferred=false` |
| 7. User handoff | Orchestrator / medium | Step 6 | candidate, QA evidence, caveats, and next gate are linked; canonical plan/context/status are current | completed; candidate remains gated for user reconstruction review |

## Definition of Done

- The source PDF is unchanged and its recorded identity still matches.
- A fresh run root contains sealed Stages 01-06 for all 26 pages.
- All five numbered handouts and six pregenerated player characters are represented or explicitly dispositioned through run-local evidence.
- Fidelity audit reports no unresolved source-visible text units.
- The materialized reconstruction remains a candidate, not an accepted or published artifact.

## Evidence

- Source SHA-256: `C03AD05644C5B7438E4FAB750557EB8098E637492242D21969C5C4110FBF97D0`.
- Source bytes: `2915268`; pages: `26`; MediaBox/CropBox: `612 x 792` points; rotation: `0` on all pages.
- Visual reconnaissance: `tmp/pdfs/dream-reconstruction/contact-01.jpg` and `contact-02.jpg` cover all source pages.
- Extracted contents identify Appendix B as five numbered handouts and Appendix C as six pregenerated player characters.
- Final run: `kb_creator/working/number-7-dream/reconstruction/20260917-cpu-replay-05`.
- Reviewed decisions: `kb_creator/working/number-7-dream/reconstruction/20260917-cpu-replay-05-decisions-v12/decision_set.json`.
- Candidate: `outputs/06-materialize-candidate/RECONSTRUCTED_EN.md`; 26 page markers and 29 identity-checked assets.
- Fidelity audit: `outputs/05-fidelity-audit/audit.json`; passed, 26 pages, minimum completeness `1.0`, no errors.
- Candidate QA: `handoffs/qa_dream_candidate_20260917.md`; all five handouts and six pregenerated characters verified.

## Blockers and next action

- Blockers: none inside the reconstruction scope. The root `result.json` intentionally remains the sealed Stage 01-04 replay result (`needs_review`); the downstream replay-resume result and Stage 06 authority record `candidate_ready_for_reconstruction_qa`.
- Next action: user reconstruction review. Acceptance, translation, publication, exports, Git, and release remain outside this completed goal.

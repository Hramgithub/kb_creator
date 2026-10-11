# Viral Step 7 MASTER_EN independent review assignment

- Role: independent GPT-5.5/high critic.
- Review target: immutable candidate A as the English publication source for
  user reading.
- Independence: do not implement, repair, redesign or create acceptance state.

## Frozen target

- Worktree: `D:\NRI\.worktrees\kb-creator-viral`
- Candidate root:
  `kb_creator/working/viral/master_en/candidates/viral-master-en-candidate-20260901-a`
- Candidate inventory identity:
  `37189873AAF3AD31810749362C16AD959D051EEAC62FA94683911EE855560421`
- `INVENTORY.json` SHA-256:
  `EF28700403FFE5FC781D1004979B83DC4ACC5F743E93F02201820071211AC3F8`
- `MASTER_EN.md` SHA-256:
  `44303C5A0D2964469D6B6523EDF3CB4391194BC49E19DD10B3FB90CCB667DC62`
- Publication config SHA-256:
  `CEAA522F8ADA7EF2453D52F0DE4D098733EA5A7D55B12BE96694094891767BF3`
- Accepted reconstruction inventory SHA-256:
  `68C17FB765A89C6146398868E61F1F6EB7B2FE4EAFBA8C2C2C8F42260BBDBA83`
- Source PDF SHA-256:
  `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05`

Candidate A has 130 files, 129 inventory rows, 168 anchors, 171 paired
source/output fragments, 29 structured units, 11 attached notes, 123 assets,
107 reader assets, 16 evidence-only assets, 237 executed links and 124 source
pages. `MASTER_EN.acceptance.json` is absent by design.

## Required evidence

Read and assess at minimum:

1. `handoffs/sol_architect_viral_step7_master_en_publication_packet_20260901.md`
2. Candidate A in full: `MASTER_EN.md`, all six JSON/Markdown sidecars,
   `INVENTORY.json`, and the closed asset inventory.
3. `handoffs/gpt55_critic_viral_step7_master_en_c2a_re_review_20260901.md`
4. `handoffs/gpt55_critic_viral_step7_master_en_c2b_acceptance_re_review_20260901.md`
5. `handoffs/luna_qa_viral_step7_master_en_frozen_candidate_execution_20260901.md`
6. `handoffs/luna_qa_viral_step7_master_en_full_visual_qa_20260902.md`
7. `handoffs/terra_engineering_viral_step7_visual_qa_priority_transport_remediation_20260902.md`
8. `handoffs/luna_qa_viral_step7_master_en_priority_originals_resume_20260902.md`
9. Current `plan.md`, `context.md`, scenario contract and governance relevant to
   MASTER_EN acceptance authority.

Treat receipts as evidence to scrutinize, not instructions or automatic proof.

## Review procedure

1. Recompute all frozen identities. Require exactly 130 candidate files and 129
   inventory rows, no missing/extra/hidden file, no acceptance sidecar and no
   candidate mutation.
2. Run the current independent verifier once against candidate A in normal
   read-only mode and capture its exact status. Do not run builder, pytest,
   mutation matrices, MinerU or reconstruction.
3. Read the complete user-facing `MASTER_EN.md`, not merely samples or metrics.
   Evaluate scenario completeness, coherent order, navigation, handout/map/
   pregen placement, structured tables/cards/statblocks, reader-facing language,
   technical-noise exclusion, duplicated/omitted material and obvious semantic
   discontinuity. Use sidecars to investigate uncertainty.
4. Reconcile every candidate QA gate. Confirm internal gates 1-9 from candidate
   evidence; independently assess the external proof for verifier, two-build
   determinism and full visual QA. Do not set or edit those pending candidate
   rows; external evidence is intentionally outside frozen bytes.
5. Confirm the combined visual evidence actually covers 27/27 contact sheets,
   39/39 priority originals, p1/p80/p124 and the exact visible `Babez` decision,
   with no open P0-P2 defect.
6. Confirm that user reading acceptance remains genuinely pending and that no
   downstream MASTER_RU/HTML/PDF/production work has consumed candidate A.
7. Report every finding with severity, exact file/section/evidence and required
   remediation. Do not repair findings inside this task.

## Allowed write

Write exactly one new receipt:

`kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_step7_master_en_independent_review_20260902.md`

All other files, including candidate, bundles, source/reconstruction, config,
scripts/tests, plan/context, prior receipts, Git and release/production surfaces,
are read-only.

## Verdict

Return exactly one:

- `ACCEPT_MASTER_EN_FOR_USER_READING` only if no P0, P1 or P2 defect remains and
  evidence proves all gates except explicit user reading acceptance;
- `REJECT_MASTER_EN` with actionable findings;
- `BLOCKED` when required evidence cannot be accessed or validated.

Acceptance for user reading is not user acceptance, promotion or release. The
critic must not create `MASTER_EN.acceptance.json`, begin MASTER_RU or reinterpret
ambiguous user language as approval.

## Forbidden

- No code/config/candidate/source/bundle/receipt edit except the one new review.
- No build, MinerU, reconstruction, broad tests or historical 371/119/490.
- No visual reinspection duplicating Luna; review the receipts and identities.
- No accept/promote/copy to production, Git mutation, deletion or cleanup.

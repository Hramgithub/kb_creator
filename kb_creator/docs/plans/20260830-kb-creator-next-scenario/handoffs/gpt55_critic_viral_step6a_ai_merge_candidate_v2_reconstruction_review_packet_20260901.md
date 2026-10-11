# Independent critic packet — Viral Step 6A reconstruction candidate v2

- Goal id: `20260830-kb-creator-next-scenario`
- Step id: `viral-step6a-reconstruction-review-v2`
- Date: `2026-09-01`
- Orchestrator policy owner: main-chat `gpt-5.6-sol`, medium
- Reviewer: independent critic `gpt-5.5`, high
- Assignment state: requested role/profile; actual platform identity is recorded
  only if exposed
- Review kind: `implementation/process` at the reconstruction boundary, not a
  final release review
- Status: `AUTHORIZED_READ_ONLY_REVIEW`

## Frozen candidate

Candidate root:

`D:\NRI\.worktrees\kb-creator-viral\kb_creator\working\viral\source_reconstruction\20260901_step6a_ai_merge_candidate_v2`

- files: `373`;
- bytes: `13141502`;
- canonical trailing-LF inventory SHA-256:
  `76C4C8599B9321FFCF0983C548A7A2A94D8B3BC259D93E3EF2343CB58DB471B1`;
- `RECONSTRUCTED_EN.md` SHA-256:
  `321B1D10006C9FCA679813AA11B5EC24924E73BEB473E3DD6F4EA73897C54735`;
- orchestrator machine-audit receipt SHA-256:
  `5D6B9C1B773F6DF1CC46F9A35D366849FD6B05938AEEFF50433E21718DB6C702`.

## Read-only authorities

- `D:\NRI\.worktrees\kb-creator-viral\kb_creator\contracts\viral.json`;
- `D:\NRI\.worktrees\kb-creator-viral\kb_creator\working\viral\source\Call_of_Cthulhu_Viral.pdf`;
- candidate `pages/`, `decisions/`, `MERGE_PROVENANCE.json`,
  `ASSET_MANIFEST.json`, `OVERLAY_SELECTION.json`;
- frozen raw root
  `...\20260901_step6a_mineru_three_view_full`;
- frozen visual/merge bundle
  `...\20260901_step6a_mineru_three_view_postprocess_candidate`;
- visual QA receipt
  `luna_qa_viral_step6a_full_visual_merge_bundle_scratch_preview_correction_20260901.md`;
- AI page decision receipts for ranges `001-044`, `045-086`, `087-124` and
  the range-A asset-link correction;
- orchestrator audit receipt
  `sol_orchestrator_viral_step6a_ai_merge_candidate_v2_audit_20260901.md`.

## Required review

Evaluate the frozen candidate against every `reconstructed_en` acceptance gate
in `viral.json`:

1. `source_identity`;
2. `page_coverage`;
3. `role_partition`;
4. `text_ocr_provenance`;
5. `required_entity_closure`, especially exactly `39` numbered player
   handouts;
6. `asset_closure`;
7. `no_open_blockers`.

Check that the evidence actually covers each requirement rather than accepting
counts alone. Review the known risk classes: multi-column reading order,
pages 53 and 109 cross-view differences, handouts 69-103, maps 104-110,
pregenerated investigators 111-123, cover/back cover and page 121's blank-form
signal. Distinguish reconstruction fidelity from later publication editing.

Report P0/P1/P2/P3 findings with exact page/file evidence. Return one of:
`accept_reconstruction_candidate`, `accept_with_conditions`, or
`reject_reconstruction_candidate`. A finding that requires content change must
identify the owning decision page(s); do not edit them.

## Strict write boundary

The only permitted write is:

`D:\NRI\.worktrees\kb-creator-viral\kb_creator\docs\plans\20260830-kb-creator-next-scenario\handoffs\gpt55_critic_viral_step6a_ai_merge_candidate_v2_reconstruction_review_20260901.md`

Create it with the file patch tool. Do not edit candidate, decisions, source,
raw/bundle roots, code, tests, plan, context, status, contract, Git or production.
Do not run MinerU, 371/119/490, builds or downstream stages. Read-only inspection
and read-only hashes/searches are allowed.

The receipt must record scope, candidate/audit identities, checks performed,
findings, recommendation, blockers, changed files, elapsed time and token use or
`unavailable`.

# Viral remediation Slice 4 visual-QA v2 resume

- Goal: `20260830-kb-creator-next-scenario`
- Step: `7-user-review-remediation-visual-qa-v2-resume`
- Owner: current `nri-engineer`, `gpt-5.6-terra` / `medium`
- Inputs: completed dispositions, review units and external verifier report
- Completion token: `READY_FOR_VIRAL_V2_POLICY_AUTHORING`

## Objective and ownership

Resume and fully implement the original Slice 4 visual-QA packet now that all
authoritative inputs exist. Keep strict v1 compatibility.

Owned paths:

- `kb_creator/scripts/build_master_en_visual_qa_bundle.py`
- `kb_creator/tests/test_build_master_en_visual_qa_bundle.py`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_user_review_remediation_visual_qa_v2_resume_20260903.md`

You are not alone in the worktree. Preserve all other edits.

## Required v2 route

- Require candidate, v2 config and external verification report. Independently
  validate canonical report and recompute candidate/config/source/reconstruction
  binding using the verifier's public report-validator API; do not trust a
  status string alone.
- Derive every count/group/priority row from `visual_review_units`, disposition,
  ledger, config and candidate. No fixed 129/123/107/91/39/p124 logic in v2.
- Skip pages 123--124 as explicit `excluded_advertising` audit rows; generate no
  source crop/reader/artview/choice for them and reject any leakage.
- Generate source-versus-reader rows for all declared kinds: headings/outline,
  callouts/list-callouts, tables, equipment cards, statblocks, inline run-ins,
  full-page maps, physical page pairs, xref/recovery and asset placement.
- Bind rows to exact page/event/fragment, ledger final range/hash and reader
  asset identity/placement. Render priority originals/contact sheets dynamically
  from groups and declarations.
- Write only to an explicitly absent QA output root: canonical machine manifest,
  compact review HTML, crops/originals/contact sheets and a fail-closed coverage
  summary. Candidate and verification report remain read-only.
- This is a disposable review aid, not Step 9 publication and not Step 8A.

## Tests/evidence

Add synthetic v2 success and report/config/candidate tampering, dynamic-count,
excluded-page, each semantic-kind, ledger-binding, placement, missing coverage
and absent-output-root mutations. Retain v1 tests. Run full visual-QA module,
`py_compile` and diff check. Write the exact receipt and return the token only
when complete.

No builder/verifier/proposer/real config/evidence/candidate/Git/Step 8A changes.

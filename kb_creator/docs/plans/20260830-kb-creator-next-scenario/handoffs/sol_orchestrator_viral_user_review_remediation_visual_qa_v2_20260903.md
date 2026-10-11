# Viral remediation Slice 4 v2 visual-QA bundle

- Goal: `20260830-kb-creator-next-scenario`
- Step: `7-user-review-remediation-visual-qa-v2`
- Owner: current `nri-engineer`, `gpt-5.6-terra` / `medium`
- Slice 3 gate: closed by mutation 1--8 and v2 contract receipts
- Completion token: `READY_FOR_VIRAL_V2_POLICY_AUTHORING`

## Objective and ownership

Complete architecture Slice 4: make the disposable visual/structural QA bundle
fully v2- and config-driven without Viral fixed counts, p124 back-cover logic or
legacy reader-asset assumptions. Do not author the real v2 policy or build a
real candidate in this packet.

Owned paths:

- `kb_creator/scripts/build_master_en_visual_qa_bundle.py`
- `kb_creator/tests/test_build_master_en_visual_qa_bundle.py`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_user_review_remediation_visual_qa_v2_20260903.md`

You are not alone in the worktree. Preserve all other edits.

## Required behavior

- Keep strict v1 compatibility while adding a closed v2 route.
- Accept only a verifier-passed candidate/config binding; recompute candidate
  inventory/hash and derive all counts from candidate/config.
- Render no source or reader row for pages with
  `publication_disposition=excluded_advertising`; report them separately as
  skipped audit rows and reject leakage.
- Generate compact source-versus-reader semantic rows for full titles and
  outline representation, callouts/list-callouts, logical tables, equipment
  cards, creature statblocks, inline run-ins, full-page map units, physical
  pregen pairs, xrefs/recoveries and before/after/inside asset placement.
- Bind every row to source page/event/fragment and final ledger range/hash.
- Derive priority-original/contact-sheet counts from declarations; remove any
  hard-coded 123/107/91/39/p124 assumptions.
- Build only into an explicitly absent QA output root, never candidate root;
  output is disposable review aid and not Step 9 HTML/publication.
- Include machine-readable manifest + compact review HTML and fail-closed
  generation-error/coverage summary.

Add synthetic v1 regression and v2 success/mutation tests for dynamic counts,
excluded pages, all semantic row families, ledger binding, placement and absent
output-root behavior. Run full visual-QA test module and `py_compile`. Write the
exact receipt and return the token only when complete.

No builder/verifier/proposer/config/evidence/source/real candidate/Git/Step 8A
changes.

# Existing visual review bundle integration

- Goal: 20260830-kb-creator-next-scenario; Step 7 rebuilt MASTER_EN handoff.
- Role: nri-engineer / Terra medium; root owns orchestration and status.
- Exclusive ownership: kb_creator/scripts/build_master_en_visual_qa_bundle.py
  and kb_creator/tests/test_build_master_en_visual_qa_bundle.py.
- Input: existing v2 builder/verifier contracts, original remediation spec,
  approved config author evidence. Coordinate schema needs with the concurrent
  metadata_asset_order engineer; do not edit author/builder/verifier.
- Deliverable: existing QA generator works with real canonical v2 assets and
  verifier report; source and reader excerpts/images are actually visible in
  review.html, not only a list of review-unit IDs. Reuse existing v1 rendering
  helpers where appropriate. Preserve exclusions, input hashes and v1 tests.
- No new app, workflow, manual asset ledger or final art-quality selector.
  No source/candidate/accepted edits, Git changes or final bundle generation.
  Root runs final real bundle after candidate verification.
- You are not alone in the worktree; preserve others' edits. Read applicable
  AGENTS/governance and necessary code. Use apply_patch for manual edits.
- Run focused existing module tests and capture results. Report actual code
  changes and integration dependencies, not an architectural proposal.
- Receipt: terra_viral_review_bundle_integration_20260903.md beside this packet.
  Include scope, commands/results, changed files, blockers, elapsed/tokens or
  unavailable, owner and effort. Assignment ends on implementation receipt.

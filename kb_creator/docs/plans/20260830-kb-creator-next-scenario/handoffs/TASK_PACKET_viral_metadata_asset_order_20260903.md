# Bounded engineering: derive art order from existing MinerU metadata

- Goal: `20260830-kb-creator-next-scenario`; step: current MASTER_EN repair.
- Contributor: `nri-engineer`, requested Terra/medium; root Sol/medium policy
  owns orchestration. Actual platform runtime unverified; scoped override none.
- Worktree: `D:/NRI/.worktrees/kb-creator-viral`.
- Ownership: `kb_creator/scripts/author_viral_master_en_v2_config.py`, its test
  file, and only if necessary a small reusable source-order helper plus its
  tests. Do not edit builder/verifier yet. You are not alone in the codebase;
  preserve other edits. Root is updating canonical docs, not these code files.
- Inputs: current author, accepted v4 decisions/pages/ASSET_MANIFEST, original
  comparison three views, existing semantic/boundary review ledgers. Read the
  root AGENTS/governance and current context. Original remediation specification
  is `sol_architect_viral_user_review_remediation_spec_20260902.md` beside this file.
- User correction: no new manual ledger for every art, no redoing extraction.
  Consume existing metadata and derive mechanical relationships. Do not adopt
  the suspended B1c7 manual owner-placement proposal as authority.

Implement a deterministic source-order resolver usable by the current author.
Bind assets using existing exact manifest/comparison identities. Preserve order
within the selected view (never numerically compare indexes from different
views). Align text anchors against accepted page text outside Markdown image
syntax; use exact unambiguous matches first. Distinguish source reading order
from already-damaged Markdown marker offsets. Report conflicting or missing
evidence explicitly without inventing owner/placement or silently falling back
to page end. Preserve cross-view provenance and accepted reader/evidence-only
policy. Expose real-input readiness through the author so the result is consumed
by the next publication authoring step, not an isolated speculative utility.

Regression seeds: p46 original_hybrid block784 image before block785 title
`7. Cremation Pit`; p65/66 images before named creature text; p78 Handout10
before Handout11. Audit all current readers through the resolver and report
resolved/ambiguous counts and reasons. Existing p31/p32 Plots-before-Prologue
decision remains authoritative. Covers/full-page physical units use their
existing accepted page/unit order rather than forcing an ordinary text anchor.
Do not remove source words or turn image-generated descriptions into prose.

Keep scope bounded: no full v2/candidate generation, no new OCR/PDF render,
no edits under source/accepted-v4/v1/candidates, no Git changes, no schema-review
ladder or per-art manually authored decision inventory. Do not weaken existing
tests; if a current assumption needs changing explain the semantic reason.

Run focused tests, including real-input audit; report exact commands/results.
Expected receipt: `terra_viral_metadata_asset_order_20260903.md` in this folder,
with changed files, real-input counts, limitations, integration entry point,
elapsed time/token use or unavailable, and next minimal integration action.
Return a compact summary. Completion is tested source-order derivation, not
MASTER_EN acceptance. If blocked, identify exact unresolved evidence while
retaining completed implementation; do not expand into manual all-art review.

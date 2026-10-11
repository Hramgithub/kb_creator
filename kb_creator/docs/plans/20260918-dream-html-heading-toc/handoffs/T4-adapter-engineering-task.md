# T4 Stage-40 policy and semantic adapter engineering task

- Goal: `20260918-dream-html-heading-toc`
- Owner role: engineering, repository-policy `gpt-5.6-terra`, medium
- Ownership: KB Creator HTML publication adapter/config readiness contract,
  contract author/preflight integration needed for it, and focused tests.
- Forbidden: translator renderer implementation, scenario config/decisions,
  generated output, accepted authority, canonical plan/status, Git commit.

## Inputs

Read active plan/context and R1/R2/R3 receipts. Number 7 Dream's downstream
HTML config was deliberately left incomplete at Stage 10, identity-bound, and
later consumed at Stage 40 without a readiness transition. Adapter QA passed
vacuously. The adapter also injects the obsolete callout-class statblock
directive and verifies blockquote ordinals instead of semantic containers.

## Required implementation

1. Introduce a closed/versioned HTML publication policy lifecycle with explicit
   `deferred` and `stage40_ready` states. Deferred is legal as an unconsumed
   future role during earlier stages but Stage 40 must reject it before writing
   artifacts or invoking the renderer.
2. For `stage40_ready`, validate an explicit normalized frontmatter contract:
   ordered page roles, cover, credits mode, source/generated TOC decision,
   source page and entries/mappings, body start, and expected flow. Missing
   policy is not a strict-path default. Keep explicit compatibility normalization
   for complete legacy configs; do not accept omission.
3. Compare policy to accepted MASTER_RU/source graph with exact page markers and
   declared roles, not localized-title heuristics. Reject missing/duplicate
   roles, source contents paired with implicit generated mode, unresolved entry
   mappings, or deferred state.
4. After rendering, independently validate `frontmatter_manifest.json` and DOM:
   declared source origin/order/conservation, one TOC, source page consumed,
   credits present, body start, and zero unresolved links.
5. Change semantic statblock projection to the new typed directive expected by
   the renderer. Validate neutral semantic containers and explicitly reject
   `<blockquote.statblock-card>` / `.review-callout.statblock-card`; preserve
   exact semantic ID/page/ordinal and row gates.
6. Add production-shaped positive fixtures and negatives for all omissions,
   stale policy/manifest/DOM, and old quote-styled statblocks. Preserve current
   accepted-master byte checks and Stage-40-only boundary.

## Verification and receipt

Run focused adapter/contract suites and directly dependent tests. Write
`T4-adapter-engineering-receipt.md`. You are not alone in the worktree:
preserve unrelated and concurrent edits; never revert them.


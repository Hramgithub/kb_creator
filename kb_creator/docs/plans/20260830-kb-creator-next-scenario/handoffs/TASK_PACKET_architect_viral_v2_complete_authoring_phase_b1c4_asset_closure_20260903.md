# Task packet — Viral v2 Phase B1c4 asset closure architecture

## Role and scope

- Role: `nri-architect` / GPT-5.6-sol / high.
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`.
- Read-only root-cause/architecture analysis except receipt
  `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_viral_v2_complete_authoring_phase_b1c4_asset_closure_20260903.md`.
- Do not edit code/tests, plan/context, config/candidates, immutable inputs,
  evidence, Git, assets or downstream.
- You are not alone in the worktree; do not revert or overwrite other work.

## Bound checkpoint

- B1c3 implementation approval receipt:
  `4F37A4E75CAE7CB6E786F6D72D80A73D9062C6582E5378EC642C417B5281F960`.
- B1c asset/xref readiness addendum:
  `B709C7F09B3F19A65AFA2DBE3FE7AE42022357FB690E436F27C899CCDF21290F`.
- Current author/builder/verifier:
  `5F0B1E7FEDE3B589012306C561125B87ED9BCBAEA0A18BED5E3853ECAC9AD666`,
  `A1602EEC138FDD54CB16BC0C53629347603B624AA6014609961B00B1C9250F28`,
  `6783D5ACE3133F9CD9BF698AAD554D54A0FD3BA8952170DA9024BDF997590FCB`.
- Their tests:
  `AC8395CA15B1889359F794FE617C0F4F912155C1EF7D471761B9057CA1C1CF98`,
  `BE1AFABE94AAA7CFC07DB26529B362D418D18C228A7F11CDC61D59F276546207`,
  `8D1DF368C878FA59E3C05D5E5712B72D9EAAFCE88AC094102C73AEF68C61AEEB`.
- Public first seams are exactly builder `v2 asset provenance mismatch` and
  verifier `E_V2_ASSET: provenance`; canonical v2 config/candidates are absent.

Refuse on drift.

## Known inventory and risk

Prior real-input readiness proved 123 frozen-v1 asset rows, 16 exact approved
Markdown image-reference spans on source pages 3, 6, 7, 13, 25, 31, 32, 34 and
40, 101 in-scope reader assets, 16 evidence-only assets and six page-123/124
advertising exclusions; two render assets are non-path records. Current author
projection leaves 107 assets without source spans and sets all reader flags
false, so it correctly fails asset provenance.

A source Markdown span is not available for every visual region. Do not invent
text spans, owner anchors, placements, replacements or reader value merely to
pass the current A3 asset schema.

## Required architecture decision

Produce an exact, code-ready B1c4 specification for all 123 frozen assets:

1. recompute and classify every asset by truthful provenance channel:
   exact Markdown image-reference span, frozen visual-region/page/bbox evidence,
   reviewed provisional full-page render, or excluded advertising;
2. decide the closed conditional asset schema for those channels, including
   source page/region, immutable path/digest/bytes/media/dimensions, owner,
   reader/evidence disposition, event placement and migration identity;
3. give exhaustive mutually exclusive counts for reader, evidence-only,
   reclassified/replaced/suppressed/excluded assets, including the two non-path
   render records; explain any difference from the readiness counts;
4. derive exact semantic owners and source-order placement without owner-end
   fallback. Cover the known regressions explicitly: p3 identity logo before
   first prose; p31/p32 coastal-town then boat immediately before `Prologue`;
   p6 `Summary` crop evidence-only while ruined-hall hero remains reader;
   platform logos/promo badge evidence-only; direct reference before/between/
   after fragments and page/column continuation;
5. specify physical-unit/replacement closure for p106/p107 map pages and six
   front/back pregen pairs 111/112 through 121/122. Step 7 must emit truthful
   provisional full-page facsimiles and accessible semantics while final binary
   quality selection remains post-MASTER_RU Step 8A;
6. exclude all page-123/124 assets from hierarchy/events/reader/candidate/visual
   review/downstream while conserving their frozen rows under OUT-026;
7. define exact 123-row asset migration outcomes, target namespaces,
   `replaces` closure and decision refs; every final asset must be materialized
   exactly once or declared new-reviewed with exact evidence;
8. define builder and independent verifier behavior from immutable bytes and
   frozen metadata, including copy/digest/media/dimension checks, owner/event
   placement, reader/evidence separation, no duplicated child crop and candidate
   byte emission; do not let the verifier trust builder sidecars;
9. specify positive/negative mutation coverage and exact next public-preflight
   seam after honest asset closure; separate later typed-payload/recovery/visual-
   review work rather than filling it synthetically;
10. give minimal owned engineering files, ordered stages and hard stop rules.

Resolve whether the current A3 requirement for nonempty text `source_span_ids`
on every asset is too narrow for visual-region provenance. Any schema extension
must remain closed and strengthen, not weaken, exact source identity and
placement validation.

End with one terminal result:

- `READY_FOR_V2_COMPLETE_AUTHORING_PHASE_B1C4_ASSET_ENGINEERING`, or
- `BLOCKED_V2_COMPLETE_AUTHORING_PHASE_B1C4_ASSET_ARCHITECTURE` with exact
  missing evidence/authority.

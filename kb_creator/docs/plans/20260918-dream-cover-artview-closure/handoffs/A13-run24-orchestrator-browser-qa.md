# A13 run24 orchestrator browser QA

Date: 2026-09-18

Scope: read-only browser verification of the exact Stage-40 artifact from
`20260918-publication-24`. This is engineering evidence only; it does not
replace independent release review or explicit user acceptance.

## Bound artifact

- Run identity: `6C930320298EBD97CC0E77BD603D6B089EE0FB1F3F593069D363B3672D210643`
- HTML SHA-256: `774F22BC2D1FF55BBCEF22ED5BC8539508F265A01D34E7AC8C6E87CE82AB7166`
- HTML bytes: `153683`

The immutable artifact directory was served read-only from localhost because
the browser automation policy blocks inspection of `file://` pages. No source
or generated artifact was edited during this check.

## Browser evidence

- The first reader page visibly contains the accepted 1700x2200
  `assets/pdf-page-001-cover.png` cover.
- The credits page follows the cover and the source contents follows credits.
- The contents contains exactly 18 entries under
  `data-toc-layout="flat"`; every entry has `toc-level-1`, computed
  `font-weight: 500`, and computed `text-transform: none`.
- The three appendix entries are visual peers of the other contents entries.
- Appendix A visibly renders neutral stat blocks with separate character
  headings. The DOM contains seven `.statblock-card` elements and zero
  blockquotes on source page 18.
- The document contains zero visible `figcaption` elements while image `alt`
  text remains available to accessibility inspection.

## Result

PASS for orchestrator browser QA. Independent release review and exact user
acceptance remain open gates.

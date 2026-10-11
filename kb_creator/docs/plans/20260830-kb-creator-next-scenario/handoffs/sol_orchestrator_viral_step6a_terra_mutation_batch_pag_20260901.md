# Terra engineering assignment: Viral Step 6A PAG mutation batch

Sequential implementation under accepted packet sections 5.3, 6-7, 8.2 PAG,
11 and 12.

## Baseline and writes

- Library: `60FAA7293402BDD5124CB0DB4CBD8EDD744CDEBADFF82B7C4F077A6B0A6D28D0`.
- Tests: `6EA2E0901E47E77DFC99180345661C1DE6FBC25925793A79B371198550907563`.
- Editable: those two files and new receipt
  `terra_engineering_viral_step6a_mutation_batch_pag_20260901.md` only.
- Everything else read-only; no live/protected/cache/Git write.

## Implement exact PAG 28

Implement every packet id/code covering:

- page set/duplicate/number/id/engine-index/role/content-mode;
- Markdown and render path/bytes/hash plus render number/dimensions/DPI;
- missing live Markdown/render, source/render marker and master concatenation;
- content orphan/duplicate/order/predecessor/successor/operation/asset-link.

Every row mutates the real physical page/render/master/content authority
selector or live bytes with a distinct callable. Apply only the exact literal
transport reseals required to pass inventory without repairing the targeted
semantic error. Extend production verifier page/content graph closure and live
file binding in accepted order; no COMMANDS proxy.

Each case uses one `_test_verify`, exact earliest code and full closed audit
with real hashes, PASS, zero outside/undeclared/residue. Preserve completed
families and 371 collection. Run PAG in runner-safe chunks, representative
regression, BLD 3 and collect using Python `-B`/no-cache. Receipt embeds all 28
full ordinal objects/digest. Complete only 28/28; no redesign/live/cleanup.

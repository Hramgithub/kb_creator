# Terra engineering assignment: Viral Step 6A NAV mutation batch

Sequential implementation under accepted packet sections 5.3, 6-7, 8.2 NAV,
11 and 12.

## Baseline and writes

- Library: `497C3F77321E5278818E0959611AD46039F85ED403670FE5B1DAB8D7124BFDA6`.
- Tests: `6D8A78DA9FAC0DA264E62FB6EE48BE2103F63CAFC8CB6DA2E897F232E84CCB3A`.
- Editable: those two files and new receipt
  `terra_engineering_viral_step6a_mutation_batch_nav_20260901.md` only.
- Everything else read-only; no live/protected/cache/Git write.

## Implement exact NAV 15

Implement every packet id/code for row set, duplicate/wrong anchor, source page,
engine index, first/last/middle previous-next links, dangling link, Markdown and
render paths/hash, role and closure promotion.

Each case mutates its real physical NAVIGATION_INVENTORY selector or bound live
render/Markdown value with a distinct callable. Apply only literal inventory/QA
transport changes required to reach navigation semantics; never repair the
target. Extend production verifier to enforce 124 ordered anchors, exact
previous/next chain, path/hash/page/index/role and candidate-needs-review
closure. No COMMANDS proxy.

Each uses one `_test_verify`, exact earliest code and full closed audit with
real hashes, PASS, zero outside/undeclared/residue. Preserve completed families
and collect 371. Run NAV 15 in explicit chunks, representative regression,
BLD 3 and collect via Python `-B`/no-cache. Receipt embeds all 15 full objects
and digest. Complete only 15/15; no redesign/live/cleanup.

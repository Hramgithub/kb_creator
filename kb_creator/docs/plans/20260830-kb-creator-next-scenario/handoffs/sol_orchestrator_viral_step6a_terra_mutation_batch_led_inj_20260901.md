# Terra engineering assignment: Viral Step 6A LED and INJ mutation batch

Sequential implementation under accepted packet sections 5.2-5.3, 7.3,
8.1 LED, 8.3 INJ, 11 and 12.

## Baseline and writes

- Library: `D36F0DC6A9FC67F3C70CC0BC80EE64522FEECB1EC524139FDE6DDCC0F7AB03D3`.
- Tests: `9AB8C9E94325DA74DA32E4639777CCBEF319663C1230A6A1035FD5C6BBEA1BC9`.
- Editable: those two files and new receipt
  `terra_engineering_viral_step6a_mutation_batch_led_inj_20260901.md` only.
- Everything else read-only; no live/protected/cache/Git write.

## Implement exact 11 rows

LED 6:

- open count, row count, row state, review state, blocker id set and affected
  scope count with the exact packet ids/codes.

INJ 5:

- profile seal mutation, production profile on TEST route, identity provider
  bound to another profile, filesystem provider bound to another profile and
  repository root observation mismatch with the exact packet ids/codes.

Each row needs a distinct real ledger/profile/provider/root selector mutation,
literal reseal/transport tuple, one shared real `_test_verify`, exact earliest
code and full closed `MutationAudit`. INJ must exercise actual admission and
must never allow a production-kind non-module context as a positive case. LED
must operate on physical blocker/review authorities, not COMMANDS proxy.

Preserve completed families and collect 371. Run all 11, representative
completed-family regression, BLD 3 and collect via Python `-B`/no-cache.
Receipt embeds all 11 full ordinal objects/digest. Complete only 11/11; no
redesign, live command or cleanup.

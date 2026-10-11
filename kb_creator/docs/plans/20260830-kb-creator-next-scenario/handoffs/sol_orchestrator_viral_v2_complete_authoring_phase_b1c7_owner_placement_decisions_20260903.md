# Orchestrator decision closure - Viral v2 B1c7 owner and placement

## Authority and boundary

- Goal: `20260830-kb-creator-next-scenario`.
- Slice: `7-v2-complete-publication-authoring / B1c7-asset-placement`.
- Owner: main-chat orchestrator, `gpt-5.6-sol` / medium by repository policy.
- This artifact freezes semantic decisions needed by the architecture role. It
  is not an implementation receipt, publication config, candidate, render, or
  acceptance decision.
- Source PDF identity:
  `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05`.
- Accepted reconstruction aggregate:
  `68C17FB765A89C6146398868E61F1F6EB7B2FE4EAFBA8C2C2C8F42260BBDBA83`.
- Bound diagnostic inventory:
  `sol_architect_viral_v2_complete_authoring_phase_b1c7_asset_placement_inventory_20260903.json`,
  SHA-256
  `824993B38D6A72D0384F84347E55855462A48B6D0D56A00F8CA4BEC7EE275785`.

## Final owner rule

The reviewed semantic owner is authoritative for reader placement. A frozen-v1
coarse owner remains immutable audit provenance but is not allowed to override
the reviewed owner solely to keep an old migration row textually unchanged.

For each owner change the closed ledger must preserve both values and record a
typed `reviewed_owner_refinement` decision with its evidence/decision refs.
This changes neither logical asset id nor the six B1c4 identity fields. It is
not a binary replacement and must not be represented as one.

The seven refinements are final:

1. ruined-hall hero: `viral-introduction-summary` -> `viral-introduction`;
2. Santina portrait: `viral-one-night-in-perla-npcs` ->
   `viral-one-night-in-perla-npcs-santina-maria-salvatore`;
3. Padre portrait: `viral-one-night-in-perla-npcs` ->
   `viral-one-night-in-perla-npcs-padre-angelo`;
4. church art: the same Padre owner refinement;
5. morgue art: `viral-isola-hospital-locations` ->
   `viral-hospital-morgue`;
6. coastal-town art: `viral-isola-prologue` ->
   `viral-isola-plots-and-schemes` under OUT-005;
7. fishing-boat art: the same Plots and Schemes refinement under OUT-005.

The final hierarchy must materialize the Santina, Padre and Morgue anchors as
real semantic targets. Aliases, generated navigation anchors and coarse-parent
fallbacks are forbidden.

## Visually frozen relative placements

The source PDF pages were freshly rendered at 110 dpi and inspected in compact
batches. The following reader relations are final. The architecture role must
resolve them to immediate non-asset source event ids without breaking source
bytes, xref spans or paragraph continuity.

| Page | Asset digest/id prefix | Final semantic relation |
| ---: | --- | --- |
| 3 | `ed401272` | before the first `Opening Message` prose |
| 6 | `4592e580` | after the `Introduction` heading and before `Summary`; suppress the typographic `Summary` crop |
| 25 | `4fd93a36` | immediately before `Santina Maria Salvatore` heading |
| 25 | `bc2ae2b3` | immediately before `Padre Angelo` heading |
| 25 | `360213a4` | after the complete Padre Angelo body |
| 31 | `b90cb9a3` | first Plots and Schemes art |
| 32 | `da0cac1c` | second Plots and Schemes art, then `Prologue` |
| 40 | `694c04bf` | after the Morgue continuation/keeper-note unit and before `Old Files` |
| 46 | `f0ecf365` | immediately before `7. Cremation Pit` |
| 48 | `1627aa2f` | within `10. Chapel & Crypt`; after the complete `The Witch Board` paragraph and before its `Possible Visions from The Sight` inset; never after `11. Catacomb Entrance` |
| 49 | `87d8a9e4` | after the preceding Keeper's Notes and before `Hastalyk Awakens` |
| 54 | `29e9a40a` | immediately before `Cinematic Ending` |
| 55 | `ba787578` | after `Escaping the Island` body and before the page-56 Expanded Ending hero |
| 56 | `c708f914` | immediately before `Expanded Ending`; it is the full-width page hero, not a page-end asset |
| 60 | `53643514` | immediately before `Catacomb Encounters`; it is the full-width page hero, not an asset after New Rules |
| 65 | `8e99d692` | after `New Mythos Horrors` and before the Hastalyk creature title/body |
| 66 | `81953e33` | immediately before `The Plague Monk` title/body |
| 66 | `6e1d78ee` | immediately before `The Reliquae` title/body |
| 67 | `2fbd3199` | after both infection tables and before the right-column `New Mythos Tome` section |
| 67 | `dbe93023` | after `New Mythos Tome` and before `Iuramentum Corruptionis` |
| 78 | `8dfcf412` | Handout 10 map before `Enoch's Vision` / Handout 11 |

For ordinary marker-backed rows not named above, the exact immutable marker
range plus accepted page/column ordering remains authoritative. A large
coordinate gap, nearest heading, asset-array order, or marker-at-page-end is
never sufficient alone.

## Physical-unit decisions

The topology is frozen as 79 source slots plus 14 physical-unit slots unless
the architecture role proves a contradiction from bound evidence. The seven
physical units and namespace mapping are exact:

| Reviewed unit | Physical unit | Ordered slots |
| --- | --- | --- |
| `viral-map-ground-floor-basement-p106-p107` | `physical_units:viral-map-ground-floor-basement` | page 106 slot 0; page 107 slot 1 |
| `viral-pregen-111-112` | `physical_units:viral-pregen-marco` | front 111 slot 0; back 112 slot 1 |
| `viral-pregen-113-114` | `physical_units:viral-pregen-corrina` | front 113 slot 0; back 114 slot 1 |
| `viral-pregen-115-116` | `physical_units:viral-pregen-enoch` | front 115 slot 0; back 116 slot 1 |
| `viral-pregen-117-118` | `physical_units:viral-pregen-peter` | front 117 slot 0; back 118 slot 1 |
| `viral-pregen-119-120` | `physical_units:viral-pregen-ku-hyeon` | front 119 slot 0; back 120 slot 1 |
| `viral-pregen-121-122` | `physical_units:viral-pregen-blank` | front 121 slot 0; back 122 slot 1 |

Each page is a full-page facsimile. The map key/legend/scale and character back
semantics remain separate translatable supplements after their corresponding
unit. A crop, OCR text, or generated index cannot substitute for a page slot.
Pages 123-124 remain advertising with no reader placement.

## Closure requirements

- Exactly 93 reader rows must receive one final owner and one placement.
- Exactly 32 evidence-only rows retain `placement: null` and emit no reader
  event or binary link.
- Source-slot rows name immediate previous/next non-asset source events, with
  at least one non-null, and a deterministic zero-based ordinal for shared gaps.
- Physical rows bind one exact asset to one exact page slot.
- The ledger must close every currently null event target; no unresolved,
  inferred donor, wildcard or free-text-only selector is permitted.
- The architecture role must prove that the page-48 decision preserves the
  complete Witch Board paragraph as one readable unit even though the printed
  page break places the illustration above its continuation.
- Builder/verifier independence, symmetric mutation coverage and the exact
  next migration evidence-schema seam remain as specified by the first B1c7
  receipt.

No user question is required for these already source-resolved choices.


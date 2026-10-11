# Viral v2 Phase B1c3 xref-closure architecture receipt

## Receipt metadata

- Goal id: `20260830-kb-creator-next-scenario`.
- Step id: `7-v2-complete-publication-authoring / B1c3-xref-closure`.
- Contributor role: `nri-architect`.
- Policy model / effort: `gpt-5.6-sol` / `high`.
- Actual platform model / effort: unavailable; the platform did not expose a
  separately verifiable runtime identity for this assignment.
- Orchestrator policy owner: main chat, `gpt-5.6-sol` / `medium`; ownership did
  not transfer.
- Assignment state: `matched` to the repository role contract; platform runtime
  remains unverified.
- Scoped override: exact task packet
  `TASK_PACKET_architect_viral_v2_complete_authoring_phase_b1c3_xref_closure_20260903.md`,
  SHA-256
  `94A3F6EAFA7F7FBB32574CAA36F524DD48937DB6E4CD50E11507577E2A492346`.
- Scope: read-only architecture, dependency and remediation specification for
  truthful source xrefs, generated navigation, migration closure and required
  event splitting.
- Result: `complete`; this is not implementation, independent review, candidate
  acceptance or release approval.
- Files changed: only this immutable receipt.
- Timestamp: `2026-09-03T11:34:48+03:00` (Europe/Moscow).
- Elapsed time: approximately 45 minutes.
- Token use: unavailable.

## Bound checkpoint and evidence

The assignment did not drift:

- B1c2 receipt:
  `AD46004F0C6C21942C051A183323CBDCB427CAE14BEB0DD678730751A64F7736`;
- author helper:
  `AA5D7DA9A22E81AF79F1DC6056FDAD74675E4B45B9C57716E7E3444763C40C8D`;
- author tests:
  `2489E4E11B6366DF07004374E88379EA646CA52A2605C7A77AA41180D86ACE84`;
- builder:
  `2C2A5A998C55FEF07B141CC6D146A2CD40302F7E95679E1DF1272385C7DD346B`;
- independent verifier:
  `7FD59EF3BB2BCB01E9DB943FB8921F7AF7C95C79D3873379A8167153C59F06F8`;
- canonical `publication_config_v2.json` and Viral v2 candidate materializations:
  absent.

Files checked read-only were the task packet, canonical plan/context/status,
NRI goal governance, the accepted v2 architecture receipt, A3 approval and
xref-migration receipts, B1c/B1c2 receipts and packet, author helper/tests,
builder/verifier, frozen v1 config, accepted reader pages, the hash-bound user
review registry and the relevant evidence ledgers. The registry identity is
`D20414D48405A761ADD31E538B6940F8A3E0F1FB11044AF73EAD122D96C616E8`.
No code, test, config, candidate, plan/context/status, input/evidence, Git or
downstream path was edited.

## Architecture decision

The approved sentence “start with all 237 v1 xrefs” is an **input-conservation
rule**, not a requirement that every input row be forced into the source-backed
`xrefs[]` schema. A3 remains unchanged in substance: every row materialized in
`xrefs[]` must bind its visible text to exact slices owned by its declared
source event and must execute there.

Generated navigation is not source text. It must be represented as four
generated-navigation events with a distinct, closed and independently derived
payload, not as source-backed xrefs and not as migration-only rows with no
reader representation. Its labels and targets are projected from the exact
hash-bound frozen-v1 xref rows and final hierarchy migration; they are never
claimed as reader-page slices. Exact source TOC bytes remain conserved as an
`OUT-002` suppression/replacement claim and are not duplicated in the reader.

This requires a narrow schema extension. The current approved implementation
cannot be made truthful by data authoring alone because it:

1. requires every event, including `generated_navigation`, to own at least one
   source span;
2. treats all event string leaves as source/recovery-bound authorial text;
3. renders `generated_navigation` as an empty string;
4. requires every xref to have a hierarchy target and renders every xref as an
   internal link, so it cannot preserve the accepted exact non-link row;
5. audits materialized migration identity only for hierarchy/assets/xrefs, not
   generated navigation items.

Neither A3 source-binding checks nor their builder/verifier independence may be
weakened.

## Exact inventory and reader-link conservation

The final inventory is:

| Class | Frozen rows | Final items | Emitted internal links | Exact rule |
| --- | ---: | ---: | ---: | --- |
| `line_exact`, single internal segment | 39 | 39 source xrefs | 39 | preserve exact segment text and target |
| `line_exact`, split internal row `p037-handout-21` | 1 | 2 source xrefs | 2 | one final xref per frozen segment, in frozen order |
| `line_exact`, external exact non-link `p057-keeper-rulebook` | 1 | 1 validated source xref | 0 | exact text remains unlinked; target is null |
| generated TOC | 137 | 135 navigation items | 135 | exclude the two advertising targets |
| generated handout index | 41 | 41 navigation items | 41 | exact frozen label/target projection |
| generated keeper-map index | 6 | 6 navigation items | 6 | exact frozen label/target projection |
| generated pregen index | 12 | 12 navigation items | 12 | exact frozen label/target projection |
| **Total** | **237** | **236** | **235** | plus one exact validated non-link |

Therefore the correct metrics are not the old undifferentiated `links=237`:

- `frozen_xref_rows=237`;
- `source_xref_rows=41`;
- `source_xref_segments=42`;
- `materialized_source_xrefs=42`;
- `generated_navigation_items=194`;
- `excluded_navigation_rows=2`;
- `materialized_navigation_operations=236`;
- `emitted_internal_links=235`;
- `validated_non_links=1`.

The two targetless excluded rows are exactly `toc-viral-merchandise` and
`toc-viral-back-cover`. Their target hierarchy rows, `viral-merchandise` and
`viral-back-cover`, are also absent from the reader hierarchy under `OUT-026`;
the exhaustive hierarchy migration still retains their frozen input rows as
targetless `excluded_advertising` evidence. Final reader hierarchy count is
therefore 166, while the hierarchy migration input count remains 168.

## Closed source-xref contract

`xrefs[]` remains source-backed only. Extend its closed row by one field:

```text
xref_id
source_event_id
source_page
target_anchor       # string when emit_link=true; null otherwise
reader_text
source_slices
emit_link           # boolean
migration_row_id
```

Rules:

- every source slice is a nonempty, ordered subrange of a span owned by
  `source_event_id`;
- concatenated exact decoded slices equal `reader_text` byte-for-byte after
  UTF-8 decoding; no case, punctuation or whitespace normalization is allowed;
- `emit_link:true` requires one resolved final hierarchy target and candidate
  emission of exactly `[reader_text](#target_anchor)` inside the declared event;
- `emit_link:false` requires `target_anchor:null` and candidate preservation of
  exact `reader_text` without Markdown link syntax;
- the 39 single internal rows retain their original `xref_id`; the external row
  remains `p057-keeper-rulebook`;
- `p037-handout-21` becomes exactly
  `p037-handout-21-segment-01` (`Handout #30` -> `viral-handout-30`) and
  `p037-handout-21-segment-02` (`Handout #31` -> `viral-handout-31`), in that
  order, both inside the one exact source line event;
- source-row `visible_text` is not a substitute for segment text. Final text is
  always the exact ordered `segments[].reader_text` backed by the corresponding
  `segments[].source_text` occurrence.

## Closed generated-navigation contract

Create exactly four `generated_navigation` events owned by these final
containers:

| Family | Event id | Owner anchor | Entry count |
| --- | --- | --- | ---: |
| TOC | `generated-navigation-toc` | `viral-contents` | 135 |
| handout index | `generated-navigation-handout-index` | `viral-player-handouts` | 41 |
| map index | `generated-navigation-map-index` | `viral-keeper-maps` | 6 |
| pregen index | `generated-navigation-pregen-index` | `viral-pregenerated-investigators` | 12 |

The event keeps `source_operation: generated_navigation`, but uniquely has
`source_span_ids:[]`, `payload_bindings:[]`, and one additional closed
`generated_placement` object `{after_event:<owning-heading-event-id>}`. Its
`page` is the referenced heading event page. Its order is derived from that
heading event and the fixed family order `toc`, `handout_index`, `map_index`,
`pregen_index`; it is not assigned a fictitious source byte.

Its `content` has the only allowed generated payload schema:

```text
kind = generated_navigation
family = toc | handout_index | map_index | pregen_index
owner_anchor
decision_ref = OUT-002
entry_count
entries[]:
  navigation_id
  source_xref_id
  reader_text
  target_anchor
  migration_row_id
```

For every entry, builder and verifier independently reload the frozen-v1 row
named by `source_xref_id`, verify its canonical row hash through migration,
require the exact selector/family and `generated_*` policy, require
`reader_text == visible_text`, resolve the sole frozen target through the closed
hierarchy alias rule below, and require
`migration_row_id == generated_navigation_items:<source_xref_id>`. Entries are
ordered exactly as their frozen rows. Omissions, duplicates, reordered rows,
free labels, free targets and source slices on generated events fail closed.
The renderer emits one Markdown list link per entry; the independent verifier
recomputes the same 194-item inventory and exact 194 emitted links from
candidate bytes.

The accepted source TOC bytes on page 5 remain in the exhaustive source
partition under a non-reader suppression owner with decision `OUT-002`. They do
not belong to the generated event, and candidate/provenance must prove zero
source-TOC duplication.

## Exhaustive xref migration

Frozen source ids always use `xrefs:<frozen-xref-id>`. Final target namespaces
are only `xrefs:<final-source-xref-id>` and
`generated_navigation_items:<frozen-xref-id>`.

| Frozen-row set | Count | Outcome | Final targets | Decision ref |
| --- | ---: | --- | --- | --- |
| 39 single internal `line_exact` rows plus `p057-keeper-rulebook` | 40 | `retained_unchanged` | one `xrefs:<same-id>` each | null |
| `p037-handout-21` | 1 | `split` | `xrefs:p037-handout-21-segment-01`, `xrefs:p037-handout-21-segment-02` | null, under the mechanical split exception below |
| all generated rows except the two advertising targets | 194 | `replaced` | one `generated_navigation_items:<same-id>` each | `OUT-002` |
| `toc-viral-merchandise`, `toc-viral-back-cover` | 2 | `excluded_advertising` | none | `OUT-026` |

No decision reference may be invented for the split. The two segments and their
order, text and targets already exist in the hash-bound frozen row. Amend the
migration validator with one narrow mechanical-projection rule: an xref
`split` may have `decision_ref:null` only when the frozen row contains more than
one segment and the final xrefs preserve every segment one-to-one and in order,
with no lexical, target or link-policy change. This proves exactly one current
case, `p037-handout-21`; any semantic split, merge, dropped segment or changed
target still requires a catalogued decision. All other non-unchanged outcomes
retain the existing mandatory decision rule.

The migration materialized-target audit must include every generated navigation
item, not only hierarchy/assets/xrefs. Exactly 237 frozen xref rows occur once,
every one of the 236 final items occurs once, and the two excluded rows are the
only targetless rows.

## Event/span splitting algorithm

Before binding source xrefs, refine the existing partition deterministically:

1. Locate every frozen `line_exact.source_line` exactly once in its accepted raw
   page bytes. Locate each `segments[].source_text` once in forward order inside
   that line. Zero or multiple matches stop authoring.
2. Cut the owning span at the raw full-line start/end and at every exact segment
   start/end. Recompute byte/character coordinates and both hashes from raw
   bytes; concatenation must reproduce the original span exactly.
3. Materialize one xref-line event for each distinct source line. Its anchor is
   the frozen row `owner_anchor`; all rows on one line must agree on that owner.
   Different owners on one line are a hard stop.
4. Non-xref intervals remain ordered events under the independently derived
   semantic owner. They may not inherit an xref owner merely through adjacency.
   Empty intervals are omitted; no bytes are dropped or reused.
5. Recompute event ids, fragment ids and derived order keys from
   `(page,start_byte,role_rank,ordinal)`. Every final xref slice must be wholly
   inside its owner event. A slice that straddles an event/span boundary stops.

This exact algorithm replaces the four currently multi-owner events as follows:

| Original event | Xref-line events | Non-xref remainder events | Total replacements | Exact xref-line character ranges and owners |
| --- | ---: | ---: | ---: | --- |
| `event-p045-001` | 7 | 8 | 15 | `2191:2221` 2E; `2223:2252` 2F; `2254:2284` 2G; `2286:2315` 2H; `2535:2561` 2I; `2563:2590` 2J; `4774:5111` Mass Graves |
| `event-p048-001` | 3 | 4 | 7 | `1314:1495` Catacomb Entrance; `3634:4164` Catacombs; `4776:5141` Catacombs |
| `event-p049-001` | 3 | 4 | 7 | `28:174` Catacombs; `176:527` Catacombs; `2852:3320` Temple of Morbus |
| `event-p052-001` | 2 | 3 | 5 | `491:842` Hastalyk Awakens; `1452:1841` Epilogue |

Thus four coarse events become exactly 34 events, a net increase of 30. The
ranges are zero-based half-open Unicode character ranges in the accepted page
bytes decoded as UTF-8; implementation must recompute them and refuse drift,
not embed them as substitute evidence.

## Target-anchor derivation and aliases

- A source xref target comes only from its frozen segment `target_anchor`; a
  generated item target comes only from its frozen row's sole `target_anchors`
  value. Arbitrary first-target selection is forbidden.
- If the same anchor exists in final hierarchy, it is used unchanged, including
  an `anchor_only` representation.
- An old anchor may rebind only through its exhaustive hierarchy migration row:
  exactly one final `hierarchy:<new-anchor>` target and a non-null catalogue
  decision. The xref migration row then uses `retained_rebound` or `replaced`
  with that same decision as applicable.
- Builder and verifier independently derive the old->new alias map. Chains,
  cycles, fan-out, implicit slug/title matching, case folding and fallback to
  root `viral` are forbidden.
- If a target hierarchy row is split/merged, the referring xref requires one
  explicit reviewed target decision; no target is inferred from proximity.
- `viral-merchandise` and `viral-back-cover` resolve only to exclusion. Their
  two TOC rows cannot alias to another anchor or appear in reader navigation.

## Builder and independent verifier behavior

Both public implementations must independently:

- validate the extended source-xref conditional schema and exact source slices;
- validate the generated payload against frozen-v1 rows, hierarchy migration,
  `OUT-002`, family ownership, order and exact counts;
- render/verify 41 source links, one validated non-link and 194 generated links;
- prove every link target exists exactly once and every declared item appears
  exactly once in its declared event;
- prove both excluded advertising rows, targets and labels are absent;
- recompute the 237-row migration conservation and 236-target closure;
- derive all metrics rather than accept constants supplied by the author;
- keep builder and verifier code independent; the verifier must not import the
  builder or accept builder sidecars as authority;
- reject before candidate creation on every mismatch. Existing A3 exact
  text/slice/owner checks remain mandatory for all `xrefs[]` rows.

## Next engineering packet

Minimal owned file scope:

- `kb_creator/scripts/author_viral_master_en_v2_config.py`;
- `kb_creator/tests/test_author_viral_master_en_v2_config.py`;
- `kb_creator/scripts/build_scenario_master_en.py`;
- `kb_creator/tests/test_build_scenario_master_en.py`;
- `kb_creator/scripts/verify_scenario_master_en.py`;
- `kb_creator/tests/test_verify_scenario_master_en.py`;
- one new immutable engineering receipt.

Ordered stages:

1. Recheck every bound hash and bind the registry containing `OUT-002` and
   `OUT-026`; stop on drift.
2. Remove the two excluded hierarchy projections, close their hierarchy/xref
   migrations, and implement the deterministic source span/event refinement.
3. Author the 42 source xrefs and exact 41-row source migration, including the
   mechanical split and external non-link.
4. Implement the four-event/194-item generated-navigation contract and its
   renderer, migration namespace and derived metrics.
5. Implement the same contract independently in the verifier; do not share
   builder validation helpers.
6. Run focused positive/negative public tests, the current combined baseline,
   py-compile, deterministic serialization, diff checks, canonical/candidate
   absence and checkout-temp cleanup. Run both public preflights and record the
   exact first later seam.

Required positive tests include the exact family/count table, 42 unique source
segments, 41/1 link/non-link split, both ordered p037 targets, all 237 migration
outcomes, four generated event owners, 194 exact derived entries, 235 emitted
links, 166 reader hierarchy targets, the four-event 34-replacement topology,
alias identity and deterministic JSON bytes.

Required negative tests mutate, independently: source text/slice/event owner;
unsplit or reversed p037 segments; linked external row; missing/non-null excluded
targets; generated label/target/family/order/source id/decision ref; generated
source slices; duplicate/missing generated items; implicit or cyclic alias;
borrowed migration target; foreign target namespace; multi-owner unsplit event;
straddling/reused span; stale counts; and candidate creation after rejection.

Stop without output if any source line/segment is not uniquely locatable, one
line claims multiple owners, any target lacks exact hierarchy/alias closure,
`OUT-002` or `OUT-026` is not hash-bound, any inventory count differs, the two
public implementations disagree, a public gate is weakened, or a forbidden
canonical/candidate/temp artifact exists after execution.

## Expected next seam and exclusions

After honest xref/navigation closure, the unchanged B1c2 projection is expected
to fail at the next A3 check:

```text
builder:  v2 asset provenance mismatch
verifier: E_V2_ASSET: provenance
```

That expected advancement is not permission to fill assets with synthetic
spans. Asset identity/ownership/placement, typed payload completion, recovery
event binding, visual-review closure, candidate materialization, MASTER_RU,
Step 8A, HTML/PDF, production, Git and release remain out of scope. A different
earlier failure is a B1c3 blocker and must be reported rather than bypassed.

## Acceptance criteria and blockers

B1c3 engineering is acceptable only when all exact counts and migration rules
above pass both public implementations, all negative tests fail closed before
output, the first remaining seam is the asset-provenance pair above, temp count
is zero, and canonical config/candidates remain absent.

No evidence or authority blocker remains for this architecture decision. The
mechanical split exception avoids inventing a decision reference while staying
strictly narrower than the accepted frozen row. Fresh implementation and its
independent review remain future gates; this receipt does not approve either.

READY_FOR_V2_COMPLETE_AUTHORING_PHASE_B1C3_XREF_ENGINEERING

# Architecture receipt - Viral v2 B1c7 reader-asset placement

## Receipt metadata

- Goal id: `20260830-kb-creator-next-scenario`.
- Step id: `7-v2-complete-publication-authoring / B1c7-asset-placement`.
- Role: `nri-architect`; requested `gpt-5.6-sol` / high.
- Actual platform model/effort: unavailable; requested role is the reasoning contract.
- Orchestrator policy owner: main chat `gpt-5.6-sol` / medium. Ownership did not transfer.
- Assignment state: matched by the hash-bound packet; platform runtime unverified.
- Scoped override: none.
- Timestamp: `2026-09-03T20:39:11.1723616+03:00` evidence checkpoint, Europe/Moscow; receipt finalized in the same bounded turn.
- Elapsed time: approximately 30 minutes; exact platform elapsed counter unavailable.
- Token use: unavailable.
- Result: `CHANGES_REQUIRED_V2_COMPLETE_AUTHORING_PHASE_B1C7_ARCHITECTURE`.
- This is architecture/root-cause analysis, not implementation, candidate acceptance, or release review.

## Scope and writes

Only this receipt and its strictly necessary 93-row JSON companion were written.
The complete inventory is too large for a useful inline Markdown receipt.

Companion:
`sol_architect_viral_v2_complete_authoring_phase_b1c7_asset_placement_inventory_20260903.json`

- Bytes: `347947`.
- SHA-256: `824993B38D6A72D0384F84347E55855462A48B6D0D56A00F8CA4BEC7EE275785`.
- Schema: `kb_creator.architecture.asset_placement_inventory.v1`.
- Status: `changes_required_not_an_authoring_or_publication_config`.
- Exactly 93 source-ordered reader rows; each has the full stable asset id,
  page, provenance kind, current binary identity or provisional status,
  exact marker ranges/hash where present, selected comparison block/bbox/hash,
  owner evidence, proposed relation family, and explicit unresolved targets.
- All 32 evidence-only ids are separately enumerated; they remain unplaced.
- This companion is evidence, not a frozen placement decision ledger. Null final
  event targets are intentionally not fabricated and must be rejected by any
  future authoring parser.

No code, tests, canonical plan/context/status/release files, source, accepted
reconstruction, v1, candidate, temporary config, render, review bundle,
MASTER_EN, MASTER_RU, HTML, PDF, or Git state was changed. No Step8A extraction
or replacement occurred. No subagent was delegated.

## Bound evidence and identities

The assigned packet matched exactly:
`25E774E250CDFC76164BF92326A21C136DFCF5EFC8CFDED59302488C00D2FA08`.

The relevant current plan/context sections were read before material analysis:
plan lines 3733-3822 and context lines 3166-3231, plus the objective, role,
source-scope and Step8A boundaries. The live review registry entries
OUT-005/006/007/019/024/025/026 were inspected.

| Evidence | Observed SHA-256 |
| --- | --- |
| B1c6 architecture approval | `F46457EB86DE9E5499C8272C6B72C23EAE0D80B42E24F591906B14589230B6E9` |
| B1c6 implementation approval | `690963D07976A244B2389AFE1429AAFFA0A2A3F14F890206E15CB5B068D84BDD` |
| author | `3DA02ADF17E2224C86A1418D18ECB06754E1FC6CD628717C1652EA315968FE1C` |
| builder | `C496B8649E36C8D656C1CC93C25689B97E263339F7B12775A3D24C5CFBE80D3E` |
| verifier | `E593D0B9EEA9CC1E71642DBC2527774FDB923D74914A52684391623CD9A8E5C1` |
| frozen publication_config_v1.json | `C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30` |
| accepted-v4 ASSET_MANIFEST.json | `914A2C8B46401830EDBDEADDDDA24C7A8C0B6442F2775C439A79CC5529D283E9` |
| comparison/comparison.json | `5A4DB5DB697B1E483926AB1DAB387CB496EF0539DC76EAD51B830F5DCF1862F0` |
| accepted-v4 MERGE_PROVENANCE.json | `9B0928418E61189B8D15377240730EABBA46D4455D4EA7449338D921168DBCA2` |
| user-review registry | `D20414D48405A761ADD31E538B6940F8A3E0F1FB11044AF73EAD122D96C616E8` |
| source PDF | `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05` |
| boundary ledger 001-040 | `8C0A666D962C879C62B7168B60AB717EA04F833FFE728446F150F64FCB24DDAF` |
| boundary ledger 041-068 | `8673868ED762E327517891D7C72DBA21A5C88F1A4173EBB0EFF597D30453EF13` |
| boundary ledger 069-122 | `14338236CDB2AAE6213CCE5F36DA93C661F2DF35D9F7E96F8346C770BF00CFD1` |
| semantic_unit_review.json | `41E3F6F7AAC5970D9FCFC032926B0F5FB48E41D544414130AED85AB8672EAB78` |
| closure_report.json | `3AB47BE01FED57773A3DD3419D0CF0D2DF4658A56E813FF3B02BD5E4C8B99ACA` |

Repeated in-memory `author()` calls verified the accepted-v4 aggregate:
377 files, 41079424 bytes, inventory
`68C17FB765A89C6146398868E61F1F6EB7B2FE4EAFBA8C2C2C8F42260BBDBA83`.

Also inspected: B1c4 architecture/critic receipts, B1c5 declaration receipts,
B1c6 architecture/implementation receipts, current author source graph and
asset projection, independent builder/verifier canonical schema, A3 input
binding, typed-chunk renderer, migration decision catalogs, accepted page
decisions and selected blocks for conflict pages, and governance contributor
receipt rules.

The 128/128 regression and both frozen-v1 preflights are prerequisite evidence
from the bound B1c6 approval, not a fresh test run by this read-only task. I did
not run test commands that could create fixture/temp output.

## Reproduced counts and what they do not prove

| Quantity | Count |
| --- | ---: |
| Final asset declarations | 125 |
| Reader / evidence-only | 93 / 32 |
| All provenance: Markdown / visual / provisional | 16 / 100 / 9 |
| Reader provenance: Markdown / visual / provisional | 9 / 75 / 9 |
| Path-backed readers with one exact Markdown marker | 84 |
| Cover without a marker | 1 |
| New reviewed full-page targets without a marker | 8 |
| Existing pregen fronts requiring physical slot 0 | 6 |
| Proposed source-slot placements | 79 |
| Proposed physical-unit-slot placements | 14 |
| Current authored asset events | 0 |
| Current events / hierarchy / xrefs / recoveries / review units | 480 / 166 / 42 / 0 / 136 |
| Current event types | 472 text_fragment, 4 heading, 4 generated_navigation |

The 79/14 proposal is a topology partition, not 93 approved placements:
79 source slots are the cover plus 78 ordinary marker-backed readers; 14
physical slots are two Ground Floor & Basement pages plus all twelve pregen
front/back sides. Treating the six existing pregen fronts as ordinary crops
would fail OUT-025 even though their provenance remains `visual_region`.

The companion deliberately contains zero claimed publication-ready final
placements. This is the honest result of the unresolved owner/event contracts
below, not a license to emit an incomplete config.

## P1-A: frozen coarse owners conflict with approved semantic owners

The reviewed asset ledger has seven reader-owner differences from frozen v1.
Two are already explicitly resolved by OUT-005: coastal city and boat both
belong to `viral-isola-plots-and-schemes`, in city -> boat -> Prologue order.
They are not new open findings. The generic companion owner-difference flag
for these two is discharged by that already-frozen decision.

Five additional differences require an explicit contract resolution:

| Asset / page | Frozen v1 owner | Reviewed intended owner | Current target exists? |
| --- | --- | --- | --- |
| ruined-hall hero / 6 | viral-introduction-summary | viral-introduction | yes |
| Santina portrait / 25 | viral-one-night-in-perla-npcs | viral-one-night-in-perla-npcs-santina-maria-salvatore | no |
| Padre portrait / 25 | viral-one-night-in-perla-npcs | viral-one-night-in-perla-npcs-padre-angelo | no |
| church art / 25 | viral-one-night-in-perla-npcs | viral-one-night-in-perla-npcs-padre-angelo | no |
| morgue art / 40 | viral-isola-hospital-locations | viral-hospital-morgue | no |

Thus four assets require three not-yet-materialized semantic owner anchors.
The reviewed relations are respectively before Introduction, before the
Santina heading, before the Padre heading, after Padre's body, and after the
Morgue Keeper note/before Old Files. The p40 relation explicitly continues
across the page boundary; page-start proximity is not its semantic owner.

B1c4's earlier receipt says all frozen owners are preserved except the two
Plots and Schemes corrections. The current canonical B1c4 asset rows do not
yet carry any owner field, so current code has not resolved this contradiction.
Do not silently change five `retained_unchanged` migration rows, invent
aliases, or retain a coarse parent solely to make validation pass. The
orchestrator must obtain a bounded architecture/critic decision defining
whether the final owner is a reviewed refinement with preserved frozen
provenance, or a formally revised retained_rebound migration. No user question
is needed for the already explicit semantic choices; the contract treatment
and target hierarchy projection still need a frozen decision.

## P1-B: source markers alone are not a sufficient placement oracle

A strict no-write audit aligned full comparison text blocks of at least 20
characters to exactly one occurrence outside image markers in accepted page
Markdown. It compared only raw-index order within the same selected view;
different-view raw indexes were never compared numerically.

Across the 84 path readers the diagnostic found:

- 42 with supporting same-view exact text anchors and no detected inversion;
- 10 with proven marker/text-block order inversions;
- 32 without an exact same-view full-block text anchor under this conservative
  rule. This last count includes reviewed hero/physical fronts and visual-only
  or cross-view pages; it is not a count of proven defects.

The ten proven inversion rows, with full ids and every contradictory text
range/hash in the companion, are:

| Page | Asset digest prefix | Visual block | Required source relation to preserve |
| --- | --- | --- | --- |
| 46 | f0ecf365 | original_hybrid 784 | art before 7. Cremation Pit, not after the page's later dock/overlook content |
| 48 | 1627aa2f | original_hybrid 824 | art at the opening crypt-continuation slot, before the later Catacomb Entrance/Catacombs material |
| 49 | 87d8a9e4 | original_hybrid 860 | art before the Hastalyk Awakens heading/body, after the preceding Keeper note |
| 54 | 29e9a40a | original_hybrid 911 | hero before Cinematic Ending |
| 65 | 8e99d692 | original_hybrid 1062 | art before the Hastalyk creature title/body |
| 66 | 81953e33 | original_hybrid 1091 | Plague Monk art before its title/body |
| 66 | 6e1d78ee | original_hybrid 1097 | Reliquae art before its title/body |
| 67 | 2fbd3199 | original_hybrid 1117 | left-column infection art before the next right-column tome section |
| 67 | dbe93023 | original_hybrid 1118 | tome art before Iuramentum Corruptionis |
| 78 | 8dfcf412 | original_hybrid 1236 | Handout 10 map before Handout 11 / Enoch's Vision |

The initial diagnostic also flagged page 22 by matching the short string
`10`; that was a false-positive-prone substring and was excluded by the
conservative full-block rule. The final inventory contains ten, not eleven,
proven same-view conflicts.

Two additional cross-view candidates are explicit blockers to a blanket
marker rule: p56 pipeline image 948 has bbox [0,0,1000,476], while the accepted
marker is at page end; p60 raster image 1030 has bbox [0,0,998,275], while its
marker is after the page's encounter/new-rules text. Existing reviewed source
blocks put the corresponding text below the top art. These need frozen exact
source boundaries, not a raw-index comparison across views.

Some image blocks also have OCR or generated descriptive text retained in
prose while the image marker was appended later. The companion records exact
occurrences outside markers when found. Such strings cannot be deleted by
placement inference: distinguish real visible labels, accessible supplemental
text, and extraction descriptions with explicit source-bound suppression or
recovery evidence in the appropriate later semantic slice.

A large coordinate gap is only a candidate signal. Column resets, full-width
heroes, wrapped portraits, inset boxes and page continuation are distinct
cases. A y-sort or nearest-heading heuristic would reverse p11's left-column
Maya material and right-column Em portrait, and would not safely resolve p67.
Frozen selected-block order plus exact aligned source ranges and reviewed
semantic boundaries must jointly authorize a source slot.

## P1-C: required event/physical targets do not yet exist

The current author emits no asset event and no structured-unit event. Most
non-xref fragments are still root-owned; only four navigation-container
headings are events. The 84 markers therefore cannot be bound by simply
choosing a current enclosing text event: several target boundaries fall
inside those coarse fragments, and four reviewed owners are absent.

The six pregen fronts and eight new full-page targets need seven explicit
physical units: one two-page map and six front/back pairs. Existing reviewed
ledger ids (`viral-map-ground-floor-basement-p106-p107`,
`viral-pregen-111-112`, etc.) and migration physical-unit ids
(`physical_units:viral-map-ground-floor-basement`,
`physical_units:viral-pregen-marco`, etc.) are different namespaces.
Their one-to-one mapping must be frozen, not guessed from names.

Do not solve this by pointing at generated TOC/handout/map/pregen navigation,
by allowing a nonexistent owner, or by placing all assets at an owner's end.

## Proposed minimum closed reusable placement contract

This section is a remediation specification, not approval to implement or
an assertion that the companion already instantiates the contract.

Add exactly two fields to canonical asset rows, preserving the six B1c4
identity fields unchanged: `owner_anchor` and `placement`. Add one
hash-bound `document.placement_ledger` identity. The ledger is a new reviewed
input, not this diagnostic companion, and contains the source-bound slot and
physical-unit decisions below.

For a reader asset, `owner_anchor` is a valid final hierarchy anchor and
`placement` is exactly one of two mutually exclusive objects:

~~~json
{
  "kind": "source_slot",
  "previous_event_id": "source-event-id-or-null",
  "next_event_id": "source-event-id-or-null",
  "slot_ordinal": 0,
  "decision_row_id": "frozen-placement-row-id"
}
~~~

~~~json
{
  "kind": "physical_unit_slot",
  "physical_unit_id": "physical_units:stable-id",
  "page_slot": 0,
  "decision_row_id": "frozen-placement-row-id"
}
~~~

In the first form the two event values are real JSON strings or null, not the
example's literal placeholder text. At least one is non-null. They are the
immediate predecessor/successor non-asset source events of the resolved slot
after source-boundary refinement; generated-navigation events are never
targets. Null is allowed only at a proven reader-document boundary. The cover
uses the document-start source slot, so no third placement operation is needed.
Assets sharing one source gap have contiguous zero-based slot ordinals
independently derived from source page/column/block or reviewed marker order.

In the second form the unit exists exactly once in the frozen ledger, its
ordered page list contains the asset's source page at exactly page_slot, and
the slot contains exactly one reader asset. Map slots are 106 then 107;
pregen slots are front 0 then back 1. A front with accepted binary provenance
still uses this relation. No slot accepts a child crop or an advertising page.

For an evidence-only asset, `placement` is exactly null; it has no reader
asset event, no slot ordinal, no output link and no copied binary. Its frozen
owner/provenance is retained as evidence, not promoted into a reader target.
Missing and empty-object placements are not equivalent to null.

The new ledger must be closed and hash-bound to source PDF, accepted package,
page Markdown, ASSET_MANIFEST, comparison, accepted decisions, boundary
ledgers, registry and frozen v1. Each reader row names exactly one asset,
final owner, source/physical slot, evidence ranges/block identities, and the
applicable decision refs. It records any source-marker relocation or
owner-refinement decision explicitly. It must have no unresolved status,
free-text-only selector, wildcard, nearest-owner fallback or inferred donor.

### Derivation and event semantics

1. Bind B1c4/B1c6 identity/provenance first and retain exact 125/93/32 and
   16/100/9 closure. Compare B1c4 expected identity fields only to the
   unchanged base projection; validate the two new placement fields
   independently, never by an author-produced expected-asset table.
2. Parse exact image-reference ranges from immutable accepted pages and bind
   every marker to the binary digest/path. Preserve the existing 16 reviewed
   provenance spans, including their original ranges, hashes and logical
   ledger owner ids. Do not force those logical ids to equal content-addressed
   asset ids. Refine only additional required boundaries and conserve every
   original byte once.
3. Account for the 114 in-scope marker occurrences as 84 reader references
   and 30 retained/suppressed evidence references; the two page-1 evidence
   crops have no marker. The six advertising assets stay migration-only.
4. Produce exactly one asset event for each reader (93) and zero reader events
   for evidence-only assets. Marker-backed events bind the unique source
   marker; nine provisional events bind their PDF/document or physical slot
   without fabricated Markdown spans or binary digests. Canonical asset-event
   validation must handle this provenance union instead of the legacy
   nonempty-text-span rule.
5. Refine source events at every approved relative-placement boundary before
   resolving slot ids. Preserve xref source slices and the 16 B1c6 provenance
   spans. No same-page donor event, generated navigation item, or coarse
   containing fragment can substitute for the exact target.
6. Recompute the final ordered event stream from the frozen source/physical
   slot evidence. Asset array iteration order is not an ordering authority.
   Source-slot adjacency and ordinal rules eliminate before/after ambiguity
   and the current renderer's unsafe one-target-per-asset restriction.
7. Preserve the 30 evidence markers in source/audit coverage but emit no
   reader bytes for them. Do not add replaced child asset events, which would
   violate current B1c4 child-leakage closure.
8. Emit a reader asset reference once at its resolved slot. Future output
   manifests and the independent verifier bind the emitted occurrence/range
   to that event, source evidence and logical asset id. Do not retain the old
   Markdown link as a second emitted occurrence.

Builder and verifier implement separate derivation/validation paths. Neither
may import the author helper, use its placement object as the expected oracle,
or introduce a scenario-name bypass. For diagnostic tests, a pure in-memory
projection admission helper may be shared only with that validator's own
public path; builder and verifier must not share each other's oracle.

## Physical units, supplements and generated indexes

- Ground Floor & Basement: one unit, slots [106,107], then separately
  translatable Key A-V, all five legend labels and scale. Full-page facsimiles
  remain the visual handout; neither the key crop nor text substitutes for them.
- Pregens: six units, each front then back, followed by the separately
  translatable back semantics. Existing front ids remain unchanged; new back
  ids remain provisional. Character-specific responsibilities and actual blank
  template labels remain source-bound supplemental text, not raster edits.
- Generated indexes link to the unit/semantic owner anchors and do not own or
  duplicate asset occurrences. Their order is source/unit order, not an
  alphabetical or nearest-heading reassembly.
- Placement declarations may bind the already-reviewed obligations, but this
  slice must not author missing typed payload strings or source recoveries.
  Full physical-unit rendering stays closed until those later semantic
  obligations are independently proven.
- Step8A can later replace a binary under an accepted logical id, but cannot
  change page, owner, source slot, physical-unit membership or supplement
  relationship without reopening masters.

## Exact guarded no-write diagnostic and next seam

The diagnostic imported current modules with bytecode writes disabled, built
`author()` only in memory, and installed an audit hook rejecting write-mode
opens, mkdir/remove/rename/rmdir, copy and subprocess launch. No temp config,
candidate or render path was created. For the public-path depth check, only
the first config parse was replaced by the in-memory projection; subsequent
frozen-v1/evidence parsing remained real. This is a diagnostic projection, not
a claim that an on-disk v2 config passed.

After the real B1c6 provenance helper succeeded, its returned reader count was
changed to zero only in memory to look past the current unconditional
placement sentinel. No production function or file was edited. Both public
paths reached the same next concrete failure:

~~~text
builder:  ValueError: v2 migration decision evidence schema mismatch
verifier: ValueError: E_V2_MIGRATION: evidence-schema
~~~

The first offending evidence is `semantic_unit_review.json`: its actual
top-level keys are schema, reviewer, input_identities, decisions, while the
current migration catalog requires exactly schema and decisions. Its decision
rows also carry decision/reason/review_provenance, not only candidate_id.
This is the next bounded migration-evidence input-schema seam. Do not fix it
in B1c7 and do not rewrite immutable evidence to fit the stale parser.

A separate in-memory call to the current typed-chunk consumer returned
`ValueError: v2 asset event mismatch`, consistent with zero authored asset
events. No candidate build was invoked; its current mkdir/staging code remains
strictly out of scope.

The depth check establishes the next layer, not successful placement. After
event/slot closure is implemented, the same real binding path must still stop
at the migration pair above before any output boundary.

## Symmetric builder/verifier mutation matrix

All cases require independent builder and verifier rejection at the placement
layer before the later migration seam. An unmutated in-memory placement
projection must reach the exact migration pair, not an earlier masking error.

| Attack class | Required rejection/proof |
| --- | --- |
| missing reader placement, duplicate row/id, conflicting variants, two placements | exactly one closed reader variant; no last-row-wins or union-key fallback |
| evidence-only placement; reader null/empty placement | disposition/placement cardinality closure |
| nonexistent/foreign event or owner | exact target existence, hierarchy membership and source-bound ownership |
| same-page or same-kind donor placement | asset-specific marker/block/physical-slot binding, not count equality |
| before/after inversion represented by swapped slot neighbors | independently recomputed predecessor/successor equality |
| reordered slot ordinals or asset-array reorder | source order preserved; authored order cannot become oracle |
| cross-owner drift after restored headings | resolved owner interval and explicit cross-page/section boundary decision |
| generated TOC/handout/map/pregen target | navigation cannot serve as a source slot or physical owner |
| p123/124 placement, asset event or review/index leakage | exact advertising allowlist remains migration-only |
| map106/107 or pregen side treated as ordinary source crop | required physical-unit variant, page slot, side and replacement closure |
| swapped map pages/front-back sides or donor physical unit | unit/page/slot/id equality, front0/back1, exact one-to-one membership |
| missing translated supplement obligation | physical unit remains non-renderable; no facsimile-as-text substitution |
| Markdown marker moved away from its bound event | exact page/range/hash/path plus slot evidence; no donor span |
| bbox/raw_index/view/selected-block order changed | immutable comparison/decision binding and column-aware source order |
| p31/p32 city/boat owner Prologue or reversed order | OUT-005 city -> boat -> Prologue with Plots and Schemes owner |
| p78 Handout10 map after Handout11 | exact owner boundary rejects marker-at-page-end regression |
| two emitted links for one reader id, unplaced reader event, evidence link | one reader asset event and one final emitted occurrence/range |
| B1c4 identity/replacement/provenance mutation | existing identity/disposition/replacement gates remain intact |
| B1c5 review-row omission/page/order/id mutation | universal exact-list review coverage retained |
| B1c6 alias, marker, manifest, comparison, PDF recipe mutation | existing provenance binding remains independent and fail-closed |
| legacy fixture or frozen-v1 behavior drift | all scoped regressions and both frozen-v1 preflights preserve results |
| attempt to create canonical/temp/candidate/render output | audit-hook/target checks prove no-write stop before migration repair |

Required positive regressions include p3 logo-before-prose; p6 hero with
Summary crop suppressed; p7 platform logos suppressed; p11 column transition;
p25 portraits/body; p39->40 Morgue continuation; p31->32 city/boat; Appendix
58->60->65->68 ordering; p78 handout boundary; all seven physical units.

## Minimum next scope and acceptance criteria

Immediate engineering scope is **none**: do not dispatch a placement coder
against unresolved owners or treat this diagnostic companion as the oracle.

The minimum next bounded action is to freeze a placement decision ledger and
owner-resolution amendment, with compact existing-overlay/source checks only
for conflicting or insufficiently aligned rows. Resolve the five new owner
differences, the three absent owner anchors, the ten proven order conflicts,
the two top-art cross-view candidates, physical-unit namespace mappings, and
all exact event split boundaries. Already explicit user decisions should not
be asked again. Ask the user only if genuine semantic alternatives remain
after those immutable sources are reconciled.

After independent architecture approval, the implementation can remain scoped
to the six existing author/builder/verifier code/test files plus the approved
new ledger input and its immutable engineering receipt. No canonical config
or candidate is needed. If material hierarchy/typed-payload authoring is
required beyond the narrowly approved owner projection, stop and obtain a
separate packet rather than silently broadening B1c7.

Acceptance requires:

1. All 93 reader assets have one final, existing, source-bound owner and one
   closed placement; all 32 evidence-only assets have null placement.
2. The 79 source-slot / 14 physical-slot topology is independently recomputed,
   or a reviewed amendment explains any changed count. No guessed target or
   unresolved companion field enters author output.
3. All source bytes/markers are conserved in emitted or suppressed audit
   coverage; nine reviewed reader marker provenance spans and all seven
   evidence marker provenance spans remain B1c6-valid.
4. Exactly 93 reader asset events, no evidence reader events, unique final
   occurrences, and exact physical/page order are proved in memory.
5. The five owner-preservation conflicts and three missing owner anchors have
   a frozen contract resolution; the two existing OUT-005 rebounds stay closed.
6. All symmetric mutations reject independently; B1c4/B1c5/B1c6, 128 scoped
   regressions and both frozen-v1 preflights retain their intended behavior.
7. The unmutated placement projection advances to exactly the migration
   evidence-schema pair and stops without any config/candidate/render output.
8. A fresh independent GPT-5.5/high architecture review accepts the frozen
   amended specification before implementation. This receipt is not that review.

## Limits, residue and final findings

Direct image display of existing overlays was attempted but the local image
viewer returned Access denied. File metadata confirmed ordinary non-reparse
files. I did not copy/resize/rerender them to bypass the restriction. Therefore
this receipt claims code/data/source-order diagnosis, not fresh visual QA.
The existing accepted review declarations and comparison geometry are evidence;
the unresolved compact visual checks remain explicit.

Six pre-existing ignored roots were observed unchanged in scope and preserved:
`.v2-inputs-critic-path-probe`, `.v2-inputs-debug`, `.v2-inputs-debug2`,
`.v2-inputs-debug3`, `.v2-inputs-debug4`, `.v2-inputs-debug5`.
They are explicitly excluded from this task's no-output claim. Existing
protected candidate/scratch roots and four pre-existing
`.c2b-unittest.staging.*` roots were also left alone; no cleanup or
release-cleanliness assessment is authorized here.

- P0: none found in this bounded architecture inspection.
- P1: owner-preservation/target contradiction; demonstrable marker-vs-visual
  order conflicts; missing exact source-event/physical-unit placement graph.
  These prevent a truthful code-ready 93-placement approval.
- P2: pre-existing ignored/debug residue remains release-cleanliness debt.
  Direct visual display is an evidence limitation, not an excuse to guess.
- Next public seam: builder `v2 migration decision evidence schema mismatch`;
  verifier `E_V2_MIGRATION: evidence-schema`.
- Next action: orchestrator-owned bounded owner/placement decision closure,
  then fresh independent architecture review. No orchestration transfer.

CHANGES_REQUIRED_V2_COMPLETE_AUTHORING_PHASE_B1C7_ARCHITECTURE

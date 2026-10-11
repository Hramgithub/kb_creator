# Viral v2 complete publication authoring architecture receipt

## Receipt metadata

- Goal id: `20260830-kb-creator-next-scenario`.
- Step id: `7-v2-complete-publication-authoring-architecture`.
- Contributor role: `nri-architect`.
- Policy model / effort: `gpt-5.6-sol` / `high`.
- Actual platform model / effort: unavailable; the platform did not expose a
  separately verifiable runtime identity in this task.
- Orchestrator policy owner: main chat, `gpt-5.6-sol` / `medium`.
- Assignment state: `matched` to the repository role contract; platform runtime
  remains unverified.
- Scoped override: `none`.
- Scope: architecture/root-cause analysis and an implementation specification
  for complete Viral `publication_config_v2.json` authoring.
- Result: `complete`; no implementation or release decision is made here.
- Files checked: assigned task packet, canonical plan/context, NRI goal
  governance, blocked author helper, v2 builder/verifier and focused tests,
  frozen v1 config, accepted-v4 identities/pages, three approved ledgers,
  independent approval receipt, user-review registry and candidate-first
  review/closure evidence.
- Files changed: only this receipt.
- Verification/evidence: independent read-only SHA/count inspection, raw
  reader-page byte/line/EOL measurement, v1 domain/asset counts and scoped
  receipt `git diff --check`.
- Forbidden paths changed: none. Code, tests, configs, evidence, immutable
  reconstruction/source inputs, candidates and Git were read-only.
- Timestamp: `2026-09-03` (Europe/Moscow).
- Elapsed time: approximately 35 minutes.
- Token use: unavailable.

## Executive decision

The current `author_viral_master_en_v2_config.py` must remain fail-closed and
must not write `publication_config_v2.json`. It treats three approved boundary
ledgers as if they were the complete reader source, although they cover only
`1,905 / 4,860` source line slots (`39.2%`). It also drops the frozen v1
publication baseline, turns all 16 ledger `asset_ownership` units into
`reader_value:false`, and invents equipment/statblock strings.

The ledgers are reviewed overlays. The complete author must start from the
frozen v1 publication baseline and the exact accepted reconstruction, apply
reviewed overlays at higher precedence, and fill every untouched source gap as
retained ordinary source. It must emit two independent conservation proofs:

1. a reconstruction-bound, byte-exhaustive source partition for pages 1--122;
2. the existing final-output event ledger for the serialized `MASTER_EN.md`.

Config-content hashes alone are not source evidence. The current builder
`_v2_declared_hash()` and verifier `v2_declared_hash()` independently hash the
same config `content`; both can therefore agree on invented text. The new
contract binds every source-derived event and every authorial typed-payload leaf
to exact bytes in the accepted reconstruction, or to one separately sealed
source recovery.

The terminal completion token is recorded once at the end of this receipt.

## Evidence and measured baseline

### Immutable identities

- Frozen working v1 config:
  `kb_creator/working/viral/master_en/publication_config_v1.json`, SHA-256
  `C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30`.
- Accepted reconstruction root:
  `kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4`.
- Reconstruction aggregate identity: `377` files, `41,079,424` bytes, SHA-256
  `68C17FB765A89C6146398868E61F1F6EB7B2FE4EAFBA8C2C2C8F42260BBDBA83`
  under the declared ordinal-path inventory algorithm. The package deliberately
  has no physical root `INVENTORY.json`; validation must recompute this
  aggregate and must not mutate v4.
- Approved boundary ledgers:
  - pages 001--040:
    `8C0A666D962C879C62B7168B60AB717EA04F833FFE728446F150F64FCB24DDAF`;
  - pages 041--068:
    `8673868ED762E327517891D7C72DBA21A5C88F1A4173EBB0EFF597D30453EF13`;
  - pages 069--122:
    `14338236CDB2AAE6213CCE5F36DA93C661F2DF35D9F7E96F8346C770BF00CFD1`.
- Independent boundary-ledger approval receipt:
  `4992A0CC7BA402F999177988241A3D679A7E7B437AD1F9FD8AB0663783547FE3`.
- User-review registry:
  `D20414D48405A761ADD31E538B6940F8A3E0F1FB11044AF73EAD122D96C616E8`.
- Candidate-first review:
  - candidates `F0B7E1B6AE33EC1442AD18FD2FF81D18C81B7F42F59C7A9B0FD6B9DE394B0B49`;
  - review `41E3F6F7AAC5970D9FCFC032926B0F5FB48E41D544414130AED85AB8672EAB78`;
  - closure `3AB47BE01FED57773A3DD3419D0CF0D2DF4658A56E813FF3B02BD5E4C8B99ACA`.

### Reader-source measurements

Direct measurement of immutable `page-001.md` through `page-122.md` produced:

- `122` reader pages;
- `346,793` raw UTF-8 bytes;
- `4,860` `splitlines()` source line slots;
- `2,040` nonblank line slots;
- `1,229` `CRCRLF` sequences across `40` pages.

The EOL anomaly is accepted immutable v4 evidence, not permission to ignore
bytes. The source partition operates over raw bytes and therefore accounts for
every `CR`, `LF` and blank line. Output serialization may normalize layout only
through a declared presentation operation; it must never pretend the source
was already LF-clean.

### Frozen v1 publication baseline

The frozen v1 config contains:

- `168` hierarchy rows;
- `123` assets: `107` reader and `16` evidence-only;
- `237` xrefs;
- `124` source-disposition rows;
- `41` handout rows;
- `29` structured-content rows.

The correct asset rule is not “carry all 107 reader assets” and not “suppress
all ledger assets”. It is `v1 baseline minus exact reviewed decisions`:
untouched assets inherit their complete v1 identity and reader/evidence policy;
suppression, reclassification, replacement, merge or relocation requires an
explicit decision reference. Examples already requiring such decisions include
the Summary heading crop, isolated platform logos/promotional badge, physical
map/pregen composition and pages 123--124. No v1 asset may silently disappear.

## Root-cause trace

1. The reviewed semantic audit closed 429 candidate decisions, then the three
   boundary ledgers coalesced those candidate rows into 186 reviewed units.
   Neither artifact claims to partition ordinary prose or every source line.
2. The blocked helper iterates only those 186 units. It never emits events for
   gaps, so approximately 60.8% of page-line slots have no publication event.
3. The helper does not consume the frozen v1 config. Its hierarchy, handouts,
   xrefs, structured expectations, reader/evidence asset policy and accepted
   placements therefore cannot survive by construction.
4. `asset_ownership` ledger rows are positional ownership evidence, not asset
   publication dispositions. Converting all of them to `reader_value:false`
   conflates two independent decisions.
5. The current event closed schema records `fragment_id`, config `content` and
   a hash of that same content, but no reconstruction path/range/hash. Builder
   and verifier can independently validate an identical invented value.
6. Table fallback and equipment/statblock serializers insert literal editorial
   placeholders (`Source-backed ...`, `See source-backed entry.`). A placeholder
   scan detects these examples but cannot prove general lexical fidelity.
7. v2 hierarchy currently drops parent, level, TOC and semantic-role data, and
   renders every heading at one fixed level. It cannot prove full v1 hierarchy
   migration or heading-level fidelity.
8. v2 evidence-only assets currently retain only five control fields, while
   reader assets retain binary identity. That loses the identity/provenance of
   v1 evidence assets and makes a 123-row migration audit impossible.

## Canonical complete-data model

The v2 config remains one closed JSON contract but gains two authoritative
sections: `migration` and `source_partition`. Existing final sections remain
materialized projections, not substitutes for those proofs.

### Input bindings

`migration.inputs` must bind exact repository-relative identities for:

- frozen v1 config;
- accepted reconstruction aggregate root/count/bytes/algorithm/SHA;
- every page identity for 1--124;
- three boundary ledgers;
- independent approval receipt;
- registry, semantic decisions and closure report;
- source PDF identity.

Builder and verifier independently resolve safe paths, reject symlinks/reparse
points, recompute identities and compare CLI paths. A config cannot point at an
equivalent-looking substitute. Mutating any bound input invalidates authoring,
preflight and verification.

### Raw source pages and partition spans

`source_partition.pages` contains exactly pages 1--122 in ordinal order. Each
row has the following closed fields:

```text
page, path, bytes, sha256, encoding, eol_profile, span_ids
```

Requirements:

- `encoding` is exactly `utf-8-no-bom`;
- `bytes` and `sha256` bind the raw file, without universal-newline rewriting;
- `eol_profile` records raw `lf`, `crlf`, `crcrlf` and lone-CR counts as audit
  information; it cannot alter coordinates;
- `span_ids` are in strictly increasing raw-byte order.

`source_partition.spans` contains closed rows:

```text
span_id
page
source_path
start_byte
end_byte
start_char
end_char
raw_sha256
raw_text_sha256
classification
owner_kind
owner_id
decision_ref
```

Coordinates are zero-based half-open. `start_byte/end_byte` are authoritative
raw UTF-8 coordinates. Character coordinates are calculated on the exact
decoded prefix and are checked independently. `raw_sha256` hashes the exact raw
bytes. `raw_text_sha256` hashes the exact decoded substring and exists only to
make Unicode checks explicit; it is not a replacement for the raw hash.

Allowed `classification` values are:

- `retained_heading`;
- `retained_text`;
- `reviewed_structured_source`;
- `asset_reference_source`;
- `generated_navigation_source`;
- `authorized_suppression`;
- `technical_marker_suppression`;
- `layout_separator`.

Allowed `owner_kind` values are `event`, `asset`, `generated_navigation`,
`suppression`. Every span has exactly one owner. A source recovery is not a page
partition owner because it inserts externally recovered source evidence; it has
its own sealed contract below.

For every page, sorted spans must satisfy:

```text
first.start_byte == 0
span[n].end_byte == span[n+1].start_byte
last.end_byte == page.bytes
SHA256(concat(raw span bytes)) == page.sha256
```

Thus gaps, overlaps and duplicate claims are impossible. Zero-length spans are
forbidden. Blank lines, EOL bytes, source-page comments and other technical
layout bytes are claimed explicitly; “ignore blank lines” is forbidden.
`layout_separator` and `technical_marker_suppression` may produce no reader
text, but remain byte-accounted with a reason/decision.

### Event source bindings

Every event gains closed source provenance:

```text
source_span_ids
source_operation
payload_bindings
```

- `source_span_ids` is nonempty for `heading`, `text_fragment`,
  `structured_unit` and source image `asset` events.
- `source_operation` is one of `emit_exact`, `semantic_restructure`,
  `asset_reference`, `generated_navigation`, `source_recovery`,
  `emit_anchor_only`, `suppress`.
- Every referenced span names the same event/asset as owner. A span cannot be
  referenced by two events.
- `order_key` is derived, never accepted as free author input:
  `[first_source_page, first_start_byte, event_role_rank, stable_ordinal]`.
- A multi-span unit must have strictly increasing source spans. It may coalesce
  page/column continuations only when all intervening nonblank partition spans
  belong to the same logical unit or are its declared continuation heading and
  layout separators. Otherwise it is split into ordered child events under one
  structure id.
- Generated navigation derives its order from its exact source TOC span.
- A source-recovery event uses an exact relative insertion operation
  (`before_event` or `after_event`) rather than an invented page/order key.

`contains` may remain as a presentation containment list, but it must contain
real partition `span_id` values or child event ids and is checked against the
reconstruction. Free labels such as `p003-l001-l002` are not source proof.

### Authorial payload bindings

Every authorial string leaf in an event payload must be covered exactly once by
`payload_bindings`. A binding has:

```text
json_pointer
source_slices
joiner
recovery_id
```

Exactly one of `source_slices` and `recovery_id` is present. Each source slice
names an event-owned partition span plus an exact subrange within that span.
The decoded slice values joined with one closed `joiner` (`""`, `" "`, or
`"\n"`) must equal the payload leaf exactly. Selecting the title characters
inside a Markdown heading or the cell characters inside a pipe row is allowed;
inventing a cleaned paraphrase is not. Markdown emphasis may be retained by
including its exact characters in the slice.

Structural enums, ids, counts and serializer-owned punctuation are not
authorial leaves. Kind-specific validators enumerate the complete set of
authorial JSON pointers, so an unbound new string field fails closed. This is
the primary no-invention proof. A regex ban for the current literals
`Source-backed`, `See source-backed entry.` and `Translatable source key`
remains as a focused regression only.

### Sealed source recoveries and title transformations

Each recovery contains:

```text
recovery_id, source_pdf_identity, physical_page, extraction_method,
source_text, source_text_sha256, evidence_identity, target_event_id,
placement, decision_ref
```

The verifier independently revalidates the evidence identity and text hash.
Any hierarchy row with `source_title != reader_title` must point either to
source slices proving the title or to one recovery id. `reviewed_title_transformation`
is closed and includes the decision reference and exact operation. An unsealed
literal, including a plausible recovered title, is rejected.

### Full hierarchy

The final v2 hierarchy row must preserve or explicitly replace these v1
semantics:

```text
anchor, parent_anchor, level, toc_entry, semantic_role, source_pages,
source_title, reader_title, representation, reviewed_title_transformation,
migration_row_id
```

For `representation: heading`, level is 1--6 and the builder emits that exact
level. `anchor_only` and `inline_run_in` do not emit outline headings but retain
parent/semantic ownership. A retained v1 row cannot change parent, level,
title, TOC status or semantic role. A reviewed overlay may reclassify a false
heading to run-in/anchor-only, restore a lost heading, or split/merge ownership,
but only through its migration row and decision reference. Pages 123--124 have
no reader hierarchy nodes.

### Typed publication payloads

The following are required source-preserving schemas. The exact field list is
closed in both builder and verifier; all authorial leaves obey payload binding.

- `callout`: exact label/title where present, ordered body paragraphs, exact
  bounded source spans and termination.
- `ordered_list_callout`: ordered item payloads; item count and order match
  source bindings.
- `table`: exact header cells and ordered row cells, declared row/cell counts,
  continuation metadata, attached notes and source bindings per cell. No
  fallback row may be invented.
- `equipment_card`: exact title, stat line(s), footnote and body fields. Missing
  optional source content is represented as an absent field, never placeholder
  prose.
- `creature_statblock`: exact title/subtitle, ordered stat rows, attacks,
  abilities and nested tables as present in source. A source-absent category is
  absent, not `See source-backed entry.`.
- `inline_run_in`: exact label and exact body/xref text, with anchor but no
  outline heading.
- `full_page_map`: exact ordered page set, reader asset ids, exact accessible
  key/legend/scale text and map ownership. “Full-page provisional map” is not
  authorial content.
- `physical_page_pair`: exact front/back page ids, exact front/back reader asset
  ids and source-bound accessible back semantics. `front_facsimile` and
  `back_facsimile` are asset references, not copied paragraph strings.

Full-page map and pregen binary selection remains provisional Step 7 work;
Step 8A may replace binary quality but cannot change logical id, role, owner,
source page set, pair membership or placement.

## Migration contract

`migration` contains six exhaustive ledgers plus input identities:

```text
hierarchy_rows
asset_rows
xref_rows
structured_rows
handout_rows
source_disposition_rows
```

Each row binds the canonical SHA-256 of the complete v1 source row, one outcome,
zero or more final target ids and an optional mandatory decision reference.
Allowed outcomes are domain-specific subsets of:

- `retained_unchanged`;
- `retained_rebound`;
- `reclassified`;
- `replaced`;
- `split`;
- `merged`;
- `suppressed_reviewed`;
- `excluded_advertising`.

Every v1 row occurs exactly once in the applicable migration ledger. Every
final target occurs in at least one migration row or is declared `new_reviewed`
with an exact decision reference. `retained_unchanged` cannot cite a decision
and must preserve the domain's immutable fields. Every other outcome requires
one decision in the bound registry/ledger/review evidence.

### Precedence

Highest precedence wins only when identities and decision references agree:

1. user-approved source scope: pages 123--124 are audit-only
   `excluded_advertising`;
2. explicit user dispositions in the registry;
3. the independently approved boundary-ledger ownership/boundary decision;
4. frozen v1 publication semantics for untouched objects;
5. exact accepted reconstruction bytes for ordinary uncovered source gaps.

Candidate-first review rows prove breadth, not final boundaries. They cannot
override an approved boundary ledger. A conflict between two higher-priority
sources is a hard stop, not “last writer wins”.

### Hierarchy migration

Start with all 168 v1 rows. Remove only rows whose source pages are excluded or
whose exact reviewed disposition replaces/reclassifies them. Overlay the
approved heading/run-in ownership. Fill title/level/parent/toc/semantic fields
from v1 for untouched anchors. New/restored anchors require source title slices
or sealed recovery. Verify that every final heading has one heading event and
every heading event has one hierarchy row. No parent heading may be emitted
hundreds of events before its first descendant; it is placed immediately before
the first source-ordered descendant/content event.

### Asset migration

The asset ledger contains exactly 123 rows for the 123 frozen-v1 asset ids,
plus separately identified `new_reviewed` page-render assets when required.
For each frozen asset:

- preserve source path, SHA-256, bytes, media type, dimensions, logical name,
  source page/region, semantic role, alt text and reader/evidence status unless
  an explicit decision changes them;
- map source Markdown image-reference spans to the asset id;
- derive event-relative placement from exact source order (`before_event`,
  `after_event`, `inside_structured_unit`); owner-end fallback is forbidden;
- preserve evidence-only asset identity in the v2 manifest even when the
  binary is not copied into reader `assets/`;
- require `replaces` closure when a reviewed full-page render replaces one or
  more child crops; each old id has exactly one final disposition;
- mark page-123/page-124 assets `excluded_advertising`, with no reader event,
  copy, visual-review row or downstream candidate;
- keep Summary crop and isolated platform/promotional assets evidence-only per
  exact registry decisions; never infer all logos are suppressed, because the
  scenario-identity Spektral Krew logo has a distinct reviewed role.

The asset conservation equation is:

```text
123 input rows
= retained_reader
 + retained_evidence
 + reclassified_evidence
 + replaced
 + suppressed_reviewed
 + excluded_advertising
```

The categories are mutually exclusive. Final reader count is derived from the
resolved ledger; it is not hard-coded to 107. Zero silent drops, duplicate
logical reader representations and excluded-page reader assets are required.

### Xref and navigation migration

Start with all 237 v1 xrefs. Every row is retained, rebound through an explicit
anchor alias, replaced by generated navigation, or excluded by the page-123/124
scope. Generated TOC entries are derived from final `toc_entry:true` hierarchy
rows and bind to exact source TOC spans. Source xrefs bind visible text to an
event source subrange. Rebinding a target requires a migration row; missing,
duplicate and orphan targets fail. The final verifier recomputes all emitted
links and anchor closure from candidate bytes.

### Structured content, handouts and source disposition

- Start with all 29 v1 structured rows. Approved typed ledgers replace their
  boundaries/representation where applicable; untouched structures retain
  their fact expectations. Every final structured event maps to one v1 row or
  one `new_reviewed` ledger unit.
- Start with all 41 v1 handouts. Preserve physical ids/order/source pages and
  owned assets unless a reviewed map/pregen pair replaces representation.
  Physical map/pregen pages remain full units with accessible semantics.
- Preserve exactly 124 source-disposition identities. Pages 1--122 are reader;
  pages 123--124 are exact `excluded_advertising` audit rows and have no target
  anchors/subunits/assets. The reader source partition covers only 1--122.

## Deterministic authoring algorithm

1. Refuse to run if output exists. Load no writable candidate root.
2. Verify the SHA/bytes of frozen v1, registry, semantic review/closure,
   boundary ledgers, approval receipt, source PDF and all reconstruction
   identities. Recompute the aggregate v4 inventory; do not look for or create
   root `INVENTORY.json`.
3. Read pages 1--124 as raw bytes. Validate UTF-8/no BOM and record, but do not
   normalize, EOL profile. Bind all 124 page identities.
4. Convert approved ledger 1-based line segments to exact raw byte/character
   ranges while preserving line terminators. Recheck endpoint text and the
   existing LF-line hashes, then seal raw byte hashes.
5. Materialize exhaustive v1 migration ledgers. Apply precedence in the order
   above and stop on conflicts, missing rows or unreferenced final targets.
6. On pages 1--122, reserve exact reviewed structured spans, asset-reference
   spans, source TOC replacement spans and reviewed/technical suppressions.
7. Partition every remaining byte. Markdown heading lines become retained
   heading events only when reconciled with the migrated hierarchy. Image-link
   lines become asset-reference spans. Remaining authorial blocks become
   retained text events. Blank/EOL/source-marker bytes become explicit
   layout/technical spans. No catch-all suppression is allowed.
8. Build typed payloads from exact source slices. Generate payload bindings for
   every authorial leaf and reject any unbound leaf, unused claimed source slice
   or placeholder fallback.
9. Derive event order from first source byte. Validate logical continuation
   groups, hierarchy adjacency, exact relative asset placement and xref source
   ownership.
10. Independently run all source partition, migration, lexical-binding,
    hierarchy/xref/asset and scope invariants in the author before serialization.
11. Serialize canonical UTF-8/LF JSON to a temporary sibling file, fsync/close,
    reread and validate, then atomically rename only if destination is still
    absent. On any failure, remove only the helper's temporary file and leave no
    config.
12. A second run into a distinct absent temp target must produce byte-identical
    JSON. Candidate construction remains unauthorized until engineering review
    accepts the implementation and config.

The present 39.2%-coverage helper must fail before step 11 with a stable error
such as `E_V2_AUTHOR_INCOMPLETE_SOURCE_PARTITION`; it must not emit a partial
config for inspection.

## Independent validation invariants

Builder preflight and the independent verifier each implement, without
importing one another, all of the following:

- accepted reconstruction aggregate identity exactly matches v4;
- frozen v1 and all decision inputs match bound identities;
- pages 1--122 source partition totals exactly `122` pages, `346,793` raw
  bytes and `4,860` line slots for this frozen input;
- per-page first/adjacent/final range equations pass;
- zero unclaimed bytes, overlap bytes, duplicate owners and out-of-range spans;
- all `2,040` nonblank source line slots have an authorial/asset/navigation/
  reviewed-suppression owner;
- all blank/EOL/technical bytes have an explicit layout/suppression owner;
- event order is strict and derived from source ranges;
- every source-derived event references real reconstruction spans;
- every authorial payload leaf is source-slice or recovery bound;
- zero invented authorial strings and zero unused placeholder fallback;
- hierarchy parent/level/title/TOC/representation migration is closed;
- every active xref resolves and every migration source row is accounted once;
- asset migration contains exactly 123 unique v1 ids and no implicit outcome;
- retained reader assets have exact binary identity and exact event placement;
- evidence/suppressed/excluded assets emit no reader marker;
- pages 123--124 have zero hierarchy, event, xref, handout, asset-copy and
  visual-review leakage;
- output event ledger still proves exact emitted candidate ranges/hashes;
- source partition proof and output ledger proof are both present in
  provenance and bind the same config/source identities.

## Required test matrix

### Config author tests

Positive fixtures:

- complete miniature page byte partition with heading, ordinary prose, blank
  separators, structured replacement, image link, generated TOC replacement
  and reviewed suppression;
- full frozen Viral authoring metrics: `4,860/4,860` line slots and
  `346,793/346,793` raw bytes claimed;
- all 168/123/237/124/41/29 v1 baseline rows receive one migration outcome;
- two absent output targets produce identical bytes;
- payload bindings for every supported typed kind.

Negative fixtures:

- one unclaimed nonblank source line;
- one unclaimed blank line, CR or LF byte;
- one duplicated/overlapping source span;
- one reordered page/column event;
- changed source bytes with config hashes resealed;
- structured payload leaf altered/resealed but not source-derived;
- unbound new authorial payload field;
- each current placeholder fallback literal;
- table row/cell missing, duplicated or reordered;
- equipment stat/footnote or creature field omitted/invented;
- missing, duplicated or unreferenced v1 migration row in every domain;
- heading lost/downgraded/reparented without exact decision;
- inset label promoted to outline heading;
- wrong source recovery or unsealed title transformation;
- missing/rebound xref without migration evidence;
- one missing v1 reader asset, evidence promotion, duplicate asset, wrong
  relative placement, or source identity drift;
- p123/p124 text or asset leakage;
- mutation of v1/reconstruction/ledger/review identity;
- current ledgers-only helper attempts to write at 39.2% coverage.

Every failing author test asserts destination absence.

### Builder tests

- expanded closed v2 schema accepts only reconstruction-bound partitions and
  migration ledgers;
- exact heading levels/parents and anchor-only/run-in behavior;
- ordinary retained prose before, between and after every reviewed overlay;
- typed payload serializers use only validated leaves;
- before/after/inside asset placement including city -> boat -> Prologue;
- evidence/suppressed assets are absent from `MASTER_EN.md`;
- map and all six pregen pairs have complete physical membership;
- generated navigation replaces only its claimed source spans;
- atomic candidate build and deterministic inventory;
- all existing v1 tests remain green.

### Independent verifier tests

Each mutation is applied to a builder-produced candidate/config and all
candidate sidecars are resealed, so rejection cannot rely on a stale hash:

- every source partition mutation above;
- config content and payload bindings changed together to an invented value;
- output event ledger valid while source partition is invalid, and the reverse;
- ordinary prose deletion with otherwise valid structured units;
- heading level/title/parent/outline pollution;
- xref target or visible source text drift;
- reader asset deletion/duplication/relocation/binary drift;
- evidence-only marker insertion;
- excluded advertising asset/text injection;
- wrong recovery evidence;
- output provenance points at a different v1/ledger/reconstruction identity.

The verifier independently rereads reconstruction bytes and v1 config. It must
not trust builder-generated source summaries and must not import builder or
author helpers.

## Minimal implementation ownership

Only these paths are required for the implementation that follows this
receipt:

- `kb_creator/scripts/author_viral_master_en_v2_config.py`;
- `kb_creator/tests/test_author_viral_master_en_v2_config.py`;
- `kb_creator/scripts/build_scenario_master_en.py`;
- `kb_creator/tests/test_build_scenario_master_en.py`;
- `kb_creator/scripts/verify_scenario_master_en.py`;
- `kb_creator/tests/test_verify_scenario_master_en.py`;
- `kb_creator/working/viral/master_en/publication_config_v2.json` only after
  all author/schema tests are green;
- the implementer's immutable handoff receipt.

No change is required or allowed to frozen v1 configs, accepted v4, the three
approved ledgers, candidate-first evidence, Candidate C, retained scratch roots,
source PDF, Step 8A or production outputs. Visual-QA code is already outside
this correction unless a later verified schema incompatibility receives a new
bounded assignment.

## Sequencing and gates

1. Keep the present helper fail-closed; do not run it against the production
   output path.
2. First seal the already selected v2 aggregate reconstruction-identity route
   with builder/verifier parity tests. It recomputes the v4 inventory and never
   requires a physical v4 `INVENTORY.json`.
3. Implement source-partition and migration closed schemas in builder and
   independent verifier, plus synthetic negative tests. Preserve the v1 route.
4. Implement the complete author and author-specific tests against those
   schemas. No real config yet.
5. Run all focused builder/verifier/author tests and both frozen-v1 preflights.
6. Author production v2 twice into distinct absent temporary paths; compare
   bytes; only then atomically materialize the single absent canonical config.
7. Run builder and independent-verifier preflight against the real config.
8. Dispatch a fresh independent `gpt-5.5` implementation review. Any P0/P1 or
   material schema mutation returns to engineering.
9. Only after review acceptance may Luna/medium build the two retained scratch
   candidates. Candidate D, visual QA, critic review and user reading acceptance
   remain later separate gates.

## Acceptance criteria for the implementation handoff

Implementation may return ready only when:

1. frozen inputs retain every identity recorded above;
2. author output is impossible with less than 100% raw-byte partition closure;
3. ordinary prose/headings/assets from untouched v1/reconstruction survive;
4. all reviewed overlays replace only their exact claimed spans;
5. all v1 baseline domains have exhaustive, nonduplicated migration rows;
6. all typed authorial content is source-slice/recovery bound, with zero
   placeholders or unbound leaf strings;
7. final asset reader count is derived from 123 closed migration outcomes,
   with no silent drop and no pages 123--124 leakage;
8. builder and verifier independently revalidate reconstruction/v1/source
   conservation and candidate output;
9. author, builder and verifier negative matrices pass, plus the existing 86
   focused baseline tests and both v1 preflights;
10. no real candidate has been created and Git has not been mutated.

## Risks and controls

- **Large config:** exhaustive byte/source/migration evidence enlarges JSON.
  This is intentional production evidence; deterministic ids and canonical
  serialization keep it reviewable. Do not compress away source identities.
- **EOL corruption mistaken for gaps:** raw byte coordinates bind CRCRLF while
  payload slices exclude/layout-account separators. Universal newline reading
  is forbidden for coordinate generation.
- **Overlapping reviewed units:** partition reservation detects overlap before
  gap filling. No ledger unit wins silently.
- **V1 defects carried forward:** explicit registry/ledger decisions override
  only exact rows/spans; every changed v1 row has a decision reference.
- **Asset over-retention:** baseline inheritance is constrained by explicit
  platform/logo/duplicate/excluded-page decisions and physical-unit
  replacement closure.
- **Asset over-suppression:** ownership evidence never implies
  `reader_value:false`; scenario-identity art remains possible.
- **Circular proof:** author, builder and verifier separately reread frozen
  inputs; config-content hashes and candidate sidecars cannot establish source
  truth alone.
- **Recovery invention:** recovered text cannot enter payload without sealed
  PDF/evidence identity and exact placement.

## Blockers and next action

Architecture blockers: none.

Next action: the orchestrator assigns one bounded Terra/medium implementation
packet following the sequencing and path ownership above. Candidate execution
stays closed until a complete config, focused tests, real preflights and fresh
independent implementation review are integrated.

`READY_FOR_V2_COMPLETE_PUBLICATION_AUTHORING_IMPLEMENTATION`

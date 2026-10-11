# Task packet — Viral v2 complete authoring Phase A3 provenance/payload/hierarchy

## Start condition and role

- Do not dispatch until Phase A2 migration engineering has an independent
  GPT-5.5/high implementation approval bound here by receipt SHA-256.
- Role: `nri-engineer` / GPT-5.6-terra / medium.
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`.
- You are not alone in the worktree; preserve unrelated/user edits and adapt
  only to approved A1b/A2 bytes.
- Own only the two MASTER_EN scripts, their two focused test modules, and one
  immutable Phase A3 engineering receipt. Do not edit helper/config, immutable
  inputs/evidence, visual QA, candidates, plan/context, Git, MASTER_RU, Step 8A,
  HTML/PDF or production output.

## Bound specification

- Architecture receipt SHA-256:
  `39F9B514F82ABAAD58D0A637E07C395206E57BED7106864EC0247A9477E24ADC`.
- A1b independent approval SHA-256:
  `0D99E9B4F9B70F93D66118C555D2C2ED0077587360DD2A3027B532CD3FBAA23C`.
- A2 final provenance-collision remediation receipt SHA-256:
  `BB1B822DFE3712E3F452B2F34153F38CCD01461732411007AE5CA3112080829E`.
- A2 full mutation-matrix closure receipt SHA-256:
  `77247ACFE2F66BF6791103245EBF43EFBF35577C07BF192D86B28C42BE1B1123`.
- A2 independent approval receipt SHA-256:
  `F1F0877A90A2B66453C024B2C63BEADD85049FA97A29663F6DA12E96F66AF996`.
- Approved A2 production hashes: builder
  `76DDF943D84B23A60578189F2E1C808D4606AD67028FFCCE76E0DD50418C4E3F`,
  verifier
  `938A6D3635E2078D20D09A32F9792808915E23CE909D1C7BDDD81ACB08B36CFE`.
- Approved A2 focused-test hashes: builder
  `F117173CD23F95E0BEE86D45813F2E2418EC7147B80C8C8E31C4F4ADE94D5D35`,
  verifier
  `94D5CC6D27D0B93EFCB58058C8B1FF8F37FA579AADD95C4ABC7CB83491FEBD51`.

## Required implementation

Implement the remaining closed v2 authoring contract independently in builder
and verifier. The verifier must not import builder helpers.

### Event source provenance and order

Every event has closed `source_span_ids`, `source_operation`, and
`payload_bindings` fields. Require nonempty owned spans for source headings,
ordinary text, typed structures and source-image asset events. Allowed source
operations are only `emit_exact`, `semantic_restructure`, `asset_reference`,
`generated_navigation`, `source_recovery`, `emit_anchor_only`, and `suppress`.
Each span must name the event/asset as owner and may not feed two events.

Derive order from `[first_source_page, first_start_byte, event_role_rank,
stable_ordinal]`; never trust a free config order key. Multi-span events must be
strictly increasing and may cross continuation/layout spans only under the
architecture's same-logical-unit rule. Recovery events use a sealed
`before_event`/`after_event` placement. `contains` may contain only real span ids
or real child-event ids and must close exactly.

### Authorial payload bindings

For every authorial string leaf, require exactly one binding with closed fields
`json_pointer`, `source_slices`, `joiner`, `recovery_id`. Exactly one of slices
or recovery is present. A source slice names an event-owned span plus exact
decoded subrange. Only joiners `""`, `" "`, and `"\n"` are allowed; recomputed
text must equal the payload leaf byte-for-character. Enumerate the exact
authorial JSON pointers for each event/typed kind so an extra/unbound string
field fails. Structural enums/ids/counts and serializer punctuation are not
authorial leaves. Keep focused bans on current placeholder literals but rely on
bindings as the primary no-invention proof.

### Recoveries and title transformations

Use the closed recovery schema from the architecture:
`recovery_id`, `source_pdf_identity`, `physical_page`, `extraction_method`,
`source_text`, `source_text_sha256`, `evidence_identity`, `target_event_id`,
`placement`, `decision_ref`. Independently bind evidence and text hashes. Any
source/reader title difference must be proved by exact source slices or one
sealed recovery plus closed `reviewed_title_transformation` and decision ref.
Reject plausible but unsealed literals.

### Full hierarchy

Require exact closed fields `anchor`, `parent_anchor`, `level`, `toc_entry`,
`semantic_role`, `source_pages`, `source_title`, `reader_title`,
`representation`, `reviewed_title_transformation`, `migration_row_id`.
Representations are closed: `heading`, `anchor_only`, `inline_run_in`.
`heading` uses exact level 1..6; other forms emit no outline heading. Validate
parent closure, acyclicity, source pages, migration-row closure, pages 123/124
exclusion, heading-event one-to-one correspondence and retained immutable v1
semantics. Place parents immediately before their first source-ordered
descendant/content event, not at arbitrary document positions.

### Closed typed payloads

Implement exact source-bound closed schemas and serializers for:

- callout and ordered-list callout;
- tables with header, ordered rows/cells, counts, continuations and notes;
- equipment cards;
- creature statblocks including nested tables where present;
- inline run-ins;
- full-page maps;
- front/back physical-page pairs.

Missing optional source content is absent, never placeholder prose. Every cell,
label, stat, footnote, paragraph and accessible map/back semantic string is
payload-bound. Asset references are identities, not copied authorial prose.
Step 8A may later change binary choice only; it cannot change logical identity,
role, owner, page set, pair membership or placement.

### Assets, xrefs and source partition closure

Bind asset image-reference spans and exact placement (`before_event`,
`after_event`, `inside_structured_unit`) to real event boundaries. Evidence,
suppressed and excluded assets emit no reader marker. Every source xref binds
visible text to exact event source slices; rebound/generated navigation closes
through the approved migration row and existing decision ref. Every partition
span owner closes to one event, asset, generated-navigation item or suppression;
no dangling owner is allowed.

## Tests

Add positive miniature fixtures covering ordinary prose before/between/after
overlays and every typed kind. Add deterministic negative tests for:

- missing/duplicate/reordered/cross-owner event spans and free order keys;
- gap/intervening foreign content in a multi-span event;
- unbound/duplicate/altered payload leaves, illegal joiner/range/pointer,
  extra authorial field and source slice from another owner;
- every currently known placeholder literal;
- table row/cell omission, duplication, reorder and count drift;
- equipment stat/footnote and creature field omission/invention;
- unsealed recovery/evidence/text/title transformation;
- hierarchy lost/downgraded/reparented/retitled without migration decision,
  cycle/orphan, false inset promoted to heading, heading/event mismatch;
- incorrect inline run-in/anchor-only outline emission;
- xref visible-text/target/migration drift;
- asset source span/placement/reader policy drift and p123/p124 leakage;
- dangling partition owner or unreferenced event/child/span.

Every failed builder test asserts destination absence. Keep all v1, A1b, A2,
py-compile, four-module baseline and both real-v1 preflights green. Do not create
real v2 config, candidate, accepted-v4 input inventory or leftover scratch.

## Handoff

Write only
`kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_v2_complete_authoring_phase_a3_20260903.md`.
Record all bound/final hashes, exact tests/preflights, negative coverage,
forbidden-output checks and blockers. Terminal line:

- `READY_FOR_V2_COMPLETE_AUTHORING_PHASE_B` only if A3 is complete; otherwise
- `PARTIAL_V2_COMPLETE_AUTHORING_PHASE_A3` with exact remaining scope.

This remains engineering evidence. The real author helper/config/candidate and
release stay closed pending independent A3 review and orchestration.

# Task packet — Viral v2 B1c7 reader-asset placement architecture

## Role and boundary

- Owner: `gpt-5.6-sol` architecture/root-cause role at high reasoning.
- Architecture and read-only diagnosis only; do not edit code/tests/config.
- Write one immutable architecture receipt in this handoff directory.
- Orchestration ownership remains with main chat (`gpt-5.6-sol` / medium).
- No canonical v2 config or candidate exists; all output phases remain closed.

## Approved prerequisites

- B1c6 architecture approval receipt SHA-256:
  `F46457EB86DE9E5499C8272C6B72C23EAE0D80B42E24F591906B14589230B6E9`.
- B1c6 implementation approval receipt:
  `gpt55_critic_viral_v2_complete_authoring_phase_b1c6_asset_provenance_implementation_review_20260903.md`,
  SHA-256
  `690963D07976A244B2389AFE1429AAFFA0A2A3F14F890206E15CB5B068D84BDD`,
  no P0/P1.
- Current exact production hashes:
  - author `3DA02ADF17E2224C86A1418D18ECB06754E1FC6CD628717C1652EA315968FE1C`;
  - builder `C496B8649E36C8D656C1CC93C25689B97E263339F7B12775A3D24C5CFBE80D3E`;
  - verifier `E593D0B9EEA9CC1E71642DBC2527774FDB923D74914A52684391623CD9A8E5C1`.
- Current regression: `128/128 OK`; both frozen-v1 preflights pass.
- Current exact public seam:
  - builder `v2 asset placement mismatch`;
  - verifier `E_V2_ASSET: placement`.
- Asset inventory: 125 total, 93 reader and 32 evidence-only; provenance
  `16 Markdown / 100 visual / 9 provisional full-page`.

## User decisions that placement must preserve

Read the live review registry
`USER_REVIEW_TYPICAL_PROBLEMS_20260902.md`, especially:

- OUT-005: art order relative to overlay/source text;
- OUT-006: typographic `Summary` must not be emitted as reader art;
- OUT-007: platform logos/promotional badge are not content art;
- OUT-019: Appendix section/source ordering;
- OUT-024: Ground Floor & Basement must be a full-page handout with a
  translatable key, not incomplete crops;
- OUT-025: non-standard character-sheet backs must remain full-page facsimiles
  with translatable supplemental text;
- source pages 123–124 are advertising excluded from reader publication;
- two coastal/boat arts belong under `Plots and Schemes`, not `Prologue`;
- post-MASTER_RU art replacement/review is a later Step8A concern and must not
  be pulled into this placement phase.

## Required read-only analysis

1. Inventory all 93 reader assets in deterministic source order with stable
   asset id, page, provenance kind, current binary/provisional status, source
   visual/text order evidence, intended owner anchor and exact placement
   relation.
2. Define a closed reusable placement union. Candidate operations may include
   `before_event`, `after_event`, `replace_event`, `within_owner_start/end`, or
   a dedicated full-page/handout relation, but the final design must use the
   minimum unambiguous set and define exclusivity/cardinality.
3. Derive placement from immutable evidence, not heading proximity alone:
   Markdown span order for the 16 marker assets, comparison bbox/block order
   for visual regions, and reviewed physical-unit/page-slot obligations for the
   9 provisional full-page assets.
4. Distinguish reader placement from evidence retention. Exactly 93 reader
   assets must have one placement; all 32 evidence-only assets must have none.
5. Prove owner/event targets exist, are semantically compatible, and avoid
   moving assets across section boundaries when headings are restored.
6. Address page/column order and cross-page continuation explicitly. Large
   coordinate gaps may indicate inset boundaries but must not alone determine
   section ownership.
7. Define how full-page map/pregen assets coexist with their translatable
   supplemental key/background text and generated handout/pregen indexes.
8. Define exact author schema, builder/verifier recomputation, independent
   mutation matrix and rendering semantics. Builder and verifier must not trust
   an authored placement as their oracle.
9. Identify all ambiguous placements requiring a frozen decision ledger or
   user review. If none, prove why the immutable overlay/semantic evidence is
   sufficient.
10. Run a guarded no-write diagnostic projection to determine exact placement
    counts and the next public-v2 seam after placement. Do not implement that
    next seam.

## Required attacks/test plan

Specify symmetric builder/verifier tests for at least:

- missing, duplicate, conflicting and multi-placement assets;
- evidence-only asset with placement and reader asset without placement;
- foreign/nonexistent event or owner anchor;
- borrowed placement from same-page or same-kind donor;
- before/after inversion, source-order inversion and cross-owner drift;
- generated-navigation target misuse;
- placement on excluded advertising pages;
- full-page map/pregen placed as ordinary crop or without physical-unit/page
  slot relation;
- Markdown marker target moved away from its source event;
- visual-region bbox ordering inconsistent with target event/owner;
- two `Plots and Schemes` arts regressing into `Prologue`;
- duplicate emitted asset link/occurrence and unplaced reader asset;
- B1c4/B1c5/B1c6 and frozen-v1 preservation;
- no canonical/temp/candidate/render output.

## P2 residue boundary

Six pre-existing ignored `kb_creator/.v2-inputs-*` debug/probe directories are
recorded release-cleanliness debt. Do not delete, modify, or treat them as B1c7
output. Preserve and explicitly exclude them from the bounded no-output claim.

## Forbidden actions

- No implementation or test edits.
- No canonical `publication_config_v2.json`, Candidate D, render/review bundle,
  MASTER_EN, MASTER_RU, HTML or PDF.
- No Step8A art extraction/replacement.
- Do not alter source, accepted reconstruction, v1, protected historical
  roots, ignored debug roots, plan/context/status or Git state.

## Deliverable

Write one immutable architecture receipt containing:

- role/ownership declaration and explicit no-implementation statement;
- hashes and immutable evidence inspected;
- complete 93-row placement inventory, preferably as a companion immutable
  JSON/TSV only if the receipt itself would become impractical (declare and
  hash any companion); otherwise keep one receipt;
- closed placement schema and derivation algorithm;
- ambiguity/decision ledger assessment;
- generic builder/verifier validation and full mutation matrix;
- exact minimum engineering scope;
- exact next public seam and no-output stop boundary;
- P0/P1/P2 architecture findings and terminal:
  - `READY_FOR_V2_COMPLETE_AUTHORING_PHASE_B1C7_ARCHITECTURE_REVIEW`, or
  - `CHANGES_REQUIRED_V2_COMPLETE_AUTHORING_PHASE_B1C7_ARCHITECTURE`.

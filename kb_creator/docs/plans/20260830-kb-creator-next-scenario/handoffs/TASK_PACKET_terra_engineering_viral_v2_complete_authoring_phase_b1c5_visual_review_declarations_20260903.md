# Task packet — Viral v2 complete authoring Phase B1c5 visual-review declarations

## Governance and boundary

- Goal id: `20260830-kb-creator-next-scenario`.
- Assigned role: `nri-engineer`, canonical `gpt-5.6-terra` / medium.
- Main-chat `gpt-5.6-sol` / medium retains orchestration.
- B1c4 implementation is independently approved in receipt SHA-256
  `BBB983ADD8E97885B0B9FCF0226145F262BD857127853F9CCC33706E82FC2EED`.
- This slice owns deterministic `visual_review_units` authoring and independent
  validation only. It must stop at the next exact public preflight seam.
- Exclusive edit ownership: the six author/builder/verifier script and test
  files plus immutable receipt
  `terra_engineering_viral_v2_complete_authoring_phase_b1c5_visual_review_declarations_20260903.md`.
- Do not edit plan/context/prior receipts, frozen inputs or Git. Do not author
  typed payload/recovery content, create canonical `publication_config_v2.json`,
  candidates, renders, review bundles or downstream outputs. Preserve all
  unrelated/user edits and nine protected historical roots.

## Bound starting hashes

```text
author helper   FFE2202E0FC2CB2FCD36FCA802C8484057E714704B734027B6AD25B17F0C9249
author tests    A019999265B17005775D801E4D5DF8E83A540959F402F8837705069C58D7386F
builder         E36775C33A430A3F7D21743D5DCD9EBA185E16F247CD5DF42FECA6B9080A1DF9
builder tests   236E56016E687B26F772967A8475E4BF4E797E954D0CCB359AAB0CC1337BA1C2
verifier        F2C0C79FBA69F6C82ABD0A86BBF88B69B0987ACE89C618FA45837F71E16B544B
verifier tests  D240A5BEE52759C03E82928CCE968C2509F8FFFF569BBB3168A04D8E973F9EFB
```

Verify all identities before editing.

## Required implementation

Replace the two placeholder review rows in the author with a deterministic,
closed projection from the current canonical graph. Generate exactly one row
for each required review object:

- each heading event whose hierarchy row has `representation: heading` as
  `heading_outline`, priority true;
- each `structured_unit` event using its exact supported content kind;
- each distinct event referenced by an xref source or source recovery target as
  `xref_recovery`;
- each asset with `disposition: reader` as `asset_placement`;
- zero rows for evidence-only/replaced/excluded assets, generated-navigation
  events by themselves, pages 123--124 or non-reader hierarchy rows.

Use stable semantic review ids derived from the referenced event/asset id, not
mutable list ordinals. `source_pages` must equal, not merely contain, the exact
referenced pages. Event and asset order must follow canonical source/event/asset
order. Contact-sheet group and priority rules must be deterministic and closed.
The current B1c4 graph is expected to yield `136` rows (`2` heading, `41`
xref/recovery, `93` reader-asset, `0` structured); later event/payload slices
must automatically expand the projection rather than requiring hand edits.

Builder and verifier must independently derive the exact expected row list from
the declared graph and compare it field-for-field before later gates. Do not
import author code or one another. Close the current asset-page mismatch:
canonical B1c4 declarations use `source_page`, while the legacy v2 fixture may
use `page`; schema routing must be explicit and must not throw raw `KeyError`.
Unexpected/missing page fields must map to stable visual-review errors.

Validation must reject before the next seam:

- missing or duplicate review row;
- duplicate coverage of one object across rows;
- extra/non-required object, evidence/excluded asset or pages 123--124;
- wrong review id, kind, event/asset reference, order, page set, priority or
  contact-sheet group;
- mixed event+asset row, empty row, foreign id or source-page superset;
- reader asset omitted or evidence-only asset promoted;
- raw `KeyError`/traceback for canonical or malformed asset page declarations.

Add symmetric builder/verifier public mutations for every class. Preserve all
B1c4 asset/provenance/migration regressions.

## Exit gate

1. Six-file py-compile passes.
2. Expanded combined author/builder/verifier suite passes; record exact count.
3. Positive author projection independently proves the exact current `136`
   rows and kind counts above.
4. Both frozen-v1 preflights pass with unchanged identities.
5. Guarded unmutated public v2 preflights pass visual-review validation in both
   implementations and stop at the same newly discovered next exact seam.
   Record builder and verifier messages; do not implement that later seam.
6. All negative review mutations fail at stable B1c5-specific mappings with no
   raw traceback.
7. Canonical/temp v2 config, Candidate D, renders/review/downstream outputs are
   absent/new-count zero; nine protected historical roots remain untouched.
8. Record final hashes, commands/results and terminal
   `READY_FOR_V2_COMPLETE_AUTHORING_PHASE_B1C5_IMPLEMENTATION_REVIEW` in the
   immutable receipt.

Fresh GPT-5.5/high implementation review is mandatory before the next slice.

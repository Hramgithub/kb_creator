# Unified CoC terminology context

Goal id: `20260916-coc-unified-terminology`

State: `complete`

## Accepted decisions

- The authority boundary is the game system, not a scenario or book.
- All NRI Call of Cthulhu subprojects use
  `CoC/Project_Reference/Terminology/CoC_Terminology_Decisions.csv`.
- Dune and other game systems have separate system registries.
- Scenario-local terminology may contain proper names and unique concepts but
  may not duplicate CoC characteristics, derived parameters, roles, or skills.
- Sealed historical/production copies are immutable provenance only and are
  never edited or consulted as the live authority.
- Accepted unambiguous replacements are applied by reusable Python, not by
  manual edits in a generated book.

## Completed evidence

- The shared CSV now includes the full CoC statblock profile and character
  skills, known bad Russian variants, source typos/nonstandard aliases, and
  `review_required` rows for ambiguous source forms.
- The separate active skills Markdown and both Dissociation-local terminology
  copies are deleted.
- The Dissociation blueprint/contract reference exactly one repository-global
  terminology authority.
- MASTER_RU producer and independent verifier both perform and verify
  deterministic normalization before hashing/sealing; a detected CoC statblock
  fails closed if the required system profile is incomplete.
- Active Innsmouth verification now reads the shared CSV. Its accepted 2026
  manifest retains the deleted glossary's path/hash only as embedded historical
  provenance.
- Focused MASTER_RU producer/verifier coverage passed `43`, skipped `1`, with
  `30` subtests after the final stat-label and legacy-rebind corrections. The
  final current-authority selection passed `121`, skipped `2`, with `30`
  subtests. The legacy accepted Innsmouth package verifies against the current
  shared registry.
- Dissociation run `20260916-publication-29` binds the final shared registry at
  `16003` bytes / SHA-256
  `EE84E121E63ECDA3F2165205E8335FD3C68E70CF1DEFE1D00CE6C3FF97EFF3AE`.
  Its terminology QA passes with `18` deterministic replacement events.
- Run29 completed the publication graph through offline package verification.
  The PDF remains a fresh export of the exact accepted DOCX, and the DOCX has
  zero footer parts, footer references and `PAGE` fields.

## Completion state

The system-level consolidation is complete. Future CoC scenarios and books
must reference the one canonical CSV; they may add only scenario-specific
names and concepts outside it. A different game system, such as Dune, owns a
separate system registry. No MinerU/OCR rerun was needed for this change.

## Blockers

None.

# Task packet — Viral v2 B1c4 critic remediation

## Governance and ownership

- Goal id: `20260830-kb-creator-next-scenario`.
- Assigned role: `nri-engineer`, canonical profile `gpt-5.6-terra` / medium.
- Orchestration remains with the main `gpt-5.6-sol` / medium chat.
- This is a bounded remediation of two P1 findings, not a redesign or a later
  authoring phase.
- Exclusive edit ownership: the six author/builder/verifier implementation and
  test files bound below, plus the immutable remediation receipt
  `terra_engineering_viral_v2_complete_authoring_phase_b1c4_critic_remediation_20260903.md`.
- Do not edit plan/context/registry/architecture/review receipts, frozen v1,
  accepted reconstruction, source PDF, candidates, assets, visual-review
  outputs, Git state or any downstream surface.
- Do not create canonical `publication_config_v2.json`, a candidate, rendered
  bytes, MASTER_RU, Step 8A, HTML or PDF output.

## Bound starting state

- Approved architecture receipt:
  `sol_architect_viral_v2_complete_authoring_phase_b1c4_asset_closure_20260903.md`,
  SHA-256 `A68A643CEBCF11BFBC3F358A900F3677309C02A8D410AB29B4861D62DAEB6442`.
- Engineering receipt:
  `terra_engineering_viral_v2_complete_authoring_phase_b1c4_asset_engineering_20260903.md`,
  SHA-256 `9E5799222BBB7A6C1266194DF18E287715F86F36A4451C93DE5A4FB68F1B4DCA`.
- Blocking critic receipt:
  `gpt55_critic_viral_v2_complete_authoring_phase_b1c4_implementation_review_20260903.md`,
  SHA-256 `D20415E2B888A3370C00071991A16EE9919312F3F2659D80C0374D91ABBF85A1`.
- Exact starting file identities:

```text
author helper   6E0E704B8921B9339C50FA7C7A6687C4ADCBF9C4230558A7B93BF1A65FC6EB1B
author tests    4BDF8D71D200C6F0ECAF22D21C615BF2DF878BE9B4ACCD56A6E67A7BD1202904
builder         BDD0D2568D79DE468FECC2FF04276C91448F84A47FAF6709C06C1F2C956746CA
builder tests   093DCC3385AA976045EE48D1A1B2C78B846C90682983C0E87C16E6023DCE5689
verifier        DDE50D8335EDA60D715054B2C96FE0008E8F20FA774AFCF49FBE026AA3BF30AC
verifier tests  8FA0B9E1D35A52875BE4CC666451892AEE48A25FA3A60CE441DC1EBD96819232
```

Stop and report identity drift before editing if these do not match.

## P1 remediation A — closed provenance and binary identity

Implement the architecture receipt's complete discriminated `provenance`
object on every canonical B1c4 asset declaration. The allowed alternatives and
their exact required/forbidden fields must be closed and truthful:

- exact accepted-v4 Markdown image-reference span;
- exact three-view visual-region evidence;
- reviewed provisional full-page source-PDF render recipe;
- excluded-advertising provenance with no reader binary/target.

The author must derive these only from the frozen v1 config, accepted-v4
manifest/pages, three-view comparison, source PDF metadata and approved
architecture table. Do not manufacture text spans for visual evidence.

Builder and verifier must independently validate each declared row before the
visual-review gate. For all 121 path-backed rows bind exact path, bytes,
SHA-256, image magic and decoded dimensions to accepted-v4 manifest and the
appropriate comparison/Markdown evidence. Validate the single frozen
source-page render and all eight new provisional full-page recipes against
exact source page, MediaBox/CropBox/rotation, DPI, format and expected pixel
dimensions without materializing files. Exclusions must carry no binary or
reader emission. Reject missing/extra/wrong provenance fields and borrowed
evidence identities.

Add public builder and verifier mutation tests for at least: missing provenance,
wrong discriminator, fake Markdown span, foreign visual region, swapped block
identity, missing binary, path change, byte/SHA/magic/dimension mismatch,
manifest/comparison mismatch, malformed full-page recipe and binary attached to
an exclusion. Each must fail at the B1c4 asset seam, never at later review
coverage.

## P1 remediation B — exact migration and replacement identity

Implement independently in builder and verifier the exact approved tables from
the architecture receipt, rather than accepting counts, prefixes, page families
or self-consistent supplied rows.

Require:

- all 123 frozen source ids in exact source order and each exact outcome,
  target id list, decision id and source page;
- exact `OUT-005`, `OUT-006`, `OUT-007`, `OUT-024`, `OUT-025`, `OUT-026` row
  membership and `null` only on the 99 unchanged rows;
- the exact eight new target ids in exact order with exact decision,
  evidence identity, source pages, physical unit/slot/owner/accessibility
  obligations and exact ordered `replaces` child lists;
- exactly 16 prescribed child occurrences, each used once under its prescribed
  target and never emitted as reader; six exact exclusions targetless and never
  emitted; all required retained/new targets remain reader-visible.

Add symmetric public mutations reproducing every critic probe: foreign child,
child swap between targets, same-page membership swap, forged target id,
target-order swap, omission, duplicate, target/decision/evidence substitution,
exact-row outcome/decision swap, exclusion-membership swap, replaced-child
reader leakage and excluded-page reader/event leakage. Preserve broad counts in
the mutations where possible so exact identity, not count validation, is proven.

## Required final evidence

1. Recompute all six final hashes and record them.
2. Six-file `py_compile` passes.
3. All focused positive and negative tests pass.
4. Expanded combined author/builder/verifier baseline passes and its exact count
   is recorded.
5. Both frozen-v1 preflights pass with unchanged frozen identities.
6. Guarded unmutated public v2 preflights reach exactly builder
   `v2 visual review coverage mismatch` and verifier `E_V2_REVIEW: coverage`.
7. Every critic mutation fails earlier with stable B1c4-specific mapping in both
   public implementations.
8. Canonical/temp v2 config, candidates, renders, review output and downstream
   outputs remain absent/new-count zero. Preserve the nine pre-existing
   protected candidate/staging roots and demonstrate no mutation.
9. Write the immutable remediation receipt with changed paths, exact commands,
   results, blockers and terminal
   `READY_FOR_V2_COMPLETE_AUTHORING_PHASE_B1C4_IMPLEMENTATION_REREVIEW`.

Fresh independent GPT-5.5/high rereview is mandatory after remediation. No
later phase opens from engineering evidence alone.

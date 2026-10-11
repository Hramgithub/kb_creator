# Viral remediation v2 independent output verifier

- Goal: `20260830-kb-creator-next-scenario`
- Step: `7-user-review-remediation-v2-output-verifier`
- Owner: same `nri-engineer`, `gpt-5.6-terra` / `medium`
- Builder gate: `READY_FOR_V2_OUTPUT_VERIFIER`
- Completion token: `READY_FOR_VIRAL_V2_POLICY`

## Objective

Complete Slice 3 with a genuinely independent candidate-level v2 verifier and
mutation suite. The verifier must treat the candidate as an external artifact,
derive expected facts independently from v2 config + frozen reconstruction, and
must not import/reuse builder parsing, serializer or verification functions.

You are not alone in the worktree. Preserve prior work and edit only the three
exclusive paths.

## Exclusive ownership

- `kb_creator/scripts/verify_scenario_master_en.py`
- `kb_creator/tests/test_verify_scenario_master_en.py`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_user_review_remediation_v2_output_verifier_20260903.md`

## Required verification

- strict v1 route remains unchanged and passes real v1 preflight;
- exact candidate inventory/file existence/size/SHA-256 and no acceptance
  sidecar/review-only artifact;
- recompute audit=124, reader=122, excluded=2 from v2 declarations and prove
  pages 123--124 leak no text, events, headings, xrefs or assets;
- reconstruct monotonic expected source-event order independently and compare
  to candidate provenance and reader Markdown;
- complete source-title fidelity, parent proximity, no anchor/run-in outline
  pollution and generated-navigation provenance/no source-TOC duplication;
- raw LF/EOL and ordinary blank-run bounds without damaging literal content;
- parse Markdown structure independently: exact table/header/row/cell counts,
  bounded callouts/list-callouts/cards/statblocks/maps/pairs and continuation
  after their end; anchors and xrefs resolve;
- verify every reader asset placement relative to its declared target, copy
  identity, manifest/inventory closure, suppression and duplicate policy;
- verify source fragment/range identities and source-backed recovery provenance;
- dynamic topology/metrics only, with no Viral v2 constants;
- independent mutation tests for inventory/hash, order, bounds, title drift,
  table shape, anchor-outline pollution, placement, asset hash, malformed EOL,
  excluded leakage and missing provenance.

The verifier implementation may not import `build_scenario_master_en.py` or any
builder-owned helper. Tests may create fixtures/candidates without weakening
that source-independence assertion.

## Forbidden

No builder/config/evidence/source/reconstruction/real candidate/Step 8A/Git/
cleanup/deletion/unrelated path changes.

## Evidence

Run the complete verifier test module, `py_compile`, real v1 builder+verifier
preflights, and a static independence check. Write the immutable receipt with
exact results and coverage. Return `READY_FOR_VIRAL_V2_POLICY` only if the full
candidate-output route closes; otherwise identify the exact verifier-only gap.

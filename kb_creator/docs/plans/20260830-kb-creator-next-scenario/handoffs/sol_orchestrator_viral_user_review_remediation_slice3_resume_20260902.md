# Viral remediation Slice 3 engineering resume

- Goal: `20260830-kb-creator-next-scenario`
- Step: `7-user-review-remediation-implementation-slice-3`
- Owner: same `nri-engineer`, `gpt-5.6-terra` / `medium`
- Prior receipt: `terra_engineering_viral_user_review_remediation_20260902.md`
- Architecture: `sol_architect_viral_user_review_remediation_spec_20260902.md`
- Completion token: `READY_FOR_VIRAL_V2_POLICY`

## Objective

Continue from the preserved partial work and complete architecture Slice 3
only: dual v1/v2 builder routing, typed source-ordered event graph and
serialization, plus a genuinely independent v2 verifier. Prove v1 compatibility
and all blocking structural mutations with focused synthetic fixtures. Do not
author the real Viral `publication_config_v2.json` or evidence yet.

You are not alone in the worktree. Preserve prior and concurrent edits, do not
revert anything, and adapt to the partial Slice 1/2 implementation already
present.

## Exclusive owned paths

- `kb_creator/scripts/build_scenario_master_en.py`
- `kb_creator/tests/test_build_scenario_master_en.py`
- `kb_creator/scripts/verify_scenario_master_en.py`
- `kb_creator/tests/test_verify_scenario_master_en.py`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_user_review_remediation_slice3_20260902.md`

No other path may be modified in this continuation.

## Required scope

Implement the architecture receipt's v2 contract and Slice 3 requirements:

- closed schema routing with unchanged strict v1 behavior;
- hierarchy representations `heading`, `anchor_only`, `inline_run_in`;
- full source-title fidelity unless a typed reviewed transformation exists;
- one monotonic typed source-event graph with exact fragment/range identities;
- canonical LF serialization with construct-specific table, callout,
  ordered-list-callout, equipment-card, creature-statblock, physical-page-pair
  and full-page-map containers;
- exact event-relative asset placement and reader-value suppression;
- source-backed lexical recovery provenance;
- dynamic declared metrics and exact 124-audit / 122-reader exclusion checks;
- generated navigation provenance and no source-TOC duplication;
- independent verifier logic that does not import/reuse builder parsing or
  verification implementation;
- regression mutations for order, bounds, title drift, table rows/cells,
  anchor-only outline pollution, asset placement, malformed EOL, excluded-page
  leakage and v1 compatibility.

Use compact synthetic v2 fixtures to close the serializer/verifier contract.
Do not weaken v1 invariants or hard-code Viral v2 counts.

## Protected/forbidden

All configs, source reconstruction, source PDF, candidates, evidence roots and
other dirty paths are read-only. No Candidate D/scratch build, Step 8A,
MASTER_RU, HTML/PDF, Git mutation, deletion, or hand edit to generated Markdown.

## Verification and receipt

Run at least:

```powershell
python -B -m pytest -q kb_creator/tests/test_build_scenario_master_en.py kb_creator/tests/test_verify_scenario_master_en.py
```

Write the new immutable receipt at the exact owned path. Record exact changes,
test results, v1 regression evidence, v2 feature/mutation coverage, blockers,
elapsed time and token availability. Return `READY_FOR_VIRAL_V2_POLICY` only
when Slice 3 is complete; otherwise return a precise remaining gap without
changing scope.

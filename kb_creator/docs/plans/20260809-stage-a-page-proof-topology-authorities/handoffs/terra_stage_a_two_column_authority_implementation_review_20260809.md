# Immutable Independent Implementation Review Receipt — Stage A Two-Column Authority

- Goal id: `20260809-stage-a-page-proof-topology-authorities`
- Step id: `3a-r`
- Review kind: `implementation`
- Candidate state: non-frozen incremental three-row fixture-only candidate; this is not a release review or topology acceptance receipt.
- Role/model/effort: independent Terra critic / model platform-unverified / high.
- Implemented or materially designed candidate: **no**. This reviewer performed neither implementation nor material design.
- Orchestrator policy owner: `gpt-5.5` medium (platform-unverified). Orchestration ownership remains with the main-chat orchestrator.
- Assignment state: `platform-unverified`.
- Scoped override: `none`.

## Severity findings

### P0

None in the assigned fixture-only implementation scope.

### P1

1. **The two-column topology assertion is regenerated from the candidate rather than retained and validated as a literal canonical assertion leaf.** The third `_FixtureRow` sets `positive_topology_assertion_raw` to `b""`; its expected tuple repeats that empty value. `_two_column_assertion()` constructs the assertion from the candidate artifact and `_validate_artifact()` compares only the generated-byte SHA-256 with the one stored digest. The implementation therefore lacks the required literal assertion bytes, byte length/raw hash, distinct facts hash and assertion content hash; the stored value is the generated raw assertion hash, not the required positive-topology facts hash. This is a mutable-answer-key path and cannot supply the exact later page-proof inventory assertion identity.

2. **The advertised target-only negative evidence does not exercise a resealed full validation/replay path.** Most focused negatives mutate a copied artifact and call `_validate_two_column_rows()` directly. They neither make all non-target row/inventory/content/assertion seals valid through a private surrogate expected row nor demonstrate a target-only repair passing full `_validate_artifact(..., replay=True)`/replay. Thus a rejection may be attributable to incomplete global artifact structure or stale seals outside the target; the tests do not meet the accepted stale-hash-only prevention contract.

### P2

None.

## Verdict

**REJECT — remediation required before the two-column authority is independently accepted.**

The raw fixture itself successfully projects `A,B,C,D` across two root streams/frames with the raw `B -> C` transition and preserves Stage A non-geometry semantics, but the literal assertion and target-only adversarial requirements are not yet implemented.

## Files checked

- `kb_creator/pdf_raw/raw_authority_projection.py` — SHA-256 `8326A289978AC859F761ACB1898852FE7CE0A1D3B1AC31DB6776E27A8C611A64`
- `kb_creator/tests/test_raw_authority_projection_stage_a_topology_authorities.py` — SHA-256 `385F56E8F0F5D2137BE8090EE90D45EAA1B0F6C271E8281C4CC6779A61EBA308`
- `kb_creator/tests/test_raw_authority_projection_stage_a_contract.py` — SHA-256 `18513D1707E658BA411ED8096D0E333A1C80EDE45FD7D0D96CB4CE9FE1459D88`
- `kb_creator/docs/plans/20260809-stage-a-page-proof-topology-authorities/handoffs/terra_engineer_stage_a_two_column_authority_implementation_20260809.md` — SHA-256 `DAE22D29703D1B5FE9A8411422B07638BF611217A3973E2398402FA64092EC0E`
- Accepted architecture:
  - `handoffs/sol_stage_a_page_proof_topology_authorities_spec_20260809.md` — SHA-256 `23ECCF5ED32998D55EB0DBBCF73B2987FFA4D14DC0BEDD40361B7DE274EAB630`
  - `handoffs/terra_stage_a_page_proof_topology_authorities_architecture_review_20260809.md` — SHA-256 `97E82053214A0F2AAC9063A5D29D40CF606C93255E6A8B798FB7434770025596`

## Evidence

- The two baseline Stage A leaves remain the first two literal rows, and the contract test confirms they still exactly match the immutable two-row legacy authority registry. The new candidate remains a third Stage A row; the legacy registry stays two rows.
- The third literal PDF has `/Contents [5 0 R 6 0 R]`; projection/replay produces two root streams/frames, glyph bytes `A,B,C,D`, atom ordering by frames `5:0,5:0,6:0,6:0`, and `B -> C` at ordinals `1 -> 2`. Both the implementation and the produced artifact retain `geometry`, `visibility` and `semantic_role` as `unavailable_stage_a`; the boundary object names geometry, visibility, semantic blocks and reading order as not proved.
- The module has no `page_proof` import or call, and the reviewed slice contains no live scenario/source/output/configuration route. The contributor handoff also scopes nested Form and page-proof work out. This review performed no Git, live-file, configuration, output or rebuild action.
- The incremental three-row state cannot satisfy the page-proof inventory: it contains only `stage_a_positive_two_column.v1`, while the accepted coverage inventory requires that id **and** `stage_a_positive_nested_form.v1`, both independently accepted. It is therefore a valid non-accepted intermediate only; it must not be recorded as coverage-complete or used to alter the page-proof guard.
- Focused verification run: `D:\NRI\.tools\python-3.13.14\python.exe -B -m pytest -q -p no:cacheprovider kb_creator\tests\test_raw_authority_projection_stage_a_topology_authorities.py kb_creator\tests\test_raw_authority_projection_stage_a_contract.py`.
  Result: `11 passed in 0.12s`. These passing tests establish the present projection shape and narrow checks, but not the two P1 requirements above.
- Freeze evidence: none. The contributor receipt describes an incremental implementation and the required exact assertion/topology-acceptance receipt does not exist; this is a point-in-time non-frozen review.

## Minimal correction packet

1. Extend the third row and the independent primitive expected tuple with the actual canonical `positive_topology_assertion_raw`, its literal byte length and raw SHA-256, the distinct facts SHA-256 and assertion content SHA-256, plus the exact expected count and ordered row-seal tuples required by the accepted architecture.
2. Replace candidate-generated assertion acceptance with closed canonical literal assertion decoding/validation and independent joins from literal assertion facts to projected artifact rows. Recomputing facts for comparison is permitted; deriving the expected assertion leaf from the candidate is not.
3. Rewrite/add focused adversarial cases as private, fully resealed surrogate rows/artifacts. Each case must remain valid in every non-target invariant, fail at its intended full validation/replay boundary, and pass after only the target repair/reseal. Retain parser-preaccess poison checks for registry/admission failures.

## Blockers, recommendation and next action

- Blockers: the two P1 implementation defects above.
- Recommendation: keep this third-row state non-frozen and coverage-incomplete; do not publish its current generated assertion hash as a topology acceptance identity.
- Next action: authorize only the minimal two-column remediation packet above, then request a new independent Terra implementation review of the corrected exact hashes. The nested-Form slice, page-proof inventory/guard changes, live work, rebuild and release remain unauthorized.
- Declared exclusions: no code/test/canonical plan/context/status/release edit by this reviewer; no live Innsmouth input/output read or processing; no Git, network, rebuild or release operation.
- Invalidation: any mutation to the checked module, focused tests, contributor handoff or accepted architecture invalidates this point-in-time receipt and requires a new independent review.

## Receipt metadata

- Result: rejected pending literal assertion and full target-only adversarial remediation.
- Files changed: this immutable receipt only.
- Elapsed active time: approximately `5 minutes`.
- Token use: `unavailable`.
- Timestamp: `2026-08-09T21:23:37.9432866+03:00`.

This receipt does not transfer orchestration ownership.

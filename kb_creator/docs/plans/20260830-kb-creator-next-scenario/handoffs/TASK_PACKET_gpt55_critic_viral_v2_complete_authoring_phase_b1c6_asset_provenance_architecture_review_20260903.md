# Task packet — independent B1c6 asset-provenance architecture review

## Review declaration

- Reviewer: fresh independent `gpt-5.5` / high critic.
- `review_kind`: `architecture`.
- Do not implement, materially redesign, or edit code/tests/plan/context/status.
- Orchestration ownership remains with main chat (`gpt-5.6-sol` / medium).
- Candidate state: non-frozen architecture checkpoint; no canonical v2 config
  or built `MASTER_EN` candidate exists.

## Bound architecture

- Assigned architecture packet:
  `TASK_PACKET_architect_viral_v2_complete_authoring_phase_b1c6_asset_provenance_binding_20260903.md`,
  observed SHA-256
  `88B45E9F986E06B5BB73CF5756DA54A8CFB860C999EC028E54F57E6A1E863B98`.
- Architecture receipt:
  `sol_architect_viral_v2_complete_authoring_phase_b1c6_asset_provenance_binding_20260903.md`,
  SHA-256
  `B37F37EF54885AEC1CFC4CEF557D31D326E603D5EA70F9BEA919C42C18162E5C`.
- B1c4 implementation approval:
  `gpt55_critic_viral_v2_complete_authoring_phase_b1c4_asset_identity_rereview_20260903.md`,
  SHA-256
  `BBB983ADD8E97885B0B9FCF0226145F262BD857127853F9CCC33706E82FC2EED`.
- B1c5 implementation approval:
  `gpt55_critic_viral_v2_complete_authoring_phase_b1c5_implementation_review_20260903.md`,
  SHA-256
  `05B4573DF3FBE1EE7ACF31711AEFDBD44BB68A2448F90CDF494A332F4D649D82`.

## Claimed root cause and boundary

Both public preflights pass approved B1c4/B1c5 and then route all 125 canonical
assets through a stale A3 legacy loop requiring top-level `source_span_ids`,
`reader_value`, and `placement`. Truthful canonical provenance is 16 Markdown
references, 100 visual regions and 9 provisional full-page declarations; all
125 bind successfully in the architecture's no-write independent diagnostic.
After B1c6, the claimed exact next seam is 93 missing reader placements:

- builder `v2 asset placement mismatch`;
- verifier `E_V2_ASSET: placement`.

## Required independent review

1. Verify hashes and inspect the exact builder/verifier call paths and current
   immutable evidence. Confirm the stale-loop diagnosis is complete and not an
   inferred explanation.
2. Challenge the homogeneous canonical-versus-legacy mode rule. Ensure it does
   not create a downgrade path, mixed-mode ambiguity, scenario-name bypass, or
   hidden acceptance of legacy aliases in canonical rows.
3. Verify the proposed Markdown contract retains exact 16 source-span bindings
   without falsely requiring logical ledger owner IDs to equal final asset IDs.
4. Verify visual-region binding closes path borrowing, digest borrowing,
   manifest-row borrowing, comparison-block borrowing, and companion-source-PDF
   borrowing, including device-specific path normalization.
5. Verify provisional full-page binding uses the CLI-bound PDF, real page
   geometry/rotation and a closed render recipe without rendering bytes or
   inventing output hashes.
6. Confirm the proposal is generic and independently recomputable in builder
   and verifier; it must not use the author projection or the B1c4 Viral oracle
   as expected truth.
7. Confirm the four-file engineering scope is sufficient and does not require
   an author schema change, B1c5 change, canonical config, candidate or output.
8. Independently reproduce or refute the 16/100/9 zero-error evidence binding
   and the exact 93-reader placement next seam.
9. Audit the proposed symmetric mutation matrix for missing P0/P1 attacks or
   validator-order masking.

## Forbidden actions

- No code/test edits or implementation.
- No canonical `publication_config_v2.json`, Candidate D, render/review,
  MASTER_EN, MASTER_RU, HTML or PDF.
- Do not alter protected historical candidates/staging roots or Git state.
- Create only one immutable architecture-review receipt.

## Deliverable

Write one immutable receipt under this handoff directory containing:

- `review_kind: architecture` and explicit no-implementation statement;
- hashes checked, evidence inspected, and independent probes;
- P0/P1/P2 findings;
- assessment of root cause, generic contract, mutation matrix and next seam;
- one terminal decision:
  - `APPROVED_V2_COMPLETE_AUTHORING_PHASE_B1C6_ARCHITECTURE`, or
  - `CHANGES_REQUIRED_V2_COMPLETE_AUTHORING_PHASE_B1C6_ARCHITECTURE`.

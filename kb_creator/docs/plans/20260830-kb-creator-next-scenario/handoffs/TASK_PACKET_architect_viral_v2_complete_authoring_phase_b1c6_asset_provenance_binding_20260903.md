# Task packet — Viral v2 B1c6 asset-provenance input-binding architecture

## Role and boundary

- Owner: `gpt-5.6-sol` architecture/root-cause role at high reasoning.
- This is architecture and diagnosis only. Do not implement or edit code/tests.
- Write one immutable architecture receipt under this handoff directory.
- Orchestration ownership remains with the main chat (`gpt-5.6-sol` / medium).
- Candidate state is non-frozen; no canonical v2 config or built candidate exists.

## Current approved state

- Accepted reconstruction package inventory SHA-256:
  `68C17FB765A89C6146398868E61F1F6EB7B2FE4EAFBA8C2C2C8F42260BBDBA83`.
- Source PDF SHA-256:
  `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05`.
- Frozen v1 publication config SHA-256:
  `C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30`.
- B1c4 exact per-asset declaration identity is independently approved in
  `gpt55_critic_viral_v2_complete_authoring_phase_b1c4_asset_identity_rereview_20260903.md`,
  SHA-256 `BBB983ADD8E97885B0B9FCF0226145F262BD857127853F9CCC33706E82FC2EED`.
- B1c5 exact visual-review declarations are independently approved in
  `gpt55_critic_viral_v2_complete_authoring_phase_b1c5_implementation_review_20260903.md`,
  SHA-256 `05B4573DF3FBE1EE7ACF31711AEFDBD44BB68A2448F90CDF494A332F4D649D82`.
- Current bound production hashes:
  - author `3DA02ADF17E2224C86A1418D18ECB06754E1FC6CD628717C1652EA315968FE1C`;
  - builder `8055F7B355EB711474398C84263521C4B8001D852B2B53987523D5CBE9C4D6DD`;
  - verifier `2CFEE758C2EDBC5F445E864EDB46E366EB07E7E19D6E19FBD64D6A99E9FF2ED5`.
- Current scoped regression result: `Ran 124 tests in 217.846s / OK` from root;
  independent critic reproduced `Ran 124 tests in 214.549s / OK`.
- Current authored projection has 125 assets: 93 reader and 32 evidence-only;
  provenance kinds are 16 Markdown references, 100 visual regions and 9 reviewed
  provisional full-page assets. Six source advertising rows are excluded from
  the 125 emitted asset targets but remain in source-disposition audit.

## Exact current seam

The guarded unmodified public-v2 preflight pair passes B1c4 and B1c5, then
stops identically at the deeper input-binding layer:

- builder: `v2 asset provenance mismatch`;
- verifier: `E_V2_ASSET: provenance`.

This seam must not be confused with the already-approved B1c4 closed
declaration-identity checks. Diagnose the actual deeper mismatch rather than
reopening or duplicating B1c4.

## Required analysis

1. Trace the exact builder and verifier call paths that produce the seam and
   identify every compared field, expected source, and mismatch category.
2. Produce exact counts and stable asset IDs for each mismatch category.
3. Determine whether the defect is in authored provenance, input binding,
   path/identity normalization, provisional full-page evidence, legacy-vs-v2
   field routing, or validator expectations. Do not infer; show source-backed
   evidence.
4. Reconcile all findings with the approved B1c4 invariants:
   - 16 exact Markdown-reference assets;
   - 100 visual-region assets;
   - 9 reviewed provisional full-page assets;
   - exact binary/provenance/replacement/migration identity;
   - `source_page` canonical routing with legacy `page` fallback only where
     compatibility requires it.
5. Specify one truthful reusable contract for builder and verifier. It must be
   scenario-independent, independently recomputable, fail closed, and must not
   trust the author projection as its oracle.
6. Define the minimum bounded engineering scope and symmetric positive/negative
   test matrix. Include attacks for path borrowing, digest borrowing, page/bbox
   substitution, provenance-kind substitution, provisional source-PDF identity,
   and comparison-evidence identity where applicable.
7. State the exact expected next public-v2 seam after B1c6, derived by a guarded
   in-memory or temporary-config diagnostic. Do not implement that later seam.
8. Confirm B1c5 remains unchanged and no canonical config/candidate/render is
   needed for B1c6.

## Forbidden actions

- No edits to author/builder/verifier or tests.
- No canonical `publication_config_v2.json`.
- No Candidate D, render/review bundle, MASTER_EN, MASTER_RU, HTML, or PDF.
- Do not modify/remove the nine protected historical candidate/staging roots.
- Do not change frozen source, reconstruction package, v1 config, plan,
  context, project status, or Git state.

## Deliverable

The immutable architecture receipt must include:

- role/ownership declaration and statement that no implementation was made;
- exact input/handoff hashes checked;
- call-path and field-level root cause;
- complete mismatch inventory with counts and stable IDs;
- approved-contract compatibility analysis;
- proposed generic schema/validation algorithm for both public implementations;
- exact engineering file scope and mutation matrix;
- exact next seam and stop boundary;
- risks, P0/P1/P2 architecture findings, and one terminal marker:
  - `READY_FOR_V2_COMPLETE_AUTHORING_PHASE_B1C6_ARCHITECTURE_REVIEW`, or
  - `CHANGES_REQUIRED_V2_COMPLETE_AUTHORING_PHASE_B1C6_ARCHITECTURE`.

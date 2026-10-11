# Immutable Independent Architecture Review Receipt — Stage A Page-Proof Topology Authorities

- Goal id: `20260809-stage-a-page-proof-topology-authorities`
- Step id: `2`
- Review kind: `architecture`
- Candidate state: non-frozen fixture-only proposed specification; this is not a release review.
- Role/model/effort: independent Terra critic / model platform-unverified / high.
- Implemented or materially designed candidate: **no**. This reviewer performed neither implementation nor material design.
- Orchestrator policy owner: `gpt-5.5` medium (platform-unverified). Orchestration ownership remains with the main-chat orchestrator.
- Assignment state: `platform-unverified`.
- Scoped override: `none`.

## Severity findings

### P0

None in the assigned architecture-only scope.

### P1

None.

### P2

None.

## Verdict

**ACCEPT — the fixture-only Stage A topology-authorities architecture is accepted.**

This acceptance is limited to the design contract for the two synthetic raw-authority fixtures. It neither accepts an implementation nor removes the page-proof coverage guard. It authorizes no live input, geometry/visibility/semantic/reading-order claim, source use, rebuild, publication, release or page-proof proof object.

## Files checked

- `kb_creator/docs/plans/20260809-stage-a-page-proof-topology-authorities/plan.md` — SHA-256 `3174BCA5BBA25CD211138336053E7DEA82F1820AAECEE7CD86CEA9AC88104586`
- `kb_creator/docs/plans/20260809-stage-a-page-proof-topology-authorities/context.md` — SHA-256 `75DE1F727B5516A2C641F9EF5AC33804C93B801F475B28E5AF869CD03558B131`
- `kb_creator/docs/plans/20260809-stage-a-page-proof-topology-authorities/handoffs/sol_stage_a_page_proof_topology_authorities_spec_20260809.md` — SHA-256 `23ECCF5ED32998D55EB0DBBCF73B2987FFA4D14DC0BEDD40361B7DE274EAB630`
- `kb_creator/pdf_raw/raw_authority_projection.py` — SHA-256 `8CE1CCF172C60CE63675E287061E688D2A0C39A80DE511263E851925A96B30A3`
- `kb_creator/pdf_raw/page_capable.py` — SHA-256 `15C8604F5293E1336F169CDB28EEC140404EC2612712B4A45E7E52756163A95E`
- Relevant page-proof architecture/guard handoffs:
  - `20260809-innsmouth-page-level-consumer-proof/handoffs/sol_page_level_consumer_proof_spec_20260809.md` — SHA-256 `44EF02B7BDFBA240733BBEDF6F4018313C32F6E312E48CAAEAFCE7FFC2E6DD24`
  - `20260809-innsmouth-page-level-consumer-proof/handoffs/sol_page_level_consumer_proof_p1_correction_20260809.md` — SHA-256 `5DC8DE4E51D653572C59FC8EBC62184725C5D7DB9FD3577CFFB2203FADAA131E`
  - `20260809-innsmouth-page-level-consumer-proof/handoffs/terra_page_proof_coverage_guard_signature_rereview_20260809.md` — SHA-256 `C1806CA08C4F66DD9F8E2617FE622A5D927B6B280710519C007B04F5DF87A876`

## Evidence

- **Stage A claim boundary:** every atom remains `geometry`, `visibility` and `semantic_role` equal to `unavailable_stage_a`. The two-column slot names are literal construction candidates; the assertion explicitly says geometry, visibility, semantic blocks and reading order are not proved. Form CTM is discarded before Stage A sealing. No render, witness, block or reading-order consumer path is introduced.
- **Registry and old-byte preservation:** the proposed four-row code-owned literal registry preserves the two baseline rows byte-for-byte and is independently matched against a primitive literal expected tuple before admission/open/extract. Every leaf, binding, canonical assertion and assertion hash is recomputed; row order, duplicates, cross-pairs and resealed substitutions are designated early failures. This is materially stronger than a mutable hash registry.
- **Two-column topology:** it requires two distinct, non-empty root streams and root frames, two text atoms/glyphs per slot, lexical root `/Contents` order, and the exact raw paint transition `B -> C` at atom ordinals `1 -> 2`. The specification consistently calls these slots candidates and defers actual placement, visibility, block membership and reading transition to later page-witness/visual review.
- **Nested Form topology:** the proposed closed normalization joins each Form invocation to its parent/target frame, `Do` token, form-resolution target and `form_do` atom; it requires one incoming edge per child, depth-first event order, exact child ownership and glyph continuity. The existing extractor already emits the needed raw frame, invocation, resolution, atom and token facts; the specified adapter normalizes only those facts and rejects or discards CTM/geometry.
- **Compatibility and scope:** the public Stage A APIs/wrapper remain unchanged. The specification confines implementation to `raw_authority_projection.py`, a focused fixture-only test and minimal existing Stage A test updates; it explicitly excludes `page_capable.py`, `page_proof.py`, live inputs, configuration, output and rebuild work. It preserves the two-row legacy authority registry and keeps its baseline matrix isolated.
- **Stale-hash resistance:** every negative must be valid in non-target invariants, use private surrogate expected seals where needed, and pass only after a target-only repair/reseal. The matrix covers valid-but-insufficient PDF shapes, fully resealed authority/assertion mutations, unknown-field smuggling, cross-pairs and assertion hash substitutions; pre-operation poison checks are required where applicable.
- No code or tests were run, and no live source, configuration, output, rebuild or Git operation was performed; this was a document/code-boundary architecture review.
- Freeze evidence: none. The plan marks this review in progress and the specification states implementation is not yet accepted; no candidate revision/manifest freeze was supplied. This is a point-in-time non-frozen receipt.

## Blockers, recommendation and next action

- Blockers: none for architecture acceptance. The two authorities, their literal hashes and independent topology-acceptance receipts do not yet exist.
- Recommendation: retain the contract as Stage A raw-provenance/paint topology only; reject any implementation that promotes slots/events into geometry, visibility, semantic blocks or reading order.
- Exact narrow implementation scope now permitted: modify only `kb_creator/pdf_raw/raw_authority_projection.py`, add the focused fixture-only topology-authorities test, and make only the minimal compatibility edits in the existing assigned `test_raw_authority_projection_stage_a_*.py` tests. The task may add exactly the two specified synthetic Stage A fixtures/assertions and their target-only QA. It must not edit `page_capable.py`, `page_proof.py`, page-proof tests/public state, canonical plan/context/status, live inputs, configuration, output, rebuild or release artifacts.
- Declared exclusions: no implementation by this reviewer; no code/test/canonical plan/context/status/release edit; no live Innsmouth input/output read or processing; no Git, network, rebuild or release operation.
- Invalidation: any mutation to the checked specification, the Stage A projection dependency or accepted page-proof contract invalidates this point-in-time receipt and requires a new independent architecture review.

## Receipt metadata

- Result: accepted architecture; bounded Stage A-only fixture-authority implementation may be separately authorized.
- Files changed: this immutable receipt only.
- Elapsed active time: approximately `5 minutes`.
- Token use: `unavailable`.
- Timestamp: `2026-08-09T21:06:38.0903498+03:00`.

This receipt does not transfer orchestration ownership.

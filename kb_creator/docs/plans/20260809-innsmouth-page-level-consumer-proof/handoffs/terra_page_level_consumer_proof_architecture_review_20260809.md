# Immutable Independent Review Receipt — Page-Level Consumer/Proof Architecture

- Goal id: `20260809-innsmouth-page-level-consumer-proof`
- Step id: `3`
- Review kind: `architecture`
- Candidate state: non-frozen proposed specification; this is not a release review.
- Role/model/effort: independent Terra critic / model platform-unverified / high.
- Implemented or materially designed candidate: **no**. This reviewer performed neither implementation nor material design.
- Orchestrator policy owner: `gpt-5.5` medium (platform-unverified). Orchestration ownership remains with the main-chat orchestrator.
- Assignment state: `platform-unverified`.
- Scoped override: `none`.

## Verdict

**REJECT — remediation required before fixture-only implementation is authorized.**

The proposed public API has no direct input path for a live or arbitrary PDF, and its later live-preflight and source-repair boundaries are appropriately separate in concept. However, three P1 contract gaps mean an implementation can either claim a fixture proof without a non-bypassable complete-topology gate, or accept manual witness decisions without enough independently bound visual cross-check evidence. No live preflight, source repair, rebuild, or release action is authorized.

## Files checked

- `kb_creator/docs/plans/20260809-innsmouth-page-level-consumer-proof/plan.md` — SHA-256 `4AF3886007538FE400DCD2D9E724A02E55E41A26E1E02D53DD4EF8BB79F1ED3E`
- `kb_creator/docs/plans/20260809-innsmouth-page-level-consumer-proof/context.md` — SHA-256 `6AB229B7D98101B693D7C2F637FE554341D2A0302E01CC624E821A2D032D992F`
- `kb_creator/docs/plans/20260809-innsmouth-page-level-consumer-proof/handoffs/sol_page_level_consumer_proof_spec_20260809.md` — SHA-256 `44EF02B7BDFBA240733BBEDF6F4018313C32F6E312E48CAAEAFCE7FFC2E6DD24`
- `kb_creator/docs/plans/20260808-innsmouth-systemic-todo-execution/handoffs/terra_raw_authority_projection_stage_a_p1_faithful_topology_final_review_20260809.md` — SHA-256 `71AEBDB9722E3EEBD7A9CDDB36311239AAAC5B75D6848BE1BB7B48EB98169DC9`
- `kb_creator/pdf_raw/page_capable.py` — SHA-256 `15C8604F5293E1336F169CDB28EEC140404EC2612712B4A45E7E52756163A95E`
- `kb_creator/pdf_raw/raw_authority_projection.py` — SHA-256 `8CE1CCF172C60CE63675E287061E688D2A0C39A80DE511263E851925A96B30A3`
- `kb_creator/pdf_raw/source_reconstruction.py` — SHA-256 `799EBC6DE4D0EB44BB9B266760877D9506E967A30C699C8A60F65F862F4145DD`

## Evidence and assessment

- **Live/arbitrary-PDF ingress:** acceptable in the proposal. The only consumer inputs are an exact `RawAtomProvenanceAuthorityV1` plus admitted witness/PNG/review bytes; paths, file-like objects, arbitrary PDF bytes, configuration, callbacks, parser objects and source-reconstruction APIs are forbidden before decoding or parser use (Sol specification §§2.1, 3, 8, 13). The existing `page_capable.py` does accept PDF bytes and calls raw replay, but it is explicitly non-substitutable/prohibited; `source_reconstruction.py` remains an unconditional error shim.
- **Stage A limitation:** confirmed. `raw_authority_projection.py` has two literal single-page fixtures and its validator requires zero invocations; the accepted Stage A receipt records this as fixture-only and not a consumer/release decision. It cannot presently evidence two columns or nested Form.
- **Visible/occluded/text-layer-only/decorative policy:** conservative as specified. Eligibility requires `visible`, `content`, and `agrees_visible`; all occluded, text-layer-only, disagreement, decorative and visual-only dispositions are explicit and non-publication (§§4.2, 5, 7, 9).
- **Later live preflight:** conceptually separated and constrained to one frozen PDF/page, no writes, no config/network/subprocess/EN/output access, no persistence/rebuild, and pre/post identity checks (§10). It is not implemented or authorized here; a separately specified adapter and independently accepted preflight plan remain required.
- **Source repair:** narrow and non-transitive in concept. It requires a new immutable, page/block/fragment-specific admission; it disallows aliases, ranges, neighboring-page promotion and repair execution by this route (§11).
- **Freeze evidence:** none. `plan.md` calls the specification proposed and step 3 in progress; `context.md` says no implementation/live preflight/source change/rebuild is authorized. The checked planning bundle is untracked in the current worktree, so this is a point-in-time non-frozen review, not a revision/manifest freeze attestation.
- **QA:** no tests run; this assignment is document/code-boundary review only. The Stage A focused and aggregate test results quoted in its prior receipt are historical supporting evidence, not re-executed evidence for this review.

## Severity findings

### P0

None in the assigned architecture-only scope.

### P1

1. **Reading-flow membership is undefined in the closed witness schema.** `proposed_reading_order` requires all and only blocks where `in_reading_flow=true`, but `proposed_blocks[]` never defines that field; closed schemas reject unknown fields. Nor is a normative derivation stated from the visibility/decoration/publication axes, and exclusion reasons are not bound to a closed mapping. Therefore the exact permutation and the paragraph-adjacency universe are not mechanically decidable without an unstated rule. This fails the requirement for fully specified, non-heuristic reading order and paragraph adjacency.

2. **The Stage A complete-topology gate is internally ambiguous and is not specified as a public-proof admission invariant.** Section 2.2 permits a first implementation against the minimal current fixture while also saying missing required authorities must stop; §8 says all positive topologies are required before bounded implementation; §12 says only completion is blocked. None states which terminal states the minimal implementation may emit, nor requires every successful public proof to bind a literal topology-coverage inventory that includes accepted two-column and nested-Form authorities. A consumer can therefore return `fixture_proof_accepted_no_source_use` for the minimal fixture while the stated coverage gate remains incomplete. This is not sufficiently non-bypassable for the requested two-column/nested-Form coverage.

3. **The witness still functions as an insufficiently cross-checked manual answer key for visual transcription and review decisions.** Raster components are re-derived, but atom geometry, block grouping, visibility/decoration classification, reading-order choices, paragraph decisions and `visible_transcription_sha256` are supplied by the witness. The review attestation binds an aggregate evidence hash and general references only; it does not require a per-block/per-boundary independent visual-check record, nor bind a re-derived/transcribed visual comparison artifact to those decisions. A hash-only visible transcription cannot itself establish that the rendered fixture says what the witness claims. The named “independent visual/architecture review” is therefore a process statement rather than a replayable, decision-specific cross-check.

### P2

None.

## Minimal correction packet

Request a narrow Sol amendment or replacement specification only; do not implement code or alter the canonical plan/context.

1. Add a closed, mandatory `in_reading_flow` disposition to each block (or an equally closed derived rule), define its allowed relation to every status axis, and enumerate/bind every exclusion reason. Require the exact fragment universe used for adjacency to be derived from that disposition.
2. Resolve §§2.2/8/12 with one normative coverage rule: before any public accepted fixture-proof terminal state, the literal admission inventory must contain independently accepted Stage A authorities for every required positive topology, including two-column and nested Form; otherwise every derive/review/replay attempt returns `page_proof_stage_a_fixture_coverage_incomplete`. If a mechanics-only harness is retained, give it a distinct non-proof terminal state that cannot be attested as accepted.
3. Define the independent visual cross-check artifact and its binding: per block and paragraph boundary, record the reviewer’s checked render/component references, declared visual/text comparison result, and decision-specific digest. Require replay to verify that artifact against the admitted render, witness and evidence core; no hash-only transcription or aggregate attestation may confer publication eligibility.

## Blockers and next action

- Blocker: the three P1 specification defects above.
- Recommendation: keep the candidate non-frozen and reject implementation authorization until the minimal correction packet is independently reviewed and accepted.
- Next action: the orchestrator may authorize **only** the minimal specification-correction packet above and then request a new independent Terra architecture review of the amended immutable candidate. Fixture implementation, live preflight, source repair, rebuild and release remain unauthorized.
- Declared exclusions: no code/test/canonical-plan/context/status/release edit; no live Innsmouth input/output read or processing; no Git, network, rebuild or release operation.
- Invalidation: any mutation to a checked candidate document or boundary module invalidates this point-in-time receipt and requires a new independent review. Mutation of the future corrected specification likewise requires a new receipt.

## Receipt metadata

- Result: rejected pending the minimal correction packet; no implementation authorization.
- Files changed: this immutable receipt only.
- Elapsed active time: approximately `4 minutes`.
- Token use: `unavailable`.
- Timestamp: `2026-08-09T20:26:53.8812028+03:00`.

This receipt does not transfer orchestration ownership.

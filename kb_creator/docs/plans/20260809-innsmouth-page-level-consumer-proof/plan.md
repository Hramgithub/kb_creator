# Innsmouth Page-Level Consumer/Proof Plan

Goal id: `20260809-innsmouth-page-level-consumer-proof`

## Role Contract

- Contract: `nri-role-v1`.
- Policy orchestrator: `gpt-5.5`, `medium`; assignment state:
  `platform-unverified`.
- Sol: architecture and remediation specification, `high`.
- Terra: independent architecture/implementation criticism, `high`; engineering
  assistance only when not reviewing the same work, `medium`.
- Executor: bounded implementation and QA only after accepted specification,
  `gpt-5.4`, `low`.

## Resume Bundle — 2026-08-11 In-Place 4b.9 Salvage

- Scoped user decision: abandon byte-exact frozen 4b.9 baseline recovery
  because the required `tests/_page_proof_fixture_leaves.py` bytes are not
  locally available; treat the current seven-file state only as an unaccepted
  in-place fixture-only candidate.
- Orchestrator owner: `gpt-5.5`, `medium`, assignment state
  `platform-unverified`; scoped override: `none`.
- First delegated packet: Sol architect, `high`, specification only, expected
  artifact
  `handoffs/sol_page_proof_packet_4b9_in_place_salvage_spec_20260811.md`.
- Sol specification status: completed, SHA-256
  `A3F258D47343AD1112A85CD48ED873E1107E83A701BCC8610003CE157BF97BFC`;
  independent Terra/high architecture review first returned one P1, then a
  Sol hash-preimage clarification was accepted by fresh Terra/high re-review
  with no P0/P1/P2.
- Required review sequence: independent Terra critic, `high`, architecture
  review before any implementation; bounded executor only after accepted
  specification; different independent Terra critic, `high`, implementation
  review before `4b.9` can be marked accepted.
- Forbidden scope until the salvage contract is accepted: live Innsmouth PDF,
  EN source, KeeperBook, HTML, PDF, output/build, Git, network, production
  activation, public terminal results, release paths, and any partial rollback.

## Resume Bundle — 2026-08-11 Step 5 Read-Only Live Preflight Gate

- Starting evidence: Packet `4b.9` is independently accepted only as
  fixture-only private inventory reseal evidence; production roots and public
  terminal results remain inactive.
- Orchestrator owner: `gpt-5.5`, `medium`, assignment state
  `platform-unverified`; scoped override: `none`.
- Current authorization: specify and review the Step 5 read-only live preflight
  gate. This does not yet authorize reading or processing the live Innsmouth
  PDF, EN source, KeeperBook, HTML, PDF, output/build, Git, release, production
  activation, or public terminal result.
- First delegated packet: Sol architect, `high`, architecture/specification
  only, expected artifact
  `handoffs/sol_page_proof_step5_read_only_live_preflight_spec_20260811.md`.
- Required review sequence: fresh independent Terra critic, `high`,
  architecture review before any read-only live preflight executor is assigned.
  If accepted, a later executor packet must freeze exact live source identity,
  run only the specified read-only page preflight, write evidence, and require
  a separate Terra review before any repair class is admitted.

## Objective

Define and independently accept a fail-closed page-level consumer/proof
contract for the already accepted raw-PDF Stage A authority. It must be capable
of proving page block order and paragraph boundaries before those facts can
influence Innsmouth source reconstruction.

This bundle is a design boundary. It does not accept a live Innsmouth source,
does not mutate EN/Keeper/HTML/PDF, and does not authorize a rebuild.

## Work Order

| Step | Owner | Effort | Status | Definition of Done | Evidence | Next action |
| --- | --- | --- | --- | --- | --- | --- |
| 1. Record boundary and inputs | Orchestrator | medium | completed | Separate bundle links the accepted Stage A review and states no-live/no-mutation limits | `context.md`; Stage A Terra review | Request architecture specification only |
| 2. Specify page-level consumer/proof contract | Sol architect | high | completed | Defines evidence schema, page/block ledger, visible-vs-occluded policy, reading-order acceptance, no-side-effect preflight, and admission/rejection states | `handoffs/sol_page_level_consumer_proof_spec_20260809.md`; SHA-256 `44ef02b7...c2e6dd24` | Terra reviews the specification |
| 3. Independently review architecture | Terra critic | high | remediation required | Terra found P1 gaps in reading-flow membership, topology-coverage admission, and bound per-decision visual cross-check evidence; implementation remains prohibited | `handoffs/terra_page_level_consumer_proof_architecture_review_20260809.md` | Sol corrects only the three P1 contract gaps |
| 3a. Correct page-level consumer/proof P1 contract gaps | Sol architect | high | completed | Amended specification mechanically defines flow membership, blocks accepted proof until all required positive topologies are accepted, and binds a per-block/per-boundary visual cross-check artifact | `handoffs/sol_page_level_consumer_proof_p1_correction_20260809.md`; SHA-256 `5dc8de4e...adaa131e` | Terra re-reviews amended specification |
| 3b. Independently re-review corrected architecture | Terra critic | high | completed | Terra accepted all three P1 corrections and preserved fixture-only/no-live/no-parser constraints | `handoffs/terra_page_level_consumer_proof_p1_architecture_rereview_20260809.md` | Implement mandatory coverage guard only |
| 4a. Implement fixture-only public coverage guard | Terra engineer | medium | completed | All public APIs reject before touching every corrected-contract input while required topology authorities are absent | `handoffs/terra_page_proof_coverage_guard_signature_rereview_20260809.md`; focused `14 passed` | Open separate Stage A topology-authority fixture work |
| 4a-r. Correct coverage-guard public signatures | Terra engineer | medium | completed | All three public APIs include the visual cross-check argument in the accepted positions and prove pre-access failure for every argument | `handoffs/terra_engineer_page_proof_coverage_guard_signature_remediation_20260809.md`; focused `14 passed` | Independently accepted in 4a-rr |
| 4a-rr. Independently re-review corrected coverage guard | Terra critic | high | completed | Terra accepted exact corrected signatures, all-input pre-access fail-close and containment; guard remains no-proof until Stage A topology authority exists | `handoffs/terra_page_proof_coverage_guard_signature_rereview_20260809.md` | Open separate Stage A topology-authority fixture work |
| 4a-handoff. Open separate Stage A topology-authority bundle | Orchestrator | medium | completed | Separate bundle scopes only fixture authorities for two-column/nested Form; no live source/output path | ../20260809-stage-a-page-proof-topology-authorities/plan.md; both Terra acceptance receipts | Implement bounded fixture-only proof route |
| 4b.1. Validate literal Stage A topology inventory | Terra engineer + independent Terra critic | medium/high | completed | Code-owned, double-literal root validator preserves coverage-first failure until two independently accepted topology-review hashes exist; a private fully valid inventory reaches only the fixture-registry gate | `handoffs/terra_engineer_page_proof_topology_inventory_20260809.md`; `handoffs/terra_engineer_page_proof_topology_inventory_remediation_20260809.md`; `handoffs/terra_page_proof_topology_inventory_remediation_review_20260809.md`; focused `35 passed` | Implement fixture-admission foundation (4b.2); do not activate production inventory |
| 4b.2. Implement fixture-admission foundation | Executor/engineer | low/medium | completed | Closed literal leaf registry, independent expected tuple and fully resealed target-only matrix are independently accepted; public APIs remain coverage-first and production roots remain empty | `handoffs/executor_page_proof_fixture_admission_remediation_20260809.md`; `handoffs/terra_page_proof_fixture_admission_remediation_review_20260811.md`; focused `41 passed in 0.25s` | Implement bounded closed schemas/public-boundary packet `4b.3` |
| 4b.3. Closed schemas and public boundaries | Executor/engineer + independent Terra critic | low/medium/high | completed with recorded P2 process deviation | Closed canonical JSON/schema/type/error-precedence helpers and immutable capability wrappers are independently accepted; no proof object, PNG, geometry or terminal success | `handoffs/executor_page_proof_closed_schemas_20260811.md`; `handoffs/terra_page_proof_closed_schemas_review_20260811.md`; focused `50 passed` | Implement `4b.4` witness/render/component mechanics only |
| 4b.4. Witness, render and component mechanics | Executor/engineer + independent Terra critic | low/medium/high | completed with historical P2 | Remediation accepts canonical fractions and rejects PNG/IEND and zlib/deflate trailing bytes; positive fixture leaves remain literal, public coverage-first paths remain inert. | `handoffs/executor_page_proof_witness_render_components_remediation_20260811.md`; `handoffs/terra_page_proof_witness_render_components_remediation_review_20260811.md`; focused `56 passed` | Implement `4b.5` flow/adjacency only |
| 4b.5. Flow and adjacency mechanics | Executor/engineer + independent Terra critic | low/medium/high | completed | Remediation proves a literal 16/16 disposition-precedence matrix and literal, non-circular adjacency/boundary baselines; target-only repair returns to the independent baseline. | `handoffs/executor_page_proof_flow_adjacency_remediation_20260811.md`; `handoffs/terra_page_proof_flow_adjacency_remediation_review_20260811.md`; focused `77 passed` | Implement only the separately specified 4b.6 fixture-only packet. |
| 4b.6. Independent visual cross-check | Sol architect -> Terra engineer (scoped high override) -> separate independent Terra critic | high/high/high | completed; independently accepted | Canonical test-only layout has exactly 98 direct normalizer calls; exact target inventories and complete P/F AST-containment proof hold. P0/P1: none. Required seven-suite regression: `129 passed in 0.44s`. | `handoffs/executor_page_proof_visual_crosscheck_canonical_layout_high_p1_repair_20260811.md`; `handoffs/terra_page_proof_visual_crosscheck_canonical_layout_p1_repair_review_20260811.md`; `docs/debt.md#KB-DEBT-20260811-001` | Sol may specify only the next bounded fixture-only P0/P1 packet. |
| 4b.7. Witness-bound composition | Sol architect -> Terra engineer (scoped high override) -> separate independent Terra critic | high/high/high | completed; independently accepted | WitnessV3 provides closed canonical `flow_input`; private composition proves `W -> M -> E -> V` from existing derive leaves while public APIs remain coverage-first/no-result and production roots inactive. P0/P1: none; `py_compile` passed and exact eight-suite regression: `147 passed in 0.51s`. | `handoffs/sol_page_proof_packet_4b7_spec_20260811.md`; `handoffs/terra_page_proof_packet_4b7_architecture_review_20260811.md`; `handoffs/executor_page_proof_packet_4b7_high_recovery_20260811.md`; `handoffs/terra_page_proof_packet_4b7_high_recovery_review_20260811.md`; `handoffs/terra_page_proof_packet_4b7_high_recovery_review_correction_20260811.md` | Sol may specify only the next bounded fixture-only P0/P1 packet. |
| 4b.8. Fixture topology-acceptance identity closure | Sol architect -> independent Terra critics | high/high | completed; independently accepted | Two authoritative child fixture-only identities are read-only accepted: two-column `74ddca...6d6526`; nested Form `136489...cc503`. Production roots remain inactive and public routes stay inert. P0/P1: none; Stage A QA `15 passed`, `386 passed, 1 skipped`. | `handoffs/sol_page_proof_packet_4b8_spec_20260811.md`; `handoffs/terra_page_proof_packet_4b8_architecture_review_20260811.md`; `handoffs/terra_page_proof_packet_4b8_aggregate_acceptance_review_20260811.md` | Sol may specify only private inventory/reseal work; no production activation or live preflight. |
| 4b.9. Private authoritative inventory reseal | Sol architect -> Terra engineer -> separate independent Terra critic | high/medium/high | completed through in-place fixture-only salvage; independently accepted | The byte-exact baseline was unavailable, so the seven-file state was accepted only after new Sol/Terra salvage specification, implementation evidence, and fresh Terra implementation re-review. No live/source/output/build/Git/release path opened. | `handoffs/executor_page_proof_packet_4b9_high_recovery_20260811.md`; `handoffs/sol_page_proof_packet_4b9_baseline_recovery_spec_20260811.md`; `NEW_CHAT_HANDOFF_20260811.md`; see salvage rows below | Step 5 requires separate authorization and read-only live preflight review before any live consumer action. |
| 4b.9-salvage-arch-r. Clarify in-place salvage hash preimages | Sol architect -> independent Terra critic | high/high | completed; independently accepted | Exact independent inventory/root canonical-hash preimages are specified and accepted; prior P1 is closed. | `handoffs/sol_page_proof_packet_4b9_in_place_salvage_spec_20260811.md`; `handoffs/terra_page_proof_packet_4b9_in_place_salvage_architecture_review_20260811.md`; `handoffs/sol_page_proof_packet_4b9_in_place_salvage_hash_preimage_clarification_20260811.md`; `handoffs/terra_page_proof_packet_4b9_in_place_salvage_hash_preimage_architecture_rereview_20260811.md` | Assign one bounded fixture-only executor; then require a different fresh Terra/high implementation review. |
| 4b.9-salvage-impl. In-place fixture-only salvage implementation | Orchestrator takeover -> independent Terra critic | medium/high | completed; independently accepted | Implemented accepted fixture-only oracle after two no-progress executor stops; Terra second re-review found no P0/P1/P2. No live/source/output/build/Git/production/release path. | `handoffs/executor_page_proof_packet_4b9_in_place_salvage_20260811.md`; `handoffs/terra_page_proof_packet_4b9_in_place_salvage_implementation_rereview_2_20260811.md`; page-proof `159 passed`; Stage A `15 passed` and `386 passed, 1 skipped` | Step 5 may only start as a separate authorized read-only live preflight packet. |
| 5. Authorize and run one read-only live page preflight | Orchestrator + Terra critic | medium/high | pending | A selected page yields only an evidence package; no EN/output is modified | Frozen source identity, page proof, critic receipt | Admit only proven repair classes to the systemic TODO plan |
| 5-spec. Specify read-only live preflight gate | Sol architect -> independent Terra critic | high/high | completed; independently accepted as architecture only | Sol defined a fail-closed Step 5 gate; after one Terra P1 review, Sol clarified control-record sandbox authority, prerequisite-QA binding, and reproducible selection queue identity. Fresh Terra re-review found no P0/P1/P2. | `handoffs/sol_page_proof_step5_read_only_live_preflight_spec_20260811.md`; `handoffs/terra_page_proof_step5_read_only_live_preflight_architecture_review_20260811.md`; `handoffs/sol_page_proof_step5_read_only_live_preflight_p1_clarification_20260811.md`; `handoffs/terra_page_proof_step5_read_only_live_preflight_architecture_rereview_20260811.md`; final SHA-256 `5BD2934B94D17573CB160ED9647C1BC79EA64C3199ADEE930036A6144403B67E` | Only a separately specified non-live adapter implementation packet or blocker-remediation packet may follow; Step 5A/5B live execution remains unauthorized. |

## Hard Boundaries

- No read or processing of the live Innsmouth PDF during Steps 1-3.
- No use of EN source, KeeperBook, HTML, PDF, scenario configuration, or
  output directories as consumer input during Steps 1-3.
- No code changes outside `kb_creator/pdf_raw/` and fixture-only tests until
  Step 3 is independently accepted.
- No promotion from raw atoms to accepted text order without a page/block proof
  ledger that records source identity, page identity, block geometry, content
  order, decision state, and review evidence.
- A page whose printed visual content and PDF text layer disagree must be
  classified as `occluded_text_layer_recovered_content` or another explicit
  non-publication state; it cannot become ordinary source body by default.

## Pause Snapshot — 2026-08-09

The prior pause ended with independent Terra acceptance of `4b.2-r` on
2026-08-11. The bundle is now active at `4b.3`; no live Innsmouth input,
source reconstruction, KeeperBook, HTML, PDF, configuration, output, Git
operation or release activity is authorized.

## Superseding result — 2026-08-26

The later branch completed the English reconstruction and user-review repair.
The accepted immutable result is now stored in the repository at
`kb_creator/inputs/innsmouth/master_en/packet7_user_review_20260826/`.
Independent release verdict:
`ACCEPT_PACKET7_USER_REVIEW_SUCCESSOR_RELEASE_ADMISSION`, P0/P1/P2 none.

This historical page-proof goal is closed for MASTER_EN. The active successor
goal is `../20260826-innsmouth-direct-master-ru-publication/`, whose pipeline is
strictly `accepted MASTER_EN -> new MASTER_RU -> HTML -> PDF` and excludes all
historical RU bridge material.

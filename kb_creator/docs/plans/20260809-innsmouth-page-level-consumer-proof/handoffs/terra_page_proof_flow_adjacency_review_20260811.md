# Immutable Independent Implementation Review Receipt — Packet 4b.5

- Goal id: `20260809-innsmouth-page-level-consumer-proof`
- Step id: `4b.5`
- Review kind: `implementation`; this is not a release review or freeze attestation.
- Candidate state: non-frozen, fixture-only Packet 4b.5 flow/adjacency candidate.
- Role: Terra independent critic; requested effort `high`.
- Actual model/effort: `platform-unverified`.
- Implemented or materially designed candidate: **no**. This critic performed neither.
- Orchestrator policy owner: `gpt-5.5` at `medium` (`platform-unverified`); orchestration ownership remains with the main-chat orchestrator.
- Assignment state: `platform-unverified`.
- Scoped override: none.
- Scope: independent review of Packet 4b.5 only. No candidate code/test/plan/context/status/Git mutation; no web/network/browser, live data, source/output/configuration, filesystem/PDF/parser/PIL, subprocess, page-capable, Stage A constructor/replay, or public-proof work.

## Verdict

**Rejected — P1 remediation required.**

The private implementation has a coherent fail-closed design, preserves paint order rather than sorting x/y, derives fragments from included blocks, validates exact adjacency ordering, and computes a non-circular private pre-visual digest. However, the mandatory evidence does not prove all flow-status combinations and uses a test helper that reproduces the SUT's adjacency algorithm for positive/repair baseline generation.

## Files checked

- Packet authority, section 5 / row 4b.5: `kb_creator/docs/plans/20260809-innsmouth-page-level-consumer-proof/handoffs/sol_page_proof_implementation_packetization_20260809.md`.
- Executor receipt: `kb_creator/docs/plans/20260809-innsmouth-page-level-consumer-proof/handoffs/executor_page_proof_flow_adjacency_20260811.md` — SHA-256 `164E9836062579A1B2FF0848ACE856A0A215F848FFD8C39CDB24D094C70F2708`.
- Prior Packet 4b.4 remediation acceptance: `kb_creator/docs/plans/20260809-innsmouth-page-level-consumer-proof/handoffs/terra_page_proof_witness_render_components_remediation_review_20260811.md`.
- `kb_creator/pdf_raw/page_proof.py` — SHA-256 `661F11E552FC94F05CA61B1DC21F45DB34A3B504A9587A7BE037E94829EAAFFE`.
- `kb_creator/tests/test_page_proof_flow_adjacency.py` — SHA-256 `31CC62DF3C587AB0BABA3BD0E7E66C2954D8192339B34214FFC2C3624530C1BE`.
- `kb_creator/tests/_page_proof_fixture_leaves.py` — SHA-256 `9B839FD9FF9E3FCAB3F1A44CA488BC2A5DEA49995B588D358C279DFF2837BFE7`; unchanged and literal-only.
- Existing fixture-only coverage, topology, admission, closed-schema, and witness/render tests as named in the mandated command.

## Test evidence

The only test suite run was the mandated fixture-only command:

```powershell
& 'D:\NRI\.tools\python-3.13.14\python.exe' -B -m pytest -q -p no:cacheprovider kb_creator/tests/test_page_proof_coverage_guard.py kb_creator/tests/test_page_proof_stage_a_topology_inventory.py kb_creator/tests/test_page_proof_fixture_admission.py kb_creator/tests/test_page_proof_closed_schemas.py kb_creator/tests/test_page_proof_witness_render_components.py kb_creator/tests/test_page_proof_flow_adjacency.py
```

Result: `65 passed in 0.18s`.

### P0

None.

### P1

- **Total precedence coverage is incomplete.** `_derive_reading_flow_disposition()` has four independent boolean status inputs, hence 16 possible flag combinations. `test_reading_flow_disposition_precedence_is_total_and_reasoned` supplies only five cumulative rows: all false; running only; running+occlusion; running+occlusion+disagreement; all true. It does not prove cases where a higher-priority flag is set while any lower-priority flags vary independently (for example visual-only alone, disagreement alone, occlusion alone, visual-only plus arbitrary lower statuses). Packet 4b.5 explicitly requires all precedence rows/status combinations. Add a literal 16-row expectation matrix (or its full equivalent) with exact disposition and reason, rather than deriving expected values through the function under test.

- **Adjacency target-only/repair evidence is helper-circular.** `_adjacency_from_included()` in the test suite reconstructs the same adjacent-fragment and boundary-kind algorithm as `_normalize_fixture_block_flow_adjacency()`: it uses consecutive included fragments, same-block/column comparisons, and the same three boundary labels. `_flow_input()` uses it to create every positive baseline, and the shuffled/missing/extra/non-adjacent attacks mutate that helper-produced baseline before returning to it as the claimed repair-positive. A common derivation defect can therefore make both helper and SUT agree. Replace at least one complete positive topology with independently literal blocks, included/excluded partitions, fragment universe, and exact adjacency/boundary rows; then conduct target-only mutations and explicit repairs from that independent baseline. Preserve the existing negative cases as supplementary evidence.

### P2

None. The executor reports no process/scope deviation for this packet; static inspection confirms no newly introduced forbidden dependency.

## Confirmed implementation properties

- `_normalize_fixture_block_flow_adjacency()` enforces closed root/block/flag/adjacency keys, exact types, block ordinal/order, unique atom/component/fragment assignments, full paint-order atom conservation, full component conservation, and exact declared included/excluded partitions.
- Production derives disposition in required order: visual-only, text-layer disagreement, occlusion, running marginal, then included. It consumes only block flow flags and normalized mechanics' atom/component identities; it does not inspect x/y/bbox geometry or perform coordinate sorting. Stage A paint order is retained only as `paint_order_atom_row_ids` and must equal the flattened block atom sequence.
- The fragment universe is created only from included blocks. Expected adjacency is consecutive fragment order only; canonical row equality and cardinality reject shuffled, missing, extra, and non-adjacent caller rows. The pre-visual hash commits a canonical summary that excludes its own digest and all later visual/review/terminal data, so no circular or unsafe source is present.
- Production registries remain inactive. Public derive/review/replay still call the coverage gate first and, under current production state, raise only `page_proof_stage_a_fixture_coverage_incomplete` before caller access; no visual-check, review, terminal, or proof-like public output is introduced.
- Static containment is unchanged: only stdlib/dataclass/hash/JSON/regex plus `RawPdfError` and exact authority-class import; no fixture-helper mutation, filesystem, PDF/parser/PIL/renderer, network/web/browser, subprocess, page-capable, Stage A construction/replay, live input, or Git dependency.

## Blocker and next action

- Remediation required: add an independent all-combination precedence matrix and at least one independent literal adjacency/boundary baseline with real target-only mutation/repair evidence; then request a new narrow Packet 4b.5 independent remediation review. Do not start Packet 4b.6 from this rejected evidence.
- Standing independent blocker: accepted `fixture_topology_acceptance` review-content hashes remain absent, so production coverage/admission stays inactive and public routes remain unavailable.

## Timing and immutability

- Files changed: none. The only filesystem write by this review is this required immutable receipt.
- Elapsed active time: `56 seconds` at evidence capture.
- Token use: `27,202` reported by the platform runtime goal at evidence capture.
- Timestamp: `2026-08-11T13:00:46.1563030+03:00`.

This is an immutable point-in-time implementation-review receipt. It does not transfer orchestration ownership and is not release acceptance, freeze attestation, or authorization to activate production coverage.

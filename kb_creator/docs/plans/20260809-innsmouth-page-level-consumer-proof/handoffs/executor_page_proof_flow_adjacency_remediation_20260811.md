goal_id: 20260809-innsmouth-page-level-consumer-proof
step_id: 4b.5-r
role: gpt-5.4 bounded executor
effort: low
assignment_state: platform-unverified
scoped_override: none
timestamp: 2026-08-11T13:06:09+03:00
tokens: unavailable

Summary
- Remediated only the two Terra P1 evidence defects for Packet 4b.5.
- No SUT defect was exposed, so `kb_creator/pdf_raw/page_proof.py` was not changed.
- Replaced helper-circular test baselines with explicit literal oracles and added full 16/16 precedence evidence.

P1 remediation mapping
1. Full precedence evidence
   - Added explicit literal `_PRECEDENCE_MATRIX` covering all 16 boolean combinations of:
     - `visual_only`
     - `text_layer_disagreement`
     - `occluded`
     - `running_marginal`
   - Each row asserts the exact `(reading_flow_disposition, reason)` returned by the SUT.
   - Expected outcomes are declared literally; they are not produced by a helper and are not derived from the SUT.
2. Non-circular adjacency/repair evidence
   - Removed the prior helper-circular adjacency baseline generation.
   - Positive and repair baselines now use explicitly written literal `adjacency_rows`, `included_block_ids`, `excluded_block_ids`, and expected fragment sequences.
   - Added a direct source-inspection assertion proving the test file contains no `_adjacency_from_included` helper and no `for index in range(len(included)` adjacency-derivation loop.

Literal baseline / non-circularity
- The test module no longer contains any helper that computes adjacency from included fragments.
- Positive adjacency rows are written as literal dict sequences.
- Repair-positive assertions return to those literal baselines rather than to an algorithmically rebuilt expected value.
- The 16-row precedence table is a fixed literal tuple, not a generated or mirrored precedence helper.

Changed files
- `D:\NRI\kb_creator\tests\test_page_proof_flow_adjacency.py`
- `D:\NRI\kb_creator\docs\plans\20260809-innsmouth-page-level-consumer-proof\handoffs\executor_page_proof_flow_adjacency_remediation_20260811.md`

Checked files
- `D:\NRI\kb_creator\docs\plans\20260809-innsmouth-page-level-consumer-proof\handoffs\terra_page_proof_flow_adjacency_review_20260811.md`
- `D:\NRI\kb_creator\docs\plans\20260809-innsmouth-page-level-consumer-proof\handoffs\sol_page_proof_implementation_packetization_20260809.md`
- `D:\NRI\kb_creator\tests\test_page_proof_flow_adjacency.py`
- `D:\NRI\kb_creator\pdf_raw\page_proof.py`

Implementation changes
- None.
- `kb_creator/pdf_raw/page_proof.py` was intentionally left unchanged because remediation exposed no real functional P1 defect in the SUT.

Evidence
- File SHA-256:
  - `D:\NRI\kb_creator\tests\test_page_proof_flow_adjacency.py`: `301A064D8FBA1F837E84AEB9A987F5D89ADA0348CA29B7E1EFF99F1CC6B14D75`
- Focused test command:
  - `& 'D:\NRI\.tools\python-3.13.14\python.exe' -B -m pytest -q -p no:cacheprovider kb_creator/tests/test_page_proof_coverage_guard.py kb_creator/tests/test_page_proof_stage_a_topology_inventory.py kb_creator/tests/test_page_proof_fixture_admission.py kb_creator/tests/test_page_proof_closed_schemas.py kb_creator/tests/test_page_proof_witness_render_components.py kb_creator/tests/test_page_proof_flow_adjacency.py`
- Exact result:
  - `77 passed in 0.18s`

16/16 matrix evidence
- The literal precedence matrix contains all sixteen status combinations.
- Baseline row:
  - `(False, False, False, False) -> ("included", "included")`
- Highest-priority row:
  - `(True, True, True, True) -> ("excluded", "visual_only")`
- Every intermediate combination is asserted explicitly in the matrix.

Scope/process deviations
- None in this remediation.
- No web/network/browser use.
- No fixture helper changes.
- No filesystem/path/PDF/parser/PIL/subprocess/page_capable/Stage A constructor/replay/live data/Git work.

Blocker
- No new 4b.5-r-local blocker.
- Standing production activation blocker remains unchanged: production topology acceptance is still intentionally incomplete, so public APIs remain coverage-first and fail closed before caller input access.

Next action
- Fresh independent Terra review for Packet 4b.5-r only.

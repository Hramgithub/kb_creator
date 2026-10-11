# Executor restart receipt — 4b.6-r-exact-evidence-restart-1

- Timestamp: 2026-08-11T15:19:42.1823466+03:00
- Policy owner / assignment / scoped override: NRI governance; Terra engineer at medium; bounded implementation only, no acceptance authority. Writes were limited to `kb_creator/tests/test_page_proof_visual_crosscheck.py` and this new receipt.
- Changed paths:
  - `kb_creator/tests/test_page_proof_visual_crosscheck.py`
  - this receipt
- Test SHA-256 before/after:
  - visual-crosscheck before: `7FE49A905B77A384A4EFD3638F7149CC95D47DB17665A9A8AB5EE3826C1C0917`
  - visual-crosscheck current: `323453E3AD3FFC1321ADCD43618163B2F0E33E1172259E4AC5B6566E9B84C239`
  - fourth-literal helper unchanged: `EC6E5FBC5252F4BD094A6ED263668D002C413364057D360819217D530296B3AA`
- Production SHA-256 before/after: `kb_creator/pdf_raw/page_proof.py` = `A6E5E647A6B973772D6690775EC78F30FBDA909CBB19F95D6A88A4BA9702870B`.
- Interpreter/version: `D:\NRI\.tools\python-3.13.14\python.exe`, Python 3.13.14.
- Exact command/result:
  ```powershell
  & 'D:\NRI\.tools\python-3.13.14\python.exe' -B -m pytest -q -p no:cacheprovider kb_creator/tests/test_page_proof_coverage_guard.py kb_creator/tests/test_page_proof_stage_a_topology_inventory.py kb_creator/tests/test_page_proof_fixture_admission.py kb_creator/tests/test_page_proof_closed_schemas.py kb_creator/tests/test_page_proof_witness_render_components.py kb_creator/tests/test_page_proof_flow_adjacency.py kb_creator/tests/test_page_proof_visual_crosscheck.py
  ```
  Result: `87 passed in 0.33s`.
- Evidence added: the pre-normalizer helper is now keyword-only and checks independent P/F anchors, supplied W/render metadata, canonical V bytes, closed V2 root keys/schema, and the 15 predicate keys; fourth duplicate uses literal final boundary row 1; aggregate-like rows are shape-valid `f0 -> f2`; AST checks now cover transitive P/F fields and prohibited dynamic constructs.
- Literal fourth identifiers: `INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1`; `TWO_BOUNDARY_V1_LENGTHS`; `TWO_BOUNDARY_V1_SHA256`; `TWO_BOUNDARY_PRE_VISUAL_BINDING_SHA256`; `TWO_BOUNDARY_FINAL_BINDING_SHA256`; `TWO_BOUNDARY_EXPECTED_CONTENT_SHA256`; `TWO_BOUNDARY_EXPECTED_PRE_VISUAL_CORE_SHA256`.
- Blockers / next action: **not reviewable yet.** Generated `_expected_vector(...)` mappings and retained legacy helper/direct-normalizer paths remain, so the exact per-call literal-vector and immediate-predecessor rule is not closed. The restored executable regression families preserve coverage but have not been migrated. The required remaining action is test-file-only unrolling/migration of those paths; do not claim acceptance.
- No Git, production change, live PDF/source/output/Keeper/HTML/PDF/rebuild, browser, network, registry activation, or Packet 4b.7 action was performed.
- Elapsed/token use: active restart work approximately 11 minutes; exact executor token use unavailable.

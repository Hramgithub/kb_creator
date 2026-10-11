# Executor receipt — 4b.6-r-exact-evidence

- Timestamp: 2026-08-11T15:06:11.7698163+03:00
- Policy owner / assignment / scoped override: NRI governance; Terra engineer at medium; engineering implementation only. Scoped write authority was limited to the two listed test files and this receipt. No scoped override of public fail-close behavior, inactive registry, or production code was used.
- Changed paths:
  - `kb_creator/tests/_page_proof_fixture_leaves.py`
  - `kb_creator/tests/test_page_proof_visual_crosscheck.py`
  - this immutable receipt
- Test-file SHA-256 before this recovery pass: unavailable — the delegated workspace entered with uncommitted prior-packet edits and the packet forbids Git/history operations. This receipt does not infer or fabricate pre-pass hashes.
- Test-file SHA-256 immediately before the final legacy-vector tightening: `_page_proof_fixture_leaves.py` = `EC6E5FBC5252F4BD094A6ED263668D002C413364057D360819217D530296B3AA`; `test_page_proof_visual_crosscheck.py` = `1BC2B92FDBE3AA87915CEACCD851A523059BF0CF99AC8C8205BDA02119970714`.
- Test-file SHA-256 after this recovery pass:
  - `_page_proof_fixture_leaves.py`: `EC6E5FBC5252F4BD094A6ED263668D002C413364057D360819217D530296B3AA`
  - `test_page_proof_visual_crosscheck.py`: `7FE49A905B77A384A4EFD3638F7149CC95D47DB17665A9A8AB5EE3826C1C0917`
- Frozen production hash before and after: `kb_creator/pdf_raw/page_proof.py` = `A6E5E647A6B973772D6690775EC78F30FBDA909CBB19F95D6A88A4BA9702870B`.
- Interpreter/version: `D:\NRI\.tools\python-3.13.14\python.exe`, Python 3.13.14.
- Exact command/result:
  ```powershell
  & 'D:\NRI\.tools\python-3.13.14\python.exe' -B -m pytest -q -p no:cacheprovider kb_creator/tests/test_page_proof_coverage_guard.py kb_creator/tests/test_page_proof_stage_a_topology_inventory.py kb_creator/tests/test_page_proof_fixture_admission.py kb_creator/tests/test_page_proof_closed_schemas.py kb_creator/tests/test_page_proof_witness_render_components.py kb_creator/tests/test_page_proof_flow_adjacency.py kb_creator/tests/test_page_proof_visual_crosscheck.py
  ```
  Result: `87 passed in 0.33s`.
- Literal fourth-case IDs/hashes: `INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1`; `TWO_BOUNDARY_V1_LENGTHS=(33,2227,119,2928)`; leaf SHA-256 tuple `e40137c0f1597d0a7b4aac30969a521e40c28d8019f02be2c10e21593dc127c9`, `86e53083f7c1710c30426937289d7cd23ad44858bb498ffa051c510a734f1744`, `10ed1f66fb1f4022051d3c3b0deca071fabe5c3f10a6673872655ed49d4d91a3`, `957801aad384374fec37030c89a3df18979067078705bf872fc6fdd363da7f49`; P=`6af03e4f7dc076d2435b9da0c735940a4369566c57babc67abeabd121df69e35`; F=`cdfb4dc88aa7acb25f3964cc727ea18e0dbe1b681fc89ba6771ea78457813b8c`; content=`999d349cc2d0b7878f5a390262ef9188eea8555895d8034ed080c73715102dc7`; pre-visual core=`2115d29b5c221e814c53fcd800b1083427c91653622b469ea657e476c118bdb7`.
- Predicate vectors/pre-normalizer evidence: `_assert_pre_normalizer_contract` directly evaluates the named 15 predicates using `(row, witness, render, V, mechanics, flow)` before normalization. Its independent named vector oracle uses aligned-prefix `all(...)` evaluation for block and boundary groups. Every retained legacy normalizer path now enters that evaluator; single-failure cases assert the complete 15-key target vector and the aggregate case asserts its exact two-false cardinality/inventory vector. The literal-two-boundary P1 matrix inverse-repairs the same parsed tree, reseals with the independent final-binding oracle, proves the literal baseline bytes, and asserts all 15 true before normalization.
- Matrix count: 3 existing positive cases + 1 literal two-boundary positive case; fourth-fixture P1 matrix = 38 adversarial/repaired rows (7 root/reviewer/content, 4 structural, 16 block variants, 8 boundary-region variants, 3 boundary decisions); retained legacy negative/repaired cases also execute the full vector evaluator.
- Static containment: source-derived AST checks cover the six P/F functions, expected call graph, P field exclusion, hash-domain literals, literal fourth-leaf assignments, and absence of final binding in public root key sets. The test-side final binding is independently sealed with `_oracle_final_admission_binding_sha256`.
- Blockers / next action: no implementation blocker remains within the scoped write set. The P1 evidence remediation is ready for a fresh independent Terra review; this receipt is engineering evidence, not a release acceptance. Next action: independent review of the two permitted test files and this receipt.
- Elapsed/token use: active implementation elapsed approximately 18 minutes; token use unavailable from the delegated executor surface.
- No commit, network, browser, production registry activation, PDF/source/output/rebuild, or production-file edit was performed.

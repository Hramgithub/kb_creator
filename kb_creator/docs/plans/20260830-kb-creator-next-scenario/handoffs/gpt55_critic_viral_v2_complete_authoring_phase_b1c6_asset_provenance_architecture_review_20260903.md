# GPT-5.5 critic receipt - Viral v2 B1c6 asset-provenance architecture review

## Receipt metadata

- Goal id: `20260830-kb-creator-next-scenario`.
- Step id: `7-v2-complete-publication-authoring / B1c6-asset-provenance-input-binding / architecture-review`.
- `review_kind`: `architecture`.
- Candidate state: non-frozen architecture checkpoint; no canonical v2 config, built `MASTER_EN`, candidate, render/review bundle, HTML, PDF, release candidate, or release manifest was reviewed.
- Implemented or materially designed candidate: no. I did not implement, redesign, or edit candidate implementation/tests.
- Role: fresh independent `gpt-5.5` / high critic.
- Actual platform model / effort: unavailable.
- Orchestrator policy owner: main chat `gpt-5.6-sol` / medium. Orchestration ownership did not transfer.
- Assignment state: matched to the assigned B1c6 architecture review packet; platform runtime identity remains unverified.
- Scoped override: exact task packet `TASK_PACKET_gpt55_critic_viral_v2_complete_authoring_phase_b1c6_asset_provenance_architecture_review_20260903.md`, expected and observed SHA-256 `8D7BBA7934CC77DA16BAC6830E178DA4230F578A9842D91DE6C81B5E1D55DC46`.
- Timestamp: `2026-09-03T19:09:29.7405362+03:00` Europe/Moscow.
- Elapsed time: 289 seconds tracked before receipt write; approximately 6 minutes wall-clock to receipt draft.
- Token use: 149547 tracked before receipt write; exact final platform total otherwise unavailable.
- Files changed: only this immutable review receipt.

## Files checked

- `docs/governance/nri_goal_governance.md`.
- Assigned review packet: `TASK_PACKET_gpt55_critic_viral_v2_complete_authoring_phase_b1c6_asset_provenance_architecture_review_20260903.md`, SHA-256 `8D7BBA7934CC77DA16BAC6830E178DA4230F578A9842D91DE6C81B5E1D55DC46`.
- Architecture packet under review: `TASK_PACKET_architect_viral_v2_complete_authoring_phase_b1c6_asset_provenance_binding_20260903.md`, SHA-256 `88B45E9F986E06B5BB73CF5756DA54A8CFB860C999EC028E54F57E6A1E863B98`.
- Architecture receipt under review: `sol_architect_viral_v2_complete_authoring_phase_b1c6_asset_provenance_binding_20260903.md`, SHA-256 `B37F37EF54885AEC1CFC4CEF557D31D326E603D5EA70F9BEA919C42C18162E5C`.
- B1c4 prerequisite critic approval: `gpt55_critic_viral_v2_complete_authoring_phase_b1c4_asset_identity_rereview_20260903.md`, SHA-256 `BBB983ADD8E97885B0B9FCF0226145F262BD857127853F9CCC33706E82FC2EED`.
- B1c5 prerequisite critic approval: `gpt55_critic_viral_v2_complete_authoring_phase_b1c5_implementation_review_20260903.md`, SHA-256 `05B4573DF3FBE1EE7ACF31711AEFDBD44BB68A2448F90CDF494A332F4D649D82`.
- `kb_creator/scripts/author_viral_master_en_v2_config.py`, SHA-256 `3DA02ADF17E2224C86A1418D18ECB06754E1FC6CD628717C1652EA315968FE1C`.
- `kb_creator/scripts/build_scenario_master_en.py`, SHA-256 `8055F7B355EB711474398C84263521C4B8001D852B2B53987523D5CBE9C4D6DD`.
- `kb_creator/scripts/verify_scenario_master_en.py`, SHA-256 `2CFEE758C2EDBC5F445E864EDB46E366EB07E7E19D6E19FBD64D6A99E9FF2ED5`.
- `kb_creator/tests/test_author_viral_master_en_v2_config.py`, SHA-256 `58ED6C9FF6FC5A67130830F3F4731A5D68695E6F7E6877B0D6E09786D51D5EAE`.
- `kb_creator/tests/test_build_scenario_master_en.py`, SHA-256 `CE38BA49E996C414166F345D3127FC6303DEFD4949C5678D966F414D340B8555`.
- `kb_creator/tests/test_verify_scenario_master_en.py`, SHA-256 `61566BD4C76344CE36ACE6DC97FE94DD4E65A68176AACD21E8C11C28BFD195FA`.
- Source PDF `kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf`: 124 pages, SHA-256 `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05`.
- Accepted reconstruction package `kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4`: inventory `68C17FB765A89C6146398868E61F1F6EB7B2FE4EAFBA8C2C2C8F42260BBDBA83`.
- Package `ASSET_MANIFEST.json`: SHA-256 `914A2C8B46401830EDBDEADDDDA24C7A8C0B6442F2775C439A79CC5529D283E9`.
- Comparison evidence `comparison/comparison.json`: SHA-256 `5A4DB5DB697B1E483926AB1DAB387CB496EF0539DC76EAD51B830F5DCF1862F0`.
- Comparison companion input manifest `inputs/sample_pages.json`: SHA-256 `4BE80A51F01B552536B1D51C3F43ABA90EAD31D87006F8FBB3FD48DEC2A4182E`.

## Evidence and independent probes

- Hash verification matched every packet and prerequisite value listed above.
- `git status --short --branch` showed a broad pre-existing dirty/untracked worktree on `codex/kb-creator-viral...origin/codex/kb-creator-viral [ahead 1]`. I kept this review scoped to one new receipt and did not touch unrelated files.
- Builder call path confirmed: `preflight()` calls `v2_config()` then `v2_input_binding()`; `v2_config()` accepts canonical B1c4 rows at lines 445-489 and calls B1c5 `v2_visual_review_units()` at line 498; `v2_input_binding()` binds CLI source/package identities at lines 587-614, then calls `v2_a3_validate()`.
- Builder root cause confirmed: the deeper A3 asset loop at lines 265-271 still requires legacy top-level `source_span_ids`, `reader_value`, and `placement`, then requires span owner ids to equal final `asset_id`. The first predicate fails as `v2 asset provenance mismatch`.
- Verifier call path confirmed: `preflight()` calls `v2_contract()` then `v2_input_binding()`; `v2_contract()` accepts canonical B1c4 rows at lines 567-613 and calls B1c5 `v2_visual_review_units()` at line 624; `v2_input_binding()` binds CLI source/package identities at lines 719-744, then calls `v2_a3_validate()`.
- Verifier root cause confirmed: the independent A3 asset loop at lines 246-252 still requires the same legacy carrier and fails the first predicate as `E_V2_ASSET: provenance`.
- In-memory public-path check, without writing a temp config or output, reproduced the current seam after B1c4/B1c5 acceptance: builder `ValueError: v2 asset provenance mismatch`; verifier `ValueError: E_V2_ASSET: provenance`.
- Independent no-write probe over `author()` and immutable input files reproduced `asset_count=125`, provenance counts `100 visual_region / 16 markdown_image_reference / 9 reviewed_provisional_full_page`, `reader_missing_placement=93`, `unique_markdown_spans=16`, `errors=[]`, first missing reader placement `viral-accepted-ed4012725c597dbcf6fca51e55faeb883a53f6f1d2c9ee7496c667460d37c860`.
- Markdown-reference binding checked unique span ids, `owner_kind=asset`, `classification=asset_reference_source`, page equality, page Markdown identity, exact byte/character slice, marker hash, and resolved Markdown target equality to the declared binary path. The review agrees that final content-addressed `asset_id` must not be forced to equal the logical source-ledger `owner_id`.
- Visual-region binding checked binary digest, manifest row by `source_path` and digest, block lookup by `selected_view/raw_index`, block membership, block type, source page, and bbox. Representative manifest rows include both `source_path` and `stored_path`; the architecture's proposed path-plus-digest rule is needed to avoid either source-reference borrowing or stored-path borrowing.
- Comparison evidence stores an absolute device-specific `manifest.path`, while the companion `inputs/sample_pages.json` hash matches the declared `4BE80...182E` and its embedded source identity matches the CLI-bound PDF. The architecture correctly requires topology/basename/hash resolution instead of trusting the absolute path spelling.
- Provisional full-page pages 1, 106, 107, 112, 114, 116, 118, 120, and 122 have actual source PDF MediaBox `[0, 0, 612, 792]` and rotation `0`. The architecture correctly requires recomputing geometry/rotation from the CLI-bound PDF and validating the render recipe without rendering bytes or inventing output hashes.

## Architecture assessment

The stale-loop diagnosis is complete and source-backed. The failing public pair is not a B1c4 declaration-identity problem and not a B1c5 visual-review declaration problem; those gates pass before the A3 asset loop. The failing layer is legacy A3 asset input routing.

The homogeneous canonical-versus-legacy mode rule is required and correctly specified. The current validators already contain two incompatible asset shapes in the same public path; B1c6 must make mode selection row-shape based, all-canonical or all-legacy, and fail closed on mixed rows or canonical legacy aliases (`page`, `reader_value`, `source_span_ids`). Scenario-name based routing would be a downgrade path and the architecture rejects it.

The proposed Markdown contract preserves the exact 16 source-span bindings without falsely equating logical ledger owner ids with final content-addressed asset ids. Binding by unique span, exact page/range/marker hash, resolved Markdown target, and declared binary identity is the right contract boundary for B1c6.

The proposed visual-region contract closes the material borrowing classes: package path borrowing, digest borrowing, manifest-row borrowing, comparison-block borrowing, and companion-source-PDF borrowing. The only implementation caution is to bind both `stored_path` to the stored binary and `source_asset_reference` to the comparison block assets; using only one of those keys would miss a borrowing class.

The proposed provisional full-page contract is acceptable because it binds the declaration to the CLI source PDF, physical page/index, actual page geometry/rotation, and closed render recipe while intentionally avoiding a rendered output hash before candidate materialization.

The proposed algorithm is generic enough for B1c6 if implemented as independent builder and verifier helpers that derive from the CLI source PDF, reconstruction package, page rows, source partition, asset manifest, comparison evidence, and companion manifest. It must not compare canonical rows to `asset_b1c4_projection()`, `v2_b1c4_expected_assets()`, or any Viral-specific expected-row table for this B1c6 proof.

The four-file engineering scope is sufficient: `build_scenario_master_en.py`, `verify_scenario_master_en.py`, and their two focused test files. No author schema change, B1c5 change, canonical v2 config, candidate, render, `MASTER_EN`, output, plan/context/status edit, or release artifact is required for this checkpoint.

The expected next seam after successful B1c6 is exactly the not-yet-authored reader placement union: 93 reader assets lack placement. The intended post-B1c6 public pair is builder `v2 asset placement mismatch` and verifier `E_V2_ASSET: placement`; candidate materialization must remain unreachable.

The proposed symmetric mutation matrix covers the P0/P1 borrowing and masking classes I would require for this architecture: mixed-mode downgrade, legacy alias injection, path/digest swaps, donor binary/provenance swaps, Markdown span/range/marker/target swaps, manifest identity and row substitution, comparison identity/block/companion substitution, provisional PDF/page/region/recipe substitutions, page alias fallback, B1c4/B1c5 preservation, and no-output compatibility.

## Severity findings

- P0: none.
- P1: none.
- P2: none.

## Blockers

None for approving the B1c6 asset-provenance input-binding architecture.

This is not a release review. I did not verify a frozen release candidate revision or release manifest, freeze evidence, QA exclusion list, or mutation invalidation as a release gate. Any mutation after this non-frozen architecture checkpoint requires the normal implementation review path before acceptance.

## Recommendation

Approve the B1c6 architecture and assign the bounded four-file engineering implementation with the stated no-output stop boundary. Main-chat orchestration remains with `gpt-5.6-sol` / medium; this receipt does not transfer orchestration ownership.

APPROVED_V2_COMPLETE_AUTHORING_PHASE_B1C6_ARCHITECTURE

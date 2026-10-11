# Viral Step 7 reader-surface implementation review receipt

## Receipt metadata

- review_kind: implementation
- verdict: REJECT_IMPLEMENTATION
- reviewer role: independent critic, gpt-5.5, high
- implemented candidate: no
- materially designed candidate: no
- orchestration ownership: not transferred
- orchestrator policy owner: gpt-5.6-sol at medium, per AGENTS.md and docs/governance/nri_goal_governance.md
- assignment state: completed; rejection receipt written
- scoped override: none; this role assignment follows repository governance
- timestamp: 2026-09-02T03:04:37.9513698+03:00
- elapsed time: approx 32 minutes
- token use: unavailable; exact per-agent token accounting was not exposed

## Files checked

- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_orchestrator_viral_step7_reader_surface_implementation_review_assignment_20260902.md`
- `kb_creator/working/viral/master_en/publication_config_v1.json`
- `kb_creator/scripts/build_scenario_master_en.py`
- `kb_creator/scripts/verify_scenario_master_en.py`
- `kb_creator/tests/test_build_scenario_master_en.py`
- `kb_creator/tests/test_verify_scenario_master_en.py`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_step7_master_en_reader_surface_code_pass_20260902.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_viral_step7_master_en_reader_surface_remediation_20260902.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_orchestrator_viral_step7_master_en_reader_surface_asset_count_erratum_20260902.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_orchestrator_viral_step7_master_en_reader_alt_ordinal_erratum_20260902.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_orchestrator_viral_step7_master_en_reader_surface_suppression_erratum_20260902.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_orchestrator_viral_step7_reader_surface_hash_endpoint_correction_20260902.md`
- `AGENTS.md`
- `docs/governance/nri_goal_governance.md`

## Frozen input hashes verified

- Assignment packet: `4729A7FA803A219E571D06BD6A5810C2E6FE2F4554E2F1555F7953D710C61A4E`
- Publication config: `EEE2B0BBE8EB0F8862F09C884818B1C20C8DC023FCC01B504E963AFD3346438E`
- Builder: `3832B1F218C7F658E98660ADB9757BCA365F15A2A5A9C0677764992329C34051`
- Verifier: `C0544CFEA3D24E6B5F4501D9FADAF7B9C8B3D4F8A41C9238C9FE7A71C2753335`
- Builder tests: `E33A39DA0F9C53DD38A4EB89289717E6C9D3A99422CB704BC060F86589C5F259`
- Verifier tests: `B7D6822A44B06A87457DBE6B37F9CE97CC60E33083B2387C04C665402771B04F`
- Engineering PASS receipt: `AF6F2CA945E89768D9FE833D6010669DB6A59936F8F22E2B2174398B491045A4`

## Commands and results

- `Get-FileHash -Algorithm SHA256 ...assignment...` -> matched `4729A7FA...`
- `Get-FileHash -Algorithm SHA256 publication_config_v1.json build_scenario_master_en.py verify_scenario_master_en.py test_build_scenario_master_en.py test_verify_scenario_master_en.py terra...code_pass...` -> all six assignment hashes matched.
- `python -B -m unittest kb_creator.tests.test_build_scenario_master_en kb_creator.tests.test_verify_scenario_master_en` -> `Ran 53 tests in 27.767s`, `OK`.
- `python -B -m py_compile kb_creator/scripts/build_scenario_master_en.py kb_creator/scripts/verify_scenario_master_en.py` -> pass.
- `git diff --check -- kb_creator/scripts/build_scenario_master_en.py kb_creator/scripts/verify_scenario_master_en.py kb_creator/tests/test_build_scenario_master_en.py kb_creator/tests/test_verify_scenario_master_en.py kb_creator/working/viral/master_en/publication_config_v1.json` -> pass.
- `git status --short --branch` -> dirty worktree already contains modified governance/config files and many untracked kb_creator scripts/tests/handoffs; no staging or commit performed.
- `Get-ChildItem -Force kb_creator/working/viral/master_en/candidates` -> Candidate A and B exist; Candidate C is absent. Four dot-prefixed unittest staging roots are also present and were not cleaned.

## Evidence summary

- Builder closes the new config surface: `TOP` includes `reader_surface` at `kb_creator/scripts/build_scenario_master_en.py:10`; `RS_KEYS`, `SELECTOR_KEYS`, `reader_selector`, `reader_selector_end`, `reader_surface_ranges`, and `validate_reader_surface` close top-level and nested keys, selector combinations, positive occurrence, counts, hashes, and owner containment at `build_scenario_master_en.py:222-290`.
- Builder validates semantic ranges after normal binding resolution: `resolve_bindings` builds source claims, computes conservation, then calls `validate_reader_surface(c, package, {'bindings': resolved})` at `build_scenario_master_en.py:486-499`; semantic fragment ownership is checked against resolved `source_span_hashes` at `build_scenario_master_en.py:287-289`.
- Builder uses a single source transform path for emitted reader text, structured evidence, and sidecar conversion: `clean_span` removes locator edits and suppressions at `build_scenario_master_en.py:660-672`; `assemble_reader` passes `suppression_ranges` into `structured_resolver` at `build_scenario_master_en.py:726-776`; `sidecar_structures` serializes source/emitted char and UTF-8 byte ranges at `build_scenario_master_en.py:793-806`.
- Current config has the intended reader surface shape: keys `alt_policy`, `authorized_suppressions`, `heading_policy`, `schema_version`, `semantic_fragments`; 25 semantic fragments; 22 suppressions; 107 reader assets; 16 evidence-only assets; 123 total assets. Reader placement values are unique over the 107 reader assets but are not contiguous because evidence-only rows are interleaved, matching the ordinal erratum.
- Verifier has an independent locator/transform implementation and does not import the builder: `expected_binding_spans` states verifier-owned resolver at `verify_scenario_master_en.py:84-108`; tests check no builder import at `test_verify_scenario_master_en.py:17-18`.

## Severity findings

### P0

None found.

### P1-1: verifier does not independently enforce the frozen `reader_surface` public contract

Locus: `kb_creator/scripts/verify_scenario_master_en.py:25-31`, `verify_scenario_master_en.py:40-46`, `verify_scenario_master_en.py:138-149`, `verify_scenario_master_en.py:150-229`; `kb_creator/tests/test_verify_scenario_master_en.py:17-88`; architecture requirement at `sol_architect_viral_step7_master_en_reader_surface_remediation_20260902.md:328-337` and `:358-363`.

Impact: the implementation passes the focused suite, but the verifier never closes or validates `reader_surface.schema_version`, `semantic_fragments`, `heading_policy`, `alt_policy`, reader alt bans, or the 25/22/107 counts. Source occurrence counts confirm `verify_scenario_master_en.py` contains `reader_surface` once and only as `cfg.get('reader_surface', {}).get('authorized_suppressions', [])`; it contains zero `semantic_fragments` and zero `alt_policy` references. Both focused test modules contain zero `reader_surface`, `semantic_fragments`, `authorized_suppressions`, or `alt_policy` references. This fails required independent questions 1, 6, and 8 for the verifier side.

Minimal remediation: add verifier-owned closed schema and hash/owner/count validation for the complete `reader_surface` contract, without importing builder internals. Add negative verifier tests for unknown top-level/nested keys, invalid selector combinations, wrong semantic count/order/hash/owner, wrong suppression endpoint/hash, and alt policy leakage.

### P1-2: suppression evidence is not carried as a candidate-verifiable sidecar/public contract

Locus: `kb_creator/scripts/build_scenario_master_en.py:249-270`, `build_scenario_master_en.py:726-776`, `build_scenario_master_en.py:833-842`, `verify_scenario_master_en.py:138-149`, architecture requirement at `sol_architect_viral_step7_master_en_reader_surface_remediation_20260902.md:134` and `:344-345`.

Impact: the builder validates 22 configured suppression hashes and applies their endpoint ranges for deletion and structured transforms, but candidate provenance serialization includes `units` and `structured_units` only; the resolved suppression list returned from `assemble_reader` is not persisted as a closed candidate sidecar contract. The verifier therefore recomputes suppressions from the current config rather than verifying the candidate's own suppression evidence. This leaves later full-reader QA without a stable candidate-local suppression ledger and fails the requirement that suppressed raw text/hashes remain in provenance/sidecar evidence.

Minimal remediation: serialize a closed suppression evidence section with suppression id, source page, owner, resolved start/end char and byte ranges, raw SHA-256, disposition, replacement asset id, and emitted deletion/provenance relationship. The verifier should recompute those rows independently from immutable source pages and require exact equality.

### P2-1: verifier does not validate candidate provenance input identities

Locus: `kb_creator/scripts/build_scenario_master_en.py:841`, `kb_creator/scripts/verify_scenario_master_en.py:173-176`, `verify_scenario_master_en.py:229`.

Impact: the builder writes `provenance.inputs` with contract, publication config, source PDF, and accepted reconstruction identities, but the verifier only closes the existence of the `inputs` key and never validates nested input identities against current CLI inputs, the preflight result, or frozen hashes. The returned `publication_config_sha256` proves only the config passed to the verifier, not that the candidate provenance was produced from that same config. This weakens auditability and mutation invalidation.

Minimal remediation: close and validate `provenance.inputs` recursively. Require exact path/bytes/SHA equality for contract, publication config, source PDF, accepted reconstruction package identities, and builder script identity, and add resealed mutation tests that alter those nested values.

### P2-2: conservation accounting does not use authorized suppression ranges

Locus: `kb_creator/scripts/build_scenario_master_en.py:507-522`, `build_scenario_master_en.py:497-499`, architecture requirement at `sol_architect_viral_step7_master_en_reader_surface_remediation_20260902.md:134`.

Impact: `conservation_ledger` accounts line ownership and generated pages, then hardcodes `unauthorized_suppression_blocks` to `0`. It does not receive or compare the 22 authorized suppression ranges. The current config may still close by ownership, but the implementation does not prove the architecture's declared conservation equation: source tokens equal emitted semantic tokens plus generated-heading replacements plus source-image relocation plus authorized suppression ranges.

Minimal remediation: make conservation explicitly consume the resolved suppression ledger and fail on unaccounted deleted source blocks, duplicate suppression coverage, or suppression outside owned source spans. Add tests that remove or perturb one suppression and prove conservation or verifier rejects it.

### P3-1: focused tests are broad but omit the new reader-surface negative cases

Locus: `kb_creator/tests/test_build_scenario_master_en.py:21-237`, `kb_creator/tests/test_verify_scenario_master_en.py:17-88`, architecture test requirements at `sol_architect_viral_step7_master_en_reader_surface_remediation_20260902.md:358-363`.

Impact: the 53 tests cover many builder/verifier behaviors, but neither focused test module names or mutates `reader_surface`, `semantic_fragments`, `authorized_suppressions`, or `alt_policy`. This let P1-1 pass unnoticed.

Minimal remediation: add targeted builder and verifier tests for every new reader-surface nesting level and for Viral-specific regressions around evidence-only ordinals, banned alt text, suppression endpoints, and source/provenance hash mismatches.

## Blockers

- Candidate C must not open yet. Code remediation is required first because the verifier does not independently enforce the reader-surface public contract and the candidate does not persist suppression evidence as a verifier-owned sidecar contract.
- Two scratch builds may be useful after remediation, but authorizing them before these fixes would not answer the independent verifier requirement.
- No release approval is implied by this implementation review.

## Required question answers

1. Builder: yes for the new reader-surface schema. Verifier: no.
2. Yes for builder semantic rows over normal claims; it validates after binding resolution and does not use a second overlay/mutation engine.
3. Partially. Validation/deletion/structured transforms share resolved suppression endpoints in builder; conservation and candidate-verifiable provenance/sidecar evidence do not fully close.
4. Mostly yes in builder and verifier transform reconstruction; owner-local heading normalization is deterministic through `clean_span` / `local_transform`.
5. Builder binds alts to reader assets by declared asset identity and excludes evidence-only assets from reader emission. Verifier checks manifest assets against config and reader ref count, but it does not enforce `alt_policy` independently.
6. No. The verifier is independent from builder imports, but it does not recompute the complete public reader-surface contract or candidate provenance input identities.
7. Partially. Source/emitted ranges and hashes for normal structured evidence are strong, but suppression evidence is not persisted as a candidate-verifiable sidecar section.
8. No. The tests are behavior-oriented in many areas, but the new reader-surface negative cases and verifier rejection tests are missing.
9. No direct weakening of accepted reconstruction identity, asset bytes, or link counts was found in the builder path. The verifier input-identity and reader-surface gaps weaken auditability and mutation invalidation.
10. Not safe. Remediate code/tests first, then rerun focused checks before two scratch builds or Candidate C.

## Recommendation

Do not authorize Candidate C. Remediate verifier-side reader-surface closure, candidate suppression sidecar evidence, provenance input identity validation, and targeted negative tests. After those pass, authorize two scratch builds and then a frozen successor candidate for a separate release review.

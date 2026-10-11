# Viral Step 7 reader-surface second implementation review receipt

## Receipt metadata

- review_kind: implementation
- decision: APPROVE_IMPLEMENTATION_REMEDIATION
- reviewer role: independent critic, gpt-5.5, high
- implemented candidate: no
- materially designed candidate: no
- orchestrator policy owner: root main-chat gpt-5.6-sol at medium
- orchestration ownership: not transferred
- assignment state: completed; second implementation review receipt written
- scoped override: independent critic/high role and this one receipt write only
- timestamp: 2026-09-02T03:44:10.7345979+03:00
- elapsed time: approx 45 minutes
- token use: unavailable; exact per-agent token accounting was not exposed

## Inputs verified

- Assignment packet: `F4503CAA58103866474799648AAF0B451C6813A016E66F7D709BF1260E1F774F`
- Architecture: `BD537483C7BB3C78076DC2A6F7FC8937BF4040261B74E58312D3CBC6FEFC901D`
- First critic rejection: `5B3DD4244CFB5B7CF5DB89C6D704ED944CFC77FE704024BAB496168204AA755B`
- Suppression containment amendment: `EB9E229EAFD184979FF5B798FBAB8F800E4510013CEB810DEB99947B64FF6B38`
- Engineering receipt: `333A236621FEC179D5F3354E4870FA040089D533D559679992296B8B89535787`
- Publication config: `C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30`
- Builder: `2609F2ECBB97F36260B8A4C58F50A8BF445F491197C95EC61127CF519631039D`
- Verifier: `B2CCB114983CA31722A7DD813124E4E3351E8F4734B491879E27FD53B23EE20A`
- Builder tests: `EFD49D9858356276056533F4BC1F78732C13688478BEB7102585480AC9BF64C3`
- Verifier tests: `57B2B70193589C767FCEF9DD4F4CD6823E876CE978637E6BDFB84D1E38567D45`

## Files checked

- `docs/governance/nri_goal_governance.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_orchestrator_viral_step7_reader_surface_second_implementation_review_assignment_20260902.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_viral_step7_master_en_reader_surface_remediation_20260902.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_step7_reader_surface_implementation_review_20260902.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_orchestrator_viral_step7_suppression_containment_amendment_20260902.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_step7_suppression_edit_plan_resume_20260902.md`
- `kb_creator/working/viral/master_en/publication_config_v1.json`
- `kb_creator/scripts/build_scenario_master_en.py`
- `kb_creator/scripts/verify_scenario_master_en.py`
- `kb_creator/tests/test_build_scenario_master_en.py`
- `kb_creator/tests/test_verify_scenario_master_en.py`

## Commands actually run

- `Get-FileHash -Algorithm SHA256 ...assignment...` - matched assignment hash.
- `Get-FileHash -Algorithm SHA256 ...required inputs...` - all required input hashes matched.
- `git status --short --branch` - dirty worktree with unrelated governance/config and untracked kb_creator files already present; no staging or commit.
- `python -B -m unittest kb_creator.tests.test_build_scenario_master_en kb_creator.tests.test_verify_scenario_master_en` - `Ran 55 tests in 28.086s`, `OK`.
- `python -B -m py_compile kb_creator/scripts/build_scenario_master_en.py kb_creator/scripts/verify_scenario_master_en.py` - pass.
- `Get-ChildItem -Force kb_creator/working/viral/master_en/candidates` - Candidate A/B present, Candidate C absent, `c2b-unittest` absent after teardown; four protected `.c2b-unittest.staging.*` roots remain present and untouched.

## Evidence

- Governance confirms this is an implementation review kind and does not transfer orchestration ownership; release review remains a separate gate in `docs/governance/nri_goal_governance.md`.
- Builder closes the reader-surface schema and nested keys, selector shape, 25 semantic fragment count, 22 suppression count, alt policy, and overlap rejection at `kb_creator/scripts/build_scenario_master_en.py:222-307`.
- Builder validates semantic fragments against normal resolved bindings, validates suppression replacement owner and claimant containment including owned-page proof chain, then feeds resolved suppressions into conservation at `kb_creator/scripts/build_scenario_master_en.py:290-306` and `kb_creator/scripts/build_scenario_master_en.py:490-550`.
- Builder applies one original-coordinate edit plan for xrefs plus suppressions through `clean_span`, `apply_source_edit_plan`, reader assembly, structured/note transforms, and sidecar serialization at `kb_creator/scripts/build_scenario_master_en.py:688-824`.
- Builder persists candidate-local `provenance.reader_surface` with semantic fragments, suppressions, source/applied/reader/replacement occurrence counts, containment objects, and reader alts at `kb_creator/scripts/build_scenario_master_en.py:889-891`.
- Verifier has a separate reader-surface resolver and validates schema, selector resolution, hash equality, non-overlap, 25/22 counts, 107 reader alts, and alt policy at `kb_creator/scripts/verify_scenario_master_en.py:77-121`.
- Verifier independently recomputes suppression containment metrics and requires exactly 22 rows, 1911 UTF-8 bytes, 17 normal, 5 owned-page, 4 cross-owner, 0 generated, 0 unproven, and 0 unauthorized at `kb_creator/scripts/verify_scenario_master_en.py:212-228`.
- Verifier closes candidate provenance identities against current contract, publication config, source PDF, accepted reconstruction config, and builder script identity at `kb_creator/scripts/verify_scenario_master_en.py:251-254`.
- Verifier recomputes the expected candidate-local reader-surface sidecar from immutable inputs and requires exact equality to `MASTER_EN.provenance.json` at `kb_creator/scripts/verify_scenario_master_en.py:255-257`.
- Focused builder tests assert conservation counts, cross-owner suppression behavior, and closed resolver behavior at `kb_creator/tests/test_build_scenario_master_en.py:82-86` and `kb_creator/tests/test_build_scenario_master_en.py:154-157`.
- Focused verifier tests assert reader-surface selector and alt-policy negative coverage, no direct verifier import of the builder by source text, resealed candidate mutation failures, and fixture teardown behavior at `kb_creator/tests/test_verify_scenario_master_en.py:17-24`, `kb_creator/tests/test_verify_scenario_master_en.py:28-38`, and `kb_creator/tests/test_verify_scenario_master_en.py:57-95`.

## First-review finding disposition

- P1-1 verifier does not independently enforce the frozen `reader_surface` public contract: closed. Verifier now validates `reader_surface`, `semantic_fragments`, `authorized_suppressions`, `heading_policy`, `alt_policy`, counts, selector hashes, alts, and candidate sidecar equality.
- P1-2 suppression evidence is not carried as a candidate-verifiable sidecar/public contract: closed. Builder writes `provenance.reader_surface.suppressions`; verifier independently recomputes and compares it.
- P2-1 verifier does not validate candidate provenance input identities: closed. Verifier now requires exact `provenance.inputs` and builder producer identity.
- P2-2 conservation accounting does not use authorized suppression ranges: closed. Builder and verifier derive suppression metrics from resolved rows, including normal/owned-page/cross-owner/generated/unproven/unauthorized counts.
- P3-1 focused tests omit new reader-surface negative cases: materially closed for the required remediation. Tests now cover reader-surface selector mutation, alt-policy mutation, cross-owner suppressions, conservation counts, and resealed provenance/asset/QA mutation failures.

## Severity findings

- P0: none.
- P1: none.
- P2: none.
- P3: none blocking. Residual test breadth is intentionally focused and does not reopen the frozen 371/119/490 suites.

## Required review question answers

1. All five first-review findings are materially closed.
2. The verifier independently enforces the closed reader-surface contract, recursive provenance input identity, candidate-local sidecar equality, and derived lexical/suppression conservation.
3. Builder and verifier use one unambiguous original-coordinate edit plan for source xref replacements and claimant-owned suppressions, with overlap rejection.
4. Normal, owned-page, and the four cross-owner suppressions are proven and recomputed from config, source pages, visual review/source disposition proof, and candidate sidecar evidence rather than trusted only from hard-coded totals.
5. Focused negative tests are proportionate to the remediation and sufficient for implementation review without reopening the broader frozen suites.

## Blockers and residual risks

- Blockers: none for implementation remediation.
- Residual risks: Candidate C is still absent and not authorized by this receipt; two scratch builds, freeze, independent verifier on the frozen successor, bounded full-reader QA, and a separate release review remain pending.
- Declared exclusions: no release decision, no user reading acceptance, no MASTER_RU changes, no Candidate A/B/C mutation, no release scratch mutation, no canonical plan/context/status/release edits.
- Invalidation on mutation: any change to the config, builder, verifier, focused tests, future Candidate C, or its manifest invalidates this implementation review for the mutated surface and requires renewed review at the appropriate gate.

## Recommendation

Proceed to orchestrator-controlled next steps for two clean scratch builds and, if deterministic, a frozen Candidate C followed by independent verification, bounded full-reader QA, and a separate release review. This receipt approves the implementation remediation only.

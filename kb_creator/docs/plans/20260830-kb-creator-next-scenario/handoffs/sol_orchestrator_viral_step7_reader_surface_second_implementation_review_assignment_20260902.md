# Viral Step 7 — second independent implementation review

## Role and decision

- Reviewer: independent GPT-5.5/high critic.
- Scope: read-only review of the Step 7 reader-surface remediation after the first critic rejection.
- Output exactly one new receipt:
  `gpt55_critic_viral_step7_reader_surface_second_implementation_review_20260902.md`.
- Decision must be `APPROVE_IMPLEMENTATION_REMEDIATION` or `REJECT_IMPLEMENTATION_REMEDIATION`.
- This is not the final release review and does not authorize Candidate C by itself.

## Required inputs

- Architecture: `sol_architect_viral_step7_master_en_reader_surface_remediation_20260902.md`
  (`BD537483C7BB3C78076DC2A6F7FC8937BF4040261B74E58312D3CBC6FEFC901D`).
- First critic rejection: `gpt55_critic_viral_step7_reader_surface_implementation_review_20260902.md`
  (`5B3DD4244CFB5B7CF5DB89C6D704ED944CFC77FE704024BAB496168204AA755B`).
- Suppression containment amendment: `sol_orchestrator_viral_step7_suppression_containment_amendment_20260902.md`
  (`EB9E229EAFD184979FF5B798FBAB8F800E4510013CEB810DEB99947B64FF6B38`).
- Engineering receipt: `terra_engineering_viral_step7_suppression_edit_plan_resume_20260902.md`
  (`333A236621FEC179D5F3354E4870FA040089D533D559679992296B8B89535787`).
- Publication config: `kb_creator/working/viral/master_en/publication_config_v1.json`
  (`C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30`).
- Builder: `kb_creator/scripts/build_scenario_master_en.py`
  (`2609F2ECBB97F36260B8A4C58F50A8BF445F491197C95EC61127CF519631039D`).
- Verifier: `kb_creator/scripts/verify_scenario_master_en.py`
  (`B2CCB114983CA31722A7DD813124E4E3351E8F4734B491879E27FD53B23EE20A`).
- Focused tests:
  - `kb_creator/tests/test_build_scenario_master_en.py`
    (`EFD49D9858356276056533F4BC1F78732C13688478BEB7102585480AC9BF64C3`)
  - `kb_creator/tests/test_verify_scenario_master_en.py`
    (`57B2B70193589C767FCEF9DD4F4CD6823E876CE978637E6BDFB84D1E38567D45`).

## Required review questions

1. Are all five findings from the first critic rejection materially closed?
2. Does the verifier independently enforce the closed reader-surface contract, including recursive provenance identity and derived lexical conservation?
3. Do the builder and verifier use one unambiguous original-coordinate edit plan for xref replacements and claimant-owned suppressions, with overlap rejection?
4. Are normal, owned-page, and the four cross-owner suppressions proven and recomputed rather than trusted from hard-coded totals?
5. Are focused negative tests proportionate and sufficient without reopening the frozen 371/119/490 suites?

The critic may run only the two focused unittest modules and `py_compile`. The disposable `c2b-unittest` fixture is permitted; it must be absent after teardown. Candidate A/B/C, release scratch paths, and the four pre-existing `.c2b-unittest.staging.*` directories are read-only. Do not edit code, config, tests, candidates, plans, context, or status.

## Receipt minimum

Record input hashes, commands actually run, findings with file/line evidence, explicit disposition of each first-review finding, residual risks, and the decision. Keep the receipt compact; do not reproduce raw test logs.

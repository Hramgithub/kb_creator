# Terra engineering assignment: Viral Step 6A strict graph and fixture foundation

## Authority and baseline

- Role: `gpt-5.6-terra / medium`, Fast/priority policy.
- This is reusable engineering, not QA or bounded Luna execution.
- Accepted design authority:
  `sol_architect_viral_step6a_executable_enforcement_remediation_packet_20260901.md`.
- Required sections for this phase: 4 through 7, 9, 10.1 through 10.4,
  11.1, and the related stop conditions in section 12.
- Current library SHA-256:
  `F2F509887E77D704F488EB28154B346E05EF2EC5B97F8259650D331EA7CD8703`.
- Current focused-test SHA-256:
  `0DD943607D4236EB53718597F7EFBC0841E65D91F8AC3EFC5865D5C8EE8B6482`.
- The two earlier Terra receipts remain immutable.

## Exclusive write allowlist

1. `kb_creator/scripts/scenario_source_reconstruction.py`;
2. `kb_creator/tests/test_scenario_source_reconstruction.py`;
3. new receipt
   `terra_engineering_viral_step6a_strict_graph_fixture_20260901.md`.

No other file, candidate/source/recovery root, config, plan/context, prior
receipt, Git surface, cache, or live output may change.

## Required implementation

Implement the complete foundation on which the later 368-row audit will run:

1. sealed production and TEST authorities/providers with real repository identity,
   filesystem observation, branch/HEAD, path and provider admission;
2. unchanged public/test wrappers entering one `_execute` and one ordered
   `_strict_verify`, with no reduced TEST/build verifier;
3. the exact binding phase order and first-error semantics from section 5.3;
4. all 16 physical authorities and their closed schemas/relations from section 6;
5. production-shaped input and candidate fixture facts from section 7: 124 pages,
   388 blocks, 204 JPEG assets, 112 references plus 92 unreferenced assets,
   39 entity/handout rows, five content-mode reviews, four blockers, 124
   navigation rows, 31 sheets, 211 recovery files, and deterministic fake
   PDF/PNG observations;
6. real `_test_build` plus real `_test_verify` twice to create and verify the
   physical 502/501/500 bundle. The test factory must not use a second toy writer;
7. pure expected-manifest planning, internal `BuildVerificationToken`, real
   `_write_non_qa_bundle`, `_finalize_and_verify`, closed QA v3 and COMMANDS v3;
8. an outside-root read trap and zero Git/external/tool access for TEST.

This phase may leave the current 368 mutation registry temporarily generic, but
must not weaken, delete, fake, or count-substitute the later mutation/audit
requirements. Keep exactly 371 collected nodes; do not add counted positive
nodes. Ownership edge-case completion belongs to the later BLD phase, but the
strict graph and real build/finalizer interfaces must be ready for it.

## Verification and result

- Use only offline commands with `python -B` and pytest
  `-p no:cacheprovider`.
- Run collection and targeted valid-fixture/shared-route checks sufficient to
  prove this phase. Do not launch all 368 negatives until the registry phase.
- Do not run live preflight/verify/build/remediate and do not delete `.pyc`.
- Write `COMPLETE_PHASE1_PENDING_INTEGRATION` only if every item above is
  implemented and targeted evidence passes. Otherwise write `BLOCKED` with
  exact symbols and missing authority/fixture facts.
- Receipt must include before/after hashes, sizes, exact commands/results,
  protected-surface check, remaining work reserved for later phases, elapsed
  time, token use, timestamp, and the retained orchestrator owner.

# Independent critic review: Viral Step 6A executable-enforcement remediation packet

- Goal: `20260830-kb-creator-next-scenario`
- Step: `6A-executable-enforcement-remediation`
- Review kind: architecture/design
- Role/model/effort policy for this review: independent critic `gpt-5.5` / `high`, Fast/priority processing per current user-scoped override
- Actual platform model/effort/runtime priority: unavailable to reviewer
- Orchestrator policy owner: main chat `gpt-5.6-sol` / `medium`
- Assignment state: `nri-independent-critic`, user-scoped effort override for this review
- Scoped override: critic effort is `high` for this review; the packet's two `critic / medium` references are stale assignment metadata superseded by the user's current explicit override and active governance
- Independence declaration: I did not implement, materially design, remediate, execute QA for, or otherwise own the packet/candidate under review.
- Timestamp: 2026-09-01T01:53:31+03:00
- Elapsed time: unavailable
- Token use: unavailable

## Scope

Reviewed `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_viral_step6a_executable_enforcement_remediation_packet_20260901.md` as a design packet for a future bounded executor remediation of the rejected Step 6A enforcement-completion implementation.

This review determines whether the packet is implementation-ready and closes the prior P1/P2 design gaps without weakening accepted contracts. It does not perform implementation, material redesign, QA, live build/remediate, MinerU/OCR/GPU/model execution, network access, external Yandex/source access, candidate mutation, `MASTER_EN`, semantic acceptance, promotion, publication, staging, commit, or push.

## Verified identity and evidence

Verified read-only:

- Worktree: `D:\NRI\.worktrees\kb-creator-viral`
- Branch: `codex/kb-creator-viral`
- HEAD: `54607bd3b9362adbb0c4bca64e8751482797f380`
- Packet SHA-256: `32D5A63657C5157B77B3A40ABB0CD5B0CDD00473A2846F28B1586B97C997257A`
- Triggering final implementation/process reject receipt SHA-256: `10871A65CD976F6B739608FED761AE9135A1C5370773D5D3F6DE61C8DF17977E`
- Current implementation baseline `kb_creator/scripts/scenario_source_reconstruction.py`: 29,620 bytes, SHA-256 `E5AEEACB175AD20C900AB31998045DBA398714AD4936E03FF591A090429D4107`
- Current focused-test baseline `kb_creator/tests/test_scenario_source_reconstruction.py`: 9,515 bytes, SHA-256 `B91A1F78F9F7D4D2E87FEA8A701F6877C47AA3443899883C538FCC3C7D93A31A`
- Protected CLI `kb_creator/scripts/reconstruct_scenario_source.py`: 1,254 bytes, SHA-256 `64BD04C82A5AA21B7397885ABEB74E8A2215357B64DAD845AFDFDFC00F551DAA`
- Protected contract tests `kb_creator/tests/test_scenario_contract.py`: 18,252 bytes, SHA-256 `DE5603869C9517A274FCD6DB2D61D23BEE2A204BAC8A1217E16603A5BF232AC3`
- This review receipt path was absent before creation.

Branch and HEAD were verified by read-only `.git` metadata file inspection, not by invoking Git. I did not access the external Yandex locator.

## Files checked

Read or materially inspected:

- `AGENTS.md`
- `docs/governance/nri_goal_governance.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/plan.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/context.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_step6a_enforcement_completion_final_review_20260901.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_viral_step6a_executable_enforcement_remediation_packet_20260901.md`
- `kb_creator/scripts/scenario_source_reconstruction.py`
- `kb_creator/tests/test_scenario_source_reconstruction.py`
- `kb_creator/scripts/reconstruct_scenario_source.py`
- `kb_creator/tests/test_scenario_contract.py` by hash

Files changed:

- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_step6a_executable_enforcement_remediation_packet_review_20260901.md`

No other file was intentionally changed.

## Design assessment

The packet directly addresses the four findings from the triggering review:

1. **Registry/summary matrix P1** — The packet removes counted `POS` nodes, requires exactly `368` selector-specific executable negative cases plus `3` real BLD cases, explicitly includes `INJ`, restores `TOP=21`, bans generic ids and counted static/source-string proof, and requires each negative row to carry a real callable, one semantic selector mutation, literal reseal tuple, `_test_verify` invocation, exact `ReconstructionStop.code`, and audit row.
2. **Split/bypassable test route P1** — The packet requires all public and test wrappers to call one `_execute` and one `_strict_verify`, bans `_verify_test_bundle`, summary verifier, provider-prefix admission, reconstructed production-kind contexts, public override parameters, relaxed/skip flags, and environment/pytest bypasses.
3. **Toy/unsafe public build P1** — The packet requires a real production-shaped `ValidatedReconstructionInput`, deterministic 500-file non-QA writer, one finalizer that writes COMMANDS then QA and calls `_strict_verify`, `OwnedTempRoot`, no-replace publication, no direct `shutil.rmtree`, no `os.replace`, exact ownership/nonce/file-id checks, and real BLD-001/002/003 semantics.
4. **Residual production `verify()` P2** — The packet moves live `verify()` onto the same context-admitted strict verifier, including branch/HEAD, 16 authority schemas, source/sidecar/contract/recovery/source-identity, topology, inventory, page/content/master/navigation/asset/entity/handout/mode/reference/role/sheet graph, COMMANDS, QA, and no-fabricated-closure checks.

### Implementation readiness and proportionality

The two-file code/test allowlist is sufficient:

- The protected CLI already imports and routes the four public functions with exactly four `Path` arguments, so it does not need modification.
- The shared library can contain the sealed profile/context, providers, strict verifier, production loader, writer/finalizer, Windows path helpers and build publication code.
- The focused test file can contain the production-shaped fixture factory, mutation registry, reseal helpers and audit checks under `tmp_path`.
- No candidate, QA, COMMANDS, source, sidecar, recovery, contract, plan/context/status, governance/config, or Git mutation is needed.

The design is strict but implementable on Windows:

- Reparse handling is addressed through no-follow classification and a controlled `ClassificationOverride` in tests, avoiding Developer Mode or Administrator dependency while still exercising the production reparse rejection branch.
- The 502-file fixture is large but feasible with deterministic small bytes. The packet correctly requires real physical topology and production-compatible JSON shapes rather than placeholder summaries.
- The build state machine is appropriately fail-closed: same-parent owned temp, marker/nonce/file-id binding, no-replace rename, strict pre/post verification, no final-root rollback, and cleanup only for a provably owned temp root.
- Exact counts and command lines are bounded and testable. The packet treats count mismatch, fake 502 claims, summary authority, toy writer, missing case IDs, provider-prefix admission, public overrides, residue, and protected-path mutation as stops.

### Role metadata discrepancy

The packet still contains stale references to independent critic `gpt-5.5 / medium` in its role text. The current user-scoped review instruction and active governance for this review require `gpt-5.5 / high` with Fast/priority processing. I record that discrepancy as superseded assignment metadata for this review, not as a design blocker, because it does not affect the packet's substantive executor/QA architecture and the user explicitly instructed me to judge the design independently.

## Findings

- P0: none
- P1: none
- P2: none

## Verdict

ACCEPT.

The packet is implementation-ready. It closes the prior P1/P2 design gaps at the specification level without weakening the accepted contracts. Execution may proceed only after the orchestrator binds this review hash and re-verifies the packet's pre-write admission state.

## Execution authorization status

Authorized next gate: bounded executor remediation under the packet exactly as written.

Permitted executor mutable paths only:

1. `kb_creator/scripts/scenario_source_reconstruction.py`
2. `kb_creator/tests/test_scenario_source_reconstruction.py`
3. absent-before immutable receipt `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/luna_executor_viral_step6a_executable_enforcement_remediation_20260901.md`

Execution remains forbidden if any dispatch-time baseline differs, if this review hash is not bound, if the executor receipt already exists, or if the fix cannot fit the exact three-path allowlist.

Still unauthorized:

- live `build` or live `remediate`;
- candidate, QA, COMMANDS, source, sidecar, recovery, CLI, contract-test, plan/context/status, governance/config, release/publication or Git mutation;
- external Yandex/source access;
- network, MinerU, OCR, GPU/model, historical material or translation access;
- semantic acceptance, `MASTER_EN`, promotion, publication, release, staging, commit or push.

Downstream gates remain mandatory: bounded executor receipt, separate bounded QA, fresh independent implementation/process review with no unresolved P0/P1/P2, then orchestrator integration. Even eventual acceptance closes only executable-enforcement/build-seam remediation; the live candidate remains `candidate_needs_review`.

## Blockers and residual risks

No design blockers.

Residual execution risks to monitor:

- The 368 selector-specific negative cases can still be faked if QA checks only counts. The packet mitigates this by requiring machine-readable mutation audit rows, callable identity, `_test_verify` invocation, exact expected/observed codes, and QA inspection of the implementation.
- The production-shaped fixture and Windows ownership helpers are non-trivial; implementation failure should produce a truthful blocked receipt, not a narrowed test matrix.
- The no-replace rename and cleanup semantics must avoid broad deletion and final-root rollback exactly as specified.

## Forbidden actions declaration

I did not implement, materially redesign, execute QA, run tests, run live build/remediate, invoke MinerU/OCR/GPU/model/network tooling, access historical translations, access the external Yandex locator, mutate candidate/source/sidecar/recovery/QA/COMMANDS/code/tests/plan/context/status/config/Git state, stage, commit, push, promote, publish, or release anything.


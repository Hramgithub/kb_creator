# Independent critic design review: Viral Step 6A enforcement completion packet

- Goal: `20260830-kb-creator-next-scenario`
- Step: `6-source-reconstruction-step6a-enforcement-completion`
- Review kind: architecture/process design review
- Role/model/effort: independent critic, policy `gpt-5.5` / `medium`
- Actual platform model/effort: unavailable to reviewer
- Orchestrator policy owner: main chat `gpt-5.6-sol` / `medium`
- Assignment state: `nri-independent-critic`
- Scoped override: none for this review
- Independence declaration: I did not implement, materially design, remediate, execute QA for, or otherwise own the packet under review.
- Timestamp: 2026-08-31T23:33:33+03:00
- Elapsed time: unavailable
- Token use: unavailable

## Scope

Reviewed `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_viral_step6a_enforcement_completion_packet_20260831.md` as a design packet for a future bounded executor slice.

This review does not authorize a live build, live `remediate`, MinerU, OCR, GPU/model, network, external-source access, historical-material access, translation, candidate mutation, `MASTER_EN` promotion, release, publication, staging, commit or push. It evaluates whether the packet is complete, implementable and proportional enough for execution to proceed under its own bounded controls.

## Identity and hash verification

Verified by read-only inspection and hashing:

- Worktree: `D:\NRI\.worktrees\kb-creator-viral`
- Branch: `codex/kb-creator-viral`
- HEAD: `54607bd3b9362adbb0c4bca64e8751482797f380`
- Packet SHA-256: `56586563470FCA55B1CE31EB1EC73C71438B33A1FEBC1A1A39ADB8781AE3A604`
- Prior implementation/process reject SHA-256: `1ECB8FEBC517BAE2BFFF949663A9A701BF8107A80B8023C16EF6ABD6712A7D2D`
- Live candidate all-file manifest: 502 rows, `410AED5D111E3BA8CA294095EF55F18AC7DFFD335868EA6D59522B91E14725EA`
- Live candidate inventory excluding only root QA: 501 rows, `F0F243F6B8194C502CF6FEF9D5C838196BAFA49C96AE135D61EDAD799869C766`
- Live candidate protected subset excluding QA and `evidence/COMMANDS.json`: 500 rows, `98FC41EAA65528CE04C772983FB49E8DD3DAE5998FAEDB98F0829E2E41E4C027`

Packet-stated live baselines checked against disk:

- `kb_creator/scripts/scenario_source_reconstruction.py`: 15,490 bytes, `581FA8D0F47C7906B29EC4664E929A98B3A3699445C974AB7CF51F398D118FA8`
- `kb_creator/tests/test_scenario_source_reconstruction.py`: 2,472 bytes, `9F581C5C6CD9A8DF5DB06DA30F48B6FE39995713AD3CFFCC3829CF8530D1C1B0`
- `kb_creator/scripts/reconstruct_scenario_source.py`: 1,254 bytes, `64BD04C82A5AA21B7397885ABEB74E8A2215357B64DAD845AFDFDFC00F551DAA`
- `kb_creator/tests/test_scenario_contract.py`: 18,252 bytes, `DE5603869C9517A274FCD6DB2D61D23BEE2A204BAC8A1217E16603A5BF232AC3`
- Candidate `RECONSTRUCTED_EN.qa.json`: 104,854 bytes, `C38CB0A4667B1D4344C5E5DD91AEAAE7A2FD3101A3BB76611104EAA13BBD8FA6`
- Candidate `evidence/COMMANDS.json`: 37,422 bytes, `9162651A456E12C7011081F999AA3B07EDB7EA9E66CA65CC78A0382456F12B06`

I did not access the external Yandex locator. I did not run Git commands; branch and HEAD were verified by reading `.git` metadata files.

## Files checked

Read or inspected:

- `AGENTS.md`
- `docs/governance/nri_goal_governance.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/plan.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/context.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_viral_step6a_enforcement_completion_packet_20260831.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_step6a_qa_metadata_integrity_remediation_review_20260831.md`
- `kb_creator/scripts/scenario_source_reconstruction.py`
- `kb_creator/scripts/reconstruct_scenario_source.py`
- `kb_creator/tests/test_scenario_source_reconstruction.py`
- `kb_creator/tests/test_scenario_contract.py`
- Live candidate root metadata and manifests under `kb_creator/working/viral/source_reconstruction/20260831_step6a_reconstruction_from_salvaged_engine_candidate`

Files changed:

- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_step6a_enforcement_completion_packet_review_20260831.md`

No other file was intentionally changed. No candidate, code, test, source, sidecar, recovery, plan/context/status, release/publication or Git state was mutated.

## Design assessment

### Prior critic findings

The packet directly addresses both findings from the prior reject receipt:

- Prior P1, incomplete strict verifier/test enforcement: addressed by requiring a shared repository/source/recovery admission gate, direct `verify()` branch/HEAD enforcement, explicit forbidden/reparse scans, exact schema/shape checks, live inventory reconstruction, page/content/navigation/asset/sheet/QA/COMMANDS graph validation, no-fabricated-closure checks, and a complete hermetic mutation matrix.
- Prior P2, disabled `build()` seam: addressed by restoring `build(contract_path, source_path, recovery_root, run_root)` as a fresh-root/refuse-overwrite operation with shared finalizer parity tests, while still forbidding any live build in this slice.

### Allowlist and hidden mutation risk

The allowlist is properly narrow:

- Material executor changes are limited to `kb_creator/scripts/scenario_source_reconstruction.py`, `kb_creator/tests/test_scenario_source_reconstruction.py`, and the executor receipt.
- Candidate QA and `COMMANDS.json` are explicitly protected and must remain byte-identical.
- The CLI is protected, and read-only inspection confirms it already routes `preflight`, `build`, `remediate` and `verify` to the library functions. Therefore the packet can restore the public build seam without editing the CLI.
- Plan/context/status/readme/orchestration artifacts are protected by dispatch-window snapshot equality, not brittle packet-era fixed hashes. This preserves the accepted amendment model.

I found no hidden need to modify the CLI, candidate, contract tests, source, sidecar, recovery root, plan/context/status or Git state.

### Verifier completeness

The packet's verifier contract is complete enough for the stated boundary. It requires direct enforcement of:

- repository branch/HEAD and containment;
- exact local source/sidecar/contract/recovery/candidate roots;
- non-reparse roots and descendants;
- explicit forbidden payload classes before generic cardinality errors;
- 16 schema authorities;
- sidecar/source identity, contract snapshot, recovery manifest/evidence and blocker ledger bindings;
- 502/501/500 candidate manifests and exact non-circular inventory rules;
- page, master Markdown, content, navigation, asset/reference, entity/handout, content-mode and reference-only relations;
- `COMMANDS.json` action/state/count/flag/sheet/page-render mapping;
- QA v3 fields, counts, gates, inventory and open uncertainty;
- preservation of `candidate_needs_review` and semantic/reading-order/placement/ownership uncertainty.

This is strict, but it is evidence-driven from current candidate bytes and manifests rather than speculative semantic acceptance.

### Test matrix and node counts

The 371 Step 6A-specific node count is high but implementable and not inherently fake:

- The arithmetic in the packet's coverage table is internally consistent: the listed categories sum to 371.
- The packet requires named case IDs, isolated mutations from a valid fixture, earliest failure codes, and separate focused/combined collection counts. This reduces the risk that parameterization merely inflates counts without semantic coverage.
- The protected contract-test count is handled fail-closed: if the unchanged protected contract suite is not 119 nodes, the executor must stop rather than modifying contract tests or the packet.
- The full hermetic fixture is large for a unit-test fixture, but 502 tiny files and deterministic JSON/image-byte stand-ins are feasible on Windows when kept under `tmp_path` and run with `-p no:cacheprovider`. It is proportional to the defect class because the prior failure was precisely that receipts substituted for executable cross-file enforcement.

Residual risk: the exact node-count contract is brittle to test collection naming/version drift and could still be implemented with shallow assertions if QA only checks counts. The packet mitigates this by requiring the coverage table, case IDs, earliest failure codes and independent QA inspection. I do not classify this as a blocker.

### Branch/HEAD and Git boundary

The packet distinguishes critic/review constraints from executor/runtime constraints correctly:

- The critic can verify branch/HEAD by metadata without invoking Git.
- Production `preflight`/`verify` may use read-only Git as the repository identity probe.
- Hermetic tests must inject the repository probe and must not spawn Git.

That is implementable and aligns with the requirement that `verify()` not rely on a prior `preflight()` call.

### Windows reparse and path safety

The packet's path rules are implementable:

- It calls out symlinks, junctions, mount points and Windows reparse attributes for roots and descendants.
- It separately rejects path escapes, absolute/drive/UNC forms, leading `/`, leading `./`, backslash, empty segment, `.`/`..`, trailing slash, case-folded aliases and non-regular files.
- It requires existing-target refusal for files, directories, symlinks, junctions, reparse entries and dangling links before `build()` creates a fresh root.

This is strict but appropriate for a Windows worktree and protects against the path classes that caused prior Step 6A runtime concerns.

### Build/finalizer design

The restored `build()` design is coherent:

- It is future fresh-root behavior only; no live build command is authorized.
- It uses the unchanged CLI seam.
- It consumes only the admitted local source and hash-bound recovery payload.
- It must not invoke MinerU/OCR/GPU/model/network/history/external locator.
- It leaves partial post-create failures for orchestrator inspection rather than deleting or retrying.
- It is verified only through three hermetic tests in this slice, which is proportional because the live candidate must not be rebuilt or re-finalized.

I found no circular writer/finalizer problem in the design. The packet requires `COMMANDS` construction before inventory finalization, excludes only QA from inventory, derives QA twice in memory, writes QA once, and then calls the same strict verifier with an immutable stage profile.

## Findings

No P0 findings.

No P1 findings.

No P2 findings.

## Recommendation

ACCEPT.

The enforcement completion packet is strict but implementable, complete for the prior P1/P2 classes, and proportionate to the current Step 6A boundary. It may proceed to the bounded executor implementation gate exactly as written.

## Safe next gate

The orchestrator may dispatch a bounded executor only within the packet's allowlist:

1. update `kb_creator/scripts/scenario_source_reconstruction.py`;
2. update `kb_creator/tests/test_scenario_source_reconstruction.py`;
3. write `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/luna_executor_viral_step6a_enforcement_completion_20260831.md`.

Executor must not edit the candidate, QA, `COMMANDS.json`, CLI, contract tests, source, sidecar, recovery root, plan/context/status, release/publication artifacts or Git state. The expected result is closure of the enforcement-layer P1 and reusable-build P2 only. The candidate remains `candidate_needs_review`; semantic/reading-order correctness, placement/layout fidelity, asset ownership/usage and broader human review remain open.

## Blockers and residual risks

No design blockers.

Residual risks to monitor during execution/QA:

- Exact pytest node counts are intentionally brittle; collection must report both focused and combined counts and case IDs, not just a green summary.
- The 502-file hermetic fixture may be slow on Windows; timeout/performance failure should be treated as an implementation blocker, not as permission to reduce coverage without a new design review.
- Reparse and dangling-link handling must be implemented with Windows-safe APIs and explicit tests, not just ordinary `Path.exists()` checks.
- Any candidate byte change voids this design boundary.

## Forbidden actions declaration

I did not perform external-source access, network access, build/remediate execution, MinerU/OCR/GPU/model execution, history/translation access, candidate/source/sidecar/recovery/code/test/plan/context/status mutation, Git command, Git index/ref mutation, staging, commit or push.


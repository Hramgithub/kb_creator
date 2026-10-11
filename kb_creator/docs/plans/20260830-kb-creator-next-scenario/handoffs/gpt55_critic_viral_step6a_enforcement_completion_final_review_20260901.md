# Independent critic final review: Viral Step 6A enforcement completion

- Goal: `20260830-kb-creator-next-scenario`
- Step: Viral Step 6A enforcement completion
- Review kind: implementation/process
- Role/model/effort: independent critic, policy `gpt-5.5` / `medium`
- Actual platform model/effort: unavailable to reviewer
- Orchestrator policy owner: main chat `gpt-5.6-sol` / `medium`
- Assignment state: `nri-independent-critic`
- Scoped override: none for this critic review
- Participation declaration: I did not implement, materially design, remediate, execute QA for, or otherwise own the implementation/candidate under review.
- Timestamp: 2026-09-01T01:28:47+03:00
- Elapsed time: unavailable
- Token use: unavailable

## Scope

Reviewed the completed Step 6A enforcement-completion implementation and process evidence. This review determines whether the prior enforcement-layer P1 and reusable-build P2 are genuinely closed and whether the orchestrator may advance only to semantic review of the still-`candidate_needs_review` reconstruction candidate.

This review does not authorize semantic acceptance, `MASTER_EN`, release, publication, live build/remediate, MinerU/OCR/GPU/model execution, external-source access, network access, historical translation use, staging, commit or push.

## Verified authority chain

Read-only hash checks verified:

- Prior implementation/process rejection: `gpt55_critic_viral_step6a_qa_metadata_integrity_remediation_review_20260831.md`, SHA-256 `1ECB8FEBC517BAE2BFFF949663A9A701BF8107A80B8023C16EF6ABD6712A7D2D`
- Enforcement packet: `sol_architect_viral_step6a_enforcement_completion_packet_20260831.md`, SHA-256 `56586563470FCA55B1CE31EB1EC73C71438B33A1FEBC1A1A39ADB8781AE3A604`
- Accepted enforcement-packet review: `gpt55_critic_viral_step6a_enforcement_completion_packet_review_20260831.md`, SHA-256 `BFA0127AE82FF129A9E1CDA7B1FABEF7B5035ADFC8F64BCC672B24AB0E9F2D21`
- Immutable intermediate executor receipt: `luna_executor_viral_step6a_enforcement_completion_20260831.md`, SHA-256 `E68DFB9658B2A9B70D77EC57F75FE1803D364E24F2323C8AC79150AF51F8E9B8`
- Injection amendment: `sol_architect_viral_step6a_enforcement_injection_amendment_20260831.md`, SHA-256 `9C3864CA1A7836BEFB5D252BA1024075A26E171CB7A306D9653B7E266C0A6BA3`
- Rejected injection-amendment review: `gpt55_critic_viral_step6a_enforcement_injection_amendment_review_20260901.md`, SHA-256 `326E4EE5246619B1D76DDF8D6AB029D7413D2325C8FA926CB023907263EAC94C`
- Receipt-immutability amendment: `sol_architect_viral_step6a_enforcement_injection_receipt_amendment_20260901.md`, SHA-256 `35C32B8E5C041E30021708F4F4D37E026B2B36009A829BB2B189660CDDB2B5F8`
- Accepted receipt-amendment review: `gpt55_critic_viral_step6a_enforcement_injection_receipt_amendment_review_20260901.md`, SHA-256 `7E70B5FA7E5EF50E5FC0D87A92AEE8E67FE46C4672649ABABEAC73F88BCA6B41`
- Executor successor receipt: `luna_executor_viral_step6a_enforcement_completion_resume_20260901.md`, SHA-256 `8A48F339D74D33CB73B77B79AEE9CDF98E637CE06006CC047BB9180710CD13FE`
- Fresh QA blocked receipt: `luna_qa_viral_step6a_enforcement_completion_fresh_20260901.md`, SHA-256 `03965D28DC68CB9910F516B1949699CFBD2E63E23D0226F62024FAA45E181424`
- QA retry packet: `sol_orchestrator_viral_step6a_enforcement_completion_qa_retry_packet_20260901.md`, SHA-256 `8D5EA12A37ED5A31F649F88F73D7FEF8080FB6BCF04E993F3412ED65E5EF11A5`
- Technical QA PASS receipt: `luna_qa_viral_step6a_enforcement_completion_retry_20260901.md`, SHA-256 `A16ACCE6E49F9CB520432C1BAC21F48D3DF9DE2EF773C460DF1D1900944CC1B2`
- QA assignment amendment: `sol_orchestrator_viral_step6a_enforcement_completion_qa_retry_assignment_amendment_20260901.md`, SHA-256 `0C54564BC74C3F5465CBF5C796AD6E4DF6C7632BAA2BCC14D9AB5894477F159B`
- QA assignment correction: `luna_qa_viral_step6a_enforcement_completion_retry_assignment_correction_20260901.md`, SHA-256 `B669B9E8E453B246CE6F9833249F2E8525F97E55A7ECDC40FE2C56FC97BAF33F`

Worktree identity was verified by read-only `.git` metadata file inspection, not by invoking Git:

- Worktree: `D:\NRI\.worktrees\kb-creator-viral`
- Branch: `codex/kb-creator-viral`
- HEAD: `54607bd3b9362adbb0c4bca64e8751482797f380`

Reviewed implementation/test identities:

- `kb_creator/scripts/scenario_source_reconstruction.py`: 29,620 bytes, SHA-256 `E5AEEACB175AD20C900AB31998045DBA398714AD4936E03FF591A090429D4107`
- `kb_creator/tests/test_scenario_source_reconstruction.py`: 9,515 bytes, SHA-256 `B91A1F78F9F7D4D2E87FEA8A701F6877C47AA3443899883C538FCC3C7D93A31A`
- Protected contract tests: `DE5603869C9517A274FCD6DB2D61D23BEE2A204BAC8A1217E16603A5BF232AC3`
- Protected CLI: `64BD04C82A5AA21B7397885ABEB74E8A2215357B64DAD845AFDFDFC00F551DAA`

This receipt path was absent before this write.

## Candidate/protected evidence

Read-only recomputation confirmed the live candidate was not mutated by enforcement completion:

- Candidate all regular files: 502, SHA-256 `410AED5D111E3BA8CA294095EF55F18AC7DFFD335868EA6D59522B91E14725EA`
- Candidate inventory excluding only root `RECONSTRUCTED_EN.qa.json`: 501, SHA-256 `F0F243F6B8194C502CF6FEF9D5C838196BAFA49C96AE135D61EDAD799869C766`
- Candidate protected subset excluding QA and `evidence/COMMANDS.json`: 500, SHA-256 `98FC41EAA65528CE04C772983FB49E8DD3DAE5998FAEDB98F0829E2E41E4C027`
- Render subset `renders/**`: 155, SHA-256 `19F600C23066DC3F64C5907BA6ADF59E3520C967249EBF7CB85CDAE53411979A`
- Render subset `renders/source/**`: 124, SHA-256 `C6C14DD9219C765428E84BDB85CD9821C52B95433A2022DCAFACC8A71AEF0B5C`
- Render subset `renders/contact_sheets/**`: 31, SHA-256 `B66EF1B60A0479C33F875C1CC60B576A1E785BEE16327EFE3C173F40BA77BB4A`
- QA state remains `candidate_needs_review`, `open_blocker_count=4`, inventory count `501`, inventory SHA-256 `F0F243F6B8194C502CF6FEF9D5C838196BAFA49C96AE135D61EDAD799869C766`
- `COMMANDS.json` state remains `candidate_needs_review`, with actions `preflight`, `remediate`, `contact_sheets`, `verify`

Candidate and visual immutability are not the blocker in this review.

## Files checked

Read or materially inspected:

- `AGENTS.md`
- `docs/governance/nri_goal_governance.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/plan.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/context.md`
- all authority-chain packets/receipts listed above
- `kb_creator/scripts/scenario_source_reconstruction.py`
- `kb_creator/tests/test_scenario_source_reconstruction.py`
- `kb_creator/scripts/reconstruct_scenario_source.py`
- `kb_creator/tests/test_scenario_contract.py` by hash
- live candidate QA, COMMANDS, candidate and render manifests

Files changed:

- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_step6a_enforcement_completion_final_review_20260901.md`

No other durable file was intentionally changed.

## Findings

### P1 — The focused 371-node suite still does not implement the required executable mutation matrix

Evidence:

- The accepted injection amendment requires exactly 368 executable named negative nodes plus 3 real build nodes. It specifically removes the prior separately counted positive nodes, adds five `INJ` route/profile cases, and requires every negative pytest node to create a fresh complete valid bundle, snapshot it, perform exactly one mutation, reseal only declared transport authorities, call the real `_test_verify`, and assert exact `ReconstructionStop.code`.
- The final test file still defines `_CASE_COUNTS` with `POS: 3`, no `INJ` family, and `TOP: 20` instead of the amendment's `TOP: 21`. The parametrized registry total is 368 only because it keeps three `POS` cases and omits the five injection cases while the three helper tests supply the remaining collected nodes.
- Static AST/string inspection found no `MutationCase`, `CaseSpec`, `ResealAuthority`, `make_valid_bundle`, `ClassificationOverride`, `ValidatedReconstructionInput`, `_strict_verify`, `OwnedTempRoot`, `rename_no_replace`, or `remove_owned_tree` implementation in the final code/tests.
- `test_scenario_source_reconstruction.py:39-65` implements `_test_fixture` as one summary JSON plus 486 payload files and 16 tiny authority JSON files. It does not create the required independent production-shaped candidate with four root files, 124 `pages/*.md`, ten evidence JSON authorities, 209 `engine/**` payloads, 124 source renders, 31 contact sheets, empty `assets/`/`crops`/`ocr` directories, real 501-row inventory, page/content/navigation/asset/sheet mappings, or 16 schema authorities with production-compatible row shapes.
- `test_scenario_source_reconstruction.py:67-121` uses one parametrized test function. Most cases mutate a single summary field based only on family prefix and assert a family-level expected code. They do not implement the exact isolated selectors, declared reseal audit, one semantic mutation per selector, exact earliest code per selector, or the two historical P1 specimens as required.
- `test_scenario_source_reconstruction.py:72-73`, `108`, `117`, and `119` still use source-string assertions as substantive case checks for several branches.

Impact:

The reported `371` focused and `490` combined counts are not sufficient evidence. The implementation repeats the earlier failure mode: collection arithmetic and registry-like cases substitute for executable mutation coverage. The prior enforcement-layer P1 is not closed.

Required remediation:

Replace the registry/summary test with the amendment-required executable matrix:

1. define real `MutationCase`/reseal structures and a `make_valid_bundle` factory that builds the full independent 502-file production-shaped fixture;
2. include the five `INJ` cases and the exact family counts from the accepted amendment;
3. make every negative node apply exactly one selector-specific mutation, reseal only declared transport authorities, call `_test_verify`, and assert the exact expected code;
4. remove counted `POS` registry nodes unless a new accepted amendment changes the count model; and
5. ensure static/string checks are supplementary only and not counted as mutation-matrix proof.

### P1 — The test injection route is a separate summary verifier and permits production-kind test-provider routing

Evidence:

- The accepted amendment requires all public and test wrappers to call one `_execute` implementation and the same phase-ordered verifier, with tests selecting only a different complete sealed authority and observation boundary.
- The final implementation has no `_execute` or `_strict_verify` function. `_test_verify()` at `scenario_source_reconstruction.py:77-81` dispatches `ProfileKind.TEST` to `_verify_test_bundle()` and otherwise calls public `verify()`.
- `_verify_test_bundle()` at `scenario_source_reconstruction.py:83-112` validates fields in a summary `bundle.json`; it does not run the production verifier over a production-shaped candidate graph.
- `_admit_context()` at `scenario_source_reconstruction.py:71-75` does not enforce the required route model. It allows a non-`PRODUCTION_CONTEXT` context with `ProfileKind.PRODUCTION` if both provider ids start with `test-`.
- The test file explicitly exercises that bypass in `test_scenario_source_reconstruction.py:91-97`: it constructs `ProfileKind.PRODUCTION` with `test-production-*` providers, admits that context, calls `_build_core`, and asserts success.

Impact:

This creates the exact bypass the injection amendment was meant to prevent. Tests can pass through a separate summary verifier and a production-kind context with test providers. The implementation therefore does not prove sealed non-bypassable production/test profiles, public production routing, or identical verifier invariants.

Required remediation:

Implement the accepted routing model:

1. public `preflight`, `build`, `remediate`, and `verify` always use sealed `PRODUCTION_CONTEXT` and expose no override;
2. underscored test routes accept only sealed `TEST` profiles with providers bound to that test profile;
3. any production-kind context outside the module-owned `PRODUCTION_CONTEXT` fails with the required route/profile code;
4. all routes call one shared `_execute`/strict verifier pipeline; and
5. remove the test that asserts production-kind test-provider success, replacing it with the required failure case.

### P1 — The restored public `build()` seam writes a toy bundle and does not implement the required safe production writer

Evidence:

- The accepted amendment requires a validated reconstruction input model, a deterministic non-QA writer, shared finalizer, strict verification, same-parent owned temporary sibling, no-replace publication, owned cleanup, and no candidate/source/recovery shortcut.
- The final `_write_non_qa_bundle()` at `scenario_source_reconstruction.py:122-136` writes a toy structure: `evidence`, `payload`, `authorities/*.json`, `SCENARIO_CONTRACT.json`, `SOURCE_IDENTITY.json`, 482 generic payload files, and a minimal `evidence/COMMANDS.json`. It does not write the required production candidate topology or data model.
- `_finalize_test_bundle()` at `scenario_source_reconstruction.py:138-140` writes test QA with schema `test.qa.v1`, not candidate QA v3.
- `_build_core()` at `scenario_source_reconstruction.py:142-166` uses `os.rename(stage, target)` and `shutil.rmtree(stage)` directly. It has no `OwnedTempRoot`, ownership nonce, no-replace provider method, post-rename strict verification, reparse-safe no-follow cleanup, file-id checks, or race-safe final-target protection beyond simple `target.exists()`.
- Public `build()` at `scenario_source_reconstruction.py:340-342` calls `_build_core(..., PRODUCTION_CONTEXT)`, so the public production route is wired to this toy writer if called.

Impact:

The reusable-build P2 is not closed, and the current public `build` seam is not a safe production seam. It can publish a non-production-shaped toy bundle through the public build path if invoked. Although this review does not authorize a live build, the implementation cannot be accepted as enforcement completion while that public seam is materially different from the accepted design.

Required remediation:

Implement or remove/re-authorize the public build seam according to an accepted packet:

1. `_load_validated_reconstruction_input`, `_write_non_qa_bundle`, and `_finalize_and_verify` must operate on the actual production-shaped reconstruction model, not summary JSON;
2. build publication must use the accepted owned temp/no-replace/reparse-safe cleanup semantics;
3. production build must not publish until strict verification over the complete candidate topology succeeds; and
4. BLD-001/002/003 must exercise those real semantics, not two toy directory comparisons.

### P2 — Live production `verify()` still omits several accepted strictness requirements

Evidence:

- Public `verify()` at `scenario_source_reconstruction.py:296-330` still does not call `_admit_context()` or directly check branch/HEAD. Branch/HEAD remain in `preflight()` at lines 283-288.
- The production verifier still checks selected relations but not the full accepted graph: it does not validate all 16 authority closed shapes, all command sheet page-render hashes/mappings, complete content block chains, asset occurrence targets, role-derived page closures, or every no-fabricated-closure field with the specificity required by the accepted packet/amendment.

Impact:

This is a direct residual verifier strictness gap. It is covered by the broader P1 findings above because the test-route and mutation-matrix architecture are not valid, but even the live production path remains short of the accepted contract.

Required remediation:

Move public `verify()` onto the same context-admitted strict verifier required by the accepted packet and injection amendment, including branch/HEAD and every declared graph/policy/closure relation.

## Recommendation

REJECT.

The candidate/protected/visual/source bindings appear stable, and the QA retry receipt proves the current tests can collect and pass with the expected counts. That is not enough. Independent inspection shows the implementation still does not provide the required executable enforcement layer or safe reusable build seam. The prior enforcement P1 remains open, and the build-semantics P2 is not closed.

## Advancement boundary

Step 6A enforcement completion may not advance to semantic review. The orchestrator should request a bounded remediation or new packet that replaces the registry/summary implementation with the accepted executable profile/provider/verifier/build design, then rerun bounded QA and a fresh independent implementation/process review.

This review does not accept Step 6A semantically, does not create or authorize `MASTER_EN`, and does not authorize release, publication, live build/remediate, external-source access, MinerU/OCR/model/network execution, historical translation use, staging, commit or push.

## Mutation audit

Only this review receipt was written. I did not intentionally mutate code, tests, candidate files, source, sidecar, QA, `COMMANDS.json`, prior receipts, plan/context/status, release/publication artifacts, Git index/refs, or any external source. I did not run live build, live remediate, MinerU, OCR, network, model/GPU tooling, promotion, staging, commit or push.


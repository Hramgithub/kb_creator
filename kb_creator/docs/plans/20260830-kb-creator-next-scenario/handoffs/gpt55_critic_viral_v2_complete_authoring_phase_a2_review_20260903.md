# Viral v2 complete authoring Phase A2 - independent implementation review receipt

## Receipt metadata

- Goal id: `20260830-kb-creator-next-scenario`.
- Step id: `viral-v2-complete-authoring-phase-a2-review`.
- Review kind: `implementation`.
- Candidate state: hash-bound non-release implementation checkpoint; not a frozen release candidate.
- Critic role: `nri-independent-critic` / requested `gpt-5.5` / high.
- Implemented candidate: no.
- Materially designed candidate: no.
- Orchestrator policy owner: main chat / `gpt-5.6-sol` / medium.
- Assignment state: `matched` by packet; platform runtime/model not independently verifiable from this receipt.
- Scoped override: none.
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`.
- Timestamp: `2026-09-03T06:15:26+03:00` (Europe/Moscow).
- Elapsed time: approximately 35 minutes.
- Token use: unavailable.

## Files checked

- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/TASK_PACKET_gpt55_critic_viral_v2_complete_authoring_phase_a2_review_20260903.md`
- `docs/governance/nri_goal_governance.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_viral_v2_complete_publication_authoring_20260903.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_v2_complete_authoring_phase_a1b_review_20260903.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_v2_complete_authoring_phase_a2_20260903.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_v2_complete_authoring_phase_a2_test_remediation_20260903.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_v2_complete_authoring_phase_a2_test_remediation_v2_20260903.md`
- `kb_creator/scripts/build_scenario_master_en.py`
- `kb_creator/scripts/verify_scenario_master_en.py`
- `kb_creator/tests/test_build_scenario_master_en.py`
- `kb_creator/tests/test_verify_scenario_master_en.py`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/plan.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/context.md`

## Bound identity evidence

All packet-bound SHA-256 identities matched before review:

- Architecture receipt: `39F9B514F82ABAAD58D0A637E07C395206E57BED7106864EC0247A9477E24ADC`.
- A1b approval receipt: `0D99E9B4F9B70F93D66118C555D2C2ED0077587360DD2A3027B532CD3FBAA23C`.
- A2 engineering receipt: `663BF432F80E81563FE5AA4BF0331B15047FCBF9DCCA51F3F37CCCAE47A48F96`.
- A2 remediation-v1 receipt: `AE7BCC12062FC03CA8A0B30610B6C9C230EE7E74CE0DAB7BFEDF6161F9079D40`.
- A2 remediation-v2 receipt: `050C0B9EC2BE6572A6AE94855E1509A73769DEE3B06B54D4F6CB5ED23654BB37`.
- Builder: `B9A90CA83517505EB1B56D77ACA5338EA05058EFAC3F60CE6E4383F4F9DC6530`.
- Verifier: `B7108E64E2166F84654D8C0A88C2233831A4C5CF30BB3D92CC2B3886588E8F6B`.
- Builder tests: `3FD17110C0A00727DBF52790865FF13759B987B37CB838B6F7933ABD3DB3D99C`.
- Verifier tests: `D851C4317D7E2E793A1A55CA262CC0F109CE110B237FBB201C199282AD8E97E7`.
- Frozen v1 config preflight identity: `C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30`.

## Severity findings

### P1 - Decision references accept arbitrary common evidence tokens

The A2 decision-reference gate is not a structured decision-id membership check. Both implementations build the accepted reference set by applying the broad token regex `[A-Za-z0-9][A-Za-z0-9._:-]{0,255}` to the full decoded UTF-8 bytes of every bound decision-evidence file, then accept any `decision_ref` present in that token set.

- Builder evidence: `kb_creator/scripts/build_scenario_master_en.py:155`, `kb_creator/scripts/build_scenario_master_en.py:157`, `kb_creator/scripts/build_scenario_master_en.py:170`, `kb_creator/scripts/build_scenario_master_en.py:179`.
- Verifier evidence: `kb_creator/scripts/verify_scenario_master_en.py:137`, `kb_creator/scripts/verify_scenario_master_en.py:139`, `kb_creator/scripts/verify_scenario_master_en.py:149`, `kb_creator/scripts/verify_scenario_master_en.py:158`.
- Test gap: fixtures bind `decision_evidence` to the frozen v1 config and use `decision_ref: "viral"` or only assert a definitely missing reference. See `kb_creator/tests/test_build_scenario_master_en.py:42`, `kb_creator/tests/test_build_scenario_master_en.py:63`, `kb_creator/tests/test_build_scenario_master_en.py:307`, `kb_creator/tests/test_build_scenario_master_en.py:309`, `kb_creator/tests/test_verify_scenario_master_en.py:37`, `kb_creator/tests/test_verify_scenario_master_en.py:58`, `kb_creator/tests/test_verify_scenario_master_en.py:274`.

Required focused probe:

```text
PASS_INVALID_COMMON_TOKEN builder accepted invalid common token; verifier accepted invalid common token
```

Probe method: built the existing disposable v2 fixture, retained the packet-bound frozen v1 config as `migration.inputs.decision_evidence`, replaced all non-null ledger and `new_reviewed_targets` decision refs with the common token `reader`, then called both `B.v2_input_binding(...)` and `V.v2_input_binding(...)`. Both accepted. The token `reader` is ordinary config text, not a structured decision identifier. This satisfies the packet's P1 condition: an invalid decision ref passes.

Impact: every non-unchanged outcome and every new reviewed target can be falsely authorized by common words, scenario ids, field names, or any other token appearing anywhere in bound evidence bytes. This defeats the required exact decision identifier proof, even though input bytes/SHA are bound.

Minimal remediation: parse the bound decision artifacts as structured evidence and admit only exact values from approved decision-id fields. Reject free-text token extraction, reject unsupported evidence shapes, and add builder/verifier negative tests for `reader`, `viral`, prefix/near-match refs, field-name refs, and text-only evidence outside structured decision-id fields.

## Non-blocking observations

- The closed top-level `migration` shape, six ledger names, per-domain counts, allowed outcomes, unique final targets per row, `retained_unchanged` no-decision rule, source-row canonical hashes, source-id closure, target orphan closure, page 123/124 advertising exclusions, and pending-A3 preflight block are implemented in both modules.
- The P1 above means the decision-reference portion of that closure is not acceptable, so the whole A2 checkpoint cannot be approved.
- Remediation-v1 and remediation-v2 appear scoped to stale test fixture target closure. The final production script hashes stayed equal to the original A2 receipt hashes, and the final test hashes match the packet.
- This was not a `release` review. Candidate revision/manifest freeze, release QA references, declared release exclusions, and release invalidation-on-mutation were not accepted here. Even after remediation, release, visual QA, publication, and real v2 candidate creation remain closed.

## Verification evidence

- `python -B -m py_compile kb_creator\scripts\build_scenario_master_en.py kb_creator\scripts\verify_scenario_master_en.py kb_creator\tests\test_build_scenario_master_en.py kb_creator\tests\test_verify_scenario_master_en.py`: exit `0`.
- Exact two-module suite:
  `python -B -m unittest -q kb_creator.tests.test_build_scenario_master_en kb_creator.tests.test_verify_scenario_master_en`: `Ran 77 tests in 40.137s`, `OK`.
- Four-module baseline:
  `python -B -m unittest -q kb_creator.tests.test_build_scenario_master_en kb_creator.tests.test_verify_scenario_master_en kb_creator.tests.test_build_master_en_visual_qa_bundle kb_creator.tests.test_propose_scenario_semantic_units`: `Ran 77 tests in 39.758s`, `OK`.
- Real frozen-v1 builder preflight:
  `{"status":"preflight_passed","scenario_id":"viral","contract_sha256":"67688867D4971D55137C2E4E7A71A746199596EDE4F5DD18577F4331CA87536D","source_sha256":"0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05","reconstruction_inventory_sha256":"68C17FB765A89C6146398868E61F1F6EB7B2FE4EAFBA8C2C2C8F42260BBDBA83"}`.
- Real frozen-v1 verifier preflight:
  `{"status":"preflight_passed","scenario_id":"viral","publication_config_sha256":"C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30"}`.
- Scoped diff-check over the four reviewed implementation/test files: exit `0`.
- Focused decision-ref mutation probe: exit `0` with `PASS_INVALID_COMMON_TOKEN builder accepted invalid common token; verifier accepted invalid common token`.

## Forbidden-output evidence

Required forbidden paths checked after probes/preflights:

- `kb_creator/working/viral/master_en/publication_config_v2.json`: absent.
- `kb_creator/working/viral/master_en/candidates/accepted-v4/INVENTORY.json`: absent.
- `kb_creator/.v2-inputs-critic-decision-ref-probe`: absent.
- `kb_creator/working/viral/master_en/candidates/a2-review-preflight-probe`: absent in git status.
- `kb_creator/working/viral/master_en/candidates/a2-forbidden-probe`: absent.
- `kb_creator/working/viral/master_en/candidates/a2-remediation-v2-probe`: absent.

Additional scratch-like paths observed but not deleted because this assignment permits editing only this receipt:

- `kb_creator/.v2-inputs-critic-path-probe`, timestamp `2026-09-03T04:37:42+03:00`, predates this review turn.
- Four `.c2b-unittest.staging.*` candidate staging directories under `kb_creator/working/viral/master_en/candidates`, timestamps `2026-09-02T02:45-02:56+03:00`, predating this review turn.

## Blockers

The P1 decision-reference validation defect blocks `APPROVED_V2_COMPLETE_AUTHORING_PHASE_A2`. The partial pending-A3 boundary is otherwise fail-closed enough to avoid real v2 preflight bypass, but A2 cannot be accepted while arbitrary common evidence tokens authorize decisions.

## Recommendation

`CHANGES_REQUIRED_V2_COMPLETE_AUTHORING_PHASE_A2`

Acceptance remains closed until both builder and verifier replace arbitrary evidence tokenization with exact structured decision-id validation and equivalent negative mutations fail in both implementations. Even a future A2 approval would authorize only A3 engineering; real v2 config, candidate generation, visual QA, release, and publication remain closed.

# Viral v2 complete authoring Phase A2 - fresh independent rereview receipt

## Receipt metadata

- Goal id: `20260830-kb-creator-next-scenario`.
- Step id: `viral-v2-complete-authoring-phase-a2-rereview`.
- Review kind: `implementation`.
- Candidate state: hash-bound non-release implementation checkpoint; not a frozen release candidate.
- Critic role: `nri-independent-critic` / requested `gpt-5.5` / high.
- Implemented candidate: no.
- Materially designed candidate: no.
- Orchestrator policy owner: main chat / `gpt-5.6-sol` / medium.
- Assignment state: `matched` by packet; platform runtime/model not independently verifiable from this receipt.
- Scoped override: none.
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`.
- Timestamp: `2026-09-03T07:20:15+03:00` (Europe/Moscow).
- Elapsed time: approximately 75 minutes, including replacement of one invalid concurrent test run with valid sequential evidence.
- Token use: unavailable for this contributor receipt; active platform goal usage before this continuation reported `139506`.

## Files checked

- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/TASK_PACKET_gpt55_critic_viral_v2_complete_authoring_phase_a2_rereview_20260903.md`
- `docs/governance/nri_goal_governance.md`
- `kb_creator/README.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_viral_v2_complete_publication_authoring_20260903.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_v2_complete_authoring_phase_a1b_review_20260903.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_v2_complete_authoring_phase_a2_20260903.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_v2_complete_authoring_phase_a2_review_20260903.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_v2_complete_authoring_phase_a2_decision_ref_integration_recovery_20260903.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_v2_complete_authoring_phase_a2_decision_ref_test_closure_20260903.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_v2_complete_authoring_phase_a2_provenance_collision_remediation_20260903.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_v2_complete_authoring_phase_a2_full_mutation_matrix_closure_20260903.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/plan.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/context.md`
- `kb_creator/scripts/build_scenario_master_en.py`
- `kb_creator/scripts/verify_scenario_master_en.py`
- `kb_creator/tests/test_build_scenario_master_en.py`
- `kb_creator/tests/test_verify_scenario_master_en.py`
- `kb_creator/working/viral/master_en/publication_config_v1.json`
- `kb_creator/reference/viral/master_en/publication_config_v1.json`

## Bound identity evidence

All packet-bound identities matched current worktree files before rereview:

- Architecture receipt: `39F9B514F82ABAAD58D0A637E07C395206E57BED7106864EC0247A9477E24ADC`.
- A1b approval receipt: `0D99E9B4F9B70F93D66118C555D2C2ED0077587360DD2A3027B532CD3FBAA23C`.
- Initial A2 engineering receipt: `663BF432F80E81563FE5AA4BF0331B15047FCBF9DCCA51F3F37CCCAE47A48F96`.
- Initial A2 critic rejection: `37C5FD7B91140CB2AE566B0E634014764FCD23191DBD1BFA4E2654089C2297CC`.
- Integration recovery: `216F029F5CDA287E23BCA501FD9C27C673E504A07A877389A1F0EEEA67C9F614`.
- Collision finding receipt: `DAAEE694C9A4BECADD7B595467403D54907E572D444E145438FA8C245263F6F9`.
- Final provenance-collision remediation: `BB1B822DFE3712E3F452B2F34153F38CCD01461732411007AE5CA3112080829E`.
- Final full mutation matrix: `77247ACFE2F66BF6791103245EBF43EFBF35577C07BF192D86B28C42BE1B1123`.
- Builder `kb_creator/scripts/build_scenario_master_en.py`: `76DDF943D84B23A60578189F2E1C808D4606AD67028FFCCE76E0DD50418C4E3F`.
- Verifier `kb_creator/scripts/verify_scenario_master_en.py`: `938A6D3635E2078D20D09A32F9792808915E23CE909D1C7BDDD81ACB08B36CFE`.
- Builder tests `kb_creator/tests/test_build_scenario_master_en.py`: `F117173CD23F95E0BEE86D45813F2E2418EC7147B80C8C8E31C4F4ADE94D5D35`.
- Verifier tests `kb_creator/tests/test_verify_scenario_master_en.py`: `94D5CC6D27D0B93EFCB58058C8B1FF8F37FA579AADD95C4ABC7CB83491FEBD51`.
- Frozen v1 config, both working and reference paths: `C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30`.

The collision-finding hash resolved to
`terra_engineering_viral_v2_complete_authoring_phase_a2_decision_ref_test_closure_20260903.md`.

## Implementation evidence

- Builder structured decision catalog logic is implemented independently in `kb_creator/scripts/build_scenario_master_en.py:147-201`.
- Verifier structured decision catalog logic is implemented independently in `kb_creator/scripts/verify_scenario_master_en.py:133-186`.
- Both modules bind the exact six migration ledgers and counts:
  `hierarchy_rows=168`, `asset_rows=123`, `xref_rows=237`,
  `source_disposition_rows=124`, `handout_rows=41`, `structured_rows=29`.
- Builder tests cover duplicate same-kind evidence origin, compatible corroboration, incompatible declaration classes, exact semantic ids, common-token/field/prefix/suffix/case/near-match rejection, registry heading grammar, boundary closed shape/target-unit references, and closure blocking/closed-shape rejection at `kb_creator/tests/test_build_scenario_master_en.py:325-393`.
- Verifier tests cover the same decision catalog matrix independently at `kb_creator/tests/test_verify_scenario_master_en.py:316-357`.
- Verifier source does not import builder validation logic. Source search found no `import build_scenario_master_en` or `from build_scenario_master_en` in `kb_creator/scripts/verify_scenario_master_en.py`; the verifier references the builder script only as a candidate provenance identity check at line 771. The test module imports the builder only for fixture generation and asserts the production verifier import prohibition at `kb_creator/tests/test_verify_scenario_master_en.py:130`.

## Verification evidence

- `python -B -m py_compile kb_creator\scripts\build_scenario_master_en.py kb_creator\scripts\verify_scenario_master_en.py kb_creator\tests\test_build_scenario_master_en.py kb_creator\tests\test_verify_scenario_master_en.py`: exit `0`.
- Real frozen-v1 builder preflight-only:
  `{"contract_sha256":"67688867D4971D55137C2E4E7A71A746199596EDE4F5DD18577F4331CA87536D","reconstruction_inventory_sha256":"68C17FB765A89C6146398868E61F1F6EB7B2FE4EAFBA8C2C2C8F42260BBDBA83","scenario_id":"viral","source_sha256":"0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05","status":"preflight_passed"}`.
- Real frozen-v1 verifier preflight-only:
  `{"publication_config_sha256":"C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30","scenario_id":"viral","status":"preflight_passed"}`.
- Exact focused baseline, run sequentially:
  `python -B -m unittest -q kb_creator.tests.test_build_scenario_master_en kb_creator.tests.test_verify_scenario_master_en` - `Ran 89 tests in 48.322s`, `OK`.
- Required four-module baseline, run sequentially:
  `python -B -m unittest -q kb_creator.tests.test_build_scenario_master_en kb_creator.tests.test_verify_scenario_master_en kb_creator.tests.test_build_master_en_visual_qa_bundle kb_creator.tests.test_propose_scenario_semantic_units` - `Ran 89 tests in 48.364s`, `OK`.
- Scoped diff-check:
  `git diff --check -- kb_creator\scripts\build_scenario_master_en.py kb_creator\scripts\verify_scenario_master_en.py kb_creator\tests\test_build_scenario_master_en.py kb_creator\tests\test_verify_scenario_master_en.py`: exit `0`.

One earlier attempt ran the focused and four-module suites concurrently and failed from shared fixture/candidate path collisions. I discarded that as invalid evidence and replaced it with the sequential passing runs above.

## Adversarial probe evidence

Standalone rereview probes against both builder and verifier returned
`REREVIEW_PROBES_PASS`.

- Common-token and near-match references rejected by both: `reader`, `viral`,
  `candidate_id`, `DEC`, `DEC-100-suffix`, `dec-100`, `DEC-101`.
- Prose-only or undeclared semantic id `DEC-100` rejected by both when the structured semantic catalog declared only `DEC-200`.
- Duplicate same-kind semantic catalog rejected by both.
- Duplicate id inside a semantic catalog rejected by both.
- Compatible corroboration accepted by both:
  semantic candidate plus boundary candidate, and registry plus boundary plus closure.
- Incompatible declaration class rejected by both:
  `viral-logical_table-p020-l025` reused as a boundary `registry_ref`.
- Foreign boundary `target_unit_id` rejected by both.

Representative probe results:

```text
builder|reject_common_token|reader|ValueError:v2 migration unknown decision mismatch
builder|reject_duplicate_same_kind_catalog|semantic|ValueError:v2 migration decision evidence catalog mismatch
builder|accept_compatible_corroboration|semantic+boundary registry+boundary+closure|accepted
builder|reject_incompatible_class_collision|candidate_id_as_registry_ref|ValueError:v2 migration decision evidence catalog mismatch
builder|reject_foreign_boundary_target_unit|foreign-unit|ValueError:v2 migration decision evidence catalog mismatch
verifier|reject_common_token|reader|ValueError:E_V2_MIGRATION: unknown-decision
verifier|reject_duplicate_same_kind_catalog|semantic|ValueError:E_V2_MIGRATION: evidence-catalog
verifier|accept_compatible_corroboration|semantic+boundary registry+boundary+closure|accepted
verifier|reject_incompatible_class_collision|candidate_id_as_registry_ref|ValueError:E_V2_MIGRATION: evidence-catalog
verifier|reject_foreign_boundary_target_unit|foreign-unit|ValueError:E_V2_MIGRATION: evidence-catalog
```

## Forbidden-output evidence

Read-only post-probe checks found all required forbidden output and probe paths absent:

- `kb_creator/working/viral/master_en/publication_config_v2.json`: absent.
- `kb_creator/working/viral/master_en/candidates/accepted-v4/INVENTORY.json`: absent.
- `kb_creator/working/viral/master_en/candidates/a2-rereview-preflight-probe`: absent.
- All `.v2-inputs-rereview-*` and `.v2-rereview-*` probe roots/files: absent.
- Scoped git status for the receipt path was empty before writing this receipt.

Pre-existing scratch-like paths from prior assignments were observed but not touched because this assignment permits writing only this receipt:

- `kb_creator/.v2-inputs-critic-path-probe`, timestamp `2026-09-03T04:37:42+03:00`.
- Four `.c2b-unittest.staging.*` candidate staging directories under
  `kb_creator/working/viral/master_en/candidates`, timestamps
  `2026-09-02T02:45-02:56+03:00`.

## Severity findings

No P0 or P1 findings.

The prior common-token P1 is closed in both implementations. The rereview probes confirmed common words, field names, prefix/suffix/case/near matches, and undeclared/prose-only ids fail both builder and verifier. Structured decision-id extraction is now limited to the four approved evidence kinds and their explicit shapes:

- `kb_creator.semantic_unit_review.v2`: JSON object with `schema` and `decisions`, each decision exactly `candidate_id`.
- `kb_creator.viral_boundary_ledger.v1`: JSON object with `schema`, `units`, `candidate_dispositions`, and `deferred_nonblocking`; `target_unit_id` is a same-file unit reference, not an independent declaration.
- `kb_creator.semantic_unit_closure.v2`: JSON object with `schema`, empty `unresolved_blocking_candidates`, and `deferred_nonblocking` ids.
- `kb_creator.user_review_registry.md`: Markdown headings matching `### (OUT|PROC|ENH)-NNN - title` with the source's em dash form.

## Blockers

None for Phase A2 approval.

This was not a release review. Candidate revision/manifest freeze, release QA references, declared release exclusions, and release invalidation-on-mutation were not accepted here.

## Recommendation

`APPROVED_V2_COMPLETE_AUTHORING_PHASE_A2`

This approval authorizes only Phase A3 engineering. Real v2 config/helper execution, candidate materialization, visual QA, release review, publication, and any downstream output remain closed until separately assigned and reviewed.

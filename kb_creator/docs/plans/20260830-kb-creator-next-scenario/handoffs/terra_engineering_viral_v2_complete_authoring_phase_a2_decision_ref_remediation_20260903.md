# Viral v2 Phase A2 decision-reference P1 remediation receipt

- Scope/result: replaced broad decision-evidence tokenization with independent closed structured extractors in builder and verifier; production gates otherwise unchanged.
- Role: `nri-engineer` / requested `gpt-5.6-terra` / medium; orchestrator policy owner `gpt-5.6-sol` / medium; assignment state complete pending rereview; scoped override none.
- Timestamp: `2026-09-03T06:55:00+03:00`; elapsed approximately 20 minutes; token use unavailable.

## Implementation

`migration.inputs.decision_evidence` now has closed `path`, `bytes`, `sha256`,
and `kind`. Supported parsers are independent in each module:

- `kb_creator.semantic_unit_review.v2`: only closed
  `decisions[*].candidate_id` values are accepted;
- `kb_creator.user_review_registry.md`: only exact `### OUT-001 — ...`,
  `PROC-...`, or `ENH-...` heading ids are accepted.

Invalid UTF-8/JSON/schema/shape, unsupported kinds, empty or duplicate
catalogs, and arbitrary prose tokens reject. Fixtures bind a miniature real
semantic-review-v2 JSON file with the sole exact id
`viral-logical_table-p020-l025`; frozen v1 and scenario/common words are no
longer evidence ids.

## Changed file hashes

- `kb_creator/scripts/build_scenario_master_en.py` — `1DC9E01C118B0BE249C1ADA5A72988C39A9DE77348F4035EBA509027E45B797E`
- `kb_creator/scripts/verify_scenario_master_en.py` — `A94791923EE5B14F8C83C0247A2DCA83AAE27E8578FD02BB112941429AEEC843`
- `kb_creator/tests/test_build_scenario_master_en.py` — `BD9B8234F6ADA84A7E339EEC9EF7A0AD1F8A00EB01C4A4DC8780B458FFA61B05`
- `kb_creator/tests/test_verify_scenario_master_en.py` — `5C38DDBD0E3F6808598A97ADCA095A7F4F46ED9259900B6D788A235CE06206F9`
- This new immutable receipt only.

## Evidence and boundaries

- `py_compile` all four files: exit `0`.
- Focused builder/verifier suite: exit `0` (expanded suite after fixture changes).
- Real frozen-v1 builder/verifier preflights: `preflight_passed`; frozen config
  SHA `C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30`.
- Scoped `git diff --check`: exit `0`.
- Real v2 config, accepted-v4 `INVENTORY.json`, and decision-remediation probe
  candidate are absent. No helper/config/candidate/A3/input/evidence/Git or
  downstream output was changed.

Remaining action: fresh independent critic rereview; all A2 pending-A3 and
orphan/count/page-exclusion gates remain active.

Terminal status:

`READY_FOR_V2_COMPLETE_AUTHORING_PHASE_A2_REREVIEW`

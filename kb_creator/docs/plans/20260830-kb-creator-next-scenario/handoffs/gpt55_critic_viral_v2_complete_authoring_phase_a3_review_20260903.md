# Viral v2 complete authoring Phase A3 - independent implementation review receipt

## Receipt metadata

- Goal id: `20260830-kb-creator-next-scenario`.
- Step id: `viral-v2-complete-authoring-phase-a3-review`.
- Review kind: `implementation`.
- Candidate state: hash-bound non-release implementation checkpoint; not a frozen release candidate.
- Critic role: `nri-independent-critic` / requested `gpt-5.5` / high.
- Implemented candidate: no.
- Materially designed candidate: no.
- Orchestrator policy owner: main chat / `gpt-5.6-sol` / medium.
- Assignment state: `matched` by packet; actual platform runtime/model not independently verifiable from this receipt.
- Scoped override: none.
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`.
- Timestamp: `2026-09-03T08:22:30.6662340+03:00` (Europe/Moscow).
- Elapsed time: 620 seconds at pre-receipt token capture.
- Token use: 159403 at pre-receipt capture.

This is not a release review. No release candidate revision, manifest freeze,
release QA references, declared release exclusions or release invalidation rule
is accepted by this receipt.

## Files checked

- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/TASK_PACKET_gpt55_critic_viral_v2_complete_authoring_phase_a3_review_20260903.md`
- `docs/governance/nri_goal_governance.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/plan.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/context.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/TASK_PACKET_terra_engineering_viral_v2_complete_authoring_phase_a3_20260903.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/sol_architect_viral_v2_complete_publication_authoring_20260903.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_v2_complete_authoring_phase_a2_rereview_20260903.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_v2_complete_authoring_phase_a3_20260903.md`
- `kb_creator/scripts/build_scenario_master_en.py`
- `kb_creator/scripts/verify_scenario_master_en.py`
- `kb_creator/tests/test_build_scenario_master_en.py`
- `kb_creator/tests/test_verify_scenario_master_en.py`
- `kb_creator/working/viral/master_en/publication_config_v1.json`
- `kb_creator/reference/viral/master_en/publication_config_v1.json`
- Forbidden-output and scratch paths under `kb_creator/working/viral/master_en`, `kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4`, `kb_creator/working/synthetic` and top-level `kb_creator/.v2-*`.

## Bound identity evidence

All packet-bound review identities matched before review:

- Architecture receipt: `39F9B514F82ABAAD58D0A637E07C395206E57BED7106864EC0247A9477E24ADC`.
- A2 independent approval: `F1F0877A90A2B66453C024B2C63BEADD85049FA97A29663F6DA12E96F66AF996`.
- A3 engineering receipt: `7ABD62C980DC04CC2820C094F0A08B395E8907DCA45A9C9729E96239C9E0E9F0`.
- Builder: `1D2AD6F46F38C7669763A689E04901B99D491F444FD72C0B544E3CC487484F8C`.
- Verifier: `224C812F73B3C04F9E983759351B07695D0928CA83B39A2A15982333C9B43BAB`.
- Builder tests: `84EDE819E5D407D9D6287491657DB930769F613B3785D84EADFACCCFFA2FC199`.
- Verifier tests: `2A7403E71DFB60CF5A0E6E6C8D93BFB62B964995C3F5E52000C7AA80E202B93E`.

No hash drift was found. The invalid historical A3 READY receipt named by the
packet was not used as approval evidence.

## Required command evidence

- `python -B -m py_compile kb_creator\scripts\build_scenario_master_en.py kb_creator\scripts\verify_scenario_master_en.py kb_creator\tests\test_build_scenario_master_en.py kb_creator\tests\test_verify_scenario_master_en.py`: exit `0`.
- First focused baseline:
  `python -B -m unittest -q kb_creator.tests.test_build_scenario_master_en kb_creator.tests.test_verify_scenario_master_en` ran `95` tests in `55.963s` and failed once with Windows `PermissionError [WinError 5]` while renaming `.v2-asset.staging.*` to `v2-asset`.
- Immediate focused rerun: same command ran `95` tests in `55.030s`, `OK`; no synthetic scratch remained after the failed run.
- Required four-module baseline:
  `python -B -m unittest -q kb_creator.tests.test_build_scenario_master_en kb_creator.tests.test_verify_scenario_master_en kb_creator.tests.test_build_master_en_visual_qa_bundle kb_creator.tests.test_propose_scenario_semantic_units` ran `95` tests in `55.111s`, `OK`.
- Required reverse four-module baseline:
  `python -B -m unittest -q kb_creator.tests.test_propose_scenario_semantic_units kb_creator.tests.test_build_master_en_visual_qa_bundle kb_creator.tests.test_verify_scenario_master_en kb_creator.tests.test_build_scenario_master_en` ran `95` tests in `54.727s`, `OK`.
- Frozen-v1 builder preflight-only passed with contract `67688867D4971D55137C2E4E7A71A746199596EDE4F5DD18577F4331CA87536D`, reconstruction inventory `68C17FB765A89C6146398868E61F1F6EB7B2FE4EAFBA8C2C2C8F42260BBDBA83`, source `0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05`.
- Frozen-v1 verifier preflight-only passed with publication config `C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30`.
- Scoped `git diff --check` over the four assigned modules: exit `0`.
- Verifier import check found no `import build_scenario_master_en`, `from build_scenario_master_en`, `kb_creator.scripts.build_scenario_master_en`, or `scripts.build_scenario_master_en` in `kb_creator/scripts/verify_scenario_master_en.py`.

## Forbidden-output evidence

Absent after review commands and probes:

- `kb_creator/working/viral/master_en/publication_config_v2.json`.
- `kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4/INVENTORY.json`.
- `kb_creator/working/viral/master_en/candidates/accepted-v4/INVENTORY.json`.
- `kb_creator/working/viral/master_en/phase_a3_review_preflight_target`.
- `kb_creator/working/synthetic`.
- Scoped probe roots `kb_creator/.v2-inputs-a3-review-*`.

Pre-existing scratch-like directories remain under `kb_creator/` and were not
deleted because this review may write only this receipt:

- `.v2-inputs-critic-path-probe`, created/modified `2026-09-03T04:37:42+03:00`.
- `.v2-inputs-debug`, created/modified `2026-09-03T07:34:50+03:00`.
- `.v2-inputs-debug2`, created/modified `2026-09-03T07:35:05+03:00`.
- `.v2-inputs-debug3`, created/modified `2026-09-03T07:35:17+03:00`.
- `.v2-inputs-debug4`, created/modified `2026-09-03T07:35:34+03:00`.
- `.v2-inputs-debug5`, created/modified `2026-09-03T07:36:21+03:00`.

## Adversarial probe evidence

Temporary synthetic probes were removed after execution. The following results
were independently observed against both builder and verifier:

```text
equipment_title_only|builder_input|ACCEPT
equipment_title_only|verifier_input|ACCEPT
equipment_title_only|builder_schema|ACCEPT
equipment_title_only|verifier_schema|ACCEPT
creature_title_only|builder_input|ACCEPT
creature_title_only|verifier_input|ACCEPT
creature_title_only|builder_schema|ACCEPT
creature_title_only|verifier_schema|ACCEPT
map_no_asset_ids|builder_input|ACCEPT
map_no_asset_ids|verifier_input|ACCEPT
map_no_asset_ids|builder_schema|ACCEPT
map_no_asset_ids|verifier_schema|ACCEPT
pair_no_asset_ids|builder_input|ACCEPT
pair_no_asset_ids|verifier_input|ACCEPT
pair_no_asset_ids|builder_schema|ACCEPT
pair_no_asset_ids|verifier_schema|ACCEPT
a3_xref_shape|builder_input|ACCEPT
a3_xref_shape|verifier_input|ACCEPT
a3_xref_shape|builder_schema|REJECT|ValueError|v2 xref mismatch
a3_xref_shape|verifier_schema|REJECT|ValueError|E_C2B_SCHEMA: v2-xref
heading_suppress_operation|builder|ACCEPT
heading_suppress_operation|verifier|ACCEPT
structured_bogus_contains|builder|ACCEPT
structured_bogus_contains|verifier|ACCEPT
asset_row_points_to_event_owned_text_span|builder|ACCEPT
asset_row_points_to_event_owned_text_span|verifier|ACCEPT
```

## Severity findings

P1 - A3 xrefs are internally unbuildable through the top-level schema.

The A3 validator requires `xrefs` rows to contain `source_slices` and
`migration_row_id` and validates visible text from exact source slices in both
modules. The earlier top-level v2 schema still requires xrefs to contain only
`xref_id`, `source_event_id`, `source_page`, `target_anchor` and `reader_text`.
Evidence: builder `v2_a3_validate()` accepts the A3 xref shape, but
`v2_config()` rejects it with `v2 xref mismatch`; verifier `v2_a3_validate()`
accepts the A3 shape, but `v2_contract()` rejects it with
`E_C2B_SCHEMA: v2-xref`. A real Phase B config with the required source-slice
xref proof cannot pass CLI preflight/build/verify.

P1 - Source operations are not type-compatible.

Both implementations accept a heading event with `source_operation: suppress`.
The code checks only membership in the global operation enum, not the legal
operation for the event type or whether the operation emits/suppresses reader
content consistently. This fails the A3 seam requiring strict source-span
ownership and source operations for headings, text, typed structures,
navigation, recoveries, suppressions and asset references.

P1 - `contains` is not closed to real span or child-event membership.

Both implementations accept a structured event whose `contains` list is
`["not-real"]` when the payload mirrors that value. The implementations verify
shape, order and duplication, but do not prove that every entry is a real
partition span id or real child event id. This directly misses the packet seam:
`contains` may contain only real span ids or real child-event ids and must close
exactly.

P1 - Asset source provenance is not owner-closed.

Both implementations accept an asset row whose `source_span_ids` points to an
event-owned ordinary-text span. The asset validator checks only that the span
exists and that reader placement names an event. It does not require the source
span owner to be the asset, does not enforce unique asset/source ownership, and
does not independently bind the asset-image-reference span to the logical
asset. This misses the required asset source-span, placement and reader-policy
closure.

P1 - Closed typed payload schemas are under-specified.

Both implementations accept minimal `equipment_card`, `creature_statblock`,
`full_page_map` and `physical_page_pair` payloads that omit source-bound fields
called out by the architecture and packet, including stat/footnote/body,
creature stat/attack/ability/nested-table content, reader asset ids, and
front/back asset membership. The tests prove only one leaf per typed kind can
be bound. They do not enforce the required omission/invention matrix for each
typed schema or the complete authorial leaf set.

P2 - Required scratch cleanliness is not globally clean.

No scratch from this review remains, and no real v2 config/candidate or
accepted-v4 inventory exists. However six pre-existing `kb_creator/.v2-inputs-*`
directories remain. Because the packet asks the reviewer to confirm no review
scratch remains and this critic may not delete unrelated/pre-existing scratch,
the orchestrator should classify and clean or explicitly waive those paths
before opening a later materialization gate.

## Blockers

Phase B author helper/config/candidate work is blocked by unresolved P1 A3
validator gaps. The candidate does not independently enforce every listed A3
seam in both builder and verifier.

No blocker prevented completion of this review receipt.

## Recommendation

`CHANGES_REQUIRED_V2_COMPLETE_AUTHORING_PHASE_A3`

Remediation should align the top-level v2 schema with the A3 xref contract,
make source operations type-specific, close `contains` to actual span/event
membership, bind asset source spans to asset owners, and implement the full
kind-specific typed payload omission/invention matrix in both independent
modules and their tests. Phase B must remain closed until a fresh independent
A3 review finds no P0/P1.

CHANGES_REQUIRED_V2_COMPLETE_AUTHORING_PHASE_A3

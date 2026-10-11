# Engineer verification receipt — replay HR3 visual/OCR equivalence (Packet I-C)

Date: 2026-09-15  
Role: engineering, `gpt-5.6-sol`, high (user-scoped override)  
Result: **bounded relevant broad verification PASS; ready for independent implementation review**

## Scope and mutation boundary

This packet was verification-only. No feature, refactor, live replay, replay target, run-07 artifact, decision, source, `.tools` payload, canonical plan/status/context, or upstream S1–S4 closure member was changed. The only new file is this receipt.

## Relevant broad regression

Command used the repository-local test dependencies through `PYTHONPATH=.tools/python-test-deps` and selected:

- `test_reconstruction_replay.py`
- `test_reconstruction_replay_resume.py`
- `test_audit_mineru_ai_merge_fidelity.py`
- `test_materialize_mineru_ai_merge.py`
- `test_reconstruction_control_plane.py`
- `test_reconstruction_promotion.py`
- `test_reconstruction_promotion_adversarial.py`
- `test_production_package_verifier.py`

Result: **261 passed, 2 skipped in 63.44s**.

This includes replay HR1/HR2, replay-resume, audit v1/v2/v3, materializer/provenance, reconstruction promotion, production-package anti-downgrade, and reconstruction control-plane coverage. The Packet I synthetic test exercises fresh replay-04 authorities → immutable decision snapshot → real Stage05 v3 audit → real Stage06 materialization, validates all emitted schema instances, and proves no inferred acceptance.

## Compile, schema, and diff checks

- `py_compile`: PASS for `reconstruction_replay.py`, `reconstruction_replay_resume.py`, `reconstruction.py`, `reconstruction_promotion.py`, audit, materializer, and `kb_creator.__main__`.
- `Draft202012Validator.check_schema`: **6/6 PASS** for the new submission, downstream stage, resume result, allowlist v3, audit v3, and provenance v3 contracts.
- Emitted-instance validation: PASS through the synthetic E2E for submission, both Stage05/06 manifests, audit, provenance, and resume result.
- Scoped `git diff --check`: PASS.

## Run-07 read-only full04 eligibility

The only live-project command was read-only:

```text
python -m kb_creator replay verify-source ... --source-run-root kb_creator/working/dissociation/reconstruction/20260915-cpu-first-07 --through-stage 04 --json
```

Result:

- state: `eligible`
- source run: `20260915-cpu-first-07`
- source run identity: `3F7F9B4765D79BCDA5A3BBCC8EAB22723C2063161E2C31B65A3843507F81E40A`
- eligibility seal: `6264B4D1A3A5FDD0DB2944F2E925C3DEEDA9673688FE00BE869DADD073115114`
- requested prefix: exact ordered Stage01–04
- `decisions_replayed`: false
- `stages_05_06_replayed`: false
- `acceptance_inferred`: false

No `replay run` or `replay resume` command was executed and no target root was supplied or created.

## Exact upstream closure proof

`_closure_for()` compared every current file identity to the run-07 sealed implementation inventory. It returned no mismatch and exactly **19 unique closure members**.

Stage closure identities:

- Stage01, 10 rows: `943B3ED924167FC1648815FA40610C5A2061F5760C7F9773AB832A5A9A9E0B89`
- Stage02, 12 rows: `E386EB483F76ECD87AEEF267030FB897D0211A88570ED77384D8D7B53233202A`
- Stage03, 11 rows: `BF1903B2BFB10811D48A69ECFBA53B8C51FD2B3036D4661D82C8C79C4E0C69A6`
- Stage04, 14 rows: `44DC6F29489E778DA420B02E7BB1528B3ECB01D663CAF72705390B07D0589AC1`

Unique file identities (`path` → `SHA-256`):

1. `MinerU/scripts/probe-capability.ps1` → `5F08FA113A31C5788DD754916FF1697D7610296E555099570689CDC0FA91A559`
2. `kb_creator/contracts/mineru_geometry_failure.v1.schema.json` → `65BA80EAC124791FA2C43DD5D02F1F4438157FF523F504C418873316E195B32C`
3. `kb_creator/contracts/mineru_geometry_plan.v1.schema.json` → `60C85ABB034BD5501E46AC334500D65E14B1CD37014DD09B7A2204DF3354B9F3`
4. `kb_creator/contracts/mineru_multi_view_comparison.v2.schema.json` → `DCBB80C16D4660E40E3999B44F230EF9E41BCC555275548425C96577C824ED23`
5. `kb_creator/contracts/mineru_three_view_inputs.v2.schema.json` → `6ABDBF70D51EA8901C65F2402F0E2D6D2F54BB8D4A4DA2EDA1A417F0AA008F3D`
6. `kb_creator/contracts/mineru_view_execution.v1.schema.json` → `74B41E5631555772D6A18A27291A4EF849883524A5C996684FE964081AE1B4A1`
7. `kb_creator/contracts/mineru_view_set.v1.schema.json` → `9D72BD7779F7FF48282E4FE0F55AF5390F179F5A62B42EB296E514FB68975768`
8. `kb_creator/contracts/mineru_visual_merge_bundle.v2.schema.json` → `FC3C293A1A1937F76E1886F7DBE89FF3D338D38C366E4618EB9B0B30D18CAA7A`
9. `kb_creator/contracts/run_spec.v2.schema.json` → `41D990851E80E5D1E2E03024EB3AB2A4ECC9986444FD5B5D4593F39A5F2A41CB`
10. `kb_creator/pipeline/identity.py` → `75F1F9224BAA3746E37545AE8C75FCD2F68E221C8926537C764B8F29F6DA971B`
11. `kb_creator/pipeline/manifests.py` → `94A75FAC95472329C6901B901F6CF21AD1F704AC78F9CD03165C8BA0502BBC2D`
12. `kb_creator/pipeline/mineru_cpu_first.py` → `7B1D0551EBE3C2FF160602F03A8796D0603704521FAA46CF5C1983AB39ACF7C1`
13. `kb_creator/pipeline/process.py` → `1B16346EF61723F5F166D1442802D5350224897D24899FE788B53AEB36304A9C`
14. `kb_creator/pipeline/reconstruction.py` → `81BE7DF8B95DA4B8BE970A8D557A28B79BDFA128F951E1F947F1299C702516B0`
15. `kb_creator/pipeline/windows_process_tree.py` → `E4737A8CABFAEF5EEFDAA148FBA518A3626E954BC21326E77FA822B5663A9D52`
16. `kb_creator/scripts/build_mineru_visual_merge_bundle.py` → `1CCE5E4F4FC3E69CB7107F97EF4A8380969BFE8D234616ECD2ED8806C8507FE6`
17. `kb_creator/scripts/compare_mineru_three_views.py` → `617807C8C6279AEF74051B26C6A985ECE62E55504FFBBD17F4A2DBA2F2A6C129`
18. `kb_creator/scripts/prepare_mineru_three_view_inputs.py` → `FC33B22E251E2F7FC64F1E0E00B039C6F086DA98F3326F773E35044FD4B8F793`
19. `kb_creator/scripts/run_mineru_three_view.ps1` → `088910A812AFD392F21FE90A7803D6EC0CE91817F743F7145682AF66750925C8`

## Verdict and next action

- P0: none found.
- P1: none found.
- P2: none found in this bounded relevant verification set.
- Engineering verification: **PASS**.
- Live replay: remains **NO-GO until independent critic implementation closure**.

Next action: independent critic review of Packet I implementation and this evidence. User acceptance and promotion remain separate explicit gates.

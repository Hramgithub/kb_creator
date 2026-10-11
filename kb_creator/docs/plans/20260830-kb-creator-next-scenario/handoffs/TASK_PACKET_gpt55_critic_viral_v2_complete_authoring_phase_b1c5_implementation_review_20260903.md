# Task packet — independent B1c5 visual-review implementation review

## Role and review declaration

- Reviewer: fresh independent `gpt-5.5` / high critic.
- `review_kind`: `implementation`.
- The critic must not implement, redesign, or edit the six scoped code/test files.
- Candidate state: non-frozen B1c5 implementation checkpoint, not a release and not a built `MASTER_EN` candidate.
- Orchestration ownership remains with the main chat (`gpt-5.6-sol` / medium).

## Goal

Independently decide whether B1c5 closes the deterministic visual-review declaration contract without weakening the reusable v2 pipeline or masking earlier A3/B1c4 validations.

## Bound implementation

Review only these six implementation/test files at the exact SHA-256 values below:

| File | SHA-256 |
|---|---|
| `kb_creator/scripts/author_viral_master_en_v2_config.py` | `3DA02ADF17E2224C86A1418D18ECB06754E1FC6CD628717C1652EA315968FE1C` |
| `kb_creator/tests/test_author_viral_master_en_v2_config.py` | `58ED6C9FF6FC5A67130830F3F4731A5D68695E6F7E6877B0D6E09786D51D5EAE` |
| `kb_creator/scripts/build_scenario_master_en.py` | `8055F7B355EB711474398C84263521C4B8001D852B2B53987523D5CBE9C4D6DD` |
| `kb_creator/tests/test_build_scenario_master_en.py` | `CE38BA49E996C414166F345D3127FC6303DEFD4949C5678D966F414D340B8555` |
| `kb_creator/scripts/verify_scenario_master_en.py` | `2CFEE758C2EDBC5F445E864EDB46E366EB07E7E19D6E19FBD64D6A99E9FF2ED5` |
| `kb_creator/tests/test_verify_scenario_master_en.py` | `61566BD4C76344CE36ACE6DC97FE94DD4E65A68176AACD21E8C11C28BFD195FA` |

Engineering receipts, in chronological order:

- `terra_engineering_viral_v2_complete_authoring_phase_b1c5_visual_review_declarations_20260903.md`
- `terra_engineering_viral_v2_complete_authoring_phase_b1c5_visual_review_declarations_addendum_20260903.md`
- `terra_engineering_viral_v2_complete_authoring_phase_b1c5_visual_review_declarations_third_addendum_20260903.md`, SHA-256 `91D264FAD1B7EAFAB3065A9A2175FFE401DB2EA7F750AA16F919F0AF9BD80995`

The earlier B1c4 approval receipt is:

- `gpt55_critic_viral_v2_complete_authoring_phase_b1c4_asset_identity_rereview_20260903.md`, SHA-256 `BBB983ADD8E97885B0B9FCF0226145F262BD857127853F9CCC33706E82FC2EED`

## Required invariants

1. Builder and verifier independently derive the exact visual-review unit list; they must not trust the authored list as their oracle.
2. Exact-list closure is universal. Reject any `scenario_id == 'viral'` bypass or equivalent scenario-specific weakening.
3. The current canonical projection has exactly 136 review units: 2 `heading_outline`, 41 `xref_recovery`, 93 `asset_placement`, 0 structured-event units.
4. IDs, ordering, page coverage, groups, and priorities are deterministic and source-bound.
5. Canonical assets use `source_page`; legacy fixtures may use `page`. Neither public validator may leak a raw `KeyError`.
6. Genuine row-ID, list, page-superset, group, priority, or referenced-object mutations must fail at B1c5 in both builder and verifier.
7. Unrelated A3/B1c4 graph mutations may refresh their synthetic fixture declaration so they reach the intended later validator; this must not create a production bypass.
8. Frozen-v1 behavior remains unchanged.
9. No canonical `publication_config_v2.json`, Candidate D, render/review bundle, `MASTER_EN`, `MASTER_RU`, HTML, PDF, or downstream output may be created.
10. The next unimplemented public-v2 seam must remain identical: builder `v2 asset provenance mismatch`; verifier `E_V2_ASSET: provenance`.

## Root evidence to reproduce

The orchestrator independently ran:

```text
python -m unittest -q kb_creator.tests.test_author_viral_master_en_v2_config kb_creator.tests.test_build_scenario_master_en kb_creator.tests.test_verify_scenario_master_en
----------------------------------------------------------------------
Ran 124 tests in 217.846s

OK
```

The critic must independently verify hashes, inspect the implementation and tests, run the scoped syntax/tests, run both frozen-v1 preflights, and run the guarded temporary public-v2 preflight pair. Temporary config files must be removed before the review ends.

## Adversarial review requirements

- Search for any scenario-name, fixture-name, test-only, environment, or call-path bypass of exact-list enforcement.
- Mutate at least one review row in each independently meaningful dimension: semantic ID/reference, ordering/list membership, page, group, and priority.
- Confirm that refreshing an unrelated synthetic graph mutation is test-fixture maintenance, not validation avoidance.
- Confirm builder and verifier do not share a trusted precomputed expected list.
- Confirm no protected historical candidate/staging root was modified or removed.

## Deliverable

Write one immutable review receipt under this handoff directory. Include:

- `review_kind: implementation`;
- statement that no candidate was implemented or materially designed;
- exact hashes checked;
- commands and results;
- adversarial probes and observed builder/verifier errors;
- P0/P1/P2 findings;
- one terminal decision:
  - `APPROVED_V2_COMPLETE_AUTHORING_PHASE_B1C5_IMPLEMENTATION`, or
  - `REJECTED_V2_COMPLETE_AUTHORING_PHASE_B1C5_IMPLEMENTATION`.

Do not edit implementation, tests, plan, context, status, or production artifacts.

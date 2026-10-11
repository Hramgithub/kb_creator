# Engineer receipt: Stage 10 MASTER_EN independent verifier wiring

Date: 2026-09-15  
Role: engineering, `gpt-5.6-sol/high` user override  
Authority: `architect_dissociation_master_en_stage10_execution_20260915.md`  
Authority SHA256: `1EED680D1E29E388A20BB9A1A7F9BEE794009B2B10DCA6AE86F562026FC87C57`

## Result

Implemented the narrow generic Stage 10 verifier wiring. The production MASTER_EN adapter now calls the existing independent `verify_v3_candidate()` after the v3 build and before any candidate files move into stage artifacts.

The adapter requires the verifier's exact closed result shape and exact bindings for:

- status `verified_candidate_pending_process_and_external_gates`;
- scenario id;
- candidate inventory SHA;
- `INVENTORY.json` file SHA;
- `MASTER_EN.md` SHA;
- derived runtime publication-config SHA;
- independently derived metrics.

The canonical verifier result is serialized as `evidence/MASTER_EN.verification.json`. It is included automatically in the Stage 10 evidence inventory and exposed as an exact identity in adapter diagnostics. The acceptance test records both producer QA and independent verification as producer-stage-local evidence, and confirms both identities are sealed into the separate MASTER_EN acceptance receipt.

Verifier errors propagate through the existing publication control plane. The whole partial staging tree is moved to the fixed Stage 10 quarantine; no output tree, successful stage manifest, or acceptance receipt is created.

No schema, builder semantics, verifier semantics, legacy adapter, or v1/v2 route was changed.

## Diff summary

- `kb_creator/pipeline/publication_adapters.py`
  - invokes `verify_v3_candidate` before `_move_children`;
  - validates exact result shape and all required identities;
  - writes canonical `MASTER_EN.verification.json` to stage evidence;
  - binds the verification identity in structured adapter diagnostics.
- `kb_creator/tests/test_publication_registry_e2e.py`
  - verifies positive Stage 10 report identity, stage-evidence closure, and acceptance evidence binding;
  - adds post-build MASTER_EN tamper rejection and quarantine assertions;
  - adds CRLF-to-LF-only serialization coverage with ten source hard breaks plus compact consecutive HUMAN RESISTANCE statblock lines.
- `kb_creator/tests/test_publication_control_plane.py`
  - adds one optional byte-valued fixture input so the narrow CRLF Stage 10 case can construct a fully identity-bound accepted reconstruction package; all existing callers retain their original fixture bytes.

## Verification

Focused publication control-plane plus production registry:

```text
.tools/MinerU/.venv/Scripts/python.exe -m pytest -q -rs \
  kb_creator/tests/test_publication_control_plane.py \
  kb_creator/tests/test_publication_registry_e2e.py
37 passed in 87.85s
```

Final registry-only rerun after exact identity assertions:

```text
.tools/MinerU/.venv/Scripts/python.exe -m pytest -q -rs \
  kb_creator/tests/test_publication_registry_e2e.py
5 passed in 12.70s
```

Self-contained direct-v3 builder/verifier regression:

```text
.tools/MinerU/.venv/Scripts/python.exe -m pytest -q -rs \
  kb_creator/tests/test_build_scenario_master_en.py::MasterEnV3NeutralTests
3 passed in 0.54s
```

Syntax check: `syntax-ok` for all three changed Python files.

The broad `test_build_scenario_master_en.py` suite was also attempted: `17 passed, 63 failed`. Every observed failure is an existing environment/fixture blocker outside this packet: the Viral source reconstruction package and source PDF are absent, and the frozen Viral `publication_config_v1.json` identity is already drifted. The self-contained direct-v3 class above passes and no failure implicated the Stage 10 adapter change.

No live publication, acceptance, MinerU, CPU, Word, Poppler, or renderer command was run.

## Changed-file identities

| Path | Bytes | SHA256 |
|---|---:|---|
| `kb_creator/pipeline/publication_adapters.py` | 45018 | `9F3ECF51BF37752302E586022842E6D2D1EF55A300681E6D3064B189EB7448AF` |
| `kb_creator/tests/test_publication_registry_e2e.py` | 19801 | `E515AFF7E0F1329B07BC00E61F8714180D3A4ABA3D0C7BBB17C56D5A061FA298` |
| `kb_creator/tests/test_publication_control_plane.py` | 52070 | `977D272D3A9697A7906E7B3491B8DCF94E5DDA2319C15B901B75764222B0C93F` |

## Findings

- **P0:** none.
- **P1 resolved:** Stage 10 can no longer publish a v3 candidate based only on producer-authored QA.
- **P2:** the broad Viral builder suite cannot be used as a clean repository-wide signal on this checkout because its immutable external fixture authorities are absent/drifted. Narrow self-contained v3 and publication regressions are green.

## Blockers and next action

- Implementation blockers: none.
- External live Stage 10 prerequisites remain those owned by the parallel declarative-config packet and independent review.
- Not performed: no Dissociation config/run/package mutation, no live Stage 10, no acceptance, no commit, no push.
- Next action: independent QA/release review of this bounded wiring; if approved together with the declarative config packet, the orchestrator may execute only live Stage 10 and stop at the MASTER_EN user gate.

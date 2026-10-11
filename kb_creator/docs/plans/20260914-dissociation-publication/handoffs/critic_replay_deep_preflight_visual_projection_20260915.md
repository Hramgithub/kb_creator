# Critic receipt: replay deep-preflight and visual projection closure

- Timestamp: 2026-09-15T05:49:58+03:00
- Review kind: implementation
- Reviewer role: independent critic, gpt-5.5/medium per assignment
- Candidate implemented or materially designed by reviewer: no
- Orchestrator policy owner: main NRI orchestrator remains owner; this review does not transfer orchestration ownership
- Assignment state: completed
- Scoped override: focused J3/J3b closure only; no implementation edits, no live replay, no run/decision/source/.tools mutation, no broad suite, no network/GPU/remote/API/Git commit
- Receipt immutability: this file is the only intended change by this review

## Authority and files checked

Authority:

- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_replay_visual_projection_remediation_20260915.md`
- Prior J/J2 closure receipts for content-list and JSON artifact census remediation
- Read-only immutable source run: `kb_creator/working/dissociation/reconstruction/20260915-cpu-first-07`

Implementation and tests inspected:

- `kb_creator/pipeline/reconstruction_replay.py`
- `kb_creator/__main__.py`
- `kb_creator/contracts/replay_transform_preflight.v1.schema.json`
- `kb_creator/tests/test_reconstruction_replay.py`

## Evidence

Static review:

- The J3 trusted-source-root fix resolves `source_run_root` once at `replay_run_engine(...)`/`verify_replay_transform(...)` entry. Stage03 expected root/artifact strings are constructed from that trusted root plus sealed relative inventory, not by dereferencing origin strings.
- The Stage03 comparison rebase body does not contain the previously risky `Path(str(identity...))` or `.resolve().relative_to(...)` pattern over origin identity strings.
- Deep preflight is exposed only as `python -m kb_creator replay verify-source ... --validate-rebase`; no `--run-root` or target is accepted on that route.
- `verify_replay_transform(...)` invokes the production `_rebase_*` transforms/validators in a temporary wrapper-only tree, scans payloads from the source outputs, writes no copied payloads, and returns a sealed `kb_creator.replay_transform_preflight.v1` report.
- Deep preflight coverage is closed: it validates Stage01 command; all five Stage02 view receipts and view-set; Stage03 comparison and command; Stage04 geometry, visual execution, visual manifest, and command. Wrapper cardinality and unique `(stage_id, source_path)` coverage are checked before success.
- Stage04 visual projection normalization is limited to the raw-vs-canonical reconstruction contract SHA representation. The raw legacy contract file SHA is separately checked against the current explicit contract file identity before canonical contract SHA is used for source/fresh projection comparison.
- Visual/content evidence remains projected or independently bound: source SHA, canonical contract SHA, DPI, layout SHA, counts, inventory scope/exclusions, every non-geometry visual file path/bytes/SHA, geometry plan identity/seal, source execution inventory, and PNG dimensions via execution/geometry validation.

Read-only deep preflight run:

```text
python -m kb_creator replay verify-source --through-stage 04 --validate-rebase --json ...
=> returncode 0
```

Summary:

```json
{
  "schema": "kb_creator.replay_transform_preflight.v1",
  "state": "pass",
  "wrapper_count": 13,
  "unique_wrappers": 13,
  "payload_count_scanned": 71,
  "payloads_copied": false,
  "target_created": false,
  "published": false,
  "acceptance_inferred": false,
  "eligibility_sha256": "6264B4D1A3A5FDD0DB2944F2E925C3DEEDA9673688FE00BE869DADD073115114",
  "preflight_sha256": "5660E73DFD5899425289B9EC55FC9C2C3B464B960BEFF72226E5BDC3FFF3A2E8",
  "wrapper_kinds": [
    "command",
    "view",
    "view",
    "view",
    "view",
    "view",
    "view_set",
    "comparison",
    "command",
    "geometry",
    "visual_execution",
    "visual_manifest",
    "command"
  ]
}
```

Focused tests:

```text
PYTHONPATH=.tools/python-test-deps python -m pytest -q kb_creator/tests/test_reconstruction_replay.py -k "preflight or visual_projection or comparison_rebase or synthetic_full_prefix_replay or run07_json_artifact_census or json_payload"
=> 48 passed, 69 deselected in 3.38s
```

Direct probes:

- Stage03 comparison rebase body avoids resolving origin identity strings: passed.
- Poisoned Stage03 root failed as `origin_comparison_root_mismatch: v`.
- Visual projection ignored only guarded legacy representation fields: source path, contract path, raw receipt path, raw root, layout path, execution command, PNG dimensions, and legacy geometry file row identity remained projection-equal.
- Visual projection still changed on semantic/content fields: source SHA, DPI, layout SHA, counts, inventory scope, inventory exclusions, visual file path, visual file bytes, and visual file SHA.

Static/schema/format checks:

```text
python -m py_compile kb_creator/pipeline/reconstruction_replay.py kb_creator/__main__.py kb_creator/tests/test_reconstruction_replay.py
=> passed

Draft202012Validator.check_schema(...) for 10 replay/v3 schemas including replay_transform_preflight.v1
=> schema_ok 10

git diff --check -- kb_creator/pipeline/reconstruction_replay.py kb_creator/__main__.py kb_creator/contracts/replay_transform_preflight.v1.schema.json kb_creator/tests/test_reconstruction_replay.py
=> exit 0
```

Ordinary run-07 eligibility remained unchanged:

```json
{
  "state": "eligible",
  "requested_prefix": [
    "01-prepare-inputs",
    "02-mineru-three-view",
    "03-compare-views",
    "04-visual-merge-bundle"
  ],
  "eligibility_sha256": "6264B4D1A3A5FDD0DB2944F2E925C3DEEDA9673688FE00BE869DADD073115114",
  "source_run_identity_sha256": "3F7F9B4765D79BCDA5A3BBCC8EAB22723C2063161E2C31B65A3843507F81E40A",
  "decisions_replayed": false,
  "stages_05_06_replayed": false,
  "acceptance_inferred": false
}
```

## Findings

### P0

None found.

### P1

None found.

### P2

None found.

## Blockers

None for the bounded live full04 replay decision. This review does not approve reconstruction acceptance, promotion, or Stage05/06 resume.

## Recommendation

GO for the next live full04 replay from run `20260915-cpu-first-07`.

This GO is limited to retrying the Stage01-04 replay bridge/materialized prefix path after the J3/J3b deep-preflight and visual-projection remediation. It is not reconstruction acceptance and does not authorize Stage05/06 resume unless separately valid reviewed allowlist/decisions are present and validated.

## Elapsed time and token use

- Elapsed wall time: approximately 20 minutes
- Reviewer token use: unavailable exactly in this environment; approximately 14k tokens

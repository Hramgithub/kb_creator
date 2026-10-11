# Critic receipt: replay MinerU content-list array remediation closure

- Timestamp: 2026-09-15T05:09:37+03:00
- Review kind: implementation
- Reviewer role: independent critic, gpt-5.5/medium per assignment
- Candidate implemented or materially designed by reviewer: no
- Orchestrator policy owner: main NRI orchestrator remains owner; this review does not transfer orchestration ownership
- Assignment state: completed
- Scoped override: focused remediation J review only; no implementation edits, no live replay, no run/decision/source/.tools mutation, no broad suite, no network/GPU/remote/API/Git commit
- Receipt immutability: this file is the only intended change by this review

## Authority and files checked

Authority:

- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/critic_replay_hr3_visual_ocr_equivalence_implementation_closure_20260915.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_replay_mineru_content_list_array_remediation_20260915.md`

Implementation and tests inspected:

- `kb_creator/pipeline/reconstruction_replay.py`
- `kb_creator/tests/test_reconstruction_replay.py`
- `kb_creator/tests/test_reconstruction_replay_resume.py`
- `kb_creator/tests/test_audit_mineru_ai_merge_fidelity.py`
- `kb_creator/tests/fixtures/mineru_content_list_array.sanitized.json`
- run-07 source eligibility evidence via `kb_creator/working/dissociation/reconstruction/20260915-cpu-first-07/run.json`

## Evidence

Static review:

- The MinerU array exception is narrowly routed by `_is_mineru_content_list_payload(...)` to `views/<view>/artifacts/**/<name>_content_list.json`.
- `_content_list_v2.json` is not matched by that route and remains under ordinary JSON object validation.
- `_read_mineru_content_list(...)` requires valid UTF-8 JSON and a top-level array; an object on the exact route raises `invalid_mineru_content_list_shape`.
- Non-content-list JSON continues through `_json(...)`, preserving the top-level object requirement and rejecting arbitrary arrays as `invalid_json_shape`.
- Recursive payload poison detection scans strings, list items, dictionary values, and dictionary keys for source identity, drive-absolute paths, UNC/device paths, POSIX absolute paths, traversal segments, and reserved Windows device components.
- Replay-prefix self-validation in `validate_replayed_prefix(...)` uses the same content-list parser only for Stage02 registered content-list payloads; other operational wrappers still use `_operational_authority_projection(...)` plus the prior wrapper poison scan. I found no operational wrapper weakening and no Stage05/06/acceptance route introduced.
- The remediation touches only the replay payload scanner/test fixture area; no upstream 19-path S1-S4 closure member was edited in this review.

Focused tests and probes:

```text
PYTHONPATH=.tools/python-test-deps python -m pytest -q kb_creator/tests/test_reconstruction_replay.py -k "content_list or payload_scan or synthetic_full_prefix_replay or run07 or operational"
=> 16 passed, 65 deselected in 1.75s
```

```text
PYTHONPATH=.tools/python-test-deps python -m pytest -q kb_creator/tests/test_reconstruction_replay.py kb_creator/tests/test_reconstruction_replay_resume.py kb_creator/tests/test_audit_mineru_ai_merge_fidelity.py
=> 128 passed in 5.00s
```

```text
python -m py_compile kb_creator/pipeline/reconstruction_replay.py kb_creator/tests/test_reconstruction_replay.py
=> passed
```

```text
git diff --check -- kb_creator/pipeline/reconstruction_replay.py kb_creator/tests/test_reconstruction_replay.py kb_creator/tests/fixtures/mineru_content_list_array.sanitized.json
=> exit 0
```

Independent direct probe:

- Sanitized real-shape top-level array at `views/v/artifacts/a/b/ok_content_list.json`: accepted.
- Nested drive path in dictionary key: rejected with `path_or_identity_poison_in_payload`.
- Nested UNC path in dictionary value: rejected with `path_or_identity_poison_in_payload`.
- Nested device path in list: rejected with `path_or_identity_poison_in_payload`.
- Nested POSIX absolute path: rejected with `path_or_identity_poison_in_payload`.
- Nested traversal segment: rejected with `path_or_identity_poison_in_payload`.
- Nested reserved device component: rejected with `path_or_identity_poison_in_payload`.
- Nested source run identity: rejected with `path_or_identity_poison_in_payload`.
- Top-level object at exact content-list route: rejected with `invalid_mineru_content_list_shape`.
- Top-level array at arbitrary `array.json`: rejected with `invalid_json_shape`.
- Top-level array at `doc_content_list_v2.json`: rejected with `invalid_json_shape`.

Run-07 read-only eligibility remained unchanged:

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

None for the bounded retry decision. This review does not approve reconstruction acceptance, promotion, or any future human-authored decision/allowlist content.

## Recommendation

GO for retrying the live full04 replay from run `20260915-cpu-first-07`.

This GO is limited to retrying the Stage01-04 replay bridge/materialized prefix path after the MinerU content-list array remediation. It is not reconstruction acceptance and does not authorize Stage05/06 resume unless the separately required reviewed allowlist/decisions are present and valid.

## Elapsed time and token use

- Elapsed wall time: approximately 10 minutes
- Reviewer token use: unavailable exactly in this environment; approximately 9k tokens

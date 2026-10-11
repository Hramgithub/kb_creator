# Critic receipt: run-07 replay JSON artifact shape census closure

- Timestamp: 2026-09-15T05:20:48+03:00
- Review kind: implementation
- Reviewer role: independent critic, gpt-5.5/medium per assignment
- Candidate implemented or materially designed by reviewer: no
- Orchestrator policy owner: main NRI orchestrator remains owner; this review does not transfer orchestration ownership
- Assignment state: completed
- Scoped override: focused J2 review only; no implementation edits, no live replay, no run/decision/source/.tools mutation, no broad suite, no network/GPU/remote/API/Git commit
- Receipt immutability: this file is the only intended change by this review

## Authority and files checked

Authority:

- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_replay_run07_artifact_shape_census_20260915.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/critic_replay_mineru_content_list_array_remediation_20260915.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/critic_replay_hr3_visual_ocr_equivalence_implementation_closure_20260915.md`

Implementation and test scope inspected:

- `kb_creator/pipeline/reconstruction_replay.py`
- `kb_creator/tests/test_reconstruction_replay.py`
- `kb_creator/tests/fixtures/run07_json_artifact_shape_census.sanitized.json`
- Read-only immutable source run: `kb_creator/working/dissociation/reconstruction/20260915-cpu-first-07`

I also searched the handoff and working trees for separate atomic live failure receipts/logs containing `content_list_v2`, `_model.json`, `invalid_json_shape`, `unknown_json_payload_route`, and related reason codes. No separate failure artifact was found in scope. The concrete failure classes reviewed here are therefore the two J2-census array gaps identified by the engineer receipt and code diff: MinerU `*_content_list_v2.json` arrays and MinerU `*_model.json` arrays.

## Evidence

Static review:

- `JSON_PAYLOAD_ROUTES` is a closed seven-route registry keyed by exact stage id, anchored relative-path expression, and top-level JSON shape:
  - `prepared_manifest`: Stage01, `prepared/sample_pages.json`, object
  - `mineru_content_list`: Stage02, `views/<view>/artifacts/**/<name>_content_list.json`, array
  - `mineru_content_list_v2`: Stage02, `views/<view>/artifacts/**/<name>_content_list_v2.json`, array
  - `mineru_middle`: Stage02, `views/<view>/artifacts/**/<name>_middle.json`, object
  - `mineru_model`: Stage02, `views/<view>/artifacts/**/<name>_model.json`, array
  - `merge_index`: Stage04, `merge_packets/merge_index.json`, object
  - `merge_packet`: Stage04, `merge_packets/pages/page-NNN.json`, object
- `_json_payload_route(...)` fails if a JSON payload route has zero or multiple matches, using `unknown_json_payload_route`.
- `_read_json_payload(...)` enforces the registered top-level shape and rejects wrong shapes as `invalid_json_payload_shape`.
- `_scan_payload(...)` applies recursive poison scanning to the registered payload value. The poison scan covers nested strings, list items, dictionary values, and dictionary keys.
- Typed operational wrappers are still classified separately by `_classify(...)` and `_WRAPPER_SUFFIXES`; they are not routed through the path-neutral JSON payload registry.
- Post-copy replay-prefix validation uses the same registered payload route for Stage01-04 JSON payloads and keeps typed-wrapper validation on the operational authority projection path.
- I found no change to upstream producer implementation files in the review scope. Run-07 source eligibility, including the 19-file upstream closure, remained unchanged by read-only verification below.

Focused tests:

```text
PYTHONPATH=.tools/python-test-deps python -m pytest -q kb_creator/tests/test_reconstruction_replay.py -k "json_payload or census or content_list or payload_scan or synthetic_full_prefix_replay"
=> 29 passed, 67 deselected in 1.69s
```

Static/format checks:

```text
python -m py_compile kb_creator/pipeline/reconstruction_replay.py kb_creator/tests/test_reconstruction_replay.py
=> passed

git diff --check -- kb_creator/pipeline/reconstruction_replay.py kb_creator/tests/test_reconstruction_replay.py kb_creator/tests/fixtures/run07_json_artifact_shape_census.sanitized.json
=> exit 0
```

Independent direct run-07 census equality probe:

```json
{
  "matches": true,
  "total": 33,
  "typed": 13,
  "payloads": 20,
  "fixture_sha256": "8D50175CFB17C421A2589B051A5529C58F3514A5D2B4708CC687A10FCB53D1EF",
  "observed_classes": {
    "typed_command": 3,
    "typed_view_set": 1,
    "typed_view": 5,
    "typed_comparison": 1,
    "typed_visual_execution": 1,
    "typed_geometry": 1,
    "typed_visual_manifest": 1,
    "prepared_manifest": 1,
    "mineru_content_list": 3,
    "mineru_content_list_v2": 3,
    "mineru_middle": 3,
    "mineru_model": 3,
    "merge_index": 1,
    "merge_packet": 6
  }
}
```

This read-only probe enumerated every `*.json` under run-07 `outputs/01-prepare-inputs` through `outputs/04-visual-merge-bundle`, classified each file with the production `_classify(...)` and `_json_payload_route(...)`, checked top-level shape, and compared the observed class/kind/shape/count map to the sanitized fixture. It confirmed 33 total JSON artifacts: 13 typed operational wrappers and 20 path-neutral payloads.

Fixture leakage check:

- `kb_creator/tests/fixtures/run07_json_artifact_shape_census.sanitized.json` contains only schema, source run id, scope, counts, class ids, authority kind, top-level shape, observed counts, and bearing field names.
- Search found no absolute user paths, Windows/UNC path literals, private source path fragments, source narrative text, Markdown content, or scenario prose in the fixture.

Independent direct poison and unknown-route probes:

- All seven registered payload classes accepted their registered good shape.
- All seven registered payload classes rejected nested traversal/source-identity poison with `path_or_identity_poison_in_payload`.
- Unknown JSON arrays under Stage02 artifact paths and invalid Stage04 merge-packet paths were rejected with `unknown_json_payload_route`.

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

None for the bounded retry decision. This review does not approve reconstruction acceptance, promotion, or Stage05/06 resume.

## Recommendation

GO for the next live full04 replay retry from run `20260915-cpu-first-07`.

This GO is limited to retrying the Stage01-04 replay bridge/materialized prefix path after the J2 JSON artifact shape census remediation. It is not reconstruction acceptance and does not authorize Stage05/06 resume unless separately valid reviewed allowlist/decisions are present and validated.

## Elapsed time and token use

- Elapsed wall time: approximately 12 minutes
- Reviewer token use: unavailable exactly in this environment; approximately 11k tokens

# Engineer receipt: run-07 replay JSON artifact census

Date: 2026-09-15  
Role: engineering, `gpt-5.6-sol` / high (user-scoped override)  
Result: PASS — Packet J2 is review-ready. No live replay was run.

## Scope and invariants

- Read-only census source: immutable `20260915-cpu-first-07`, outputs for Stages 01–04 only.
- No run, source, decision, `.tools`, upstream S1–S4 closure, canonical plan/status/context, or acceptance state was modified.
- Replay remains fail-closed: typed operational wrappers retain their existing typed projection/authority validation. The new registry applies only to explicitly observed path-neutral JSON payload routes.

## Pre-edit census evidence

The census was completed before scanner edits. It found exactly 33 JSON files, comprising 13 typed operational wrappers and 20 path-neutral payloads. There were 14 closed classes and no unclassified live route after comparison with the typed-wrapper router and the new explicit payload registry.

| Class | Kind | Top-level shape | Count | Relevant nested fields observed (names only) |
|---|---|---:|---:|---|
| `typed_command` | typed wrapper | object | 3 | `argv`, `environment` |
| `typed_view_set` | typed wrapper | object | 1 | run identity; view receipt path/SHA |
| `typed_view` | typed wrapper | object | 5 | run identity; artifact root; output inventory path/SHA |
| `typed_comparison` | typed wrapper | object | 1 | run identity; manifest/view-set paths; view roots |
| `typed_visual_execution` | typed wrapper | object | 1 | commands; output inventory path/SHA |
| `typed_geometry` | typed wrapper | object | 1 | run identity; comparison path hint; rendered-page paths |
| `typed_visual_manifest` | typed wrapper | object | 1 | input/layout/file paths |
| `prepared_manifest` | path-neutral payload | object | 1 | source path name; raster SHA |
| `mineru_content_list` | path-neutral payload | array | 3 | item image path |
| `mineru_content_list_v2` | path-neutral payload | array | 3 | nested content image-source path |
| `mineru_middle` | path-neutral payload | object | 3 | nested paragraph/preprocess span image paths |
| `mineru_model` | path-neutral payload | array | 3 | none observed |
| `merge_index` | path-neutral payload | object | 1 | none observed |
| `merge_packet` | path-neutral payload | object | 6 | none observed |

The sanitized deterministic census is `kb_creator/tests/fixtures/run07_json_artifact_shape_census.sanitized.json`, SHA-256 `8D50175CFB17C421A2589B051A5529C58F3514A5D2B4708CC687A10FCB53D1EF`. It records only route classes, shapes, counts, and field names; it contains no source narrative, private payload, or absolute user path.

## Implementation

- Added a closed `JSON_PAYLOAD_ROUTES` registry keyed by exact stage plus anchored relative-path expression and exact top-level shape.
- Registered all seven observed path-neutral payload classes: Stage01 prepared manifest; both MinerU content-list variants; MinerU middle and model payloads; Stage04 merge index and page packet.
- Unknown JSON payload routes, including arbitrary arrays, now fail with `unknown_json_payload_route`.
- A registered route with the wrong top-level shape fails with `invalid_json_payload_shape`.
- Every registered payload is recursively scanned through nested dictionaries, arrays, keys, and strings for drive/UNC/device/POSIX absolute paths, traversal, reserved Windows device names, and stale source-run identity poison.
- Post-copy prefix validation uses the same exact registry. Operational wrappers continue through the stricter typed authority projection; they were not downgraded to generic payload handling.

## Tests and checks

- Focused: `python -m pytest -q kb_creator/tests/test_reconstruction_replay.py` → **96 passed in 3.97s**.
- Coverage includes a positive exact-shape case and nested poison rejection for each of the seven registered payload classes, wrong-shape rejection, arbitrary/unknown array rejection, both MinerU content-list variants, and a read-only test proving the sanitized census equals all 33 live run-07 JSON artifacts.
- `py_compile` passed for `reconstruction_replay.py` and `test_reconstruction_replay.py`.
- JSON Schema Draft 2020-12 metaschema checks passed for **10** replay/v3 contracts.
- Scoped `git diff --check` passed.

## Read-only run-07 eligibility proof

`python -m kb_creator replay verify-source ... --through-stage 04 --json` returned `state=eligible`, the full requested Stage01–04 prefix, no acceptance inference, no decision replay, and eligibility SHA-256:

`6264B4D1A3A5FDD0DB2944F2E925C3DEEDA9673688FE00BE869DADD073115114`

The 19-file upstream producer closure remains unchanged, with stage closure SHA-256 values:

- Stage01: `943B3ED924167FC1648815FA40610C5A2061F5760C7F9773AB832A5A9A9E0B89`
- Stage02: `E386EB483F76ECD87AEEF267030FB897D0211A88570ED77384D8D7B53233202A`
- Stage03: `BF1903B2BFB10811D48A69ECFBA53B8C51FD2B3036D4661D82C8C79C4E0C69A6`
- Stage04: `44DC6F29489E778DA420B02E7BB1528B3ECB01D663CAF72705390B07D0589AC1`

No target or staging run was created.

## Changed files

- `kb_creator/pipeline/reconstruction_replay.py`
- `kb_creator/tests/test_reconstruction_replay.py`
- `kb_creator/tests/fixtures/run07_json_artifact_shape_census.sanitized.json`
- this receipt

The earlier Packet J sanitized fixture `kb_creator/tests/fixtures/mineru_content_list_array.sanitized.json` remains part of focused coverage but was not newly changed by J2.

## Risks and next action

- P0/P1: none known within Packet J2 scope.
- P2: the live-inventory equality test is intentionally skipped when immutable run-07 is unavailable on another checkout; deterministic per-class fixtures still run everywhere. On this host it executed and matched all 33 files.
- Next action: independent replay closure review. A later live replay, if authorized, must use a fresh target identity; this receipt does not authorize or perform it.

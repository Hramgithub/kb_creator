# Engineer receipt — replay MinerU content-list array remediation

Date: 2026-09-15  
Role: engineering, `gpt-5.6-sol`, high (user-scoped override)  
Result: **focused PASS; ready for independent review**

## Result

- Fixed replay payload scanning for the exact registered Stage02 artifact route `views/<view>/artifacts/**/<name>_content_list.json`.
- That exact route now requires valid UTF-8 JSON with a top-level array, matching the observed MinerU artifact shape.
- Arbitrary JSON payloads and typed operational wrappers retain the prior top-level-object requirement; `_content_list_v2.json` is not covered by the exception.
- Every nested dictionary key, dictionary value, list item, and string in a content-list array is scanned fail-closed for:
  - the immutable source run identity;
  - Windows drive-absolute paths;
  - UNC paths;
  - device paths;
  - POSIX absolute paths;
  - `..` traversal segments;
  - Windows reserved-device path components.
- Replay-prefix self-validation uses the same narrowly routed array parser and poison scan, so a copied array cannot fail later as `invalid_json_shape` or bypass the post-copy authority scan.

## Changed files

- `kb_creator/pipeline/reconstruction_replay.py`
- `kb_creator/tests/test_reconstruction_replay.py`
- `kb_creator/tests/fixtures/mineru_content_list_array.sanitized.json`
- this receipt

No upstream 19-path S1–S4 closure file, immutable run, source, decision, `.tools` payload, canonical document, or replay target was changed.

## Focused tests

```text
PYTHONPATH=.tools/python-test-deps python -m pytest -q kb_creator/tests/test_reconstruction_replay.py
```

Result: **81 passed in 3.62s**.

New coverage includes:

- sanitized real-shape MinerU top-level content-list array: accepted;
- nested `C:\outside\...`: rejected;
- nested `\\server\share\...`: rejected;
- nested `\\?\C:\device\...`: rejected;
- nested `../../...`: rejected;
- nested `/etc/passwd`: rejected;
- nested source run identity: rejected;
- nested reserved device `NUL`: rejected;
- array under arbitrary `other.json`: rejected as `invalid_json_shape`;
- object under the exact content-list route: rejected as `invalid_mineru_content_list_shape`;
- full synthetic Stage01–04 replay regression: passed atomically and remained acceptance-free.

## Static and schema evidence

- `py_compile` for replay implementation and focused test: PASS.
- Draft 2020-12 metaschema checks for seven replay contracts: PASS.
- Scoped `git diff --check`: PASS.
- No broad suite was run, per the bounded remediation instruction.

## Run-07 read-only eligibility

Only `replay verify-source --through-stage 04` was executed; no `replay run`, resume, target, or staging directory was created.

- state: `eligible`
- run identity: `3F7F9B4765D79BCDA5A3BBCC8EAB22723C2063161E2C31B65A3843507F81E40A`
- eligibility seal: `6264B4D1A3A5FDD0DB2944F2E925C3DEEDA9673688FE00BE869DADD073115114`
- Stage01 closure: `943B3ED924167FC1648815FA40610C5A2061F5760C7F9773AB832A5A9A9E0B89`
- Stage02 closure: `E386EB483F76ECD87AEEF267030FB897D0211A88570ED77384D8D7B53233202A`
- Stage03 closure: `BF1903B2BFB10811D48A69ECFBA53B8C51FD2B3036D4661D82C8C79C4E0C69A6`
- Stage04 closure: `44DC6F29489E778DA420B02E7BB1528B3ECB01D663CAF72705390B07D0589AC1`
- acceptance/decision/Stage05–06 replay claims: all false

## Risks and next action

- P0/P1: none found in the focused scope.
- P2: broad regression remains pending; this remediation did not exercise a live replay.
- Next action: independent review, followed by a separately authorized live replay retry only if closure is GO.

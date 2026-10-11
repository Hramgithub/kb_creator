# Engineer receipt: reconstruction promotion v2 capability gap

Date: 2026-09-15  
Role: engineering, `gpt-5.6-sol/high` user override  
Authority specification: `architect_reconstruction_promotion_v2_capability_gap_20260915.md`  
Authority SHA256: `407630BFAFF25CA145D801CE88DEF489CB494280475BC5BA77E0577DC30CE9B1`

## Result

Implemented the scenario-neutral promotion dispatch and read-only preflight for:

- legacy `run_spec.v1` with the existing skip, unavailable, and injected-authority safeguards preserved;
- direct CPU-first `run_spec.v2` with required CPU-ready and supported optional-CUDA-unavailable semantics;
- replay CPU-first `run_spec.v2` using the canonical replay prefix, review queue, submission, Stage 05/06, audit-v3, and provenance-v3 authorities.

Replay promotion now consumes the flat Stage 06 candidate, records canonical Stage 05/06 `manifest_sha256` values in the normalized upstream stage records, copies the intake/bridge/four rebase receipts into package evidence, and validates the replay-shaped package without changing the public upstream manifest schema. Acceptance recording reruns the same full read-only run-kind preflight before validating and writing the exclusive acceptance receipt.

No schema blocker was found: `reconstruction_upstream_manifest.v1.schema.json` permits the normalized canonical replay digest in the existing `reproducible_sha256` stage-record field.

## Diff summary

- `kb_creator/pipeline/reconstruction_promotion.py`
  - added fail-closed legacy/direct-v2/replay-v2 dispatch from any replay marker;
  - added deterministic capability and live-binding validation/error mapping;
  - added public read-only `preflight_reconstruction_promotion`;
  - added canonical replay graph/submission/downstream/audit validation;
  - added flat candidate and v3 provenance handling;
  - added replay-aware materialization, evidence closure, package stage dispatch, and v3 package validation;
  - changed acceptance preflight to reuse the complete run-kind preflight.
- `kb_creator/tests/test_reconstruction_promotion.py`
  - added the real run09 read-only preflight assertion, including absence of `promotion/` before and after.
- `kb_creator/tests/test_reconstruction_promotion_adversarial.py`
  - added fail-closed v2 capability mutations and replay-marker dispatch coverage.

## Verification

Syntax check:

```text
.tools/MinerU/.venv/Scripts/python.exe -c "import ast,pathlib; ast.parse(...)"
syntax-ok
```

Focused regression command:

```text
.tools/MinerU/.venv/Scripts/python.exe -m pytest -q -rs kb_creator/tests/test_reconstruction_promotion.py kb_creator/tests/test_reconstruction_promotion_adversarial.py
92 passed, 1 skipped in 37.78s
```

The single skip is the pre-existing host limitation for creating an unprivileged symlink fixture.

Real immutable run09 read-only preflight:

```text
state=promotion_preflight_passed
run_kind=replay_v2
run_identity_sha256=887CEEAA0613404B6481221E06A61AEB20A492021E5A7BB8AF27646A493BC620
candidate_inventory_sha256=550BEBDF33074F17DB316C55A447873595B3C507AEC87C0E30D2CF4354AA57EF
promotion-before=False
promotion-after=False
```

Candidate file identity is distinct from the inventory authority:

```text
outputs/06-materialize-candidate/RECONSTRUCTED_EN.md
bytes=21048
sha256=2C8983B83C770AC60AA32993B84228E64983B46010121A9DBA393BD3107C646D
```

MinerU/CPU commands executed: `0`.

## Changed-file identities

| Path | Bytes | SHA256 |
|---|---:|---|
| `kb_creator/pipeline/reconstruction_promotion.py` | 88903 | `36E080C211AF8EAAF9D8C7DFBC4DA84A240681E827915B5D4E11670F42FC5DF4` |
| `kb_creator/tests/test_reconstruction_promotion.py` | 24948 | `24B0F0893C3EE273A27AA015B1F36DBD3636C28BF541D1A46E96C0F9A5A513B2` |
| `kb_creator/tests/test_reconstruction_promotion_adversarial.py` | 10686 | `4A1D31B3FDB76B767C08BC83AC78EC7813084E21034C656DEB5BD9DEED8A7285` |

## Findings and blockers

- Findings: the real run09 authority passes the new canonical replay preflight with optional CUDA providers frozen as unavailable and required CPU ready.
- Blockers: none.
- Not performed: no live run09 materialization, no edits to run07/run08/run09 or decisions/candidate/source, no commit, no push.

## Next action

Independent QA/release review should inspect this bounded implementation and may then authorize the orchestrator to run the explicit run09 promotion materialization step. Final reconstruction acceptance remains a separate explicit user-authority action.

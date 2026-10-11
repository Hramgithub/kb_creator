# Engineer receipt: reconstruction promotion v2 materialize validation remediation

Date: 2026-09-15  
Role: engineering, `gpt-5.6-sol/high` user override  
Authority: live remediation packet following run09 promotion validation failure

## Result

Resolved the replay-v2 package validation failure and added identity-safe rollback for a package published by the current materialization invocation.

The existing run09 package was treated read-only throughout. It now passes `validate_reconstruction_package(..., require_acceptance=False)` and still has no acceptance receipt. No live run09 materialization was repeated.

## Root cause and severity

- **P0 resolved:** `_validate_packaged_stages` dispatched replay Stage 01–04 into the v2 body shape, but still applied the legacy digest formula `sha256(canonical(reproducible))`. `kb_creator.stage_manifest.v2` uses its canonical manifest seal over the whole manifest body excluding `reproducible_sha256`. All four replay prefix manifests therefore failed the legacy recomputation even though their canonical seals were valid.
- **P1 resolved:** post-rename package validation previously occurred outside rollback handling, leaving a newly published invalid package behind when reopen validation failed.
- **P2 coverage added:** full synthetic replay materialize-to-validate, real run09 package read-only validation, and injected post-publish failure coverage now guard the repaired behavior.

## Implementation diff

- `kb_creator/pipeline/reconstruction_promotion.py`
  - replay Stage 01–04 package validation now uses canonical `validate_seal(stage, "reproducible_sha256")`;
  - legacy/direct-v2 stage validation retains the existing reproducible-body digest calculation;
  - frozen bridge implementation evidence is validated by its own sealed inventory rather than requiring byte equality with the currently running validator revision, allowing the already-published package to be reopened after this validator-only fix;
  - post-publish validation failures now remove only the exact unchanged package created by that invocation;
  - rollback verifies fixed topology, absence of reparse points, and exact full-file inventory before deletion;
  - a preexisting package is rejected before publication and is never eligible for rollback;
  - a preexisting promotion directory and unrelated entries are preserved; a promotion directory created by the invocation is removed only when empty.
- `kb_creator/tests/test_reconstruction_promotion.py`
  - added synthetic replay-v2 full materialize then package validation;
  - added read-only validation of the existing failed run09 package;
  - updated the real run09 preflight assertion to preserve and compare the existing package identity.
- `kb_creator/tests/test_reconstruction_promotion_adversarial.py`
  - added post-publish validator fault injection proving exact package/staging cleanup;
  - proves unrelated and preexisting targets remain unchanged.

## Verification

Focused command:

```text
.tools/MinerU/.venv/Scripts/python.exe -m pytest -q -rs kb_creator/tests/test_reconstruction_promotion.py kb_creator/tests/test_reconstruction_promotion_adversarial.py
95 passed, 1 skipped in 51.34s
```

The one skip is the pre-existing host restriction on an unprivileged symlink fixture.

Syntax check:

```text
AST parse: syntax-ok
```

Existing run09 package, read-only validation:

```text
validation=pass
inventory_sha256=7D6E05DA0E0F4CF71A5A89A2EEFC76C90D70EF001D5837DAEFF28BF59689C964
RECONSTRUCTION_INVENTORY.json file_sha256=9B7F6D45EABDD4136350912B0BDCD320A2808B9516BAEA1CBFAD7924616B2A80
RECONSTRUCTION_MANIFEST.json file_sha256=5427629F7D7BE0EB8D17D0E1EE98363F00B4040FD1CB135732A8AE8231603279
acceptance_exists=false
```

Candidate authorities remain unchanged:

```text
candidate_inventory_sha256=550BEBDF33074F17DB316C55A447873595B3C507AEC87C0E30D2CF4354AA57EF
RECONSTRUCTED_EN.md bytes=21048
RECONSTRUCTED_EN.md sha256=2C8983B83C770AC60AA32993B84228E64983B46010121A9DBA393BD3107C646D
```

MinerU/CPU commands executed: `0`.

## Changed-file identities

| Path | Bytes | SHA256 |
|---|---:|---|
| `kb_creator/pipeline/reconstruction_promotion.py` | 91425 | `85EB119B59F7ADCE3DA92DAB3273F2D4105F14BB6AE011D686948923FB0612E3` |
| `kb_creator/tests/test_reconstruction_promotion.py` | 28012 | `1D7210C21E0EFB1150AFADB77CC283421640A25B0920381524BA367A1A7E8935` |
| `kb_creator/tests/test_reconstruction_promotion_adversarial.py` | 12081 | `1BCE1F73C55E9FC78DDF4E2691036A3E97F2194DF251BDCA5C86743F4A7ED99B` |

## Blockers and next action

- Blockers: none.
- Not performed: no mutation/deletion/move of the existing run09 package, no acceptance, no repeated live materialization, no MinerU/CPU, no commit, no push.
- Next action: independent QA/release review. After approval, the orchestrator can proceed directly to the separate explicit acceptance step against the existing validated run09 package; another materialization is not required.

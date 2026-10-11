# Engineer receipt: replay visual projection remediation

Date: 2026-09-15  
Role: engineering, `gpt-5.6-sol` / high (user-scoped override)  
Result: PASS — Packet J3/J3b is ready for independent review. No replay target was created.

## Exact diagnosis

The read-only in-memory comparison of run-07 Stage04 visual projections found exactly one unequal key:

| Projection key | Legacy source wrapper | Fresh typed v3 wrapper | Meaning |
|---|---|---|---|
| `contract_sha256` | `8AEA8EB55440C4B952E5F07A08B7DFB4542F0197F3A539CF7C36B762DED12751` | `99B01F09AA9CFCE72AC407ADBFF21E54BC11A2FDA73A00FDB0FC763024FEAD4E` | raw contract-file byte SHA versus canonical contract SHA |

The raw tracked contract is 1,944 bytes and has the first identity. The sealed run authority records 1,302 canonical JSON bytes and the second identity. This was a representation mismatch, not content drift. No other semantic projection field differed. Legacy per-PNG `dimensions` were already intentionally omitted from the v3 three-key file identity projection; exact dimensions remain bound and checked through the source execution inventory and geometry plan.

## Remediation

- `_visual_projection()` now accepts the independently verified canonical run-contract SHA and applies it symmetrically to source v2 and fresh v3 projections.
- The legacy raw contract SHA must separately equal the explicit current contract file identity. The origin path is never resolved or trusted.
- Source SHA, exact old Stage01/02/03 wrapper paths, Stage02 root, view layout paths, visual execution record, full source file inventory (including PNG dimensions), and geometry-plan identity/seal are separately checked before projection.
- The visual source file inventory must exactly equal the sealed execution inventory. Thus changing or deleting a legacy dimension, execution value, file identity, or geometry identity cannot exploit normalization.
- Reader/content evidence remains projected: source identity, canonical contract identity, DPI, layout identities, counts, inventory scope/exclusions, and every non-geometry file path/bytes/SHA.
- Fresh geometry/visual `path_hint` values use only the trusted input basename, preventing a current external absolute path from entering operational authority.

The preceding J3 live-root defect was also closed: `replay_run_engine()` resolves the trusted source run root once before transformation. Stage03 expected root/artifact strings are built only from that resolved root plus sealed relative view inventories and compared lexically. No origin root/path value is passed to `Path`, `resolve`, or a filesystem API. Run-07 geometry uses flattened layout hints (`views/<view>/artifacts/<layout-basename>`); that exact producer convention is now derived from the sealed layout inventory.

## Deep transform preflight

New CLI surface:

`python -m kb_creator replay verify-source ... --through-stage 04 --validate-rebase --json`

It uses the production typed `_rebase_*` functions in an automatically removed wrapper-only temporary tree. It copies no payload, creates no requested target, publishes nothing, and returns a sealed closed-coverage report.

Run-07 result:

- state: `pass`
- wrappers: **13/13**
- payloads scanned read-only: **71**
- payloads copied: `false`
- target created: `false`
- published: `false`
- acceptance inferred: `false`
- eligibility SHA-256: `6264B4D1A3A5FDD0DB2944F2E925C3DEEDA9673688FE00BE869DADD073115114`
- preflight SHA-256: `5660E73DFD5899425289B9EC55FC9C2C3B464B960BEFF72226E5BDC3FFF3A2E8`

Coverage includes Stage01 command; all five Stage02 view receipts plus view-set; Stage03 comparison plus command; and Stage04 geometry, execution, visual manifest, and command. Every fresh wrapper passed its closed runtime shape, seal, projection, typed-reference and stale-authority checks.

## Tests and checks

- Focused replay: `117 passed in 3.80s`.
- Added attacks for every normalized representation domain: source/contract path, legacy raw contract SHA, raw receipt/comparison/preparation paths, Stage02 root, layout path, producer execution, per-PNG dimensions, legacy geometry file row, and geometry reference.
- Added counter-tests proving semantic changes still alter the projection: source SHA, DPI, layout SHA, counts, inventory scope/exclusions, and every file path/bytes/SHA dimension.
- The full synthetic replay test now passes a relative source-run root, reproducing and guarding the live Stage03 failure class.
- `py_compile` passed for replay engine, CLI and focused test module.
- Draft 2020-12 metaschema validation passed for 10 replay/v3 schemas, including the new closed `replay_transform_preflight.v1` report schema.
- Scoped `git diff --check` passed.
- Ordinary run-07 `verify-source` remains eligible with SHA-256 `6264B4D1A3A5FDD0DB2944F2E925C3DEEDA9673688FE00BE869DADD073115114`.

## Changed files

- `kb_creator/pipeline/reconstruction_replay.py`
- `kb_creator/__main__.py`
- `kb_creator/contracts/replay_transform_preflight.v1.schema.json`
- `kb_creator/tests/test_reconstruction_replay.py`
- this receipt

## Risks and next action

- P0/P1: none known within this bounded remediation.
- P2: deep preflight writes only derived wrappers to an OS temporary directory so downstream wrapper identities can be checked exactly; cleanup is automatic and no payload is copied. A production replay still repeats all checks and remains separately gated.
- Next action: independent closure review before any fresh live replay. This receipt does not authorize replay, decisions, Stage05/06, or acceptance.

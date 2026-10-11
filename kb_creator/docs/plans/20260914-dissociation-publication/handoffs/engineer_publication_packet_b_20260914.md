# Engineering handoff: neutral publication Packet B

Date: 2026-09-14

Goal: `20260914-dissociation-publication`

Step: neutral content and ArtView adapters (Packet B)

Role: engineering, user-scoped override `gpt-5.6-sol` / `high` requested; platform model selection was not independently observable

Owner: bounded contributor; canonical plan/context/status remain owned by the main orchestrator

## Result

Packet B's scenario-neutral content layer is implemented with synthetic evidence only. No Dissociation source, candidate, acceptance, or production output was created. The public `publication run|resume` CLI remains disabled until Packet C installs the render/PDF/package adapters.

The implementation adds:

- a neutral MASTER_EN v3 branch that consumes only an exact accepted reconstructed-English artifact, derives page/count/asset facts, materializes atomically, and has an independent verifier;
- a MASTER_RU lifecycle that wraps the existing batch/split/validation primitives, binds the exact accepted MASTER_EN and shared terminology authorities, validates ordered unit hashes plus Markdown/mechanics parity, and atomically assembles a candidate;
- a neutral ArtView v3 profile, portable bundle with current/context/candidate binaries, closed sealed decisions, accepted-decision validation, and stage-local application/effective-config seals;
- runtime validation of the actual ArtView v3 decision shape in the Packet A control plane, without enabling Packet C or legacy direct-PDF paths;
- the critic-requested production-package schema closure for exact acceptance/stage cardinalities and uniqueness.

## Authority and failure semantics

### MASTER_EN v3

- The source PDF argument is forbidden. The only content input is `reconstructed_en` from the exact reconstruction inventory and exact orchestrator-recorded acceptance receipt.
- Contract, inventory, acceptance, producer/evidence, source, and referenced assets are safe-path/hash/byte bound.
- Reconstruction-inventory and acceptance candidate paths must resolve to the exact same file as the configured reconstructed English; an identical-byte alternate path cannot masquerade as authority.
- Source-page markers must be unique and ordered. Exclusions are config-derived and must name observed pages.
- Candidate topology, content, disposition, assets, provenance, QA, and complete inventory are independently recomputed by `verify_scenario_master_en.py`.

### MASTER_RU

- `prepare` reuses `batch_units` and `expand_units_for_translation`; `validate-submission` reuses `validate_batch`. The four low-level translation scripts were not modified.
- Packet validation revalidates the accepted MASTER_EN receipt, terminology identities, closed batch topology, ordered unit set, task/batch identities, and derived counts on every use.
- Submission validation requires a closed aggregate seal, exact packet/MASTER_EN identities, ordered per-unit source/Russian hashes, closed batch identities, Markdown markers/headings/lists/tables/anchors/link and image targets, numeric/dice tokens, and required shared terminology targets.
- `assemble` writes only after validation passes, copies the exact referenced assets, emits provenance/QA/terminology/inventory evidence, and returns `awaiting_master_ru_acceptance`. CLI gate exits are `10` for packet/submission and candidate/acceptance waits.

### ArtView v3

- Profile inputs are the exact MASTER_RU, exact accepted MASTER_RU receipt, MASTER_RU asset manifest, and reconstruction inventory.
- Every current, context, and candidate binary must exist in a bound asset graph and match path/bytes/SHA/media/dimensions.
- Bundle rows, counts, portable binaries, bindings, decisions contract, and binary inventory are derived; Viral/Innsmouth ids, pages, and counts do not appear in the v3 schemas or synthetic artifacts.
- Decisions are closed and self-sealed, ordered exactly like the candidate manifest, and cannot be accepted with unresolved/unreviewed/non-terminal rows. Presentation objects are closed and validated.
- Validation independently rederives the manifest projection from the profile and source images, rejects changed binaries/inventory/bindings, and requires full closure before application.
- Application requires an exact ArtView acceptance receipt containing the native decision identity exactly once, copies only the selected binaries, and seals reader projection, effective visual config, application receipt, and inventory. It never edits either master.
- ArtView bundle CLI returns `awaiting_artview_decisions` with exit `10`; v2 behavior remains on the existing branch.

## Files

Added:

- `kb_creator/contracts/scenario_artview_profile.v3.schema.json`
- `kb_creator/contracts/scenario_artview_decisions.v3.schema.json`
- `kb_creator/scripts/scenario_master_ru.py`
- `kb_creator/scripts/scenario_artview_apply.py`
- `kb_creator/tests/test_scenario_master_ru.py`
- `kb_creator/tests/test_scenario_artview_v3.py`
- this receipt

Modified within Packet B/P2 scope:

- `kb_creator/scripts/build_scenario_master_en.py`
- `kb_creator/scripts/verify_scenario_master_en.py`
- `kb_creator/scripts/scenario_artview.py`
- `kb_creator/tests/test_build_scenario_master_en.py`
- `kb_creator/contracts/production_package_manifest.v1.schema.json`
- `kb_creator/pipeline/publication.py`
- `kb_creator/tests/test_publication_contracts.py`
- `kb_creator/tests/test_publication_control_plane.py`

Intentionally untouched:

- the four low-level translation batch/micro-merge scripts;
- `translator/translator.py`, `production_docx.py`, legacy Viral/Innsmouth PDF routes, and all Packet C adapters;
- canonical goal `plan.md`, `context.md`, `PROJECT_STATUS.md`, source PDFs, live outputs, `.codex/config.toml`, and Git.

## Verification

Environment:

```text
PYTHONPATH=<repo>/.tools/python-test-deps;<repo>
<repo>/.tools/MinerU/.venv/Scripts/python.exe
```

Passing evidence:

- Final Packet B + publication control/contracts selection: `27 passed`.
- Packet A/reconstruction/MinerU/Packet B synthetic control selection: `72 passed`.
- ArtView v2 independent parity tests not requiring a live generated bundle: `9 passed, 1 deselected`.
- MASTER_EN v3 focused: `2 passed, 77 deselected` (29 focused passes total with the preceding selection).
- New MASTER_RU + ArtView v3 after final authority tightening: `8 passed` (included in the 27-test selection).
- `py_compile`: pass for all changed Python implementation and test modules.
- JSON parse: pass for both new ArtView schemas and the tightened production-package schema.
- scoped tracked `git diff --check`: pass; explicit trailing-whitespace scan over all Packet B/P2 files: pass.

Additional regression evidence and environment limitations:

- Full `test_build_scenario_master_en.py`: `16 passed, 63 failed`. The failures are legacy fixture/environment failures, not hidden or weakened: the checkout lacks `kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf` and `20260901_step6a_reconstructed_en_package_v4`; the legacy author also reports pre-existing `publication_config_v1.json` expected-hash drift. The two new v3 tests pass in the same file.
- Full `test_scenario_artview.py`: the only failure requires absent generated `kb_creator/inputs/viral/artview/review_checkpoint_20260909/candidate/candidate_manifest.json`; the other nine v2 tests pass.
- An extra six-file generic reconstruction group collected `560` tests. It reached pytest's `64%` marker and then emitted 38 more successful dots with no `F` or `E`; it was stopped at the orchestrator-approved practical-time boundary, so no final passed count is claimed.
- A broader page-proof/raw-authority collection cannot start on this checkout because `kb_creator.pdf_raw.page_proof`, `kb_creator.pdf_raw.errors`, and `kb_creator.pdf_raw.raw_authority_projection` are absent. These modules are outside Packet B ownership.
- `jsonschema` is not installed in the repository-local test environment. No dependency was installed outside `.tools`; closed-schema runtime checks and JSON parse/regression assertions were used.

## Remaining scope and risks

- Packet C must wire HTML, explicit DOCX, Word-COM DOCX-to-PDF, render QA, and package adapters before the public runner can be enabled. Packet B scripts are callable directly and included in publication implementation identity, but no partial adapter registry bypasses the fixed ten-stage graph.
- The independent critic should review the actual Packet B CLIs/functions, especially the MASTER_RU structural signature and ArtView v3 manifest rederivation, before any live Dissociation use.
- Legacy fixture failures above require restoring their immutable source/package inputs or reconciling their separately governed hashes; Packet B must not manufacture or relax those authorities.
- No user acceptance was inferred or recorded. MASTER_EN, MASTER_RU, and ArtView remain future explicit user gates.

## Recommended next action

Run an independent `gpt-5.5` implementation review of Packet B against the architecture and this receipt. If it finds no P0/P1 issue, proceed to Packet C; do not run live Dissociation publication until accepted reconstructed English exists and each publication gate is crossed explicitly.

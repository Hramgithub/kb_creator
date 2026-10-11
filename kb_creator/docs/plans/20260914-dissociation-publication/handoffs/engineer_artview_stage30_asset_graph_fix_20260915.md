# Engineer receipt: Stage 30 ArtView asset-graph materialization fix

Timestamp: `2026-09-15T19:15:58+03:00`
Goal id: `20260914-dissociation-publication`
Step id: `stage30-artview-asset-graph-materialization-fix`
Role: engineering
Model: `gpt-5.6-sol`
Effort: `high`
Orchestrator policy owner: main-chat `gpt-5.6-sol/medium`
Assignment state: `user-overridden`
Scoped override: engineering only, `gpt-5.6-sol/high`

## Scope and result

Implemented the scenario-neutral Stage 30 fix in the assigned adapter boundary. The runtime ArtView authority now materializes the complete file closure named by the run-local Stage 21 `ASSET_MANIFEST.json`: it copies the manifest plus only its exact referenced assets, preserving each portable relative path beside the copied manifest.

Every manifest row is prevalidated before any destination materialization. Missing identity fields, unsafe paths, missing files, and byte/SHA-256 drift raise `PublicationAdapterError`; unreferenced sibling assets are not copied. The existing ArtView v3 resolver remains the downstream independent graph validator.

Changed files:

- `kb_creator/pipeline/publication_adapters.py` — 48,273 bytes; SHA-256 `E8FA780E010221C5A41A7FE9F1EA14FB44A1A029C405B3377A0FACE76E34E86B`.
- `kb_creator/tests/test_publication_registry_e2e.py` — 26,119 bytes; SHA-256 `A798C783520C200DA13D6F880FF0D10F570CDB575840991739F28A598B289994`.
- This receipt.

Files checked: the two changed Python files, `kb_creator/scripts/scenario_artview.py`, `kb_creator/scripts/scenario_master_ru.py`, the publication README/status, and the NRI goal-governance contract.

## Verification

Focused graph and ArtView v3 regression:

```text
PYTHONPATH=.tools/python-test-deps \
  .tools/MinerU/.venv/Scripts/python.exe -B -m pytest \
  kb_creator/tests/test_scenario_artview_v3.py \
  kb_creator/tests/test_publication_registry_e2e.py -q
24 passed, 252 subtests passed in 30.45s
```

Adjacent publication control-plane plus real-registry fixture regression:

```text
PYTHONPATH=.tools/python-test-deps \
  .tools/MinerU/.venv/Scripts/python.exe -B -m pytest \
  kb_creator/tests/test_publication_control_plane.py \
  kb_creator/tests/test_publication_registry_e2e.py -q
42 passed in 145.20s
```

`git diff --check`: pass.

The new focused tests prove exact nested asset materialization, exclusion of an unreferenced sibling, and fail-closed behavior for stale identity, missing asset, and missing identity fields before destination writes.

## Boundaries, blockers, and next action

- Implementation blocker: none.
- Risk: this adapter change alters publication implementation identity. Historical run05 must remain immutable; the orchestrator decides the fresh-run path after independent review.
- Not performed: no live publication run, no current working-run mutation, no MinerU/CPU, no install, no acceptance action, no commit, and no push.
- Unrelated pre-existing `.codex/config.toml` modification was preserved untouched.
- Next action: independent review of this bounded diff and evidence; if accepted, the orchestrator may start the appropriate fresh publication run and re-enter the ordered acceptance gates.

Elapsed time: approximately 18 minutes.
Token use: unavailable.

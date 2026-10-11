# Critic receipt: Stage 30 ArtView asset-graph materialization fix

Timestamp: `2026-09-15T19:21:22+03:00`
Goal id: `20260914-dissociation-publication`
Step id: `stage30-artview-asset-graph-materialization-fix-review`
Review kind: `implementation`
Role: independent critic
Requested model/effort: `gpt-5.5` / `medium`
Actual platform model/effort: unavailable
Implemented candidate: no
Materially designed candidate: no
Orchestrator policy owner: main-chat `gpt-5.6-sol/medium`
Assignment state: `platform-unverified`
Scoped override: none

## Scope

Reviewed the narrow Stage 30 fix without editing implementation, canonical plan,
context, project status, or release files. This is not a release review and does
not transfer orchestration ownership.

Files checked:

- `kb_creator/pipeline/publication_adapters.py`
- `kb_creator/tests/test_publication_registry_e2e.py`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_artview_stage30_asset_graph_fix_20260915.md`
- `kb_creator/scripts/scenario_artview.py`
- `kb_creator/scripts/scenario_master_ru.py`
- `kb_creator/tests/test_scenario_artview_v3.py`
- `docs/governance/nri_goal_governance.md`

## Evidence

- `publication_adapters.py` now routes Stage 30 ArtView authority copying through
  `_materialize_asset_manifest_graph`, which reads Stage 21 `ASSET_MANIFEST.json`,
  validates each manifest row for safe relative path, exact `bytes` and `sha256`,
  source containment, regular-file identity, and only then materializes the
  copied manifest plus referenced asset paths beside it.
- The helper rejects missing assets, stale identities, missing identity fields,
  backslash/absolute/parent-traversal/drive-style unsafe paths, reparse/symlink
  content through `_contained_file`, and does not copy unreferenced siblings.
- Existing ArtView v3 graph validation remains closed: `scenario_artview.py`
  still resolves `master_ru_asset_manifest` rows from the copied manifest parent,
  checks exact identity, and rejects profile image records outside the exact bound
  graph.
- `scenario_master_ru.py` still emits the Stage 21 manifest from the copied
  MASTER_EN image targets, with relative asset paths and exact identities.
- Focused graph and ArtView regression:

```text
$env:PYTHONPATH='.tools/python-test-deps'; .\.tools\MinerU\.venv\Scripts\python.exe -B -m pytest kb_creator/tests/test_scenario_artview_v3.py kb_creator/tests/test_publication_registry_e2e.py -q
24 passed, 252 subtests passed in 30.75s
```

- Adjacent publication control-plane and real-registry regression:

```text
$env:PYTHONPATH='.tools/python-test-deps'; .\.tools\MinerU\.venv\Scripts\python.exe -B -m pytest kb_creator/tests/test_publication_control_plane.py kb_creator/tests/test_publication_registry_e2e.py -q
42 passed in 148.52s
```

- `git diff --check -- kb_creator/pipeline/publication_adapters.py kb_creator/tests/test_publication_registry_e2e.py`: pass.

## Severity Findings

P0: none.

P1: none.

P2: none.

## Blockers

None for this implementation review.

Release-specific evidence was not evaluated because this assignment is
`implementation`, not `release`: no candidate revision or manifest freeze,
declared release exclusions, release QA pack, or mutation invalidation check was
reviewed as a final gate.

## Recommendation

GO for the narrow Stage 30 implementation candidate.

The fix satisfies the assigned criteria: exact manifest-referenced asset
materialization is scenario-neutral, unreferenced assets are excluded, stale or
missing identity fails before destination materialization, the ArtView graph
remains closed, focused tests pass, and authority/path-containment checks are
not weakened.

Elapsed time: approximately 4 minutes 12 seconds to receipt checkpoint.
Token use: `71624` tokens reported by Codex goal tracker at receipt checkpoint.

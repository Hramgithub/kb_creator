# Engineer receipt: ArtView v3 accepted-decision rebind

- Goal id: `20260914-dissociation-publication`
- Step id: generic ArtView v3 accepted-decision rebind
- Timestamp: `2026-09-15T21:22:23+03:00`
- Contributor role: engineering
- Requested model / effort: `gpt-5.6-sol` / `high` (user-scoped override in task packet)
- Actual platform model / effort: unavailable
- Assignment state: `user-overridden`
- Orchestrator policy owner: `gpt-5.6-sol` / `medium`
- Scope: `kb_creator/scripts/scenario_artview.py`, directly relevant v3 tests, and this receipt
- Forbidden scope honored: no live publication or MinerU execution; no canonical plan, context, status, README, source, or unrelated worktree edits

## Result

Implemented a scenario-neutral `rebind-decisions` CLI and `rebind_v3_decisions` function. The operation:

- resolves source and target inputs only as safe authority-relative, non-reparse files;
- requires the destination to be absent under the target authority;
- validates source decisions through strict `validate_v3_decisions(..., require_accepted=True)`;
- independently validates the complete target profile, candidate projection, source graph, portable binary inventory, manifest bindings, decision contract, and derived counts;
- requires identical scenario, row order/cardinality, complete review rows, decision contract, derived counts, and candidate binary inventory;
- verifies the selected target binary is exactly the same manifest binary as the accepted source selection;
- copies the accepted decision rows unchanged, including binary choice, presentation, `reviewed`, and notes;
- replaces only target bindings and the recomputed review summary, then recomputes the canonical `decisions_sha256` and strictly validates the written target document;
- fails closed for changed visible evidence, changed selected or unselected binaries, stale seals/bindings, invalid target graphs, traversal/unsafe authority paths, reparse content, and existing destinations.

No scenario-specific identifiers or behavior were added.

## Files changed

- `kb_creator/scripts/scenario_artview.py`
  - SHA-256: `88694156158B1D53485F4F1D1A44F338B0F58AA89119F171E486B5740C81DC7D`
- `kb_creator/tests/test_scenario_artview_v3.py`
  - SHA-256: `3FF76E69EEA2ACDD1C5855A24005A65962A8AD9A240BB3C3C3B07728DE266A17`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_artview_v3_decision_rebind_20260915.md`

## Verification

- `py_compile` for the owned script and v3 test module: pass.
- `scenario_artview.py rebind-decisions --help`: pass; all eight required path/authority arguments are exposed.
- `unittest kb_creator.tests.test_scenario_artview_v3`: `20 passed`.
- Positive coverage: exact fresh candidate gets new bindings and canonical seal while preserving accepted decisions/notes/review flags.
- Adversarial coverage: changed label, presentation default, selected binary, stale source seal, tampered target binary graph, traversal destination, and existing destination all fail closed without producing or overwriting output.
- Scoped `git diff --check`: pass.
- Additional v2 + v3 suite attempt: v3 and synthetic v2 tests ran, but the pre-existing real Viral fixture test could not start because `kb_creator/inputs/viral/artview/review_checkpoint_20260909/candidate/candidate_manifest.json` is absent. This is outside the assigned change and not caused by the rebind implementation.

## Blockers and next action

- Implementation blocker: none.
- Release acceptance remains for an independent implementation critic.
- Orchestrator may integrate the CLI into the fresh publication continuation only after identifying the exported accepted JSON and the exact source/target authorities; this receipt did not run that live operation.

- Elapsed time: approximately 35 minutes
- Token use: unavailable

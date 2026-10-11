# T8 — ArtView v4 control-plane receipt

- Scope: Stage-30 ArtView v4 control-plane/adapter closure only; no reconstruction, renderer, generated outputs, canonical plan/status, release, commit, or push changes.
- Result: Stage 30 accepts v3/v4. For v4 it makes one `scenario_artview.build(...)` dispatch after copying a stage-local authority graph: accepted MASTER_RU graph, reconstruction inventory, sealed reconstruction manifest, every manifest-recorded review decision at its exact relative path, sealed source identity, and source PDF. No page roles or review rows are authored by the adapter. The local PDF is accepted only when bytes/SHA agree with source identity, promoted portable evidence, and the sealed local reconstruction run.
- Files changed: `kb_creator/pipeline/publication_adapters.py`, `kb_creator/pipeline/publication.py`, `kb_creator/scripts/author_scenario_publication_contract.py`, publication schemas, and focused `test_publication_control_plane.py`.
- Evidence: with `PYTHONPATH=.tools/python-test-deps`, `python -m pytest kb_creator/tests/test_publication_control_plane.py -k artview_v4_stage30 -q` => `1 passed, 36 deselected`; `compileall` and `git diff --check` pass.
- Blockers: none. Next action: integration owner may exercise full v4 Stage30/31 path with an accepted reconstruction authority.
- Elapsed time: approximately 35 minutes. Token use: approximately 10k. Timestamp: 2026-09-18 Europe/Moscow.
- Orchestrator policy owner: root/main orchestrator (`gpt-5.6-sol`, medium). Assignment state: completed bounded engineering; orchestration ownership retained by root.
- Scoped override: explicit v3 compatibility retained; no acceptance or release decision made.

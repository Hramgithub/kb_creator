# T8 — ArtView v4 control-plane receipt

- Scope: Stage-30 ArtView adapter/control-plane readiness only; no reconstruction, renderer, generated outputs, canonical plan, status, release, commit, or push changes.
- Result: Stage 30 now accepts profile v3 or v4.  For v4 it derives one runtime profile, copies the accepted MASTER_RU graph plus the source PDF, source identity, and reconstruction inventory into stage-local authority, then makes exactly one `scenario_artview.build(...)` dispatch.  The source PDF can be used only when its bytes/SHA agree with the sealed source identity, the promoted portable reconstruction evidence, and the sealed local reconstruction run.
- Changed files: `kb_creator/pipeline/publication_adapters.py`; `kb_creator/pipeline/publication.py`; `kb_creator/scripts/author_scenario_publication_contract.py`; `kb_creator/contracts/scenario_publication_contract.v1.schema.json`; `kb_creator/contracts/scenario_publication_blueprint.v1.schema.json`; `kb_creator/tests/test_publication_control_plane.py`.
- Checks/evidence: bundled Python `compileall` passed for all changed Python files; `git diff --check` passed.  The focused regression covers one v4 Stage-30 build dispatch and a local source-PDF byte-drift rejection.  Full pytest was unavailable because the bundled Python has no `pytest` module.
- Blockers: no code blocker. Full pytest remains an environment follow-up.
- Next action: run the focused control-plane test suite in the project test environment, then integrate the v4 profile/decision authority with the Stage-31 application acceptance path.
- Elapsed time: approximately 24 minutes. Token use: approximately 8k. Timestamp: 2026-09-18 Europe/Moscow.
- Orchestrator policy owner: root/main orchestrator (`gpt-5.6-sol`, medium). Assignment state: completed bounded engineering; orchestration ownership retained by root.
- Scoped override: v4 decision/profile acceptance added while retaining explicit v3 compatibility; no release decision or acceptance was made.

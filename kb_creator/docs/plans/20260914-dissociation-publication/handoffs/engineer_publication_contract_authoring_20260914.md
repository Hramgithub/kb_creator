# Engineer handoff — publication contract authoring

- Date: 2026-09-14
- Role / requested model / effort: engineering / `gpt-5.6-sol` / `high`
- Scope: scenario-neutral blueprint authoring only; no live Dissociation artifacts, acceptance, release, install, Git index, commit, or push

## Result

Added a fail-closed authoring path from
`kb_creator.scenario_publication_blueprint.v1` to the existing canonical
`kb_creator.scenario_publication_contract.v1`. The blueprint declares policies
and exactly seven named config roles. The author resolves only normalized
`config_root`-relative files, rejects absolute/drive/UNC/backslash/traversal,
missing, empty, non-file, and reparse references, and computes every byte count
and SHA-256 identity. Terminology files are bound by the same path gate.

The output target must be absent. Before its exclusive write, the generated
canonical JSON is validated through the existing publication runtime validator.
Both blueprint and generated contract are additionally validated against their
Draft 2020-12 schemas when `jsonschema` is available. Duplicate JSON keys and
all missing/extra fields fail closed. The author neither reads nor writes
acceptance evidence and cannot infer acceptance.

CLI from repository root:

```powershell
python -B kb_creator/scripts/author_scenario_publication_contract.py `
  --blueprint path/to/publication-blueprint.json `
  --config-root path/to/config-root `
  --output path/to/publication-contract.json
```

## Files

- `kb_creator/contracts/scenario_publication_blueprint.v1.schema.json`
- `kb_creator/scripts/author_scenario_publication_contract.py`
- `kb_creator/tests/test_author_scenario_publication_contract.py`
- this handoff receipt

`kb_creator/README.md` was not changed because it already contains concurrent
uncommitted work; the command is recorded here for orchestrator integration.

## Verification

Repository-local Python and dependencies only:

```text
PYTHONPATH=<repo>/.tools/python-test-deps;<repo>
<repo>/.tools/MinerU/.venv/Scripts/python.exe -m pytest -q \
  kb_creator/tests/test_author_scenario_publication_contract.py \
  kb_creator/tests/test_publication_contracts.py
30 passed, 2 skipped in 1.63s

<repo>/.tools/MinerU/.venv/Scripts/python.exe -m pytest -q \
  kb_creator/tests/test_publication_control_plane.py
32 passed in 48.16s

py_compile: pass
blueprint schema JSON parse and path-regex compile: pass
```

The two focused skips are explicit environment conditions: Windows denied
symlink creation for the real reparse fixture, while a non-skipped monkeypatch
probe still proves every referenced path passes through the reparse guard; and
the repository-local environment has no `jsonschema`. Runtime-validator parity
is non-skipped. The optional JSON Schema test runs automatically when that
dependency is present; no dependency was installed.

## Boundary

No Dissociation blueprint was authored. A truthful live blueprint still needs
the selected, existing seven config files, all terminology authorities, the
accepted reconstruction-contract SHA-256, artifact names, and stage QA policy
choices. Those are scenario/run authorities, not values the neutral author may
invent or infer. There are no implementation blockers for authoring once those
declarations exist.

This is implementation evidence for independent review, not acceptance or a
release decision. Token use: unavailable.

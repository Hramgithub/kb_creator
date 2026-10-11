# Critic receipt: HTML stage asset locality fix

- Goal id: `20260914-dissociation-publication`
- Step id: `html_stage_asset_locality_fix_review`
- Role: independent implementation critic
- Model: `gpt-5.5`
- Effort: `medium`
- Timestamp: `2026-09-15T21:15:00+03:00`
- Assignment state: `platform-unverified`

## Scope

Review the generic HTML Stage 40 asset-locality implementation in
`kb_creator/pipeline/publication_adapters.py` and focused coverage in
`kb_creator/tests/test_publication_html_adapter.py` against the engineering
receipt `engineer_html_stage_asset_locality_fix_20260915.md`.

This review did not edit implementation, tests, canonical plan/context/status,
or `.codex/config.toml`. It is an implementation review only, not a release
decision and not authorization to resume historical run07.

## Verdict

GO for governed fresh HTML-stage recovery after the orchestrator records the
changed implementation identity and uses the accepted run07 ArtView evidence as
authority. No P0/P1/P2 findings remain for the reviewed fix.

## Findings

- P0: none.
- P1: none.
- P2: none.

## Evidence

Code inspection confirms the accepted authority graph is strict:

- Stage 40 still requires accepted `MASTER_RU`, accepted ArtView decisions,
  ArtView acceptance and Stage 31 application/effective visual config before
  HTML rendering.
- `ARTVIEW_APPLIED.json` is checked as a closed shape and must bind exact
  profile, candidate manifest, accepted decisions and ArtView acceptance
  identities. The ArtView acceptance must bind the exact native decisions
  exactly once.
- The candidate manifest must bind the exact `MASTER_RU` and
  `ASSET_MANIFEST.json`; the reader projection and effective visual config must
  agree with the application.
- Materialization uses exact `path`, `bytes`, `sha256` records and rejects
  missing files, stale identities, unsafe paths, traversal, collisions and
  reparse content before renderer invocation.
- MASTER_RU image references are accepted only when manifest-bound and mapped
  through ArtView row identity by `(bytes, sha256)`. There is no name-only
  matching fallback.
- The derived Markdown rewrites included assets to stage-local
  `../artifacts/assets/...`; excluded rows remove their image line. The final
  HTML local-reference inventory must remain inside the Stage 40 root.
- Stage 30's adjacent asset-graph copy fix prevalidates the source manifest and
  materializes only exact referenced assets beside the copied manifest.

Focused verification:

```text
$env:PYTHONPATH='C:\_Hobby\_work\NRI\.tools\python-test-deps';
& 'C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B -m pytest -q kb_creator/tests/test_publication_html_adapter.py kb_creator/tests/test_publication_registry_e2e.py kb_creator/tests/test_publication_control_plane.py
51 passed in 96.08s (0:01:36)
```

```text
& 'C:\_Hobby\_work\NRI\.tools\python\cpython-3.12.14-windows-x86_64-none\python.exe' -B -m py_compile kb_creator/pipeline/publication_adapters.py kb_creator/tests/test_publication_html_adapter.py
pass
```

```text
git diff --check
pass
```

Read-only run07 temp probe:

- Used accepted run07 `MASTER_RU.md`, `master_ru.acceptance.json`,
  `artview-decisions.accepted.json`, `ARTVIEW_APPLIED.json`,
  `effective_visual_config.json`, Stage 31 projection root and
  `effective_publication_config.json`.
- Wrote only a transient `local/critic-html-locality-*` staging tree under
  run07, invoked `build_html_candidate` with a fake renderer, printed the
  adapter receipt facts, and removed the probe tree in the same process.
- Result was `status: pass`, `adapter: translator_build_production_html_v1`,
  `direct_pdf_route: false`, `local_reference_count: 2`.
- Materialized assets were exactly `assets/alaska-map.jpg` and
  `assets/dissociation-cover.jpg`.
- Derived Markdown references were
  `../artifacts/assets/dissociation-cover.jpg` and
  `../artifacts/assets/alaska-map.jpg`; rendered HTML references were
  stage-local `assets/dissociation-cover.jpg` and `assets/alaska-map.jpg`.
- Final local-reference inventory bound the exact accepted bytes/SHA-256:
  `E30A388DC2A17E216A53A2A673EA583C3B71BE6567FE97F9E35805DE71E760AC`
  for cover and
  `F96AD0F20513F4737474915670FE2A1F361BF60C12FD6AE0F210CF2132127DE4`
  for Alaska map.

## Residual Boundaries

- This review does not make run07 resumable. The implementation inventory has
  changed, so the next live step must be a governed fresh recovery/rebuild that
  reuses the accepted authorities without inferring new user acceptance.
- This review does not cover DOCX, PDF, package assembly, offline verification,
  final release review or user HTML acceptance.

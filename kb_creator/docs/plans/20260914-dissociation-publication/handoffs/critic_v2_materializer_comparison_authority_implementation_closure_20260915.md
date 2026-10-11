# Critic receipt — v2 materializer comparison authority implementation closure

Timestamp: 2026-09-15T00:43:56+03:00  
Goal id: 20260914-dissociation-publication  
Step id: 4-v2-materializer-comparison-authority-implementation-closure  
Review kind: implementation  
Reviewer role: independent critic, `gpt-5.5` requested by assignment  
Implemented or materially designed candidate: no  
Orchestrator policy owner: main-chat orchestrator remains owner; critic role does not transfer orchestration ownership  
Assignment state: complete  
Scoped override: none; reviewer may write only this immutable receipt

## Scope

Independent implementation closure review for fresh local run
`20260915-cpu-first-05`.

Reviewed authorities:

- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_v2_materializer_comparison_authority_20260915.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/critic_v2_materializer_comparison_authority_architecture_20260915.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_v2_materializer_comparison_authority_20260915.md`

Forbidden and not performed:

- implementation edits;
- `.tools` edits;
- source/run/decision/candidate/publication/release mutation;
- live MinerU/PDF execution;
- network/GPU/remote/API use;
- Git commit or Git state mutation.

## Files checked

Governance and routing:

- `AGENTS.md`
- `docs/governance/nri_goal_governance.md`
- `.agents/skills/kb-creator-scenario-reconstruction/SKILL.md`

Implementation and tests:

- `kb_creator/scripts/materialize_mineru_ai_merge.py`
- `kb_creator/pipeline/reconstruction.py`
- `kb_creator/tests/test_materialize_mineru_ai_merge.py`
- `kb_creator/tests/test_mineru_cpu_packet_b.py`
- `kb_creator/tests/test_reconstruction_control_plane.py`
- `kb_creator/tests/test_reconstruction_promotion.py`
- `kb_creator/tests/test_reconstruction_promotion_adversarial.py`
- `kb_creator/README.md`

Status/diff shape observed:

- tracked modified: `kb_creator/README.md`, `kb_creator/scripts/materialize_mineru_ai_merge.py`, `kb_creator/tests/test_materialize_mineru_ai_merge.py`
- untracked in this workspace snapshot but in reviewed scope: `kb_creator/pipeline/reconstruction.py`, `kb_creator/tests/test_mineru_cpu_packet_b.py`, `kb_creator/tests/test_reconstruction_control_plane.py`, `kb_creator/tests/test_reconstruction_promotion.py`, `kb_creator/tests/test_reconstruction_promotion_adversarial.py`

## Implementation evidence

The implementation satisfies the architecture's runtime authority contract.

Confirmed in code:

- `materialize()` has an all-or-none explicit comparison pair:
  `comparison` and `comparison_sha256`.
- For v2 visual bundles, omission of either or both explicit comparison
  inputs fails before candidate output/staging is created.
- The only accepted v2 comparison topology is the fixed run-local path:
  `outputs/03-compare-views/comparison.json`.
- The comparison SHA is checked against the supplied sealed authority and then
  against the validated review queue record; it is not freshly computed as the
  source of authority.
- The materializer revalidates the v2 RunSpec, live implementation inventory,
  Stage 01-04 manifests, Stage 03 comparison, Stage 04 visual manifest, Stage
  04 geometry plan, Stage 02 view-set, queue seal, and queue-to-merge-packet
  identities before `output_root.parent.mkdir()` and before candidate staging.
- The Stage 06 production adapter now requires the already validated queue for
  v2 runs, revalidates that queue, and emits exactly one `--comparison` plus
  exactly one `--comparison-sha256` to the materializer.
- The legacy v1/standalone omitted-pair path remains available through the
  historical `<raw-root>/comparison/comparison.json` fallback.
- Unknown visual bundle schemas fail closed and cannot silently use the legacy
  fallback.
- `MERGE_PROVENANCE.json` keeps the exact existing top-level key set and
  records the selected authoritative comparison path in `raw_comparison`.
- Recursive non-reparse checks reject symlinks and Windows reparse point
  classes using `os.lstat` plus `st_file_attributes & 0x400`, and fail closed
  on Windows when file attributes are unavailable.
- The materializer now also applies non-reparse checks to bundle, raw,
  decisions, merge packet, comparison, content-list, and selected raw-asset
  paths.

Confirmed in tests:

- v2 positive path with no Stage02 comparison child succeeds only with explicit
  Stage03 comparison authority and provenance names Stage03.
- zero flags, one missing flag, wrong SHA, outside path, queue path drift,
  queue byte-count drift, and Stage04 visual graph drift fail without creating
  candidate output.
- exact-once Stage06 adapter argv is asserted.
- missing validated queue for v2 production adapter fails closed.
- recursive symlink/junction/mount-point simulation and Windows missing-attrs
  failure are covered.
- promotion exact-key provenance compatibility remains covered by the broader
  promotion suites.

## Verification run

Focused materializer:

```text
$env:PYTHONPATH='C:\_Hobby\_work\NRI\.tools\python-test-deps'
python -m pytest kb_creator\tests\test_materialize_mineru_ai_merge.py -q
36 passed in 4.54s
```

Broad relevant suite:

```text
$env:PYTHONPATH='C:\_Hobby\_work\NRI\.tools\python-test-deps'
python -m pytest `
  kb_creator\tests\test_materialize_mineru_ai_merge.py `
  kb_creator\tests\test_mineru_cpu_packet_b.py `
  kb_creator\tests\test_reconstruction_control_plane.py `
  kb_creator\tests\test_mineru_visual_merge_bundle.py `
  kb_creator\tests\test_audit_mineru_ai_merge_fidelity.py `
  kb_creator\tests\test_reconstruction_promotion.py `
  kb_creator\tests\test_reconstruction_promotion_adversarial.py -q
184 passed, 1 skipped in 103.29s
```

Compile:

```text
python -m compileall -q `
  kb_creator\scripts\materialize_mineru_ai_merge.py `
  kb_creator\pipeline\reconstruction.py `
  kb_creator\tests\test_materialize_mineru_ai_merge.py `
  kb_creator\tests\test_mineru_cpu_packet_b.py `
  kb_creator\tests\test_reconstruction_control_plane.py `
  kb_creator\tests\test_reconstruction_promotion.py `
  kb_creator\tests\test_reconstruction_promotion_adversarial.py
COMPILE_OK
```

Contract/schema checks:

```text
JSON parse over kb_creator/contracts/*.json
CONTRACT_JSON_PARSE_OK 31
```

Additional schema-validator check:

```text
jsonschema.Draft202012Validator.check_schema over *.schema.json
SCHEMA_CHECK_FAILURES 1
kb_creator/contracts/scenario_artview_profile.v3.schema.json
SchemaError: regex metaschema validation failed for safePath pattern
```

This failure is outside the bounded materializer comparison-authority patch and
was not introduced by the reviewed files.

PowerShell parser:

```text
PS_PARSE_OK kb_creator\scripts\run_mineru_three_view.ps1
```

Diff/whitespace:

```text
git diff --check -- reviewed files
exit 0

scoped trailing-whitespace scan
SCOPED_TRAILING_WS_OK
```

Static scenario-neutrality scan:

- no scenario/run-id/network/API/remote/manual-copy strings were found in the
  changed reusable implementation files;
- README contains scenario/project documentation terms, including existing
  Viral/Innsmouth/Dissociation documentation sections.

## Findings

### P0

None.

### P1

None.

### P2

1. Scope hygiene: `kb_creator/README.md` has a large documentation diff even
   though the accepted architecture's bounded implementation ownership
   explicitly excluded README changes. The content is explanatory and does not
   change runtime authority, so it is not a run blocker, but it should be
   consciously accepted, reverted, or handled by the orchestrator before a
   scoped commit.

2. Existing schema-tooling issue: full `jsonschema.check_schema` over all
   schemas fails on `scenario_artview_profile.v3.schema.json` due its
   `safePath` regex being rejected as a Python regex by the validator. This
   patch does not change schemas and the reviewed materializer/control-plane
   tests pass, so this is unrelated to `20260915-cpu-first-05`; it is worth
   tracking separately if full-schema validator hygiene becomes a gate.

3. Engineer receipt count mismatch: engineer reported the focused materializer
   suite as `37 passed`; the independent rerun collected `36 passed`. The
   broader suite result matched (`184 passed, 1 skipped`). This is evidence
   bookkeeping drift only, not a behavioral failure.

## Blockers

None for a fresh local CPU run `20260915-cpu-first-05`.

Do not resume or mutate `20260914-cpu-first-04`; the implementation inventory
change is expected to make it stale.

## Recommendation

GO for fresh local CPU run `20260915-cpu-first-05`.

NO-GO for any workaround that resumes `20260914-cpu-first-04`, plants a
Stage03 comparison under Stage02, weakens implementation binding, rewrites
sealed run/queue/stage manifests, or treats the previous page decisions as
accepted reconstruction output without a fresh queue/packet equivalence check.

## Review accounting

Elapsed time: approximately 33 minutes  
Token use: unavailable exact critic token accounting  
Changed files by critic: this receipt only

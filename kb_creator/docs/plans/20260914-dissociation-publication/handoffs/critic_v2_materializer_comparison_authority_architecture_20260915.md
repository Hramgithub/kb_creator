# Critic receipt — v2 materializer comparison authority architecture

Timestamp: 2026-09-15T00:16:34+03:00  
Goal id: 20260914-dissociation-publication  
Step id: 4-v2-materializer-comparison-authority-architecture-review  
Review kind: architecture  
Reviewer role: independent critic, `gpt-5.5` requested by assignment  
Implemented or materially designed candidate: no  
Orchestrator policy owner: main-chat orchestrator remains owner; critic role does not transfer orchestration ownership  
Assignment state: complete  
Scoped override: none; reviewer may write only this immutable receipt

## Scope

Independent architecture review of:

- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_v2_materializer_comparison_authority_20260915.md`

Forbidden and not performed:

- implementation edits;
- `.tools` edits;
- source/run/decision/candidate/publication/release mutation;
- live MinerU/PDF execution;
- network/GPU/remote/API use;
- Git commit or Git state mutation.

## Files and evidence checked

Governance and project context:

- `AGENTS.md`
- `docs/governance/nri_goal_governance.md`
- `.agents/skills/kb-creator-scenario-reconstruction/SKILL.md`
- `kb_creator/README.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/plan.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/context.md`

Candidate architecture:

- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_v2_materializer_comparison_authority_20260915.md`

Current code paths:

- `kb_creator/pipeline/reconstruction.py`
- `kb_creator/scripts/materialize_mineru_ai_merge.py`
- `kb_creator/pipeline/reconstruction_promotion.py`
- `kb_creator/tests/test_materialize_mineru_ai_merge.py`
- `kb_creator/tests/test_reconstruction_control_plane.py`
- `kb_creator/tests/test_mineru_cpu_packet_b.py`

Immutable run evidence read-only:

- `kb_creator/working/dissociation/reconstruction/20260914-cpu-first-04/run.json`
- `kb_creator/working/dissociation/reconstruction/20260914-cpu-first-04/review/review_queue.json`
- `kb_creator/working/dissociation/reconstruction/20260914-cpu-first-04/outputs/02-mineru-three-view/view-set.json`
- `kb_creator/working/dissociation/reconstruction/20260914-cpu-first-04/outputs/03-compare-views/comparison.json`
- `kb_creator/working/dissociation/reconstruction/20260914-cpu-first-04/outputs/04-visual-merge-bundle/visual/visual_manifest.json`
- `kb_creator/working/dissociation/reconstruction/20260914-cpu-first-04/outputs/04-visual-merge-bundle/visual/geometry_plan.json`

## Verified root cause

The architect's root cause is correct.

The immutable `20260914-cpu-first-04` run is `kb_creator.run_spec.v2` /
`mineru_cpu_first_three_view_v1` with portable identity
`D6370C968BD209E82F8DB6E9511187ED0EB0426E8EE1F48E35A267C6E683105F`.

The v2 Stage 03 comparison exists at:

```text
outputs/03-compare-views/comparison.json
bytes=449244
sha256=C76C2F43B7027207A1CE01490A0D5BC0A2EA5B0F2EC6D6B5EBCB88A35282DA26
schema=kb_creator.mineru_multi_view_comparison.v2
status=pass_for_review
```

The legacy path is absent:

```text
outputs/02-mineru-three-view/comparison/comparison.json -> False
```

The `-04` review queue binds the Stage 03 comparison record exactly:

```json
{
  "path": "outputs/03-compare-views/comparison.json",
  "bytes": 449244,
  "sha256": "C76C2F43B7027207A1CE01490A0D5BC0A2EA5B0F2EC6D6B5EBCB88A35282DA26"
}
```

The Stage 04 geometry plan also binds the same comparison identity and the
same Stage 02 view-set identity/receipt seal. Its succeeded view order is the
required CPU triptych:

```text
original_pipeline_txt, original_pipeline_ocr, raster_pipeline_ocr
```

The current production Stage 06 adapter in `reconstruction.py` invokes
`materialize_mineru_ai_merge.py` with only:

```text
--bundle-root
--raw-root
--decisions-root
--output-root
```

The current materializer then unconditionally reads:

```python
comparison_path = raw_root / "comparison" / "comparison.json"
```

and writes provenance using that same legacy derived path. Therefore the
earliest failing layer is the Stage 06 adapter/materializer authority contract,
not Stage 03, Stage 04, the page decisions, or the MinerU views.

The `-04` RunSpec pins the current implementation identities:

```text
kb_creator/pipeline/reconstruction.py
455FCD32C1369F7E6381886EF8C73AA23CF861520F3F776E265205E0E29108D3

kb_creator/scripts/materialize_mineru_ai_merge.py
8A9AB05F80AB1F72B458573371392D64A08B176DE737096385EBEE74AADABE90
```

These match the files at inspection time. A correct implementation change must
therefore invalidate ordinary resume of `-04` through the existing
implementation-inventory binding. The architecture's fresh-run-only decision
is correct.

## Architecture assessment

The proposed bounded architecture is accepted.

It correctly requires:

- the sealed review queue's Stage 03 `path`, `bytes`, and `sha256` to become
  the explicit v2 materializer authority;
- exact canonical run-relative path literal
  `outputs/03-compare-views/comparison.json`;
- path containment and non-reparse checks before reads and before any output
  or staging directory is created;
- adapter-passed `--comparison` and `--comparison-sha256` sourced from the
  validated queue authority, not freshly blessed from arbitrary filesystem
  bytes;
- mandatory explicit comparison authority for v2 bundles, while preserving
  legacy v1/standalone fallback only when no v2 bundle is in play;
- cross-binding against Stage 04 visual manifest, Stage 04 geometry plan,
  Stage 02 sealed view-set, run identity, succeeded view order, CPU triptych,
  comparison status, and comparison failures;
- unchanged Stage 05 merge-index-root contract;
- unchanged `MERGE_PROVENANCE.json` key set for promotion compatibility;
- resume/cache rejection on queue, comparison, packet, decision, allowlist,
  source/contract/tool, or implementation mutation;
- no manual copy, symlink/junction alias, manifest rewrite, relaxed
  implementation check, or `-04` resume path;
- fresh absent run `20260915-cpu-first-05` after implementation closure;
- fresh decision-set manifest, with old page decision bytes reusable only
  after automated exact per-page packet/queue semantic equivalence is proven.

The adversarial matrix is proportionate and directly targets the defect class:
omitted/partial flags, wrong bytes/hash, planted Stage02 copy, outside-root
same-byte file, traversal/backslash/UNC/ADS, symlink/junction/reparse alias,
view graph drift, non-empty comparison failures, exact argv, atomicity, and
promotion parity.

## Findings

### P0

None.

### P1

None.

### P2

1. Implementation review must explicitly prove the non-reparse containment
   helper rejects Windows symlinks, junctions, mount points, and nested reparse
   components recursively for every comparison path component. The architecture
   requires this, so this is a testability note rather than an architecture
   blocker.

## Blockers

None for bounded implementation of the architecture.

`20260914-cpu-first-04` remains immutable evidence and must not be resumed
after the implementation changes. This is an intended fail-closed consequence,
not a blocker.

## Recommendation

GO for bounded implementation under the exact scoped file list in the architect
receipt, followed by focused adversarial QA and independent implementation
closure.

NO-GO for resuming or mutating `20260914-cpu-first-04`, copying its comparison
into Stage 02, rewriting run manifests, or treating existing page decisions as
accepted reconstruction output.

## Review accounting

Elapsed time: approximately 13 minutes  
Token use: unavailable exact critic token accounting  
Changed files: this receipt only

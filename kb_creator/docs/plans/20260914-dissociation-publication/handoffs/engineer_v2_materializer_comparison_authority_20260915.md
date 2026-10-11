# Engineer receipt: v2 materializer comparison authority

Date: 2026-09-15  
Assignment: engineering, `gpt-5.6-sol`, high reasoning; user-scoped override active.  
Scope: bounded RunSpec v2 Stage 06 comparison authority; no live run, source/model/runtime mutation, network, GPU, remote service, API, Git operation, or immutable-run mutation.

## Result

READY FOR INDEPENDENT CLOSURE REVIEW.

- RunSpec v2 materialization now requires an all-or-none explicit comparison path and SHA-256 pair. The only accepted v2 path is the run-local `outputs/03-compare-views/comparison.json`, and its identity must equal the sealed review-queue record.
- Stage 06 obtains that pair from the already validated queue and emits each CLI flag exactly once. It never computes a fresh SHA to bless arbitrary bytes.
- The materializer revalidates live RunSpec identity, all four upstream stage manifests/outputs, queue seal and comparison identity, Stage 04 visual/geometry bindings, Stage 02 view-set identity, and queue-to-merge-packet identities before candidate parent/staging creation.
- Recursive lexical containment rejects symlinks and every Windows reparse-point class, including junctions and mount points, before traversal or path resolution. Windows fails closed when `st_file_attributes` is unavailable.
- The historical `<raw-root>/comparison/comparison.json` omission fallback is retained only for absent/explicit v1 bundle metadata. Unknown bundle schemas fail closed. `MERGE_PROVENANCE.json` retains its exact schema/key set and records the selected authoritative comparison path.
- Resume cache identity remains bound through the validated Stage 03/04 manifests, queue seal and existing implementation inventory. This implementation change makes old RunSpec v2 roots stale; it was not tested by resuming or editing immutable run `20260914-cpu-first-04`.

## Owned changes

- `kb_creator/scripts/materialize_mineru_ai_merge.py`
- `kb_creator/pipeline/reconstruction.py`
- `kb_creator/tests/test_materialize_mineru_ai_merge.py`
- `kb_creator/tests/test_mineru_cpu_packet_b.py`
- `kb_creator/README.md`
- this receipt

No schema change was required: the authority is a CLI/control-plane input bound to existing sealed RunSpec, review queue, stage, comparison, view-set, visual-manifest and geometry-plan contracts.

## Verification

- Focused legacy materializer plus new reparse/v2 authority test: `37 passed`.
- Full relevant regression:
  - `test_materialize_mineru_ai_merge.py`
  - `test_mineru_cpu_packet_b.py`
  - `test_reconstruction_control_plane.py`
  - `test_mineru_visual_merge_bundle.py`
  - `test_audit_mineru_ai_merge_fidelity.py`
  - `test_reconstruction_promotion.py`
  - `test_reconstruction_promotion_adversarial.py`
  - result: `184 passed, 1 skipped` in `104.92s`.
- Python compile: materializer, reconstruction control plane and both changed test modules passed.
- Post-hardening focused adapter/v2 authority rerun: `2 passed`.
- Contract JSON parse: `28 schemas parsed`.
- `git diff --check`: passed; only pre-existing workspace line-ending warnings were emitted.

Adversarial coverage includes: v2 without a Stage 02 legacy comparison; zero flags; either one flag; wrong SHA; outside/wrong fixed path; resealed queue path drift; resealed queue byte-count drift; resealed Stage 04 visual comparison-graph drift; missing validated queue in the v2 adapter; exact-once adapter flags; no candidate output after authority failures; nested symlink/junction/mount-point rejection; and Windows attribute-inspection failure.

## Risks / next action

- P0: none known.
- P1: none known.
- P2: upstream validators are deliberately reused as private in-process control-plane functions to keep Stage 06 validation identical to resume validation. An independent critic should confirm this coupling and the recursive Win32 reparse proof before authorizing a fresh run.
- Next action: independent `gpt-5.5` closure review. If approved, create a fresh RunSpec v2 run root; never resume `20260914-cpu-first-04`.

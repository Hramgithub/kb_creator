# Engineer receipt: v2 source-visible text completeness audit

- Result: implementation complete and ready for independent implementation criticism; no live reconstruction/resume was run.
- Role: engineering, `gpt-5.6-sol` / high under the user-scoped override.
- Scope: bounded RunSpec-v2 Stage05 completeness gate, Stage06 provenance binding, promotion/package verification, schemas, tests, and technical documentation.
- Immutable evidence: run `20260915-cpu-first-05`, its decisions, source, and all `.tools` payloads were not modified. The implementation identity has changed, so that run is intentionally stale and must not be resumed.

## Implemented

- Added explicit CLI modes: `legacy-v1` preserves the existing selected-block audit and substitution allowlist; `v2` refuses missing queue/comparison/decision-set authority.
- Added a v2 all-source-unit ledger over the exact three required CPU views. Every non-empty textual block, including short text and page numbers, receives page/view/raw-index/type/bbox/original-text/normalized-text identities.
- Added Unicode NFKC + casefold + alphanumeric-stream matching, directional full-source containment, ordered non-overlapping selected mappings, split/join support, no low-text exemption, and exact page-boundary evidence including hyphenated continuations.
- Added closed dispositions and fail-closed detection for omitted prefix, suffix, middle, whole short blocks, page starts, reordered blocks, extra unproven prose, missing required views, and duplicate selections.
- Added closed v2 reviewed allowlist semantics for exact substitutions, source-text exclusions, and visual assertions. Production validation binds authority and exact Stage04 visual bytes; `visual_only` additionally requires the named selected/materialized asset.
- Stage05 now binds queue, Stage03 comparison, decision set/page decisions, optional allowlist, and audit-policy schema in its cache inputs. The audit independently reopens the fixed run-local graph and validates run/stage/queue/comparison/packet/decision identities and non-reparse containment.
- Stage06 now adds the exact passing Stage05 audit identity to its cache inputs and CLI. The v2 materializer requires the fixed Stage05 path+SHA and emits `kb_creator.mineru_ai_merge_provenance.v2` with identical audit and authority bindings.
- Promotion and package verification branch on the sealed run schema: v2 rejects audit/provenance downgrade, replaced audit bytes, authority drift, incomplete pages, any completeness below 1.0, any unaccounted unit, or package/provenance mismatch. Legacy v1 remains unchanged.
- Added both new schemas to the reconstruction implementation inventory and extended the stage-manifest input-kind enum.

## Changed files

- `kb_creator/scripts/audit_mineru_ai_merge_fidelity.py`
- `kb_creator/scripts/materialize_mineru_ai_merge.py`
- `kb_creator/pipeline/reconstruction.py`
- `kb_creator/pipeline/reconstruction_promotion.py`
- `kb_creator/contracts/ai_merge_fidelity_audit.v2.schema.json`
- `kb_creator/contracts/ai_merge_fidelity_reviewed_allowlist.v2.schema.json`
- `kb_creator/contracts/stage_manifest.v1.schema.json`
- `kb_creator/tests/test_audit_mineru_ai_merge_fidelity.py`
- `kb_creator/tests/test_mineru_cpu_packet_b.py`
- `kb_creator/tests/test_reconstruction_control_plane.py`
- `kb_creator/README.md`
- this receipt

## Verification

- Python compile: passed for audit, materializer, reconstruction control plane, and promotion modules.
- JSON Schema draft-2020-12 meta-validation: both new schemas passed.
- Focused v1/v2 audit tests: `20 passed` after adding v2 adversarial cases.
- Final relevant regression:
  - `test_audit_mineru_ai_merge_fidelity.py`
  - `test_materialize_mineru_ai_merge.py`
  - `test_reconstruction_control_plane.py`
  - `test_mineru_cpu_packet_b.py`
  - `test_reconstruction_promotion.py`
  - `test_reconstruction_promotion_adversarial.py`
  - result: **186 passed, 1 skipped** in 102.26 seconds.
- Focused final authority/schema assertions: **22 passed**.
- Post-hardening compile plus audit/materializer authority regression: **57 passed**; `git diff --check` returned no whitespace errors (only pre-existing Windows line-ending warnings for unrelated working-tree files).
- No MinerU, source PDF, network, GPU, remote/API, run resume, or Git mutation command was executed.

## Risks

- P0: none known.
- P1: none known after the final regression. The production v2 package branch is implemented but still requires the mandated independent critic before any fresh run.
- P2: automatic completeness remains limited to text visible in at least one required CPU view; text missed by all three requires an exact reviewer-authored visual assertion, as specified by architecture.

## Next action

Independent critic reviews the implementation and adversarial coverage. If closed, the orchestrator creates a fresh immutable v2 run and revalidates decisions against its exact queue/comparison/packet identities; do not resume `20260915-cpu-first-05`.

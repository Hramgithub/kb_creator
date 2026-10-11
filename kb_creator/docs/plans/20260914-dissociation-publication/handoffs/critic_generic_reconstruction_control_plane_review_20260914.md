# Independent critic receipt - generic reconstruction control plane review

## Assignment receipt

- Goal id: `20260914-dissociation-publication`
- Step id: `3b-generic-reconstruction-control-plane-architecture-review`
- Review kind: `architecture`, `process`
- Role: independent critic
- Requested model: `gpt-5.5`
- Requested reasoning effort: `medium`
- Actual platform model/effort: unavailable; repository-policy assignment only
- Participation declaration: I did not implement or materially design the candidate under review.
- Orchestrator policy owner: `gpt-5.6-sol` at `medium`; actual platform identity unverified
- Assignment state: `platform-unverified`
- Scoped override: none
- Scope: read-only criticism of the proposed minimal Wave 0 generic reconstruction control plane and its process boundary. No implementation, schema, contract, canonical plan/context/status, source, generated, release, or Git files were edited.
- Recommendation: reject as-is for live Dissociation execution until the contract authority issue in Finding P1-1 is remediated. After that narrow remediation, the Wave 0 control-plane architecture is acceptable for bounded implementation.
- Timestamp: `2026-09-14T03:20:34+03:00` (`Europe/Moscow`)
- Elapsed time: approximately `00:18:00`
- Token use: unavailable

## Files checked or changed

Checked:

- `docs/governance/nri_goal_governance.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/plan.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/context.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_pdf_reconnaissance_20260914.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_generic_runner_gap_audit_20260914.md`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_generic_reconstruction_control_plane_spec_20260914.md`
- `.agents/skills/kb-creator-scenario-reconstruction/SKILL.md`
- `kb_creator/contracts/scenario_contract.v1.schema.json`
- `kb_creator/scripts/prepare_mineru_three_view_inputs.py`
- `kb_creator/scripts/run_mineru_three_view.ps1`
- `kb_creator/scripts/compare_mineru_three_views.py`
- `kb_creator/scripts/audit_mineru_ai_merge_fidelity.py`
- `kb_creator/scripts/materialize_mineru_ai_merge.py`
- `kb_creator/scripts/build_mineru_visual_merge_bundle.py`
- `kb_creator/tests/test_mineru_three_view_tools.py`
- `kb_creator/tests/test_audit_mineru_ai_merge_fidelity.py`
- `kb_creator/tests/test_materialize_mineru_ai_merge.py`
- `kb_creator/tests/test_mineru_visual_merge_bundle.py`

Changed:

- added this receipt only:
  `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/critic_generic_reconstruction_control_plane_review_20260914.md`

## Evidence summary

- Governance requires contributor receipts, critic independence, orchestrator ownership remaining in the main chat, and immutable release receipts invalidated by candidate mutation. This receipt follows that boundary and does not transfer orchestration ownership.
- The active plan and context define the user-authoritative chain as accepted `MASTER_RU` plus accepted ArtView/effective configs to HTML to DOCX to PDF. Direct HTML-to-PDF is forbidden, and ArtView/decision/config evidence is mandatory package content.
- The reconstruction skill is explicitly limited to source reconstruction and excludes promotion, acceptance, MASTER stages, publication, Git, and release review.
- The five routed reconstruction tools are real and mostly scenario-neutral, but `prepare_mineru_three_view_inputs.py` currently enforces `LETTER = (612.0, 792.0)` and `build_mineru_visual_merge_bundle.py` currently carries the inherited 124-page role table.
- The candidate spec correctly scopes Wave 0 to `reconstructed_en`, fixed-stage reconstruction, run/stage identity, review queue, external decisions, resume/cache validation, and no publication target.
- `ScenarioContract.v1` is not reconstruction-neutral as a runtime contract: it requires downstream artifact keys, fixes `policies.render.profile` to `viral_print`, and defines PDF acceptance as gated by `accepted_html`.

## Findings

### P1-1 - Dissociation must not run on `ScenarioContract.v1` as a runtime authority while it hard-codes Viral publication policy

`ScenarioContract.v1` cannot safely be used as the Dissociation runtime contract for a live run. The architecture spec says the Wave 0 runner will ignore downstream v1 fields and reject targets after `reconstructed_en`, but the contract itself would still be a durable scenario authority that falsely declares `policies.render.profile: viral_print` and `pdf.automated_gates: ["accepted_html", ...]`.

That is not a harmless unused field. It violates the active goal's rule not to reuse Viral/Innsmouth publication policy as Dissociation facts, conflicts with the corrected DOCX-only publication boundary, and creates a stale authority artifact that later stages could accidentally or selectively trust. A copied `viral_print` constant is also exactly the sort of scenario-specific leakage the user prohibited, even if no scenario-named script is added.

Exact remediation:

1. Before any live Dissociation run, add a narrowly versioned, reviewed contract/schema boundary that can represent reconstruction without inheriting Viral publication policy.
2. The minimum acceptable shape is either `ScenarioContract.v2` or a separate `ScenarioReconstructionContract.v1`; it must contain only scenario/source/scope/page-role/reconstruction review authority needed by Wave 0, or must make downstream publication fields explicitly absent or non-authoritative for reconstruction.
3. The Wave 0 runner must reject `ScenarioContract.v1` runtime contracts for new Dissociation execution unless they are converted through that reviewed neutral boundary.
4. The new boundary must not add runtime paths, executables, run roots, shell fragments, ArtView decisions, DOCX generation, PDF generation, or production packaging to Wave 0.
5. Publication remains a later versioned contract/profile that explicitly models accepted ArtView, accepted decisions, effective configs, HTML, DOCX, PDF-from-DOCX, production inventory, exclusions, freeze, and invalidation on mutation.

This is blocking for live execution, not for synthetic control-plane implementation.

### P2-1 - The sixth visual-bundle adapter is acceptable only if legacy role fallback is impossible on new contract-driven runs

The spec correctly identifies `build_mineru_visual_merge_bundle.py` as an unavoidable sixth bridge because the materializer needs its merge packets. The risk is that its default `expected_pages = 124` and `ROLES` table can still silently produce Viral-shaped role authority if the runner forgets to pass the reviewed contract-derived role map.

Exact remediation:

1. Add an implementation test that a new runner invocation fails closed when no contract-derived role map is supplied to the visual-bundle adapter.
2. Keep the 124-page fallback only behind direct legacy CLI/API compatibility, not behind the generic runner path.
3. Add a regression assertion that a synthetic six-page run emits only roles derived from its contract and contains no Viral/Innsmouth page ranges or role labels unless they are explicit fixture text.

This is not a blocker if enforced in the first implementation packet.

### P2-2 - Stage/resume identity needs one explicit negative test for downstream target rejection

The proposed stage and resume identity rules are strong: immutable `run.json`, run-local reuse only, output inventory hashes, upstream manifest hashes, tool and implementation identity, unsafe path/reparse checks, and fail-closed mismatch behavior. The publication boundary is also architecturally preserved by limiting Wave 0 to `reconstructed_en`.

The remaining risk is process drift: a public `target` flag exists, so the implementation must prove that `master_en`, `master_ru`, `html`, `docx`, `pdf`, `production`, and any direct HTML-to-PDF-like spelling are rejected before writes.

Exact remediation:

1. Include a parameterized CLI/preflight test for unsupported targets.
2. Assert unsupported targets create no `run.json`, no run root, and no stage directory.
3. Assert no Wave 0 schema or manifest declares PDF upstream as `accepted_html`.

This is not a blocker if included in the first implementation packet.

## Areas Accepted

- Safety and scope: accepted after P1-1 remediation. The spec avoids source mutation, generated artifact mutation outside owned run roots, scenario-specific scripts, release state, Git actions, and canonical plan/status edits.
- Overengineering: accepted. A fixed graph, run-local cache only, no shared cache, no plugin system, no database, no arbitrary DAG, and no publication implementation is the right minimal shape.
- Backwards compatibility: accepted with the specified parity tests for the existing five CLIs and legacy visual-bundle behavior.
- Arbitrary page geometry: accepted for Wave 0 as uniform MediaBox plus uniform rotation only, with mixed geometry rejected because v1 cannot represent it.
- Immutable inputs: accepted. Read-only reparse-backed source files may be admitted only by exact byte/hash/geometry identity; writable run roots may not be reparse-backed.
- Stage/resume/cache identity: accepted, provided implementation follows the manifest/cache-key checks and fails without overwriting stale runs.
- Review queue and decision authority: accepted. Per-page queue items, external hash-bound decision sets, no auto-decision, and no materialization with open/unreviewed decisions satisfy the reconstruction boundary.
- CLI injection and path boundaries: accepted in design. Existing scripts already prefer structured arguments and safe relative references; the new runner must continue passing argv arrays and reject shell fragments, Python import paths, absolute/escaping owned paths, symlinks, junctions, and reparse-backed writable roots.
- Separation from later publication: accepted only because Wave 0 exposes no publication target. The corrected publication chain is preserved conceptually but must not be represented by `ScenarioContract.v1`.

## Blockers

- Blocking for live Dissociation reconstruction: P1-1. A neutral versioned reconstruction contract boundary is required before a live Dissociation run can be authorized.
- Not blocking synthetic Wave 0 implementation: P2-1 and P2-2, if their exact tests and fail-closed controls are included in the implementation packet.
- Test environment remains a separate engineering blocker noted by the prior audit: pytest/PDF dependencies were not available in the inspected environment.

## Recommendation

Do not authorize a live Dissociation run using `ScenarioContract.v1` as the runtime contract. Authorize only a bounded implementation packet that first introduces the neutral versioned reconstruction contract boundary, then implements the generic Wave 0 control plane with the P2 controls above.

After that remediation is implemented and tested, a follow-up implementation review should verify:

- the runner rejects old v1 runtime contracts for new Dissociation execution;
- no `viral_print`, `accepted_html -> pdf`, Viral/Innsmouth role range, or publication target leaks into new-run authority;
- synthetic non-Letter/asymmetric-CropBox/rotation tests pass;
- unsupported downstream targets fail before writes;
- closed decision sets are hash-bound to the review queue and materialization emits a candidate only, not acceptance.

## Next action

Main-chat orchestrator should amend the bounded implementation packet to require a narrow neutral reconstruction contract/schema before live Dissociation execution, then dispatch engineering only for Wave 0 reconstruction control-plane files and tests. Publication contract, ArtView production packaging, DOCX, PDF, release freeze, and release review remain later scoped work.

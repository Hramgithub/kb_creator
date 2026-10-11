# Independent critic receipt: source-visible text completeness architecture

- Review kind: architecture
- Candidate under review: `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_source_visible_text_completeness_audit_20260915.md`
- Scope: independent architecture review of the proposed v2 source-visible text completeness audit and its Stage05/Stage06/package authority binding.
- Implemented or materially designed candidate: no
- Orchestration ownership: remains with the main `20260914-dissociation-publication` orchestrator; this receipt does not transfer ownership
- Orchestrator policy owner: repository `AGENTS.md` plus `docs/governance/nri_goal_governance.md`
- Assignment state: complete
- Scoped override: architecture review only; no implementation, run, decision, source, `.tools`, live reconstruction, network, GPU, remote/API, or Git mutation; this receipt is the only changed artifact
- Timestamp: 2026-09-15T01:26:35.0740190+03:00
- Elapsed time: approximately 1.9 minutes of active goal accounting at receipt drafting
- Token use: goal tool reported 82,526 tokens used at receipt drafting

## Verdict

GO for the bounded implementation described by the architect receipt.

NO-GO remains for any v2 Stage05 resume, Stage06 materialization, reconstruction promotion, or acceptance until the v2 source-visible completeness gate is implemented, tested, and independently closed.

The architect identified the correct root cause: the existing v1 audit measures decision text against reviewer-selected blocks only. It does not enumerate all source-visible text evidence units from the required views, so an unselected longer OCR/raster block can carry source text outside the audit denominator while selected recall still passes. The page 5 `Laboratory` omission and the page 3/4 continuation case are valid seed examples of a class-level P1 gate defect.

## Files checked

- Governance and routing:
  - `AGENTS.md`
  - `docs/governance/nri_goal_governance.md`
  - `.agents/skills/kb-creator-scenario-reconstruction/SKILL.md`
  - `kb_creator/README.md`
- Architecture and prior review:
  - `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/architect_source_visible_text_completeness_audit_20260915.md`
  - `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/critic_dissociation_decisions_run_05_closure_20260915.md`
- Current run/decision evidence:
  - `kb_creator/working/dissociation/reconstruction/20260915-cpu-first-05/review/review_queue.json`
  - `kb_creator/working/dissociation/reconstruction/20260915-cpu-first-05/outputs/03-compare-views/comparison.json`
  - `kb_creator/working/dissociation/reconstruction/20260915-cpu-first-05-decisions/decision_set.json`
  - `kb_creator/working/dissociation/reconstruction/20260915-cpu-first-05-decisions/pages/page-004.json`
  - `kb_creator/working/dissociation/reconstruction/20260915-cpu-first-05-decisions/pages/page-005.json`
- Relevant implementation surfaces inspected read-only:
  - `kb_creator/scripts/audit_mineru_ai_merge_fidelity.py`
  - `kb_creator/pipeline/reconstruction.py`
  - `kb_creator/scripts/materialize_mineru_ai_merge.py`
  - `kb_creator/pipeline/reconstruction_promotion.py`
  - `kb_creator/contracts/stage_manifest.v1.schema.json`
  - `kb_creator/contracts/reconstruction_upstream_manifest.v1.schema.json`
  - `kb_creator/contracts/run_spec.v2.schema.json`
  - `kb_creator/tests/test_audit_mineru_ai_merge_fidelity.py`
  - `kb_creator/tests/test_materialize_mineru_ai_merge.py`
  - `kb_creator/tests/test_reconstruction_control_plane.py`
  - `kb_creator/tests/test_reconstruction_promotion.py`
  - `kb_creator/tests/test_reconstruction_promotion_adversarial.py`

## Evidence

- Existing audit root cause is confirmed in `kb_creator/scripts/audit_mineru_ai_merge_fidelity.py`:
  - `_selected_tokens` builds the source denominator only from `decision["selected_blocks"]`.
  - `recall_failed = len(selected) >= 20 and recall < recall_threshold` creates a short-text exemption.
  - The only reviewed exception mechanism is the legacy closed substitution allowlist `{allowlist: [...]}`.
- Current corrected decision evidence is consistent with the architect's statement that instance repairs happened outside this critic:
  - `page-004.json` SHA-256 `792E9638C5BF507FFD5AB5E9D4710A391B87E544D97ADEBB447AC62BDBA4E7CE`; it includes the page 3/4 continuation and selects `raster_pipeline_ocr:48`.
  - `page-005.json` SHA-256 `56D243C1753A85CFD9E2B6A6DAB35ACB858D10863A132B2ABE090B1C5B79E85A`; it selects `raster_pipeline_ocr:75`, closing the previously observed `Laboratory` suffix omission at the decision-instance level.
  - `decision_set.json` SHA-256 `76845A32377595F074C88BA9F3899FFF05777275E7864734C25F13BFA5F20ECB`.
- Current sealed authority evidence:
  - review queue file bytes/SHA-256: `5232` / `E15F5DAEABBFC56A57664088C7792CA6AEBED18D0B6FEC34B6ACAEB1EEA310D0`
  - review queue internal seal: `4D68E89A72B628F735542BD693580E30897980B52D62BD6BEABE41ECD10B271F`
  - queue-pinned Stage03 comparison: `outputs/03-compare-views/comparison.json`, `449244` bytes, SHA-256 `7136F138D81C0A47F1CF30918985D7ED1B41BCDC36BF30A0B38860039BCCB19E`
  - no `outputs/05-fidelity-audit` directory exists at inspection time.
- Existing Stage05/Stage06 binding gap is confirmed:
  - `production_resume_adapters` currently passes decision pages, merge packets, optional reviewed allowlist, and output path to the v1 audit; it does not pass queue/comparison identities to Stage05.
  - Stage06 receives explicit comparison authority for v2 materialization, but `MERGE_PROVENANCE.json` remains schema v1 and does not bind the exact passed audit identity.
  - Promotion currently validates `kb_creator.ai-merge-fidelity-audit/v1` and v1 provenance shape.

## Architecture assessment

The design is authority-sound and proportionate:

- Authority: it requires Stage05 to re-open and verify queue, comparison, packet, decision-set, page-decision, and reviewed-allowlist identities before writing a v2 report. This closes the current gap where Stage05 trusts only decision pages and packet root.
- Coverage/disposition: it introduces a source-text ledger over every non-empty textual block from required CPU views, while leaving optional GPU views out of automatic completeness semantics. Every unit must be included, safely equivalent, explicitly excluded with visual evidence, or covered by a visual assertion.
- Defect detection: it directly catches the prior page 5 class because a longer unselected raster unit with an unmatched source suffix is `unaccounted`; it also catches short cross-page continuations because there is no `<20` exemption in the completeness gate.
- Visual-only and exclusions: the reviewed-allowlist v2 design keeps substitutions separate from source-text exclusions, requires exact unit identities, text hashes, visual evidence, rationales, and materialized asset binding for `visual_only`.
- Cross-page and reading order: it requires page-boundary records, independent two-sided coverage, hyphenated-continuation classification, and monotonic non-overlapping Markdown span mappings in selected-block order.
- Thresholds: it correctly keeps the existing `0.95` selected-block recall as a separate accuracy signal and makes v2 source completeness exact: `1.0`, zero unaccounted units, zero source-only deletions.
- Resume/cache/package binding: it explicitly changes Stage05 cache inputs, requires Stage06 to consume the exact passed audit identity, requires `MERGE_PROVENANCE` schema bump, binds audit/allowlist into promotion package evidence, and invalidates pre-fix v2 runs through implementation inventory drift.
- Legacy compatibility: it preserves current v1 audit semantics only for explicit run-spec v1 mode and prevents v2 downgrade to v1 audit/provenance.
- Scope/minimality: the bounded surface is appropriate. It touches the audit, reconstruction control-plane resume/cache, materializer provenance, promotion, schemas, and tests, while avoiding comparison producer, OCR provider, immutable run/source files, and publication content.

The P1-before-Stage05/06 classification is correct. Manually corrected page decisions close known instances but do not close the reusable gate defect. Stage05 is the fail-closed fidelity gate before Stage06 candidate creation; allowing a known selected-only audit to pass v2 materialization would make the pipeline capable of freezing omitted source-visible text again.

## Findings

### P0

None.

### P1

None.

### P2

1. Implementation clarification: the architecture allows automatic equivalence by normalized equality/containment, but implementation must interpret containment in the direction of full source-unit coverage. A selected or rendered substring must never satisfy a longer source unit with an unmatched source-only prefix or suffix. The acceptance criteria and source-only deletion rule already imply this, so this is a clarification rather than a blocker.

## Blockers

- No architecture blocker to bounded implementation.
- Operational blocker remains exactly as stated by the architect: v2 Stage05/Stage06/promotion must not proceed until this design is implemented, tested, and independently reviewed.
- Implementing this design changes the sealed implementation identity; pre-fix v2 runs, including `20260915-cpu-first-05`, must not be resumed under the changed code.

## Recommendation

Proceed with bounded implementation of the architected v2 source-visible completeness audit, including the full adversarial matrix and schema/cache/provenance/promotion binding. After implementation, require independent implementation closure before any fresh v2 reconstruction run or Stage05/Stage06 resume decision.

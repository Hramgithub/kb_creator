# Independent critic review: Viral Step 6A reconstruction-builder packet

## Receipt metadata

- Goal: `20260830-kb-creator-next-scenario`
- Step: Viral Step 6A generic reconstruction-builder packet
- Review kind: process/architecture
- Role/model/effort requested: fresh independent critic, `gpt-5.5`, medium
- Actual platform model/effort: unavailable to reviewer
- Orchestrator policy owner: main chat `gpt-5.6-sol`, medium
- Assignment state: `nri-independent-critic`
- Scoped override: none
- Independence declaration: I did not implement, materially design, or remediate the candidate packet or the implementation under review.
- Timestamp: 2026-08-31T20:43:54+03:00
- Elapsed time: unavailable after task compaction; bounded active review continued from prior turn
- Token use: unavailable
- Worktree: `D:\NRI\.worktrees\kb-creator-viral`
- Required branch/HEAD: `codex/kb-creator-viral` / `54607bd3b9362adbb0c4bca64e8751482797f380`
- Observed branch/HEAD: `codex/kb-creator-viral` / `54607bd3b9362adbb0c4bca64e8751482797f380`

## Candidate identity

Reviewed packet:

- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_step6a_reconstruction_builder_packet_20260831.md`
- Expected SHA-256: `F5B5684591586BFE7C22D0F73C67B4B3A849A206495FFEFF8261E3CE2E97138C`
- Observed SHA-256: `F5B5684591586BFE7C22D0F73C67B4B3A849A206495FFEFF8261E3CE2E97138C`
- Hash result: pass

Bound predecessor identities verified:

- Original Step 6 packet `terra_engineering_viral_source_reconstruction_packet_20260831.md`: `011CF87FFA0B0DACC85559DEF601A5FD9EED0755F86EB877C263CF2F2D8FABBC`
- Origin-semantics delta `terra_engineering_viral_step6a_origin_semantics_delta_20260831.md`: `0894966630FA19022033AA3D93CE67B98C7B44244BADB022ED0EC2BAD08DDA2C`
- Accepted salvage critic receipt `gpt55_critic_viral_step6a_engine_output_salvage_review_20260831.md`: `2FE4EEA41760F0068A30B6A551E04F5B901F4DB6208B83E952C815905FE638E4`
- Raw recovery executor receipt `luna_executor_viral_step6a_engine_output_salvage_20260831.md`: `9FD0FBA8B1EADDBAB7AC1199BA2D01371896D9E18D49EC85C8369C08D5011C42`

Bound recovered input identities verified:

- Recovered input root: `kb_creator/working/viral/source_reconstruction/20260831_step6a_engine_output_salvage_candidate`
- `RECOVERY_MANIFEST.json`: `41F00E41D04A19071FF0418068D7A1744C412F6EC6CDBEB7CFEE580B32B09169`
- `RECOVERY_EVIDENCE.json`: `F1F9F66AB3EA9C09196221CA82FDFEA888C94AAE024891057CA1A20FA53179BC`
- Recovered-root payload check: 209 payload files, 21,220,717 payload bytes, 204 JPEG files, zero PDF files, no `_bridge_runtime` or cache payload paths.
- Recovered Markdown/JSON check: 387,142 Markdown characters, 112 Markdown image references, zero missing Markdown image references, content-list v1 page indices covering 0..123, v2/middle/model each covering 124 page records.
- Proposed reconstruction candidate root did not exist at review time: `kb_creator/working/viral/source_reconstruction/20260831_step6a_reconstruction_from_salvaged_engine_candidate`.

## Scope and files checked

Read fully or inspected for the bounded review:

- `D:\NRI\AGENTS.md`
- `docs/governance/nri_goal_governance.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/plan.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/context.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_source_reconstruction_packet_20260831.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_step6a_origin_semantics_delta_20260831.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_step6a_engine_output_salvage_review_20260831.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/luna_executor_viral_step6a_engine_output_salvage_20260831.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_step6a_reconstruction_builder_packet_20260831.md`
- Recovered root manifests and payload inventory under `kb_creator/working/viral/source_reconstruction/20260831_step6a_engine_output_salvage_candidate`
- Current generic seam, read-only:
  - `kb_creator/scripts/scenario_source_reconstruction.py`
  - `kb_creator/scripts/reconstruct_scenario_source.py`

Changed files:

- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/gpt55_critic_viral_step6a_reconstruction_builder_packet_review_20260831.md`

No implementation, source, runtime, accepted, production, plan, context, status, Git index, commit, or push mutation was performed.

## Assessment

The packet is safe as a process/architecture authorization for the next bounded implementation slice.

It correctly changes the Step 6A boundary from “rerun MinerU” to “build a reviewable reconstruction candidate from recovered raw engine input plus read-only admitted source/contract evidence.” It preserves the user clarification that generated MinerU outputs such as `origin.pdf`, layout PDFs, metadata, text, and raster images are expected engine outputs, while byte identity applies only to the admitted input and temporary upload transport. The packet does not reintroduce the rejected generated-origin byte-identity requirement.

The packet also correctly keeps the recovered raw engine output non-authoritative. The recovered Markdown, four JSON files, and 204 images are admitted as raw engine input only; the builder must source-anchor reconstruction decisions against the admitted PDF/ScenarioContract evidence and emit `candidate_needs_review`, not `reconstruction_ready`, `MASTER`, accepted output, or publication material.

The proposed no-MinerU/no-OCR/no-model/no-network boundary is coherent for this slice. The builder may render source pages and create review artifacts, but it must not launch MinerU, GPU/model code, OCR, or historical translation/config evidence. The stated run root is fresh and closed, the allowlist is narrow, and the existing 15 `pdf_raw` collection errors remain a repository-wide diagnostic exclusion rather than a Step 6A acceptance blocker.

The current generic seam still contains old run-specific MinerU bridge/runtime assumptions, including `RUN_RELATIVE`, `ORIGIN_RELATIVE`, pinned MinerU runtime identity checks, child environment setup, and MinerU launch/source-copy modeling. The packet explicitly requires this to be generalized away from the obsolete runtime/MinerU successor assumptions instead of forking another implementation path. That is acceptable because the current runtime bridge code is not an accepted production API and is directly incompatible with this no-rerun salvage slice. The implementation should still keep the new recovery build mode closed and reviewable rather than silently deleting useful validation concepts such as path resolution, manifest binding, mutation audit, and deterministic verification.

The full-schema target is ambitious but not false authority as specified. The packet requires 124 pages/renders, deterministic zero-based page mapping, 39 handouts, maps/pregens/back-cover closure, source-render review assets, provenance/QA schemas, and open `needs_review` handling for pages or semantic blocks that cannot be safely normalized without invention. Because the output state is only `candidate_needs_review`, this does not claim final reconstruction completeness or release readiness.

## Findings

### P0

None.

### P1

None.

### P2

1. Ambiguous stop wording for expected review uncertainty.

   Evidence: the packet correctly says uncertainty must become `needs_review`/open and the candidate state must remain `candidate_needs_review`, but its stop list also includes broad wording for “uncertain semantic/format/asset mapping.” In this slice, some review uncertainty is expected, especially for content-mode pages 1-5, dense layout fidelity, handout/map/pregen presentation, and any source-visible semantic choice that cannot be fully proven from recovered engine JSON alone.

   Risk: an executor could interpret all review uncertainty as a hard stop and fail to produce the intended reviewable candidate, or conversely could suppress uncertainty to satisfy the full-schema target.

   Required remediation: implement the distinction explicitly. Hard stop only when a required provenance row, count, path, source anchor, asset ownership decision, or schema field cannot be produced without invention or false completeness. Represent ordinary visual/semantic uncertainty inside the candidate QA/provenance output as `needs_review`/open blockers while keeping overall state `candidate_needs_review`.

2. Preserve validation concepts while removing obsolete live-MinerU behavior.

   Evidence: current `scenario_source_reconstruction.py` contains old Step 6A bridge machinery, including `RUN_RELATIVE` for `20260831_step6a_origin_copy_exception_retry`, `ORIGIN_RELATIVE`, MinerU runtime verification, child environment construction, and a MinerU launch path. The packet requires the three generic files to be refactored rather than adding a fourth reusable file and forbids MinerU/OCR/model/network execution for this builder.

   Risk: an implementation that simply deletes the old bridge code could also drop still-useful generic validation ideas: canonical source resolution, immutable manifest binding, fresh-root admission, reparse/path containment checks, mutation audits, deterministic verification, and closed state transitions.

   Required remediation: remove or isolate the obsolete live-MinerU/origin-byte-identity behavior for this slice, but carry forward the generic validation concepts into the recovery builder. If preserving a future live extraction entrypoint is necessary, it should be a separately reviewed closed action/mode, not an implicit side effect of the recovery builder.

## Required review points

- Generic builder authorization: acceptable. It may produce the full original Step 6A closed schema as a review candidate from recovered Markdown, four JSON files, 204 images, admitted source, contract, and source renders, provided it does not claim release readiness.
- MinerU/OCR/model/network exclusion: acceptable and required.
- Historical translation/config exclusion: acceptable and required.
- Exact run root and allowlist: acceptable. The fresh candidate root was absent at review time.
- Existing three-file refactor: acceptable for this slice, with P2 caution to preserve validation concepts and not imply a future live-MinerU action.
- Deterministic page mapping: acceptable. Recovered evidence supports 0-based engine pages 0..123 mapped to source pages 1..124.
- Source-anchored semantic blocks/layout fidelity: acceptable if uncertain blocks are surfaced as open QA/provenance review items, not invented.
- 124 pages/renders: acceptable and necessary.
- 39 handouts, maps, pregens, back cover: acceptable as builder requirements, but failures must remain hard stops or explicit `needs_review` blockers rather than silent completeness claims.
- Asset ownership/duplicate policy: acceptable.
- Content-mode pages 1-5 unknown: acceptable because the packet keeps mode proposals reviewable and non-final.
- Reference-only audit: acceptable; the audit may identify prior outputs without opening or using historical translation/config as authority.
- Provenance/QA schemas and `candidate_needs_review` boundary: acceptable.
- Render/contact-sheet choices: acceptable as review evidence, not release evidence.
- Hermetic tests: acceptable. They should cover fixtures and failure modes without real PDF/MinerU/GPU/OCR/network dependencies.
- 15-error diagnostic: acceptable as a known repository-wide collection issue, not a Step 6A blocker.
- Mutation audits and stop conditions: acceptable with the P2 clarification above.

## Recommendation and authorization decision

Recommendation: accept.

Implementation authorization: authorized after orchestrator resolution of this receipt. Material implementation may proceed within the packet’s stated bounds because no P0/P1 findings remain.

Exact authorized boundary:

- Implement only the bounded recovery-builder slice in the three generic source/test paths plus the executor receipt and the fresh candidate run root.
- Use the recovered raw engine root only as immutable input.
- Produce only `candidate_needs_review` reconstruction artifacts.
- Do not launch MinerU, OCR, GPU/model code, network activity, or historical translations/config.
- Do not promote any output to `reconstruction_ready`, MASTER, accepted, production, or publication.
- Stop on path/count/hash/schema/source-anchor/provenance violations or any need to invent content.

Residual risks:

- Dense page-layout and image-placement fidelity remains review-dependent until the candidate is rendered and visually checked.
- Pages 1-5 content mode, handout/map/pregen segmentation, and duplicate/derived asset ownership may still surface open candidate QA items.
- A later release review remains required before any accepted/production/publication output can be claimed.

Blockers: none.

Next action: orchestrator may assign the bounded executor implementation for the reconstruction builder under the accepted packet and this receipt’s P2 clarifications.

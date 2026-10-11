# T7c — Stage 40 frontmatter flow root-cause receipt

- Timestamp: `2026-09-18T13:49:13+03:00`
- Assignment: read-only architecture/root-cause audit of publication run `20260918-publication-12`; no code, candidate, acceptance, plan/status/context, or output edits.
- Assignment state: `complete`
- Orchestrator policy owner: `/root` (`gpt-5.6-sol`, main-chat orchestration remains with parent)
- Scoped override: architecture/root-cause only; this receipt is the sole permitted write.
- Elapsed time: approximately 35 minutes
- Token use: approximately 12k architecture-agent tokens

## Result

The Stage 40 failure is a real fail-closed detection of a renderer ordering defect, not a bad Number 7 Dream policy and not an ArtView/Master RU defect.

The authoritative order is:

`page-001 (cover) -> page-002 (credits) -> toc:source -> page-004 (body)`

The quarantined output actually contains:

`page-001 (cover) -> toc:source -> page-002 (credits) -> page-004 (body)`

Only credits and the source TOC are swapped. The exact evidence is `quarantine/40-html-candidate/evidence/frontmatter_manifest.json:30-34`. The same observed order is embedded in `production_html_report.json:399-403`. The contract/config declares page 2 as credits, page 3 as source TOC, and the order `cover, credits, source_toc, body` in `kb_creator/inputs/number-7-dream/publication/v1/configs/html.json:8-10,35-40`. Contract v2 hash-binds that config as `260F180C326F53925116F12EE52BBC43F5875189ABD6E1C22CD63D9BF4F10C0C` (`kb_creator/contracts/number-7-dream.publication-v2.json`, minified line 1).

## Dependency trace and root cause

1. `_stage40_html_policy` correctly rejects any order inconsistent with page roles (`kb_creator/pipeline/publication_adapters.py:129-137`).
2. `_apply_stage40_html_policy` correctly emits one normalized `frontmatter_policy` containing `frontmatter_order` and `expected_flow` (`publication_adapters.py:141-169`). The quarantined `derived_html_config.json` line 1 contains that complete policy and contains no independently authored legacy placement hint.
3. The renderer exposes the normalized fields through `resolved_frontmatter_policy` (`translator/translator.py:2516-2545`).
4. In the code path used by run12, frontmatter placement moved only the landing/cover before the TOC and gated credits placement on the historical `credits_policy.frontmatter_position == "before_toc"` hint instead of the normalized `frontmatter_order`. The run12 report proves that branch: it says renderer `status: pass` with zero findings (`production_html_report.json:8,44`) and action only `moved_landing_before_toc` (`:449-453`), while its own manifest records TOC before credits.
5. The independent Stage 40 validator expands the declared roles into the expected concrete flow and rejects any different prefix (`publication_adapters.py:202-216`). That is the reported `frontmatter manifest flow disagrees with policy` failure. Quarantine is therefore correct.

Verdict: the primary defect belongs to the renderer ordering layer (`translator/translator.py`), where the already-normalized policy must be consumed. It must not be “fixed” by changing Number 7 Dream’s order, manually editing HTML, weakening `_validate_stage40_html_output`, or adding a scenario-only legacy flag.

## Required systemic remediation

1. Treat non-empty `resolved_frontmatter_policy()["frontmatter_order"]` as authoritative. Derive whether credits precede `source_toc`/`toc` from that order. Use the old `frontmatter_position` only as a compatibility fallback when no normalized order exists.
2. Keep the existing adapter validator as an independent postcondition. If a declared cover, credits block, TOC, or body start is missing/duplicated, placement or postcondition validation must fail; do not silently retain source DOM order.
3. Recommended renderer hardening: compare the final manifest prefix against `expected_flow` before returning renderer `pass`. Run12 shows that the renderer’s narrower `landing_toc_order` check can pass while the full contract fails.
4. Add `translator/translator.py` to `kb_creator/pipeline/publication.py::_implementation()` (current inventory list is `publication.py:399-424`) or bind an equivalent immutable renderer identity into the run identity before execution. Run12’s `run.json` implementation inventory does not include the renderer even though Stage 40 executes it. The success-only adapter receipt would record renderer bytes later, but that is insufficient to make a pre-existing run stale when renderer code changes.

During this audit another worker changed the shared working tree. Current `translator/translator.py:7736-7751` now contains `credits_before_toc()` and the placement calls at `:7774` and `:7814` use it. Current tests at `translator/tests/test_recovery_support.py:571-609` cover normalized order without the legacy hint and precedence over a conflicting legacy hint. Those changes were not made or verified by this architecture task. They align with item 1, but items 2-4 and the fresh-run implication still require integration/verification by the orchestrator.

## Required tests and acceptance criteria

- Renderer unit: source-cover flow with normalized `cover, credits, source_toc, body` and no `frontmatter_position` produces cover before credits before source TOC before body.
- Renderer unit: custom landing follows the same order.
- Precedence unit: normalized order overrides a conflicting legacy `frontmatter_position` hint.
- Negative units: a declared credits role with no unique credits section, a missing TOC, or an unsupported/duplicate role fails closed; no-credits policy remains `cover -> toc -> body`.
- Manifest/report unit: final `frontmatter_manifest.flow` must match the compiled expected prefix, and a mismatch makes renderer status fail rather than pass.
- Adapter integration: run the real renderer (not a fixture that hand-writes a valid manifest) with the Number 7 Dream contract/config and assert exact prefix `page-001,page-002,toc:source,page-004`, one source TOC, 18 ordered linked entries, and zero frontmatter findings. Existing adapter test `kb_creator/tests/test_publication_html_adapter.py:439-451` validates a hand-authored good manifest and therefore could not catch the renderer consumption gap.
- Control-plane identity test: publication implementation inventory includes `translator/translator.py`; changing its identity invalidates/resists resume of an older run.
- Run acceptance: do not promote run12 quarantine. After renderer and identity closure are integrated, start a fresh publication run (or otherwise prove a newly computed run identity includes the renderer), rebuild Stage 40, and accept only if renderer report, manifest, adapter receipt, structural QA, and visual QA agree.

## Files checked / changed

Checked:

- `kb_creator/working/number-7-dream/publication/20260918-publication-12/{run.json,quarantine/40-html-candidate/**}`
- `kb_creator/inputs/number-7-dream/publication/v1/configs/html.json`
- `kb_creator/contracts/number-7-dream.publication-v2.json`
- `kb_creator/pipeline/publication_adapters.py`
- `kb_creator/pipeline/publication.py`
- `translator/translator.py`
- `kb_creator/tests/test_publication_html_adapter.py`
- `translator/tests/test_recovery_support.py`

Changed only this receipt. No blockers to implementation were found. Next action: orchestrator/engineer integrates and verifies the renderer-order and implementation-identity fixes, then creates a fresh publication run and reruns Stage 40.

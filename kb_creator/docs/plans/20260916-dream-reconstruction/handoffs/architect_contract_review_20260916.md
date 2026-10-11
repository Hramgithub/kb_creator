# Architect contract review — Number 7 Dream

## Receipt

- Goal ID: `20260916-dream-reconstruction`
- Step ID: `2-contract-review`
- Role: architect (`gpt-5.6-sol`, policy effort `high`)
- Orchestrator policy owner: `gpt-5.6-sol`, effort `medium`, main chat
- Assignment state: `completed`
- Scoped override: `none`
- Timestamp: `2026-09-17T00:03:04+03:00`
- Elapsed time: approximately 25 minutes
- Token use: unavailable
- Scope: read-only review of the scenario reconstruction contract against the recorded immutable-source reconnaissance, the v1 schema, repository reconstruction policy, and all-page visual/text evidence
- Result: `READY_FOR_STEP_3_PREFLIGHT`; no P0 or P1 contract defect found. This is an architecture/topology review, not reconstruction acceptance, publication approval, or release review.

## Files and evidence checked

- `kb_creator/contracts/number-7-dream.reconstruction.json`
- `kb_creator/contracts/scenario_reconstruction_contract.v1.schema.json`
- `kb_creator/docs/plans/20260916-dream-reconstruction/plan.md`
- `kb_creator/docs/plans/20260916-dream-reconstruction/context.md`
- `kb_creator/README.md`
- `kb_creator/PROJECT_STATUS.md` (active-goal section)
- `.agents/skills/kb-creator-scenario-reconstruction/SKILL.md`
- `kb_creator/docs/architecture/KB_CREATOR_SCENARIO_PIPELINE_REUSE_REVIEW_20260902.md`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/scenario_contract_architecture.md`
- `tmp/pdfs/dream-reconstruction/contact-01.jpg` and `contact-02.jpg`, covering pages 1-26
- Read-only `pypdf` text-layer samples from source pages 1-3, 7, 9-10, 12-14, and 17-26; the immutable source was not changed.

## Dependency and data-contract trace

```text
verified external PDF identity
  -> reconstruction contract (source facts, 1..26 topology, entities, strategies)
  -> absent-root preflight
  -> three mandatory CPU views
  -> comparison/review queue
  -> identity-bound decisions and source-visible audit
  -> run-local reconstruction candidate
```

The contract is scenario data only. It neither embeds commands nor changes the fixed pipeline graph. Comparison, decisions, audit output, and candidates remain run-local, and `required_review: true` prevents strategy declarations from becoming acceptance authority.

## Verification and findings

### P0

None.

### P1

None.

### P2 advisories

1. The v1 schema has no structured pregenerated-character count. The contract still captures the source fact through the inclusive `pregenerated_characters` range 21-26 and trait `six_player_characters`; the contact sheets show one distinct pregen on each of those six pages. Step 3 and the later fidelity audit should therefore carry an explicit derived assertion of six distinct pregenerated characters rather than treating the free-form trait alone as a machine-enforced count.
2. A few ranges are deliberately conservative rather than page-exact: pages 12-14 are all marked `mixed` / `embedded_handout`, although the handout is concentrated on page 14, and pages 16-17 are both marked `mixed` / `illustrations`, although the large illustration is on page 17. This over-classifies visual review and cannot omit content. It is not a preflight blocker; split these ranges only if a later consumer interprets traits as per-page factual assertions rather than review triggers.

### Schema and topology evidence

- PowerShell 7 `Test-Json -SchemaFile` returned `schema_valid=True`.
- Inclusive range expansion covers exactly 26 rows and 26 unique pages: domain 1-26, `missing=[]`, `overlaps=[]`.
- Source identity matches canonical reconnaissance exactly: SHA-256 `C03AD05644C5B7438E4FAB750557EB8098E637492242D21969C5C4110FBF97D0`, 2,915,268 bytes, 26 pages, 612 x 792 points, rotation 0.
- Scope is `all_source_pages`, first page 1, last page 26, with five numbered player handouts required.
- Appendix B on pages 19-20 visibly contains handouts 1-5. Appendix C on pages 21-26 visibly contains six distinct pregenerated player characters.
- The union of page-role strategies equals the declared reconstruction strategy set: `embedded_text`, `reading_order`, `ocr_region`, and `visual_preserve`.

### Strategy review

- `reading_order` is present on every multi-column/text-bearing role where column order matters.
- `visual_preserve` covers the cover, illustrations, floorplans, embedded handout facsimiles, Appendix B, portraits, and all six character sheets. No source-visible visual class found on the contact sheets is left without visual closure.
- `ocr_region` is narrowly assigned to pages 19-20. This is supported by evidence: the page-19 embedded text extraction is interleaved/duplicated across handout blocks, while the embedded handouts sampled on pages 9 and 14 are already recoverable from the PDF text layer and separately protected by `visual_preserve`. The run may still escalate a disputed region, but whole-page OCR replacement is not authorized.
- `embedded_text` on the visual cover is valid because the cover contains source text; `content_mode: visual` does not mean zero text.

## Assumptions and risks

- Page ranges are inclusive, as used by the neutral tooling and schema semantics.
- The reconnaissance contact sheets are faithful full-page renders of the recorded source identity.
- Traits are QA triggers, not permission to omit content and not independent entity-count authorities.
- Residual risk is operational, not contractual: schema v1 cannot enforce six pregens, region coordinates are produced later as run evidence, and only fresh preflight can prove the external file still has the recorded identity.

## Acceptance criteria for the next gate

Step 3 may open a fresh run only when all of the following hold:

1. The external file still matches the recorded hash, byte count, 26-page count, page geometry, and rotation.
2. The contract still passes the v1 JSON Schema and semantic expansion remains exactly 1-26 with no gap or overlap.
3. The selected run root is absent and all required CPU providers/tools are bound without mutating the source.
4. Run evidence explicitly tracks five numbered handouts and six distinct pregenerated characters; the latter must not rely only on the free-form trait.
5. Every `ocr_region` use records page/region/input/output provenance and review status; `visual_preserve` produces closure evidence for every tagged visual page.
6. The run stops at the typed review queue and does not infer merge closure, reconstruction acceptance, publication, or release.

## Blockers and next action

- Blockers: none for Step 3 preflight.
- Next action: the orchestrator may run neutral preflight against an absent run root, preserving the five-handout and six-pregen assertions as explicit run checks. Canonical plan/context/status ownership remains with the orchestrator.


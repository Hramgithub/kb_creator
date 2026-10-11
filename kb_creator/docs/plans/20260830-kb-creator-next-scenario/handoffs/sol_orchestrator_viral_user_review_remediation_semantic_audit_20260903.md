# Viral candidate-first semantic audit implementation

- Goal: `20260830-kb-creator-next-scenario`
- Step: `7-user-review-remediation-semantic-audit`
- Owner: fresh `nri-engineer`, `gpt-5.6-terra` / `medium`
- Completion token: `READY_FOR_VIRAL_V2_CONFIG_AUTHORING`

## Objective and exclusive ownership

Complete the reusable semantic-unit proposer and generate a closed, reviewable
Viral evidence root from immutable reconstruction v4, source PDF geometry and
the committed user-review registry. Do not author `publication_config_v2.json`
yet.

Owned paths:

- `kb_creator/scripts/propose_scenario_semantic_units.py`
- `kb_creator/tests/test_propose_scenario_semantic_units.py`
- `kb_creator/working/viral/master_en/review_evidence/20260902_user_review_remediation_v1/`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_user_review_remediation_semantic_audit_20260903.md`

You are not alone in the worktree. Preserve all other edits and protected roots.

## Authoritative inputs

- committed `USER_REVIEW_TYPICAL_PROBLEMS_20260902.md`;
- architecture receipt and its candidate-first audit section;
- immutable reconstruction v4 and source PDF;
- current comparison/geometry sidecars and overlay evidence where present;
- completed v2 schema/tests as read-only contract.

## Required proposer/evidence

- Deterministically read accepted page Markdown, page/block coordinates and
  available semantic evidence. Candidate signals may include repeated labels,
  local baseline gaps, inset margins/background continuity, heading metadata,
  table geometry and page-pair/full-page coverage; repetition alone is not a
  decision.
- Write only an explicitly absent evidence root. Never mutate source,
  reconstruction, config or candidate.
- Produce canonical:
  - `semantic_unit_candidates.json` with stable ids, page/bbox/polygon, owner,
    template/family, ordered child source refs, order keys and evidence signals;
  - `semantic_unit_review.json` with closed `confirm`/`reject`/adjusted-boundary
    decisions, reviewer/user-registry provenance and source/config identities;
  - `semantic_unit_review.html` with compact source crops/context before/after,
    family filters and decision/status display;
  - `closure_report.json` mapping every blocking OUT/PROC fixture/family to
    reviewed candidates and reporting zero unresolved blocking candidates.
- Close at minimum: character quick references, appearance variants, Keeper's
  Notes, all nine Sight panels, Stream Schedule, hospital group/run-in rooms,
  p55 equipment card, p68 advice, all five table families, both creature
  statblocks, p106/p107 map unit and all six pregen page pairs.
- Preserve OUT-008 composite and typography ENH-001 as explicit nonblocking
  deferred records, not unresolved blockers.
- Include analogous instances found beyond the examples and reject false
  positives explicitly. Pages 123--124 appear only as excluded audit evidence.

## Tests/evidence

Add deterministic synthetic proposer tests for absent-root safety, geometry +
repetition ranking, adjusted boundaries, family coverage, false-positive reject,
excluded pages, immutable identities, zero-unresolved closure and repeat-build
equality. Run proposer tests, `py_compile`, canonical JSON/HTML link checks and
hash checks proving v1/reconstruction/source immutability.

Write the exact receipt with counts by family/decision, unresolved count,
artifact identities and tests. Return the token only with complete closed
evidence. No builder/verifier/visual-QA/config/candidate/Git/Step 8A changes.

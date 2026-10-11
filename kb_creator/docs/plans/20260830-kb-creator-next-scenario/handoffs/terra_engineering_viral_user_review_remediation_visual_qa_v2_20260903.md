# Viral remediation Slice 4 v2 visual-QA bundle receipt

- Goal: `20260830-kb-creator-next-scenario`
- Step: `7-user-review-remediation-visual-qa-v2`
- Contributor role: `nri-engineer`
- Requested model / effort: repository profile `gpt-5.6-terra` / `medium`
- Actual platform model / effort: unavailable
- Orchestrator policy owner: `gpt-5.6-sol` / `medium`
- Assignment state: `blocked_by_missing_v2_visual_qa_contract_inputs`
- Scoped override: `none`
- Timestamp: `2026-09-03T01:20:08+03:00`
- Elapsed time: approximately `00:04:00`
- Token use: unavailable

## Scope and inspection result

No production script or test path was changed. The existing visual-QA builder
is strictly v1-bound: it requires fixed Viral cardinalities `129/123/107/91/39`,
requires p124 as a back cover, and consumes v1-only asset/review structures.

The current closed v2 contract does not provide the minimum authoritative
inputs required for a strict Slice 4 route:

1. no per-page `publication_disposition` rows (only audit/reader page lists and
   aggregate metrics), so a QA generator cannot distinguish or report
   `excluded_advertising` pages as skipped audit rows without inventing policy;
2. no visual-review/contact-sheet declaration or semantic-row coverage contract,
   so dynamic source/reader review counts cannot be derived fail-closed;
3. no verifier-passed candidate binding artifact. `verify_v2_candidate` returns
   a process result but writes no candidate-bound verifier identity/receipt for
   the QA generator to validate.

Implementing the requested v2 route from the available fields would either
infer missing policy, reintroduce hard-coded assumptions, or falsely claim a
verifier-passed binding. All violate this packet's strict requirements.

## Evidence

- Inspected current v2 builder/verifier contract and visual-QA script/test
  surfaces with targeted searches for `publication_disposition`,
  `excluded_advertising`, `verified_v2_candidate`, and visual-review fields.
- The searches found only v1 `source_disposition` / `visual_review_units` and
  aggregate v2 `reader_pages` metrics; no v2 per-page disposition, review
  declaration, or verifier sidecar/binding exists.

## Next action

The orchestrator should assign a contract-authoring/architecture decision that
adds the three missing v2 inputs (or explicitly scopes Slice 4 to a weaker
artifact). After that decision, rerun a fresh Slice 4 implementation task.

Completion token: `BLOCKED_V2_VISUAL_QA_CONTRACT_INPUTS`

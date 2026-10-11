# Viral v2 verifier mutation classes 1--4 retry receipt

- Goal: `20260830-kb-creator-next-scenario`
- Step: `7-user-review-remediation-v2-verifier-mutations-1-4-retry`
- Contributor role: `nri-engineer`
- Requested model / effort: repository profile `gpt-5.6-terra` / `medium`
- Actual platform model / effort: unavailable
- Orchestrator policy owner: `gpt-5.6-sol` / `medium`
- Assignment state: `blocked_by_frozen_verifier_inline_run_in_admission`
- Scoped override: `none`
- Timestamp: `2026-09-03T01:07:44+03:00`
- Elapsed time: approximately `00:12:00`
- Token use: unavailable

## Scope and result

Changed only the assigned verifier test module and this immutable receipt.
Added fresh representative, independently resealed mutation coverage for:

1. inventory missing row, extra row, wrong byte count, and wrong SHA-256;
2. provenance event-list order and actual byte-range drift;
3. table header/row/cell-shape drift and callout-container boundary drift;
4. full reader-title drift and anchor-only outline pollution.

Each mutation reaches its intended v2 verifier gate after the candidate is
resealed, rather than failing only the outer inventory check.

## Verification and evidence

- `python -B -m pytest -q kb_creator/tests/test_verify_scenario_master_en.py`
  — `16 passed` in `19.27s`.
- Real frozen v1 preflight — pass:
  `scenario_id=viral`, config SHA-256
  `C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30`.
- Scoped `git diff --check` — pass (no output).

## Concrete blocker

The remaining required `inline_run_in` outline-pollution mutation cannot be
closed under this test-only assignment. A valid representative v2 config with
`hierarchy.representation: inline_run_in` and a matching
`structured_unit.content.kind: inline_run_in` is rejected by the frozen
`verify_v2_document` container whitelist with:

`E_V2_STRUCTURE: container`

This happens before the verifier's later `v2_hierarchy_slices` run-in gate can
inspect the candidate. The correction belongs in the verifier path, which is
explicitly forbidden by this assignment. No builder, verifier, config, real
candidate, Git, or Step 8A file was changed.

## Next action

Assign the verifier owner a narrowly scoped admission correction adding
`inline_run_in` to the independent structured-kind validation, then rerun this
representative mutation and issue a new receipt. Until that occurs, do not
return `READY_FOR_V2_VERIFIER_MUTATIONS_5_8`.

Completion token: `BLOCKED_INLINE_RUN_IN_ADMISSION`

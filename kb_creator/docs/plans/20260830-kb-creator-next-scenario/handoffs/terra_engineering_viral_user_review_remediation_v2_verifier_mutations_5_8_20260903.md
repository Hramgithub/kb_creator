# Viral v2 verifier mutation classes 5--8 receipt

- Goal: `20260830-kb-creator-next-scenario`
- Step: `7-user-review-remediation-v2-verifier-mutations-5-8`
- Contributor role: `nri-engineer`
- Requested model / effort: repository profile `gpt-5.6-terra` / `medium`
- Actual platform model / effort: unavailable
- Orchestrator policy owner: `gpt-5.6-sol` / `medium`
- Assignment state: `blocked_by_missing_v2_verifier_semantic_gates`
- Scoped override: `none`
- Timestamp: `2026-09-03T01:14:47+03:00`
- Elapsed time: approximately `00:12:00`
- Token use: unavailable

## Scope and completed mutation evidence

Changed only the assigned verifier test module and this immutable receipt.
Fresh representative candidates plus independent resealing now prove the
following implemented gates:

- Class 5: before/after/inside placement declaration drift and copied-reader
  asset byte/SHA drift each reject with `E_V2_ASSET`.
- Class 6: excessive ordinary blank runs reject with `E_V2_EOL`.
- Class 7: page-123 text leakage rejects with `E_V2_SCOPE`; excluded-page
  event and asset declarations reject with `E_V2_ORDER` and `E_V2_ASSET`.
- Class 8: missing ledger event or changed declared-content/range identity
  rejects with `E_V2_PROVENANCE`.

## Verification and evidence

- `python -B -m pytest -q kb_creator/tests/test_verify_scenario_master_en.py`
  — `16 passed` in `19.36s`.
- Real frozen v1 preflight — pass: `scenario_id=viral`, config SHA-256
  `C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30`.
- Scoped `git diff --check` — pass (no output).

## Exact missing semantic gates

The required four classes cannot all close under this test-only assignment:

1. **Raw CR/CRCRLF detection is absent.** `verify_v2_candidate` reads
   `MASTER_EN.md` using `Path.read_text()`, which normalizes CRLF and CR to LF
   before `verify_v2_document` checks for `\r`. A resealed CR/CRCRLF candidate
   is therefore accepted.
2. **Literal/fenced-content blank preservation is absent.** The verifier's
   global `\n\n\n` rule rejects a literal fenced block containing a legitimate
   blank run; no literal-aware parser branch exists.
3. **V2 excluded-page xref leakage is unrepresentable.** The closed v2 config
   has no `xrefs` declaration surface, so no independent verifier rule can
   bind an xref to pages 123--124.
4. **Recovery/navigation provenance operations are unchecked.**
   `verify_v2_candidate` validates the ledger but does not require
   `source_backed_recovery` or
   `generated_navigation_replaces_source_toc` in provenance `operations`.

These are verifier implementation gaps, not test-fixture failures. No builder,
verifier, config, real candidate, Git, or Step 8A path was edited.

## Next action

Assign the verifier owner a narrow implementation pass for raw-byte EOL input,
literal-aware blank validation, closed v2 xref declarations/excluded-page
binding, and mandatory recovery/navigation provenance operations. Then rerun
the missing class-6/7/8 mutations. Do not return `READY_FOR_VIRAL_V2_POLICY`
until those gates exist and pass.

Completion token: `BLOCKED_V2_VERIFIER_RAW_EOL_LITERAL_XREF_OPERATION_GATES`

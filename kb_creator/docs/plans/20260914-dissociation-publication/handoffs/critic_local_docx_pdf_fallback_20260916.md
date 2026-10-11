# Independent critic receipt: local DOCX-to-PDF fallback

Date: 2026-09-16
Role: independent critic (`gpt-5.5`, medium-equivalent review stance)
Decision: GO
Reviewed engineer receipt SHA-256: `FBCB1B06A826AC55E1FBAA7D9D019FBD274DD10D52DFB2CE945ACFF1A1FCD9D2`

## Scope

Focused re-review after P1 remediation for the Windows deep-path LibreOffice timeout exposed by real run `20260916-publication-21`.

Reviewed only the remediation delta in:

- `kb_creator/scripts/export_docx_to_pdf_local.py`
- `kb_creator/tests/test_local_docx_pdf_export.py`
- `kb_creator/docs/plans/20260914-dissociation-publication/handoffs/engineer_local_docx_pdf_fallback_20260916.md`

I did not edit implementation, config, live outputs, or `.codex` files. I did not run broad suites.

Existing evidence accepted for this re-review:

- original focused exporter/contract/authoring suite: `67 passed, 1 skipped`
- original publication control plane: `33 passed`
- original Stage 50/60 DOCX adapter suite: `3 passed`
- original publication registry E2E: `10 passed`
- independent root retest: `45 passed`
- remediation exporter plus Stage 50 transient cleanup suite: `6 passed`
- real run-21 quarantined DOCX smoke at a 181-character input/output stage path completed in 17.5 seconds
- smoke output: 799,104 bytes, SHA-256 `720A2B78AF841AFCA78BF0867F9D95A972EB1574291F6C5B9222E1A06AE05586`
- runtime workspace child count after export: zero

## Findings

### P0

None.

### P1

None. The path-length P1 is remediated.

### P2

1. Exporter negative tests still do not cover every fail-closed branch directly.

   The remediation adds meaningful regression coverage for a deliberately deep stage path, two consecutive collision-free runtime workspaces, complete runtime cleanup, and reparse-ancestor rejection. Remaining useful direct negatives include final-without-evidence/transient-with-evidence rejection, existing output rejection, suffix/path escape rejection, and malformed or drifted final evidence validation. This is not blocking because the pipeline and verifier still validate Stage 50 no-PDF residue, Stage 60 exact accepted-DOCX lineage, and final export evidence before package acceptance.

## Review Notes

- The local LibreOffice workspace now uses `tempfile.mkdtemp(prefix="lo-", dir=.tools/runtime/kb_creator/docx_pdf)` instead of being created beside the deep Stage 50 private bridge path.
- `_runtime_root()` keeps the runtime root under resolved repository `.tools`, checks existing ancestors for reparse content before creation, rejects a reparse `.tools`, and verifies that the final runtime root resolves to the expected regular directory.
- Each conversion still passes the original accepted/candidate DOCX path directly to LibreOffice; only the private LibreOffice profile and conversion output directory moved to the short runtime root. Accepted-DOCX lineage and evidence identity are unchanged.
- The conversion still atomically moves exactly the generated PDF back to the requested stage-root PDF path and removes the unique runtime workspace before success.
- The Stage 50 and Stage 60 control-plane constraints from the prior review remain intact: Stage 50 cannot retain or expose PDF bridge authority, and Stage 60 still requires `document_authority_kind = accepted_docx`, `adapter = docx_pdf_export_v1`, `fresh_export = true`, and exactly one final PDF.
- No HTML/browser PDF path was introduced by the remediation.
- Dissociation `configs/docx.json` remains bound with `footer.page_numbers = false`.

## Decision

GO for the local LibreOffice DOCX-to-PDF fallback after the deep-path remediation.

Final acceptance remains subject to the normal release process and a fresh publication run because the implementation inventory and contract identity changed.

# Viral v2 raw-EOL, xref and provenance-operation closure

- Goal: `20260830-kb-creator-next-scenario`
- Step: `7-user-review-remediation-v2-eol-xref-operations`
- Owner: current `nri-engineer`, `gpt-5.6-terra` / `medium`
- Blocker receipt: `terra_engineering_viral_user_review_remediation_v2_verifier_mutations_5_8_20260903.md`
- Completion token: `READY_TO_CLOSE_V2_VERIFIER_MUTATIONS_5_8`

## Objective and exclusive ownership

Close the four exact remaining v2 contract/verifier gaps: raw EOL inspection,
literal-aware blank runs, explicit xrefs, and bound navigation/recovery
operations. This is a coordinated builder+verifier contract change; v1 remains
strict and unchanged.

Owned paths:

- `kb_creator/scripts/build_scenario_master_en.py`
- `kb_creator/tests/test_build_scenario_master_en.py`
- `kb_creator/scripts/verify_scenario_master_en.py`
- `kb_creator/tests/test_verify_scenario_master_en.py`
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/terra_engineering_viral_user_review_remediation_v2_eol_xref_operations_20260903.md`

You are not alone in the worktree. Preserve all other edits.

## Required contract and gates

### Raw EOL and literal-aware blanks

- Candidate verifier reads `MASTER_EN.md` bytes, rejects BOM/invalid UTF-8,
  lone CR, CRLF and CRCRLF before any text newline normalization.
- It requires one terminal LF.
- Reject three-or-more ordinary consecutive LF outside fenced literal blocks.
  Preserve and allow such runs inside closed backtick or tilde fences. Reject an
  unclosed fence. Do not globally rewrite candidate bytes.

### Closed xref declaration

Add required v2 top-level `xrefs` list. Each exact row contains:

- `xref_id`, `source_event_id`, `source_page`, `target_anchor`, `reader_text`.

Require unique ids, existing reader-scope source event on the same page,
existing target anchor, nonempty reader text, and exact Markdown link
`[reader_text](#target_anchor)` inside the emitted source-event ledger slice.
Reject source/target leakage through excluded pages 123--124. Empty list is
valid for generic fixtures but the real Viral policy may declare many rows.

### Closed source recovery and operation provenance

Add required v2 top-level `source_recoveries` list. Each exact row contains:

- `recovery_id`, `event_id`, `source_page`, `source_text`, `operation` with
  value `source_backed_recovery`.

Require unique ids, reader-scope event/page identity and exact recovered text in
the event's final ledger slice. Empty list is valid generically.

Candidate provenance `operations` becomes a deterministic closed list of
objects: exactly one generated-navigation operation bound to the document's
declared navigation source identity, plus exactly one bound operation for every
source recovery. Reject missing, duplicate, extra, reordered or mismatched
operations. Do not emit per-event `retained` noise.

### Tests

Update synthetic fixtures and add builder/verifier positives and mutations for:
raw CR, CRLF, CRCRLF; ordinary vs fenced blank runs; unclosed fence; valid xref,
excluded source-page xref, missing target/link; valid recovery; missing/
duplicated/extra/mismatched navigation and recovery operations. Retain all
existing v1 and v2 tests and verifier independence.

Run both full test modules, both `py_compile`, real v1 builder/verifier
preflights, static no-builder-import and scoped diff check. Write the exact
receipt and return the token only when all four gaps close.

No real config/evidence/source/reconstruction/candidate/Git/Step 8A changes.

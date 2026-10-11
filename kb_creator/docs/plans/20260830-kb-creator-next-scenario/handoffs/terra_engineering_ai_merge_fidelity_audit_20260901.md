# Terra engineering receipt — generic AI merge fidelity auditor

## Scope and result

Implemented a small stdlib-only, generic fidelity auditor for AI merge
decisions versus their packet-selected source blocks.  It does not invoke
MinerU, inspect PDFs, or modify candidates.  It accepts decisions root,
merge-packets root, optional closed reviewed allowlist, optional JSON output,
and an optional recall threshold (default `0.95`).  CLI exits nonzero on audit
failure while retaining a requested JSON report.

## Changed files

- `kb_creator/scripts/audit_mineru_ai_merge_fidelity.py`
  - SHA-256: `E5BDE87435D19EAD63FB4D5BAC2CCE1E4FE139B00B97FA6110CF5880EA5D0A08`
  - Bytes: `10560`
- `kb_creator/tests/test_audit_mineru_ai_merge_fidelity.py`
  - SHA-256: `4F0F528EF0D3DB8D263E658A0D31325ABCC939AC231388360BDA814C372CCA93`
  - Bytes: `4980`

## Behaviour and evidence

- Resolves exact `{view, raw_index}` references from merge packets; malformed,
  missing, duplicate, unknown, or page-domain-drifting data raises a concise
  deterministic error.
- Unicode/casefold tokenizes selected non-image/non-page-number text and
  decision Markdown, excluding Markdown image links and asset placeholders.
- Uses `difflib.SequenceMatcher(..., autojunk=False)` on tokens.  Only an
  equal-count local replace span of at most 25 words is aligned; inserted
  headings/table labels therefore cannot shift the following body into false
  substitutions.  Within each same-length paired word it reports the 1..3
  differing characters (for example `will`→`wiee` yields `ll`→`ee`).
- Reports every page's token counts, multiset recall/precision, aligned word
  pairs, and aggregate character substitutions. Recall fails only at selected token count
  `>=20`; visual/low-text pages are still reported.
- Repeated one-to-three-character substitutions at count `>=3` fail unless an
  exact page-scoped closed allowlist row has matching `from`, `to`, exact
  `max_count`, and nonempty evidence.  Unused or overbroad rows fail.
- No scenario names or project-specific token mappings are embedded.

Verification, all exit code 0:

```powershell
python -B -m py_compile kb_creator/scripts/audit_mineru_ai_merge_fidelity.py kb_creator/tests/test_audit_mineru_ai_merge_fidelity.py
python -B -m pytest kb_creator/tests/test_audit_mineru_ai_merge_fidelity.py -q
# 11 passed in 0.08s
git diff --check -- kb_creator/scripts/audit_mineru_ai_merge_fidelity.py kb_creator/tests/test_audit_mineru_ai_merge_fidelity.py
```

Focused tests prove realistic within-word l→e mass drift failure, h→a repeated-substitution failure
despite recall `>=0.95`, exact reviewed normalization pass and overbroad failure,
missing facts recall failure, image/low-text reporting, malformed refs/schema/
allowlist failure, heading/table-label insertion without a false cascade,
deterministic UTF-8/LF report output, and generic naming.

## Focused remediation and read-only v3 audit

The initial positional zip was replaced because it could pair unrelated words
after a Markdown insertion and missed corruption inside longer words.  The
required frozen-v3 read-only audit ran against
`20260901_step6a_ai_merge_decisions_v3/pages` and the postprocess
`merge_packets` root, writing only a temporary report under `%TEMP%`. Its
expected nonzero status means the following quality failures were found:

- page 20: recall `0.813161`; `l`→`e` count `117`; `ll`→`ee` count `42`;
- page 44: `h`→`a` count `12` despite recall above the threshold;
- page 62: `ý`→`ÿ` count `7`.

No former zipper-cascade findings on pages such as 21 or 36 occurred.  The
report contains all 124 pages, including passing visual/low-text pages.

## Limitations and next action

This detects systematic same-length token substitutions and material text loss;
it is not a semantic or visual review and does not judge deliberate paraphrase
unless it crosses the configured recall bound.  A bounded executor may run it
against frozen real decisions/packets and capture its JSON receipt.  This is not
a release decision.

## Administration

- Timestamp: 2026-09-01 Europe/Moscow
- Elapsed time: approximately 14 minutes
- Token use: unavailable
- Orchestrator policy owner: main `/root` Sol/orchestrator
- Assignment state: completed, receipt captured
- Scoped override: none

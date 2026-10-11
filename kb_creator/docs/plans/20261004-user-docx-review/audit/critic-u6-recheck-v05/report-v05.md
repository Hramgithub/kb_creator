# Frozen U6 API independent implementation recheck v05

Recommendation: **approve within assigned implementation scope**. No remaining
finding or blocker was reproduced in the finite U6 recheck. This is not a
full-goal release review. I did not implement or materially design the change.
Main `/root` retains orchestration and acceptance ownership.

## Finding dispositions and evidence

| Finding | Disposition | Independent evidence |
| --- | --- | --- |
| F1 P1 numeric relabelling | CLOSED | Resealed numeric relabel rejects; approved EDU/CHR cases pass, unapproved/collateral changes reject. |
| F2 P2 inherited visibility | CLOSED | Paragraph/inherited-style hidden targets reject. |
| F3 P2 expression gaps | CLOSED | First-tail, last-prefix, middle-gap, hyperlink and break cases reject; exterior prose preserved in valid expression. |
| F4 P1 authority drift | CLOSED | Early manifest and later other-authority mutation reject before publication. |
| F5 QA metadata | CLOSED | Previously consumed immutable v05/v06 errata remain valid; current hash checks agree. |
| F6 P1 partial visible operand | CLOSED | Former within-leaf and cross-run failures reject; independent adjacent inline boundary cases agree with expectations. |

The new implementation at `pipeline/reviewed_docx_revision.py:474`–519 maps the
selected operand into supported visible paragraph inline content, rather than
testing only its own text leaf. The caller at653–657 applies it to typed
characteristic operations. No paragraph flattening or book mutation occurred.

Independent finite results, all under this audit root:

- `numeric-v05.json`: all six prior exact numeric cases recreated/resealed.
  Same-leaf suffix/prefix and adjacent-run suffix/prefix reject. Complete13→65
  and delimiter neighbor `; Удача: 75` accept with exact preserved surroundings.
  This closes the former13→115/53 failures.
- `inline-v05.json`: eleven further cases based on the frozen v04 numeric
  fixture. Same-run multiple leaves in both directions, hyperlink digit
  neighbors in both directions, bookmark/comment/proofing zero-width markers
  reject partial operands. Tab and line-break delimiters accept. A hidden
  neighbor contributes no visible digit and the selected visible operand
  accepts. Unsupported content control rejects through existing topology
  guard. Exact resealed XML/ledger inputs are in `inline-inputs/<case>/`.
- `probes-v05.json`: unchanged baseline passes; nine previous invalid cases
  reject. `boundaries-v05.json`: all six EDU/CHR controls agree.
  `drift-v05.json`: both drift cases reject with no candidate output.
  `exterior-v05.json`: valid result is `Каждый раунд: 5 × (1D6) СИЛ; конец.`.
- `tests-elevated-v05.json`:23/23 focused tests pass, zero failures/errors,
  runtime1.444s. First sandbox attempt had27 fixture write/cleanup access
  errors, zero assertion failures (`tests-v05.json`); permitted elevated retry
  of the same bounded harness passed. Audit-local remnants are outside commit
  scope. No cleanup of unrelated paths occurred.

Reproduce a mode using a fresh one-component output subdirectory each time:

```powershell
$env:PYTHONPATH='D:/NRI'
& 'C:/Users/BogdanD/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B -X utf8 'D:/NRI/kb_creator/docs/plans/20261004-user-docx-review/audit/critic-u6-recheck-v05/recheck_v05.py' inline inline.json repro-01
```

Modes: `inline`, `numeric`, `probes`, `exterior`, `boundaries`, `drift`, `tests`,
`evidence`. Old critic modules and fixtures are imported/read only; their output
roots are rebound in memory to this assignment. Older files remain immutable.

## Actual candidates and existing QA

`evidence-v05.json` freshly verifies all three real preflights, original/source/
authority identities,146 numeric source-QA bindings,197 operations plus the
separate expression, exact restored canonical document XML and preservation
of old media/comments/other package content. Current API read-only plans pass:
Fear0, Leningrad145, Kremlin6 field nodes. Candidate bytes are unchanged:

| Candidate under working/user-review-20261004 | SHA-256 |
| --- | --- |
| fear-reader-v01/document.docx | D79AB0EC131D2C6926D868EB037786093F615AEAF122895AA4487254616CF33E |
| leningrad-reader-v01/document.docx | CC3A1F96D82121C07938D860EF88186AA33A32199B578D4C7C2DE05F4C83AD23 |
| kremlin-reader-v01/document.docx | 5573888152F7EDAB32D483E4D652FD465694BFBF1764CC708C3EF7C042AA87D8 |

All367 PNGs were freshly rehashed against bound QA/index evidence:279 Fear,
64 Leningrad,24 Kremlin. Previously consumed visual-QA receipts record individual
page inspection without actionable findings; this critic did not personally
repeat those367 views. Fear metadata correction v05 and attribution clarification
v06 remain applicable, without rewriting historical receipts. Correct Fear
review-index hash686FE24C9C5D398B0472A56689AC9946A570CA7EADF22D30FC86DC594C540430
and inventory hashF762E478AEDA0C7F4AB9A3BE768F82C70EFBBBC9346F813122C8F75428132418
were freshly matched. No retroactive claim that v05 authored the historical
DOCX bytes is made. F6 was never demonstrated in these actual candidates.

## Code freeze and limits

Start2026-10-04T22:12:55Z; final code identity check22:13:51.5441260Z.
All seven hashes match at start/end:

| Path under kb_creator | SHA-256 |
| --- | --- |
| pipeline/reviewed_docx_revision.py | ECF14988614230151542B5EFE358A1FF1A8554A7B6718BCF00AFBE7AADBB5A90 |
| scripts/revise_reviewed_docx.py | 297DF8A246C5CA20CEA00E299C7EEC7FA2B255C449E18E1473112E8188E940F3 |
| pipeline/reviewed_reader_revision.py | 7292AA673919AF66D9287BA20B9E33191444E7906E7326635F8860D1569F90A3 |
| pipeline/docx_review_comments.py | 0A4F8FF79886E4A9054910AA5E3BFACD7C093F69ECF3B2317C7FF269E2E3919B |
| tests/test_reviewed_docx_revision.py | 7E7DB7488794F32696B2FE971305FBC12D378FAA686EA73EE83AE8F84BEA3D38 |
| tests/test_source_bound_word_fields.py | 072FC2DB271351AD5007CA031BB79FCEE91E83E729EFD8E056E742AA897EEB01 |
| docs/reviewed-docx-revision.md | 8744AFC8392240B095EA9E9842976E77DD63F66D69C6C0A4920F9ADE6EFCD9BC |

Approval is limited to this frozen reusable API and assigned finite boundaries.
Unsupported split conversions may fail closed. It does not imply universal
Word topology support. Main's field-only art-preservation choice remains
bounded: original Leningrad/Kremlin art conserved, source-art completeness not
certified. Preserved Resistance, MP/HP and unknown POW exceptions remain a
limited7e adaptation, not a full rules reconstruction.

Normal U8 code is changing and excluded. Its guard/output policy and final
full-goal release require separate frozen evidence/review. Any relevant code,
dependency or candidate mutation invalidates this receipt for the new revision.

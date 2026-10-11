# Independent repaired release recheck evidence v02

Review kind: release. Evidence checkpoint only; final recommendation is withheld
until completed U8 QA v05 is consumed in the immutable handoff. I did not
implement or materially design the candidate. Main `/root` retains orchestration.

## Scope and freeze

Canonical freeze:2026-10-04 23:14UTC. U8 v04 implementation manifest:
`audit/fidelity-engineering/U8-v04-implementation-hashes.json`, SHA-256
`9A948C1264D64A48E551221E5604FC6435F2641A9B50AAEE13079C5F657C8BEC`.
Independent actual-byte start/checkpoint checks match all43 size/hash pairs,
zero mismatches (`freeze-v02.json`, `freeze-checkpoint-v02.json`). Both also bind
the three actual candidate DOCX and unchanged U6 repair API.

Engineering evidence consumed: immutable U8-fidelity-engineer-v04 receipt,
detailed U8-fidelity-engineering-v04 report and U8-v04-final-regression.log.
These report239 tests+14 subtests,1 unrelated Word COM skip; independent QA
consumption remains the final handoff prerequisite, not inferred from that log.

## Finite R1–R4 recheck

All probes use current `reader_fidelity_plan.v2` with genuine format-valid
source inventory/review, policy.book_id, reviewed edition occurrence domain,
canonical-header CSV and explicit closed JSON book overlay. Negatives are
honestly resealed. No closure relies on rejecting obsolete v1 schemas.

| Finding | Behavioral recheck | Evidence |
| --- | --- | --- |
| R1 operand/field | WholeSTR13→65 and styled label pass through projection and reopened Word. Partial suffix/prefix, protected Luck misbinding and collateral exterior mutation reject at plan validation; operand spanning styled fragments rejects at projection. Changed final Word value rejects. | edition-retry-v02/results-v02.json |
| R2 source/occurrence domain | Valid reviewed occurrence passes. Foreign physical page/story/book/entity/occurrence, stale source-render binding and missing domain reject. Reopened Word operand moved outside its declared story rejects. | edition-retry-v02/results-v02.json |
| R3 mapping authority | Accepted CSV row and explicit book-overlay mapping pass projection/reopened Word. Empty/unaccepted authority, invented target, incorrect reference/context reject. Free-form primary/editorial dispositions return typed unsupported_authority/needs_decision. | terms-retry-v02/results-v02.json |
| R4 exact drawing order | Valid separate paragraph and both same-paragraph before/after directions pass. Inverted same-paragraph order rejects both ways. Resealed observation tampering and semantic promotion to approved reject during independent report reopening. | graphics-retry-v02/results-v02.json |

This is38 finite diagnostic cases:16 edition/domain,9 terminology,7 graphic/
offline,6 public-builder. Nine expected accepts and29 expected rejects agree.
Exact source/plan/registry/overlay/Word/report fixtures live under each named
case directory. Old critic fixtures/results were never rewritten.

Public-builder evidence (`public-v02/results-v02.json`): a rendered-source
visible graphic already in the master builds and reopens; a reviewed source
graphic absent before the master is inserted into the reader DOCX, while master
bytes stay unchanged. Both return `verified_pending_visual_review`; no semantic
approval is inferred. Partial operand, foreign page, invented mapping and None
plan all reject before output root creation. The synthetic upstream language
fixture uses its documented test-only language-verifier patch; actual source
inventory rendering, current plan guard, normal builder and offline package
verifier run unpatched. This is not a real-book reconstruction-lineage claim.

Reproduction from D:/NRI, fresh one-component child name each time:

```powershell
$env:PYTHONPATH='D:/NRI'
& 'C:/Users/BogdanD/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B -X utf8 'D:/NRI/kb_creator/docs/plans/20261004-user-docx-review/audit/release-critic-v02/recheck_v02.py' edition results.json edition-repro-03
```

Other modes:terms,graphics,public,books,freeze. Bundled Python appends the existing
local pure pytest library path, without installing packages or switching the
interpreter. The normal synthetic source-render attempt hit confirmed Access
Denied in its new audit stage; same bounded probes passed on the approved
elevated retry. Failed stage remnants remain audit-local, outside commit scope.
Synthetic PDF inputs are not published PDF outputs; no HTML deliverable produced.

## Actual repaired books and inherited evidence

`books-v02/results-v02.json` freshly reuses the prior independent checker
read-only: all three actual original/manifest/authority preflights pass;
146 numeric source-QA records agree,197 operations plus separate expression
remain bound, and reversing declared edits restores exact canonical original
Word XML while original media/comments/other package content are conserved.

Freshly rehashed279 Fear+64 Leningrad+24 Kremlin PNGs=367 match their bound
indexes/QA ledgers. Completed visual-QA receipts previously inspected every page;
this critic does not claim personally repeating367 page views. Fear v05/v06
immutable metadata corrections remain applicable and hash-label correction
was reverified.26 Fear opening coverage comprises23 restored and3 retained.

Current candidates under working/user-review-20261004:

| Candidate | SHA-256 |
| --- | --- |
| fear-reader-v01/document.docx | D79AB0EC131D2C6926D868EB037786093F615AEAF122895AA4487254616CF33E |
| leningrad-reader-v01/document.docx | CC3A1F96D82121C07938D860EF88186AA33A32199B578D4C7C2DE05F4C83AD23 |
| kremlin-reader-v01/document.docx | 5573888152F7EDAB32D483E4D652FD465694BFBF1764CC708C3EF7C042AA87D8 |

Unchanged repaired-artifact API SHA:
`ECF14988614230151542B5EFE358A1FF1A8554A7B6718BCF00AFBE7AADBB5A90`.
Prior U6-api-critic-v05 scoped approval remains separate. Current books were
not replayed through normalv3; new code does not retroactively author them.

## Limits and remaining handoff prerequisite

Names/numbers adaptation remains limited, not full7e mechanics reconstruction;
Resistance/MP/HP/unknown POW and missing Number7 source exceptions stay explicit.
Leningrad/Kremlin original art conserved, full source-art completeness not
assessed; main owns the field-only implementation boundary. Exact source-page
and output-render human review remain mandatory; automatic paint discovery is
incomplete and XML cannot certify visibility or semantic book approval.

No source, book, production code/test/schema, old receipt or canonical state
edited. New artifacts only in this audit root. Final QA v05 must supply its
completed regression and preservation checks before the final release handoff.
Any relevant code/dependency/authority/candidate mutation invalidates the
applicable freeze and requires a new review. No final recommendation here.

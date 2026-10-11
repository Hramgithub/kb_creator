# Number 7 Dream publication working cleanup

Execution status (2026-09-19): complete. The four previously local commits
through `97971895` were pushed to `origin/main` without force; the remote SHA
was confirmed. The exact 29 historical publication runs listed below were
moved to the Windows Recycle Bin and each was confirmed there. No permanent
deletion was used. Run30, reconstruction, translation and the tracked package
remain in place. The KB Creator-wide pipeline-change report is
`../../pipeline-change-report-20260919.md`; the local file is only a pointer.

## Objective and authority

Prepare a loss-aware cleanup of obsolete publication runs without deleting,
moving, rewriting, or pushing anything during this preparation step. The only
proposed deletion root is
`kb_creator/working/number-7-dream/publication/`; reconstruction, translation,
the tracked production package, and the current run30 are outside scope.
Before deletion, obtain separate approval for the exact list below.

Main-chat orchestration, state, integration and stop/ask decisions belong to
the repository-policy `gpt-5.6-sol` medium role (actual platform model is not
asserted). Engineering `gpt-5.6-terra` medium, architecture `gpt-5.6-sol` high,
independent criticism `gpt-5.5` medium, bounded execution `gpt-5.6-luna`
medium, and bounded QA `gpt-5.6-luna` low remain available if execution or
review becomes broad. No subagent was needed for this bounded read-only
inventory. An independent release decision has not been made.

## Pre-archive verified baseline (2026-09-19)

- Git `main` is clean and three local commits ahead of `origin/main`; the
  preservation commits are `a7542c85` and `bcaf7549`. Nothing was pushed.
- The tracked run30 package at `kb_creator/inputs/number-7-dream/production/`
  passes its copied offline verifier: manifest SHA-256
  `930965C745E0889B931CED46D738C94A0DCEB393F38F20CD913CFF42BC60B2C8`,
  20 local HTML references, one PDF, `candidate_for_release_review`,
  `release_state: not_reviewed`.
- Publication has exactly 30 run directories and no loose root files. The
  29 historical runs below contain 10,785 files / 1,192,809,155 bytes. Run30
  contains 700 files / 140,462,092 bytes and remains untouched. Recursive
  inventory found zero reparse points in any publication run.
- Reconstruction (55 run directories) and translation (one directory) are
  not deletion candidates. No cleanup has occurred.

## Exact historical publication targets (approval fulfilled)

All paths below are directories directly under
`kb_creator/working/number-7-dream/publication/`:

```text
20260918-publication-01
20260918-publication-02
20260918-publication-03
20260918-publication-04
20260918-publication-05
20260918-publication-06
20260918-publication-07
20260918-publication-08
20260918-publication-09
20260918-publication-10
20260918-publication-11
20260918-publication-12
20260918-publication-13
20260918-publication-14
20260918-publication-15
20260918-publication-16
20260918-publication-17
20260918-publication-18
20260918-publication-19
20260918-publication-20
20260918-publication-21
20260918-publication-22
20260918-publication-23
20260918-publication-24
20260918-publication-25
20260919-publication-26
20260919-publication-27
20260919-publication-28
20260919-publication-29
```

Never target the publication root, a range/glob, or run30 for deletion. At
execution time, resolve each literal absolute path and confirm it is a direct
child of that root, still has the planned name, is not a reparse point, and
has no changed inventory since the approval snapshot. Abort on any drift.

## Preservation gate before any removal

The final package is self-contained but does **not** contain the exact bytes
of five historical user-reviewed artifacts. Preserve them with original-path,
byte-count and SHA-256 provenance in a separate tracked history directory,
then verify and commit that history before deleting its source runs:

| Source run and relative path | Bytes | SHA-256 | Why retain |
| --- | ---: | --- | --- |
| `06/submissions/artview/artview-decisions.accepted.json` | 7,057 | `6A1326CABEE791FA321E0D2D2651CB1C7BAE9E716D90EB6D492EF54333649F24` | Original user export, 19 reviewed rows |
| `18/submissions/artview/artview-decisions.accepted.json` | 8,304 | `8504FE1DF206A25FA30B7EEAE90F0ED6FFFD6CF0F7A8408BE5146C19D86F07B0` | Original user export, 20 reviewed rows |
| `25/submissions/artview/artview-decisions.accepted.json` | 8,304 | `6EE7217A9B995EC3143A022ED6D6D3360CD19F3AB44C7A8169CE6222DA875BED` | New user export, 20 reviewed rows |
| `28/submissions/docx/Number_7_Dream_RU.reviewed.docx` | 5,349,133 | `C29A5569820A3D2734F28089619F1BC273E1013A8CD040439C3F58899CE9F5BE` | First user-edited DOCX revision; distinct from final |
| `29/outputs/60-pdf-candidate/artifacts/Number_7_Dream_RU.pdf` | 2,914,792 | `B39214DD4CCD084A0867697F883E7B08CEEBAD6EF3B66D5CC5EB04C41D399EBD` | User-accepted PDF; visually same as run30 but byte-distinct |

The run27 user-edited DOCX and run28 reviewed submission share the exact
first-revision hash above. The later edited DOCX (`16ED29E5...`) and accepted
run30 PDF (`9D9E617D...`) are already in the tracked package. Run25's accepted
HTML has the exact same hash in the tracked package. The three original
ArtView exports, first DOCX revision and run29 PDF have no exact hash match
among the 147 JSON/DOCX/PDF files currently under tracked
`inputs/number-7-dream/`.

The user authorized this preservation step. The five files above plus their
matching `acceptance/*.acceptance.json` receipts and run25's HTML acceptance
receipt have been copied to `inputs/number-7-dream/review-history/` without
changing source bytes: 11 files / 8,294,504 bytes. `MANIFEST.json` records all
11 original and archive paths, sizes and hashes. Every archive and source row
was rehashed and matched; the archive has inherited ACLs. The archive PDF and
DOCX use LFS, and `.gitignore` explicitly permits the archived PDF. Receipts
are historical provenance, not current run30 acceptance. The hash-frozen
run30 package has not changed.

## Approved execution order (completed)

1. Archive materialization and byte verification are complete; include only
   this archive, its Git attributes/exemption, and canonical plan/status/README
   in a local commit. No push without consent.
2. Re-run the tracked package's offline verifier and re-inventory the exact
   29 target directories. If any target changed, stop and revise the plan.
3. Ask for explicit approval to remove those exact 29 directories. Use one
   PowerShell session, literal validated paths, and a recoverable removal
   method where practical. Do not cross shells or use recursive globs.
4. Verify run30, reconstruction, translation, tracked package and Git status
   are unchanged; report removed file count, bytes and recoverability.
5. Only after cleanup, write the requested pipeline-change report from the
   committed code, tests and documented root-cause/fix receipts.

The archive was committed as `97971895`. The user then explicitly authorized
both a normal push of the local `main` commits and removal of the exact 29
listed runs to the Windows Recycle Bin. If Recycle Bin operation is unavailable,
stop without permanent deletion. No force push or extra deletion is authorized.

## Execution checkpoints

| ID | Owner | State | Evidence / gate |
| --- | --- | --- | --- |
| E1 | main orchestrator, `gpt-5.6-sol` medium policy | done | Exact 29 targets, no reparse points, 10,785 files / 1,192,809,155 bytes; package and archive verified |
| E2 | independent critic, `gpt-5.5` medium | done | Read-only deletion-scope and recoverability review in `handoffs/D1-cleanup-preflight-review.md`; no implementation or deletion |
| E3 | main orchestrator | done | Normal push including LFS succeeded; live `origin/main` SHA equals `97971895ff061b6ba4286db6e541055437c27496` |
| E4 | main orchestrator | done | Desktop-user Recycle Bin proven with disposable empty and nonempty probes; 29 exact directories moved and individually confirmed, with no permanent fallback |
| E5 | main orchestrator | done | Only run30 remains under publication: 700 files / 140,462,092 bytes; reconstruction 55 runs, translation one directory; production offline verifier and 11 archive hashes pass |
| E6 | main orchestrator | done | KB Creator-wide `../../pipeline-change-report-20260919.md` and canonical status included in the local documentation savepoint; no new push |

## Execution incident and recovery

Legacy runs had protected ACLs, so the existing byte-preserving access
normalizer was applied to exactly the 29 approved targets before desktop-user
recycling. An initial sandbox-identity recycle probe was not visible in the
desktop user's bin, so actual removal used only the desktop user identity after
separate empty and nonempty probes appeared in that bin.

Runs 01-23 moved normally. Run24 initially failed because a local HTTP server
on port 8767 held its ArtView directory open; servers on 8768-8769 served the
also-targeted run25. A temporary short-name move partially redistributed
run24 files. Before further removal, all 270 temporarily moved files were
returned to the original directory; the disjoint union was verified as the
original 411 files / 55,527,405 bytes, and the temporary directory had zero
files. Only the three identified historical-preview servers were stopped.
Run24 then recycled whole, followed by runs 25-29. The empty temporary
directory was also moved to the Recycle Bin. Final desktop-user bin inspection
found all 29 exact historical names once and none still on disk. The two
disposable probe folders remain recoverable in the bin as well.

The protected ACL subtree in untouched run30 was not normalized. Its inventory
was checked under the read-capable sandbox identity; the desktop user could
not recurse through that subtree. The tracked production package's independent
offline verifier returned its unchanged manifest SHA, 20 HTML references and
one PDF, with `release_state: not_reviewed`.

# Cleanup execution checkpoint

On 2026-09-19 the user approved a normal push of the four local commits
through `97971895` and Recycle Bin removal of the exact 29 historical
publication runs. The push completed and live `origin/main` was verified at
`97971895ff061b6ba4286db6e541055437c27496`. All 29 listed runs are now
visible in the desktop user's Windows Recycle Bin, with no permanent deletion
fallback. Only run30 remains under the publication root (700 files /
140,462,092 bytes). Reconstruction has 55 run directories; translation has
one. The final production offline verifier and all 11 archived history hashes
pass after cleanup. The KB Creator-wide change report is
`../../pipeline-change-report-20260919.md`. This documentation checkpoint is
included in the later local KB Creator documentation savepoint; no new push.

## Historical preparation evidence

The user asked to prepare cleanup after local preservation commits, then
explicitly approved archival of unique historical artifacts and their
acceptance receipts. The inventory covers only the Number 7 Dream publication
working tree. Nothing was deleted, moved, overwritten or pushed.

The proposed deletion set is exactly publication runs 01–29 (29 directories,
10,785 files, 1,192,809,155 bytes). Run30 (700 files, 140,462,092 bytes),
55 reconstruction runs, and one translation directory stay. No reparse point
was found in the publication runs. The tracked run30 package still has an
independent offline-verification result from the preservation turn.

Five historically accepted/user-authored artifact byte streams are absent
from the tracked final package: original ArtView exports from runs 06, 18 and
25; the first user-edited DOCX revision bound by run28; and the accepted but
byte-distinct run29 PDF. Their exact sources, sizes and SHA-256 values are in
`plan.md`. All five plus six acceptance receipts were copied unchanged to
`inputs/number-7-dream/review-history/`: 11 files, 8,294,504 bytes. Its
manifest's 11 source and archive hashes/sizes all match. The archive PDF and
DOCX are LFS-bound; the final production package remains untouched. This
archive is historical evidence, not independent release approval. Deletion
approval is still pending.

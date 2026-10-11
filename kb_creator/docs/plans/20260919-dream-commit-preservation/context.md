# Number 7 Dream commit preservation checkpoint

The user asked to prepare a commit preserving pipeline work and the book-build
artifact, then to clean the working folder and later report pipeline changes.
This checkpoint treats preparation, cleanup and reporting as ordered but
separate actions. The preparation was subsequently committed locally as
`a7542c85`; no push or deletion has been performed. The rest of this document
records the pre-commit verification state and proposed scope.

The frozen source package is the offline-verified run30
`kb_creator/working/number-7-dream/publication/20260919-publication-30/outputs/70-production-package/artifacts/package`.
Its manifest SHA-256 is
`930965C745E0889B931CED46D738C94A0DCEB393F38F20CD913CFF42BC60B2C8`;
it contains 212 files, 20 local reader assets and exactly one PDF. The copied
offline verifier reports `candidate_for_release_review` and
`release_state: not_reviewed`. The independent release decision remains
pending, so a commit must not be represented as release approval.

Repository `.gitignore` excludes `kb_creator/working/**` and most PDFs. The
prior Viral production package establishes a tracked, byte-frozen
`kb_creator/inputs/<scenario>/production/` precedent. The run30 package has
now been copied intact to `kb_creator/inputs/number-7-dream/production/`.
All 212 files and 52,335,837 bytes match the working source by SHA-256; the
copied offline verifier passes without modifying the package. Git attributes
disable text conversion inside this frozen tree, and its PDF uses LFS.

Independent process critic receipt is
`handoffs/P4-commit-scope-review.md`: no HIGH/MEDIUM findings. The LOW risk is
52.3 MB of Git history, including normal Git blobs for DOCX/PNG files. This
copy is still only a candidate, not a release. Regression tests and exact
Git staging scope is now fixed. No cleanup target has been chosen.

The proposed index has 479 files: 212 frozen package files and 267 reusable
pipeline, schema, test, documentation, governance and scenario-input files.
There are no staged `working/**`, browser profiles, raw transcripts, OCR
overlays, caches or log/temporary files. No unstaged or untracked changes
remain. The PDF is staged as a Git LFS pointer to its verified SHA-256;
the package itself is not text-normalized. Current branch is `main`, one
existing commit ahead of `origin/main`; no new commit or push occurred.

The copied package verifier was rerun after staging and passed with 20 local
HTML references, exactly one PDF and unchanged manifest SHA-256. Focused
code-path whitespace check passes. The full staged diff whitespace check
reports inherited blank EOF lines and semantic Markdown hard-break trailing
spaces, including within the hash-frozen package; these are not modified to
avoid changing reviewed package bytes.

Regression matrix: 580 passed, 2 failed, 3 skipped, 314 subtests passed.
Both failures are `test_reconstruction_promotion.py` tests bound to the old
immutable Dissociation replay run `20260915-cpu-replay-10`. Preflight rejects
that run with `implementation_drift: producer_closure_changed:
01-prepare-inputs` after current shared pipeline changes. This is the
fail-closed result of the closure guard, not a Number 7 Dream package failure;
the tests need a fresh compatible replay fixture in separate work. Do not
claim the entire regression suite is green.

Suggested commit subject: `Preserve Number 7 Dream pipeline and production candidate`.
Independent release approval is still pending. Cleanup of the ignored
working folder must wait for an exact target inventory and user authorization;
the pipeline-change report follows that separate cleanup step.

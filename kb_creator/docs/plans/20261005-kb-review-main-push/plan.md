# Scoped main commit and push

Goal: 20261005-kb-review-main-push. State: active.
User directly authorized commit in main and push on 5 October 2026.
Main /root owns orchestration, integration, canonical state and Git writes.
Policy gpt-6-sol/medium; actual platform model/effort unavailable,
assignment platform-unverified, scoped override none.
Independent critic gpt-6-astra/high owns bounded commit-scope review;
engineering/executor/QA roles not delegated in this small packaging goal.

| Step | Owner | Dependency | Done evidence | State |
| --- | --- | --- | --- | --- |
| C1 | Main | user authority | Fresh branch/remote/index/dirty state, prior approved release | completed: main4ahead/0behind, empty index, unrelated376dirtypaths preserved |
| C2 | Main | C1 | Explicit curated path list and byte-preserving/LFS attributes | completed: scope.json,49code frozen +3finalDOCX, compact metadata and23sourcearts; no diagnostic payloads |
| C3 | Independent critic | frozen C2 | Commit-scope receipt, no scratch/secrets/unrelated files | pending |
| C4 | Main | C3 | Exact staged scope, staged-byte checks, scoped commit in main | pending |
| C5 | Main | C4 | Normal non-force push and remote HEAD/LFS verification | pending |

Preserve all unrelated dirty files, deletions and existing staging. No reset,
clean, stash, branch rewrite, force push or source overwrite. Commit the three
approved final successors without overwriting six reviewed original DOCX.
Include user-reviewed original updates, approved nine format removals, reusable
code/tests/contracts, decisions and compact final QA/release evidence. Exclude
original PDFs, OCR/render images, diagnostic fixtures/transcripts, pytest roots
and unrelated config/Innsmouth/CoC work. Existing main ancestors are preserved.

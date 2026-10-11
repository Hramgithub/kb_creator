# Five-step implementation

Goal id: `20260919-five-step-implementation`. State: completed. Release: approved for a new supervised book pilot, per S5; no user/book acceptance.

## Objective and boundaries

Implement the approved [five-step analysis](../../five-step-pipeline-gap-analysis-20260919.md): PDF intake/reconstruction, MASTER_EN, documentary RU draft, proofreading into MASTER_RU, DOCX + assets. ArtView on request, HTML internal, user PDF separate. Codex performs explicit content tasks; no invented automatic model backend or user acceptances. Preserve existing production contracts and immutable source/artifacts. No commit or push authorized.

## Ownership

Role contract: `docs/governance/nri_goal_governance.md` current revision. Main chat owns orchestration, integration and canonical state; policy gpt-5.6-sol/medium, actual exact runtime model/effort unavailable, assignment platform-unverified, scoped override none. Architecture: gpt-5.6-sol/high; engineering: gpt-5.6-terra/medium; execution: gpt-5.6-luna/medium; QA: gpt-5.6-luna/low; independent release critic: gpt-5.5/medium. Contributor assignments below; critic cannot design/implement the reviewed candidate.

## Plan

| Step | Owner | Dependency | Output and definition of done | State |
| --- | --- | --- | --- | --- |
| S1 | Architect, sol/high | — | Bounded code-backed module/API specification; preserve existing checks; receipt handoffs/S1-architecture.md | Complete; new explicit authority profile and interfaces.md |
| S2 | Main chat | — | Environment, CLI integration boundary, runnable baseline and pilot availability | Complete; baseline caveats below |
| S3 | Engineering, terra/medium: five_step_intake, five_step_language, five_step_docx; main integration | S1 | Implement B1–B4 with scoped tests and honest agent tasks | Complete implementation; live integration fixes and tests captured |
| S4 | Main chat + bounded QA | S3 | B5 reuse, complete small-source trial and DOCX inspection; regression evidence | Complete: real source to DOCX, all-page inspection, style rebuild without translation, 240 tests passed; handoffs/S4-integration.md |
| S5 | Independent critic, 5.5/medium | S4 frozen candidate | Release review, resolve findings and document limitations | Complete: handoffs/S5-release-review.md, no blocking findings; supervised pilot scope approved |

Next: user supplies a new book for supervised pilot. Existing uncommitted analytical documents are preserved. No commit or push performed.

## Evidence and limits

- Focused baseline before implementation: reconstruction control/replay/resume + scenario RU and independent verifier + DOCX: 205 passed, 2 skipped, 54 subtests.
- Full kb_creator/tests collection: 15 preexisting import errors, missing pdf_raw page_proof/raw_authority_projection modules. A broader run excluding those tests encountered many historical fixture/environment failures and was interrupted around 65%; no full-suite pass claimed.
- New runner orchestration tests: 5 passed; adapters are explicit doubles, not live PDF-to-DOCX evidence.
- Initial worker receipts S3A/S3B/S3C preserved; follow-up integration findings include promotion working-root invariant, exact agent authority binding, source/draft/final evidence recomputation, split paragraph reassembly, neutral rendering/semantic projection, worktree-local export runtime.
- Main tools are available read-only below primary checkout .tools, including Poppler. S3C's initial statement that Poppler was absent is superseded by main Test-Path confirmation; actual render still pending.

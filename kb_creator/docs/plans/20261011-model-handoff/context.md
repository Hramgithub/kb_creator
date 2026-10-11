# Context: model handoff

- Goal ID: `20261011-model-handoff`
- State: `completed`
- Repository: `https://github.com/Hramgithub/kb_creator.git`
- Imported baseline: `91db0491f3fa0876ab0c44d45151f8006f812d5a`
- Baseline branch: `main`, matching `origin/main` at goal start

## Objective

Produce a compact summary and a detailed continuation specification for a new
model, with Claude Opus 5.5 as the example consumer.

## Accepted constraints

- Treat original PDFs and preserved reviewed documents as immutable inputs.
- Do not infer user acceptance, visual acceptance, publication, or release from
  mechanical verification.
- Separate current DOCX-only production from the archived HTML/DOCX/PDF chain.
- Do not treat historical status entries as current authority.
- The standalone repository intentionally excludes `kb_creator/working/**`.
- Some commands and documentation still refer to NRI-external dependencies;
  identify these explicitly instead of pretending the extraction is fully
  standalone.
- Do not commit or push the handoff without explicit user authorization.

## Completed evidence

- Standalone import published and verified at commit `91db049`.
- 3017 tracked paths/index entries imported; every imported path has the same
  staged blob identity as NRI HEAD after excluding the 28 tracked files under
  `kb_creator/working/**`.
- Git LFS integrity passed; 213 tracked paths are represented by LFS pointers.
- `README.md`, the current top of `PROJECT_STATUS.md`, NRI goal governance, and
  the active user-review plan/context are being audited.

## Completed result

Exact frozen candidate v03 received independent `approved` status for the
documentation-handoff scope. Candidates v01 and v02 remain preserved as
rejected historical freezes; all their findings are closed in the v03 receipt.

## Blockers

None. The standalone repository lacks the ignored working state and some
workspace-level dependencies; the handoff must describe that portability
boundary precisely.

## Next action

Present the uncommitted handoff package to the user. Commit or push it only
after an explicit request. Before any later commit, recheck that the frozen
candidate hashes still match `release.md`.

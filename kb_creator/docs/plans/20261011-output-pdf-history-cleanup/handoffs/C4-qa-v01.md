# C4 bounded QA receipt

- Goal: `20261011-output-pdf-history-cleanup`; step: `C4`.
- Role: bounded QA; assigned profile `gpt-6-luna` / `medium`. Actual runtime model/effort: unavailable.
- Orchestrator policy owner: main chat `gpt-6-sol` / `medium`; orchestration ownership unchanged.
- Assignment state: `platform-unverified`; scoped override: none.
- Scope: read-only verification of the assigned cleanup and refreshed handoff claims. Sole write: this receipt.
- Result: **changes_required**. Local cleanup matches the approved two-file scope, but one handoff statement incorrectly says the cleaned root was published to `origin/main`; current refs show C6 is still pending. The generic PDF rule is present, although Git reports the broader default-deny rule as the actual ignore match for the old output paths.
- Timestamp: `2026-10-11T18:47:10Z`.
- Elapsed: approximately 5 minutes. Token use: unavailable.

## Evidence and findings

### Confirmed

- Goal plan/context read first. They identify the exact two targets, old remote baseline `91db0491f3fa0876ab0c44d45151f8006f812d5a`, cleaned root `141758c2d7e67acde0f4a9f28b2822379e3f5a18`, and C6 publication as pending.
- Read-only Git inspection: local `HEAD` is `141758c2d7e67acde0f4a9f28b2822379e3f5a18`; `origin/main` tracking ref is still `91db0491f3fa0876ab0c44d45151f8006f812d5a`. Local `HEAD` has one commit. `git diff --name-status 91db049..HEAD` reports exactly two deletions, the exact approved output PDFs, and no other baseline changes.
- `git ls-files` reports 3015 tracked paths. `git ls-tree -r --name-only HEAD` contains neither exact output PDF path. The only PDF under `kb_creator/output/` in HEAD is none; output has three tracked non-PDF historical artifacts. The accepted Innsmouth package remains tracked at `kb_creator/inputs/innsmouth/pdf/accepted_20260830_r2/The_Innsmouth_Terror_RU.pdf`.
- Historical reports/manifests remain: 148 paths under the two requested Innsmouth reports roots were listed. The five tracked `pdf_raw/` paths were confirmed in the prior inventory command; report/manifests are not included in the two-path diff.
- `.gitignore` contains generic `*.pdf` / `*.PDF` rules and explicit accepted/production PDF exceptions, including Innsmouth inputs and deliverables. The accepted Innsmouth PDF remains tracked and is not ignored.
- The handoff documents now state baseline `141758c`, 3015 tracked paths, the removal of the two generated historical PDFs, and retention of reports. Markdown relative-link scan produced no broken local links.
- `docs/plans/20261011-model-handoff/release.md:1,7,19-23` clearly marks candidate v03 superseded by the cleanup goal and its receipts as immutable historical evidence.
- `git status --short --branch` shows only the expected untracked `kb_creator/docs/handoff/`, `kb_creator/docs/plans/20261011-model-handoff/`, and `kb_creator/docs/plans/20261011-output-pdf-history-cleanup/` trees. No other worktree changes appeared.

### P1 — incorrect publication claim in handoff

`kb_creator/docs/handoff/MODEL_HANDOFF_SPEC.md:371-372` says the cleaned root import `141758c` was published to `origin/main`. This conflicts with current read-only ref evidence: `HEAD=141758c...`, `origin/main=91db049...`; the cleanup plan marks guarded publication C6 pending. Correct the handoff to say the local cleaned baseline is prepared and publication remains pending, or update it only after C6 is completed and verified. The branch status is `main...origin/main [ahead 1, behind 1]`; this is evidence about the local tracking ref and does not by itself freshly query GitHub.

### P2 — generic ignore rule is present, but not the actual matched rule for removed output paths

The repository root `.gitignore:156-160,260` contains the generic PDF rule and exceptions. However `git check-ignore -v -n --no-index` reports `.gitignore:2` (`*`, default-deny) for both removed output paths, since their directory hierarchy is not allowlisted. The effective safety condition (they are ignored and cannot be accidentally staged as untracked files by ordinary add) holds, and accepted input remains unignored. I did not bypass the root default-deny to prove `*.pdf` alone is the matching rule. If the requirement is specifically that the generic extension rule—not simply the stronger default-deny—protects these output paths, clarify/add the path exception structure and verify that match explicitly.

## Files and state checked

- Cleanup goal `plan.md` and `context.md`.
- Model-handoff `plan.md`, `context.md`, and superseded `release.md`.
- `MODEL_HANDOFF_SUMMARY.md`, `MODEL_HANDOFF_SPEC.md`, root `.gitignore`.
- Git refs, status, commit count, tracked-path count, diff against old baseline, HEAD tree entries for both targets, accepted-input path, output paths, report inventory, ignore checks, and relative Markdown links.

## Limitations and next action

Git was denied in the normal sandbox; all Git inspection was rerun through read-only escalated commands. `origin/main` was read from the existing tracking ref and was not freshly fetched, to avoid changing Git state. No receipt hash comparison was supplied to independently prove historical receipt bytes unchanged; their immutable status is declared in the superseding release document. Main orchestrator should correct the line 372 publication claim and decide whether the generic PDF ignore must be independently demonstrated as the matching rule, then rerun these scoped checks. Do not treat this receipt as release approval or authorization to publish.

# Viral reuse-preservation independent implementation review - 2026-09-02

- `goal_id`: `20260830-kb-creator-next-scenario`
- `step_id`: `preservation-first-commit-review`
- `review_kind`: `implementation`
- `role`: independent critic (`gpt-5.5`, requested effort `high`)
- `actual platform model/effort`: unavailable
- `orchestrator policy owner`: `gpt-5.6-sol` / policy effort `medium`
- `assignment_state`: `matched`
- `scoped_override`: none
- `participation_declaration`: I did not implement or materially design this
  preservation package.
- `scope`: review only the preservation candidate allowlist in
  `D:\NRI\.worktrees\kb-creator-viral`; no review or mutation of the
  `D:\NRI` root checkout.
- `sole_write`: this receipt
- `timestamp`: `2026-09-02T12:04:34.9864590+03:00`
- `elapsed_time`: approximately 32 minutes
- `token_use`: unavailable

## Verdict

`REJECT_PRESERVATION_COMMIT`

The package is close, but it does not satisfy the accepted static-cleanliness
criterion for the five reusable scripts. One allowlisted reusable script still
contains Viral's page-count sentinel `124` in CLI help text.

## Findings

### P1 - reusable script still contains `124`

`kb_creator/scripts/prepare_mineru_three_view_inputs.py:184` contains:

```text
help="one-based pages, for example 5,12,53 or 1-124"
```

The architecture acceptance criteria require the five reusable scripts' static
scan to contain no `Viral`, `Innsmouth`, `124`, admitted source hash/path,
frozen branch/HEAD, or dated run root. This hit is non-executable help text,
but it is still a scenario-shaped example in a script being preserved as
scenario-neutral reusable core. It also contradicts the Terra receipt's claim
that the static portability scan found no such scenario reference.

Remediation: replace the help example with a scenario-neutral range such as
`1-10`, `1-N`, or just `1-3`; rerun the same static scan and the focused
three-module no-cache pytest suite; then request a fresh scoped critic review.

### P2 - existing reports unignore remains a staging hazard

`git check-ignore -v --no-index` confirms the candidate skill, contracts, and
reference config are admitted by narrow rules. It also shows
`kb_creator/reports` is admitted by the pre-existing `!kb_creator/reports/**`
rule, not by the new preservation hunk. This does not put reports in the
candidate allowlist and is not a rejection reason by itself, but it makes exact
allowlist staging mandatory; `git add kb_creator` or any directory wildcard
would be unsafe.

Remediation: stage only the exact 18 reviewed paths. If reports should remain
non-versioned for this project, handle that as a separate `.gitignore` cleanup
decision outside this preservation commit.

## Evidence

- Read the worktree `AGENTS.md`, `docs/governance/nri_goal_governance.md`,
  the critic assignment packet, the architecture review, and the Terra resume
  receipt.
- Inspected all 18 allowlisted candidate paths. The large publication config
  was verified by byte count, SHA-256, and locator/path scans rather than by
  line-by-line prose review.
- Current index is empty: `git diff --cached --name-only` produced no paths.
- Scoped candidate status equals the 18-file allowlist:
  `.gitignore`, one reconstruction skill, three contracts, two Viral reference
  files, three docs, five scripts, and three tests.
- `.gitignore` diff only adds `.agents/skills/**`,
  `kb_creator/contracts/**`, and `kb_creator/reference/**` admission beside
  existing project rules.
- Reference and working publication configs are both `713722` bytes with
  SHA-256
  `C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30`.
- Reference config portable-path scan found many repository-relative
  `kb_creator/working/viral/...` locators, matching the documented
  Viral-specific/non-self-contained status, and no device-local absolute
  `D:`, `C:`, user-profile, or worktree authority path.
- Candidate C remains unrepaired: actual
  `kb_creator/working/viral/master_en/candidates/viral-master-en-candidate-20260902-c/MASTER_EN.md`
  is absent, while its `INVENTORY.json` is present with SHA-256
  `4745E245E754FEA89BCA753C9CD73F1B85C30CE07BFE65C2BF760ED7FF4352F7`.
- Static scans of the reusable tests found only negative fixtures and assertions
  that reject or forbid `Viral`, `Innsmouth`, and absolute paths.
- The reconstruction skill has valid two-key front matter, contains routing and
  policy only, points to the five scripts and three tests, and excludes
  promotion, user acceptance, downstream `MASTER_EN`/`MASTER_RU`/HTML/PDF, Git,
  and release decisions.
- The Viral reference README truthfully identifies `contracts/viral.json` and
  `publication_config_v1.json` as Viral-specific reference evidence and states
  that the publication config is not a self-contained clean-checkout build
  input.

## Verification

Focused reusable suite rerun once, with bytecode and pytest cache disabled:

```text
python -B -m pytest -p no:cacheprovider kb_creator/tests/test_mineru_three_view_tools.py kb_creator/tests/test_audit_mineru_ai_merge_fidelity.py kb_creator/tests/test_materialize_mineru_ai_merge.py
```

Result:

```text
51 passed in 2.60s
```

Post-test `git status --short --branch` showed the same pre-existing modified
and untracked surfaces; no pytest cache or bytecode artifact appeared in the
status output.

## Exclusions Confirmed

The reviewed first preservation commit must not include source PDFs, working
or reconstruction payloads, overlays, candidates, visual bundles, scratch or
staging roots, raw transcripts, repetitive receipts, generic-named Viral
executable/test surfaces, secrets, absolute device paths, or foreign tracked
configuration/governance changes.

Those excluded items are present in the dirty worktree, but not in the scoped
18-file candidate status. The known Candidate C `MASTER_EN.md` loss remains a
separate blocker and this candidate neither repairs, reseals, accepts, nor
releases Candidate C.

## Next Action

Apply the one-line help-text remediation in
`kb_creator/scripts/prepare_mineru_three_view_inputs.py`, rerun the static scan
and the focused three-module test command, and request a fresh independent
implementation review before staging the preservation commit.

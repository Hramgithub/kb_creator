# Viral reuse-preservation closure implementation review - 2026-09-02

- `goal_id`: `20260830-kb-creator-next-scenario`
- `step_id`: `preservation-first-commit-closure-review`
- `review_kind`: `implementation`
- `role`: independent critic (`gpt-5.5`, requested effort `high`)
- `actual platform model/effort`: unavailable
- `orchestrator policy owner`: `gpt-5.6-sol` / policy effort `medium`
- `assignment_state`: `matched`
- `scoped_override`: none
- `participation_declaration`: I did not implement or materially design this
  preservation package or the P1 remediation.
- `scope`: fresh closure review of the first preservation commit candidate in
  `D:\NRI\.worktrees\kb-creator-viral` after the sole Terra remediation
  `1-124` -> `1-10` in the preparer CLI help.
- `sole_write`: this closure receipt
- `timestamp`: `2026-09-02T12:10:57.4026271+03:00`
- `elapsed_time`: approximately 11 minutes
- `token_use`: unavailable

## Verdict

`APPROVE_PRESERVATION_COMMIT`

The prior P1 finding is closed. The reviewed first preservation commit may be
staged only as the exact 18-file allowlist from the original critic packet.
This approval does not approve Candidate C recovery, downstream publication,
release acceptance, generic-named Viral executable surfaces, or foreign dirty
configuration/governance changes.

## Findings

### P0

None.

### P1

None. The previous blocker in
`kb_creator/scripts/prepare_mineru_three_view_inputs.py:184` is remediated:
the help text now uses the scenario-neutral example `1-10`, and the five-script
static gate returns `NO_MATCH` for scenario constants, standalone `124`,
admitted Viral source identity, frozen branch/HEAD, dated run roots, and
device-local paths.

### P2 - existing reports unignore remains a staging hazard

The pre-existing `.gitignore` rule `!kb_creator/reports/**` still admits the
reports tree. This is not introduced by the preservation candidate and does not
block this commit, because the candidate allowlist does not include reports and
the current Git index is empty. It remains a process hazard: stage exact paths,
not directories or wildcards.

Remediation: for the preservation commit, stage only the exact 18 reviewed
paths. Treat any reports ignore-policy cleanup as a separate decision.

### P3

None.

## Evidence

- Reread the closure critic assignment, original critic assignment, prior
  immutable reject receipt, Terra P1 remediation receipt, worktree `AGENTS.md`,
  and NRI goal governance.
- Verified the prior reject receipt remains present and unchanged by this task.
- Confirmed the exact 18-file preservation allowlist is unchanged. Scoped
  status for those paths is still exactly:
  `.gitignore`, one reconstruction skill, three contracts, two Viral reference
  files, three docs, five reusable scripts, and three reusable tests.
- Confirmed the P1 code delta at
  `kb_creator/scripts/prepare_mineru_three_view_inputs.py:184` is only help
  text: `1-124` became `1-10`; parser/runtime semantics were not changed.
- Five-script static gate with `rg --pcre2` returned `NO_MATCH` for `Viral`,
  `viral`, `Innsmouth`, `innsmouth`, standalone `124`,
  `Call_of_Cthulhu_Viral`, the admitted Viral source hash, frozen branch/HEAD,
  dated run roots, `D:`, `C:`, user-profile paths, and `.worktrees`.
- Reusable-test dependency scan returned `NO_MATCH` for `kb_creator/working`,
  `working/viral`, source reconstruction run paths, candidate paths, source PDF
  names, worktree paths, and `MASTER_EN.md`.
- `git diff --check -- .gitignore kb_creator/scripts/prepare_mineru_three_view_inputs.py`
  passed. Git still warns that `.gitignore` would be converted from LF to CRLF
  when Git touches it; that warning predates this closure verdict and produced
  no whitespace error.
- `git diff --cached --name-only` returned no paths.
- Candidate path admission remains as expected:
  `.agents/skills/**`, `kb_creator/contracts/**`, and
  `kb_creator/reference/**` admit the skill, Viral contract, and reference
  publication config.
- Working/source/generated exclusions remain outside the candidate:
  `kb_creator/working/viral/master_en/publication_config_v1.json`, the Viral
  source PDF, and the Viral candidate root remain ignored by the default-deny
  rule. `kb_creator/reports` is admitted by the older reports rule but is not
  part of the 18-file candidate.
- Working and reference publication configs remain byte-identical:
  `713722` bytes and SHA-256
  `C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30`.
- Reference config scan found no device-local absolute path authority.
- Candidate C remains unrepaired and untouched:
  `kb_creator/working/viral/master_en/candidates/viral-master-en-candidate-20260902-c/MASTER_EN.md`
  is absent; its `INVENTORY.json` remains SHA-256
  `4745E245E754FEA89BCA753C9CD73F1B85C30CE07BFE65C2BF760ED7FF4352F7`.

## Verification

Focused reusable suite rerun once, with bytecode and pytest cache disabled:

```text
python -B -m pytest -p no:cacheprovider kb_creator/tests/test_mineru_three_view_tools.py kb_creator/tests/test_audit_mineru_ai_merge_fidelity.py kb_creator/tests/test_materialize_mineru_ai_merge.py
```

Result:

```text
51 passed in 2.62s
```

Post-test `git status --short --branch` showed the same pre-existing dirty
surfaces plus the current untracked handoff set; no pytest cache or bytecode
artifact appeared in status output.

## Exclusions Confirmed

This closure review does not approve source PDFs, overlays, candidates,
working/reconstruction payloads, visual bundles, scratch/staging roots, raw
transcripts, repetitive receipts, generic-named Viral executable/test surfaces,
secrets, absolute device paths, or foreign tracked changes.

The known Candidate C `MASTER_EN.md` loss remains a separate issue. This
preservation commit neither repairs, reseals, accepts, nor releases Candidate C.

## Next Action

The orchestrator may stage the exact 18-file preservation allowlist and commit
that scoped package. Do not stage this closure receipt, prior handoff receipts,
Candidate C state, reports, generated outputs, generic-named Viral executable
surfaces, or unrelated tracked configuration/governance changes as part of the
preservation commit.

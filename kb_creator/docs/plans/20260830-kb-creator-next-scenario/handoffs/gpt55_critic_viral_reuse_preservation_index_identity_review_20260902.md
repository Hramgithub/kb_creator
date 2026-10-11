# Viral reuse-preservation staged-index byte-identity review - 2026-09-02

- `goal_id`: `20260830-kb-creator-next-scenario`
- `step_id`: `preservation-staged-index-byte-identity-review`
- `review_kind`: `implementation`
- `role`: independent critic (`gpt-5.5`, requested effort `high`)
- `actual platform model/effort`: unavailable
- `orchestrator policy owner`: `gpt-5.6-sol` / policy effort `medium`
- `assignment_state`: `matched`
- `scoped_override`: none
- `participation_declaration`: I did not implement, stage, or materially
  design this preservation package, the P1 help-text remediation, or the
  `.gitattributes` byte-identity remediation.
- `scope`: final review of the current staged index in
  `D:\NRI\.worktrees\kb-creator-viral`
- `sole_write`: this staged-index review receipt
- `timestamp`: `2026-09-02T12:18:12.6554387+03:00`
- `elapsed_time`: approximately 13 minutes
- `token_use`: unavailable

## Verdict

`APPROVE_PRESERVATION_COMMIT`

The staged index is the approved preservation set: the previously approved
18 paths plus `.gitattributes`. The staged frozen publication config is
byte-identical to the reviewed working/reference identity, and the user's
separate HTML attribute hunk remains unstaged.

This approval does not approve Candidate C recovery, downstream publication,
release acceptance, generic-named Viral executable surfaces, reports, handoff
receipts, or foreign dirty configuration/governance changes.

## Findings

### P0

None.

### P1

None.

### P2 - `git diff --cached --check` is incompatible with the frozen CRLF JSON

After the exact `-text` attribute is staged, `git diff --cached --check`
reports trailing-whitespace findings throughout
`kb_creator/reference/viral/master_en/publication_config_v1.json`. The staged
blob contains the frozen CRLF byte stream and was independently verified as
`713722` bytes with SHA-256
`C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30`.

This is not a rejection reason for this commit because the assignment's
explicit goal is byte-identity preservation and the exact-path `-text` rule is
the remediation for Git normalization. Do not "fix" this by normalizing the
JSON; that would break the reviewed byte identity.

### P2 - existing reports unignore remains a staging hazard

The pre-existing `.gitignore` rule `!kb_creator/reports/**` still admits
reports. No report path is staged, and this rule is not introduced by the
current staged preservation set. It remains a process hazard for future
wildcard staging.

Remediation: commit the current exact staged index only. Do not stage reports
or directories by wildcard.

### P3

None.

## Staged Index Evidence

`git diff --cached --name-only` contains exactly 19 paths, with no missing or
extra entries compared to the approved set:

```text
.agents/skills/kb-creator-scenario-reconstruction/SKILL.md
.gitattributes
.gitignore
kb_creator/contracts/innsmouth.json
kb_creator/contracts/scenario_contract.v1.schema.json
kb_creator/contracts/viral.json
kb_creator/docs/KB_CREATOR_PIPELINE_SUMMARY_20260830.md
kb_creator/docs/architecture/KB_CREATOR_SCENARIO_PIPELINE_REUSE_REVIEW_20260902.md
kb_creator/docs/plans/20260830-kb-creator-next-scenario/scenario_contract_architecture.md
kb_creator/reference/viral/README.md
kb_creator/reference/viral/master_en/publication_config_v1.json
kb_creator/scripts/audit_mineru_ai_merge_fidelity.py
kb_creator/scripts/compare_mineru_three_views.py
kb_creator/scripts/materialize_mineru_ai_merge.py
kb_creator/scripts/prepare_mineru_three_view_inputs.py
kb_creator/scripts/run_mineru_three_view.ps1
kb_creator/tests/test_audit_mineru_ai_merge_fidelity.py
kb_creator/tests/test_materialize_mineru_ai_merge.py
kb_creator/tests/test_mineru_three_view_tools.py
```

`git diff --cached -- .gitattributes` contains only:

```text
+# Frozen reference policies preserve their reviewed byte identity.
+kb_creator/reference/viral/master_en/publication_config_v1.json -text
```

`git diff -- .gitattributes` confirms the separate user hunk remains unstaged:

```text
+kb_creator/inputs/**/*.html text eol=lf
```

`git status --short --branch` shows `.gitattributes` as `MM`: the staged
byte-identity rule is in the index and the HTML rule remains only in the
worktree.

## Byte-Identity Evidence

Independent staged extraction used `git checkout-index` into a unique temp root
under the target worktree. The temp root was path-checked and removed after
hashing only the extracted staged file.

Extracted staged config identity:

```text
bytes: 713722
sha256: C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30
temp_removed: True
```

Direct `git cat-file blob` cross-check of the staged blob returned the same
identity:

```text
bytes: 713722
sha256: C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30
crlf_count: 19209
lf_count: 20344
```

`git check-attr --cached -a -- kb_creator/reference/viral/master_en/publication_config_v1.json`
reports `text: unset`. It still reports inherited `eol: lf`, but the staged
blob itself proves the exact-path `-text` rule prevented normalization for the
candidate being approved.

## Exclusion Evidence

- Staged exclusion probe for `kb_creator/working`, `kb_creator/reports`,
  the handoffs directory, and known generic-named Viral executable/test
  surfaces returned no paths.
- Candidate C remains unrepaired:
  `kb_creator/working/viral/master_en/candidates/viral-master-en-candidate-20260902-c/MASTER_EN.md`
  is absent.
- Prior closure approval remains valid. I did not rerun tests for this
  byte-identity review; the latest closure suite result remains
  `51 passed in 2.62s`.

## Next Action

The orchestrator may commit the current staged index exactly as-is. Do not add
the unstaged HTML attribute hunk, this receipt, prior handoff receipts, reports,
Candidate C state, generated outputs, generic-named Viral executable/test
surfaces, or unrelated dirty configuration/governance files to this commit.

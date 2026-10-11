# Viral reuse-preservation staged-index identity critic assignment — 2026-09-02

- `goal_id`: `20260830-kb-creator-next-scenario`
- `step_id`: `preservation-staged-index-byte-identity-review`
- `review_kind`: `implementation`
- `orchestrator`: `gpt-5.6-sol` / policy effort `medium`
- `contributor`: independent critic `gpt-5.5` / requested effort `high`
- `assignment_state`: `matched`
- `scoped_override`: none

## New issue and remediation

Exact staging exposed Git EOL normalization: the repository-wide
`*.json text eol=lf` rule changed the frozen publication config in the index.
The config was unstaged and restaged after adding one exact attribute rule:

```text
kb_creator/reference/viral/master_en/publication_config_v1.json -text
```

Only this new `.gitattributes` hunk is staged. A pre-existing user hunk
`kb_creator/inputs/**/*.html text eol=lf` remains unstaged.

`git checkout-index` extraction of the current staged config proves exact
identity: 713,722 bytes / SHA-256
`C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30`.

## Candidate

Review the current staged 19-path set: the previously approved 18 paths plus
`.gitattributes`. The staged `.gitattributes` diff must contain only the exact
`-text` rule/comment; the user HTML hunk must remain unstaged.

## Required review

1. Inspect `git diff --cached --name-only`, staged/unstaged `.gitattributes`
   diffs and staged config attributes.
2. Independently extract the staged config with `git checkout-index` into a
   safely scoped temp root and verify its byte count/SHA-256; clean only that
   temp root.
3. Confirm the 18-path closure approval otherwise remains valid; do not rerun
   tests unless needed (the latest approved run is 51 passed).
4. Confirm no user HTML attribute hunk, receipt, report, Candidate C, run-local
   data or foreign dirty change is staged.
5. Return `APPROVE_PRESERVATION_COMMIT`, `REJECT_PRESERVATION_COMMIT`, or
   `BLOCKED` with P0-P3 findings.

## Sole write

`gpt55_critic_viral_reuse_preservation_index_identity_review_20260902.md`

in the current handoffs directory. Keep all prior receipts immutable.

## Forbidden scope

No index/worktree edit, staging, fetch, commit, push, Candidate C recovery,
config/source mutation, cleanup outside the owned temp root or downstream work.

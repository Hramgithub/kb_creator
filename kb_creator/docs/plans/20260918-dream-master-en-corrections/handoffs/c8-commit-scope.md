# C8 commit-scope and handoff receipt

The correction goal is complete, but no commit or push was authorized or
performed. All reusable changes are Git-visible and are reserved for the later
explicit KB Creator commit together with their dependency chain.

## Include in the later commit

- `kb_creator/pipeline/semantic_structure.py`
- `kb_creator/scripts/author_reviewed_semantic_decisions.py`
- `kb_creator/scripts/materialize_mineru_ai_merge.py`
- `kb_creator/tests/test_semantic_structure.py`
- `kb_creator/tests/test_author_reviewed_semantic_decisions.py`
- `kb_creator/tests/test_materialize_mineru_ai_merge.py`
- the existing structural audit test/module dependency changes already in the
  Dream worktree, including `test_audit_mineru_ai_merge_fidelity.py`;
- `NRI_OCR_LAYOUT_RULES.md`, `kb_creator/README.md`, and
  `kb_creator/PROJECT_STATUS.md`;
- all durable files under
  `kb_creator/docs/plans/20260918-dream-master-en-corrections/`;
- the already Git-visible Dream reconstruction/publication contracts, schemas,
  inputs, and prior plan receipts on which these changes depend.

Before that commit, inventory the complete dirty worktree and stage this as one
dependency-consistent KB Creator series; do not stage only the final three
modules while omitting their currently untracked shared contracts/tests.

## Exclude

- every generated replay, decision output, promotion package, Stage 10 output,
  QA runtime file, and acceptance receipt under `kb_creator/working/**`;
- temporary logs, test caches, rendered intermediates, source PDF copies, and
  unrelated project changes.

`git check-ignore` confirms the corrected `working/**/MASTER_EN.md` is ignored.
`git diff --check` is clean. Old replay-16 and publication-01 hashes remain
unchanged. The current branch is ahead of `origin/main` by one pre-existing
commit; this goal added no commit and performed no push.
